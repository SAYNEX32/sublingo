from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.deps import get_current_user
from app.models import Episode, EpisodeLemma, Lemma, User, UserWord
from app.nlp.analyzer import analyze_lines
from app.nlp.knowledge import p_known
from app.nlp.srt_parser import count_words, decode_srt, parse_srt_content
from app.services.episodes import save_analysis

router = APIRouter(prefix="/episodes", tags=["episodes"])

MAX_UPLOAD_BYTES = 2_000_000


def build_episode_out(db: Session, episode: Episode) -> schemas.EpisodeOut:
    word_count = db.scalar(
        select(func.count())
        .select_from(EpisodeLemma)
        .where(EpisodeLemma.episode_id == episode.id)
    )
    return schemas.EpisodeOut(
        id=episode.id,
        title=episode.title.name,
        season=episode.season,
        number=episode.number,
        subtitle_lines=episode.subtitle_lines,
        word_count=word_count or 0,
    )


@router.post("/analyze", response_model=schemas.EpisodeOut)
def analyze_episode(
    file: UploadFile = File(...),
    title: str = Form(...),
    season: int | None = Form(None),
    number: int | None = Form(None),
    db: Session = Depends(get_db),
):
    raw = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is too large")

    lines = parse_srt_content(decode_srt(raw))
    if not lines:
        raise HTTPException(status_code=422, detail="No subtitle text found")

    stats, phrasal = analyze_lines(lines)
    episode = save_analysis(
        db, title.strip(), season, number, len(lines), count_words(lines), stats, phrasal
    )
    return build_episode_out(db, episode)


@router.get("", response_model=list[schemas.EpisodeOut])
def list_episodes(db: Session = Depends(get_db)):
    episodes = db.scalars(select(Episode).order_by(Episode.id.desc())).all()
    return [build_episode_out(db, episode) for episode in episodes]


@router.get("/{episode_id}/words", response_model=schemas.EpisodeWords)
def episode_words(
    episode_id: int,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    pos: str | None = None,
    db: Session = Depends(get_db),
):
    episode = db.get(Episode, episode_id)
    if episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")

    query = (
        select(EpisodeLemma, Lemma)
        .join(Lemma, Lemma.id == EpisodeLemma.lemma_id)
        .where(EpisodeLemma.episode_id == episode_id)
    )
    if pos:
        query = query.where(Lemma.pos == pos.upper())
    query = (
        query.order_by(EpisodeLemma.count.desc(), Lemma.zipf.asc(), Lemma.id.asc())
        .limit(limit)
        .offset(offset)
    )

    words = [
        schemas.WordOut(
            lemma_id=lemma.id,
            lemma=lemma.text,
            pos=lemma.pos,
            level=lemma.level,
            zipf=lemma.zipf,
            count=entry.count,
            example=entry.example,
        )
        for entry, lemma in db.execute(query).all()
    ]
    return schemas.EpisodeWords(episode=build_episode_out(db, episode), words=words)


@router.get("/{episode_id}/report", response_model=schemas.ReportOut)
def episode_report(
    episode_id: int,
    limit: int = Query(50, ge=1, le=500),
    target: float = Query(0.95, ge=0.5, le=1.0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    episode = db.get(Episode, episode_id)
    if episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    if episode.total_words <= 0:
        raise HTTPException(
            status_code=409,
            detail="Episode has no word total; upload it again",
        )

    rows = db.execute(
        select(EpisodeLemma, Lemma, UserWord.status)
        .join(Lemma, Lemma.id == EpisodeLemma.lemma_id)
        .outerjoin(
            UserWord,
            and_(UserWord.lemma_id == Lemma.id, UserWord.user_id == user.id),
        )
        .where(EpisodeLemma.episode_id == episode_id, Lemma.pos != "PHRASAL")
        .order_by(EpisodeLemma.count.desc(), Lemma.zipf.asc(), Lemma.id.asc())
    ).all()

    scored = []
    for entry, lemma, status in rows:
        if status == "known":
            known_prob = 1.0
        elif status == "learning" or user.vocab_threshold is None:
            known_prob = 0.0
        else:
            known_prob = p_known(lemma.zipf, user.vocab_threshold)
        scored.append((entry.count * (1 - known_prob), entry, lemma))
    scored.sort(key=lambda item: -item[0])

    unknown_total = sum(item[0] for item in scored)
    total = episode.total_words
    coverage = min(1.0, max(0.0, 1 - unknown_total / total))

    need = unknown_total - (1 - target) * total
    words_to_target = None
    if need > 1e-9:
        running = 0.0
        for index, (expected, _, _) in enumerate(scored, start=1):
            running += expected
            if running >= need - 1e-9:
                words_to_target = index
                break

    to_learn = [
        schemas.WordOut(
            lemma_id=lemma.id,
            lemma=lemma.text,
            pos=lemma.pos,
            level=lemma.level,
            zipf=lemma.zipf,
            count=entry.count,
            example=entry.example,
        )
        for expected, entry, lemma in scored
        if expected > 0
    ][:limit]

    return schemas.ReportOut(
        episode=build_episode_out(db, episode),
        total_words=total,
        unknown_occurrences=round(unknown_total, 1),
        coverage=round(coverage, 4),
        target=target,
        vocab_threshold=user.vocab_threshold,
        words_to_target=words_to_target,
        to_learn=to_learn,
    )