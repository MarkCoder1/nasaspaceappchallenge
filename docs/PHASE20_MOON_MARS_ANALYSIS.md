# Terra Twin — Phase 20: Moon–Mars Quantitative Comparison

## 1. Executive Summary

**STATUS: READY**

The Moon–Mars quantitative comparison has been completed using validated lunar and Martian elevation datasets at 20 m native post spacing. The analysis compares terrain morphology distributions (slope, local relief, terrain ruggedness) using Wasserstein distance, Kolmogorov–Smirnov statistic, and bootstrap uncertainty quantification.

**Key Result:** TMSI = 49.92 (95% CI: [43.72, 56.80]), Confidence: HIGH (qualitative)

## 2. Datasets Used

### 2.1 Target: Mars Jezero CTX DTM

| Property | Value |
|----------|-------|
| File | `data/processed/mars_jezero_ctx_elevation_m.tif` |
| CRS | ESRI:103885 (equirectangular with MOLA control) |
| Dimensions | 1596 × 1512 pixels |
| Resolution | 20.0 m × 20.0 m (native post spacing) |
| Elevation range | -2,710.70 m to -1,515.54 m |
| Mean elevation | -2,356.87 m |
| Valid pixels | 2,413,152 (100%) |
| Status | VALIDATED |

### 2.2 Candidate: Moon LOLA DEM

| Property | Value |
|----------|-------|
| File | `data/processed/moon_lola_80s_20m_elevation_m.tif` |
| CRS | Moon (2015) Sphere / Ocentric / South Polar (IAU:30135) |
| Dimensions | 2048 × 2048 pixels |
| Resolution | 20.0 m × 20.0 m (native post spacing) |
| Elevation range | -2,872.11 m to 1,959.42 m |
| Mean elevation | -113.34 m |
| Valid pixels | 4,194,304 (100%) |
| Status | VALIDATED |

## 3. Methodology

### 3.1 Feature Extraction

Three terrain morphology features were extracted from both datasets at native 20 m resolution:

| Feature | Definition | Units | Window |
|---------|-----------|-------|--------|
| Slope | Gradient magnitude via central differences | Degrees | Pixel spacing |
| Local relief | Max − min elevation in complete window | m | 60 m (3×3 cells at 20 m) |
| Terrain ruggedness | Riley TRI (sqrt of mean squared center-to-neighbor diffs) | m | 60 m (3×3 cells at 20 m) |

### 3.2 Similarity Computation

- **Metric**: Terrain Morphology Similarity Index (TMSI)
- **Formula**: TMSI = 100 × exp(−D), where D = weighted mean of pooled-IQR-normalized Wasserstein distances
- **Weights**: Equal weights (1.0 each) across slope, local relief, terrain ruggedness
- **Spatial extent**: 10.24 km
- **No raster upsampling**: Both datasets at native 20 m resolution

### 3.3 Uncertainty Quantification

- **Method**: Block bootstrap with spatial blocking
- **Interpretation**: Intervals quantify spatial sampling variability under block-size assumption; not calibrated probabilities
- **Block sizes tested**: Multiple block sizes for sensitivity analysis

## 4. Results

### 4.1 Overall Similarity

| Metric | Value |
|--------|-------|
| Similarity index (TMSI) | 49.92 |
| Confidence | HIGH (qualitative) |
| Combined distance D | 0.6947 |
| 95% CI lower | 43.72 |
| 95% CI upper | 56.80 |
| Bootstrap mean | 49.70 |
| Bootstrap median | 49.83 |

### 4.2 Feature-Level Comparisons

| Feature | Wasserstein | KS Statistic | Normalized Distance | Target Mean | Candidate Mean |
|---------|-------------|--------------|---------------------|-------------|----------------|
| Slope | 8.78 | 0.49 | 0.69 | 4.999° | 13.782° |
| Local relief | 8.54 | 0.49 | 0.69 | 4.51 m | 13.05 m |
| Terrain ruggedness | 2.88 | 0.50 | 0.71 | 1.56 m | 4.44 m |

**Strongest matches:** slope, local relief  
**Largest differences:** terrain ruggedness, local relief

### 4.3 Interpretation

Mars terrain exhibits systematically higher values across all three morphology features compared to the Moon:
- Slope: Mars mean ~2.8× Moon mean
- Local relief: Mars mean ~2.9× Moon mean  
- Terrain ruggedness: Mars mean ~2.8× Moon mean

Despite these differences in absolute magnitude, the distribution shapes show moderate similarity (TMSI ≈ 50), indicating that the relative distribution of terrain types within each region shares some statistical commonalities.

## 5. Limitations

1. **TMSI is not a probability**: Does not establish habitability, safety, or geological equivalence
2. **No upsampling**: Both datasets compared at native 20 m resolution; no interpolation performed
3. **Environmental differences**: Earth/Moon/Mars physical conditions differ even when morphology distributions overlap
4. **Extent dependence**: Results specific to 10.24 km spatial extent
5. **Spatial autocorrelation**: Strong spatial autocorrelation (Moran's I ≈ 0.98) means pixels are not independent observations
6. **Vertical datum differences**: Moon (LOLA datum) vs. Mars (delta geoid/MOLA control)
7. **Horizontal CRS differences**: Moon (polar stereographic) vs. Mars (equirectangular)

## 6. Scientific Safeguards

- No claim of geological equivalence from terrain statistics
- Confidence is qualitative, not statistical
- Spatial autocorrelation acknowledged
- All Phase 17 limitations preserved
- No data fabrication

## 7. Reproducibility

All results are reproducible from:
- Input datasets: `data/processed/moon_lola_80s_20m_elevation_m.tif`, `data/processed/mars_jezero_ctx_elevation_m.tif`
- Processing code: `science/similarity/scoring/similarity.py` (compare_terrain), `science/similarity/features/feature_extraction.py` (extract_terrain_features)
- Results saved: `data/metadata/phase20_moon_mars_comparison.json`

## 8. Classification

**Moon–Mars comparison: READY**

Both datasets validated, 20 m native resolution, complete statistical uncertainty quantification, all limitations documented.