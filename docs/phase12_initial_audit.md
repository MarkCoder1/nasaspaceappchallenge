# Phase 12 Initial Audit Report

## 1. Repository state
- Git: single commit `86e958b`. All Phase 1–11 work present as working-tree additions.
- Baseline validation (Phase 11 complete): 74 Python tests passed, compilation clean, ESLint clean (1 pre-existing warning), TypeScript clean, Next.js production build clean.
- Earth remains PENDING (Earthdata authentication blocked); Earth–Moon and Earth–Mars return HTTP 409.

## 2. Existing architecture

### Backend (FastAPI + Pydantic)
- `backend/app/main.py` — FastAPI app, CORS, includes `health` and `similarity` routers.
- `backend/app/api/similarity.py` — routes: `/status`, `/features`, `/methodology`, `/results`, `/raster/{id}`, `/export/{json,csv,pdf}`, `/compare` (POST).
- `backend/app/services/similarity.py` — `DATASET_REGISTRY` (Mars + Moon only), `UNAVAILABLE_DATASETS` (Earth), `compare_dataset_ids()`, `similarity_status()`, `feature_definitions()`, `methodology()`, `stored_experiment()`, `raster_preview_svg()`.
- `backend/app/services/export.py` — `build_export_package()`, `export_json()`, `export_csv()`, `export_pdf()`. Package includes methodology, engine_status, datasets, results, provenance, interpretation.
- `backend/app/schemas/similarity.py` — `SimilarityCompareRequest`, `SimilarityResponse`, `SimilarityStatusResponse`. No comparison metadata (extent, overlap, window coords) in the response schema.
- `backend/tests/` — `test_health.py`, `test_similarity_api.py`, `test_earth_gates.py`, `test_phase10_gates.py`.

### Science engine (`science/`)
- `science/similarity/features/feature_extraction.py` — `extract_terrain_features()`, slope / 60 m local relief / 60 m Riley TRI; `TerrainFeatureSet`.
- `science/similarity/scoring/similarity.py` — `compare_terrain()`: resolution gate, Wasserstein + pooled-IQR, TMSI = 100×exp(−D), confidence, limitations.
- `science/similarity/comparison/uncertainty.py` — `assess_resolution()` (max ratio 4.0), `classify_confidence()`.
- `science/similarity/comparison/bootstrap.py` — spatial block bootstrap (160/320/640 m).
- `science/validation/phase11_experiments.py` — window extraction, overlap detection, comparison runner; outputs `data/metadata/phase11_sampling_framework.json`.
- **No `science/metadata/` directory exists.** No standardized comparison metadata schema or validation module exists.

### Frontend (Next.js 16 / React 19 / Tailwind 4)
- `frontend/app/page.tsx` — renders `ResearchWorkbench`.
- `frontend/components/ResearchWorkbench.tsx` — views: explorer, features, uncertainty, provenance. Displays baseline TMSI, feature distributions, bootstrap, Moran's I, provenance cards, Earth PENDING banner, export buttons.
- `frontend/lib/api.ts` — types: `Experiment`, `BaselineResult`, `FeatureResult`, `BootstrapResult`, `SpatialDiag`, `SimilarityStatus`; functions: `fetchStatus()`, `fetchExperiment()`, `rasterUrl()`, `downloadExport()`. No comparison metadata types (extent, overlap, window coords, sampling strategy).
- `frontend/app/globals.css` — design system: matte black/charcoal, green/amber accents, monospaced values.

### Data
- `data/processed/mars_jezero_ctx_elevation_m.tif` (VALIDATED), `data/processed/moon_lola_80s_20m_elevation_m.tif` (VALIDATED).
- `data/metadata/phase11_sampling_framework.json` — Phase 11 experiment output: within_body (Mars 15, Moon 120), between_body (96), overlap_bias (15), summary stats.
- `data/metadata/phase10_extent_sensitivity.json`, `phase10_benchmark_investigation.json`.

## 3. Existing scientific capabilities (preserved)
- TMSI = 100 × exp(−D), equal weights, pooled-IQR normalization, Wasserstein + KS diagnostics.
- Moon–Mars baseline: TMSI `49.92285382858792`, confidence HIGH, reproducible.
- Resolution compatibility gate (max ratio 4.0); spatial block bootstrap; Moran's I; semivariograms.
- Feature ablation, weight sensitivity, block-size sensitivity, seed sensitivity, convergence.

## 4. Missing metadata (Workstream A gap)
The `SimilarityResponse` schema and `compare_dataset_ids()` do **not** record:
- Comparison ID, experiment identifier, sampling strategy, window selection method.
- Window A/B coordinates (col_off, row_off, n_cells), spatial extent km, CRS per window.
- Overlap ratio, overlap classification (identical/high/partial/none/unknown).
- Terrain coverage %, missing-data %.
- Algorithm version, dataset version, processing timestamp, random seed.

No `science/metadata/` schema/validation/serialization module exists. Exports do not include comparison sampling metadata.

## 5. Missing diagnostics (Workstream B gap)
- No overlap classification module with mathematically defined thresholds.
- No extent-sensitivity communication alongside scores (extent not displayed next to TMSI).
- No sampling-sensitivity inspection (within-body/between-body distributions not in frontend).
- No interpretation safeguards/warnings for overlap, extent mismatch, resolution mismatch, insufficient coverage, missing metadata.

## 6. Frontend gaps (Workstream C gap)
`ResearchWorkbench.tsx` displays only the single Moon–Mars baseline. It does not show:
- Within-body vs between-body TMSI distributions.
- Overlap ratio / window relationship / sampling method per comparison.
- Extent sensitivity warnings.
- Comparison metadata (window coords, CRS, resolution per window).
- Scientific interpretation distinguishing "what it measures" vs "what it does not establish".
- Phase 11 experiment outputs are not consumed by the frontend.

## 7. Test gaps (Workstream D gap)
Existing tests cover: Earth gates, baseline reproduction, resolution gate boundary, reproducibility. No tests cover:
- Metadata schema validation, missing metadata handling, overlap classification.
- Identical-window detection, extent mismatch detection, different-resolution warnings.
- Missing-data handling, export metadata preservation, interpretation safeguards.
- Phase 11 findings reproducibility (identical windows → 100, overlapping identified, etc.).

## 8. Documentation gaps (Workstream E gap)
No `docs/phase12_*` files exist. Required: metadata architecture, overlap diagnostics, extent sensitivity, ResearchWorkbench, scientific validation, final report.

## 9. Backward-compatibility risks
- Adding fields to `SimilarityResponse` schema: additive only, optional fields, existing clients unaffected.
- Changing `compare_dataset_ids()` signature: avoid; extend via optional kwargs or a separate metadata function.
- Frontend: additive views/components only; existing views unchanged.
- Earth PENDING state and HTTP 409 must remain intact.
- Moon–Mars baseline `49.92285382858792` must remain reproducible.

## 10. Implementation sequence
1. Write `docs/phase12_initial_audit.md` (this file).
2. Workstream A: create `science/metadata/` — `schema.py` (Pydantic models), `validation.py` (required-field checks), `serialization.py` (to/from dict).
3. Workstream B: `science/similarity/comparison/overlap.py` — overlap fraction/classification thresholds; `extent.py` — extent sensitivity helpers; integrate into `compare_terrain()` result via optional metadata (additive, schema-compatible).
4. Workstream D: `backend/tests/test_phase12_metadata.py`, `science/tests/test_phase12_overlap.py`, `science/tests/test_phase12_extent.py`, `science/tests/test_phase12_phase11_reproducibility.py`.
5. Workstream C: extend `frontend/lib/api.ts` types; add `SamplingDiagnostics`, `TmsiDistribution`, `InterpretationSafeguards` components to `ResearchWorkbench.tsx`; consume `phase11_sampling_framework.json` via a new backend endpoint or static artifact.
6. Workstream E: write 5 docs + final report.
7. Run all tests + lint + typecheck + build; write final Phase 12 report.

## 11. Audit conclusion
Phase 12 is feasible without breaking existing contracts. The primary additions are additive: a metadata schema module, overlap/extent diagnostics, frontend components consuming existing Phase 11 artifacts, and new tests. Earth remains PENDING; no Earth data fabricated; Moon–Mars baseline preserved.
