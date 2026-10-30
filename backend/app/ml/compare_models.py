"""Compare word-knowledge models with repeated grouped cross-validation.

Run from the backend folder:
    uv run python -m app.ml.compare_models
"""
import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.dummy import DummyClassifier  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score  # noqa: E402
from sklearn.model_selection import StratifiedGroupKFold  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from app.ml.features import FEATURE_SETS, add_features  # noqa: E402
from app.nlp.knowledge import SLOPE, estimate_threshold, p_known  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = ROOT / "ml" / "data" / "out" / "knowledge_dataset.csv"
RESULTS_DIR = ROOT / "ml" / "results"

MIN_ROWS = 60


class AppFormula:
    """The model used in the app: sigmoid(slope * (zipf - t)), t fitted on the answers."""

    def __init__(self, slope: float = SLOPE):
        self.slope = slope

    def fit(self, X, y):
        answers = list(zip(X["zipf"], np.asarray(y).astype(bool)))
        self.threshold_ = estimate_threshold(answers, self.slope)
        return self

    def predict_proba(self, X):
        p = np.array([p_known(zipf, self.threshold_, self.slope) for zipf in X["zipf"]])
        return np.column_stack([1 - p, p])


def make_models():
    def logreg():
        return make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=1000))

    return {
        "prior (no features)": ("frequency", lambda: DummyClassifier(strategy="prior")),
        **{
            f"app formula (slope {slope})": ("frequency", lambda slope=slope: AppFormula(slope))
            for slope in (0.75, 1.0, 1.5, 2.0, 3.0)
        },
        "logreg: frequency": ("frequency", logreg),
        "logreg: frequency+form": ("frequency+form", logreg),
        "logreg: frequency+cognate": ("frequency+cognate", logreg),
        "logreg: all features": ("all", logreg),
        "boosting: all features": (
            "all",
            lambda: HistGradientBoostingClassifier(
                max_depth=3,
                learning_rate=0.05,
                max_iter=150,
                min_samples_leaf=10,
                random_state=0,
            ),
        ),
    }


def score(y_true, y_prob) -> dict[str, float]:
    clipped = np.clip(y_prob, 1e-6, 1 - 1e-6)
    return {
        "auc": roc_auc_score(y_true, clipped),
        "log_loss": log_loss(y_true, clipped, labels=[0, 1]),
        "brier": brier_score_loss(y_true, clipped),
    }


def evaluate(frame: pd.DataFrame, repeats: int, folds: int):
    models = make_models()
    y = frame["label"].to_numpy()
    groups = frame["lemma_id"].to_numpy()

    per_repeat = {name: [] for name in models}
    oof_mean = {name: np.zeros(len(frame)) for name in models}

    for repeat in range(repeats):
        splitter = StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=repeat)
        oof = {name: np.zeros(len(frame)) for name in models}
        for train_idx, test_idx in splitter.split(frame, y, groups):
            for name, (feature_set, factory) in models.items():
                columns = FEATURE_SETS[feature_set]
                model = factory()
                model.fit(frame.iloc[train_idx][columns], y[train_idx])
                oof[name][test_idx] = model.predict_proba(frame.iloc[test_idx][columns])[:, 1]
        for name in models:
            per_repeat[name].append(score(y, oof[name]))
            oof_mean[name] += oof[name] / repeats

    return per_repeat, oof_mean


def summarize(per_repeat) -> pd.DataFrame:
    rows = []
    for name, scores in per_repeat.items():
        table = pd.DataFrame(scores)
        rows.append(
            {
                "model": name,
                "auc": table["auc"].mean(),
                "auc_std": table["auc"].std(),
                "log_loss": table["log_loss"].mean(),
                "log_loss_std": table["log_loss"].std(),
                "brier": table["brier"].mean(),
            }
        )
    return pd.DataFrame(rows)


def save_markdown(summary: pd.DataFrame, info: str) -> None:
    lines = [
        info,
        "",
        "| Model | AUC | Log-loss | Brier |",
        "|---|---|---|---|",
    ]
    for row in summary.itertuples():
        lines.append(
            f"| {row.model} | {row.auc:.3f} ± {row.auc_std:.3f} | "
            f"{row.log_loss:.3f} ± {row.log_loss_std:.3f} | {row.brier:.3f} |"
        )
    lines += [
        "",
        "± is the standard deviation over repeated cross-validation splits. "
        "It shows split-to-split variability, not the uncertainty of the data itself.",
    ]
    (RESULTS_DIR / "metrics.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_auc(summary: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 0.5 * len(summary) + 1.5))
    positions = np.arange(len(summary))
    ax.barh(positions, summary["auc"], xerr=summary["auc_std"], color="#4c6aa8")
    ax.axvline(0.5, color="gray", linestyle="--", linewidth=1)
    ax.set_yticks(positions)
    ax.set_yticklabels(summary["model"])
    ax.invert_yaxis()
    ax.set_xlim(0.4, 1.0)
    ax.set_xlabel("ROC AUC (higher is better)")
    ax.set_title("Predicting whether a user knows a word")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "auc.png", dpi=150)
    plt.close(fig)


def plot_calibration(y, probabilities: np.ndarray, name: str) -> None:
    bins = np.quantile(probabilities, np.linspace(0, 1, 6))
    bins[0], bins[-1] = -1e-9, 1 + 1e-9
    bin_ids = np.digitize(probabilities, bins[1:-1])
    xs, ys = [], []
    for bin_id in range(5):
        mask = bin_ids == bin_id
        if mask.sum() >= 3:
            xs.append(probabilities[mask].mean())
            ys.append(y[mask].mean())

    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.plot([0, 1], [0, 1], "--", color="gray", linewidth=1)
    ax.plot(xs, ys, "o-", color="#4c6aa8")
    ax.set_xlabel("Predicted probability of knowing the word")
    ax.set_ylabel("Observed share of known words")
    ax.set_title(f"Calibration: {name}")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "calibration.png", dpi=150)
    plt.close(fig)


def bootstrap_auc(y, oof_mean, reference="logreg: frequency", draws=1000, seed=0):
    """95% intervals for AUC and for the AUC difference against the reference model."""
    rng = np.random.default_rng(seed)
    names = list(oof_mean)
    samples = {name: [] for name in names}
    for _ in range(draws):
        idx = rng.integers(0, len(y), len(y))
        if len(set(y[idx])) < 2:
            continue
        for name in names:
            samples[name].append(roc_auc_score(y[idx], oof_mean[name][idx]))

    rows = []
    for name in names:
        values = np.array(samples[name])
        diff = values - np.array(samples[reference])
        rows.append(
            {
                "model": name,
                "auc_low": np.percentile(values, 2.5),
                "auc_high": np.percentile(values, 97.5),
                "diff_vs_frequency": diff.mean(),
                "diff_low": np.percentile(diff, 2.5),
                "diff_high": np.percentile(diff, 97.5),
            }
        )
    return pd.DataFrame(rows)


def append_intervals(intervals: pd.DataFrame) -> None:
    lines = [
        "",
        "Bootstrap 95% intervals over words (1000 draws). "
        "A difference counts as real only if its interval excludes 0.",
        "",
        "| Model | AUC 95% interval | AUC difference vs logreg: frequency |",
        "|---|---|---|",
    ]
    for row in intervals.itertuples():
        lines.append(
            f"| {row.model} | {row.auc_low:.3f} to {row.auc_high:.3f} | "
            f"{row.diff_vs_frequency:+.3f} ({row.diff_low:+.3f} to {row.diff_high:+.3f}) |"
        )
    with (RESULTS_DIR / "metrics.md").open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--source", choices=["placement", "exercise", "all"], default="placement")
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--folds", type=int, default=5)
    args = parser.parse_args()

    frame = pd.read_csv(args.data)
    if args.source != "all":
        frame = frame[frame["source"] == args.source]
    frame = add_features(frame.reset_index(drop=True))

    if len(frame) < MIN_ROWS or frame["label"].nunique() < 2:
        print(f"Only {len(frame)} usable rows. Collect at least {MIN_ROWS} labelled words first.")
        return

    per_repeat, oof_mean = evaluate(frame, args.repeats, args.folds)
    summary = summarize(per_repeat)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    info = (
        f"Data: {len(frame)} labels, {frame['lemma_id'].nunique()} distinct words, "
        f"{frame['user_id'].nunique()} user(s), {frame['label'].mean():.0%} known. "
        f"Source: {args.source}. {args.repeats}x repeated {args.folds}-fold "
        "cross-validation, folds grouped by word."
    )
    summary.to_csv(RESULTS_DIR / "metrics.csv", index=False)
    save_markdown(summary, info)
    plot_auc(summary)

    intervals = bootstrap_auc(frame["label"].to_numpy(), oof_mean)
    intervals.to_csv(RESULTS_DIR / "auc_intervals.csv", index=False)
    append_intervals(intervals)

    best = summary.sort_values("log_loss").iloc[0]["model"]
    plot_calibration(frame["label"].to_numpy(), oof_mean[best], best)

    print(info)
    print()
    print(summary.round(3).to_string(index=False))
    print("\nBootstrap 95% intervals:")
    print(intervals.round(3).to_string(index=False))
    print(f"\nBest by log-loss: {best}")
    print(f"Saved to {RESULTS_DIR}")


if __name__ == "__main__":
    main()