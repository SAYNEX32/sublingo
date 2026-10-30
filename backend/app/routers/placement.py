import random

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.deps import get_current_user
from app.models import Lemma, PlacementAnswer, User, UserWord
from app.nlp.analyzer import is_spoken_variant
from app.nlp.knowledge import estimate_threshold, pick_placement_ids
from app.services.exercises import BLOCKED_DISTRACTORS

router = APIRouter(prefix="/placement", tags=["placement"])

MIN_ANSWERS = 10


@router.get("/words", response_model=list[schemas.PlacementWord])
def placement_words(
    n: int = Query(30, ge=10, le=60),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(Lemma.id, Lemma.zipf, Lemma.text).where(Lemma.pos != "PHRASAL", Lemma.zipf >= 1.5)
    ).all()
    candidates = [(row.id, row.zipf) for row in rows if not is_spoken_variant(row.text) and row.text not in BLOCKED_DISTRACTORS]
    answered = set(
        db.scalars(select(PlacementAnswer.lemma_id).where(PlacementAnswer.user_id == user.id))
    )
    fresh = [item for item in candidates if item[0] not in answered]
    if len(fresh) >= n:
        candidates = fresh
    if len(candidates) < n:
        raise HTTPException(
            status_code=409, detail="Not enough analyzed words; analyze an episode first"
        )

    ids = pick_placement_ids(candidates, n, random.Random())
    lemmas = {
        lemma.id: lemma for lemma in db.scalars(select(Lemma).where(Lemma.id.in_(ids)))
    }
    return [
        schemas.PlacementWord(lemma_id=i, lemma=lemmas[i].text, pos=lemmas[i].pos)
        for i in ids
    ]


@router.post("/submit", response_model=schemas.PlacementResult)
def placement_submit(
    data: schemas.PlacementSubmitIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ids = {answer.lemma_id for answer in data.answers}
    lemmas = {
        lemma.id: lemma for lemma in db.scalars(select(Lemma).where(Lemma.id.in_(ids)))
    }
    answers = {
        answer.lemma_id: answer.known
        for answer in data.answers
        if answer.lemma_id in lemmas
    }
    if len(answers) < MIN_ANSWERS:
        raise HTTPException(status_code=422, detail="Not enough valid answers")

    threshold = estimate_threshold(
        [(lemmas[lemma_id].zipf, known) for lemma_id, known in answers.items()]
    )

    existing = {
        item.lemma_id: item
        for item in db.scalars(
            select(UserWord).where(
                UserWord.user_id == user.id, UserWord.lemma_id.in_(set(answers))
            )
        )
    }
    for lemma_id, known in answers.items():
        db.add(
            PlacementAnswer(
                user_id=user.id,
                lemma_id=lemma_id,
                zipf=lemmas[lemma_id].zipf,
                known=known,
            )
        )
        if known:
            current = existing.get(lemma_id)
            if current is not None:
                current.status = "known"
            else:
                db.add(UserWord(user_id=user.id, lemma_id=lemma_id, status="known"))

    user.vocab_threshold = threshold
    db.commit()
    return schemas.PlacementResult(
        vocab_threshold=threshold,
        answers_used=len(answers),
        known_count=sum(answers.values()),
    )