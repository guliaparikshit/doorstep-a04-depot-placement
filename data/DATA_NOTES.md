# A4 Dataset Understanding

## Main Dataset

The primary starting dataset for A4 is bookings.csv.

Each row represents one booking request from the Doorstep service.

## Why bookings.csv is important

A4 is a geographical demand problem. Booking locations help us understand where service demand is concentrated across the city.

Important information for A4 includes geographical information such as latitude and longitude, along with other booking information that may be useful during analysis.

## Data Dictionary

DATA_DICTIONARY.md is the reference document used to understand the meaning of the available fields, relationships between files, and dataset structure.

## Initial Data Checks

Before applying clustering, we will check:

- Missing location values
- Invalid latitude or longitude values
- Duplicate records
- Data types and column structure
- Distribution of booking locations

## Next Step

The next stage is to load bookings.csv, explore its columns and geographical distribution, and prepare the location data for clustering.
