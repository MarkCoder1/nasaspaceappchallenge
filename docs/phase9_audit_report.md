# Phase 9 Audit Report

## 1. Repository state
- Git: single commit `86e958b` (Initial commit from Create Next App). Working tree contains all Phase 1–8 work as untracked/modified additions (backend/, data/, docs/, frontend/, science/, test_datasets.py).
- Existing validation: 30 Python tests passed, Python compilation clean, ESLint clean (1 pre-existing warning), TypeScript clean, Next.js production build clean.

## 2. Datasets
| Planet | Dataset | Local file | State |
|---|---|---|---|
| Mars | Jezero CTX DTM | `data/processed/mars_jezero_ctx_elevation_m.tif` | VALIDATED |
| Moon | LOLA-derived DEM subset | `data/processed/moon_lola_80s_20m_elevation_m.tif` | VALIDATED |
| Earth | NASADEM HGT v001 | none acquired | PENDING |

- No Earth raster exists in `data/raw` or `data/processed`.
- Mars raster: `JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif` (9,662,387 bytes).
- Moon raster: 2048×2048 LOLA south-polar window.

## 3. Earthdata / NASADEM acquisition
- `science/data_ingestion/earthdata_auth.py`: diagnostic-only helpers (`diagnose_earthdata_auth`, `login_interactive`). No credentials stored or logged.
- `science/data_ingestion/cmr.py`: CMR granule lookup for collection `C2763264762-LPCLOUD`, ROI bbox `-68,-24,-67,-23` (Atacama region). Produces `data/metadata/earth_nasadem_cmr.json`.
- `science/data_ingestion/download_data.py`: bounded downloader (refuses files >100 MB, refuses to overwrite existing files, writes SHA-256 provenance). Requires a `download_url`; Earth catalog entry has `download_url=None` because protected granules require Earthdata auth.
- `science/data_ingestion/dataset_catalog.py`: `earth_nasadem_hgt_v001` marked `selected=True, state=PENDING`, `download_url=None`.
- `data/metadata/earth_nasadem_cmr.json`: 8 granules identified (NASADEM_HGT_s23w067/068, s24w068/069, s25w067/068/069, s23w069), all on `lp-prod-protected` requiring Earthdata OAuth.
- `data/metadata/earthdata_authentication_diagnostic.json`: `status=credentials_unavailable`, `client_installed=true`, `credential_strategy=environment`, message `LoginStrategyUnavailable`.
- `data/metadata/earth_nasadem_hgt_v001.json`: `state=PENDING`, `access_status=BLOCKED_BY_EARTHDATA_AUTHENTICATION`, access attempt redirected to Earthdata OAuth returning HTTP 401 without credentials.

## 4. Backend
- `backend/app/services/similarity.py` `DATASET_REGISTRY` contains only `mars_jezero_ctx_dtm` and `moon_lola` (both VALIDATED). Earth is only in `UNAVAILABLE_DATASETS`.
- `comparison_capabilities`: `earth_mars` disabled, `earth_moon` disabled, `moon_mars` enabled.
- `production_comparisons_enabled`: False. `validated_comparisons`: `["moon_mars"]`.
- `/api/similarity/compare` rejects Earth dataset IDs with HTTP 409.
- Official Moon–Mars baseline TMSI: `49.92285382858792`, confidence HIGH, preserved in `data/metadata/moon_mars_phase7_experiments.json`.

## 5. Frontend
- `frontend/components/ResearchWorkbench.tsx`: explorer/features/uncertainty/provenance views, Earth PENDING banner, export buttons (JSON/CSV/PDF), Moon↔Mars results.
- Earth shown as PENDING; Earth comparisons disabled.

## 6. Scientific engine
- `science/similarity/features/feature_extraction.py`: slope (degrees, metre-per-pixel), 60 m local relief, 60 m Riley TRI; requires one band and a CRS; `describe_coordinate_system` enforces Mars CRS naming for Mars bodies.
- `science/similarity/scoring/similarity.py`: `compare_terrain` — resolution compatibility gate, Wasserstein + pooled-IQR normalization, equal weights, TMSI = 100×exp(−D), confidence classification, optional bootstrap + block-size sensitivity.
- Coordinate-system check is Mars-specific (`"Mars" in wkt`); no Earth CRS branch exists yet.

## 7. Phase 7 validation artifacts
- `data/metadata/moon_mars_phase7_experiments.json`: baseline, bootstrap convergence (64/256/1000), seed sensitivity, block-size sensitivity (160/320/640 m), feature ablation, weight sensitivity, Moran's I, semivariograms, normalization sensitivity, benchmarks (synthetic test-only), provenance, interpretation.

## 8. Audit conclusion
**Earth cannot be acquired in this session.** Earthdata authentication is unavailable (`LoginStrategyUnavailable`, environment strategy) and protected LP DAAC granules return HTTP 401 without credentials. No alternate DEM was substituted. Per the Phase 9 directive, Earth remains PENDING and no three-planet comparison is claimed.

**Independent validation work that does NOT require Earth data** can and will proceed using the existing validated Moon and Mars rasters: resolution sensitivity, spatial-extent sensitivity, feature sensitivity, weight sensitivity, spatial dependence (block-bootstrap justification), and cross-dataset consistency. These strengthen the methodology independent of Earth integration.
