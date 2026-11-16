# Phase 11 Audit Report

## 1. Repository state
- Git: single commit `86e958b`. All Phase 1–10 work present as working-tree additions.
- Baseline validation: 58 Python tests passed, compilation clean, ESLint clean (1 pre-existing warning), TypeScript clean, Next.js production build clean.
- No Phase 11 work started (no `phase11_*` docs or source changes exist).

## 2. Datasets
| Planet | Dataset | Local file | State |
|---|---|---|---|
| Mars | Jezero CTX DTM | `data/processed/mars_jezero_ctx_elevation_m.tif` | VALIDATED |
| Moon | LOLA-derived DEM subset | `data/processed/moon_lola_80s_20m_elevation_m.tif` | VALIDATED |
| Earth | NASADEM HGT v001 | none acquired | PENDING |

- Mars raster: 1596 × 1512 cells, 20 m spacing → 31.92 km × 30.24 km
- Moon raster: 2048 × 2048 cells, 20 m spacing → 40.96 km × 40.96 km
- No Earth raster exists. Earthdata authentication blocked (`credentials_unavailable`).
- Phase 10 experiment artifacts present: `phase10_extent_sensitivity.json`, `phase10_benchmark_investigation.json` (experiment outputs, not validated products).

## 3. Backend comparison gates (source of truth)
- `DATASET_REGISTRY`: only `mars_jezero_ctx_dtm` and `moon_lola` (VALIDATED). Earth absent.
- `comparison_capabilities`: `earth_mars` disabled, `earth_moon` disabled, `moon_mars` enabled.
- `production_comparisons_enabled=False`; `validated_comparisons=["moon_mars"]`.
- `/api/similarity/compare` returns HTTP 409 for any Earth dataset ID.
- Official Moon–Mars baseline: TMSI `49.92285382858792`, confidence HIGH.

## 4. Phase 10 findings (reused, not re-run)
Spatial-extent sensitivity (`data/metadata/phase10_extent_sensitivity.json`):

| Extent (km) | Cells | TMSI | Combined D |
|---|---|---|---|
| 5.12 | 256 | 23.7099 | 1.4393 |
| 10.24 | 512 | 27.7206 | 1.2830 |
| 20.48 | 1024 | 46.4041 | 0.7678 |
| Full (ref) | — | 49.9229 | 0.6947 |

30.72 km and 40.96 km skipped (exceed Mars coverage). Score varies ~26 points across comparable extents.

Same-body benchmark (`data/metadata/phase10_benchmark_investigation.json`):
- Moon center vs northwest (20.48 km, overlapping): TMSI 58.1318
- Moon center vs southeast (20.48 km, overlapping): TMSI 83.3207
- Moon northwest vs southeast (20.48 km, non-overlapping): TMSI 54.8968
- Mars center vs northwest (10.24 km, overlapping): TMSI 56.1800
- Mars center vs southeast (10.24 km, overlapping): TMSI 65.5092
- Mars northwest vs southeast (10.24 km, non-overlapping): TMSI 46.5452
- Cross-body Moon–Mars (ref): TMSI 49.9229

No independent external benchmark obtainable (Earth blocked; alternatives require auth or exceed download limits).

## 5. Scientific engine (preserved, not modified)
- `feature_extraction.py`: slope, 60 m local relief, 60 m Riley TRI; requires one band + CRS.
- `scoring/similarity.py`: `compare_terrain` — resolution gate, Wasserstein + pooled-IQR normalization, equal weights, TMSI = 100×exp(−D).
- `comparison/bootstrap.py`: spatial block bootstrap (160/320/640 m).
- `comparison/uncertainty.py`: `assess_resolution` (max ratio 4.0), `classify_confidence`.
- `compare_dataset_ids`: backend entry point; rejects Earth / unavailable / self-comparison with HTTP 409.

## 6. Audit conclusion
**Earth remains PENDING** — no authentic NASADEM, no Earth comparisons enabled. All Phase 11 work uses only the validated Moon and Mars rasters. Phase 10 extent-sensitivity and same-body benchmark results are directly reusable as Experiment D and as prior evidence. No Phase 11 source changes exist yet; experiments and docs will be added incrementally without modifying the official TMSI baseline.
