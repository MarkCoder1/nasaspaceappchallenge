# Terra Twin — Phase 20.5: TMSI Mathematical Audit

## 1. Executive Summary

**VERDICT: VERIFIED**

The TMSI (Terrain Morphology Similarity Index) mathematical implementation is correctly implemented and all reported values are independently reproduced with exact match.

| Comparison | Reported TMSI | Independently Recalculated | Match |
|------------|--------------|---------------------------|-------|
| Moon–Mars | 49.92 | 49.922854 | ✅ Exact |
| Earth–Moon | 61.95 | 61.950148 | ✅ Exact |
| Earth–Mars | 73.14 | 73.135982 | ✅ Exact |

## 2. TMSI Formula Audit

### 2.1 Mathematical Definition

The TMSI formula as implemented in `science/similarity/scoring/similarity.py`:

```
D = combined_distance = Σ(w_i × d_i) / Σ(w_i)
TMSI = 100 × exp(−D)
```

Where:
- `w_i` = weight for feature i (default: equal weights = 1.0 each)
- `d_i` = normalized_distance for feature i = Wasserstein distance / pooled_IQR
- `pooled_IQR` = max(IQR_target, IQR_candidate) — note: this is the MAX of the two IQRs, not a true pooled IQR

### 2.2 Feature Normalization

Each feature's distributions are compared using:

1. **Wasserstein distance** (Earth Mover's Distance): measures the "work" to transform one distribution into another
2. **Pooled IQR**: `max(Q75_target − Q25_target, Q75_candidate − Q25_candidate)` — takes the larger of the two IQRs
3. **Normalized distance**: `Wasserstein / pooled_IQR`

**Assessment:** The use of `max(IQR)` rather than a true pooled IQR is a conservative scaling choice. When one distribution is much wider than the other, using the larger IQR as the denominator will produce a smaller normalized distance, potentially overstating similarity. This is documented but not quantified.

### 2.3 Feature Weighting

Default weights: equal weights (1.0 each) across slope, local_relief, and terrain_ruggedness.

```python
weights = {'slope': 1.0, 'local_relief': 1.0, 'terrain_ruggedness': 1.0}
```

**Assessment:** Equal weighting is a reasonable default but is arbitrary — no sensitivity analysis of weight choices is reported in Phase 20. Different weight choices could change the TMSI ranking.

### 2.4 Metric Directionality

The formula `TMSI = 100 × exp(−D)` means:
- D = 0 → TMSI = 100 (identical distributions)
- D → ∞ → TMSI → 0 (completely different distributions)
- Higher TMSI = more similar morphology distributions

**Assessment:** Directionality is correct and interpretable. However, TMSI = 50 does NOT mean "50% similar" — it means D = ln(2) ≈ 0.693, which has no direct interpretability as a percentage of similarity.

### 2.5 Score Boundaries

- **Upper bound:** TMSI = 100 (theoretical, only when distributions are identical)
- **Lower bound:** TMSI → 0 (approaches 0 as distributions diverge, never reaches 0)
- **Practical range:** All Phase 20 results fall between 49.92 and 73.14

**Assessment:** Boundaries are mathematically sound. The exponential form ensures TMSI is always positive and bounded above by 100.

### 2.6 Missing Value Handling

Feature layers use `np.isfinite()` masking. Invalid values (NaN, nodata) are excluded from distribution comparisons.

**Assessment:** Correct handling. No missing values were found in any Phase 20 dataset (all 100% valid for Moon/Mars, 98.94% for Earth).

### 2.7 Sensitivity to Outliers

Wasserstein distance is sensitive to outliers in the tails of distributions. KS statistic is sensitive to differences anywhere in the ECDF. No outlier trimming or robustification is applied.

**Assessment:** Appropriate for terrain morphology analysis where extreme values (steep slopes, deep relief) are scientifically meaningful. However, a single extreme outlier could disproportionately affect Wasserstein distance.

### 2.8 Feature Scaling Comparability

Features have different units:
- Slope: degrees
- Local relief: meters
- Terrain ruggedness: meters

Normalization by pooled_IQR makes each feature's distance unitless, enabling comparison across features. However, the IQR-based scaling means features with naturally wider distributions (e.g., slope on steep terrain) will have smaller normalized distances for the same absolute Wasserstein distance.

**Assessment:** IQR normalization is appropriate but the use of `max(IQR)` rather than a combined pooled IQR is a methodological choice that should be explicitly justified.

## 3. Independent Recalculation Results

### 3.1 Moon–Mars

| Feature | Wasserstein | KS | Pooled IQR | NormD | Weight |
|---------|-------------|-----|------------|-------|--------|
| local_relief | 8.5395 | 0.4919 | 12.4072 | 0.6883 | 1.0 |
| slope | 8.7769 | 0.4883 | 12.8051 | 0.6854 | 1.0 |
| terrain_ruggedness | 2.8755 | 0.4955 | 4.0479 | 0.7104 | 1.0 |

- Combined distance: 0.694691
- TMSI: 100 × exp(−0.694691) = **49.922854** ✅ Matches reported 49.92

### 3.2 Earth–Moon

| Feature | Wasserstein | KS | Pooled IQR | NormD | Weight |
|---------|-------------|-----|------------|-------|--------|
| local_relief | 5.8902 | 0.4063 | 12.4072 | 0.4747 | 1.0 |
| slope | 6.1429 | 0.4129 | 12.8051 | 0.4797 | 1.0 |
| terrain_ruggedness | 1.9513 | 0.4089 | 4.0479 | 0.4821 | 1.0 |

- Combined distance: 0.478840
- TMSI: 100 × exp(−0.478840) = **61.950148** ✅ Matches reported 61.95

### 3.3 Earth–Mars

| Feature | Wasserstein | KS | Pooled IQR | NormD | Weight |
|---------|-------------|-----|------------|-------|--------|
| local_relief | 2.8017 | 0.1497 | 8.6601 | 0.3235 | 1.0 |
| slope | 2.7608 | 0.1429 | 9.3433 | 0.2955 | 1.0 |
| terrain_ruggedness | 0.9933 | 0.1568 | 3.1084 | 0.3196 | 1.0 |

- Combined distance: 0.312850
- TMSI: 100 × exp(−0.312850) = **73.135982** ✅ Matches reported 73.14

## 4. Edge Cases Tested

| Edge Case | Behavior | Assessment |
|-----------|----------|------------|
| Empty feature set | Raises ValueError | ✅ Correct |
| Unit mismatch | Raises ValueError | ✅ Correct |
| All invalid values | Raises ValueError | ✅ Correct |
| Zero IQR | Uses `np.finfo(np.float64).eps` as minimum scale | ✅ Prevents division by zero |
| Single shared feature | Computes TMSI with weight_total = that feature's weight | ✅ Correct |

## 5. Mathematical Assumptions

1. **Equal feature weighting** — arbitrary default, no sensitivity analysis
2. **max(IQR) scaling** — conservative but not justified in documentation
3. **Exponential decay** — arbitrary choice; no alternative functional forms tested
4. **No feature correlation adjustment** — features treated as independent
5. **Distribution sampling capped at 100,000 values** — may miss tail behavior in very large datasets

## 6. Classification

**TMSI Mathematical Implementation: VERIFIED**

The TMSI formula is correctly implemented, all reported values are exactly reproduced, and edge cases are handled properly. Methodological choices (equal weights, max(IQR) scaling, exponential form) are documented but represent arbitrary decisions that could affect results.

---

**Next:** See `PHASE20_5_CONFIDENCE_INTERVAL_AUDIT.md` for the bootstrap CI assessment.