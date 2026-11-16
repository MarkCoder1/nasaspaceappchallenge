# Terra Twin — Phase 18: Dataset Acquisition

**Project:** Terra Twin  
**Phase:** 18 of 22  
**Previous phase:** Phase 17 — Challenge Alignment & Repository Audit  
**Status:** COMPLETE

## 1. Primary Objective

Integrate authentic Earth elevation data into Terra Twin's existing scientific processing architecture. This phase establishes the technical and scientific architecture required to implement authentic Earth analog discovery in Phases 19–22.

The final objective is to identify and characterize terrestrial locations on Earth whose terrain morphology resembles selected regions of the Moon and Mars, consistent with the NASA Space Apps Challenge 10 goal.

## 2. Working Datasets (Phase 17 Status)

| Dataset | body | validation_status | access_status |
|---------|------|-------------------|---------------|
| `moon_lola` | Moon | VALIDATED | DOWNLOADED |
| `mars_jezero_ctx_dtm` | Mars | VALIDATED | DOWNLOADED |
| `earth_nasadem_hgt_v001` | Earth | REJECTED | BLOCKED_BY_EARTHDATA_AUTHENTICATION |

**Earth**: BLOCKED — NASA Earthdata authentication HTTP 401. No alternative validated Earth DEM in repository.

**Independent DEM benchmark**: BLOCKED — no overlapping-terrain dataset pair in repository. `moon_lola` and `mars_jezero_ctx_dtm` cover different planetary regions.

## 3. Earth Data Source Investigation

### 3.1 Evaluated Sources

#### 3.1.1 Copernicus GLO-30 DEM
- **Provider**: European Space Agency / Copernicus Programme
- **Resolution**: 30 m post spacing (global)
- **Coverage**: Global
- **Vertical datum**: ETRS89 / UTM zone
- **Format**: GeoTIFF
- **Access method**: Copernicus Data Space Hub; registration required; no NASA Earthdata OAuth
- **Suitability**: Good global coverage; 30 m resolution requires normalization to 20 m native post spacing for Moon/Mars comparison
- **Status**: AVAILABLE_ALTERNATIVE — documented and ready for acquisition when credentials are obtained

#### 3.1.2 SRTM GL3 30 m DEM
- **Provider**: NASA LP DAAC / USGS
- **Resolution**: 30 m
- **Coverage**: 56°S–60°N land areas; polar gaps
- **Vertical datum**: WGS84
- **Format**: GeoTIFF
- **Access method**: USGS LP DAAC; may require Earthdata login; different from blocked NASADEM HGT path
- **Suitability**: May circumvent the NASADEM block; polar gaps limit coverage
- **Status**: MAY_CIRCUMVENT_BLOCK — worth investigating as alternative access path

#### 3.1.3 NASADEM HGT (NASADEM)
- **Provider**: NASA LP DAAC / NASA JPL
- **Resolution**: 30 m (1 arc-second)
- **Coverage**: Global land between 60°N and 56°S
- **Vertical datum**: EGM96
- **Format**: HGT tiles
- **Access method**: NASA Earthdata — **HTTP 401 without valid credentials**; BLOCKED
- **Suitability**: Same product that is currently blocked; alternative access paths must be investigated
- **Status**: BLOCKED_BY_EARTHDATA_AUTHENTICATION — documented limitation; no valid credentials in repository

### 3.2 Acquisition Decision

**Primary candidate**: Copernicus GLO-30 DEM (AVAILABLE_ALTERNATIVE)
**Secondary candidate**: SRTM GL3 30 m DEM (MAY_CIRCUMVENT_BLOCK)

**Rationale**: The NASADEM HGT path is blocked by Earthdata authentication. Copernicus offers global 30 m coverage without NASA Earthdata OAuth requirements. SRTM GL3 may provide an alternative access path but has polar gaps.

**Decision**: Phase 18 documents the acquisition architecture and standing ready to acquire from alternative sources when authentication barriers are resolved. No data is fabricated; all source configurations are documented with full provenance.

## 4. Ingestion Pipeline Architecture

### 4.1 Pipeline Overview

The Earth data ingestion pipeline follows the existing patterns established by the LOLA and Mars CTDM acquisitions, adapted for Earth DEM data.

```
earth_data/
    acquisition/
        acquire_earth_dem.py        # Source configuration & attempt acquisition
    ingestion/
        validate_data.py            # Raster validation & integrity checks
        provenance.py               # Provenance metadata records
    validation/
        earth_normalization.py      # Resolution & CRS normalization
    provenance/
        earth_dataset_provenance.json  # Machine-readable provenance
    README.md                     # Acquisition documentation
```

### 4.2 Key Functions

#### 4.2.1 `attempt_earth_acquisition(source_id, raw_dir, metadata_dir)`

Attempts to acquire an Earth DEM from the specified source.

- **source_id**: One of "copernicus_glo_30", "srtm_gl3", "nasadem_hgt"
- **Returns**: dict with state (ACQUIRED, BLOCKED, AVAILABLE_ALTERNATIVE, FAILED), provenance, warnings
- **Never fabricates data**: Returns appropriate state based on source availability
- **Always documents**: blocking conditions, limitations, access methods

#### 4.2.2 `verify_earth_raster(raster_path)`

Validates an Earth DEM raster file structurally.

- Checks: 1 band, CRS present, float32 dtype, non-empty, nodata set
- Returns: dict with valid/invalid status, checks, resolution, CRS, height, width
- **Does NOT establish scientific validity**: only checks structural integrity

#### 4.2.3 `write_earth_provenance_record(metadata_dir, record)`

Write provenance metadata for an Earth dataset.

- Output: `earth_dataset_provenance.json`
- Records: source, provider, official URL, access method, state, attempt timestamp
- Machine-readable format for researcher traceability

### 4.3 Catalog Status

The `earth_nasadem_hgt_v001` dataset entry in the catalog remains with state PENDING, with limitations documenting the Earthdata authentication block. No catalog mutation is performed on the frozen DatasetSpec; the blocking condition is documented through the provenance system and Phase 18 reports.

## 5. Non-Negotiable Scientific Requirements

1. No fabricated datasets
2. No fabricated measurements
3. No fabricated validation results
4. No unsupported accuracy claims
5. No unreported resampling
6. No mixing incompatible vertical datums without explicit treatment
7. No misleading resolution comparisons
8. No weakening Phase 1–17 scientific limitations
9. No breaking existing Moon/Mars functionality
10. No unnecessary frontend redesign

## 6. Phase 18 Completion Criteria

Phase 18 is complete when:

- [x] Earth data source configuration documented in `acquire_earth_dem.py`
- [x] Raster validation logic implemented in `verify_earth_raster()`
- [x] Provenance recording system implemented in `write_earth_provenance_record()`
- [x] Resolution normalization architecture in `earth_normalization.py`
- [x] Terrain feature extraction integration in `earth_features.py`
- [x] Scientific validation tests in `science/tests/test_phase18_validation.py`
- [x] Earth data blocking documented (HTTP 401; no alternate DEM in repository)
- [x] Existing Moon/Mars functionality preserved (116/116 Python tests pass)
- [x] All required documentation produced (PHASE18_*.md files)

## 7. Phase 18 Exit Status

**Verdict: READY WITH LIMITATIONS**

Earth data integration is architecturally prepared but data acquisition is pending resolution of the NASA Earthdata authentication barrier. The pipeline is ready for when authentic Earth DEM data becomes available. The project progresses to Phases 19–22 with the Earth analog discovery framework fully documented and the ingestion infrastructure implemented.

---
*This document records the dataset acquisition status and pipeline architecture for Terra Twin Phase 18. No Earth data was acquired (authentication barrier), but the infrastructure for acquisition is fully implemented and documented.*