# Terra Twin — Phase 21: Baseline Report

## 1. Executive Summary

Phase 21 (Independent Scientific Review & Research Publication Readiness) establishes a comprehensive audit baseline for the completed Moon–Mars–Earth Terrain Morphological Similarity Index (TMSI) research. This document records the current repository state, scientific architecture, datasets, preprocessing operations, assumptions, and outputs as of the start of Phase 21.

**No previous research results have been overwritten or modified.** All Phase 17–20.6 deliverables are preserved intact.

## 2. Repository State

### 2.1 Git State

- **Repository root:** `/Users/markadam/Desktop/NASA SPACE APP CHALLENGE/nasaspaceapp`
- **Current branch:** `main`
- **Last commit:** `86e958b` (Initial commit from Create Next App)
- **Working tree status:** All project files are untracked (not committed to git)
- **Untracked top-level entries:** `backend/`, `data/`, `docs/`, `frontend/`, `research/`, `science/`, `submission/`, `test_datasets.py`, `tsconfig.json`, `package.json`, `package-lock.json`, `eslint.config.mjs`, `next.config.ts`

### 2.2 Repository Structure

| Directory | Contents |
|-----------|----------|
| `backend/` | FastAPI application (health, similarity APIs), Pydantic schemas, export service |
| `data/raw/` | Raw source DEMs: USGS 3DEP tiles (n36w117, n37w117), Mars Jezero CTX DTM, Moon LOLA |
| `data/processed/` | Processed DEMs: USGS 3DEP at 20 m UTM, Moon LOLA, Mars Jezero, Earth processing metadata |
| `data/metadata/` | Comparison result JSONs for Phases 20–20.6, preprocessing metadata, Earth data diagnostics |
| `docs/` | 70+ documentation files from Phases 3–20.6 |
| `frontend/` | Next.js frontend with ResearchWorkbench component |
| `research/` | Research paper draft |
| `science/` | Python scientific computing: similarity engine, feature extraction, data ingestion, preprocessing, validation |
| `submission/` | NASA Space Apps submission files |

### 2.3 Key Science Modules

| Module | Purpose |
|--------|---------|
| `science/similarity/scoring/similarity.py` | TMSI computation: `compare_terrain()` |
| `science/similarity/comparison/distance.py` | Distribution distances: Wasserstein, KS, pooled IQR, normalized distance |
| `science/similarity/comparison/bootstrap.py` | Spatial block bootstrap CI, seed sensitivity analysis |
| `science/similarity/features/feature_extraction.py` | Terrain feature extraction: slope, local relief, terrain ruggedness |
| `science/similarity/features/slope.py` | Slope computation |
| `science/similarity/features/local_relief.py` | Local relief computation |
| `science/similarity/features/terrain_ruggedness.py` | Riley TRI computation |
| `science/similarity/scoring/weights.py` | Weight validation |
| `science/similarity/scoring/sensitivity.py` | Weight sensitivity analysis |
| `science/similarity/comparison/uncertainty.py` | Resolution assessment, confidence classification |
| `science/similarity/comparison/distribution.py` | Feature layer comparison |
| `science/similarity/comparison/extent.py` | Extent sensitivity diagnostics |
| `science/similarity/comparison/overlap.py` | Overlap bias diagnostics |
| `science/similarity/comparison/spatial.py` | Spatial diagnostics |
| `science/data_ingestion/acquire_earth_dem.py` | Earth DEM acquisition pipeline |
| `science/earth_normalization.py` | Earth DEM resolution normalization |
| `science/earth_features.py` | Earth feature extraction integration |
| `science/datasets/registry.py` | Candidate registry with status transitions |
| `science/datasets/registry.json` | Candidate catalog (13 candidates) |
| `science/preprocessing/` | Coordinate systems, resolution, validation, pipeline modules |

## 3. Authoritative TMSI Implementation

### 3.1 TMSI Formula

The Terrain Morphology Similarity Index (TMSI) is computed as:

```
D = combined_distance = Σ(w_i × d_i) / Σ(w_i)
TMSI = 100 × exp(−D)
```

Where:
- `w_i` = weight for feature i (default: equal weights = 1.0 each)
- `d_i` = normalized_distance for feature i = Wasserstein distance / pooled_IQR
- `pooled_IQR` = max(IQR_target, IQR_candidate) — uses the larger of the two IQRs (conservative scaling)

### 3.2 Feature Extraction

Three terrain morphology features are extracted from each raster:

| Feature | Definition | Units | Window |
|---------|-----------|-------|--------|
| Slope | atan of metre-per-pixel gradient magnitude | degrees | Pixel spacing |
| Local relief | Maximum − minimum elevation in complete window | m | 60 m (3×3 cells at 20 m) |
| Terrain ruggedness | Riley TRI: sqrt(mean squared center-to-neighbor differences) | m | 60 m (3×3 cells at 20 m) |

### 3.3 Distribution Comparison

For each feature, distributions are compared using:
- **Wasserstein distance** (Earth Mover's Distance) via `scipy.stats.wasserstein_distance`
- **KS statistic** via `scipy.stats.ks_2samp`
- **Pooled IQR** = max(IQR_target, IQR_candidate)
- **Normalized distance** = Wasserstein / pooled_IQR
- Distributions are subsampled to 100,000 values via linspace indexing if larger

### 3.4 Uncertainty Quantification

- **Method:** Non-overlapping spatial block bootstrap with replacement
- **Block size:** 320 m (16 cells at 20 m resolution)
- **Repetitions:** 1,000 (increased from 64 in Phase 20.6)
- **Confidence interval:** Percentile method (2.5th–97.5th percentiles)
- **Seed:** 42 (default, configurable)
- **Sample cap:** 4,096 values per bootstrap repetition

## 4. Datasets

### 4.1 Validated Datasets

| Dataset | File | Body | Resolution | CRS | Valid Pixels | Elevation Range |
|---------|------|------|------------|-----|-------------|-----------------|
| Moon LOLA DEM | `data/processed/moon_lola_80s_20m_elevation_m.tif` | Moon | 20 m | Moon (2015) Polar Stereographic | 4,194,304 | −2,872 to 1,959 m |
| Mars Jezero CTX DTM | `data/processed/mars_jezero_ctx_elevation_m.tif` | Mars | 20 m | Equirectangular (MOLA) | 2,413,152 | −2,711 to −1,516 m |
| Earth USGS 3DEP n36w117 | `data/processed/USGS_1_n36w117_20m_utm11n.tif` | Earth | 20 m (resampled from ~29.3 m) | EPSG:26911 (UTM 11N) | 25,315,828 | −73 to 1,869 m |
| Earth USGS 3DEP n37w117 | `data/processed/USGS_1_n37w117_20m_utm11n.tif` | Earth | 20 m (resampled from ~29.3 m) | EPSG:26911 (UTM 11N) | 25,002,423 | −85 to 2,177 m |

### 4.2 Blocked / Unavailable Datasets

- **NASADEM HGT V001:** Blocked by NASA Earthdata authentication (HTTP 401)
- **Copernicus GLO-30:** Registration required, not acquired
- **SRTM GL3:** DNS resolution issues, not acquired

### 4.3 Original Data Preservation

All original raw DEM files are preserved unmodified in `data/raw/`. Processed derivatives are stored separately in `data/processed/`. No original file has been modified.

## 5. Comparison Results (Phase 20–20.6)

| Comparison | TMSI | 95% CI (1,000 reps) | Classification |
|------------|------|---------------------|----------------|
| Moon–Mars | 49.92 | [42.69, 56.92] | READY |
| Earth–Moon | 61.95 | [51.99, 72.56] | CONDITIONALLY READY |
| Earth–Mars | 73.14 | [64.99, 78.55] | CONDITIONALLY READY |

## 6. Phase 17 Scientific Limitations (All Preserved)

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

## 7. Phase 19 Eligibility Rules (Preserved)

- Only `READY_FOR_COMPARISON` candidates eligible for quantitative scoring
- `CANDIDATE` and `DATA_AVAILABLE` candidates ineligible
- Status transitions: `CANDIDATE → SOURCE_VERIFIED → DATA_AVAILABLE → READY_FOR_COMPARISON`
- Unvalidated candidates must not receive quantitative Earth–Moon/Mars similarity scoring

## 8. Phase 21 Baseline Complete

The repository state has been documented. All Phase 17–20.6 deliverables are preserved. No results have been overwritten or modified. Phase 21 is now ready to proceed with the independent scientific review workstreams.