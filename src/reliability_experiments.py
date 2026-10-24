"""
A4 — K-Means Reliability Experiments
Team 6 | TA3 — Clustering and Model Evaluation

Repeat selected K-Means experiments across 10 random seeds.

Purpose:
Check how much nearest-centre distance changes when
the initial random state changes.

Distances are straight-line geographical estimates,
not actual road distances.
"""

from pathlib import Path
from datetime import date

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from model import run_kmeans
from evaluate import distance_summary


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "clean_bookings.csv"
)

RESULTS_DIR = PROJECT_ROOT / "results"
PLOTS_DIR = RESULTS_DIR / "plots"
EXPERIMENT_LOG = PROJECT_ROOT / "experiments.csv"

K_VALUES = [3, 5, 6, 8]
SEEDS = list(range(42, 52))


def load_coordinates():
    """Load completed booking locations."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Cleaned bookings not found. Run data_loader.py first."
        )

    df = pd.read_csv(INPUT_FILE)

    coordinates = df[["lat", "lng"]].to_numpy(dtype=float)

    if len(coordinates) == 0:
        raise ValueError("No booking locations found.")

    if not np.isfinite(coordinates).all():
        raise ValueError("Invalid booking coordinates found.")

    return coordinates


def run_reliability_tests(coordinates):
    """Repeat selected K-Means runs across ten seeds."""

    records = []

    for k in K_VALUES:

        print(f"\nTesting K={k}")

        for seed in SEEDS:

            result = run_kmeans(
                coordinates,
                n_clusters=k,
                random_state=seed,
            )

            distances = distance_summary(
                coordinates,
                result["centres"],
            )

            records.append({
                "k": k,
                "seed": seed,
                "mean_km": distances["mean_km"],
                "median_km": distances["median_km"],
                "p90_km": distances["p90_km"],
            })

            print(
                f"  Seed {seed}: "
                f"mean = {distances['mean_km']:.4f} km"
            )

    return pd.DataFrame(records)


def summarize_results(details):
    """Calculate mean and sample standard deviation across seeds."""

    summary = (
        details.groupby("k")
        .agg(
            runs=("seed", "count"),
            mean_distance_km=("mean_km", "mean"),
            std_distance_km=("mean_km", "std"),
            min_distance_km=("mean_km", "min"),
            max_distance_km=("mean_km", "max"),
        )
        .reset_index()
    )

    return summary


def create_reliability_chart(summary):
    """Show variability in average distance across random seeds."""

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 6))

    plt.errorbar(
        summary["k"],
        summary["mean_distance_km"],
        yerr=summary["std_distance_km"],
        fmt="o-",
        capsize=6,
        markersize=7,
        linewidth=2,
        color="#7358DB",
    )

    plt.title("K-Means Reliability Across 10 Random Seeds")
    plt.xlabel("Number of Candidate Depots (K)")
    plt.ylabel("Mean Nearest-Centre Distance (km)")
    plt.xticks(K_VALUES)
    plt.grid(alpha=0.25)
    plt.tight_layout()

    output = PLOTS_DIR / "kmeans_seed_reliability.png"

    plt.savefig(output, dpi=200)
    plt.close()

    return output


def update_experiment_log(details):
    """Record each seed experiment without duplicating run IDs."""

    columns = [
        "run_id", "date", "who", "what_changed",
        "main_metric", "value", "seed", "notes",
    ]

    records = []

    for row in details.itertuples(index=False):

        records.append({
            "run_id": f"kmeans_reliability_k{row.k}_seed{row.seed}",
            "date": date.today().isoformat(),
            "who": "Team 6",
            "what_changed": f"K-Means K={row.k}; seed={row.seed}",
            "main_metric": "mean_nearest_centre_km",
            "value": round(row.mean_km, 6),
            "seed": row.seed,
            "notes": (
                "10-seed reliability experiment; "
                "39,302 completed bookings; "
                "straight-line distance"
            ),
        })

    new_rows = pd.DataFrame(records)

    if EXPERIMENT_LOG.exists():
        existing = pd.read_csv(EXPERIMENT_LOG)
    else:
        existing = pd.DataFrame(columns=columns)

    combined = pd.concat(
        [existing, new_rows],
        ignore_index=True,
    )

    combined = combined.drop_duplicates(
        subset=["run_id"],
        keep="last",
    )

    combined[columns].to_csv(
        EXPERIMENT_LOG,
        index=False,
    )


def main():

    print("\n===== TA3 K-MEANS RELIABILITY TEST =====")

    coordinates = load_coordinates()

    print(f"Bookings: {len(coordinates):,}")
    print(f"K values: {K_VALUES}")
    print(f"Random seeds: {SEEDS}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    details = run_reliability_tests(coordinates)
    summary = summarize_results(details)

    details.to_csv(
        RESULTS_DIR / "kmeans_reliability_runs.csv",
        index=False,
    )

    summary.to_csv(
        RESULTS_DIR / "kmeans_reliability_summary.csv",
        index=False,
    )

    chart = create_reliability_chart(summary)

    update_experiment_log(details)

    print("\n===== RELIABILITY SUMMARY =====")
    print(summary.round(4).to_string(index=False))

    print(f"\nChart saved: {chart}")
    print("Detailed and summary CSV files saved in results/")
    print("Experiment log updated.")

    print("\n===== RELIABILITY TEST COMPLETE =====")


if __name__ == "__main__":
    main()
