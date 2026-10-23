"""
A4 — Doorstep Booking Data Visualisation
Team 6 | TA2 — Exploratory Data Analysis

Creates three charts from the cleaned booking dataset.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "clean_bookings.csv"
OUTPUT_DIR = PROJECT_ROOT / "results" / "plots"

sns.set_theme(style="whitegrid")


def load_data():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Cleaned dataset not found. Run src/data_loader.py first."
        )
    return pd.read_csv(INPUT_FILE)


def plot_area_bookings(df):
    """Chart 1: Completed bookings in each area."""

    counts = df["area"].value_counts().sort_values()

    plt.figure(figsize=(11, 6))
    ax = sns.barplot(
        x=counts.values,
        y=counts.index,
        color="#7358DB"
    )

    ax.set_title("Completed Doorstep Bookings by Area", fontsize=16)
    ax.set_xlabel("Number of Bookings")
    ax.set_ylabel("Area")

    for i, value in enumerate(counts.values):
        ax.text(value + 35, i, f"{value:,}", va="center")

    plt.xlim(0, counts.max() * 1.16)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "bookings_by_area.png", dpi=180)
    plt.close()


def plot_zone_bookings(df):
    """Chart 2: Completed bookings across geographical zones."""

    counts = df["zone"].value_counts().sort_values(ascending=False)

    plt.figure(figsize=(9, 6))
    ax = sns.barplot(
        x=counts.index.astype(str),
        y=counts.values,
        color="#7358DB"
    )

    ax.set_title("Completed Doorstep Bookings by Zone", fontsize=16)
    ax.set_xlabel("Zone")
    ax.set_ylabel("Number of Bookings")

    for bar, value in zip(ax.patches, counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 100,
            f"{value:,}",
            ha="center"
        )

    plt.ylim(0, counts.max() * 1.15)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "bookings_by_zone.png", dpi=180)
    plt.close()


def plot_monthly_bookings(df):
    """Chart 3: Monthly completed bookings over time."""

    dates = pd.to_datetime(df["date"], errors="coerce")

    monthly = (
        df.loc[dates.notna()]
        .assign(month=dates[dates.notna()].dt.to_period("M"))
        .groupby("month")
        .size()
    )

    plt.figure(figsize=(12, 6))
    plt.plot(
        monthly.index.astype(str),
        monthly.values,
        marker="o",
        linewidth=2.5,
        color="#7358DB"
    )

    plt.title("Monthly Completed Doorstep Bookings", fontsize=16)
    plt.xlabel("Month")
    plt.ylabel("Number of Bookings")
    plt.xticks(rotation=45, ha="right")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "monthly_bookings.png", dpi=180)
    plt.close()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()

    print(f"Loaded {len(df):,} cleaned bookings.")

    plot_area_bookings(df)
    print("Created: bookings_by_area.png")

    plot_zone_bookings(df)
    print("Created: bookings_by_zone.png")

    plot_monthly_bookings(df)
    print("Created: monthly_bookings.png")

    print("\nAll three visualisations generated successfully!")
    print(f"Saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
