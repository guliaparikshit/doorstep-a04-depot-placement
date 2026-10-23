"""
A4 — Geospatial Demand Clustering for Micro-Depot Placement.

Clustering algorithms for Doorstep booking locations.
Team 6 | AI & ML Thematic Assessment

K-Means uses projected coordinates in kilometres so that
Euclidean distances are approximately meaningful locally.
DBSCAN uses haversine distances directly on Earth coordinates.
"""

import numpy as np
from sklearn.cluster import KMeans, DBSCAN


EARTH_RADIUS_KM = 6371.0088


def project_coordinates(data):
    """
    Convert latitude/longitude into approximate local kilometre coordinates.

    Suitable for a city-scale clustering prototype, not road distances.
    """
    coordinates = np.asarray(data, dtype=float)

    if coordinates.ndim != 2 or coordinates.shape[1] != 2:
        raise ValueError("Data must have two columns: latitude and longitude.")

    if not np.isfinite(coordinates).all():
        raise ValueError("Coordinates contain missing or invalid numbers.")

    latitude = np.radians(coordinates[:, 0])
    longitude = np.radians(coordinates[:, 1])

    reference_lat = np.mean(latitude)
    reference_lng = np.mean(longitude)

    x = EARTH_RADIUS_KM * (longitude - reference_lng) * np.cos(reference_lat)
    y = EARTH_RADIUS_KM * (latitude - reference_lat)

    return np.column_stack((x, y)), reference_lat, reference_lng


def unproject_coordinates(centres, reference_lat, reference_lng):
    """Convert projected K-Means centres back to latitude and longitude."""
    x = centres[:, 0]
    y = centres[:, 1]

    latitude = np.degrees(y / EARTH_RADIUS_KM + reference_lat)
    longitude = np.degrees(
        x / (EARTH_RADIUS_KM * np.cos(reference_lat)) + reference_lng
    )

    return np.column_stack((latitude, longitude))


def run_kmeans(data, n_clusters=3, random_state=42):
    """
    Apply K-Means to customer booking coordinates.

    Returns a dictionary containing labels, depot candidates
    and the fitted model.
    """
    coordinates = np.asarray(data, dtype=float)

    if not 1 <= n_clusters <= len(coordinates):
        raise ValueError("Invalid number of clusters.")

    projected, ref_lat, ref_lng = project_coordinates(coordinates)

    model = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=10
    )

    labels = model.fit_predict(projected)

    centres = unproject_coordinates(
        model.cluster_centers_, ref_lat, ref_lng
    )

    return {
        "labels": labels,
        "centres": centres,
        "model": model,
        "inertia": model.inertia_
    }


def run_dbscan(data, eps=1.0, min_samples=10):
    """
    Apply DBSCAN using geographical distances.

    eps is expressed in kilometres.
    Label -1 represents noise or isolated points.
    """
    coordinates = np.asarray(data, dtype=float)

    if coordinates.ndim != 2 or coordinates.shape[1] != 2:
        raise ValueError("Data must have latitude and longitude columns.")

    if not np.isfinite(coordinates).all():
        raise ValueError("Coordinates contain invalid values.")

    if eps <= 0 or min_samples < 1:
        raise ValueError("eps must be positive and min_samples >= 1.")

    radians = np.radians(coordinates)

    model = DBSCAN(
        eps=eps / EARTH_RADIUS_KM,
        min_samples=min_samples,
        metric="haversine",
        algorithm="ball_tree"
    )

    labels = model.fit_predict(radians)

    return {
        "labels": labels,
        "model": model,
        "n_clusters": len(set(labels) - {-1}),
        "noise_points": int(np.sum(labels == -1))
    }
