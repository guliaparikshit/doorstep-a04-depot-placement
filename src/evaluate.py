"""
Evaluation utilities for A4 — Depot Placement.

This module will be used to analyse clustering results,
depot locations and service-distance behaviour.
"""


def calculate_service_distance(bookings, depots):
    """
    Calculate the distance from each booking location
    to its nearest proposed depot.

    Implementation will be added during evaluation development.
    """
    raise NotImplementedError("Service-distance calculation pending.")


def compare_depot_counts(results):
    """
    Compare service-distance results for different numbers
    of proposed depots.

    This will help determine when adding another depot
    provides only a small additional benefit.
    """
    raise NotImplementedError("Depot-count comparison pending.")


def evaluate_clustering(labels, data):
    """
    Evaluate the quality of clustering results.

    Clustering metrics and analysis will be added
    after the initial data and models are ready.
    """
    raise NotImplementedError("Clustering evaluation pending.")




