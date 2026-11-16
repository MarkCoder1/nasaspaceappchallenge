# Terra Twin — Phase 22: Baseline Report

## 1. Executive Summary

Phase 22 (Scientific Novelty & Original Contribution Validation) establishes a baseline for assessing whether the Terrain Morphology Similarity Index (TMSI) methodology offers an original methodological contribution beyond existing planetary terrain-comparison approaches.

This document records the repository state, the authoritative TMSI implementation, the exact feature set, normalization procedures, weights, distribution metrics, and all prior documentation as of the start of Phase 22.

**No previous results or source data have been modified.** All Phase 17–21 deliverables are preserved intact.

## 2. Repository State

### 2.1 Git State

- **Repository root:** `/Users/markadam/Desktop/NASA SPACE APP CHALLENGE/nasaspaceapp`
- **Current branch:** `main`
- **Last commit:** `86e958b` (Initial commit from Create Next App)
- **Working tree status:** All project files are untracked

### 2.2 Repository Structure (Relevant Components)

| Directory | Contents |
|-----------|----------|
| `science/similarity/scoring/similarity.py` | TMSI computation: `compare_terrain()` |
| `science/similarity/comparison/distance.py` | Distribution distances: Wasserstein, KS, pooled IQR, normalized distance |
| `science/similarity/comparison/bootstrap.py` | Spatial block bootstrap CI, seed sensitivity analysis |
| `science/similarity/features/feature_extraction.py` | Terrain feature extraction: slope, local relief, terrain ruggedness |
| `science/similarity/features/slope.py` | Slope computation |
| `science/similarity/features/local_relief.py` | Local relief computation |
| `science/similarity/features/terrain_ruggedness.py` | Riley TRI computation |
| `science/similarity/scoring/weights.py` | Weight validation |
| `science/similarity/comparison/uncertainty.py` | Resolution assessment, confidence classification |
| `science/similarity/comparison/distribution.py` | Feature layer comparison |
| `science/similarity/comparison/extent.py` | Extent sensitivity diagnostics |
| `science/similarity/comparison/overlap.py` | Overlap bias diagnostics |
| `science/data_ingestion/acquire_earth_dem.py` | Earth DEM acquisition pipeline |
| `science/earth_normalization.py` | Earth DEM resolution normalization |
| `science/datasets/registry.py` | Candidate registry with status transitions |
| `science/datasets/registry.json` | Candidate catalog |
| `data/raw/` | Raw source DEMs (USGS 3DEP tiles, Mars Jezero CTX DTM, Moon LOLA) |
| `data/processed/` | Processed DEMs and metadata |
| `data/metadata/` | Comparison result JSONs for Phases 20–20.6 |
| `docs/` | 70+ documentation files from Phases 3–21 |

## 3. Authoritative TMSI Implementation

### 3.1 TMSI Mathematical Formula

The Terrain Morphology Similarity Index (TMSI) is computed as follows:

**Step 1 — Feature Extraction:** For each raster, extract three terrain morphology features:
- **Slope:** Gradient magnitude via central differences, converted to degrees
- **Local Relief:** Maximum − minimum elevation in a complete square window (60 m physical window, 3×3 cells at 20 m resolution)
- **Terrain Ruggedness:** Riley TRI: sqrt(mean squared center-to-neighbor elevation differences), 60 m window

**Step 2 — Distribution Comparison:** For each feature, compare target and candidate distributions:
- **Wasserstein distance:** Computed via `scipy.stats.wasserstein_distance` on subsampled (max 100,000 values via linspace indexing) distributions
- **KS statistic:** Computed via `scipy.stats.ks_2samp(method="auto")`
- **Pooled IQR:** `max(IQR_target, IQR_candidate)` where IQR = Q75 − Q25
- **Normalized distance:** `Wasserstein / max(pooled_IQR, ε)` where ε = machine epsilon

**Step 3 — Composite Index:**
```
combined_distance = Σ(w_i × d_i) / Σ(w_i)
TMSI = 100 × exp(−combined_distance)
```
Where `w_i` are feature weights (default: equal weights = 1.0 each) and `d_i` are normalized distances.

### 3.2 Uncertainty Quantification

**Spatial Block Bootstrap:**
- Block size: 320 m (16 cells at 20 m resolution)
- Repetitions: 1,000 (increased from 64 in Phase 20.6)
- Random seed: 42 (default)
- Sample cap: 4,096 values per bootstrap repetition
- Confidence interval: Percentile method (2.5th–97.5th percentiles)
- Sampling: up to 32 blocks per repetition, concatenated and subsampled to 4,096 values

**Seed Sensitivity:**
- 5 seeds tested: [42, 123, 456, 789, 1011]
- Reports per-seed TMSI means and confidence intervals plus aggregate statistics

### 3.3 Feature Set

| Feature | Definition | Units | Window |
|---------|-----------|-------|--------|
| Slope | atan of metre-per-pixel gradient magnitude | degrees | Pixel spacing (native resolution) |
| Local relief | Maximum − minimum elevation in complete square window | m | 60 m physical window (3×3 cells at 20 m) |
| Terrain ruggedness | Riley TRI: sqrt(mean squared center-to-neighbor elevation differences) | m | 60 m physical window (3×3 cells at 20 m) |

### 3.4 Weights

Default: Equal weights (1.0 each) for all three features.

### 3.5 Comparison Results (Verified)

| Comparison | TMSI | 95% CI (1,000 reps) | Classification |
|------------|------|---------------------|----------------|
| Moon–Mars | 49.92 | [42.69, 56.92] | READY |
| Earth–Moon | 61.95 | [51.99, 72.56] | CONDITIONALLY READY |
| Earth–Mars | 73.14 | [64.99, 78.55] | CONDITIONALLY READY |

## 4. Datasets

### 4.1 Moon LOLA DEM

| Property | Value |
|----------|-------|
| File | `data/processed/moon_lola_80s_20m_elevation_m.tif` |
| Source | NASA LOLA (Lunar Orbiter Laser Altimeter) |
| CRS | Moon (2015) Sphere / Ocentric / South Polar (IAU:30135) |
| Resolution | 20.0 m × 20.0 m (native post spacing) |
| Dimensions | 2048 × 2048 pixels |
| Vertical Datum | LOLA project datum |
| Elevation Units | Meters |
| Nodata | NaN |
| Valid Pixels | 4,194,304 (100%) |
| Elevation Range | −2,872.11 m to 1,959.42 m |
| Mean Elevation | −113.34 m |
| Status | VALIDATED |

### 4.2 Mars Jezero CTX DTM

| Property | Value |
|----------|-------|
| File | `data/processed/mars_jezero_ctx_elevation_m.tif` |
| Source | USGS / MRO CTX (Context Camera) |
| CRS | ESRI:103885 (equirectangular with MOLA control) |
| Resolution | 20.0 m × 20.0 m (native post spacing) |
| Dimensions | 1596 × 1512 pixels |
| Vertical Datum | Delta geoid (MOLA control) |
| Elevation Units | Meters |
| Nodata | NaN |
| Valid Pixels | 2,413,152 (100%) |
| Elevation Range | −2,710.70 m to −1,515.54 m |
| Mean Elevation | −2,356.87 m |
| Status | VALIDATED |

### 4.3 Earth USGS 3DEP n36w117

| Property | Value |
|----------|-------|
| Raw File | `data/raw/USGS_1_n36w117.tif` |
| Processed File | `data/processed/USGS_1_n36w117_20m_utm11n.tif` |
| Source | USGS 3DEP (3D Elevation Program) |
| Source URL | https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/n36w117/ |
| Source CRS | EPSG:4269 (NAD83 geographic) |
| Processed CRS | EPSG:26911 (UTM Zone 11N) |
| Native Resolution | ~29.3 m (1 arc-second) |
| Processed Resolution | 20.0 m (bilinear interpolation) |
| Vertical Datum | NAVD88 |
| Elevation Units | Meters |
| Nodata | −999999 |
| Raw Valid Pixels | 13,046,544 (100%) |
| Processed Valid Pixels | 25,315,828 (98.94%) |
| Raw Elevation Range | −73.02 m to 1,869.05 m |
| Processed Elevation Range | −72.87 m to 1,868.83 m |
| Mean Elevation | 671.59 m |
| Coverage | 34.9983°N–36.0017°N, 117.0017°W–115.9983°W |
| Region | Southern Arizona / Death Valley vicinity |
| Status | STRUCTURALLY VALIDATED |

### 4.4 Earth USGS 3DEP n37w117

| Property | Value |
|----------|-------|
| Raw File | `data/raw/USGS_1_n37w117.tif` |
| Processed File | `data/processed/USGS_1_n37w117_20m_utm11n.tif` |
| Source | USGS 3DEP (3D Elevation Program) |
| Source URL | https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/n37w117/ |
| Source CRS | EPSG:4269 (NAD83 geographic) |
| Processed CRS | EPSG:26911 (UTM Zone 11N) |
| Native Resolution | ~29.3 m (1 arc-second) |
| Processed Resolution | 20.0 m (bilinear interpolation) |
| Vertical Datum | NAVD88 |
| Elevation Units | Meters |
| Nodata | −999999 |
| Raw Valid Pixels | 13,046,544 (100%) |
| Processed Valid Pixels | 25,002,423 (98.95%) |
| Raw Elevation Range | −85.08 m to 2,176.92 m |
| Processed Elevation Range | −85.08 m to 2,176.39 m |
| Mean Elevation | 895.40 m |
| Coverage | 35.9983°N–37.0017°N, 117.0017°W–115.9983°W |
| Region | Central Valley, California |
| Status | STRUCTURALLY VALIDATED |

### 4.5 Blocked / Unavailable Datasets

- **NASADEM HGT V001:** Blocked by NASA Earthdata authentication (HTTP 401)
- **Copernicus GLO-30:** Registration required, not acquired
- **SRTM GL3:** DNS resolution issues, not acquired

## 5. Phase 17 Scientific Limitations (All Preserved)

1. TMSI cannot establish planetary body identity
2. Extent-sensitivity (23.71 @ 5.12 km → 49.92 @ 10.24 km)
3. Earth data blocked by NASA Earthdata authentication (HTTP 401)
4. Independent DEM benchmark blocked
5. Spatial autocorrelation not fully captured (Moran's I = 0.979)
6. "HIGH confidence" is qualitative, not statistical
7. Results design-dependent (10.24 km extent)
8. Riley TRI is roughness index, not hazard measure
9. Slope sensitive to DEM noise at steep slopes
10. Edge cells excluded from local relief statistics

## 6. Phase 20 Limitations (Documented and Preserved)

| # | Limitation |
|---|-----------|
| P20-1 | Earth DEM effective resolution ~29.3 m (resampled to 20 m processing grid) |
| P20-2 | Vertical datum differences (NAVD88 vs. LOLA/MOLA/delta geoid) not quantitatively resolved |
| P20-3 | Earth coverage limited to two USGS tiles (Death Valley / southern Arizona region) |
| P20-4 | Bootstrap repetitions = 1,000 (increased from 64 in Phase 20.6) |
| P20-5 | Equal feature weights (arbitrary; no sensitivity analysis) |
| P20-6 | max(IQR) scaling rather than true pooled IQR |

## 7. Phase 21 Limitations (Newly Identified)

| # | Limitation |
|---|-----------|
| P21-1 | Feature correlation not adjusted (slope, relief, ruggedness derived from same DEM) |
| P21-2 | Systematic (not random) subsampling to 100K values |
| P21-3 | Exponential transform TMSI = 100 × exp(−D) is arbitrary |
| P21-4 | Percentile bootstrap may not be optimal for bounded TMSI |
| P21-5 | Block size 320 m may not fully decorrelate (Moran's I ≈ 0.979) |
| P21-6 | No multiple-comparison correction |

## 8. Phase 22 Baseline Complete

The repository state has been documented. All Phase 17–21 deliverables are preserved intact. No results or source data have been modified. Phase 22 is now ready to proceed with the prior art investigation and original contribution assessment.