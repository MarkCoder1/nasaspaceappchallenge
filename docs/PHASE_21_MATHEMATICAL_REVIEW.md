# Terra Twin — Phase 21: Independent Mathematical Review of TMSI

## 1. Executive Summary

This document presents an independent mathematical review of the Terrain Morphology Similarity Index (TMSI) implementation in the Terra Twin codebase. Every mathematical operation in the TMSI pipeline has been formally defined, its scientific interpretation explained, its assumptions identified, and its implementation independently reproduced.

**Overall Finding:** The TMSI implementation is mathematically consistent and internally correct. All reported values are reproducible. However, several methodological choices are arbitrary (equal weights, max(IQR) scaling, exponential transform) and lack sensitivity analysis. The TMSI score is a descriptive statistic, not a calibrated probability or measure of geological equivalence.

## 2. Mathematical Formalism

### 2.1 Feature Extraction

#### 2.1.1 Slope

For a raster cell at position (i,j) with elevation z(i,j) and cell resolution (Δx, Δy):

```
g_x(i,j) = (z(i,j+1) - z(i,j-1)) / (2·Δx)
g_y(i,j) = (z(i+1,j) - z(i-1,j)) / (2·Δy)
slope(i,j) = atan(√(g_x² + g_y²))
```

- Units: degrees
- Window: pixel spacing (no neighborhood window)
- Edge cells: excluded via gradient computation (requires neighbors)
- Assumption: raster is regularly spaced; gradient approximated by central differences

#### 2.1.2 Local Relief

For each cell (i,j), a 60 m physical window (3×3 cells at 20 m resolution) is defined:

```
local_relief(i,j) = max(z over window) − min(z over window)
```

- Units: metres
- Window: 60 m physical (3×3 cells at 20 m post spacing)
- Edge cells: excluded (incomplete windows)
- Assumption: square window; all 9 cells must be valid

#### 2.1.3 Terrain Ruggedness (Riley TRI)

For each cell (i,j), a 60 m physical window (3×3 cells at 20 m resolution):

```
TRI(i,j) = sqrt( (1/N) · Σ_k (z_k − z(i,j))² )
```

where z_k are the N valid neighbor cells in the 3×3 window excluding the center cell.

- Units: metres
- Window: 60 m physical (3×3 cells at 20 m post spacing)
- Edge cells: excluded
- Assumption: Riley TRI is a roughness index, not a hazard measure

### 2.2 Distribution Comparison

For each feature f, two distributions are compared: target T_f and candidate C_f.

#### 2.2.1 Subsampling

Each distribution is subsampled to at most 100,000 values via linspace indexing:

```
indices = linspace(0, N−1, min(N, 100000))
sampled = values[indices]
```

- Assumption: systematic subsampling preserves distribution characteristics
- Limitation: systematic (not random) subsampling may miss localized features

#### 2.2.2 Wasserstein Distance

The 1-Wasserstein distance (Earth Mover's Distance) between two 1D distributions:

```
W(T,C) = ∫₀¹ |F_T⁻¹(u) − F_C⁻¹(u)| du
```

where F_T⁻¹ and F_C⁻¹ are the quantile functions of the two distributions.

- Implementation: `scipy.stats.wasserstein_distance`
- Units: same as the feature (degrees for slope, metres for relief/ruggedness)
- Sensitivity: sensitive to differences across the entire distribution, including tails

#### 2.2.3 Kolmogorov–Smirnov Statistic

```
KS(T,C) = supₓ |F_T(x) − F_C(x)|
```

where F_T and F_C are the empirical cumulative distribution functions.

- Implementation: `scipy.stats.ks_2samp(method="auto")`
- Range: [0, 1]; 0 = identical distributions, 1 = completely disjoint
- Sensitivity: sensitive to differences in location, spread, and shape

#### 2.2.4 Pooled IQR (max scaling)

```
pooled_IQR = max(IQR_T, IQR_C)
IQR = Q75 − Q25
```

- **Note:** This is NOT a true pooled IQR (which would combine both distributions). It uses the maximum of the two individual IQRs.
- Rationale: conservative scaling (larger denominator → smaller normalized distance)

#### 2.2.5 Normalized Distance

```
d_i = W(T,C) / max(IQR_T, IQR_C, ε)
```

where ε = machine epsilon (to prevent division by zero).

- Units: unitless
- Interpretation: Wasserstein distance scaled by the larger spread of the two distributions

## 2.3 Composite TMSI Index

### 2.3.1 Weighted Combined Distance

```
D = Σ(w_i × d_i) / Σ(w_i)
```

where w_i are feature weights (default: equal weights = 1.0 each).

### 2.3.2 TMSI Score

```
TMSI = 100 × exp(−D)
```

- Range: (0, 100]
- TMSI = 100 when D = 0 (identical distributions)
- TMSI → 0 as D → ∞ (completely different distributions)
- Interpretation: higher = more similar morphology distributions

## 2.4 Uncertainty Quantification (Bootstrap)

### 2.4.1 Spatial Block Bootstrap

The bootstrap resamples spatial blocks (not individual pixels) to account for spatial autocorrelation:

1. Divide each raster into non-overlapping spatial blocks of size B×B cells
2. Retain only blocks with ≥50% valid pixels
3. For each repetition:
   - Sample up to 32 blocks with replacement from each dataset
   - Concatenate selected blocks into a sample (capped at 4,096 values)
   - Compute Wasserstein distance for each feature
   - Compute TMSI = 100 × exp(−weighted_mean(normalized_distances))
4. After R repetitions, compute 2.5th and 97.5th percentiles for CI

### 2.4.2 Block Size

- Default: 320 m (16 cells at 20 m resolution)
- Candidate blocks: 160 m, 320 m, 640 m
- Rationale: block size should exceed the spatial correlation range

## 2.5 Confidence Classification

The `classify_confidence()` function assigns a qualitative confidence level based on:
- Target valid percent
- Candidate valid percent  
- Resolution compatibility
- Feature count

## 3. Independent Reproduction

All TMSI values were independently recalculated during Phase 20.5 audit:

| Comparison | Reported TMSI | Reproduced TMSI | Match |
|------------|--------------|-----------------|-------|
| Moon–Mars | 49.92 | 49.9229 | ✅ Exact |
| Earth–Moon | 61.95 | 61.9501 | ✅ Exact |
| Earth–Mars | 73.14 | 73.1360 | ✅ Exact |

All confidence intervals were also independently reproduced with exact match.

## 4. Mathematical Weaknesses Identified

### 4.1 Arbitrary Feature Weights

**Issue:** Equal weights (1.0 each) are assigned to slope, local relief, and terrain ruggedness without justification.

**Impact:** Different weight choices could change TMSI values and potentially the ranking of comparisons. No weight sensitivity analysis was performed in the original codebase.

**Severity:** Moderate — the choice of equal weights is reasonable but arbitrary.

### 4.2 max(IQR) Scaling

**Issue:** The pooled IQR uses `max(IQR_T, IQR_C)` rather than a true pooled IQR (combining both distributions).

**Impact:** When one distribution is much wider than the other, using the larger IQR as denominator produces smaller normalized distances, potentially overstating similarity.

**Severity:** Moderate — conservative scaling but not justified in documentation.

### 4.3 Exponential Transform

**Issue:** The transform `TMSI = 100 × exp(−D)` is arbitrary. No alternative functional forms were tested.

**Impact:** The interpretation of TMSI values as "percent similarity" is not mathematically justified. TMSI = 50 does not mean "50% similar."

**Severity:** Moderate — the score is bounded (0, 100] but lacks probabilistic interpretation.

### 4.4 No Feature Correlation Adjustment

**Issue:** Features are treated as independent in the weighted combination, but slope, local relief, and terrain ruggedness are mathematically related (all derived from the same elevation data).

**Impact:** Correlated features are effectively double-counted, giving disproportionate weight to shared information.

**Severity:** Moderate — could bias the combined distance toward features that are more correlated.

### 4.5 Systematic Subsampling

**Issue:** Distributions are subsampled via `linspace(0, N−1, 100000)` — a systematic (not random) subsample.

**Impact:** May miss localized features or periodic patterns in the data.

**Severity:** Low — for large, spatially continuous rasters, systematic subsampling is generally adequate.

### 4.6 Bootstrap Limitations

**Issue:** 1,000 repetitions (increased from 64 in Phase 20.6) is still on the low side for stable CI estimation. Seed sensitivity analysis showed max TMSI difference < 0.44 across 5 seeds, which is acceptable but not negligible.

**Impact:** CI bounds may vary slightly across different random seeds.

**Severity:** Low — 1,000 repetitions is adequate for most applications.

## 5. Classification

**TMSI Mathematical Implementation: VERIFIED**

The TMSI formula is correctly implemented, all reported values are exactly reproducible, and edge cases are handled properly. Methodological choices (equal weights, max(IQR) scaling, exponential form) are documented but represent arbitrary decisions that could affect results. No mathematical errors were found.

## 6. Recommendations

1. **Document weight sensitivity:** Perform analysis of how different weight schemes affect TMSI rankings.
2. **Consider alternative pooling:** Evaluate true pooled IQR vs. max(IQR) scaling.
3. **Address feature correlation:** Consider decorrelating features or adjusting weights for correlation.
4. **Clarify score interpretation:** Explicitly state that TMSI is a descriptive index, not a calibrated probability or percentage of similarity.