"""
DEPOTIQ — Cloud Dashboard Summary Export
Team 6 | TA4

Creates public-dashboard aggregate statistics
without publishing individual booking records.
"""

from pathlib import Path
import json

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "data" / "processed" / "clean_bookings.csv"
OUTPUT_FILE = ROOT / "results" / "dashboard_summary.json"


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Cleaned bookings not found. Run data_loader.py first."
        )

    df = pd.read_csv(INPUT_FILE)

    required = {"zone", "area", "date"}

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    # Count geographical demand distribution.
    zone_counts = (
        df["zone"]
        .fillna("Unknown")
        .astype(str)
        .value_counts()
        .sort_index()
    )

    area_counts = (
        df["area"]
        .fillna("Unknown")
        .astype(str)
        .value_counts()
        .sort_values(ascending=False)
    )

    # Convert dates and count completed bookings per month.
    dates = pd.to_datetime(df["date"], errors="coerce")

    monthly_counts = (
        dates.dropna()
        .dt.to_period("M")
        .astype(str)
        .value_counts()
        .sort_index()
    )

    summary = {
        "source": "Doorstep cleaned completed-bookings dataset",
        "description": (
            "Aggregated dashboard information; "
            "individual booking records are not included."
        ),
        "original_bookings": 40660,
        "cleaned_bookings": int(len(df)),
        "excluded_bookings": 40660 - int(len(df)),
        "zones": int(df["zone"].nunique()),
        "areas": int(df["area"].nunique()),
        "bookings_by_zone": {
            str(key): int(value)
            for key, value in zone_counts.items()
        },
        "bookings_by_area": {
            str(key): int(value)
            for key, value in area_counts.items()
        },
        "bookings_by_month": {
            str(key): int(value)
            for key, value in monthly_counts.items()
        },
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    # Basic integrity checks.
    assert sum(summary["bookings_by_zone"].values()) == len(df)
    assert sum(summary["bookings_by_area"].values()) == len(df)

    print("\n===== DEPOTIQ CLOUD SUMMARY =====")
    print(f"Original bookings: {summary['original_bookings']:,}")
    print(f"Cleaned bookings: {summary['cleaned_bookings']:,}")
    print(f"Zones: {summary['zones']}")
    print(f"Areas: {summary['areas']}")

    print("\nBookings by zone:")
    for name, count in summary["bookings_by_zone"].items():
        print(f"  {name}: {count:,}")

    print("\nBookings by area:")
    for name, count in summary["bookings_by_area"].items():
        print(f"  {name}: {count:,}")

    print(f"\nSummary saved to: {OUTPUT_FILE}")
    print("Individual booking records were NOT exported.")
    print("===== EXPORT COMPLETE =====")


if __name__ == "__main__":
    main()
