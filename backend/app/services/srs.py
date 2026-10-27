from dataclasses import dataclass
from datetime import datetime, timedelta

GRADUATE_DAYS = 21
RETRY_MINUTES = 10
MIN_EASE = 1.3
EASE_PENALTY = 0.2


@dataclass
class SrsState:
    ease: float
    repetitions: int
    interval_days: int


def update_srs(
    state: SrsState, correct: bool, now: datetime
) -> tuple[SrsState, datetime]:
    """Simplified SM-2: returns the new state and the next review time."""
    if not correct:
        new_state = SrsState(max(MIN_EASE, state.ease - EASE_PENALTY), 0, 0)
        return new_state, now + timedelta(minutes=RETRY_MINUTES)

    repetitions = state.repetitions + 1
    if repetitions == 1:
        interval = 1
    elif repetitions == 2:
        interval = 6
    else:
        interval = max(state.interval_days + 1, round(state.interval_days * state.ease))
    return SrsState(state.ease, repetitions, interval), now + timedelta(days=interval)