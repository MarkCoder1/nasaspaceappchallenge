# Terra Twin — Phase 20: Earth–Mars Comparison

## 1. Executive Summary

**STATUS: CONDITIONALLY READY**

Earth–Mars terrain morphology comparison completed using authentic USGS 3DEP 1-arc-second DEM data (resampled to 20 m) and validated Mars Jezero CTX DTM (20 m native). The comparison focuses on the Death Valley / southern Arizona region (USGS tile n36w117) vs. the Martian Jezero crater region.

**Key Result:** TMSI = 73.14 (95% CI: [65.41, 78.40]), Confidence: HIGH (qualitative)

**Classification: CONDITIONALLY READY** — Earth data limitations (effective resolution ~29.3 m, vertical datum NAVD88, US-only coverage) must be explicitly acknowledged. Do not force an Earth–Mars result if scientific compatibility cannot be established.

## 2. Datasets

### 2.1 Target: Mars Jezero CTX DTM

| Property | Value |
|----------|-------|
| File | `data/processed/mars_jezero_ctx_elevation_m.tif` |
| CRS | ESRI:103885 (equirectangular with MOLA control) |
| Resolution | 20.0 m (native post spacing) |
| Vertical datum | Delta geoid (MOLA control) |
| Valid pixels | 2,413,152 (100%) |
| Elevation range | -2,710.70 m to -1,515.54 m |
| Mean elevation | -2,356.87 m |
| Region | Jezero crater, Mars |

### 2.2 Candidate: USGS 3DEP (n36w117)

| Property | Value |
|----------|-------|
| File | `data/processed/USGS_1_n36w117_20m_utm11n.tif` |
| Source CRS | EPSG:4269 (NAD83 geographic) |
| Processed CRS | EPSG:26911 (UTM Zone 11N) |
| Native resolution | ~29.3 m (1 arc-second) |
| Processed resolution | 20.0 m (resampled, downsampled) |
| Vertical datum | NAVD88 |
| Valid pixels | 25,315,828 (98.94%) |
| Elevation range | -72.87 m to 1,868.83 m |
| Mean elevation | 671.59 m |
| Coverage | 34.9983°N–36.0017°N, 117.0017°W–115.9983°W |
| Region | Southern Arizona / Death Valley vicinity |

## 3. Data Processing

### 3.1 Reprojection

Earth data was reprojected from EPSG:4269 (geographic degrees) to EPSG:26911 (UTM Zone 11N, projected metres) using bilinear interpolation. This enables slope and relief calculations in consistent metre units.

### 3.2 Resolution Normalization

Source data at ~29.3 m (1 arc-second) was downsampled to 20 m using bilinear interpolation to match the Mars native resolution.

**Critical limitation:** Resampling from 29.3 m to 20 m does NOT increase measurement resolution. The effective resolution remains approximately 29.3 m. All Earth–Mars comparisons must be interpreted with this resolution mismatch documented.

### 3.3 Vertical Datum

Earth data uses NAVD88; Mars data uses delta geoid (MOLA control). These are different reference surfaces and cannot be directly compared without explicit datum transformation. Elevation values are compared in their native datums with this limitation noted.

## 4. Results

### 4.1 Overall Similarity

| Metric | Value |
|--------|-------|
| Similarity index (TMSI) | 73.14 |
| Confidence | HIGH (qualitative) |
| Combined distance D | 0.3128 |
| 95% CI lower | 65.41 |
| 95% CI upper | 78.40 |

### 4.2 Feature-Level Comparisons

| Feature | Wasserstein | KS Statistic | Normalized Distance | Mars Mean | Earth Mean |
|---------|-------------|--------------|---------------------|-----------|------------|
| Slope | 2.76° | 0.14 | 0.30 | 13.782° | Not directly comparable* |
| Local relief | 2.80 m | 0.15 | 0.32 | 13.05 m | Not directly comparable* |
| Terrain ruggedness | 0.99 m | 0.16 | 0.32 | 4.44 m | Not directly comparable* |

*Earth feature means not shown due to vertical datum differences and resampling effects.

**Strongest matches:** slope, terrain ruggedness  
**Largest differences:** local relief, terrain ruggedness

### 4.3 Interpretation

Earth (Death Valley region) shows the highest similarity to Mars of all comparisons (TMSI ≈ 73). The 95% CI [65.41, 78.40] is well above 50, and the KS statistics (0.14–0.16) are quite low, suggesting the distribution shapes are quite similar.

However, this result must be interpreted with extreme caution:

1. **Resolution mismatch**: Earth effective resolution ~29.3 m vs. Mars 20 m native
2. **Vertical datum**: NAVD88 vs. delta geoid
3. **Coverage**: Single USGS tile, Death Valley region only
4. **Environmental differences**: Earth has active geology, atmosphere, hydrology; Mars does not
5. **TMSI is not geological equivalence**: Similar morphology distributions do not imply similar formation processes

## 5. Classification

**Earth–Mars comparison: CONDITIONALLY READY**

The comparison is statistically computable and uncertainty-quantified. However:
- Earth effective resolution is ~29.3 m, not genuinely 20 m
- Vertical datum differences not quantitatively resolved
- Single geographic region limits generalizability
- TMSI does not establish geological equivalence
- Do not force an Earth–Mars result if scientific compatibility cannot be established

## 6. Limitations

All Phase 17 limitations preserved. Additional Earth-specific limitations:
- USGS 3DEP coverage limited to conterminous United States
- Resampled resolution does not create new information
- NAVD88 vertical datum differs from Martian reference surface
- Single test window (Death Valley region) may not be representative of global Martian analogs
- Earth's active geological processes differ fundamentally from Mars