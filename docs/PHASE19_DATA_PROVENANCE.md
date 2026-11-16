# Terra Twin — Phase 19: Data Provenance

## 1. Overview

Data provenance in Terra Twin Phase 19 traceability records the origin, acquisition history, and licensing information for all candidate geographic locations, source datasets, and Earth elevation data. The provenance system ensures that no fabricated datasets, measurements, or scientific results are presented, and that all existing limitations from Phases 17 and 18.1 are preserved.

## 2. Provenance Tracking for Candidates

Each candidate registry entry maintains the following provenance fields:

| Field | Description | Source |
|------|-------------|--------|
| `supporting_references` | Source organization and publications supporting the candidate's inclusion | Populated from NASA, USGS, ESA, and peer-reviewed publications |
| `source_dataset` | Name of the dataset used for candidate selection | e.g., `USGS 3DEP`, `SRTM`, `NASA MEaSUREs` |
| `source_url` | Direct URL to the source dataset or publication | Official URL from the producing institution |
| `data_acquisition_status` | Status of any Earth DEM acquisition attempt | e.g., `available`, `pending`, `unknown` |
| `last_updated` | Timestamp of last catalog modification | `YYYY-MM-DD` format or ISO timestamp |

### Provenance Integrity Rules

- **No fabricated data**: All provenance information reflects actual attempts or documented availability. No dataset is claimed to exist if it does not.
- **No unsupported accuracy claims**: Provenance records document what is known and what is unknown; they do not invent measurements or validation results.
- **Dataset licensing information**: Official source URLs retain licensing and access condition information. Users must comply with the terms of the original data providers (NASA, USGS, ESA, etc.).
- **Earth data acquisition blocking documented**: The provenance system records that `earth_nasadem_hgt_v001` is `BLOCKED_BY_EARTHDATA_AUTHENTICATION` — HTTP 401 without valid Earthdata credentials. No fabricated Earth DEM is presented as available.

## 3. Earth Data Acquisition Provenance

### 3.1 NASADEM HGT — Blocked State

- **Source**: NASADEM HGT V001 via NASA Earthdata
- **Access method**: NASA Earthdata; HTTP 401 without credentials
- **Current state**: `BLOCKED_BY_EARTHDATA_AUTHENTICATION`
- **Diagnostic record**: `earthdata_authentication_diagnostic.json` documents the blocking condition
- **Provenance record**: `earth_dataset_provenance.json` records `state: BLOCKED_BY_EARTHDATA_AUTHENTICATION`
- **User action required**: Register for NASA Earthdata Login at `https://urs.earthdata.nasa.gov/`, obtain credentials, configure locally
- **Outcome**: Acquisition not performed; pipeline ready for when credentials are obtained

### 3.2 Alternative Sources (Documented, Not Acquired)

| Source | Provider | Expected Resolution | Status |
|--------|----------|---------------------|--------|
| Copernicus GLO-30 DEM | ESA / Copernicus Programme | 30 m | Registration required; no acquisition attempted in this environment |
| SRTM GL3 30 m DEM | NASA LP DAAC / USGS | 30 m | Polar gaps; may require Earthdata authentication depending on tile |
| USGS 3DEP | U.S. Geological Survey | 1 m–30 m | S3 bucket verified; 3DEP product path not yet identified globally |
| ALOS AW3D30 | JAXA | 30 m | Most promising open access global DEM; no acquisition attempted |

All alternative source states are documented through the `acquire_earth_dem.py` source configuration, which reports `state: AVAILABLE_ALTERNATIVE`, `MAY_CIRCUMVENT_BLOCK`, or `BLOCKED_BY_EARTHDATA_AUTHENTICATION` — never fabricated.

## 4. Provenance Recording Pipeline

### 4.1 When Authentic Earth DEM Is Acquired

When an authentic Earth DEM is successfully acquired through the Phase 18 pipeline, the following provenance steps are executed:

1. **Acquisition**: `attempt_earth_acquisition(source_id, raw_dir, metadata_dir)` returns a result dict with state, provenance, and warnings
2. **Raster validation**: `verify_earth_raster(raster_path)` checks structural integrity (CRS, dtype, dimensions, nodata)
3. **Provenance recording**: `write_earth_provenance_record(metadata_dir, record)` writes `earth_dataset_provenance.json`
4. **Acquisition metadata**: `write_acquisition_metadata(dataset, raster_path, metadata_dir, url)` writes `acquisition_metadata.json`

### 4.2 Provenance Record Structure

A provenance record includes:
- `source`: Human-readable source name
- `provider`: Producing institution or organization
- `official_url`: Official URL for the data source
- `access_method`: Description of how the data was acquired or attempted
- `state`: `ACQUIRED`, `BLOCKED`, `AVAILABLE_ALTERNATIVE`, or `PENDING`
- `attempt_timestamp`: When the attempt was made
- `note`: Detailed description of the outcome (success, block, or limitation)
- `warnings`: List of known limitations or cautions

## 5. Provenance and Phase 20 Integration

### 5.1 Source Provenance Retention

All candidate metadata retains source provenance throughout the status workflow. When a candidate transitions from `CANDIDATE` to `SOURCE_VERIFIED` to `DATA_AVAILABLE` to `READY_FOR_COMPARISON`, the `supporting_references` and `source_url` fields are preserved and never fabricated or altered.

### 5.2 Validation Status Provenance

The `scientific_validation_status` field (`unvalidated` or `validated`) is tracked alongside the candidate status. Only candidates with `READY_FOR_COMPARISON` status and `validated` scientific validation status are eligible for Phase 20 quantitative comparison.

### 5.3 Provenance Integrity Enforcement

- `candidate_eligible_for_evaluation(candidate_id)` enforces that only `READY_FOR_COMPARISON` candidates are eligible
- The registry `update_candidate_status()` function prevents status transitions without documented prerequisites
- Backend `similarity_status()` reports Earth comparisons as disabled until a validated Earth DEM is acquired
- The CandidateDetailPanel displays an explicit integrity statement for CANDIDATE-status candidates

## 6. Known Limitations

- No authentic Earth DEM acquired in this environment (blocked by NASA Earthdata HTTP 401)
- All candidate provenance records reflect documented attempts or unavailable statuses — no fabricated data
- Earth data acquisition pipeline (Phase 18) is infrastructure-complete; acquisition pending user credentials
- Dataset licensing requirements must be satisfied by the user independently; Terra Twin does not provide licensing validation
- Pre-existing provenance records from Phases 17 and 18.1 are preserved and not modified

**Verdict**: PHASE19_DATA_PROVENANCE.md — Complete with documented limitations.