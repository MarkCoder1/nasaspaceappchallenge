# Terra Twin — Phase 20: Initial Architecture and Dataset Audit

## 1. Executive Summary

Phase 20 builds upon the Phase 19 Earth Candidate Registry and Interactive Discovery Map to implement quantitative planetary terrain comparison. This audit establishes the starting point by documenting all available datasets, existing infrastructure, compatibility constraints, and implementation requirements.

## 2. Available Datasets

### 2.1 Lunar Datasets

#### Moon LOLA DEM (Primary)
- **File**: `data/processed/moon_lola_80s_20m_elevation_m.tif`
- **Size**: 14.2 MB
- **CRS**: Moon (2015) Sphere / Ocentric / South Polar (IAU:30135)
- **Dimensions**: 2048 × 2048 pixels
- **Resolution**: 20.0 m × 20.0 m (native post spacing)
- **Extent**: 40.96 km × 40.96 km (centered on south polar region)
- **Data type**: float32
- **Bands**: 1
- **Nodata**: NaN
- **Valid pixels**: 4,194,304 (100%)
- **Elevation range**: -2,872.11 m to 1,959.42 m
- **Mean elevation**: -113.34 m
- **Status**: VALIDATED

#### Moon LOLA Central Window (Secondary)
- **File**: `data/processed/moon_lola_central_20km_window.tif`
- **Size**: 3.6 MB
- **CRS**: Same as above (Moon polar stereographic)
- **Dimensions**: 1024 × 1024 pixels
- **Resolution**: 20.0 m × 20.0 m
- **Extent**: 20.48 km × 20.48 km
- **Valid pixels**: 1,048,576 (100%)
- **Elevation range**: -2,872.11 m to 1,738.43 m
- **Mean elevation**: -139.22 m
- **Status**: VALIDATED

### 2.2 Martian Datasets

#### Mars Jezero CTX DTM (Primary)
- **File**: `data/processed/mars_jezero_ctx_elevation_m.tif`
- **Size**: 7.5 MB
- **CRS**: ESRI:103885 (equirectangular with MOLA control)
- **Dimensions**: 1596 × 1512 pixels
- **Resolution**: 20.0 m × 20.0 m (native post spacing)
- **Extent**: ~31.92 km × ~30.24 km
- **Data type**: float32
- **Bands**: 1
- **Nodata**: NaN
- **Valid pixels**: 2,413,152 (100%)
- **Elevation range**: -2,710.70 m to -1,515.54 m
- **Mean elevation**: -2,356.87 m
- **Status**: VALIDATED

### 2.3 Earth Datasets (USGS 3DEP)

#### USGS_1_n36w117 (Southern Arizona)
- **File**: `data/raw/USGS_1_n36w117.tif`
- **Size**: 51.8 MB
- **CRS**: EPSG:4269 (NAD83 geographic)
- **Dimensions**: 3612 × 3612 pixels
- **Resolution**: ~0.0002778° × ~0.0002778° (~29.3 m/pixel, 1 arc-second)
- **Extent**: 34.9983°N–36.0017°N, 117.0017°W–115.9983°W
- **Data type**: float32
- **Bands**: 1
- **Nodata**: -999999
- **Valid pixels**: 13,046,544 (100%)
- **Elevation range**: -73.02 m to 1,869.05 m
- **Mean elevation**: 671.51 m
- **Vertical datum**: North American Vertical Datum of 1988 (NAVD88)
- **Source**: USGS 3DEP 1-arc-second DEM
- **Source URL**: https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/n36w117/
- **Status**: STRUCTURALLY VALIDATED, NEEDS PROCESSING

#### USGS_1_n37w117 (Central Valley, California)
- **File**: `data/raw/USGS_1_n37w117.tif`
- **Size**: 50.3 MB
- **CRS**: EPSG:4269 (NAD83 geographic)
- **Dimensions**: 3612 × 3612 pixels
- **Resolution**: ~0.0002778° × ~0.0002778° (~29.3 m/pixel, 1 arc-second)
- **Extent**: 35.9983°N–37.0017°N, 117.0017°W–115.9983°W
- **Data type**: float32
- **Bands**: 1
- **Nodata**: -999999
- **Valid pixels**: 13,046,544 (100%)
- **Elevation range**: -85.08 m to 2,176.92 m
- **Mean elevation**: 896.08 m
- **Vertical datum**: NAVD88
- **Source**: USGS 3DEP 1-arc-second DEM
- **Source URL**: https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/n37w117/
- **Status**: STRUCTURALLY VALIDATED, NEEDS PROCESSING

### 2.4 Blocked / Unavailable Datasets

#### NASADEM HGT V001
- **Status**: BLOCKED_BY_EARTHDATA_AUTHENTICATION (HTTP 401)
- **Reason**: NASA Earthdata Login credentials required
- **Endpoints blocked**: CMR granule search, download endpoints

## 3. Existing Infrastructure

### 3.1 Similarity Scoring Module (`science/similarity/scoring/similarity.py`)

**Key functions:**
- `compare_terrain(target, candidate, weights, include_uncertainty, window_a, window_b, spatial_extent_km)` — Main comparison function
- `assess_resolution(target, candidate)` — Resolution compatibility check
- `classify_confidence(target_valid_percent, candidate_valid_percent, resolution, feature_count)` — Confidence classification
- `validate_weights(weights)` — Weight validation and defaults

**Return structure:**
- `similarity_index` (0-100 scale)
- `combined_distance`
- `confidence` level
- `feature_comparisons` per feature (Wasserstein, KS, normalized distance)
- `strongest_matches`, `largest_differences`
- `limitations` (including resolution common analysis scale)
- `data_sources` (provenance)
- Optional: `statistical_uncertainty` (bootstrap), `block_size_sensitivity`
- Optional: `comparison_diagnostics` (overlap, extent sensitivity)

**Critical limitations documented in compare_terrain:**
- TMSI is terrain-morphology index, not probability/habitability/safety certification
- Features interpreted at common physical scale; no raster upsampling performed
- Earth and planetary environmental conditions differ even when morphology distributions are similar

### 3.2 Feature Extraction Module (`science/similarity/features/feature_extraction.py`)

**Key functions:**
- `extract_terrain_features(raster_path, ...)` — Full feature extraction from raster
- `earth_terrain_feature_set_from_raster(...)` — Earth-specific feature set creation
- `compare_available_features(target, candidate)` — Feature-level comparison
- `slope_degrees(...)` — Slope calculation via gradient
- `local_relief_m(...)` — Local relief (max-min in window)
- `terrain_ruggedness_index(...)` — Riley TRI

**Features computed:**
- Slope (degrees)
- Local relief (m)
- Terrain ruggedness (m, Riley TRI)

### 3.3 Statistical Modules (`science/similarity/comparison/`)

**Bootstrap**: `bootstrap_tmsi(target, candidate, weights)` — Block bootstrap uncertainty
**Block size**: `block_size_sensitivity(target, candidate, weights)` — Block size sensitivity
**Distance**: `compare_distributions(...)`, `ks_2samp(...)`, `wasserstein_distance(...)`
**Distribution**: KS test, Wasserstein distance, distribution overlap analysis
**Extent**: `diagnose_extent_sensitivity(...)` — Extent sensitivity diagnostics
**Overlap**: `diagnose_overlap(...)` — Window overlap diagnostics

### 3.4 Backend API (`backend/app/`)

**Endpoints:**
- `GET /api/health` — Health check
- `GET /api/similarity/status` — Similarity engine status
- `GET /api/similarity/features` — Feature definitions
- `GET /api/similarity/methodology` — Methodology documentation
- `GET /api/similarity/results` — Stored experiment results
- `GET /api/similarity/sampling-framework` — Phase 11 sampling framework
- `GET /api/similarity/raster/{dataset_id}` — Raster preview SVG
- `GET /api/similarity/export/{json,csv,pdf}` — Export functionality
- `POST /api/similarity/compare` — Dataset comparison

**Comparison capabilities reported:**
- `moon_mars`: enabled (validated Moon and Mars inputs available)
- `earth_mars`: disabled (no validated Earth elevation raster)
- `earth_moon`: disabled (no validated Earth or lunar elevation raster)

### 3.5 Frontend (`frontend/components/ResearchWorkbench.tsx`)

**Existing components:**
- EXPLORE view — Elevation visualization
- COMPARE view — Feature comparison
- RELIABILITY view — Bootstrap confidence and sensitivity
- DATA & METHODS view — Dataset inventory and provenance
- MAP view — Earth candidate discovery map
- CandidateDetailPanel — Candidate detail with integrity statements

**Candidate interface (21 fields):**
- id, name, country, environment_classification, planetary_relevance, status
- latitude, longitude, bounding_box
- scientific_description, geological_context
- selection_rationale, supporting_references
- source_dataset, source_url
- data_acquisition_status, dem_availability, spatial_resolution
- coordinate_reference_system, elevation_coverage, terrain_feature_availability
- scientific_validation_status, known_limitations, last_updated

## 4. Compatibility Analysis

### 4.1 Resolution Compatibility

| Dataset | Native Resolution | Target Resolution | Normalization Required |
|---------|------------------|-------------------|----------------------|
| Moon LOLA | 20 m | 20 m | No |
| Mars Jezero | 20 m | 20 m | No |
| Earth USGS 3DEP | ~29.3 m (1 arc-sec) | 20 m | Yes (downsampling) |

**Critical requirement:** USGS data at ~29.3 m must NOT be described as 20 m after resampling. Downsampling from 29.3 m to 20 m is required for comparison, but the effective resolution remains ~29.3 m. Resolution sensitivity testing must be documented.

### 4.2 CRS Compatibility

| Dataset | CRS | Projection Type | Compatibility |
|---------|-----|-----------------|---------------|
| Moon LOLA | Moon (2015) Polar Stereographic | Projected (polar) | Native metres |
| Mars Jezero | ESRI:103885 | Equirectangular | Native metres |
| Earth USGS 3DEP | EPSG:4269 (NAD83) | Geographic (degrees) | Requires reprojection |

**Compatibility notes:**
- Moon and Mars datasets are already in projected CRS with metre units
- Earth USGS data is in geographic CRS (degrees) — requires reprojection to projected CRS before slope/relief calculations
- Horizontal datum differences: NAD83 (Earth) vs. body-specific datums (Moon/Mars)
- Vertical datum differences: NAVD88 (Earth) vs. LOLA/MOLA/MOLA-delta-geoid

### 4.3 Vertical Datum Compatibility

| Dataset | Vertical Datum | Notes |
|---------|---------------|-------|
| Moon LOLA | LOLA project datum | Lunar reference surface |
| Mars Jezero | Delta geoid (MOLA control) | Martian reference surface |
| Earth USGS 3DEP | NAVD88 | North American Vertical Datum 1988 |

**Requirement:** Vertical datum differences must be explicitly documented and treated separately, not implicitly compared.

## 5. Implementation Requirements

### 5.1 Workstream A — Moon–Mars Comparison (READY)

Both datasets are validated and at 20 m native resolution. Infrastructure exists for direct comparison.

**Tasks:**
1. Extract terrain features from both datasets
2. Run compare_terrain with uncertainty quantification
3. Document resolution, CRS, and vertical datum compatibility
4. Produce reproducible results

### 5.2 Workstream B — Earth–Moon Comparison (CONDITIONALLY READY)

Earth USGS 3DEP data acquired but requires:
1. Reprojection from EPSG:4269 to projected CRS
2. Resolution normalization (29.3 m → common analysis scale)
3. Vertical datum documentation (NAVD88 vs. LOLA)
4. Feature extraction on processed Earth data
5. Comparison with Moon dataset

### 5.3 Workstream C — Earth–Mars Comparison (CONDITIONALLY READY)

Same requirements as Earth–Moon, with Mars dataset instead of Moon.

### 5.4 Workstream D — Statistical Validation

Requires bootstrap confidence intervals, KS statistics, Wasserstein distances, spatial autocorrelation accounting.

### 5.5 Workstream E — Visualizations

Requires integration into ResearchWorkbench frontend with clear distinction between:
- Observed measurements
- Derived measurements
- Statistical estimates
- Uncertainty
- Unsupported comparisons

### 5.6 Workstream F — Scientific Interpretation

Requires complete scientific interpretation with explicit limitation documentation.

## 6. Scientific Safeguards (Preserved from Phases 17–19)

All 10 Phase 17 limitations preserved:
1. TMSI cannot establish planetary body identity
2. Extent-sensitivity (23.71 @ 5.12 km → 49.92 @ 10.24 km)
3. Earth data blocked by NASA Earthdata authentication
4. Independent DEM benchmark blocked
5. Spatial autocorrelation not fully captured (Moran's I = 0.979)
6. "HIGH confidence" is qualitative
7. Results design-dependent (10.24 km extent)
8. Riley TRI is roughness index, not hazard measure
9. Slope sensitive to DEM noise at steep slopes
10. Edge cells excluded from local relief statistics

Phase 19 eligibility rules preserved:
- Only READY_FOR_COMPARISON candidates eligible
- Unvalidated candidates ineligible for quantitative scoring
- Status transitions: CANDIDATE → SOURCE_VERIFIED → DATA_AVAILABLE → READY_FOR_COMPARISON

## 7. Implementation Plan

### 7.1 Execution Order

1. Initial Phase 20 architecture and dataset audit (this document)
2. Workstream A — Moon–Mars comparison
3. Workstream D — Statistical validation
4. Workstream B — Earth–Moon comparison
5. Workstream C — Earth–Mars comparison
6. Workstream E — Visualizations
7. Workstream F — Scientific interpretation
8. Full integration and regression testing

### 7.2 Required Documentation

- `docs/PHASE20_INITIAL_AUDIT.md` — This document
- `docs/PHASE20_MOON_MARS_ANALYSIS.md`
- `docs/PHASE20_EARTH_MOON_ANALYSIS.md`
- `docs/PHASE20_EARTH_MARS_ANALYSIS.md`
- `docs/PHASE20_STATISTICAL_VALIDATION.md`
- `docs/PHASE20_TERRAIN_VISUALIZATIONS.md`
- `docs/PHASE20_SCIENTIFIC_INTERPRETATION.md`
- `docs/PHASE20_FINAL_REPORT.md`

## 8. Readiness Classification

| Comparison | Status | Reason |
|------------|--------|--------|
| Moon–Mars | ✅ READY | Both datasets validated, 20 m native, infrastructure ready |
| Earth–Moon | ⚠️ CONDITIONALLY READY | Earth DEM acquired; requires reprojection and normalization |
| Earth–Mars | ⚠️ CONDITIONALLY READY | Same as Earth–Moon, additional environmental differences |

## 9. Conclusion

Phase 20 infrastructure is ready for implementation. Moon–Mars comparison can proceed immediately. Earth comparisons require reprojection and resolution normalization of USGS 3DEP data. All scientific limitations from Phases 17–19 are preserved.