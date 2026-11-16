# Phase 10 Sampling Sensitivity Report (Workstream C)

## Objective
Investigate how spatial-extent (terrain sampling window) affects the stability and interpretability of the TMSI. Phase 9 identified a 3.47-point shift between full (40.96 km) and sub-window (20.48 km) Moon; Phase 10 systematizes this across multiple extents.

## Method
Centered square windows of equal physical extent extracted from BOTH validated rasters (Mars Jezero CTX DTM, Moon LOLA subset). For each extent where both datasets cover the area:
1. Extract window from Mars and Moon at 20 m nominal spacing.
2. Compute slope, 60 m local relief, 60 m Riley TRI.
3. Compute Wasserstein + pooled-IQR normalized distances, combined D, TMSI.
4. Compute spatial block bootstrap (320 m, 64 reps, seed 42) for 95% uncertainty.
5. Record valid coverage.

Equal weights (slope=local_relief=terrain_ruggedness=1.0). No raster upsampling.

## Mars coverage constraint
Mars raster: 1596 × 1512 cells = 31.92 km × 30.24 km.
Moon raster: 2048 × 2048 cells = 40.96 km × 40.96 km.
Extents exceeding Mars coverage (30.72 km, 40.96 km) cannot be compared fairly and are skipped.

## Results

| Extent (km) | Cells | TMSI | Confidence | Combined D | Boot mean | 95% lower | 95% upper |
|---|---|---|---|---|---|---|---|
| 5.12 | 256 | 23.7099 | HIGH | 1.4393 | 22.8115 | 14.0817 | 31.8306 |
| 10.24 | 512 | 27.7206 | HIGH | 1.2830 | 25.3366 | 18.8116 | 32.8372 |
| 20.48 | 1024 | 46.4041 | HIGH | 0.7678 | 43.7518 | 36.6632 | 50.2544 |
| Full (ref) | — | 49.9229 | HIGH | 0.6947 | 49.7380 | 42.6599 | 56.6150 |

30.72 km and 40.96 km: not comparable (exceed Mars coverage). Recorded as skipped.

## Key findings
1. **TMSI is strongly extent-dependent.** Range across comparable extents: 23.71 → 49.92 (Δ ≈ 26.2 points). Small windows (≤10.24 km) produce substantially lower TMSI than full extent.
2. **Bootstrap intervals do not capture extent-driven variability.** Each extent's 95% interval reflects block-resampling variability within that fixed extent, NOT the across-extent shift. The interval at 5.12 km [14.08, 31.83] does not overlap the full-extent estimate 49.92 — demonstrating extent is a structural choice, not sampling noise.
3. **Valid coverage is 100%** at all tested extents (both rasters fully valid in their windows), so the effect is not driven by missing data.
4. **Feature distances shrink with extent** (combined D: 1.4393 at 5.12 km → 0.6947 at full), meaning small windows exaggerate perceived morphological differences.

## Recommended sampling strategy (experimental)
1. **Fixed physical-area windows.** Use the largest common square extent supported by all datasets in a comparison (here ~30 km, limited by Mars height). Report it explicitly.
2. **Do not compare across extents.** A TMSI from a 10 km window is not comparable to one from a 40 km window.
3. **Prefer larger extents (≥20 km)** where coverage permits; small windows are dominated by local heterogeneity and understate similarity.
4. **Non-overlapping windows** for same-body self-consistency checks (overlap inflates TMSI; observed up to 83.32 for overlapping Moon windows).
5. **State the Mars coverage limit.** Mars Jezero extent (31.92×30.24 km) caps the common comparison window.

This strategy is offered as an experimental option. The official Phase 7 baseline (full validated extents) remains unchanged.

## Data artifact
Raw per-extent results: `data/metadata/phase10_extent_sensitivity.json`. Temporary window rasters created during the experiment were deleted; they are not validated products and are not registered in `DATASET_REGISTRY`.
