# Terra Twin — Phase 20.5: Confidence Interval Audit

## 1. Executive Summary

**VERDICT: VERIFIED WITH LIMITATIONS**

All three reported confidence intervals are independently reproduced with exact match. However, the bootstrap methodology has limitations: only 64 repetitions, block sampling limited to 32 blocks per repetition, and no seed variation analysis.

| Comparison | Reported CI | Independently Reproduced | Match |
|------------|------------|---------------------------|-------|
| Moon–Mars | [43.72, 56.80] | [43.7194, 56.7985] | ✅ Exact |
| Earth–Moon | [53.23, 74.81] | [53.2344, 74.8076] | ✅ Exact |
| Earth–Mars | [65.41, 78.40] | [65.4146, 78.4017] | ✅ Exact |

## 2. Bootstrap Methodology Audit

### 2.1 Resampling Methodology

**Method:** Non-overlapping spatial block bootstrap with replacement.

**Implementation** (`science/similarity/comparison/bootstrap.py`):

1. Divide each raster into non-overlapping spatial blocks
2. Only include blocks with ≥50% valid pixels
3. For each bootstrap repetition:
   - Sample up to 32 blocks with replacement from each dataset
   - Concatenate selected blocks into a sample
   - Cap sample at 4096 values (random subsample if larger)
   - Compute Wasserstein distance for each feature
   - Compute TMSI = 100 × exp(−weighted_mean(normalized_distances))
4. After 64 repetitions, compute 2.5th and 97.5th percentiles for CI

### 2.2 Number of Bootstrap Iterations

**Used:** 64 repetitions per comparison

**Assessment:** 64 repetitions is on the low side for bootstrap CI estimation:
- Standard practice: 1,000+ repetitions for stable CI bounds
- 64 repetitions gives limited precision for percentile estimation
- The 2.5th and 97.5th percentiles of 64 values correspond to approximately the 2nd and 63rd ordered values — coarse quantile estimation

**Impact:** CI bounds may be unstable across different random seeds. A seed sensitivity analysis was not performed.

### 2.3 Confidence Interval Calculation

**Method:** Percentile method (2.5th and 97.5th percentiles of bootstrap distribution)

**Assessment:** Correct implementation of percentile bootstrap. However, percentile bootstrap assumes the bootstrap distribution is approximately symmetric around the original estimate, which may not hold for TMSI (bounded at 0–100, potentially skewed).

### 2.4 Spatial Block Construction

**Block size:** 320 m (16 cells at 20 m resolution)

**Block validity:** Blocks with ≥50% valid pixels are included

**Sampling:** Up to 32 blocks selected with replacement per repetition

**Assessment:** Spatial block bootstrap correctly accounts for spatial autocorrelation (Moran's I ≈ 0.979). However:
- Block size of 320 m may not capture the full spatial correlation range
- Sampling only 32 blocks per repetition limits the effective bootstrap sample size
- Blocks near raster edges may be smaller than 320 m

### 2.5 Random Seed Handling

**Seed:** Fixed at 42 for all comparisons

**Assessment:** Fixed seed ensures reproducibility but prevents assessment of seed sensitivity. Different seeds could produce different CI bounds, especially with only 64 repetitions.

### 2.6 Sample Independence Assumptions

**Assumption:** Spatial blocks are treated as approximately independent units

**Reality:** Strong spatial autocorrelation (Moran's I ≈ 0.979) means even blocks may be correlated with neighboring blocks

**Assessment:** Block bootstrap is the correct approach for spatially correlated data, but the block size of 320 m may not fully decorrelate adjacent blocks.

## 3. Independent Reproduction Results

### 3.1 Moon–Mars

| Statistic | Reported | Reproduced | Match |
|-----------|----------|------------|-------|
| TMSI | 49.92 | 49.9229 | ✅ |
| CI lower | 43.72 | 43.7194 | ✅ |
| CI upper | 56.80 | 56.7985 | ✅ |
| Mean | — | 49.6951 | — |
| Median | — | 49.8306 | — |

### 3.2 Earth–Moon

| Statistic | Reported | Reproduced | Match |
|-----------|----------|------------|-------|
| TMSI | 61.95 | 61.9501 | ✅ |
| CI lower | 53.23 | 53.2344 | ✅ |
| CI upper | 74.81 | 74.8076 | ✅ |
| Mean | — | 63.1171 | — |
| Median | — | 63.1783 | — |

### 3.3 Earth–Mars

| Statistic | Reported | Reproduced | Match |
|-----------|----------|------------|-------|
| TMSI | 73.14 | 73.1360 | ✅ |
| CI lower | 65.41 | 65.4146 | ✅ |
| CI upper | 78.40 | 78.4017 | ✅ |
| Mean | — | 71.8180 | — |
| Median | — | 72.0998 | — |

## 4. Uncertainty Type Distinction

The audit distinguishes four types of uncertainty:

| Type | Addressed in Phase 20? | Assessment |
|------|----------------------|------------|
| Measurement uncertainty | ❌ No | DEM measurement error not quantified |
| Sampling uncertainty | ✅ Yes | Bootstrap CI quantifies spatial sampling variability |
| Processing uncertainty | ⚠️ Partially | Resolution normalization documented but not quantified |
| Model/methodological uncertainty | ⚠️ Partially | TMSI formula limitations documented but not quantified |

**Assessment:** Only sampling uncertainty is quantified. Measurement and processing uncertainties are acknowledged but not quantified. Model uncertainty (TMSI formula choice) is acknowledged but not tested.

## 5. Limitations Identified

1. **64 repetitions** — coarse quantile estimation, CI bounds may be seed-sensitive
2. **No seed sensitivity analysis** — different seeds could yield different CIs
3. **Block size of 320 m** — may not fully decorrelate spatially adjacent blocks
4. **Max 32 blocks per repetition** — limits effective bootstrap sample size
5. **Percentile bootstrap** — assumes approximate symmetry, may not hold for bounded TMSI
6. **No bias correction** — bootstrap-t or BCa intervals not computed

## 6. Classification

**Confidence Interval Implementation: VERIFIED WITH LIMITATIONS**

All reported CIs are independently reproduced with exact match. The bootstrap methodology is correctly implemented for spatially correlated data. However, 64 repetitions is low, no seed sensitivity analysis was performed, and only sampling uncertainty is quantified.

---

**Next:** See `PHASE20_5_DATA_PROVENANCE_AUDIT.md` for the data provenance assessment.