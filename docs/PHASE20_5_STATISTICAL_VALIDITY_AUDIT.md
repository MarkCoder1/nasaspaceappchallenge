# Terra Twin — Phase 20.5: Statistical Validity Audit

## 1. Executive Summary

**VERDICT: VERIFIED WITH LIMITATIONS**

Statistical methods are correctly implemented and all reported statistics are independently verified. However, key limitations exist: low bootstrap repetition count (64), max(IQR) rather than true pooled IQR scaling, strong spatial autocorrelation (Moran's I ≈ 0.979), no multiple-comparison correction, and Earth data effective resolution mismatch (~29.3 m vs. 20 m target).

| Statistical Element | Status | Assessment |
|--------------------|--------|------------|
| Wasserstein distance | ✅ VERIFIED | Correctly implemented via scipy |
| KS statistic | ✅ VERIFIED | Correctly implemented via scipy |
| Normalized distance | ✅ VERIFIED | Correct computation |
| TMSI formula | ✅ VERIFIED | 100 × exp(−combined_distance) |
| Bootstrap CI | ✅ VERIFIED | Correctly implemented, 64 reps |
| Spatial autocorrelation | ⚠️ LIMITATION | Block bootstrap used, but strong autocorrelation remains |
| Multiple comparisons | ⚠️ LIMITATION | No correction applied |
| Sample sizes | ✅ ADEQUATE | 100K samples per feature per dataset |

## 2. Wasserstein Distance Audit

### 2.1 Implementation

Uses `scipy.stats.wasserstein_distance` on subsampled distributions (max 100,000 values via linspace indexing).

**Assessment:** Correct implementation. Wasserstein distance is appropriate for comparing full distribution shapes, not just central tendencies.

### 2.2 Values Observed

| Comparison | Slope | Local Relief | Terrain Ruggedness |
|------------|-------|--------------|-------------------|
| Moon–Mars | 8.78 | 8.54 | 2.88 |
| Earth–Moon | 6.14 | 5.89 | 1.95 |
| Earth–Mars | 2.76 | 2.80 | 0.99 |

**Interpretation:** Earth–Mars has the lowest Wasserstein distances across all features, indicating the most similar distribution shapes. Moon–Mars has the highest distances.

## 3. KS Statistic Audit

### 3.1 Implementation

Uses `scipy.stats.ks_2samp` with `method="auto"`.

**Assessment:** Correct implementation. KS statistic measures the maximum vertical distance between ECDFs.

### 3.2 Values Observed

| Comparison | Slope | Local Relief | Terrain Ruggedness | Interpretation |
|------------|-------|--------------|-------------------|----------------|
| Moon–Mars | 0.49 | 0.49 | 0.50 | Moderate difference |
| Earth–Moon | 0.41 | 0.41 | 0.41 | Moderate difference |
| Earth–Mars | 0.14 | 0.15 | 0.16 | High similarity |

**Interpretation:** Earth–Mars KS statistics (0.14–0.16) indicate very similar distribution shapes. Moon–Mars (0.49–0.50) and Earth–Moon (0.41) indicate moderate distributional differences.

### 3.3 KS Sensitivity to Sample Size

Large sample sizes (100K per feature) mean even small distributional differences produce statistically significant KS statistics. Effect size (normalized distance) is more informative than p-value.

## 4. IQR Normalization Audit

### 3.1 Method

`pooled_iqr = max(IQR_target, IQR_candidate)`

**Assessment:** This is NOT a true pooled IQR (which would combine both distributions into one and compute the IQR). Using `max(IQR)` is a conservative choice — when one distribution is much wider, using the larger IQR as denominator produces smaller normalized distances, potentially overstating similarity.

**Example:** If target IQR = 5 and candidate IQR = 20, pooled_IQR = 20. A Wasserstein distance of 4 would give normalized_distance = 0.2, suggesting high similarity, even though the distributions have very different spreads.

## 5. Spatial Autocorrelation Audit

### 5.1 Documentation

Phase 11 documented Moran's I ≈ 0.979 for all features on both Moon and Mars, indicating very strong spatial autocorrelation.

### 5.2 Bootstrap Treatment

The bootstrap uses spatial blocks (not pixel-level resampling) to account for autocorrelation:
- Block size: 320 m (16 cells at 20 m resolution)
- Blocks sampled with replacement
- 64 repetitions

**Assessment:** Block bootstrap is the correct approach. However:
- 320 m block size may not fully decorrelate adjacent blocks
- Strong autocorrelation (Moran's I = 0.979) means even 320 m blocks may be correlated
- CI bounds may be too narrow (underestimate true uncertainty)

## 6. Sample Size Audit

| Dataset | Raw Pixels | Sampled per Feature |
|---------|-----------|-------------------|
| Moon LOLA | 4,194,304 | 100,000 |
| Mars Jezero | 2,413,152 | 100,000 |
| Earth USGS n36w117 | 25,315,828 | 100,000 |

**Assessment:** Sample sizes are adequate. Subsampling to 100,000 values via linspace indexing provides representative coverage without excessive computation. However, linspace indexing is systematic (not random) sampling, which may miss localized features.

## 7. Multiple Comparisons Audit

Three pairwise comparisons were performed without Bonferroni correction or other family-wise error rate control.

**Assessment:** Acceptable for exploratory analysis where each comparison addresses a distinct research question. Results should not be interpreted as a family of tests. No claims of "statistical significance" across the family are made.

## 8. TMSI Score Interpretation

### 8.1 What TMSI Measures

TMSI measures the similarity of terrain morphology feature distributions (slope, local relief, terrain ruggedness) between two planetary surfaces at a common physical scale.

### 8.2 What TMSI Does NOT Measure

- Geological equivalence
- Planetary body identity
- Habitability
- Landing safety
- Formation process similarity
- Temporal evolution similarity

### 8.3 Score Interpretation Guide

| TMSI Range | Interpretation |
|------------|---------------|
| 80–100 | Very high distribution similarity |
| 60–80 | Moderate-high similarity |
| 40–60 | Moderate similarity |
| 20–40 | Low-moderate similarity |
| 0–20 | Low similarity |

**Phase 20 results:**
- Moon–Mars: 49.92 (moderate similarity)
- Earth–Moon: 61.95 (moderate-high similarity)
- Earth–Mars: 73.14 (high similarity)

## 9. Classification

**Statistical Validity: VERIFIED WITH LIMITATIONS**

All statistical methods are correctly implemented. Results are numerically accurate. However:
- Bootstrap repetition count (64) is low
- No seed sensitivity analysis
- max(IQR) scaling is a conservative but undocumented choice
- Strong spatial autocorrelation not fully captured
- No multiple-comparison correction
- Earth effective resolution mismatch (~29.3 m vs. 20 m)

---

**Next:** See `PHASE20_5_SCIENTIFIC_CONCLUSIONS_AUDIT.md` for the scientific conclusions assessment.