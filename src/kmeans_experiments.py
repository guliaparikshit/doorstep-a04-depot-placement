"""
A4 — K-Means Depot Count Experiments
Team 6 | TA3 — Clustering and Model Evaluation

Tests K-Means for K=1 through K=10 using the cleaned
Doorstep booking dataset.

Measures straight-line geographical distance from each
booking to its nearest proposed cluster centre.

These are candidate centres, NOT final accessible depots.
"""

from pathlib import Path
from datetime import date

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from model import run_kmeans
from evaluate import distance_summary, compare_depot_counts


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "clean_bookings.csv"
RESULTS_DIR = PROJECT_ROOT / "results"
PLOTS_DIR = RESULTS_DIR / "plots"
EXPERIMENT_LOG = PROJECT_ROOT / "experiments.csv"

RANDOM_SEED = 42
K_VALUES = range(1, 11)


def load_coordinates():
    """Read cleaned booking coordinates."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Cleaned dataset not found. Run data_loader.py first."
        )

    df = pd.read_csv(INPUT_FILE)

    coordinates = df[["lat", "lng"]].to_numpy(dtype=float)

    if not np.isfinite(coordinates).all():
        raise ValueError("Invalid coordinates found.")

    print(f"Cleaned bookings loaded: {len(coordinates):,}")

    return coordinates


def run_experiments(coordinates):
    """Run K-Means for 1 to 10 clusters."""

    records = []

    for k in K_VALUES:

        print(f"Running K-Means with K={k}...")

        result = run_kmeans(
            coordinates,
            n_clusters=k,
            random_state=RANDOM_SEED,
        )

        summary = distance_summary(
            coordinates,
            result["centres"],
        )

        records.append({
            "k": k,
            "mean_km": summary["mean_km"],
            "median_km": summary["median_km"],
            "p90_km": summary["p90_km"],
            "max_km": summary["max_km"],
            "total_km": summary["total_km"],
            "inertia": result["inertia"],
            "seed": RANDOM_SEED,
        })

        print(
            f"  Average nearest-centre distance: "
            f"{summary['mean_km']:.3f} km"
        )

    return pd.DataFrame(records)


def generate_comparison_table(results):
    """Calculate distance improvements for each additional depot."""

    comparisons = compare_depot_counts(
        results[["k", "mean_km"]].to_dict("records")
    )

    improvement_df = pd.DataFrame(comparisons)

    merged = results.merge(
        improvement_df[
            ["k", "improvement_km", "improvement_pct"]
        ],
        on="k",
        how="left",
    )

    return merged


def create_plots(results):
    """Generate distance and improvement graphs."""

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # Graph 1 — Average nearest-depot distance
    plt.figure(figsize=(10, 6))

    plt.plot(
        results["k"],
        results["mean_km"],
        marker="o",
        linewidth=2.5,
        color="#7358DB",
    )

    plt.title("K-Means: Depot Count vs Average Distance")
    plt.xlabel("Number of Candidate Depots (K)")
    plt.ylabel("Average Nearest-Centre Distance (km)")
    plt.xticks(list(K_VALUES))
    plt.grid(alpha=0.25)
    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "kmeans_distance_vs_k.png",
        dpi=200,
    )
    plt.close()

    # Graph 2 — Percentage improvement
    plt.figure(figsize=(10, 6))

    improvement_data = results.dropna(
        subset=["improvement_pct"]
    )

    plt.bar(
        improvement_data["k"],
        improvement_data["improvement_pct"],
        color="#7358DB",
    )

    plt.title("K-Means: Improvement from Adding a Depot")
    plt.xlabel("Number of Candidate Depots (K)")
    plt.ylabel("Reduction in Average Distance (%)")
    plt.xticks(list(K_VALUES))
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "kmeans_improvement_vs_k.png",
        dpi=200,
    )
    plt.close()

    print("\nGraphs created successfully.")


def log_experiments(results):
    """Add the experiment records to the project's experiment log."""

    experiment_rows = []

    for row in results.itertuples(index=False):
        experiment_rows.append({
            "run_id": f"kmeans_k{row.k}_seed{row.seed}",
            "date": date.today().isoformat(),
            "who": "Team 6",
            "what_changed": f"K-Means K={row.k}",
            "main_metric": "mean_nearest_centre_km",
            "value": round(row.mean_km, 6),
            "seed": row.seed,
            "notes": (
                "Completed-booking dataset; "
                "straight-line Haversine distance; "
                "candidate centres only"
            ),
        })

    new_rows = pd.DataFrame(experiment_rows)

    columns = [
        "run_id", "date", "who", "what_changed",
        "main_metric", "value", "seed", "notes",
    ]

    if EXPERIMENT_LOG.exists():
        existing = pd.read_csv(EXPERIMENT_LOG)
    else:
        existing = pd.DataFrame(columns=columns)

    combined = pd.concat(
        [existing, new_rows],
        ignore_index=True,
    )

    # Prevent repeated execution from duplicating identical runs.
    combined = combined.drop_duplicates(
        subset=["run_id"],
        keep="last",
    )

    combined = combined[columns]
    combined.to_csv(EXPERIMENT_LOG, index=False)

    print("Experiment log updated.")


def main():

    print("\n===== TA3 K-MEANS EXPERIMENTS =====")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    coordinates = load_coordinates()

    results = run_experiments(coordinates)
    results = generate_comparison_table(results)

    output_csv = RESULTS_DIR / "kmeans_comparison.csv"

    results.to_csv(output_csv, index=False)

    create_plots(results)
    log_experiments(results)

    print("\n===== FINAL COMPARISON TABLE =====")

    display_columns = [
        "k", "mean_km", "median_km",
        "p90_km", "improvement_pct",
    ]

    print(
        results[display_columns].round(3).to_string(
            index=False
        )
    )

    print(f"\nResults saved to: {output_csv}")
    print(f"Graphs saved to: {PLOTS_DIR}")
    print("\nIMPORTANT: Cluster centres are not final depot sites.")
    print("===== TA3 K-MEANS EXPERIMENT COMPLETE =====")


if __name__ == "__main__":
    main()
