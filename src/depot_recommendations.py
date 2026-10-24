"""
DEPOTIQ — A4 Micro-Depot Placement
Team 6 | TA4 — Depot Recommendation Engine

Generates candidate micro-depot locations using K-Means.

Workflow:
1. Load cleaned Doorstep bookings.
2. Run K-Means clustering.
3. Find an observed booking coordinate near each cluster centre.
4. Assign every booking to its nearest candidate.
5. Export proposed coordinates and evaluation results.
6. Generate an interactive depot-location map.

IMPORTANT:
Candidate locations are not verified operational depot sites.
Booking coordinates are used only as spatial reference points.
Road access, land use, permissions and costs need later validation.
"""

from pathlib import Path
import argparse

import folium
from folium.plugins import HeatMap
import numpy as np
import pandas as pd

from model import run_kmeans, project_coordinates
from evaluate import calculate_service_distance


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "clean_bookings.csv"

RESULTS_DIR = PROJECT_ROOT / "results"
PLOTS_DIR = RESULTS_DIR / "plots"

EARTH_RADIUS_KM = 6371.0088
DEFAULT_K = 5
RANDOM_SEED = 42


def load_booking_locations():
    """Read cleaned bookings and validate coordinates."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Cleaned bookings missing. Run src/data_loader.py first."
        )

    df = pd.read_csv(INPUT_FILE)

    required = {"booking_id", "lat", "lng"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")

    df = df.dropna(subset=["lat", "lng"]).copy()

    df = df[
        df["lat"].between(-90, 90)
        & df["lng"].between(-180, 180)
    ].reset_index(drop=True)

    if df.empty:
        raise ValueError("No valid booking coordinates found.")

    return df


def select_candidate_sites(coordinates, centres):
    """
    Choose a distinct observed coordinate near each K-Means centre.

    A centre is a mathematical average that may fall in an
    unsuitable location. Observed booking coordinates are
    used as provisional spatial anchors instead.

    This DOES NOT verify road accessibility or depot eligibility.
    """

    projected, reference_lat, reference_lng = project_coordinates(
        coordinates
    )

    centre_lat = np.radians(centres[:, 0])
    centre_lng = np.radians(centres[:, 1])

    centre_x = (
        EARTH_RADIUS_KM
        * (centre_lng - reference_lng)
        * np.cos(reference_lat)
    )

    centre_y = (
        EARTH_RADIUS_KM
        * (centre_lat - reference_lat)
    )

    projected_centres = np.column_stack((centre_x, centre_y))

    # Find the nearest distinct observed coordinate to each centre.
    selected_indices = []
    used_coordinates = set()

    for centre in projected_centres:

        squared_distances = np.sum(
            (projected - centre) ** 2,
            axis=1,
        )

        for index in np.argsort(squared_distances):
            candidate = tuple(coordinates[index])

            if candidate not in used_coordinates:
                selected_indices.append(int(index))
                used_coordinates.add(candidate)
                break
        else:
            raise ValueError(
                "Not enough unique locations for the requested depots."
            )

    return coordinates[selected_indices]


def calculate_candidate_statistics(coordinates, candidates):
    """Assign bookings to nearest candidate and calculate coverage."""

    booking_lat = np.radians(coordinates[:, 0])
    booking_lng = np.radians(coordinates[:, 1])

    nearest_distances = np.full(len(coordinates), np.inf)
    nearest_candidate = np.full(len(coordinates), -1, dtype=int)

    for i, candidate in enumerate(candidates):

        candidate_lat = np.radians(candidate[0])
        candidate_lng = np.radians(candidate[1])

        delta_lat = booking_lat - candidate_lat
        delta_lng = booking_lng - candidate_lng

        a = (
            np.sin(delta_lat / 2) ** 2
            + np.cos(booking_lat)
            * np.cos(candidate_lat)
            * np.sin(delta_lng / 2) ** 2
        )

        a = np.clip(a, 0, 1)

        distances = (
            2 * EARTH_RADIUS_KM
            * np.arcsin(np.sqrt(a))
        )

        improved = distances < nearest_distances

        nearest_distances[improved] = distances[improved]
        nearest_candidate[improved] = i

    records = []

    for i, (lat, lng) in enumerate(candidates):

        mask = nearest_candidate == i
        cluster_distances = nearest_distances[mask]

        records.append({
            "depot_id": f"D{i + 1}",
            "lat": round(float(lat), 7),
            "lng": round(float(lng), 7),
            "assigned_bookings": int(mask.sum()),
            "mean_distance_km": (
                round(float(cluster_distances.mean()), 4)
                if len(cluster_distances) else np.nan
            ),
            "p90_distance_km": (
                round(float(np.percentile(cluster_distances, 90)), 4)
                if len(cluster_distances) else np.nan
            ),
            "site_status": "provisional_unverified",
        })

    return pd.DataFrame(records), nearest_distances


def create_depot_map(bookings, depots):
    """Create interactive HTML map with demand and depot candidates."""

    coordinates = bookings[["lat", "lng"]].to_numpy(dtype=float)

    centre_lat = float(np.median(coordinates[:, 0]))
    centre_lng = float(np.median(coordinates[:, 1]))

    map_obj = folium.Map(
        location=[centre_lat, centre_lng],
        zoom_start=11,
        tiles=None,
        control_scale=True,
    )

    # Background map provider used successfully during TA2.
    folium.TileLayer(
        tiles=(
            "https://server.arcgisonline.com/ArcGIS/rest/"
            "services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
        ),
        attr="Tiles &copy; Esri and contributors",
        name="Street Map",
        overlay=False,
        show=True,
    ).add_to(map_obj)

    heat_layer = folium.FeatureGroup(
        name="Booking Demand Heatmap",
        show=True,
    )

    HeatMap(
        data=coordinates.tolist(),
        radius=12,
        blur=16,
        min_opacity=0.25,
    ).add_to(heat_layer)

    heat_layer.add_to(map_obj)

    depot_layer = folium.FeatureGroup(
        name="Provisional Depot Candidates",
        show=True,
    )

    for row in depots.itertuples(index=False):

        popup = (
            f"<b>{row.depot_id}</b><br>"
            f"Assigned bookings: {row.assigned_bookings:,}<br>"
            f"Mean distance: {row.mean_distance_km:.2f} km<br>"
            "<b>Provisional site — not road-verified</b>"
        )

        folium.Marker(
            location=[row.lat, row.lng],
            tooltip=f"{row.depot_id} — provisional candidate",
            popup=folium.Popup(popup, max_width=260),
            icon=folium.Icon(
                color="red",
                icon="home",
            ),
        ).add_to(depot_layer)

    depot_layer.add_to(map_obj)

    folium.LayerControl(collapsed=False).add_to(map_obj)

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    output = PLOTS_DIR / "recommended_depots_map.html"
    map_obj.save(str(output))

    return output


def generate_recommendations(k=DEFAULT_K):
    """Run the complete provisional depot recommendation pipeline."""

    print("\n===== DEPOTIQ — DEPOT RECOMMENDATIONS =====")

    bookings = load_booking_locations()
    coordinates = bookings[["lat", "lng"]].to_numpy(dtype=float)

    unique_count = len(np.unique(coordinates, axis=0))
    if not 1 <= k <= unique_count:
        raise ValueError(
            f"K must be between 1 and {unique_count}."
        )

    print(f"Bookings analysed: {len(bookings):,}")
    print(f"Requested candidate depots: {k}")

    clustering = run_kmeans(
        coordinates,
        n_clusters=k,
        random_state=RANDOM_SEED,
    )

    candidates = select_candidate_sites(
        coordinates,
        clustering["centres"],
    )

    depots, distances = calculate_candidate_statistics(
        coordinates,
        candidates,
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    depot_file = RESULTS_DIR / "depots.csv"
    depots.to_csv(depot_file, index=False)

    map_file = create_depot_map(bookings, depots)

    # Verify nearest-depot distances using the shared evaluation module.
    checked_distances = calculate_service_distance(
        coordinates,
        candidates,
    )

    if not np.allclose(
        distances,
        checked_distances,
        atol=1e-7,
    ):
        raise AssertionError("Distance calculation verification failed.")

    print("\n===== CANDIDATE DEPOT TABLE =====")
    print(depots.to_string(index=False))

    print("\n===== COVERAGE SUMMARY =====")
    print(f"Mean distance: {distances.mean():.3f} km")
    print(f"Median distance: {np.median(distances):.3f} km")
    print(f"P90 distance: {np.percentile(distances, 90):.3f} km")

    print(f"\nDepot CSV: {depot_file}")
    print(f"Interactive map: {map_file}")

    print(
        "\nIMPORTANT: Sites are provisional spatial candidates, "
        "not verified physical depots."
    )
    print("===== RECOMMENDATION GENERATION COMPLETE =====")

    return depots


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Generate provisional A4 depot candidates."
    )

    parser.add_argument(
        "--k",
        type=int,
        default=DEFAULT_K,
        help="Number of provisional candidate depots (default: 5).",
    )

    args = parser.parse_args()
    generate_recommendations(k=args.k)
