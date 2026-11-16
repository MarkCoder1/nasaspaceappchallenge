# Terra Twin — Phase 21: Statistical Robustness Audit

## 1. Executive Summary

**VERDICT: VERIFIED WITH LIMITATIONS**

The statistical methods used in Terra Twin (Wasserstein distance, KS statistic, pooled IQR normalization, spatial block bootstrap confidence intervals) are correctly implemented. All reported values are reproducible. However, several statistical limitations exist: bootstrap repetition count (1,000) is moderate, no seed sensitivity analysis was performed in Phase 20 (added in 20.6), spatial autocorrelation is strong (Moran's I ≈ 0.979), no multiple-comparison correction, and max(IQR) rather than true pooled IQR scaling.

## 2. Statistical Methods Audit

### 2.1 Wasserstein Distance (1-Wasserstein / Earth Mover's Distance)

**Implementation:** `scipy.stats.wasserstein_distance`

**Mathematical Definition:**
```
W(T,C) = ∫₀¹ |F_T⁻¹(u) − F_C⁻¹(u)| du
```

**Strengths:**
- Sensitive to differences across the entire distribution, not just central tendency
- Has a clear physical interpretation (minimum "work" to transform one distribution into another)
- Handles continuous distributions well

**Limitations:**
- Units depend on the feature (degrees for slope, metres for relief/ruggedness)
- Sensitive to outliers in the tails
- Requires normalization for cross-feature comparison

**Assessment:** Appropriate choice for comparing terrain feature distributions.

### 2.2 Kolmogorov–Smirnov Statistic

**Implementation:** `scipy.stats.ks_2samp(method="auto")`

**Mathematical Definition:**
```
KS(T,C) = supₓ |F_T(x) − F_C(x)|
```

**Strengths:**
- Non-parametric, no distributional assumptions
- Sensitive to differences in location, spread, and shape
- Well-understood with known null distribution

**Limitations:**
- Sensitive to sample size (large samples detect trivial differences)
- Does not quantify effect size directly
- Most sensitive to differences near the median, less sensitive to tails

**Assessment:** Appropriate complementary metric to Wasserstein distance.

### 2.3 Pooled IQR Normalization

**Implementation:**
```
pooled_IQR = max(IQR_T, IQR_C)
normalized_distance = W / max(IQR_T, IQR_C, ε)
```

**Assessment:** 
- **Weakness:** Uses `max(IQR)` rather than a true pooled IQR. This is a conservative scaling choice but not a standard statistical practice.
- **Impact:** When one distribution is much wider than the other, using the larger IQR as denominator produces smaller normalized distances, potentially overstating similarity.
- **Recommendation:** Consider using a true pooled IQR or document the conservative choice explicitly.

### 2.4 Bootstrap Confidence Intervals

**Implementation:** Spatial block bootstrap with replacement

**Parameters:**
- Block size: 320 m (16 cells at 20 m resolution)
- Repetitions: 1,000 (increased from 64 in Phase 20.6)
- Sampling: up to 32 blocks per repetition, capped at 4,096 values
- Confidence interval: percentile method (2.5th–97.5th percentiles)
- Seed: 42 (fixed)

**Strengths:**
- Accounts for spatial autocorrelation by resampling blocks rather than pixels
- Non-parametric, no distributional assumptions
- Percentile method is straightforward and interpretable

**Limitations:**
- **64 → 1,000 repetitions:** 1,000 is adequate but still moderate for stable CI estimation
- **No seed sensitivity analysis in Phase 20:** Added in Phase 20.6 (5 seeds tested, stable results)
- **Block size of 320 m:** May not fully capture spatial autocorrelation range
- **Max 32 blocks per repetition:** Limits effective bootstrap sample size
- **Percentile bootstrap:** Assumes approximate symmetry; TMSI is bounded (0–100) and may be skewed

**Assessment:** Appropriate methodology with documented limitations.

## 3. Additional Statistical Audits

### 3.1 Spatial Autocorrelation

**Documented:** Moran's I ≈ 0.979 (strong spatial autocorrelation) from Phase 11

**Impact:**
- Pixels are not independent observations
- Effective sample size is much smaller than pixel count
- Standard statistical tests assuming independence would be invalid
- Block bootstrap is the correct approach for spatially correlated data

**Residual Concern:** The block size of 320 m may not fully decorrelate adjacent blocks given Moran's I = 0.979. CI intervals may be slightly too narrow.

### 3.2 Sample Size Analysis

| Dataset | Raw Pixels | Sampled per Feature (per bootstrap rep) |
|---------|-----------|----------------------------------------|
| Moon LOLA | 4,194,304 | 100,000 |
| Mars Jezero | 2,413,152 | 100,000 |
| Earth USGS n36w117 | 25,315,828 | 4,096 (bootstrap sample cap) |

**Assessment:**
- Large raw sample sizes are adequate
- Subsampling to 100,000 for distribution comparison is reasonable
- Bootstrap sample cap of 4,096 per repetition may limit precision for Earth data (which has 25M+ valid pixels)

### 3.3 Multiple Comparisons

**Three pairwise comparisons performed:** Moon–Mars, Earth–Moon, Earth–Mars

**Assessment:** No Bonferroni correction or other family-wise error rate control applied. Acceptable for exploratory analysis where each comparison addresses a distinct research question, but results should not be interpreted as a family of tests.

### 3.4 Weight Sensitivity

**Current:** Equal weights (1.0 each) for slope, local relief, terrain ruggedness

**Assessment:** No weight sensitivity analysis performed. Different weight choices could change TMSI values and potentially the ranking of comparisons.

### 3.5 Resolution Sensitivity

**Current:** All comparisons at 20 m processing resolution

**Assessment:** Earth data at ~29.3 m native resolution resampled to 20 m. No multi-resolution sensitivity analysis performed. Results may be resolution-dependent.

### 3.6 Seed Sensitivity (Phase 20.6)

**Results from 5 seeds (42, 123, 456, 789, 1011):**

| Comparison | Mean TMSI | Min TMSI | Max TMSI | Max Abs Diff |
|------------|-----------|----------|----------|-------------|
| Moon–Mars | 49.68 | 49.54 | 49.97 | 0.43 |
| Earth–Moon | 62.33 | 62.22 | 62.53 | 0.31 |
| Earth–Mars | 71.49 | 71.26 | 71.63 | 0.38 |

**Assessment:** TMSI estimates are stable across seeds (max difference < 0.44). Results are not sensitive to seed choice.

## 4. Statistical Weaknesses Summary

| Weakness | Severity | Impact | Mitigation |
|----------|----------|--------|------------|
| max(IQR) scaling instead of true pooled IQR | Moderate | May overstate similarity when distributions have different spreads | Documented as methodological choice |
| 1,000 bootstrap repetitions | Low-Moderate | CI bounds may have Monte Carlo error | Increased from 64; 1,000 is adequate for most purposes |
| No weight sensitivity analysis | Moderate | Different weights could change rankings | Not performed; arbitrary equal weights |
| Strong spatial autocorrelation (Moran's I ≈ 0.979) | Moderate | CI may be slightly too narrow | Block bootstrap addresses this partially |
| No multiple-comparison correction | Low | Results should not be interpreted as family of tests | Documented as exploratory analysis |
| Systematic (not random) subsampling | Low | May miss localized patterns | Adequate for large, continuous rasters |

## 5. Classification

**Statistical Robustness: VERIFIED WITH LIMITATIONS**

All statistical methods are correctly implemented and results are reproducible. The bootstrap methodology properly accounts for spatial autocorrelation. However, the max(IQR) scaling, equal feature weights, and moderate bootstrap repetition count are methodological choices that should be documented and considered when interpreting results.

## 6. Recommendations

1. **Increase bootstrap repetitions:** 1,000 is adequate; 2,000+ would provide more stable CI bounds
2. **Perform weight sensitivity analysis:** Test how different weight schemes affect TMSI rankings
3. **Consider alternative pooling:** Evaluate true pooled IQR vs. max(IQR) scaling
4. **Report effect sizes:** Along with TMSI, report Wasserstein distances and KS statistics as effect sizes
5. **Document subsampling method:** Explicitly state that systematic (not random) subsampling is used