# A4 → A1 Integration Guide

## Project

A4 — Geospatial Demand Clustering for Micro-Depot Placement

## Purpose

Our A4 module recommends locations for micro-depots based on customer booking demand. These depot locations can be used by the A1 Route Planner when planning van routes.

## Input

Our main input is `bookings.csv`, which contains booking locations using latitude (`lat`) and longitude (`lng`).

## Expected Output

The A4 module will generate `results/depots.csv` containing recommended depot coordinates.

### Proposed CSV Format

| Column | Description |
| --- | --- |
| `lat` | Depot latitude in decimal degrees |
| `lng` | Depot longitude in decimal degrees |

Each row represents one recommended depot location.

## How A1 Will Use It

1. A4 analyses geographical booking demand.
2. A4 recommends suitable depot locations.
3. A4 exports the locations to `results/depots.csv`.
4. A1 reads these coordinates as possible depot locations for route planning.

## Assumptions and Limitations

- Coordinates use decimal degrees.
- The number of depots will be selected after evaluating different options.
- Clustering centres are initial candidates, not automatically verified road-accessible locations.
- Practical accessibility must be checked before final recommendations.
- Straight-line distances are not the same as actual road distances.
- The final schema and integration tests must be confirmed with the A1 team.

## Current Status

This document describes the planned integration. The final depot CSV and A1 integration have not yet been implemented or tested.
