"""Recompute every user's vocabulary threshold from all stored placement answers.

Run after changing the model slope:
    uv run python -m app.ml.recompute_thresholds
"""
import sys

from sqlalchemy import select

from app.database import SessionLocal
from app.models import PlacementAnswer, User
from app.nlp.knowledge import estimate_threshold


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    with SessionLocal() as db:
        for user in db.scalars(select(User)):
            rows = db.execute(
                select(PlacementAnswer.lemma_id, PlacementAnswer.zipf, PlacementAnswer.known)
                .where(PlacementAnswer.user_id == user.id)
                .order_by(PlacementAnswer.id)
            ).all()
            if not rows:
                continue
            latest = {row.lemma_id: (row.zipf, row.known) for row in rows}
            old = user.vocab_threshold
            user.vocab_threshold = estimate_threshold(list(latest.values()))
            print(f"user {user.id}: {len(latest)} words, threshold {old} -> {user.vocab_threshold}")
        db.commit()


if __name__ == "__main__":
    main()