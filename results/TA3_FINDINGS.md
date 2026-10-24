# TA3 — Clustering and Model Evaluation

## Project Information

**Project:** A4 — Geospatial Demand Clustering for Micro-Depot Placement  
**Track:** A — Service as a Service  
**Team:** Team 6  
**Assessment:** TA3 — Clustering and Model Evaluation

## 1. Objective

The objective of TA3 was to evaluate geographical demand clustering using K-Means and DBSCAN and study how the number of proposed micro-depots affects customer-to-depot distance.

## 2. Dataset

- Original booking records: 40,660
- Completed bookings used for initial analysis: 39,302
- Excluded records: 1,358 (1,344 no-shows and 14 records marked duplicate)
- Valid coordinate records in the original dataset: 40,660

The source dataset is kept unchanged. Clustering uses the cleaned completed-bookings dataset.

## 3. K-Means: K=1 to K=10

We tested ten depot counts using all 39,302 cleaned bookings, with random seed 42.

| K | Mean distance (km) | Improvement from previous K (%) |
|---|---:|---:|
| 1 | 6.197 | — |
| 2 | 4.138 | 33.226 |
| 3 | 3.240 | 21.703 |
| 4 | 2.534 | 21.798 |
| 5 | 2.028 | 19.947 |
| 6 | 1.784 | 12.031 |
| 7 | 1.621 | 9.146 |
| 8 | 1.485 | 8.371 |
| 9 | 1.385 | 6.757 |
| 10 | 1.309 | 5.473 |

### Interpretation

Increasing K reduces the mean distance to the nearest candidate depot. The additional benefit generally becomes smaller at higher K.

The graph suggests investigating approximately five or six depots as potential trade-off points, but it does not establish an economically optimal depot count.

## 4. DBSCAN Experiments

We ran DBSCAN on a reproducible sample of 6,000 completed bookings with min_samples=30 and random seed 42.

| eps (km) | Clusters | Noise (%) | Silhouette | Davies–Bouldin |
|---|---:|---:|---:|---:|
| 0.3 | 17 | 60.583 | 0.154 | 0.567 |
| 0.5 | 13 | 23.433 | 0.530 | 0.653 |
| 0.8 | 4 | 5.150 | 0.490 | 0.477 |
| 1.2 | 2 | 0.500 | 0.570 | 0.379 |

### Interpretation

As the neighbourhood radius increases, nearby demand groups merge and the proportion labelled as noise decreases.

Silhouette and Davies–Bouldin results must be interpreted carefully because noise points were excluded when calculating clustering-quality scores.

No DBSCAN setting is declared universally best.

## 5. K-Means Reliability

We repeated selected K-Means experiments across ten random seeds (42–51), using all 39,302 completed bookings.

| K | Runs | Mean distance (km) | Standard deviation (km) |
|---|---:|---:|---:|
| 3 | 10 | 3.2400 | 0.0000 |
| 5 | 10 | 2.0284 | 0.0000 |
| 6 | 10 | 1.7842 | 0.0001 |
| 8 | 10 | 1.4854 | 0.0001 |

### Interpretation

The measured nearest-centre distances varied very little across the ten tested seeds. This indicates stable results for these configurations and this dataset.

It does not establish stability under changes in demand, different datasets, or real road-accessibility restrictions.

## 6. K-Means vs DBSCAN: Common-Sample Comparison

We tested both algorithms on the same 6,000 booking locations.

- K-Means: K=4
- DBSCAN: eps=0.8 km, min_samples=30
- Each method produced four clusters under these settings.

| Metric | K-Means | DBSCAN |
|---|---:|---:|
| Clusters | 4 | 4 |
| Noise (%) | 0.00 | 5.15 |
| Mean nearest-centre distance (km) | 2.522 | 3.242 |
| Median distance (km) | 2.272 | 2.879 |
| 90th-percentile distance (km) | 4.585 | 5.881 |
| Silhouette on common non-noise subset | 0.550 | 0.490 |

### Interpretation

Under the tested settings, K-Means achieved approximately 22.2% lower mean nearest-candidate distance than DBSCAN.

However, K-Means used mathematical cluster centroids, whereas DBSCAN used actual booking locations selected as representatives of each cluster.

These are not identical depot-selection methods, so the difference should not be interpreted as a universal algorithm ranking.

The distance metric included every booking in the shared sample, including DBSCAN noise points. Silhouette scores were calculated on a common non-noise subset.

## 7. Evaluation Metrics

- **Mean nearest-centre distance:** Average straight-line geographical distance between each booking and its closest candidate location.
- **Median distance:** Middle nearest-centre distance across bookings.
- **90th-percentile distance:** Distance within which 90% of booking-to-nearest-candidate distances fall.
- **Silhouette score:** Estimates how well-separated and compact the clusters are; higher is generally better.
- **Davies–Bouldin index:** Measures cluster similarity and spread; lower is generally better.
- **Noise percentage:** Proportion of bookings DBSCAN labelled as isolated/noise.
- **Standard deviation across seeds:** Measures variation in a result under different random initialisations.

## 8. Key Limitations

1. We measured geographical straight-line distances, not actual road travel distances.
2. K-Means centres are mathematical positions, not verified depot properties.
3. Our initial modelling includes completed bookings only; other definitions of customer demand should also be tested.
4. K-Means full-dataset experiments and standalone DBSCAN sample experiments have different dataset sizes.
5. The common-sample comparison uses one set of selected algorithm parameters.
6. Distance reduction alone does not account for depot construction, rental, refilling or operating costs.
7. Booking locations come from the faculty-provided Doorstep dataset; any simulation or planted data patterns must be described based on the supplied data dictionary.
8. The presented candidate centres have not been verified for road accessibility.

## 9. Preliminary Conclusion

K-Means is a promising initial method for generating a specified number of candidate micro-depot locations. DBSCAN provides useful information about naturally dense geographical demand regions and isolated bookings.

Increasing depot count reduces geographical distance, but the final number and locations should be selected only after economic and practical validation.

No final depot count or verified depot locations are claimed in TA3.

## 10. Generated Evidence

- `results/kmeans_comparison.csv`
- `results/dbscan_comparison.csv`
- `results/kmeans_reliability_runs.csv`
- `results/kmeans_reliability_summary.csv`
- `results/model_comparison.csv`
- `results/plots/kmeans_distance_vs_k.png`
- `results/plots/kmeans_improvement_vs_k.png`
- `results/plots/dbscan_clusters_vs_eps.png`
- `results/plots/dbscan_noise_vs_eps.png`
- `results/plots/dbscan_cluster_map.png`
- `results/plots/kmeans_seed_reliability.png`
- `results/plots/kmeans_vs_dbscan_distance.png`
- `results/plots/kmeans_vs_dbscan_clusters.png`
- `experiments.csv`

## 11. Next Stage — TA4

Next, the project will focus on selecting practical depot candidates, validating accessibility, exporting `results/depots.csv`, testing the full pipeline, developing the Streamlit dashboard and preparing the final documentation and demonstration.
