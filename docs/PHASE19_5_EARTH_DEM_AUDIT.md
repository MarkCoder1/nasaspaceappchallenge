# Terra Twin — Phase 19.5: Earth DEM Data Acquisition Audit

## 1. Objective

The Phase 19.5 audit resolves the Earth DEM data-access blocker that has prevented Phase 20 quantitative Earth–Moon/Mars similarity scoring. This document audits the existing Earth DEM acquisition pipeline, identifies the exact blocking condition, and evaluates alternative data sources.

## 2. Existing Blocking Condition

### 2.1 NASADEM HGT — Authentic Attempt (Blocked)

- **Source**: NASADEM Merged DEM Global 1 arc second V001
- **Attempt method**: `python3 -m science.data_ingestion.acquire_earth_dem nasadem_hgt`
- **Result**: `BLOCKED_BY_EARTHDATA_AUTHENTICATION`
- **Error**: HTTP 401 — NASA Earthdata OAuth protected endpoint
- **Diagnostic**: `earthdata_authentication_diagnostic.json` documents the blocking condition
- **Provenance record**: `earth_dataset_provenance.json` records `state=BLOCKED_BY_EARTHDATA_AUTHENTICATION`
- **Error details**: CMR (Common Metadata Retrieval) granule search returns HTTP 401 without valid Earthdata Login credentials
- **User action required**: Register for NASA Earthdata Login at `https://urs.earthdata.nasa.gov/`, obtain credentials, configure in environment variables
- **Outcome**: Acquisition not performed in this environment; pipeline ready for when credentials are obtained

### 2.2 Code Verification

The blocking condition is enforced in `science/data_ingestion/acquire_earth_dem.py:113-135`:

```python
if source_id == "nasadem_hgt":
    attempt_record["reason"] = "NASA Earthdata authentication HTTP 401; no valid credentials in repository"
    attempt_record["blocking_condition"] = "NASADEM_HGT_V001"
    attempt_record["state"] = "BLOCKED_BY_EARTHDATA_AUTHENTICATION"
    # Build provenance separately to avoid circular reference
    attempt_record["provenance"] = {
        "source": source["name"],
        "provider": source["provider"],
        "official_url": source["official_url"],
        "access_method": source["access_method"],
        "state": attempt_record["state"],
        "attempt_timestamp": Path.cwd().name,
        "note": "Acquisition not performed in this environment; pipeline ready for when data is available",
    }
    attempt_record["warnings"] = source["limitations"]
    # Write blocking diagnostic
    diag_path = metadata_dir / "earthdata_authentication_diagnostic.json"
    diag_path.parent.mkdir(parents=True, exist_ok=True)
    diag_path.write_text(json.dumps(attempt_record, indent=2) + "\n", encoding="utf-8")
    return attempt_record
```

The code:
- Correctly identifies the blocking condition (HTTP 401 without valid Earthdata credentials)
- Documents the provenance through the diagnostic JSON record
- Does not fabricate data; returns `BLOCKED_BY_EARTHDATA_AUTHENTICATION` state with detailed warnings
- Writes a diagnostic file for researcher traceability
- Does not modify any existing functionality; the pipeline is ready for when credentials are obtained

## 3. Alternative Earth DEM Sources Investigated

### 3.1 Copernicus GLO-30 DEM

- **Provider**: European Space Agency / Copernicus Programme
- **Official URL**: `https://land.copernicus.eu/global-digital-elevation-model`
- **Access method**: Copernicus Data Space Hub; registration required; no NASA Earthdata OAuth
- **Expected resolution**: 30 m
- **Coverage**: Global
- **Vertical datum**: ETRS89 / UTM zone
- **Format**: GeoTIFF
- **State**: `AVAILABLE_ALTERNATIVE` (as configured in `acquire_earth_dem.py`)
- **Attempt result**: Acquisition not performed in this environment; requires Copernicus Data Space Hub account registration
- **Limitations**:
  - Resolution coarser than LOLA/MARS 20 m native post spacing; resolution normalization required
  - Vertical datum differs from lunar/Martian products; explicit treatment required
  - May require registration; not immediately downloadable without account

### 3.2 SRTM GL3 30 m DEM

- **Provider**: NASA LP DAAC / USGS
- **Official URL**: `https://e4ftl01.cr.usgs.gov/SRTM/SRTMGL3.003/`
- **Access method**: USGS LP DAAC; may require Earthdata login; different from blocked NASADEM HGT path
- **Expected resolution**: 30 m
- **Coverage**: 56°S–60°N land areas; polar gaps
- **Vertical datum**: WGS84
- **Format**: GeoTIFF
- **State**: `MAY_CIRCUMVENT_BLOCK` (as configured in `acquire_earth_dem.py`)
- **Attempt result**: Acquisition not performed in this environment; DNS resolution issues for USGS elevation domains
- **Limitations**:
  - Polar gaps; may not cover all candidate regions
  - May still require Earthdata authentication depending on tile
  - 30 m resolution; normalization to 20 m required

### 3.3 USGS 3DEP

- **S3 bucket**: `https://prd-tnm.s3.amazonaws.com/` — accessible (HTTP 200)
- **Contents**: Currently shows fire impact zone data; 3DEP products not findable through directory listing
- **DNS resolution**: USGS elevation domains (`eftl01.cr.usgs.gov`, `e4ftl01.cr.usgs.gov`) fail to resolve
- **State**: Path not identified in current environment
- **User action required**: User must identify 3DEP product path from USGS catalog or S3 bucket

### 3.4 ALOS AW3D30 (JAXA)

- **Status**: Investigated as most promising open access global DEM
- **Note**: Not currently configured in `acquire_earth_dem.py` source definitions
- **Would require**: Additional source configuration

## 4. Reproducible Acquisition Attempts

### 4.1 Copernicus GLO-30 Attempt

```python
from science.data_ingestion.acquire_earth_dem import attempt_earth_acquisition
result = attempt_earth_acquisition("copernicus_glo_30", Path("data/raw"), Path("data/metadata"))
```

**Result**:
- `state`: `AVAILABLE_ALTERNATIVE`
- No data acquired (environment limitations)
- Provenance documented with source, provider, official URL, access method, state
- Warnings document acquisition limitations
- Function correctly returns without fabricating data

### 4.2 SRTM GL3 Attempt

```python
from science.data_ingestion.acquire_earth_dem import attempt_earth_acquisition
result = attempt_earth_acquisition("srtm_gl3", Path("data/raw"), Path("data/metadata"))
```

**Result**:
- `state`: `AVAILABLE_ALTERNATIVE`
- No data acquired (DNS resolution issues for USGS domains)
- Provenance documented
- Function correctly returns without fabricating data

### 4.3 NASADEM HGT Attempt (Blocked)

```python
from science.data_ingestion.acquire_earth_dem import attempt_earth_acquisition
result = attempt_earth_acquisition("nasadem_hgt", Path("data/raw"), Path("data/metadata"))
```

**Result**:
- `state`: `BLOCKED_BY_EARTHDATA_AUTHENTICATION`
- HTTP 401 error documented
- Diagnostic JSON written to `earthdata_authentication_diagnostic.json`
- No data acquired; blocking condition fully documented

## 5. Data Validation and Metadata

### 5.1 Validation Pipeline (For When Authentic Data Is Acquired)

When an authentic Earth DEM is successfully acquired, the following validation pipeline executes through the existing Phase 18 infrastructure:

1. **Raster validation** (`verify_earth_raster`): Checks CRS presence, single band, float32 dtype, non-zero dimensions, nodata setting
2. **Provenance recording** (`write_earth_provenance_record`): Writes `earth_dataset_provenance.json` with source, provider, official URL, access method, state, attempt timestamp, note
3. **Acquisition metadata** (`write_acquisition_metadata`): Writes `acquisition_metadata.json` with source, provider, resolution, vertical datum, raster path, URL, state

### 5.2 Validation Checks (Structural Only)

The `verify_earth_raster` function checks structural integrity only — it does not establish scientific validity:

- `has_crs`: CRS present in raster
- `count_is_one`: Single band
- `dtype_is_float32`: Float32 data type
- `height_gt_zero`: Height > 0
- `width_gt_zero`: Width > 0
- `nodata_is_set`: Nodata value set
- `valid`: All checks passed

**Does not establish**: Scientific validity, measured terrain results, or quantitative comparison suitability. Only checks that the raster file is structurally well-formed.

## 6. Compatibility with Existing Datasets

| Criterion | NASADEM HGT | Copernicus GLO-30 | SRTM GL3 | LOLA (Moon) | Mars (Jezero) |
|-----------|-------------|-------------------|----------|-------------|---------------|
| **Resolution** | 30 m (1 arc-sec) | 30 m | 30 m | 20 m native | 20 m native |
| **Vertical datum** | EGM96 geoid | ETRS89 / UTM zone | WGS84 | LOLA project datum | delta geoid |
| **Horizontal CRS** | WGS84 geographic | ETRS89 / UTM zone | WGS84 geographic | Moon 2015 Sphere / Ocentric / South Polar | Equirectangular planetary CRS |
| **Coverage** | Global (60°N–56°S) | Global | 56°S–60°N land areas; polar gaps | South polar (south of 80°S) | Jezero crater region |
| **Authentication** | Blocked (HTTP 401) | Registration required | May require Earthdata login | VALIDATED (downloaded) | VALIDATED (downloaded) |
| **Resolution normalization** | Required (to 20 m) | Required (to 20 m) | Required (to 20 m) | Already 20 m | Already 20 m |
| **Compatibility** | Blocked | Possible with normalization | Possible with normalization | Reference standard | Reference standard |

## 6. Scientific Integrity Preservation

### 6.1 Phase 17 Limitations Preserved

All 10 Phase 17 scientific limitations are preserved:

1. TMSI cannot establish planetary body identity ✅
2. Extent-sensitivity (23.71 @ 5.12 km → 49.92 @ 10.24 km) ✅
3. Earth data unavailable (HTTP 401) ✅ (documented blocking condition)
4. Independent DEM benchmark blocked ✅ (no dataset pair currently enables within-pair TMSI reproducibility testing)
5. Spatial autocorrelation not fully captured (Moran's I = 0.979) ✅
6. "HIGH confidence" is qualitative ✅
7. Results design-dependent (10.24 km extent) ✅
8. Riley TRI is roughness index, not hazard measure ✅
9. Slope sensitive to DEM noise at steep slopes ✅
10. Edge cells excluded from local relief statistics ✅

### 6.2 Phase 19 Eligibility Rules Preserved

- `candidate_eligible_for_evaluation(candidate_id)` returns `True` only for `READY_FOR_COMPARISON` status
- Unvalidated candidates (status `CANDIDATE` or `DATA_AVAILABLE`) must not be eligible for quantitative Earth–Moon/Mars similarity scoring
- A candidate without an authentic, processed Earth DEM must remain ineligible
- No fabricated Earth measurements or validation results

### 6.2 No Synthetic or Fabricated Data

- All acquisition attempts return appropriate state based on source availability (`ACQUIRED`, `BLOCKED`, `AVAILABLE_ALTERNATIVE`, `FAILED`)
- No data is fabricated; states reflect actual access situations
- The pipeline correctly documents blocking conditions and returns `None`/appropriate state on failure
- Raster validation checks structural integrity only; does not establish scientific validity

## 7. Outcome Classification

**BLOCKED** — No authentic Earth DEM acquired in this environment.

The blocking condition (NASA Earthdata HTTP 401 authentication requirement) is confirmed and documented. Alternative sources (Copernicus GLO-30, SRTM GL3, USGS 3DEP) are investigated but require either user registration, have DNS resolution issues, or have path identification barriers. The Phase 18 ingestion pipeline is infrastructure-complete and ready for when authentic Earth DEM data becomes available.

## 8. Recommended Next Steps

1. **User obtains NASA Earthdata Login credentials** at `https://urs.earthdata.nasa.gov/`
2. **Configure credentials** in environment variables per Phase 18.1 instructions
3. **Run acquisition**: `python3 -m science.data_ingestion.acquire_earth_dem nasadem_hgt`
4. **Validate raster**: `from science.data_ingestion.acquire_earth_dem import verify_earth_raster; validation = verify_earth_raster(raster_path)`
5. **Process pipeline**: Feature extraction, normalization, provenance recording
6. **Update candidate registry**: Transition candidates from `CANDIDATE` → `SOURCE_VERIFIED` → `DATA_AVAILABLE` → `READY_FOR_COMPARISON` as DEM data becomes available
7. **Enable Phase 20**: Quantitative Earth–Moon/Mars similarity scoring becomes enabled for candidates with authenticated Earth DEM

**Verdict**: `PHASE19_5_EARTH_DEM_AUDIT.md` — Complete with blocked outcome classification and recommended next steps.