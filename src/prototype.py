"""
A4 — Initial K-Means Clustering Prototype
Team 6 | TA2 — Initial Implementation

Uses real Doorstep booking locations to demonstrate K-Means
with three geographical demand clusters.

The cluster centres are preliminary candidates, not final depots.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from model import run_kmeans


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "clean_bookings.csv"
OUTPUT_DIR = PROJECT_ROOT / "results" / "plots"


def main():

    print("\n===== A4 K-MEANS PROTOTYPE =====")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Cleaned bookings not found. Run data_loader.py first."
        )

    df = pd.read_csv(INPUT_FILE)
    coordinates = df[["lat", "lng"]].to_numpy(dtype=float)

    print(f"Bookings analysed: {len(coordinates):,}")

    # Initial demonstration with three groups
    result = run_kmeans(
        coordinates,
        n_clusters=3,
        random_state=42,
    )

    labels = result["labels"]
    centres = result["centres"]

    print("\nK-Means successfully completed!")
    print("Number of clusters: 3")

    for cluster_id in range(3):
        count = int(np.sum(labels == cluster_id))
        lat, lng = centres[cluster_id]

        print(
            f"Cluster {cluster_id + 1}: "
            f"{count:,} bookings | "
            f"Centre: {lat:.5f}, {lng:.5f}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Use a reproducible sample for a readable scatter plot.
    rng = np.random.default_rng(42)

    sample_indices = rng.choice(
        len(coordinates),
        size=min(6000, len(coordinates)),
        replace=False,
    )

    sampled_coords = coordinates[sample_indices]
    sampled_labels = labels[sample_indices]

    plt.figure(figsize=(11, 8))

    scatter = plt.scatter(
        sampled_coords[:, 1],
        sampled_coords[:, 0],
        c=sampled_labels,
        cmap="viridis",
        s=9,
        alpha=0.5,
    )

    plt.scatter(
        centres[:, 1],
        centres[:, 0],
        c="red",
        s=220,
        marker="X",
        edgecolors="black",
        linewidths=1.2,
        label="Cluster Centres",
    )

    for i, (lat, lng) in enumerate(centres):
        plt.annotate(
            f"C{i + 1}",
            (lng, lat),
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=11,
            fontweight="bold",
        )

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(
        "Doorstep Demand Clustering — Initial K-Means (K=3)"
    )

    plt.colorbar(scatter, label="Cluster Label")
    plt.legend()
    plt.grid(alpha=0.2)
    plt.tight_layout()

    plot_path = OUTPUT_DIR / "initial_kmeans_clusters.png"

    plt.savefig(plot_path, dpi=200)
    plt.close()

    # Save preliminary centre coordinates separately.
    centre_table = pd.DataFrame(
        {
            "cluster": [1, 2, 3],
            "lat": centres[:, 0],
            "lng": centres[:, 1],
        }
    )

    centre_path = OUTPUT_DIR / "prototype_centres.csv"
    centre_table.to_csv(centre_path, index=False)

    print(f"\nCluster chart saved: {plot_path}")
    print(f"Preliminary centres saved: {centre_path}")

    print("\nIMPORTANT: These are not final depot recommendations.")
    print("===== PROTOTYPE COMPLETE =====")


if __name__ == "__main__":
    main()
