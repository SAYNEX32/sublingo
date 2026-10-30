import pandas as pd

from app.ml.cognates import cognate_zipf
from app.ml.features import FEATURE_SETS, add_features


def test_cognate_found_for_international_word():
    assert cognate_zipf("atom") >= 4.0


def test_no_cognate_for_native_word():
    assert cognate_zipf("scientist") == 0.0


def test_non_words_have_no_cognate():
    assert cognate_zipf("x1") == 0.0
    assert cognate_zipf("ab") == 0.0


def test_add_features_creates_every_column():
    frame = pd.DataFrame(
        {"lemma": ["atom", "argue"], "pos": ["NOUN", "VERB"], "zipf": [4.4, 4.1]}
    )
    result = add_features(frame)
    for columns in FEATURE_SETS.values():
        assert set(columns) <= set(result.columns)
    assert result.loc[0, "pos_NOUN"] == 1
    assert result.loc[1, "pos_VERB"] == 1
    assert result.loc[0, "syllables"] == 2