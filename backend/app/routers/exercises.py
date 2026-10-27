import random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.deps import get_current_user
from app.models import Episode, EpisodeLemma, Exercise, Lemma, User, UserWord
from app.nlp.knowledge import p_known
from app.services.exercises import build_exercise
from app.services.srs import GRADUATE_DAYS, SrsState, update_srs

router = APIRouter(prefix="/exercises", tags=["exercises"])

KNOWN_PROB_SKIP = 0.7
CANDIDATE_LIMIT = 40
DUE_LIMIT = 10


def to_out(exercise: Exercise, is_new: bool) -> schemas.ExerciseOut:
    return schemas.ExerciseOut(
        id=exercise.id,
        kind=exercise.kind,
        sentence=exercise.blanked,
        options=[schemas.OptionOut(**option) for option in exercise.options],
        is_new=is_new,
    )


@router.get("/next", response_model=schemas.ExerciseOut | None)
def next_exercise(
    episode_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if db.get(Episode, episode_id) is None:
        raise HTTPException(status_code=404, detail="Episode not found")

    now = datetime.now(timezone.utc)
    rng = random.Random()

    pending = db.scalar(
        select(Exercise)
        .where(Exercise.user_id == user.id)
        .order_by(Exercise.id.desc())
        .limit(1)
    )
    if pending is not None and pending.answered_at is None:
        answered_before = db.scalar(
            select(func.count())
            .select_from(Exercise)
            .where(
                Exercise.user_id == user.id,
                Exercise.lemma_id == pending.lemma_id,
                Exercise.answered_at.is_not(None),
            )
        )
        return to_out(pending, is_new=not answered_before)

    due = db.scalars(
        select(Lemma)
        .join(UserWord, UserWord.lemma_id == Lemma.id)
        .where(
            UserWord.user_id == user.id,
            UserWord.status == "learning",
            or_(UserWord.next_review.is_(None), UserWord.next_review <= now),
        )
        .order_by(UserWord.next_review.asc(), UserWord.id.asc())
        .limit(DUE_LIMIT)
    ).all()
    for lemma in due:
        exercise = build_exercise(db, lemma, user, episode_id, rng)
        if exercise is not None:
            db.commit()
            return to_out(exercise, is_new=False)

    candidates = db.scalars(
        select(Lemma)
        .join(EpisodeLemma, EpisodeLemma.lemma_id == Lemma.id)
        .outerjoin(
            UserWord,
            and_(UserWord.lemma_id == Lemma.id, UserWord.user_id == user.id),
        )
        .where(
            EpisodeLemma.episode_id == episode_id,
            Lemma.pos != "PHRASAL",
            UserWord.id.is_(None),
            EpisodeLemma.example != "",
        )
        .order_by(EpisodeLemma.count.desc(), Lemma.zipf.asc(), Lemma.id.asc())
        .limit(CANDIDATE_LIMIT)
    ).all()
    for lemma in candidates:
        if (
            user.vocab_threshold is not None
            and p_known(lemma.zipf, user.vocab_threshold) >= KNOWN_PROB_SKIP
        ):
            continue
        exercise = build_exercise(db, lemma, user, episode_id, rng)
        if exercise is None:
            continue
        db.add(
            UserWord(
                user_id=user.id,
                lemma_id=lemma.id,
                status="learning",
                ease=2.5,
                repetitions=0,
                interval_days=0,
                next_review=now,
            )
        )
        db.commit()
        return to_out(exercise, is_new=True)

    return None


@router.post("/{exercise_id}/answer", response_model=schemas.AnswerOut)
def answer_exercise(
    exercise_id: int,
    data: schemas.AnswerIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise = db.get(Exercise, exercise_id)
    if exercise is None or exercise.user_id != user.id:
        raise HTTPException(status_code=404, detail="Exercise not found")
    if exercise.answered_at is not None:
        raise HTTPException(status_code=409, detail="Already answered")
    if data.lemma_id not in {option["lemma_id"] for option in exercise.options}:
        raise HTTPException(status_code=422, detail="Not one of the options")

    now = datetime.now(timezone.utc)
    correct = data.lemma_id == exercise.lemma_id
    exercise.chosen_lemma_id = data.lemma_id
    exercise.correct = correct
    exercise.response_ms = data.response_ms
    exercise.answered_at = now

    word = db.scalar(
        select(UserWord).where(
            UserWord.user_id == user.id, UserWord.lemma_id == exercise.lemma_id
        )
    )
    if word is None:
        word = UserWord(user_id=user.id, lemma_id=exercise.lemma_id, status="learning")
        db.add(word)
        word.ease, word.repetitions, word.interval_days = 2.5, 0, 0

    state, next_review = update_srs(
        SrsState(word.ease, word.repetitions, word.interval_days), correct, now
    )
    word.ease = state.ease
    word.repetitions = state.repetitions
    word.interval_days = state.interval_days
    word.next_review = next_review
    word.status = "known" if state.interval_days >= GRADUATE_DAYS else "learning"

    lemma = db.get(Lemma, exercise.lemma_id)
    db.commit()
    return schemas.AnswerOut(
        correct=correct,
        correct_lemma_id=lemma.id,
        correct_lemma=lemma.text,
        answer_form=exercise.answer_form,
        sentence=exercise.sentence,
        status=word.status,
        interval_days=word.interval_days,
        next_review=next_review,
    )