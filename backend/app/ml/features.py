import re

import pandas as pd

from app.ml.cognates import cognate_zipf

POS_GROUPS = ("NOUN", "VERB", "ADJ", "ADV")
COGNATE_MIN_ZIPF = 3.0
VOWEL_GROUPS = re.compile(r"[aeiouy]+")

BASE = ["zipf"]
FORM = ["length", "syllables", *[f"pos_{pos}" for pos in POS_GROUPS], "pos_OTHER"]
COGNATE = ["cognate_zipf", "has_cognate"]

FEATURE_SETS = {
    "frequency": BASE,
    "frequency+form": BASE + FORM,
    "frequency+cognate": BASE + COGNATE,
    "all": BASE + FORM + COGNATE,
}


def add_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add word-level features to a frame with columns lemma, pos and zipf."""
    result = frame.copy()
    words = result["lemma"].str.lower()
    result["length"] = words.str.len()
    result["syllables"] = words.map(lambda w: max(1, len(VOWEL_GROUPS.findall(w))))
    for pos in POS_GROUPS:
        result[f"pos_{pos}"] = (result["pos"] == pos).astype(int)
    result["pos_OTHER"] = (~result["pos"].isin(POS_GROUPS)).astype(int)
    result["cognate_zipf"] = words.map(cognate_zipf)
    result["has_cognate"] = (result["cognate_zipf"] >= COGNATE_MIN_ZIPF).astype(int)
    return result