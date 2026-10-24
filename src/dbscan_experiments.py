"""
A4 — DBSCAN Clustering Experiments
Team 6 | TA3 — Clustering and Model Evaluation

Tests DBSCAN on a reproducible sample of completed Doorstep bookings.

Outputs:
- DBSCAN experiment comparison CSV
- Cluster-count comparison graph
- Noise-percentage graph
- DBSCAN geographical cluster plot

IMPORTANT:
These are exploratory results, not final depot recommendations.
"""

from pathlib import Path
from datetime import date

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from model import run_dbscan
from evaluate import evaluate_clustering


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "clean_bookings.csv"
RESULTS_DIR = PROJECT_ROOT / "results"
PLOTS_DIR = RESULTS_DIR / "plots"
EXPERIMENT_LOG = PROJECT_ROOT / "experiments.csv"

RANDOM_SEED = 42
SAMPLE_SIZE = 6000
MIN_SAMPLES = 30

# DBSCAN neighbourhood radius, measured in kilometres.
EPS_VALUES = [0.3, 0.5, 0.8, 1.2]


def load_data():
    """Load a reproducible sample of cleaned bookings."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Cleaned dataset missing. Run data_loader.py first."
        )

    df = pd.read_csv(INPUT_FILE)

    required = {"lat", "lng"}
    if not required.issubset(df.columns):
        raise ValueError("Dataset must contain lat and lng.")

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")

    df = df.dropna(subset=["lat", "lng"])
    df = df[
        df["lat"].between(-90, 90)
        & df["lng"].between(-180, 180)
    ].copy()

    if df.empty:
        raise ValueError("No valid booking locations found.")

    sample = df.sample(
        n=min(SAMPLE_SIZE, len(df)),
        random_state=RANDOM_SEED,
    ).copy()

    sample = sample.reset_index(drop=True)

    print(f"Total cleaned bookings: {len(df):,}")
    print(f"DBSCAN experiment sample: {len(sample):,}")
    print(f"Random seed: {RANDOM_SEED}")

    return sample


def run_experiments(coordinates):
    """Test DBSCAN with different neighbourhood radii."""

    records = []
    all_labels = {}

    for eps in EPS_VALUES:

        print(f"\nRunning DBSCAN: eps={eps} km, "
              f"min_samples={MIN_SAMPLES}")

        result = run_dbscan(
            coordinates,
            eps=eps,
            min_samples=MIN_SAMPLES,
        )

        labels = result["labels"]
        all_labels[eps] = labels

        noise_count = int(np.sum(labels == -1))
        noise_pct = 100 * noise_count / len(labels)

        # Quality scores may be undefined for some DBSCAN results.
        quality = evaluate_clustering(
            labels,
            coordinates,
            sample_size=1500,
        )

        records.append({
            "eps_km": eps,
            "min_samples": MIN_SAMPLES,
            "sample_size": len(coordinates),
            "n_clusters": result["n_clusters"],
            "noise_points": noise_count,
            "noise_pct": noise_pct,
            "silhouette": quality["silhouette"],
            "davies_bouldin": quality["davies_bouldin"],
            "seed": RANDOM_SEED,
        })

        print(f"Clusters discovered: {result['n_clusters']}")
        print(f"Noise points: {noise_count:,}")
        print(f"Noise percentage: {noise_pct:.2f}%")

        if quality["silhouette"] is not None:
            print(f"Silhouette: {quality['silhouette']:.3f}")
        else:
            print("Silhouette: Not defined")

    return pd.DataFrame(records), all_labels


def create_comparison_charts(results):
    """Save DBSCAN comparison graphs."""

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # Chart 1: Number of clusters
    plt.figure(figsize=(10, 6))

    plt.plot(
        results["eps_km"],
        results["n_clusters"],
        marker="o",
        linewidth=2.5,
        color="#7655D8",
    )

    plt.title("DBSCAN: Neighbourhood Radius vs Clusters")
    plt.xlabel("Neighbourhood Radius (km)")
    plt.ylabel("Number of Clusters")
    plt.xticks(EPS_VALUES)
    plt.grid(alpha=0.25)
    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "dbscan_clusters_vs_eps.png",
        dpi=200,
    )
    plt.close()

    # Chart 2: Noise percentage
    plt.figure(figsize=(10, 6))

    plt.bar(
        results["eps_km"].map(lambda x: f"{x:g}"),
        results["noise_pct"],
        color="#7655D8",
    )

    plt.title("DBSCAN: Noise Points vs Neighbourhood Radius")
    plt.xlabel("Neighbourhood Radius (km)")
    plt.ylabel("Noise Points (%)")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "dbscan_noise_vs_eps.png",
        dpi=200,
    )
    plt.close()


def create_cluster_plot(coordinates, labels, eps):
    """Visualise one DBSCAN result geographically."""

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    unique_labels = np.unique(labels)
    non_noise = labels != -1

    plt.figure(figsize=(11, 8))

    # All non-noise clusters, coloured by label.
    if np.any(non_noise):
        plt.scatter(
            coordinates[non_noise, 1],
            coordinates[non_noise, 0],
            c=labels[non_noise],
            cmap="tab20",
            s=10,
            alpha=0.65,
            label="Clustered bookings",
        )

    # Noise is shown separately in grey.
    if np.any(~non_noise):
        plt.scatter(
            coordinates[~non_noise, 1],
            coordinates[~non_noise, 0],
            c="grey",
            s=12,
            alpha=0.5,
            label="Noise / isolated bookings",
        )

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(
        f"Doorstep DBSCAN Clusters | eps={eps} km"
    )
    plt.grid(alpha=0.2)
    plt.legend()
    plt.tight_layout()

    output_path = PLOTS_DIR / "dbscan_cluster_map.png"
    plt.savefig(output_path, dpi=200)
    plt.close()

    return output_path


def update_experiment_log(results):
    """Record the actual experimental runs."""

    columns = [
        "run_id", "date", "who", "what_changed",
        "main_metric", "value", "seed", "notes",
    ]

    new_rows = []

    for row in results.itertuples(index=False):

        new_rows.append({
            "run_id": (
                f"dbscan_eps{row.eps_km:g}_"
                f"min{row.min_samples}_"
                f"sample{row.sample_size}_"
                f"seed{row.seed}"
            ),
            "date": date.today().isoformat(),
            "who": "Team 6",
            "what_changed": (
                f"DBSCAN eps={row.eps_km} km; "
                f"min_samples={row.min_samples}"
            ),
            "main_metric": "n_clusters",
            "value": row.n_clusters,
            "seed": row.seed,
            "notes": (
                f"Sample={row.sample_size}; "
                f"noise={row.noise_pct:.2f}%; "
                "exploratory DBSCAN parameter comparison"
            ),
        })

    if EXPERIMENT_LOG.exists():
        existing = pd.read_csv(EXPERIMENT_LOG)
    else:
        existing = pd.DataFrame(columns=columns)

    combined = pd.concat(
        [existing, pd.DataFrame(new_rows)],
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

    print("\nExperiment log updated.")


def main():

    print("\n===== TA3 DBSCAN EXPERIMENTS =====")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    sample = load_data()
    coordinates = sample[["lat", "lng"]].to_numpy(dtype=float)

    results, all_labels = run_experiments(coordinates)

    output_file = RESULTS_DIR / "dbscan_comparison.csv"
    results.to_csv(output_file, index=False)

    create_comparison_charts(results)

    # Use eps=0.5 km for the initial visual illustration.
    # This is not a claim that it is the best parameter.
    plot_path = create_cluster_plot(
        coordinates,
        all_labels[0.5],
        eps=0.5,
    )

    update_experiment_log(results)

    print("\n===== FINAL DBSCAN COMPARISON =====")

    display_columns = [
        "eps_km",
        "min_samples",
        "n_clusters",
        "noise_points",
        "noise_pct",
        "silhouette",
        "davies_bouldin",
    ]

    print(
        results[display_columns]
        .round(3)
        .to_string(index=False)
    )

    print(f"\nComparison saved: {output_file}")
    print(f"Cluster plot saved: {plot_path}")
    print(f"All graphs saved in: {PLOTS_DIR}")

    print(
        "\nNOTE: Results use a reproducible 6,000-booking "
        "sample, not all 39,302 records."
    )
    print("===== DBSCAN EXPERIMENT COMPLETE =====")


if __name__ == "__main__":
    main()
