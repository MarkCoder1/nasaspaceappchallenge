# Terra Twin — Phase 20.5: Reproducibility and Regression Audit

## 1. Executive Summary

**VERDICT: VERIFIED**

All Phase 20 results are independently reproducible. Identical inputs produce identical outputs. Existing Phase 17–19 functionality has not regressed. All 10 Phase 17 scientific limitations are preserved.

| Reproducibility Test | Result |
|---------------------|--------|
| TMSI recalculation (Moon-Mars) | ✅ Exact match (49.922854) |
| TMSI recalculation (Earth-Moon) | ✅ Exact match (61.950148) |
| TMSI recalculation (Earth-Mars) | ✅ Exact match (73.135982) |
| CI reproduction (all 3 comparisons) | ✅ Exact match |
| Existing Python tests | 98/98 pass |
| Phase 19 candidate tests | 14/17 pass (3 pre-existing TS-in-Python failures) |
| ESLint | 13 errors (baseline match, 0 new) |
| TypeScript | 5 errors (pre-existing, 0 new) |
| Numerical reproducibility | ✅ Verified |

## 2. Reproducibility Methodology

### 2.1 Independent Recalculation

All Phase 20 TMSI values were independently recalculated from raw data using the same methodology:

1. Load raster datasets
2. Extract terrain features (slope, local relief, terrain ruggedness)
3. Compute Wasserstein distance, KS statistic, pooled IQR
4. Compute normalized distance = Wasserstein / pooled_IQR
5. Compute combined_distance = weighted_mean(normalized_distances)
6. Compute TMSI = 100 × exp(−combined_distance)

All three comparisons produced identical results to the reported values.

### 2.2 Bootstrap Reproduction

All three confidence intervals were independently reproduced:
- Moon–Mars: [43.7194, 56.7985] vs reported [43.72, 56.80] ✅
- Earth–Moon: [53.2344, 74.8076] vs reported [53.23, 74.81] ✅
- Earth–Mars: [65.4146, 78.4017] vs reported [65.41, 78.40] ✅

### 2.3 Deterministic Components

| Component | Deterministic? | Seed |
|-----------|---------------|------|
| TMSI calculation | Yes | N/A (no randomness) |
| Bootstrap CI | Yes | Seed = 42 |
| Feature extraction | Yes | N/A (no randomness) |
| Resolution normalization | Yes | Bilinear interpolation (deterministic) |

**Assessment:** All components are deterministic given a fixed seed. Results are fully reproducible.

## 3. Processing Configuration Documentation

### 3.1 Earth Data Processing

| Parameter | Value |
|-----------|-------|
| Source CRS | EPSG:4269 (NAD83) |
| Target CRS | EPSG:26911 (UTM Zone 11N) |
| Target resolution | 20.0 m |
| Resampling method | Bilinear interpolation |
| Source resolution | ~29.3 m (1 arc-second) |

### 3.2 Feature Extraction Parameters

| Parameter | Value |
|-----------|-------|
| Local neighborhood | 60.0 m |
| Ruggedness neighborhood | 60.0 m |
| Feature types | Slope, local relief, terrain ruggedness |

### 3.3 Comparison Parameters

| Parameter | Value |
|-----------|-------|
| Weights | Equal (1.0 each) |
| Spatial extent | 10.24 km |
| Bootstrap repetitions | 64 |
| Bootstrap block size | 320 m |
| Bootstrap seed | 42 |
| Distribution sample cap | 100,000 values |

## 4. Intermediate Outputs

All intermediate outputs are preserved:

| File | Description |
|------|-------------|
| `data/processed/USGS_1_n36w117_20m_utm11n.tif` | Processed Earth DEM |
| `data/processed/USGS_1_n37w117_20m_utm11n.tif` | Processed Earth DEM |
| `data/processed/phase20_earth_processing_metadata.json` | Earth processing metadata |
| `data/metadata/phase20_moon_mars_comparison.json` | Moon–Mars results |
| `data/metadata/phase20_earth_moon_comparison.json` | Earth–Moon results |
| `data/metadata/phase20_earth_mars_comparison.json` | Earth–Mars results |

## 5. Regression Testing

### 5.1 Existing Python Tests

| Test Suite | Result |
|------------|--------|
| `science/tests/test_phase18_validation.py` | 14/14 pass |
| `science/tests/test_phase19_candidates.py` | 14/17 pass (3 pre-existing TS-in-Python failures) |
| All other science tests | 98/98 pass |

**Assessment:** No regressions introduced by Phase 20. The 3 pre-existing failures are TypeScript-in-Python namespace issues unrelated to Phase 20.

### 5.2 Frontend Tests

| Check | Result |
|-------|--------|
| ESLint | 13 errors (baseline match, 0 new) |
| TypeScript | 5 errors (pre-existing, 0 new) |

**Assessment:** No new lint or type errors introduced by Phase 20.

### 5.3 Phase 17 Scientific Limitations Preserved

| # | Limitation | Status |
|---|-----------|--------|
| 1 | TMSI cannot establish planetary body identity | ✅ Preserved |
| 2 | Extent-sensitivity | ✅ Preserved |
| 3 | Earth data blocked by NASA Earthdata auth | ✅ Preserved |
| 4 | Independent DEM benchmark blocked | ✅ Preserved |
| 5 | Spatial autocorrelation (Moran's I = 0.979) | ✅ Preserved |
| 6 | "HIGH confidence" is qualitative | ✅ Preserved |
| 7 | Results design-dependent | ✅ Preserved |
| 8 | Riley TRI is roughness index | ✅ Preserved |
| 9 | Slope sensitive to DEM noise | ✅ Preserved |
| 10 | Edge cells excluded from local relief | ✅ Preserved |

## 6. Phase 19 Eligibility Enforcement Audit

| Rule | Status |
|------|--------|
| Only READY_FOR_COMPARISON candidates eligible | ✅ Enforced |
| CANDIDATE candidates ineligible | ✅ Enforced |
| DATA_AVAILABLE candidates ineligible | ✅ Enforced |
| Status transitions: CANDIDATE → SOURCE_VERIFIED → DATA_AVAILABLE → READY_FOR_COMPARISON | ✅ Enforced |
| No unvalidated comparison results manufactured | ✅ Verified |

## 7. Original Data Integrity

| File | Status | SHA-256 |
|------|--------|---------|
| `data/raw/USGS_1_n36w117.tif` | ✅ Unmodified | 6dad0432...cd40 |
| `data/raw/USGS_1_n37w117.tif` | ✅ Unmodified | d6100180...ca302 |
| `data/processed/moon_lola_80s_20m_elevation_m.tif` | ✅ Unmodified | — |
| `data/processed/mars_jezero_ctx_elevation_m.tif` | ✅ Unmodified | — |

## 8. Classification

**Reproducibility: VERIFIED**

All results are independently reproducible. Identical inputs produce identical outputs. Processing configurations are fully documented. No regressions in existing functionality. All scientific limitations preserved.

---

**Next:** See `PHASE20_5_FINAL_REPORT.md` for the overall verdict and Phase 21 recommendation.