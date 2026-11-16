# Terra Twin — Phase 18.1: Initial Issue Audit

**Project:** Terra Twin  
**Phase:** 18.1 — Pre Phase 19 stabilization  
**Previous phase:** Phase 18 — Authentic Earth Dataset Integration  
**Status:** IN PROGRESS

## 1. Audit Scope

This document records the findings from investigating authentic Earth DEM acquisition routes, technical issues, and code quality matters that must be resolved before Phase 19 (Earth Candidate Registry & Interactive Discovery Map) can begin.

The audit covers:
- Earth data source investigation (USGS 3DEP, Copernicus, NASA Earthdata)
- Technical issue inventory
- Code quality and warning cleanup
- Regression test status
- Documentation readiness

## 2. Earth Data Source Investigation

### 2.1 NASADEM HGT (Blocked)
- **Status**: BLOCKED_BY_EARTHDATA_AUTHENTICATION (HTTP 401)
- **Provider**: NASA LP DAAC / NASA JPL
- **Product**: NASADEM HGT V001, 30 m (1 arc-second) global land between 60°N and 56°S
- **Vertical datum**: EGM96
- **Access method**: NASA Earthdata; requires valid Earthdata credentials
- **Blockage reason**: Official `lp-prod-protected` URL redirects to NASA Earthdata OAuth; returns HTTP 401 without credentials
- **Repository status**: `earth_nasadem_hgt_v001` catalog entry state=PENDING; `earthdata_authentication_diagnostic.json` documents blocking condition
- **Attempted in Phase 18**: Pipeline infrastructure fully implemented; no data acquired
- **Required action**: User must obtain NASA Earthdata Login credentials (free account at https://urs.earthdata.nasa.gov/)

### 2.2 SRTM GL3 30 m DEM (Alternative Path)
- **Status**: MAY_CIRCUMVENT_BLOCK — investigation needed
- **Provider**: NASA LP DAAC / USGS
- **Product**: SRTM GL3, 30 m resolution
- **Coverage**: 56°S–60°N land areas; polar gaps
- **Vertical datum**: WGS84
- **Format**: GeoTIFF
- **Access method**: USGS LP DAAC; may require Earthdata login; different from blocked NASADEM HGT path
- **Data URLs**: `https://eftl01.cr.usgs.gov/SRTM/SRTMGL3.003/` and `https://e4ftl01.cr.usgs.gov/SRTM/SRTMGL3.003/`
- **DNS resolution**: `eftl01.cr.usgs.gov` fails to resolve in current environment; `e4ftl01.cr.usgs.gov` also unresolved
- **S3 bucket**: `prd-tnm.s3.amazonaws.com` resolves; 3DEP products not findable through directory listing
- **Tested tile**: `SRTMGL3_h04v05.zip` at `e4ftl01.cr.usgs.gov` returned HTTP 404
- **Requirement**: User must verify tile availability and access method
- **Potential**: If SRTM GL3 is accessible without authentication, it would provide an authentic Earth DEM without the NASA Earthdata barrier

### 2.3 Copernicus GLO-30 DEM (Registered access required)
- **Status**: AVAILABLE_ALTERNATIVE (documented); actual acquisition requires account
- **Provider**: European Space Agency / Copernicus Programme
- **Product**: Copernicus GLO-30 DEM, 30 m post spacing global
- **Coverage**: Global
- **Vertical datum**: ETRS89 / UTM zone
- **Format**: GeoTIFF
- **Data URL**: `https://dataspace.copernicus.eu/`
- **Account requirement**: Free account registration at `https://dataspace.copernicus/`; CCM (Copernicus Contributing Missions) access may be required for GLO products
- **Registration workflow**:
  1. Visit `https://dataspace.copernicus/`
  2. Create free account
  3. Verify email address
  4. Open account profile
  5. Select option for Copernicus Contributing Missions data access
  6. Complete registration information
  7. Submit access request
- **OData API**: Requires OAuth2 token; S3 bulk access with generated credentials
- **GLO-30 vs GLO-90**: Must distinguish between DSM (Digital Surface Model) and DTM (Digital Terrain Model); GLO products must not be automatically described as bare-earth terrain
- **Requirement**: User must complete registration and verify access before acquisition attempt

### 2.4 USGS 3DEP DEM (Direct public access investigation)
- **Status**: Investigation needed; direct public access generally available without account
- **Provider**: USGS The National Map
- **Product**: 3DEP (3D Elevation Program) DEM, various resolutions (1 m–30 m)
- **Coverage**: Continental US primarily; global coverage being built out
- **Vertical datum**: NAVD88 / WGS84 (varies by product)
- **Data catalog**: `https://data.usgs.gov/datacatalog/`
- **Tested endpoints**:
  - `https://elevation.nationalmap.gov/` — gateway timeout
  - `https://elevation.nationalmap.gov/arcgis/rest/services/` — gateway timeout
  - `https://apps.nationalmap.gov/api/v1/products` — returns HTML, not JSON (frontend-rendered)
  - `https://prd-tnm.s3.amazonaws.com/` — S3 bucket accessible, 3DEP products not findable through listing
  - SRTM GL3 tiles (`eftl01.cr.usgs.gov`, `e4ftl01.cr.usgs.gov`) — DNS resolution fails in current environment
- **Requirement**: User must verify 3DEP data availability through USGS data catalog or direct download
- **Potential**: USGS 3DEP direct public download is the preferred route if accessible, as it typically does not require account creation

### 2.5 Copernicus GLO-90 DEM
- **Status**: Same access requirements as GLO-30
- **Product**: Copernicus GLO-90 DEM, 90 m post spacing global
- **Distinction from GLO-30**: Coarser resolution; different product identification
- **Access**: Same Copernicus Data Space Hub registration required

## 3. Technical Issue Inventory

### 3.1 Rasterio NotGeoreferencedWarning
- **Affected code**: Test fixtures in `science/tests/test_phase18_validation.py`
- **Description**: `NotGeoreferencedWarning: Dataset has no geotransform, GCPs, or RPCs. The identity matrix will be returned.` reported during test execution
- **Root cause**: Test rasters created without valid geotransform/CRS, or with identity transform only
- **Severity**: Medium (warning, not error)
- **Reproduction**: Runs during `python3 -m pytest science/tests/test_phase18_validation.py`
- **Proposed correction**:
  - Option A: Add valid transform and CRS to test fixtures representing a geospatial raster
  - Option B: Document that certain test fixtures intentionally represent non-georeferenced synthetic rasters and ensure they are never mistaken for real geographic datasets
  - Option C: Add `import warnings; warnings.filterwarnings('ignore', category=rasterio.NotGeoreferencedWarning)` in test setup
- **Verification**: Re-run affected tests after correction; warning should be eliminated or properly documented

### 3.2 NumPy PendingDeprecationWarning
- **Affected code**: `science/earth_normalization.py` line 69
- **Description**: `PendingDeprecationWarning: Use @ matmul instead of * mul operator for matrix multiplication`
- **Root cause**: `new_transform = src.transform * src.transform.scale(` uses `*` for matrix multiplication instead of `@`
- **Severity**: Medium (pending deprecation, not immediate error)
- **Mathematical equivalence**: For 2×2 transformation matrices, `*` and `@` produce different results. The `*` operator performs element-wise multiplication, while `@` performs matrix multiplication. If `src.transform.scale()` returns a proper scale matrix, the two operations are not equivalent.
- **Tested equivalence**: Need to verify whether `src.transform * src.transform.scale()` is mathematically intentional or should be `src.transform @ src.transform.scale()`
- **Proposed correction**: If matrix multiplication is intended, change `*` to `@`. If element-wise multiplication is intentional, add a comment explaining the design choice.
- **Verification**: Run numerical tests comparing results before and after change; ensure no regression in geotransform calculations

### 3.3 ESLint Baseline (8 errors)
- **Current baseline**: 8 errors (established in Phase 17, carried into Phase 18)
- **Investigation needed**: All 8 errors must be classified
- **Classification categories**:
  - Existing baseline issues (pre-Phase 18, should not be touched unless relevant)
  - Newly introduced issues (from Phase 18 changes; should fix if safe)
  - Genuine correctness problems (must fix)
  - Style/configuration issues (fix if safe, no unnecessary rewrites)
- **Requirement**: Fix safe, relevant issues without unnecessarily rewriting working components
- **Non-negotiable**: Do not modify unrelated functionality merely to reduce an error count

### 3.4 TypeScript Zero-Error Result
- **Status**: 0 TypeScript errors maintained (`npx tsc --noEmit`)
- **Verification**: Preserved from Phase 18; no new errors introduced
- **Non-negotiable**: Must remain at 0 errors

## 4. Code Quality and Warning Cleanup

### 4.1 Rasterio Warning Cleanup
- **File**: `science/tests/test_phase18_validation.py`
- **Issue**: `NotGeoreferencedWarning` during test execution
- **Current state**: 14/14 tests pass; warnings reported by pytest but not treated as failures
- **Action**: Determine whether to fix the root cause (add geotransform to test fixtures) or document the intentional use of synthetic non-georeferenced rasters

### 4.2 NumPy Warning Cleanup
- **File**: `science/earth_normalization.py` line 69
- **Issue**: `PendingDeprecationWarning` for matrix multiplication
- **Current state**: Warning reported but not treated as error
- **Action**: Verify whether `*` or `@` is correct for the transformation; apply correction if mathematically equivalent

### 4.3 ESLint 8 Errors
- **File**: Throughout frontend source
- **Action**: Classify all 8 errors; fix safe, relevant issues; do not unnecessary rewrite working components
- **Baseline preservation**: Must not increase error count above 8

### 4.4 TypeScript
- **Action**: Preserve 0-error result; do not introduce new errors

## 5. Regression and Scientific Validation

### 5.1 Python Test Suite
- **Result**: 14/14 Phase 18 validation tests pass
- **Tests**: `test_phase18_validation.py` — all synthetic, no real Earth data acquired
- **Moon/Mars tests**: 116/116 Python tests continue to pass (verified in Phase 18)
- **Action**: Rerun all tests after any code changes; preserve passing status

### 5.2 Scientific Limitations Preservation
- **All 10 limitations preserved**: TMSI cannot establish planetary body identity, extent-sensitivity, Earth data unavailable (HTTP 401), independent DEM benchmark blocked, spatial autocorrelation not fully captured, "HIGH confidence" is qualitative, results design-dependent, Riley TRI is roughness index, slope sensitive to DEM noise, edge cells excluded from local relief
- **Action**: Verify no limitation is weakened or removed during Phase 18.1 changes

### 5.3 Existing Functionality Preservation
- **Moon/Mars comparison**: All existing functionality preserved
- **TMSI computation**: Unchanged
- **Feature extraction**: Unchanged
- **Test suite**: 116/116 Python tests pass; 14/14 Phase 18 validation tests pass

## 6. Documentation Status

### 6.1 Phase 18 Documentation (Complete)
- `docs/PHASE18_DATASET_ACQUISITION.md` — ✅ Complete
- `docs/PHASE18_INGESTION_ARCHITECTURE.md` — ✅ Complete
- `docs/PHASE18_SCIENTIFIC_VALIDATION.md` — ✅ Complete
- `docs/PHASE18_DATA_PROVENANCE.md` — ✅ Complete
- `docs/PHASE18_FINAL_REPORT.md` — ✅ Complete

### 6.2 Phase 18.1 Deliverables (In Progress)
- `docs/PHASE18_1_INITIAL_ISSUE_AUDIT.md` — ✅ In production (this file)
- `docs/PHASE18_1_PROVIDER_ACCESS_REPORT.md` — Not yet started
- `docs/PHASE18_1_AUTHENTIC_DATA_ACQUISITION.md` — Not yet started
- `docs/PHASE18_1_WARNING_CLEANUP.md` — Not yet started
- `docs/PHASE18_1_SCIENTIFIC_VERIFICATION.md` — Not yet started
- `docs/PHASE18_1_FINAL_REPORT.md` — Not yet started

## 7. Phase 18.1 Exit Criteria Assessment

| Criterion | Status |
|-----------|--------|
| Outstanding technical issues audited | ✅ (this document) |
| At least one legitimate Earth data acquisition route tested | ⚠️ SRTM GL3, Copernicus investigated; actual acquisition not yet successful in this environment |
| At least one authentic Earth DEM acquired | ❌ Not yet acquired (authentication barriers, DNS resolution issues) |
| Metadata and source verified | ❌ (pending acquisition) |
| Passed geospatial integrity validation | ❌ (pending acquisition) |
| Entered actual Earth processing pipeline | ❌ (pending acquisition) |
| Terrain features calculated from authentic raster | ❌ (pending acquisition) |
| Machine-readable provenance generated | ❌ (pending acquisition) |
| Existing regression tests pass | ✅ (14/14 validation tests; 116/116 Moon/Mars tests) |
| Remaining authentication/warning issues documented | ✅ (this document) |
| All six documentation deliverables produced | ⚠️ Only initial issue audit started |

## 8. Immediate Action Required

### 8.1 User Intervention Required (Authentication)
The following providers require user action for authentication/registration:

1. **NASA Earthdata**: Free account at `https://urs.earthdata.nasa.gov/`
   - Required for: NASADEM HGT acquisition
   - Steps: Register, verify email, obtain token/credentials
   - Credential configuration: `EARTHDATA_USERNAME` and `EARTHDATA_TOKEN` environment variables

2. **Copernicus Data Space**: Free account at `https://dataspace.copernicus/`
   - Required for: Copernicus GLO-30/GLO-90 DEM acquisition
   - Steps: Register, verify email, select CCM access, obtain OAuth2 token
   - Credential configuration: `COPERNICUS_ACCESS_TOKEN` environment variable

3. **USGS 3DEP**: No account typically required, but verification needed
   - Tested endpoints: S3 bucket, National Map API, elevation services
   - Current environment: DNS resolution issues for `eftl01.cr.usgs.gov` and `e4ftl01.cr.usgs.gov`
   - Action: User must verify 3DEP data accessibility from their environment

### 8.2 Independent Work (No User Intervention Required)
The following can proceed without user action:
- Complete warning cleanup (rasterio, NumPy)
- ESLint classification and fix
- Test suite verification
- Documentation production for completed work
- Pipeline infrastructure verification

---
*This initial issue audit documents the investigation status as of Phase 18.1 launch. User action required for authentication on all major Earth data providers. Independent code quality and infrastructure work can proceed concurrently.*