from datetime import datetime, timedelta, timezone

import pytest

from app.services.srs import SrsState, update_srs

NOW = datetime(2026, 10, 25, tzinfo=timezone.utc)


def test_correct_answers_grow_interval():
    state = SrsState(2.5, 0, 0)
    intervals = []
    for _ in range(4):
        state, _ = update_srs(state, True, NOW)
        intervals.append(state.interval_days)
    assert intervals == [1, 6, 15, 38]


def test_wrong_answer_resets_progress():
    state, next_review = update_srs(SrsState(2.5, 3, 15), False, NOW)
    assert (state.repetitions, state.interval_days) == (0, 0)
    assert state.ease == pytest.approx(2.3)
    assert next_review == NOW + timedelta(minutes=10)


def test_ease_has_a_floor():
    state, _ = update_srs(SrsState(1.35, 2, 6), False, NOW)
    assert state.ease == 1.3