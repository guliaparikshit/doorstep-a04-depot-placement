"""
A4 — Geospatial Demand Clustering for Micro-Depot Placement

Data loading, quality checking, and cleaning.
Team 6 — Doorstep Project
"""

from pathlib import Path
import pandas as pd


# Project folders
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BOOKINGS = PROJECT_ROOT / "data" / "raw" / "bookings.csv"
PROCESSED_FOLDER = PROJECT_ROOT / "data" / "processed"


def load_bookings(file_path=DEFAULT_BOOKINGS):
    """Load the original booking data without modifying the source file."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Bookings file not found: {path}")

    bookings = pd.read_csv(path)

    required_columns = {
        "booking_id", "lat", "lng", "status", "zone", "area"
    }

    missing = required_columns - set(bookings.columns)

    if missing:
        raise ValueError(
            f"Required columns missing: {sorted(missing)}"
        )

    return bookings


def check_data_quality(df):
    """Display basic data-quality information."""

    print("\n===== DOORSTEP DATA QUALITY REPORT =====")

    print(f"Total bookings: {len(df):,}")
    print(f"Total columns: {len(df.columns)}")

    print("\nMissing values in each column:")
    print(df.isnull().sum().to_string())

    print("\nDuplicate booking IDs:")
    print(int(df["booking_id"].duplicated().sum()))

    print("\nBooking status distribution:")
    print(df["status"].value_counts(dropna=False).to_string())

    lat = pd.to_numeric(df["lat"], errors="coerce")
    lng = pd.to_numeric(df["lng"], errors="coerce")

    invalid_coordinates = (
        lat.isna()
        | lng.isna()
        | ~lat.between(-90, 90)
        | ~lng.between(-180, 180)
    )

    print("\nMissing or invalid coordinates:")
    print(int(invalid_coordinates.sum()))

    print("\nUnique geographical zones:")
    print(df["zone"].nunique())

    print("\nUnique areas:")
    print(df["area"].nunique())

    print("\n===== DATA QUALITY REPORT COMPLETE =====")


def clean_bookings(df):
    """
    Prepare completed bookings for initial clustering analysis.

    Steps:
    1. Keep completed bookings.
    2. Remove repeated booking IDs.
    3. Convert coordinates to numbers.
    4. Remove missing or invalid coordinates.
    """

    cleaned = df.copy()

    # Keep completed bookings for our initial analysis
    cleaned = cleaned[
        cleaned["status"] == "completed"
    ].copy()

    # Remove duplicate booking IDs
    cleaned = cleaned.drop_duplicates(
        subset=["booking_id"],
        keep="first"
    )

    # Convert coordinates to numeric values
    cleaned["lat"] = pd.to_numeric(
        cleaned["lat"], errors="coerce"
    )

    cleaned["lng"] = pd.to_numeric(
        cleaned["lng"], errors="coerce"
    )

    # Remove missing coordinates
    cleaned = cleaned.dropna(subset=["lat", "lng"])

    # Keep geographically valid coordinates
    cleaned = cleaned[
        cleaned["lat"].between(-90, 90)
        & cleaned["lng"].between(-180, 180)
    ].copy()

    # Reset row numbering
    cleaned = cleaned.reset_index(drop=True)

    return cleaned


def save_cleaned_data(df):
    """Save cleaned bookings as a separate CSV file."""

    PROCESSED_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = PROCESSED_FOLDER / "clean_bookings.csv"

    df.to_csv(output_path, index=False)

    return output_path


def main():
    """Run the complete loading and cleaning process."""

    # Step 1 — Load original data
    bookings = load_bookings()

    print("\nSuccessfully loaded Doorstep bookings!")

    # Step 2 — Examine data quality
    check_data_quality(bookings)

    # Step 3 — Clean bookings
    cleaned = clean_bookings(bookings)

    # Step 4 — Save cleaned dataset
    output_path = save_cleaned_data(cleaned)

    # Step 5 — Final summary
    print("\n===== DATA CLEANING SUMMARY =====")

    print(f"Original bookings: {len(bookings):,}")
    print(f"Cleaned bookings: {len(cleaned):,}")

    removed = len(bookings) - len(cleaned)

    print(f"Excluded records: {removed:,}")

    print("\nCleaned booking statuses:")
    print(cleaned["status"].value_counts().to_string())

    print("\nFirst 5 cleaned records:")
    print(cleaned.head(5).to_string(index=False))

    print(f"\nCleaned dataset saved to:\n{output_path}")

    print("\n===== CLEANING COMPLETED =====")


if __name__ == "__main__":
    main()
