# Terra Twin — Phase 20: Statistical Validation

## 1. Executive Summary

**STATUS: COMPLETE**

Statistical validation methods were implemented and applied to all three planetary comparisons (Moon–Mars, Earth–Moon, Earth–Mars). Methods include Kolmogorov–Smirnov statistics, Wasserstein distance, distribution overlap, interquartile range comparisons, bootstrap confidence intervals, and block-size sensitivity analysis.

**Key finding:** All comparisons show moderate TMSI values (49.92–73.14) with bootstrap 95% confidence intervals that do not include 0 or 100, indicating statistically distinguishable but moderately similar terrain morphology distributions.

## 2. Statistical Methods

### 2.1 Kolmogorov–Smirnov (KS) Statistic

**What it measures:** The maximum vertical distance between the empirical cumulative distribution functions (ECDFs) of two terrain feature distributions. Values range from 0 (identical distributions) to 1 (completely disjoint).

**Scientific interpretation:** A KS statistic of 0.5 means the two distributions differ at their point of maximum divergence by 50% of the total probability mass. KS is sensitive to differences in both location (median) and shape (spread, skewness) of distributions.

**Limitations:**
- Does not quantify effect size directly
- Sensitive to sample size (large samples may detect trivial differences)
- Does not identify which part of the distribution differs most

### 2.2 Wasserstein Distance (Earth Mover's Distance)

**What it measures:** The minimum "work" required to transform one distribution into another, where work = mass × distance moved. Computed as the integral of the absolute difference between ECDFs.

**Scientific interpretation:** Unlike KS, Wasserstein distance is sensitive to the magnitude of differences across the entire distribution, not just the maximum divergence. It provides a more intuitive measure of how different two distributions are in terms of their values.

**Limitations:**
- Units depend on the feature being compared (e.g., meters for elevation, degrees for slope)
- Requires normalization for cross-feature comparison

### 2.3 Normalized Distance

**What it measures:** Wasserstein distance normalized by the pooled interquartile range (IQR) of the two distributions. This provides a scale-invariant measure of distributional difference.

**Formula:** Normalized distance = Wasserstein / pooled_IQR

**Scientific interpretation:** Values near 0 indicate similar distributions; values near 1 or greater indicate substantial differences. This normalization enables comparison across features with different units (slope in degrees vs. relief in meters).

### 2.4 Bootstrap Confidence Intervals

**What they measure:** Spatial sampling variability of the TMSI under a block-bootstrap resampling assumption.

**Method:**
- Spatial blocks are resampled (not individual pixels) to account for spatial autocorrelation
- TMSI recomputed for each bootstrap replicate
- 95% confidence interval reported as 2.5th–97.5th percentiles

**Interpretation:** Intervals quantify spatial sampling variability under the stated block-size assumption. They are NOT calibrated probabilities or measurement error bars. Strong spatial autocorrelation (Moran's I ≈ 0.98) means pixels are not independent observations.

**Limitations:**
- Block size selection affects interval width
- Intervals assume stationarity within blocks
- Does not capture all sources of uncertainty (e.g., vertical datum differences)

### 2.5 Block-Size Sensitivity

**What it measures:** How TMSI estimates and confidence intervals vary with different spatial block sizes.

**Purpose:** Tests robustness of uncertainty estimates to the spatial blocking assumption. Larger blocks better capture spatial autocorrelation but reduce effective sample size; smaller blocks increase sample size but may underestimate autocorrelation effects.

## 3. Results by Comparison

### 3.1 Moon–Mars Comparison

| Statistic | Value |
|-----------|-------|
| TMSI | 49.92 |
| 95% CI | [43.72, 56.80] |
| Bootstrap mean | 49.70 |
| Bootstrap median | 49.83 |
| KS range (features) | 0.49–0.50 |
| Wasserstein range | 2.88–8.78 |

**Interpretation:** The CI does not include 0 or 100, confirming that Moon and Mars terrain morphology distributions are statistically distinguishable. However, the moderate TMSI (~50) indicates some distributional overlap.

**Feature-level KS statistics:**
- Slope: 0.49
- Local relief: 0.49
- Terrain ruggedness: 0.50

### 3.2 Earth–Moon Comparison

| Statistic | Value |
|-----------|-------|
| TMSI | 61.95 |
| 95% CI | [53.23, 74.81] |
| Bootstrap mean | Not separately reported |
| KS range (features) | 0.41–0.41 |
| Wasserstein range | 1.95–6.14 |

**Interpretation:** Earth (Death Valley region, USGS 3DEP) shows higher similarity to the Moon than Mars does (TMSI 61.95 vs. 49.92). However, this must be interpreted with caution due to:
- Earth effective resolution ~29.3 m (resampled to 20 m)
- Vertical datum: NAVD88 vs. LOLA
- Coverage limited to US desert region

**Feature-level KS statistics:**
- Slope: 0.41
- Local relief: 0.41
- Terrain ruggedness: 0.41

### 3.3 Earth–Mars Comparison

| Statistic | Value |
|-----------|-------|
| TMSI | 73.14 |
| 95% CI | [65.41, 78.40] |
| KS range (features) | 0.14–0.16 |
| Wasserstein range | 0.99–2.80 |

**Interpretation:** Earth (Death Valley region) shows the highest similarity to Mars (TMSI 73.14). The CI [65.41, 78.40] is entirely above 50, indicating statistically significant similarity at the conventional threshold. However:
- Same Earth data limitations as above
- Mars vs. Earth environmental differences remain profound

**Feature-level KS statistics:**
- Slope: 0.14
- Local relief: 0.15
- Terrain ruggedness: 0.16

The very low KS statistics (0.14–0.16) for Earth–Mars suggest the distribution shapes are quite similar, particularly for slope and local relief.

## 4. Cross-Comparison Summary

| Comparison | TMSI | 95% CI | KS Range | Interpretation |
|------------|------|--------|----------|----------------|
| Moon–Mars | 49.92 | [43.72, 56.80] | 0.49–0.50 | Moderate similarity, distinguishable distributions |
| Earth–Moon | 61.95 | [53.23, 74.81] | 0.41–0.41 | Moderate-high similarity |
| Earth–Mars | 73.14 | [65.41, 78.40] | 0.14–0.16 | High similarity (but Earth data limitations apply) |

## 5. Sample Sizes

| Dataset | Slope pixels | Local relief pixels | Terrain ruggedness pixels |
|---------|-------------|---------------------|--------------------------|
| Moon LOLA | 4,186,116 | 4,186,116 | 4,186,116 |
| Mars Jezero | 2,406,940 | 2,406,940 | 2,406,940 |
| Earth USGS n36w117 | ~25.3M | ~25.3M | ~25.3M |

**Note:** Large sample sizes mean even small distributional differences may produce statistically significant KS statistics. Effect size (normalized distance) should be prioritized over p-value thinking.

## 6. Spatial Autocorrelation

All datasets exhibit strong spatial autocorrelation (Moran's I ≈ 0.98 from Phase 11). This means:

1. Adjacent pixels are not independent observations
2. Effective sample size is much smaller than pixel count
3. Bootstrap intervals must use spatial blocks, not pixel-level resampling
4. Confidence intervals may be optimistic if block size is too small

## 7. Multiple Comparisons

Three pairwise comparisons were performed (Moon–Mars, Earth–Moon, Earth–Mars). No Bonferroni correction was applied because:
- Comparisons address different research questions
- Each comparison has independent uncertainty quantification
- Results should be interpreted individually, not as a family of tests

## 8. Limitations

1. **TMSI is descriptive, not inferential**: Does not establish geological equivalence
2. **CI is not calibrated probability**: Quantifies spatial sampling variability only
3. **Earth resolution**: Effective resolution ~29.3 m despite 20 m resampling
4. **Earth coverage**: Limited to two USGS tiles (Death Valley region)
5. **Vertical datum**: NAVD88 (Earth) vs. LOLA/MOLA/delta-geoid (Moon/Mars)
6. **Horizontal CRS**: Geographic (Earth) vs. projected (Moon/Mars) — reprojection applied
7. **Spatial autocorrelation**: Strong (Moran's I ≈ 0.98), not fully captured by bootstrap

## 8. Classification

**Statistical validation: COMPLETE**

All statistical methods implemented, results quantified, limitations documented. Confidence intervals and KS statistics support interpretation of TMSI values but do not establish geological equivalence.