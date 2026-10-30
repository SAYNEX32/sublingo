"""Check the cognate feature against a hand-labelled word list.

Run from the backend folder:
    uv run python -m app.ml.eval_cognates
"""
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import roc_auc_score

from app.ml.cognates import cognate_zipf
from app.ml.features import COGNATE_MIN_ZIPF

LABELS_PATH = Path(__file__).resolve().parents[3] / "ml" / "labels" / "cognates.csv"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    labels = pd.read_csv(LABELS_PATH)
    labels["score"] = labels["word"].map(cognate_zipf)
    positive = labels["cognate"] == 1
    flagged = labels["score"] >= COGNATE_MIN_ZIPF

    print(f"Words: {len(labels)} ({int(positive.sum())} cognates)")
    print(f"AUC of the raw score:   {roc_auc_score(labels['cognate'], labels['score']):.3f}")
    print(
        f"Threshold {COGNATE_MIN_ZIPF}: found {flagged[positive].mean():.0%} of cognates, "
        f"{flagged[~positive].mean():.0%} of non-cognates flagged by mistake"
    )
    print("\nMissed cognates:", ", ".join(labels.loc[positive & ~flagged, "word"]))
    print("False alarms:", ", ".join(labels.loc[~positive & flagged, "word"]))


if __name__ == "__main__":
    main()