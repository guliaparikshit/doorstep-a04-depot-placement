# A4 — Geospatial Demand Clustering for Micro-Depot Placement

## Project
AI & Machine Learning — Thematic Assessment

**Track:** A — Service as a Service  
**Module:** A4 — Depot Placement

## Team

- **Parikshit Gulia — 231302245** — Team Leader & Data/Project Coordination
- **Mukul Punia — 231302217** — Data Exploration & Preprocessing
- **Siddharth Sehwag — 231302226** — ML / Clustering
- **Nishant Chaudhary — 231302237** — Evaluation, Visualization & Documentation

## Problem

Doorstep provides mobile car-washing services where vans travel to customers. Vans may need to travel long distances to restock water and other supplies, which can waste time and reduce useful service capacity.

Our A4 module studies where booking demand is geographically concentrated and aims to recommend practical locations for micro-depots.

## Objective

The objective is to identify geographical demand clusters from booking locations and study how different depot placements can reduce unnecessary service distance.

## Dataset

The Doorstep project provides multiple connected datasets. For A4, our initial focus is on:

- `bookings.csv`
- `DATA_DICTIONARY.md`

`bookings.csv` contains booking-level information, including geographical information that can be used to study demand locations.

`DATA_DICTIONARY.md` explains the meaning of dataset fields and relationships between the provided files.

## Planned Methodology

1. Understand and clean the booking-location data.
2. Explore and visualise booking locations on a map.
3. Apply K-Means clustering for different values of K.
4. Explore DBSCAN as an alternative clustering method.
5. Study how the number of depots affects service distance.
6. Identify practical and reachable depot locations.
7. Produce the final depot recommendations and supporting map.

## Expected Output

The A4 module is expected to produce:

- `depots.csv` containing proposed depot locations
- A map showing the recommended depot locations

The output is intended to support the A1 Route Planner module.

## Repository Structure

```text
data/        → raw and processed data
src/         → Python source code
notebooks/   → exploratory analysis
results/     → outputs, maps and plots
paper/       → technical paper
