"""
A4 — Geographical Booking Demand Map
Team 6 | TA2 — Exploratory Data Analysis

Creates an interactive map showing real Doorstep booking locations.

Outputs:
    results/plots/booking_demand_map.html
"""

from pathlib import Path
from html import escape

import folium
import pandas as pd
from folium.plugins import HeatMap, MarkerCluster


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "clean_bookings.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "results" / "plots"

OUTPUT_FILE = OUTPUT_DIR / "booking_demand_map.html"


# --------------------------------------------------
# Load and validate data
# --------------------------------------------------

def load_cleaned_bookings():
    """Load cleaned customer bookings and check their coordinates."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Cleaned dataset not found. "
            "Please run src/data_loader.py first."
        )

    df = pd.read_csv(INPUT_FILE)

    required_columns = {
        "booking_id", "lat", "lng", "area", "zone"
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")

    df = df.dropna(subset=["lat", "lng"]).copy()

    df = df[
        df["lat"].between(-90, 90)
        & df["lng"].between(-180, 180)
    ].copy()

    if df.empty:
        raise ValueError("No valid booking coordinates found.")

    return df


# --------------------------------------------------
# Create interactive map
# --------------------------------------------------

def create_booking_map():
    """Create the Doorstep booking-demand heatmap."""

    print("\n===== A4 BOOKING MAP GENERATOR =====")

    df = load_cleaned_bookings()

    centre_lat = float(df["lat"].median())
    centre_lng = float(df["lng"].median())

    print(f"Total valid bookings: {len(df):,}")
    print(f"Map centre: {centre_lat:.5f}, {centre_lng:.5f}")

    # Start without default OpenStreetMap tiles.
    booking_map = folium.Map(
        location=[centre_lat, centre_lng],
        zoom_start=11,
        tiles=None,
        control_scale=True,
        prefer_canvas=True,
    )

    # Esri street-map background.
    folium.TileLayer(
        tiles=(
            "https://server.arcgisonline.com/ArcGIS/rest/"
            "services/World_Street_Map/MapServer/tile/"
            "{z}/{y}/{x}"
        ),
        attr="Tiles &copy; Esri and contributors",
        name="Esri Street Map",
        overlay=False,
        control=True,
        show=True,
        max_zoom=19,
    ).add_to(booking_map)

    # Optional blank background if an online provider is blocked.
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
        attr="&copy; OpenStreetMap contributors &copy; CARTO",
        name="Alternative Light Map",
        overlay=False,
        control=True,
        show=False,
    ).add_to(booking_map)

    # Heatmap uses all cleaned booking coordinates.
    heatmap_layer = folium.FeatureGroup(
        name="Booking Demand Heatmap",
        show=True,
    )

    HeatMap(
        data=df[["lat", "lng"]].values.tolist(),
        radius=12,
        blur=16,
        min_opacity=0.25,
    ).add_to(heatmap_layer)

    heatmap_layer.add_to(booking_map)

    # Show a reproducible sample of individual bookings.
    sample = df.sample(
        n=min(1200, len(df)),
        random_state=42,
    )

    marker_layer = folium.FeatureGroup(
        name="Sample Booking Markers",
        show=False,
    )

    marker_cluster = MarkerCluster(
        name="Booking Markers",
    ).add_to(marker_layer)

    for row in sample.itertuples(index=False):
        booking_id = escape(str(row.booking_id))
        area = escape(str(row.area))
        zone = escape(str(row.zone))

        popup_html = (
            f"<b>Booking:</b> {booking_id}<br>"
            f"<b>Area:</b> {area}<br>"
            f"<b>Zone:</b> {zone}"
        )

        folium.Marker(
            location=[float(row.lat), float(row.lng)],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip="Doorstep booking",
        ).add_to(marker_cluster)

    marker_layer.add_to(booking_map)

    # Add a small project information box.
    info_html = """
    <div style="
        position: fixed;
        bottom: 30px;
        left: 50px;
        z-index: 9999;
        background: rgba(13, 19, 49, 0.94);
        color: white;
        padding: 12px 16px;
        border-radius: 10px;
        font-family: Arial, sans-serif;
        box-shadow: 0 3px 12px rgba(0,0,0,.2);
        max-width: 260px;
    ">
        <b style="font-size: 15px;">
            Doorstep | A4 Demand Map
        </b>
        <div style="font-size: 12px; margin-top: 6px;">
            Heatmap: all cleaned completed bookings
        </div>
        <div style="font-size: 12px; margin-top: 4px;">
            Markers: reproducible sample of 1,200
        </div>
        <div style="font-size: 11px; margin-top: 6px;">
            Team 6 | Exploratory Data Analysis
        </div>
    </div>
    """

    booking_map.get_root().html.add_child(
        folium.Element(info_html)
    )

    folium.LayerControl(
        collapsed=False,
    ).add_to(booking_map)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    booking_map.save(str(OUTPUT_FILE))

    print("\nHeatmap generated from all cleaned bookings.")
    print(f"Individual markers: {len(sample):,}")
    print(f"Map saved to: {OUTPUT_FILE}")
    print("\n===== MAP GENERATION COMPLETE =====")


if __name__ == "__main__":
    create_booking_map()
