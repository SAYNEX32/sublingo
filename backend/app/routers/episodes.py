from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.models import Episode, EpisodeLemma, Lemma
from app.nlp.analyzer import analyze_lines
from app.nlp.srt_parser import decode_srt, parse_srt_content
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
    episode = save_analysis(db, title.strip(), season, number, len(lines), stats, phrasal)
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
        query.order_by(EpisodeLemma.count.desc(), Lemma.zipf.asc())
        .limit(limit)
        .offset(offset)
    )

    words = [
        schemas.WordOut(
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