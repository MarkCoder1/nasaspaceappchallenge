# Terra Twin — Phase 19.5: Acquisition Report

## 1. Executive Summary

**STATUS: PARTIALLY RESOLVED**

Authentic USGS 3DEP Earth DEM data successfully acquired and validated. NASADEM HGT remains blocked by authentication requirements.

### Acquisition Results

| Source | Status | Files | Size | Validation |
|--------|--------|-------|------|------------|
| **USGS 3DEP n36w117** | ✅ **ACQUIRED** | USGS_1_n36w117.tif | 51.8 MB | Structurally validated |
| **USGS 3DEP n37w117** | ✅ **ACQUIRED** | USGS_1_n37w117.tif | 50.3 MB | Structurally validated |
| **NASADEM HGT** | ❌ **BLOCKED** | N/A | N/A | HTTP 401 without credentials |

## 2. Acquired Data Details

### 2.1 USGS_1_n36w117.tif

- **File size**: 51,840,518 bytes (51.8 MB)
- **Dimensions**: 3612 × 3612 pixels (13,046,544 valid pixels)
- **Resolution**: 0.000277777777787014° longitude × 0.000277777777786999° latitude (~29.3 m/pixel)
- **Elevation range**: -73.02 m to 1869.05 m
- **Mean elevation**: 671.51 m
- **CRS**: EPSG:4269 (North American Datum of 1983)
- **Vertical datum**: North American Vertical Datum of 1988 (NAVD88)
- **Nodata value**: -999999
- **Valid pixel fraction**: 100%
- **SHA-256**: 6dad0432701c28fc920befc47cd21c21d4914ff6c3a710d3ab5551ebf489cd40
- **Source**: https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/n36w117/USGS_1_n36w117.tif

### 2.2 USGS_1_n37w117.tif

- **File size**: 50,321,599 bytes (50.3 MB)
- **Dimensions**: 3612 × 3612 pixels (13,046,544 valid pixels)
- **Resolution**: Same as n36w117 (~29.3 m/pixel)
- **Elevation range**: -85.08 m to 2176.92 m
- **Mean elevation**: 896.08 m
- **CRS**: EPSG:4269 (NAD83)
- **Vertical datum**: NAVD88
- **Nodata value**: -999999
- **Valid pixel fraction**: 100%
- **SHA-256**: d6100180753d276b407ec585a872dc41d3515ea838c551ad22ec3aca4e6d8ad1
- **Source**: https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/n37w117/USGS_1_n37w117.tif

### 2.3 Geographic Coverage

| Tile | West | East | South | North | Coverage Region |
|------|------|------|-------|-------|-----------------|
| USGS_1_n36w117 | -117.0017 | -115.9983 | 34.9983 | 36.0017 | Southern Arizona |
| USGS_1_n37w117 | -117.0017 | -115.9983 | 35.9983 | 37.0017 | Central Valley, California |

## 3. NASADEM HGT Blocking Condition

### 3.1 Error Details

- **Endpoint**: https://cmr.earthdata.nasa.gov/search/granules.json?collection_concept_id=C2763264762-LPCLOUD
- **HTTP Status**: 401 (Unauthorized)
- **Cause**: Missing NASA Earthdata Login credentials
- **Blocking record**: earthdata_authentication_diagnostic.json documents the condition

### 3.2 User Action Required

1. Register for NASA Earthdata Login at https://urs.earthdata.nasa.gov/
2. Configure credentials in environment variables
3. Run acquisition: python3 -m science.data_ingestion.acquire_earth_dem nasadem_hgt
4. Update candidate registry: update_candidate_status(candidate_id, "DATA_AVAILABLE")

## 4. Alternative Sources Investigated

### 4.1 Copernicus GLO-30 DEM
- **Status**: AVAILABLE_ALTERNATIVE (registration required)
- **Resolution**: 30 m
- **Limitations**: Vertical datum differs; normalization required

### 4.2 SRTM GL3
- **Status**: MAY_CIRCUMVENT_BLOCK (DNS resolution issues)
- **Resolution**: 30 m
- **Limitations**: Polar gaps; may still require Earthdata auth

## 5. Classification

**OUTCOME: PARTIALLY RESOLVED**

- ✅ Authentic USGS 3DEP data acquired and validated
- ✅ Structural validation passed
- ✅ No synthetic or fabricated data
- ❌ NASADEM HGT blocked by authentication

**Next Step**: Obtain NASA Earthdata Login credentials to complete full Earth DEM integration.