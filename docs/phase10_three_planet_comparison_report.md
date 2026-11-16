# Phase 10 Three-Planet Comparison Report (Workstream D)

## Comparison capability status (backend source of truth)
| Comparison | Enabled | Reason |
|---|---|---|
| Moon–Mars | YES | Validated Moon + Mars inputs available |
| Earth–Moon | NO | No validated Earth elevation raster |
| Earth–Mars | NO | No validated Earth elevation raster |

Earth is only present in `UNAVAILABLE_DATASETS`; it is not in `DATASET_REGISTRY`. `/api/similarity/compare` returns HTTP 409 for any Earth dataset ID.

## Validated comparison result (Moon–Mars, historical baseline)
- TMSI: `49.92285382858792`
- Confidence: HIGH
- Combined distance D: `0.694691295520326`
- Bootstrap mean (1000 reps, 320 m): `49.93214617884011`
- 95% interval: `[42.59005785005729, 57.153579453411744]`
- Strongest matches: slope, local relief
- Reproduced exactly in Phase 10 repeatability test.

## New comparisons (Earth–Moon, Earth–Mars)
**Not available.** Earth remains PENDING; no Earth raster validated; no Earth features calculated; no Earth comparison scores exist. No values are fabricated.

## Preconditions for enabling Earth comparisons
1. Earthdata authentication succeeds locally (user-supplied credentials).
2. NASADEM granule(s) downloaded and checksummed.
3. Earth raster passes all validation gates (file, geospatial, data quality, resolution).
4. Earth enters `DATASET_REGISTRY` as VALIDATED via the validation pipeline (not manual edit).
5. Resolution-compatibility gate passes for each Earth–Moon / Earth–Mars pair.
6. Comparison executed through `compare_terrain` (official methodology); result stored; uncertainty + bootstrap computed.

## Scientific caveat
A validated Earth dataset does not automatically imply every Earth–Moon or Earth–Mars comparison is scientifically compatible. Each pair requires its own resolution-compatibility and coverage checks, per `assess_resolution` (maximum ratio 4.0) and `classify_confidence` (coverage ≥50% minimum).
