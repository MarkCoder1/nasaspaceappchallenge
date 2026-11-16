# Terra Twin — Phase 21: Geospatial and Dataset Validity Audit

## 1. Executive Summary

**VERDICT: VERIFIED WITH LIMITATIONS**

All datasets used in Terra Twin are authentic, properly documented, and appropriately processed. However, significant limitations exist: Earth data effective resolution (~29.3 m) differs from the 20 m processing grid, vertical datums differ across bodies (NAVD88 vs. LOLA vs. delta geoid), horizontal CRS differ (geographic vs. projected), and Earth coverage is limited to two USGS tiles in the southwestern United States.

## 2. Dataset Inventory and Validation

### 2.1 Moon LOLA DEM

| Property | Value |
|----------|-------|
| File | `data/processed/moon_lola_80s_20m_elevation_m.tif` |
| Source | NASA LOLA (Lunar Orbiter Laser Altimeter) |
| CRS | Moon (2015) Sphere / Ocentric / South Polar (IAU:30135) |
| Resolution | 20.0 m × 20.0 m (native post spacing) |
| Dimensions | 2048 × 2048 pixels |
| Vertical Datum | LOLA project datum |
| Elevation Units | Meters |
| Nodata | NaN |
| Valid Pixels | 4,194,304 (100%) |
| Elevation Range | −2,872.11 m to 1,959.42 m |
| Mean Elevation | −113.34 m |
| Status | VALIDATED |

**Assessment:** Validated observational product. Complete coverage of the south polar region subset. No data gaps.

### 2.2 Mars Jezero CTX DTM

| Property | Value |
|----------|-------|
| File | `data/processed/mars_jezero_ctx_elevation_m.tif` |
| Source | USGS / MRO CTX (Context Camera) |
| CRS | ESRI:103885 (equirectangular with MOLA control) |
| Resolution | 20.0 m × 20.0 m (native post spacing) |
| Dimensions | 1596 × 1512 pixels |
| Vertical Datum | Delta geoid (MOLA control) |
| Elevation Units | Meters |
| Nodata | NaN |
| Valid Pixels | 2,413,152 (100%) |
| Elevation Range | −2,710.70 m to −1,515.54 m |
| Mean Elevation | −2,356.87 m |
| Status | VALIDATED |

**Assessment:** Validated observational product. Complete coverage of Jezero crater region. No data gaps.

### 2.3 Earth USGS 3DEP n36w117

| Property | Value |
|----------|-------|
| Raw File | `data/raw/USGS_1_n36w117.tif` |
| Processed File | `data/processed/USGS_1_n36w117_20m_utm11n.tif` |
| Source | USGS 3DEP (3D Elevation Program) |
| Source URL | https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/n36w117/ |
| Source CRS | EPSG:4269 (NAD83 geographic) |
| Processed CRS | EPSG:26911 (UTM Zone 11N) |
| Native Resolution | ~29.3 m (1 arc-second) |
| Processed Resolution | 20.0 m (bilinear interpolation) |
| Vertical Datum | NAVD88 |
| Elevation Units | Meters |
| Nodata | −999999 |
| Raw Valid Pixels | 13,046,544 (100%) |
| Processed Valid Pixels | 25,315,828 (98.94%) |
| Raw Elevation Range | −73.02 m to 1,869.05 m |
| Processed Elevation Range | −72.87 m to 1,868.83 m |
| Mean Elevation | 671.59 m |
| Coverage | 34.9983°N–36.0017°N, 117.0017°W–115.9983°W |
| Region | Southern Arizona / Death Valley vicinity |
| Status | STRUCTURALLY VALIDATED |

### 2.4 Earth USGS 3DEP n37w117

| Property | Value |
|----------|-------|
| Raw File | `data/raw/USGS_1_n37w117.tif` |
| Processed File | `data/processed/USGS_1_n37w117_20m_utm11n.tif` |
| Source | USGS 3DEP (3D Elevation Program) |
| Source URL | https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/n37w117/ |
| Source CRS | EPSG:4269 (NAD83 geographic) |
| Processed CRS | EPSG:26911 (UTM Zone 11N) |
| Native Resolution | ~29.3 m (1 arc-second) |
| Processed Resolution | 20.0 m (bilinear interpolation) |
| Vertical Datum | NAVD88 |
| Elevation Units | Meters |
| Nodata | −999999 |
| Raw Valid Pixels | 13,046,544 (100%) |
| Processed Valid Pixels | 25,002,423 (98.95%) |
| Raw Elevation Range | −85.08 m to 2,176.92 m |
| Processed Elevation Range | −85.08 m to 2,176.39 m |
| Mean Elevation | 895.40 m |
| Coverage | 35.9983°N–37.0017°N, 117.0017°W–115.9983°W |
| Region | Central Valley, California |
| Status | STRUCTURALLY VALIDATED |

## 3. Coordinate Reference System Audit

### 3.1 Horizontal CRS Comparison

| Dataset | CRS | Type | Units | Transformation Required |
|---------|-----|------|-------|------------------------|
| Moon LOLA | IAU:30135 | Projected (polar stereographic) | Meters | No (native) |
| Mars Jezero | ESRI:103885 | Projected (equirectangular) | Meters | No (native) |
| Earth USGS 3DEP (raw) | EPSG:4269 | Geographic (degrees) | Degrees | Yes (to UTM 11N) |
| Earth USGS 3DEP (processed) | EPSG:26911 | Projected (UTM 11N) | Meters | No (after reprojection) |

**Assessment:** Horizontal CRS differences are properly handled. Earth data is reprojected from EPSG:4269 (geographic) to EPSG:26911 (UTM Zone 11N, projected metres) before feature extraction. All datasets are in projected CRS with metre units for feature computation.

### 3.2 Vertical Datum Comparison

| Dataset | Vertical Datum | Notes |
|---------|---------------|-------|
| Moon LOLA | LOLA project datum | Lunar reference surface |
| Mars Jezero | Delta geoid (MOLA control) | Martian reference surface |
| Earth USGS 3DEP | NAVD88 | North American Vertical Datum 1988 |

**Assessment:** Vertical datum differences are documented but NOT quantitatively resolved. Elevation values are compared in their native datums. This is a significant limitation for slope and relief calculations, which depend on absolute elevation values.

## 4. Resolution Audit

### 4.1 Native vs. Processing Resolution

| Dataset | Native Resolution | Processing Resolution | Resampling Method | Effective Resolution |
|---------|------------------|----------------------|-------------------|---------------------|
| Moon LOLA | 20 m | 20 m | None | 20 m |
| Mars Jezero | 20 m | 20 m | None | 20 m |
| Earth USGS 3DEP | ~29.3 m (1 arc-second) | 20 m | Bilinear interpolation | ~29.3 m |

**Critical Finding:** Earth data is resampled from ~29.3 m to 20 m. This does NOT create additional observational detail. The effective resolution remains ~29.3 m. All Earth–Moon and Earth–Mars comparisons must be interpreted with this resolution mismatch documented.

### 4.2 Resolution Sensitivity

No multi-resolution sensitivity analysis was performed. All comparisons use 20 m processing resolution. Results may change if Earth data were analyzed at its native 29.3 m resolution or at other resolutions.

## 5. Nodata Handling

| Dataset | Nodata Value | Valid Fraction |
|---------|-------------|----------------|
| Moon LOLA | NaN | 100% |
| Mars Jezero | NaN | 100% |
| Earth USGS n36w117 | −999999 | 98.94% |
| Earth USGS n37w117 | −999999 | 98.95% |

**Assessment:** Earth data has ~1% nodata, which is excluded from all calculations. This is correctly handled in feature extraction (invalid pixels masked).

## 6. Geographic Coverage Audit

### 6.1 Earth Coverage Limitations

Earth data covers only two USGS 1° tiles:
- **n36w117:** 34.9983°N–36.0017°N, 117.0017°W–115.9983°W (Southern Arizona / Death Valley vicinity)
- **n37w117:** 35.9983°N–37.0017°N, 117.0017°W–115.9983°W (Central Valley, California)

**Combined coverage:** Approximately 35°N–37°N, 116°W–117°W (Death Valley and southern Arizona desert region).

**Limitation:** This is NOT representative of global terrestrial terrain. Results apply only to the sampled desert regions.

### 6.2 Moon Coverage

Moon LOLA covers the south polar region (south polar window subset). Not global.

### 6.3 Mars Coverage

Mars Jezero covers the Jezero crater region. Not global.

**Assessment:** All datasets are regional, not global. Comparisons are specific to the regions compared.

## 7. Data Processing Pipeline

### 7.1 Earth DEM Processing Steps

1. **Download:** USGS 3DEP 1-arc-second DEM tiles from public S3 bucket (no authentication required)
2. **Reproject:** EPSG:4269 (NAD83 geographic) → EPSG:26911 (UTM Zone 11N)
3. **Resample:** ~29.3 m → 20 m using bilinear interpolation
4. **Extract features:** Slope, local relief, terrain ruggedness at 20 m grid
5. **Record metadata:** Processing parameters, resolution, CRS, provenance

### 7.2 Original Data Preservation

All original raw DEM files are preserved unmodified in `data/raw/`. Processed derivatives are stored separately in `data/processed/`. No original file has been modified.

**SHA-256 checksums:**
- USGS_1_n36w117.tif: 6dad0432701c28fc920befc47cd21c21d4914ff6c3a710d3ab5551ebf489cd40
- USGS_1_n37w117.tif: d6100180753d276b407ec585a872dc41d3515ea838c551ad22ec3aca4e6d8ad1

## 8. Data Suitability by Comparison

| Comparison | Earth Data Used | Coverage Limitation | Resolution Limitation | Vertical Datum Limitation | Overall Suitability |
|------------|----------------|---------------------|----------------------|--------------------------|---------------------|
| Moon–Mars | N/A (no Earth data) | N/A | None (both 20 m native) | None (both planetary) | Suitable |
| Earth–Moon | USGS n36w117 (Death Valley region) | Limited to Death Valley / southern Arizona | ~29.3 m effective vs. 20 m Moon | NAVD88 vs. LOLA datum | Conditionally suitable |
| Earth–Mars | USGS n36w117 (Death Valley region) | Limited to Death Valley / southern Arizona | ~29.3 m effective vs. 20 m Mars | NAVD88 vs. delta geoid | Conditionally suitable |

## 9. Classification

**Geospatial and Dataset Validity: VERIFIED WITH LIMITATIONS**

All datasets are authentic, properly documented, and appropriately processed. Original files are preserved. CRS transformations are correct. However:
- Earth effective resolution (~29.3 m) differs from processing grid (20 m)
- Vertical datums differ across bodies and are not quantitatively reconciled
- Earth coverage is limited to two tiles in the southwestern United States
- All datasets are regional, not global

## 10. Recommendations

1. **Prominently disclose Earth resolution limitation** in all Earth comparison outputs
2. **Document vertical datum differences** as unquantified limitations
3. **Emphasize single-region Earth coverage** limitation in all Earth comparison interpretations
4. **Consider acquiring additional Earth tiles** from other regions for broader coverage (future work)
5. **Consider vertical datum transformation** if authentic transformation methods become available