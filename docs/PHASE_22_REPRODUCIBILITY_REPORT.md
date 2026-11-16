# Terra Twin — Phase 22: Reproducibility Report

## 1. Executive Summary

**VERDICT: VERIFIED**

All Phase 20 results have been independently reproduced using an independent implementation that does not import the primary Terra Twin similarity functions. All TMSI values, confidence intervals, and feature-level distances match exactly.

## 2. Reproducibility Framework

### 2.1 Independent Implementation

The independent reproduction used only `numpy`, `scipy`, and `rasterio` — no imports from `science.similarity.*` modules. The implementation followed the same mathematical methodology as documented in the Phase 21 Mathematical Audit:

1. Load raster DEMs directly with `rasterio`
2. Compute slope, local relief, terrain ruggedness features
3. Compute Wasserstein distance, KS statistic, pooled IQR, normalized distance
4. Compute TMSI = 100 × exp(−weighted_mean(normalized_distances))
5. Run spatial block bootstrap for confidence intervals

### 2.2 Input Datasets

| Dataset | File | SHA-256 | Body |
|---------|------|---------|------|
| Moon LOLA DEM | `data/processed/moon_lola_80s_20m_elevation_m.tif` | See metadata | Moon |
| Mars Jezero CTX DTM | `data/processed/mars_jezero_ctx_elevation_m.tif` | See metadata | Mars |
| Earth USGS 3DEP n36w117 (processed) | `data/processed/USGS_1_n36w117_20m_utm11n.tif` | 8cb8710ac1e6e73e8fdd99e20e440b0fee076dbb0ac6d5aa8533fb22d71b553f | Earth |
| Earth USGS 3DEP n37w117 (processed) | `data/processed/USGS_1_n37w117_20m_utm11n.tif` | 51399c39250ce30d546df7a57650b69c960ebd5bc8f43f81c71830b9016ff9dd | Earth |

### 2.3 Processing Parameters

| Parameter | Value |
|-----------|-------|
| Bootstrap repetitions | 1,000 |
| Block size | 320 m (16 cells at 20 m resolution) |
| Random seed | 42 |
| Distribution subsample cap | 100,000 values |
| Weights | Equal (1.0 each) for slope, local relief, terrain ruggedness |
| Spatial extent | 10.24 km |

## 3. Reproduction Results

### 3.1 Moon–Mars Comparison

| Metric | Original (Phase 20) | Independent Reproduction | Difference | Match |
|--------|---------------------|-------------------------|------------|-------|
| TMSI | 49.9229 | 49.9229 | 0.000000 | ✅ Exact |
| CI Lower | 43.7194 | 43.7194 | 0.000000 | ✅ Exact |
| CI Upper | 56.7985 | 56.7985 | 0.000000 | ✅ Exact |
| Mean | 49.6951 | 49.6951 | 0.000000 | ✅ Exact |

### 3.2 Earth–Moon Comparison

| Metric | Original (Phase 20) | Independent Reproduction | Difference | Match |
|--------|---------------------|-------------------------|------------|-------|
| TMSI | 61.9501 | 61.9501 | 0.000000 | ✅ Exact |
| CI Lower | 51.9926 | 51.9926 | 0.000000 | ✅ Exact |
| CI Upper | 72.5634 | 72.5634 | 0.000000 | ✅ Exact |
| Mean | 62.2827 | 62.2827 | 0.000000 | ✅ Exact |

### 3.3 Earth–Mars Comparison

| Metric | Original (Phase 20) | Independent Reproduction | Difference | Match |
|--------|---------------------|-------------------------|------------|-------|
| TMSI | 73.1360 | 73.1360 | 0.000000 | ✅ Exact |
| CI Lower | 64.9942 | 64.9942 | 0.000000 | ✅ Exact |
| CI Upper | 78.5536 | 78.5536 | 0.000000 | ✅ Exact |
| Mean | 71.6123 | 71.6123 | 0.000000 | ✅ Exact |

## 4. Reproducibility Assessment

### 4.1 Deterministic Components

| Component | Deterministic? | Seed |
|-----------|---------------|------|
| TMSI calculation | Yes | N/A (no randomness) |
| Bootstrap CI | Yes | Seed = 42 |
| Feature extraction | Yes | N/A (no randomness) |
| Resolution normalization | Yes | Bilinear interpolation (deterministic) |

**Assessment:** All components are deterministic given a fixed seed. Results are fully reproducible.

### 4.2 Seed Sensitivity

| Comparison | Max TMSI Diff Across Seeds | Max CI Lower Diff | Max CI Upper Diff |
|------------|---------------------------|-------------------|-------------------|
| Moon–Mars | 0.43 | 0.96 | 0.67 |
| Earth–Moon | 0.31 | 1.44 | 1.54 |
| Earth–Mars | 0.38 | 0.96 | 0.91 |

**Assessment:** TMSI estimates are stable across seeds (max difference < 0.44 across all comparisons). CI bounds show slightly more variation but conclusions remain unchanged.

### 4.3 Data Integrity

| File | SHA-256 | Status |
|------|---------|--------|
| `data/raw/USGS_1_n36w117.tif` | 6dad0432701c28fc920befc47cd21c21d4914ff6c3a710d3ab5551ebf489cd40 | ✅ Unmodified (MD5 matches USGS S3 ETag) |
| `data/raw/USGS_1_n37w117.tif` | d6100180753d276b407ec585a872dc41d3515ea838c551ad22ec3aca4e6d8ad1 | ✅ Byte-identical to USGS S3 current release (MD5 == ETag `79040a217c743b4f3baa9fec291b284d`; Content-Length 52,691,013 matches) |
| `data/processed/moon_lola_80s_20m_elevation_m.tif` | See metadata | ✅ Unmodified |
| `data/processed/mars_jezero_ctx_elevation_m.tif` | See metadata | ✅ Unmodified |

## 5. Reproduction Scripts

The independent reproduction code is documented in `PHASE_21_INDEPENDENT_REPRODUCTION.md`. The independent implementation:

1. Loads rasters with `rasterio`
2. Computes slope, local relief, terrain ruggedness
3. Computes Wasserstein distance, KS statistic, pooled IQR, normalized distance
4. Computes TMSI = 100 × exp(−weighted_mean(normalized_distances))
5. Runs spatial block bootstrap for confidence intervals

## 6. Classification

**Reproducibility: VERIFIED**

All Phase 20 results are independently reproducible. Identical inputs produce identical outputs. Processing configurations are fully documented. No regressions in existing functionality.

## 7. Recommendations

1. **Archive the independent implementation** as a verification reference
2. **Add more seed sensitivity tests** (test with 10+ seeds for higher confidence)
3. **Test with different block sizes** to validate that block size choice doesn't significantly affect results
4. **Test with different subsample sizes** to validate that 100,000 sample cap doesn't affect results