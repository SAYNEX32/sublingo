import random

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import EpisodeLemma, Exercise, Lemma, User
from app.nlp.analyzer import get_nlp

BLANK = "_____"
MIN_SENTENCE_LEN = 15
MAX_SENTENCE_LEN = 250
ZIPF_WINDOW = 0.7
BLOCKED_DISTRACTORS = {"asshole", "goddamn", "lettin"}


def make_blank(sentence: str, lemma_text: str) -> tuple[str, str] | None:
    """Replace the word with a blank; returns (blanked sentence, original form)."""
    doc = get_nlp()(sentence)
    for token in doc:
        if not token.is_alpha:
            continue
        if token.lemma_.lower() == lemma_text or token.text.lower() == lemma_text:
            end = token.idx + len(token.text)
            return sentence[: token.idx] + BLANK + sentence[end:], token.text
    return None


def find_sentence(db: Session, lemma_id: int, episode_id: int) -> str | None:
    rows = db.execute(
        select(EpisodeLemma.episode_id, EpisodeLemma.example).where(
            EpisodeLemma.lemma_id == lemma_id, EpisodeLemma.example != ""
        )
    ).all()
    rows.sort(key=lambda row: row.episode_id != episode_id)
    for row in rows:
        if MIN_SENTENCE_LEN <= len(row.example) <= MAX_SENTENCE_LEN:
            return row.example
    return None


def pick_distractors(
    db: Session, lemma: Lemma, sentence: str, rng: random.Random, count: int = 3
) -> list[Lemma] | None:
    lowered = sentence.lower()
    rows = db.scalars(
        select(Lemma)
        .where(
            Lemma.pos == lemma.pos,
            Lemma.id != lemma.id,
            Lemma.zipf.between(lemma.zipf - ZIPF_WINDOW, lemma.zipf + ZIPF_WINDOW),
        )
        .order_by(func.abs(Lemma.zipf - lemma.zipf), Lemma.id)
        .limit(60)
    ).all()
    pool = [
        row
        for row in rows
        if row.text.isalpha()
        and len(row.text) >= 3
        and row.text not in lowered
        and row.text not in BLOCKED_DISTRACTORS
    ]
    if len(pool) < count:
        return None
    return rng.sample(pool[:20], count)


def build_exercise(
    db: Session, lemma: Lemma, user: User, episode_id: int, rng: random.Random
) -> Exercise | None:
    sentence = find_sentence(db, lemma.id, episode_id)
    if sentence is None:
        return None
    blank = make_blank(sentence, lemma.text)
    if blank is None:
        return None
    distractors = pick_distractors(db, lemma, sentence, rng)
    if distractors is None:
        return None

    blanked, answer_form = blank
    options = [{"lemma_id": item.id, "text": item.text} for item in [lemma, *distractors]]
    rng.shuffle(options)

    exercise = Exercise(
        user_id=user.id,
        lemma_id=lemma.id,
        kind="cloze",
        sentence=sentence,
        blanked=blanked,
        answer_form=answer_form,
        options=options,
    )
    db.add(exercise)
    db.flush()
    return exercise