"""Export labelled word-knowledge data from the database.

Run from the backend folder:
    uv run python -m app.ml.export_dataset
"""
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Exercise, Lemma, PlacementAnswer

OUT_PATH = Path(__file__).resolve().parents[3] / "ml" / "data" / "out" / "knowledge_dataset.csv"


def collect_rows() -> list[dict]:
    rows: list[dict] = []
    with SessionLocal() as db:
        placement = db.execute(
            select(PlacementAnswer, Lemma)
            .join(Lemma, Lemma.id == PlacementAnswer.lemma_id)
            .order_by(PlacementAnswer.id)
        ).all()

        # one label per user and word: the latest answer wins
        latest = {}
        for answer, lemma in placement:
            latest[(answer.user_id, answer.lemma_id)] = (answer, lemma)

        for answer, lemma in latest.values():
            rows.append(
                {
                    "source": "placement",
                    "user_id": answer.user_id,
                    "lemma_id": lemma.id,
                    "lemma": lemma.text,
                    "pos": lemma.pos,
                    "zipf": lemma.zipf,
                    "label": int(answer.known),
                    "response_ms": None,
                    "created_at": answer.created_at,
                }
            )

        exercises = db.execute(
            select(Exercise, Lemma)
            .join(Lemma, Lemma.id == Exercise.lemma_id)
            .where(Exercise.answered_at.is_not(None))
            .order_by(Exercise.id)
        ).all()
        for exercise, lemma in exercises:
            rows.append(
                {
                    "source": "exercise",
                    "user_id": exercise.user_id,
                    "lemma_id": lemma.id,
                    "lemma": lemma.text,
                    "pos": lemma.pos,
                    "zipf": lemma.zipf,
                    "label": int(bool(exercise.correct)),
                    "response_ms": exercise.response_ms,
                    "created_at": exercise.answered_at,
                }
            )
    return rows


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    frame = pd.DataFrame(collect_rows())
    if frame.empty:
        print("No answers in the database yet.")
        return

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUT_PATH, index=False)

    print(f"Saved {len(frame)} rows to {OUT_PATH}")
    print(frame.groupby("source")["label"].agg(rows="count", known_share="mean").round(2))
    print(f"Users: {frame['user_id'].nunique()}, distinct words: {frame['lemma_id'].nunique()}")


if __name__ == "__main__":
    main()