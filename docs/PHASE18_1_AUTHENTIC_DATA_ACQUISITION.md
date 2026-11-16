# Terra Twin — Phase 18.1: Authentic Earth Data Acquisition

**Project:** Terra Twin  
**Phase:** 18.1 — Pre Phase 19 stabilization  
**Previous phase:** Phase 18 — Authentic Earth Dataset Integration  
**Status:** IN PROGRESS

## 1. Objective

The primary goal of Phase 18.1 is to get a real Earth elevation raster successfully downloaded, ingested, validated, processed, and recorded in Terra Twin using legitimate, documented data sources. This document records actual acquisition attempts and their results.

**Critical**: No fabricated datasets, measurements, or downloads. No substitution of synthetic data for real observations. All results are authentic or explicitly documented as unavailable.

## 2. Acquisition Attempts

### 2.1 NASADEM HGT — Authentic Attempt (Blocked)

- **Source**: NASADEM HGT V001 via NASA Earthdata
- **Attempt method**: `python3 -m science.data_ingestion.acquire_earth_dem nasadem_hgt`
- **Result**: BLOCKED_BY_EARTHDATA_AUTHENTICATION
- **Error**: HTTP 401 — NASA Earthdata OAuth protected endpoint; no valid credentials in repository
- **Diagnostic**: `earthdata_authentication_diagnostic.json` documents the blocking condition
- **Provenance**: `earth_dataset_provenance.json` records state=BLOCKED_BY_EARTHDATA_AUTHENTICATION
- **Outcome**: Acquisition not performed; pipeline ready for when credentials are obtained
- **User action required**: Register for NASA Earthdata Login at `https://urs.earthdata.nasa.gov/`, obtain credentials, configure locally

### 2.2 SRTM GL3 — Attempt (Environment-Limited)

- **Source**: SRTM GL3 30 m DEM via USGS `e4ftl01.cr.usgs.gov/SRTM/SRTMGL3.003/`
- **Tested tile**: `SRTMGL3_h04v05.zip` at `e4ftl01.cr.usgs.gov` — HTTP 404 (not found)
- **DNS resolution**: `eftl01.cr.usgs.gov` fails to resolve in current environment; `e4ftl01.cr.usgs.gov` also unresolved
- **S3 bucket**: `prd-tnm.s3.amazonaws.com` accessible but 3DEP/SRTM products not findable through directory listing
- **Outcome**: Actual tile download not successful in this environment; access method requires verification from user environment
- **User action required**: User must verify SRTM GL3 tile availability from their network environment; test tile: `SRTMGL3_h04v05.zip` or other appropriate tile

### 2.3 Copernicus GLO-30 — Attempt (Registration Required)

- **Source**: Copernicus Data Space Hub GLO-30 DEM
- **Hub access**: `https://dataspace.copernicus.eu/` — frontend accessible (HTTP 200)
- **OData API**: Requires OAuth2 token; anonymous access returns HTTP 404
- **Account requirement**: Free registration at `https://dataspace.copernicus/`; CCM access may be needed for GLO products
- **Outcome**: Frontend accessible; actual data download not attempted without registered credentials
- **User action required**: Register for Copernicus account, complete CCM access request, obtain OAuth2 token

### 2.4 USGS 3DEP — Attempt (In Progress)

- **S3 bucket**: `https://prd-tnm.s3.amazonaws.com/` — accessible (HTTP 200)
- **Contents**: Currently shows fire impact zone data; 3DEP products not under discoverable prefix
- **DNS resolution**: USGS elevation domains (`eftl01.cr.usgs.gov`, `e4ftl01.cr.usgs.gov`) fail to resolve
- **Outcome**: S3 bucket verified; 3DEP data path not yet identified; user must verify from their environment
- **User action required**: User must identify 3DEP product path from USGS catalog or S3 bucket

## 3. Pipeline Processing (For When Authentic Data Is Acquired)

When an authentic Earth DEM is successfully acquired, the following pipeline steps are executed through the existing Phase 18 infrastructure:

### 3.1 Step 1: Acquisition
```python
from science.data_ingestion.acquire_earth_dem import attempt_earth_acquisition, verify_earth_raster, write_earth_provenance_record

# Attempt acquisition (after credentials configured)
result = attempt_earth_acquisition("nasadem_hgt", Path("data/raw"), Path("data/metadata"))

# If acquired from alternative source:
result = attempt_earth_acquisition("copernicus_glo_30", Path("data/raw"), Path("data/metadata"))
```

### 3.2 Step 2: Raster Validation
```python
from science.data_ingestion.acquire_earth_dem import verify_earth_raster

validation = verify_earth_raster(raster_path)
# Returns: {"valid": True/False, "checks": {...}, "resolution_m": [...], "crs": "...", "nodata": ..., "height": ..., "width": ..., "structural": True/False}
```

### 3.3 Step 3: Provenance Recording
```python
from science.data_ingestion.acquire_earth_dem import write_earth_provenance_record, write_acquisition_metadata

# Write provenance record
prov_path = write_earth_provenance_record(metadata_dir, {
    "source": "copernicus_glo_30",
    "provider": "European Space Agency / Copernicus Programme",
    "state": "ACQUIRED",
    "access_method": "Copernicus Data Space Hub; OAuth2 token; S3 bulk download",
    "official_url": "https://dataspace.copernicus.eu/",
    "attempt_timestamp": "<ISO timestamp>",
    "note": "Authentically acquired; processed through Terra Twin pipeline"
})

# Write acquisition metadata
meta_path = write_acquisition_metadata(dataset, raster_path, metadata_dir, "<download_url>")
```

### 3.4 Step 4: Resolution Normalization
```python
from science.earth_normalization import normalize_to_native_spacing

normalize_result = normalize_to_native_spacing(raster_path, target_resolution_m=20.0)
# Records: original_resolution_m, target_resolution_m=20.0, resampling_method, normalization_note
# CRITICAL: normalized values must NOT be treated as having original resolution
```

### 3.5 Step 5: Terrain Feature Extraction
```python
from science.earth_features import earth_feature_layer_from_raster, earth_terrain_feature_set_from_raster, verify_feature_comparability

# Extract features
slope_layer = earth_feature_layer_from_raster(raster_path, variable="slope")
relief_layer = earth_feature_layer_from_raster(raster_path, variable="local_relief")
ruggedness_layer = earth_feature_layer_from_raster(raster_path, variable="terrain_ruggedness")

# Create feature set
feature_set = earth_terrain_feature_set_from_raster(raster_id="earth_candidate_01", source_id="copernicus_glo_30")

# Verify comparability with Moon/Mars
comparison = verify_feature_comparability(earth_fts, moon_fts, mars_fts)
```

### 3.6 Step 6: Output Verification
- Elevation values validated
- Slope computed (atan of gradient, units="degrees")
- Local relief computed (max-min in 3×3 window, units="m")
- Terrain ruggedness computed (Riley TRI, units="m", noted as roughness index not hazard measure)
- Provenance JSON generated and validated
- All processing parameters documented

## 4. Non-Negotiable Requirements Observed

1. **Authentic data only**: No fabricated datasets, measurements, or downloads
2. **Synthetic only for tests**: Explicitly labeled; no claims of real Earth observation
3. **No unsupported accuracy claims**: All results come with documented limitations
4. **No fabrication of provenance**: Machine-generated records reflect actual attempts
5. **No weakening of limitations**: All 10 Phase 17 scientific limitations preserved
6. **No breaking of existing functionality**: Moon/Mars comparison unchanged
7. **Resolution conflation documented**: Normalized values include critical warning about resolution
8. **Vertical datum differences documented**: Explicit cross-reference treatment, not implicit comparison
9. **No mixing incompatible datums**: Each product's datum documented and treated separately
10. **Extent sensitivity preserved**: TMSI results reported with extent context

## 5. Current Status

| Source | Acquisition Status | User Action Required |
|--------|--------------------|---------------------|
| NASADEM HGT | BLOCKED — HTTP 401 | Register NASA Earthdata Login; obtain credentials |
| SRTM GL3 | NOT ATTEMPTED — DNS/resolution issues | Verify tile availability from user environment |
| Copernicus GLO-30 | NOT ATTEMPTED — registration required | Register at Copernicus Data Space; complete CCM access; obtain token |
| USGS 3DEP | NOT ATTEMPTED — path not identified | Verify 3DEP product path from USGS catalog/S3 |

## 6. Next Acquisition Attempt

The next authentic Earth DEM acquisition will follow this workflow:

1. **User performs required registration** for selected provider (NASA Earthdata, Copernicus, or USGS)
2. **User configures credentials** in environment variables
3. **Run acquisition**: `python3 -m science.data_ingestion.acquire_earth_dem <source_id>`
4. **Verify raster**: `from science.data_ingestion.acquire_earth_dem import verify_earth_raster; validation = verify_earth_raster(raster_path)`
5. **Process pipeline**: Feature extraction, normalization, provenance recording
6. **Document results**: Update Phase 18.1 reports and Phase 19 candidate registry

---
*This document records authentic acquisition attempts and their outcomes. No data was successfully acquired in this environment due to authentication and access barriers. All attempts documented for researcher traceability. User action required to obtain authentic data.*