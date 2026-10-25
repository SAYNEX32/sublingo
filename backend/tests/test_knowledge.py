import random

from app.nlp.knowledge import BANDS, estimate_threshold, p_known, pick_placement_ids

ZIPFS = [2.0 + 0.1 * step for step in range(26)]


def test_p_known_midpoint():
    assert p_known(3.5, 3.5) == 0.5


def test_p_known_grows_with_frequency():
    assert p_known(4.5, 3.5) > p_known(3.5, 3.5) > p_known(2.5, 3.5)


def test_all_known_gives_low_threshold():
    assert estimate_threshold([(zipf, True) for zipf in ZIPFS]) < 2.6


def test_all_unknown_gives_high_threshold():
    assert estimate_threshold([(zipf, False) for zipf in ZIPFS]) > 4.3


def test_mixed_answers_give_middle_threshold():
    answers = [(zipf, zipf >= 3.5) for zipf in ZIPFS]
    assert abs(estimate_threshold(answers) - 3.5) < 0.3


def test_pick_ids_spreads_over_bands():
    candidates = [(i, 1.5 + (i % 40) * 0.1) for i in range(400)]
    zipf_by_id = dict(candidates)
    ids = pick_placement_ids(candidates, 28, random.Random(1))
    assert len(ids) == 28 and len(set(ids)) == 28
    for low, high in BANDS:
        assert sum(low <= zipf_by_id[i] < high for i in ids) == 4