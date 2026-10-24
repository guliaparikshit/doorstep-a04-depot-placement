"""
A4 — K-Means vs DBSCAN Comparison
Team 6 | TA3 — Clustering and Model Evaluation

Compare K-Means and DBSCAN using the SAME 6,000 booking locations.

K-Means:
    K = 4

DBSCAN:
    eps = 0.8 km
    min_samples = 30

Metrics:
    - Number of clusters
    - Noise percentage
    - Mean nearest-centre distance
    - Median nearest-centre distance
    - 90th percentile distance
    - Silhouette score (common non-noise subset)

IMPORTANT:
Distances are straight-line geographical estimates, not road distances.
Cluster centres are candidates, not final depot recommendations.
"""

from pathlib import Path
from datetime import date

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.metrics import silhouette_score

from model import (
    run_kmeans,
    run_dbscan,
    project_coordinates,
)

from evaluate import distance_summary


# --------------------------------------------------
# Project configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "clean_bookings.csv"
)

RESULTS_DIR = PROJECT_ROOT / "results"
PLOTS_DIR = RESULTS_DIR / "plots"
EXPERIMENT_LOG = PROJECT_ROOT / "experiments.csv"

SAMPLE_SIZE = 6000
RANDOM_SEED = 42

KMEANS_K = 4

DBSCAN_EPS = 0.8
DBSCAN_MIN_SAMPLES = 30


# --------------------------------------------------
# Load identical booking sample
# --------------------------------------------------

def load_sample():
    """Select a reproducible sample for both algorithms."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Cleaned dataset missing. Run data_loader.py first."
        )

    df = pd.read_csv(INPUT_FILE)

    required = {"lat", "lng"}

    if not required.issubset(df.columns):
        raise ValueError("Missing latitude or longitude columns.")

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")

    df = df.dropna(subset=["lat", "lng"])

    df = df[
        df["lat"].between(-90, 90)
        & df["lng"].between(-180, 180)
    ].copy()

    sample = df.sample(
        n=min(SAMPLE_SIZE, len(df)),
        random_state=RANDOM_SEED,
    ).reset_index(drop=True)

    print(f"Original cleaned bookings: {len(df):,}")
    print(f"Comparison sample: {len(sample):,}")

    return sample[["lat", "lng"]].to_numpy(dtype=float)


# --------------------------------------------------
# DBSCAN representative locations
# --------------------------------------------------

def get_dbscan_representatives(coordinates, labels):
    """
    Select one actual booking location from each DBSCAN cluster.

    For each cluster:
    1. Find its average projected position.
    2. Select the booking closest to that average.

    These are preliminary representative locations, not
    road-accessibility-verified depots.
    """

    projected, _, _ = project_coordinates(coordinates)

    centres = []

    cluster_ids = sorted(set(labels) - {-1})

    for cluster_id in cluster_ids:

        indices = np.flatnonzero(labels == cluster_id)

        cluster_points = projected[indices]

        centre = cluster_points.mean(axis=0)

        squared_distances = np.sum(
            (cluster_points - centre) ** 2,
            axis=1,
        )

        closest_index = indices[
            np.argmin(squared_distances)
        ]

        centres.append(coordinates[closest_index])

    if not centres:
        return np.empty((0, 2), dtype=float)

    return np.asarray(centres, dtype=float)


# --------------------------------------------------
# Silhouette on identical subset
# --------------------------------------------------

def common_subset_silhouette(
    coordinates,
    kmeans_labels,
    dbscan_labels,
):
    """
    Evaluate both label assignments on the same DBSCAN
    non-noise booking points.

    The sample is limited for efficient silhouette calculation.
    """

    covered_indices = np.flatnonzero(dbscan_labels != -1)

    if len(covered_indices) < 3:
        return None, None

    rng = np.random.default_rng(RANDOM_SEED)

    if len(covered_indices) > 1500:
        covered_indices = rng.choice(
            covered_indices,
            size=1500,
            replace=False,
        )

    subset = coordinates[covered_indices]

    projected, _, _ = project_coordinates(subset)

    km_labels = kmeans_labels[covered_indices]
    db_labels = dbscan_labels[covered_indices]

    def safe_silhouette(labels):

        n_clusters = len(np.unique(labels))

        if not 2 <= n_clusters < len(labels):
            return None

        return float(
            silhouette_score(projected, labels)
        )

    return (
        safe_silhouette(km_labels),
        safe_silhouette(db_labels),
    )


# --------------------------------------------------
# Run both algorithms
# --------------------------------------------------

def compare_models(coordinates):
    """Run both algorithms and calculate comparable distances."""

    print("\n===== RUNNING K-MEANS =====")

    kmeans_result = run_kmeans(
        coordinates,
        n_clusters=KMEANS_K,
        random_state=RANDOM_SEED,
    )

    km_centres = kmeans_result["centres"]
    km_labels = kmeans_result["labels"]

    km_distances = distance_summary(
        coordinates,
        km_centres,
    )

    print(f"K-Means clusters: {len(km_centres)}")
    print(f"Mean distance: {km_distances['mean_km']:.3f} km")

    print("\n===== RUNNING DBSCAN =====")

    dbscan_result = run_dbscan(
        coordinates,
        eps=DBSCAN_EPS,
        min_samples=DBSCAN_MIN_SAMPLES,
    )

    db_labels = dbscan_result["labels"]

    db_centres = get_dbscan_representatives(
        coordinates,
        db_labels,
    )

    n_noise = int(np.sum(db_labels == -1))

    noise_percentage = (
        100 * n_noise / len(coordinates)
    )

    print(f"DBSCAN clusters: {len(db_centres)}")
    print(f"DBSCAN noise: {noise_percentage:.2f}%")

    if len(db_centres) == 0:
        raise ValueError(
            "DBSCAN found no clusters at these parameters."
        )

    # Calculate coverage distance on ALL identical sample points.
    # Noise bookings are included in the DBSCAN distance calculation.
    db_distances = distance_summary(
        coordinates,
        db_centres,
    )

    print(f"Mean distance: {db_distances['mean_km']:.3f} km")

    # Use an identical DBSCAN-covered subset for quality scores.
    km_sil, db_sil = common_subset_silhouette(
        coordinates,
        km_labels,
        db_labels,
    )

    records = [
        {
            "algorithm": "K-Means",
            "clusters": len(km_centres),
            "noise_pct": 0.0,
            "mean_km": km_distances["mean_km"],
            "median_km": km_distances["median_km"],
            "p90_km": km_distances["p90_km"],
            "silhouette_common": km_sil,
        },
        {
            "algorithm": "DBSCAN",
            "clusters": len(db_centres),
            "noise_pct": noise_percentage,
            "mean_km": db_distances["mean_km"],
            "median_km": db_distances["median_km"],
            "p90_km": db_distances["p90_km"],
            "silhouette_common": db_sil,
        },
    ]

    return (
        pd.DataFrame(records),
        km_centres,
        db_centres,
    )


# --------------------------------------------------
# Save visual comparisons
# --------------------------------------------------

def create_charts(results):
    """Create visual comparison charts."""

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    algorithms = results["algorithm"].tolist()

    # Chart 1: Average geographical distance
    plt.figure(figsize=(9, 6))

    bars = plt.bar(
        algorithms,
        results["mean_km"],
        color=["#7456DA", "#16A6B6"],
        width=0.5,
    )

    for bar, value in zip(bars, results["mean_km"]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.04,
            f"{value:.3f} km",
            ha="center",
        )

    plt.title("K-Means vs DBSCAN: Nearest-Centre Distance")
    plt.ylabel("Average Straight-Line Distance (km)")
    plt.ylim(0, results["mean_km"].max() * 1.2)
    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "kmeans_vs_dbscan_distance.png",
        dpi=200,
    )

    plt.close()

    # Chart 2: Cluster count
    plt.figure(figsize=(9, 6))

    bars = plt.bar(
        algorithms,
        results["clusters"],
        color=["#7456DA", "#16A6B6"],
        width=0.5,
    )

    for bar, value in zip(bars, results["clusters"]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            str(int(value)),
            ha="center",
        )

    plt.title("Clusters Discovered by Each Algorithm")
    plt.ylabel("Number of Clusters")
    plt.ylim(0, max(results["clusters"]) * 1.25)
    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "kmeans_vs_dbscan_clusters.png",
        dpi=200,
    )

    plt.close()

    print("\nComparison graphs generated.")


# --------------------------------------------------
# Update experiment history
# --------------------------------------------------

def update_experiment_log(results):
    """Record model comparison results."""

    columns = [
        "run_id", "date", "who", "what_changed",
        "main_metric", "value", "seed", "notes",
    ]

    records = []

    for row in results.itertuples(index=False):

        model_name = (
            "kmeans" if row.algorithm == "K-Means"
            else "dbscan"
        )

        records.append({
            "run_id": (
                f"comparison_{model_name}_"
                f"sample{SAMPLE_SIZE}_seed{RANDOM_SEED}"
            ),
            "date": date.today().isoformat(),
            "who": "Team 6",
            "what_changed": (
                "K-Means K=4"
                if model_name == "kmeans"
                else "DBSCAN eps=0.8 km, min_samples=30"
            ),
            "main_metric": "mean_nearest_centre_km",
            "value": round(row.mean_km, 6),
            "seed": RANDOM_SEED,
            "notes": (
                f"Actual clusters={row.clusters}; "
                f"noise={row.noise_pct:.2f}%; "
                "same 6000-booking sample; "
                "straight-line Haversine distance; "
                "DBSCAN represented by nearest booking to cluster mean"
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


# --------------------------------------------------
# Main pipeline
# --------------------------------------------------

def main():

    print("\n===== TA3 MODEL COMPARISON =====")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    coordinates = load_sample()

    results, km_centres, db_centres = compare_models(
        coordinates
    )

    results_file = RESULTS_DIR / "model_comparison.csv"

    results.to_csv(results_file, index=False)

    create_charts(results)
    update_experiment_log(results)

    print("\n===== FINAL MODEL COMPARISON =====")

    print(
        results.round(3).to_string(index=False)
    )

    print(f"\nResults saved: {results_file}")
    print(f"K-Means candidate centres: {len(km_centres)}")
    print(f"DBSCAN representative points: {len(db_centres)}")

    if len(km_centres) != len(db_centres):
        print(
            "\nCAUTION: Cluster counts differ. "
            "Distance results also reflect different "
            "numbers of candidate locations."
        )

    print(
        "\nIMPORTANT: Candidate locations are not "
        "validated road-accessible depot sites."
    )

    print("\n===== COMPARISON COMPLETE =====")


if __name__ == "__main__":
    main()
