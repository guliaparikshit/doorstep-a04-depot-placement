# A4 → A1 Integration Guide

## Project
**A4:** Geospatial Demand Clustering for Micro-Depot Placement  
**Team:** Team 6  
**Track:** A — Service as a Service  
**Application:** DEPOTIQ

## 1. Purpose

Our A4 module analyses geographical Doorstep booking demand and recommends provisional micro-depot locations.

The A1 Route Planner can use these candidate locations as geographical inputs for route-planning experiments.

## 2. Input Dataset

The A4 module uses:

- data/raw/bookings.csv
- data/processed/clean_bookings.csv

We analysed 40,660 original bookings and retained 39,302 completed bookings for clustering.

Original data is preserved without modification.

## 3. Main Output

File: results/depots.csv

Columns:

- depot_id: Candidate identifier
- lat: Latitude in decimal degrees
- lng: Longitude in decimal degrees
- assigned_bookings: Number of bookings assigned to the nearest candidate
- mean_distance_km: Average straight-line distance for assigned bookings
- p90_distance_km: 90th-percentile straight-line distance
- site_status: Verification status

## 4. A1 Handover Output

File: results/depots_for_a1.csv

Schema:

depot_id,lat,lng

Coordinates use WGS84 decimal degrees.

The current file contains five provisional candidate locations.

This is a proposed handover schema. The A1 team must confirm that it matches their expected input format.

## 5. How to Regenerate

Install project dependencies:

    python -m pip install -r requirements.txt

Generate provisional depot candidates:

    python src/depot_recommendations.py --k 5

Export coordinates for A1:

    python src/export_a1.py

Launch the dashboard:

    python -m streamlit run app.py

## 6. Current Results

Planning scenario: K=5

- Completed bookings analysed: 39,302
- Provisional candidates: 5
- Mean nearest-candidate distance: 2.037 km
- Median distance: 1.887 km
- P90 distance: 3.592 km

Distances are geographical straight-line estimates, not driving distances.

K=5 is a planning scenario, not a proven economically optimal depot count.

## 7. Integration Checks

Completed in A4:

- Candidate coordinate generation
- Coordinate validation
- Unique depot IDs
- CSV export
- Five-row handover file generated

Pending with A1:

- Confirm expected input column names
- Confirm coordinate system and units
- Test importing the handover CSV into the A1 Route Planner
- Test route generation using exported candidate depots

## 8. Important Limitations

The candidate coordinates are selected using observed booking locations near K-Means centres.

They are not verified physical depot properties.

Before real deployment, the following must be checked:

- Road accessibility
- Legal permission and land suitability
- Availability of water and supplies
- Parking and loading space
- Operating and rental costs

The current solution is an academic geographical planning prototype, not a production routing or logistics system.

## 9. Next Integration Milestone

Share results/depots_for_a1.csv with the A1 team and perform a real import test.

Document any schema changes, failed tests and integration outcomes before marking A1 integration complete.
