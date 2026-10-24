"""
A4 — Depot Placement Evaluation
Team 6 | TA3 — Clustering and Model Evaluation

Evaluate geographical depot coverage and clustering quality.

Important:
Distances are straight-line geographical estimates (km),
NOT actual road-travel distances.
"""

import numpy as np

from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
)

from model import project_coordinates


EARTH_RADIUS_KM = 6371.0088


def validate_coordinates(data):
    """Validate latitude-longitude data."""

    coordinates = np.asarray(data, dtype=float)

    if coordinates.ndim != 2 or coordinates.shape[1] != 2:
        raise ValueError(
            "Coordinates must have two columns: lat and lng."
        )

    if len(coordinates) == 0:
        raise ValueError("Coordinates cannot be empty.")

    if not np.isfinite(coordinates).all():
        raise ValueError("Coordinates contain invalid numbers.")

    if (
        np.any(np.abs(coordinates[:, 0]) > 90)
        or np.any(np.abs(coordinates[:, 1]) > 180)
    ):
        raise ValueError("Latitude or longitude is outside valid limits.")

    return coordinates


def calculate_service_distance(bookings, depots):
    """
    Find distance from each booking to its nearest depot.

    Returns one nearest-depot distance per booking, in km.
    Uses the Haversine formula.
    """

    bookings = validate_coordinates(bookings)
    depots = validate_coordinates(depots)

    booking_lat = np.radians(bookings[:, 0])
    booking_lng = np.radians(bookings[:, 1])

    depot_lat = np.radians(depots[:, 0])
    depot_lng = np.radians(depots[:, 1])

    nearest_distances = np.full(
        len(bookings),
        np.inf,
        dtype=float,
    )

    # Loop through depots to avoid building a huge
    # booking-by-depot matrix in memory.
    for lat, lng in zip(depot_lat, depot_lng):

        delta_lat = booking_lat - lat
        delta_lng = booking_lng - lng

        a = (
            np.sin(delta_lat / 2) ** 2
            + np.cos(booking_lat)
            * np.cos(lat)
            * np.sin(delta_lng / 2) ** 2
        )

        a = np.clip(a, 0.0, 1.0)

        distances = (
            2 * EARTH_RADIUS_KM
            * np.arcsin(np.sqrt(a))
        )

        nearest_distances = np.minimum(
            nearest_distances,
            distances,
        )

    return nearest_distances


def distance_summary(bookings, depots):
    """Calculate useful nearest-depot distance statistics."""

    distances = calculate_service_distance(
        bookings, depots
    )

    return {
        "mean_km": float(np.mean(distances)),
        "median_km": float(np.median(distances)),
        "p90_km": float(np.percentile(distances, 90)),
        "max_km": float(np.max(distances)),
        "total_km": float(np.sum(distances)),
    }


def compare_depot_counts(results):
    """
    Compare depot counts using average nearest-depot distance.

    results: list of dictionaries containing
    'k' and 'mean_km'.

    Returns records with absolute and percentage improvement.
    """

    if not results:
        raise ValueError("No depot-count results supplied.")

    ordered = sorted(results, key=lambda row: row["k"])

    comparisons = []
    previous_mean = None

    for row in ordered:
        k = int(row["k"])
        mean_km = float(row["mean_km"])

        if previous_mean is None:
            improvement_km = None
            improvement_pct = None
        else:
            improvement_km = previous_mean - mean_km
            improvement_pct = (
                100 * improvement_km / previous_mean
                if previous_mean > 0 else None
            )

        comparisons.append({
            "k": k,
            "mean_km": mean_km,
            "improvement_km": improvement_km,
            "improvement_pct": improvement_pct,
        })

        previous_mean = mean_km

    return comparisons


def evaluate_clustering(labels, data, sample_size=3000):
    """
    Evaluate clustering quality using a reproducible sample.

    Silhouette score:
        Higher is generally better (maximum 1).

    Davies-Bouldin score:
        Lower is generally better.

    Noise points labelled -1 are excluded from
    clustering-quality calculations.
    """

    coordinates = validate_coordinates(data)
    labels = np.asarray(labels)

    if len(labels) != len(coordinates):
        raise ValueError(
            "Number of labels must match number of bookings."
        )

    valid_mask = labels != -1

    valid_coords = coordinates[valid_mask]
    valid_labels = labels[valid_mask]

    n_clusters = len(np.unique(valid_labels))
    noise_points = int(np.sum(~valid_mask))

    result = {
        "n_clusters": n_clusters,
        "noise_points": noise_points,
        "silhouette": None,
        "davies_bouldin": None,
    }

    if n_clusters < 2 or len(valid_coords) <= n_clusters:
        return result

    # Use projected kilometre coordinates,
    # not raw latitude-longitude values.
    projected, _, _ = project_coordinates(
        valid_coords
    )

    # Sampling avoids expensive calculations on
    # all 39,302 points.
    if len(projected) > sample_size:
        rng = np.random.default_rng(42)
        sample_indices = rng.choice(
            len(projected),
            size=sample_size,
            replace=False,
        )

        projected = projected[sample_indices]
        valid_labels = valid_labels[sample_indices]

    sampled_clusters = len(np.unique(valid_labels))

    if sampled_clusters < 2 or sampled_clusters >= len(projected):
        return result

    result["silhouette"] = float(
        silhouette_score(projected, valid_labels)
    )

    result["davies_bouldin"] = float(
        davies_bouldin_score(projected, valid_labels)
    )

    return result


if __name__ == "__main__":

    print("===== A4 EVALUATION MODULE TEST =====")

    example_bookings = np.array([
        [28.48, 77.08],
        [28.50, 77.10],
        [28.42, 77.02],
    ])

    example_depots = np.array([
        [28.49, 77.09],
        [28.43, 77.03],
    ])

    summary = distance_summary(
        example_bookings,
        example_depots,
    )

    print("Example nearest-depot distance statistics:")

    for name, value in summary.items():
        print(f"{name}: {value:.3f}")

    print("\nEvaluation functions executed successfully.")
