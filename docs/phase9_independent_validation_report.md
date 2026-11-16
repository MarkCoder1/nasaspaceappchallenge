# Phase 9 Independent Validation Report

## Scope
Independent validation of the TMSI methodology using only the existing validated Moon (LOLA) and Mars (Jezero CTX) rasters. No Earth data is used. Earth remains PENDING (NASADEM acquisition blocked by Earthdata authentication). No results are fabricated.

## Data used
- Mars: `data/processed/mars_jezero_ctx_elevation_m.tif` (20 m, ESRI:103885).
- Moon: `data/processed/moon_lola_80s_20m_elevation_m.tif` (2048×2048, 20 m nominal, 16.056 m effective).
- Stored Phase 7 diagnostics: `data/metadata/moon_mars_phase7_experiments.json`.

## Experiment A — Repeatability (deterministic baseline reproduction)
| Run | TMSI | Confidence |
|---|---|---|
| 1 | 49.92285382858792 | HIGH |
| 2 | 49.92285382858792 | HIGH |

Result: **PASS**. The baseline is deterministic and repeatable; identical inputs produce identical TMSI. The stored Phase 7 baseline `49.92285382858792` is reproduced exactly.

## Experiment B — Resolution compatibility sensitivity
The engine gates comparisons on `effective_resolution_m` ratio with `maximum_ratio = 4.0`.

| Configuration | Target scale (m) | Candidate scale (m) | Ratio | Compatible |
|---|---|---|---|---|
| Official (Mars 20.0 / Moon 16.056) | 20.0 | 16.056 | 1.2456 | True |
| Boundary (Mars 20.0 / Moon-sim 80.0) | 20.0 | 80.0 | 4.0000 | True |
| Beyond boundary (Mars 20.0 / Moon-sim 81.0) | 20.0 | 81.0 | 4.0500 | False |

Result: **PASS**. The resolution gate admits the official Moon–Mars pair, admits the 4.0 boundary, and rejects 4.05. Resolution incompatibility is enforced.

## Experiment C — Spatial-extent sensitivity
| Moon extent | Area | TMSI |
|---|---|---|
| Full validated window | 40.96 km × 40.96 km | 49.92285382858792 |
| Central sub-window | 20.48 km × 20.48 km | 46.44812594080244 |

Delta (full − sub-window): +3.4747.

Result: **Material extent sensitivity confirmed.** Changing the sampled spatial boundary shifts TMSI by ~3.5 points. Results are extent-dependent; extent must be reported alongside any comparison. A derived sub-window raster `data/processed/moon_lola_central_20km_window.tif` was written solely for this experiment and is not a validated science product.

## Experiment D — Feature sensitivity (single-feature ablation)
Reproduces Phase 7 ablation:

| Feature only | TMSI | Combined distance D | Confidence |
|---|---|---|---|
| slope | 50.38759096672298 | 0.6854252522033859 | HIGH |
| local_relief | 50.24460531119791 | 0.6882670018031668 | HIGH |
| terrain_ruggedness | 49.14566058278336 | 0.7103816325544253 | HIGH |
| equal-weight baseline | 49.92285382858792 | 0.694691295520326 | HIGH |

Result: **PASS**. Matches Phase 7 exactly. Ruggedness-only is the lowest (49.1457); slope-only is the highest (50.3876). No single feature dominates enough to invalidate the equal-weight baseline.

## Experiment E — Weight sensitivity
Reproduces Phase 7 weight sensitivity:

| Weight scheme | TMSI | Combined distance D | Confidence |
|---|---|---|---|
| equal (1,1,1) | 49.92285382858792 | 0.694691295520326 | HIGH |
| slope_emphasis (2,1,1) | 50.038634712167976 | 0.692374784691091 | HIGH |
| relief_emphasis (1,2,1) | 50.003098019418736 | 0.6930852220910362 | HIGH |
| ruggedness_emphasis (1,1,2) | 49.72741079949528 | 0.6986138797788508 | HIGH |

Result: **PASS**. Reasonable alternative weights shift TMSI within ~0.3 points of baseline. Conclusions are not hypersensitive to modest weight changes.

## Experiment F — Spatial dependence (block-bootstrap justification)
Moran's I from stored Phase 7 diagnostics:

| Body | Feature | Moran's I |
|---|---|---|
| Mars | slope | 0.979047 |
| Mars | local_relief | 0.982601 |
| Mars | terrain_ruggedness | 0.983469 |
| Moon | slope | 0.989876 |
| Moon | local_relief | 0.994712 |
| Moon | terrain_ruggedness | 0.995272 |

Minimum Moran's I: 0.979047.

Result: **Strong spatial autocorrelation confirmed on all features and both bodies.** Pixels are not independent observations; independent-pixel uncertainty would be invalid. The non-overlapping spatial block bootstrap is justified.

## Experiment G — Bootstrap uncertainty (baseline, 320 m blocks, 64 reps, seed 42)
| Statistic | Value |
|---|---|
| Bootstrap mean TMSI | 49.7380 |
| 95% lower | 42.6599 |
| 95% upper | 56.6150 |
| Baseline TMSI within interval | True |

Result: **PASS**. The deterministic baseline (49.9229) lies within the bootstrap interval, consistent with Phase 7 (1000-rep mean 49.9321, interval [42.5901, 57.1536]).

## Experiment H — Cross-dataset consistency / independent benchmark
Result: **Not attempted — no suitable independent benchmark available.**
- No independently labeled real-world benchmark dataset exists for this comparison.
- Synthetic benchmarks in the registry are marked `kind=synthetic_test_only, production_eligible=false` and are excluded from scientific findings.
- Limitation: independent external validation of TMSI against a published reference remains pending.

## Overall validation verdict
The TMSI methodology is internally consistent, deterministic, resolution-gated, extent-sensitive, feature-balanced, weight-robust, and spatially-dependence-aware. The principal open limitation is the absence of an independent real-world benchmark and the PENDING Earth dataset.
