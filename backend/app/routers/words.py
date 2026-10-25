from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.deps import get_current_user
from app.models import Lemma, User, UserWord

router = APIRouter(prefix="/words", tags=["words"])


@router.put("/mark", response_model=schemas.MarkOut)
def mark_words(
    data: schemas.MarkIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    valid = set(db.scalars(select(Lemma.id).where(Lemma.id.in_(set(data.lemma_ids)))))
    existing = {
        item.lemma_id: item
        for item in db.scalars(
            select(UserWord).where(
                UserWord.user_id == user.id, UserWord.lemma_id.in_(valid)
            )
        )
    }

    for lemma_id in valid:
        current = existing.get(lemma_id)
        if data.status == "unknown":
            if current is not None:
                db.delete(current)
        elif current is not None:
            current.status = data.status
        else:
            db.add(UserWord(user_id=user.id, lemma_id=lemma_id, status=data.status))

    db.commit()
    return schemas.MarkOut(updated=len(valid))


@router.get("/mine", response_model=list[schemas.UserWordOut])
def my_words(
    status: str | None = Query(None, pattern="^(known|learning)$"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        select(UserWord, Lemma)
        .join(Lemma, Lemma.id == UserWord.lemma_id)
        .where(UserWord.user_id == user.id)
    )
    if status:
        query = query.where(UserWord.status == status)
    query = (
        query.order_by(UserWord.updated_at.desc(), UserWord.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return [
        schemas.UserWordOut(
            lemma_id=lemma.id, lemma=lemma.text, pos=lemma.pos, status=item.status
        )
        for item, lemma in db.execute(query).all()
    ]