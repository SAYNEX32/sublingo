import math
import random

SLOPE = 3.0
PRIOR_MEAN = 3.5
PRIOR_SD = 1.0
GRID = [round(1.0 + 0.05 * step, 2) for step in range(91)]
BANDS = [(1.5, 2.5), (2.5, 3.0), (3.0, 3.5), (3.5, 4.0), (4.0, 4.51)]


def p_known(zipf: float, threshold: float, slope: float = SLOPE) -> float:
    """Probability that a user knows a word: logistic in word frequency."""
    return 1 / (1 + math.exp(-slope * (zipf - threshold)))


def estimate_threshold(answers: list[tuple[float, bool]]) -> float:
    """MAP estimate of the user's threshold from (zipf, known) answers."""
    best_threshold = PRIOR_MEAN
    best_score = -math.inf
    for threshold in GRID:
        score = -((threshold - PRIOR_MEAN) ** 2) / (2 * PRIOR_SD**2)
        for zipf, known in answers:
            p = min(max(p_known(zipf, threshold), 1e-6), 1 - 1e-6)
            score += math.log(p if known else 1 - p)
        if score > best_score:
            best_threshold, best_score = threshold, score
    return best_threshold


def pick_placement_ids(
    candidates: list[tuple[int, float]], n: int, rng: random.Random
) -> list[int]:
    """Pick n lemma ids spread evenly over frequency bands."""
    per_band = max(1, n // len(BANDS))
    chosen: list[tuple[int, float]] = []
    leftovers: list[tuple[int, float]] = []
    for low, high in BANDS:
        band = [item for item in candidates if low <= item[1] < high]
        rng.shuffle(band)
        chosen += band[:per_band]
        leftovers += band[per_band:]
    rng.shuffle(leftovers)
    chosen += leftovers[: max(0, n - len(chosen))]
    rng.shuffle(chosen)
    return [item[0] for item in chosen[:n]]