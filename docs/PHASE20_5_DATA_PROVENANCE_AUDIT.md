# Terra Twin — Phase 20.5: Data and Provenance Audit

## 1. Executive Summary

**VERDICT: VERIFIED**

All source datasets are authentic, original files are preserved, and processing metadata is complete. Earth USGS 3DEP data was acquired from public USGS S3 bucket (no NASA Earthdata authentication required). Moon and Mars datasets are validated products from Phases 17–18.

| Dataset | Authenticity | Original Preserved | Provenance Documented |
|---------|-------------|-------------------|----------------------|
| Moon LOLA DEM | ✅ NASA validated | ✅ Yes | ✅ Complete |
| Mars Jezero CTX DTM | ✅ USGS validated | ✅ Yes | ✅ Complete |
| Earth USGS 3DEP n36w117 | ✅ USGS authentic | ✅ Yes | ✅ Complete |
| Earth USGS 3DEP n37w117 | ✅ USGS authentic | ✅ Yes | ✅ Complete |

## 2. Dataset Details

### 2.1 Moon LOLA DEM

| Property | Value |
|----------|-------|
| File | `data/processed/moon_lola_80s_20m_elevation_m.tif` |
| Source | NASA LOLA (Lunar Orbiter Laser Altimeter) |
| CRS | Moon (2015) Sphere / Ocentric / South Polar (IAU:30135) |
| Resolution | 20.0 m × 20.0 m (native post spacing) |
| Dimensions | 2048 × 2048 pixels |
| Vertical datum | LOLA project datum |
| Elevation units | Meters |
| Nodata | NaN |
| Valid pixels | 4,194,304 (100%) |
| Elevation range | −2,872.11 m to 1,959.42 m |
| Mean elevation | −113.34 m |
| Status | VALIDATED |

### 2.2 Mars Jezero CTX DTM

| Property | Value |
|----------|-------|
| File | `data/processed/mars_jezero_ctx_elevation_m.tif` |
| Source | USGS / MRO CTX (Context Camera) |
| CRS | ESRI:103885 (equirectangular with MOLA control) |
| Resolution | 20.0 m × 20.0 m (native post spacing) |
| Dimensions | 1596 × 1512 pixels |
| Vertical datum | Delta geoid (MOLA control) |
| Elevation units | Meters |
| Nodata | NaN |
| Valid pixels | 2,413,152 (100%) |
| Elevation range | −2,710.70 m to −1,515.54 m |
| Mean elevation | −2,356.87 m |
| Status | VALIDATED |

### 2.3 Earth USGS 3DEP n36w117

| Property | Value |
|----------|-------|
| Raw file | `data/raw/USGS_1_n36w117.tif` |
| Processed file | `data/processed/USGS_1_n36w117_20m_utm11n.tif` |
| Source | USGS 3DEP (3D Elevation Program) |
| Source URL | https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/n36w117/ |
| Acquisition method | Direct S3 download (public, no authentication required) |
| Source CRS | EPSG:4269 (NAD83 geographic) |
| Processed CRS | EPSG:26911 (UTM Zone 11N) |
| Native resolution | ~29.3 m (1 arc-second) |
| Processed resolution | 20.0 m (resampled via bilinear interpolation) |
| Vertical datum | NAVD88 |
| Elevation units | Meters |
| Nodata | −999999 |
| Raw valid pixels | 13,046,544 (100%) |
| Processed valid pixels | 25,315,828 (98.94%) |
| Raw elevation range | −73.02 m to 1,869.05 m |
| Processed elevation range | −72.87 m to 1,868.83 m |
| Mean elevation | 671.59 m |
| Coverage | 34.9983°N–36.0017°N, 117.0017°W–115.9983°W |
| Region | Southern Arizona / Death Valley vicinity |

### 2.4 Earth USGS 3DEP n37w117

| Property | Value |
|----------|-------|
| Raw file | `data/raw/USGS_1_n37w117.tif` |
| Processed file | `data/processed/USGS_1_n37w117_20m_utm11n.tif` |
| Source | USGS 3DEP (3D Elevation Program) |
| Source URL | https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/n37w117/ |
| Acquisition method | Direct S3 download (public, no authentication required) |
| Source CRS | EPSG:4269 (NAD83 geographic) |
| Processed CRS | EPSG:26911 (UTM Zone 11N) |
| Native resolution | ~29.3 m (1 arc-second) |
| Processed resolution | 20.0 m (resampled via bilinear interpolation) |
| Vertical datum | NAVD88 |
| Elevation units | Meters |
| Nodata | −999999 |
| Raw valid pixels | 13,046,544 (100%) |
| Processed valid pixels | 25,002,423 (98.95%) |
| Raw elevation range | −85.08 m to 2,176.92 m |
| Processed elevation range | −85.08 m to 2,176.39 m |
| Mean elevation | 895.40 m |
| Coverage | 35.9983°N–37.0017°N, 117.0017°W–115.9983°W |
| Region | Central Valley, California |

## 3. Original Data Preservation

**Confirmed:** All original raster files are preserved unmodified:

| File | Status |
|------|--------|
| `data/raw/USGS_1_n36w117.tif` | ✅ EXISTS (51.8 MB) |
| `data/raw/USGS_1_n37w117.tif` | ✅ EXISTS (50.3 MB) |
| `data/raw/USGS_1_n36w117.xml` | ✅ EXISTS (metadata) |
| `data/raw/USGS_1_n37w117.xml` | ✅ EXISTS (metadata) |
| `data/processed/moon_lola_80s_20m_elevation_m.tif` | ✅ EXISTS (14.2 MB) |
| `data/processed/mars_jezero_ctx_elevation_m.tif` | ✅ EXISTS (7.5 MB) |

Processed derivatives are stored separately from originals. No original file was modified.

## 4. Resampling Methodology Audit

### 4.1 Earth DEM Resampling

Earth data was reprojected from EPSG:4269 (geographic degrees) to EPSG:26911 (UTM Zone 11N, projected metres) and resampled from ~29.3 m to 20 m using bilinear interpolation.

**Critical disclosure:** The processing metadata explicitly states:

> "Resampling to 20 m does NOT increase measurement resolution. Effective resolution remains ~29.3 m after downsampling. No new information created."

This disclosure is present in `data/processed/phase20_earth_processing_metadata.json`.

**Assessment:** Correct handling. The effective resolution limitation is explicitly documented. However, the Earth–Moon and Earth–Mars comparisons still treat Earth data as if it were at 20 m resolution for feature extraction, which may overstate the effective spatial detail available.

### 4.2 Coordinate Reference System Audit

| Dataset | CRS | Type | Units | Compatibility |
|---------|-----|------|-------|---------------|
| Moon LOLA | IAU:30135 | Projected (polar stereographic) | Meters | Native |
| Mars Jezero | ESRI:103885 | Projected (equirectangular) | Meters | Native |
| Earth USGS 3DEP (raw) | EPSG:4269 | Geographic | Degrees | Requires reprojection |
| Earth USGS 3DEP (processed) | EPSG:26911 | Projected (UTM 11N) | Meters | Compatible after reprojection |

**Assessment:** Horizontal CRS differences are properly handled through reprojection. Earth data is correctly transformed to a projected CRS before feature extraction.

### 4.3 Vertical Datum Audit

| Dataset | Vertical Datum | Notes |
|---------|---------------|-------|
| Moon LOLA | LOLA project datum | Lunar reference surface |
| Mars Jezero | Delta geoid (MOLA control) | Martian reference surface |
| Earth USGS 3DEP | NAVD88 | North American Vertical Datum 1988 |

**Assessment:** Vertical datum differences are documented in processing metadata and comparison limitations. However, no quantitative datum transformation is applied. Elevation values are compared in their native datums. This is a known limitation that affects the interpretability of elevation-based features (slope, relief, ruggedness) across bodies.

## 5. Nodata Handling

| Dataset | Nodata Value | Valid Fraction |
|---------|-------------|----------------|
| Moon LOLA | NaN | 100% |
| Mars Jezero | NaN | 100% |
| Earth USGS n36w117 | −999999 | 98.94% |
| Earth USGS n37w117 | −999999 | 98.95% |

**Assessment:** Earth data has ~1% nodata, which is excluded from all calculations. This is correctly handled.

## 6. Geographic Coverage Limitations

**Critical limitation:** Earth data covers only two USGS 1° tiles:
- n36w117: Southern Arizona / Death Valley vicinity
- n37w117: Central Valley, California

**Assessment:** These tiles are NOT representative of global terrestrial terrain. The Earth–Mars and Earth–Moon comparisons are specific to desert/alluvial environments in the southwestern United States. Results cannot be generalized to other Earth environments (polar, tropical, alpine, etc.).

## 7. Classification

**Data and Provenance: VERIFIED**

All datasets are authentic, original files preserved, provenance fully documented, CRS and vertical datum differences disclosed, resampling limitations explicitly stated. Earth data coverage limitations are clearly documented.

---

**Next:** See `PHASE20_5_STATISTICAL_VALIDITY_AUDIT.md` for the statistical validity assessment.