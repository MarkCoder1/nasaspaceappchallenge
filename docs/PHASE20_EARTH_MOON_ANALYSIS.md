# Terra Twin — Phase 20: Earth–Moon Comparison

## 1. Executive Summary

**STATUS: CONDITIONALLY READY**

Earth–Moon terrain morphology comparison completed using authentic USGS 3DEP 1-arc-second DEM data (resampled to 20 m) and validated Moon LOLA DEM (20 m native). The comparison focuses on the Death Valley / southern Arizona region (USGS tile n36w117) vs. the lunar south polar region.

**Key Result:** TMSI = 61.95 (95% CI: [53.23, 74.81]), Confidence: HIGH (qualitative)

**Classification: CONDITIONALLY READY** — Earth data limitations (effective resolution ~29.3 m, vertical datum NAVD88, US-only coverage) must be explicitly acknowledged.

## 2. Datasets

### 2.1 Target: Moon LOLA DEM

| Property | Value |
|----------|-------|
| File | `data/processed/moon_lola_80s_20m_elevation_m.tif` |
| CRS | Moon (2015) Polar Stereographic (IAU:30135) |
| Resolution | 20.0 m (native) |
| Vertical datum | LOLA project datum |
| Valid pixels | 4,194,304 (100%) |
| Elevation range | -2,872.11 m to 1,959.42 m |
| Mean elevation | -113.34 m |

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

Source data at ~29.3 m (1 arc-second) was downsampled to 20 m using bilinear interpolation to match the Moon/Mars native resolution.

**Critical limitation:** Resampling from 29.3 m to 20 m does NOT increase measurement resolution. The effective resolution remains approximately 29.3 m. All Earth–Moon comparisons must be interpreted with this resolution mismatch documented.

### 3.3 Vertical Datum

Earth data uses NAVD88; Moon data uses LOLA project datum. These are different reference surfaces and cannot be directly compared without explicit datum transformation. Elevation values are compared in their native datums with this limitation noted.

## 4. Results

### 4.1 Overall Similarity

| Metric | Value |
|--------|-------|
| Similarity index (TMSI) | 61.95 |
| Confidence | HIGH (qualitative) |
| Combined distance D | 0.4788 |
| 95% CI lower | 53.23 |
| 95% CI upper | 74.81 |

### 4.2 Feature-Level Comparisons

| Feature | Wasserstein | KS Statistic | Normalized Distance | Moon Mean | Earth Mean |
|---------|-------------|--------------|---------------------|-----------|------------|
| Slope | 6.14° | 0.41 | 0.48 | 4.999° | Not directly comparable* |
| Local relief | 5.89 m | 0.41 | 0.48 | 4.51 m | Not directly comparable* |
| Terrain ruggedness | 1.95 m | 0.41 | 0.48 | 1.56 m | Not directly comparable* |

*Earth feature means not shown due to vertical datum differences and resampling effects.

**Strongest matches:** local relief, slope  
**Largest differences:** terrain ruggedness, slope

### 4.3 Interpretation

Earth (Death Valley region) shows moderate-to-high similarity to the Moon (TMSI ≈ 62). The 95% CI [53.23, 74.81] is entirely above 50, suggesting the distributions are more similar than dissimilar. However:

1. **Resolution mismatch**: Earth effective resolution ~29.3 m vs. Moon 20 m native
2. **Vertical datum**: NAVD88 vs. LOLA datum
3. **Coverage**: Single USGS tile, limited geographic extent
4. **Environmental differences**: Earth has atmosphere, water, biology; Moon does not

## 5. Classification

**Earth–Moon comparison: CONDITIONALLY READY**

The comparison is statistically computable and uncertainty-quantified. However, results must be interpreted with the following explicit caveats:
- Earth effective resolution is ~29.3 m, not genuinely 20 m
- Vertical datum differences not quantitatively resolved
- Single geographic region limits generalizability
- TMSI does not establish geological equivalence

## 6. Limitations

All Phase 17 limitations preserved. Additional Earth-specific limitations:
- USGS 3DEP coverage limited to conterminous United States
- Resampled resolution does not create new information
- NAVD88 vertical datum differs from lunar reference surface
- Single test window (Death Valley region) may not be representative of global lunar analogs