"""
DEPOTIQ — A4 to A1 Integration Export
Team 6 | TA4

Exports provisional depot coordinates for the A1 Route Planner.
No road accessibility or operating suitability is implied.
"""

from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "results" / "depots.csv"
OUTPUT = ROOT / "results" / "depots_for_a1.csv"


def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            "results/depots.csv not found. "
            "Run depot_recommendations.py first."
        )

    df = pd.read_csv(INPUT)

    required = ["depot_id", "lat", "lng"]

    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    export = df[required].copy()

    if export.empty:
        raise ValueError("No depot candidates to export.")

    for col in ["lat", "lng"]:
        export[col] = pd.to_numeric(
            export[col], errors="raise"
        )

    if (
        export[required].isna().any().any()
        or export["depot_id"].duplicated().any()
        or not export["lat"].between(-90, 90).all()
        or not export["lng"].between(-180, 180).all()
    ):
        raise ValueError("Invalid or duplicate depot records.")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    export.to_csv(OUTPUT, index=False)

    print("\n===== A4 TO A1 INTEGRATION =====")
    print(export.to_string(index=False))
    print(f"\nExported {len(export)} provisional depot candidates.")
    print(f"Saved to: {OUTPUT}")
    print("Coordinates are WGS84 decimal degrees.")
    print("These are NOT verified road-accessible sites.")
    print("===== EXPORT COMPLETE =====")


if __name__ == "__main__":
    main()
