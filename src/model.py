Clustering model module for A4 — Depot Placement.

The module will contain the clustering methods used to identify
geographical demand groups from Doorstep booking locations.
"""


def run_kmeans(data, n_clusters):
    """
    Run K-Means clustering on geographical demand data.

    Parameters
    ----------
    data : array-like
        Booking location data used for clustering.
    n_clusters : int
        Number of clusters to create.

    Returns
    -------
    object
        Clustering result.

    Implementation will be added during the model development stage.
    """
    raise NotImplementedError("K-Means implementation pending.")


def run_dbscan(data, eps, min_samples):
    """
    Run DBSCAN clustering on geographical demand data.

    Parameters
    ----------
    data : array-like
        Booking location data used for clustering.
    eps : float
        Neighbourhood distance parameter.
    min_samples : int
        Minimum number of nearby points required to form a dense region.

    Returns
    -------
    object
        Clustering result.

    Implementation will be added during the model development stage.
    """
    raise NotImplementedError("DBSCAN implementation pending.")
