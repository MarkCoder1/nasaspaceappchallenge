# Terra Twin — Phase 22: Alternative Method Benchmarking

## 1. Executive Summary

**VERDICT: COMPLETE**

Alternative statistical methods (cosine similarity, Euclidean distance, Pearson correlation) were benchmarked against the TMSI methodology using the same Earth DEM data. The results show that:

- TMSI values are **not directly comparable** to cosine similarity, Euclidean distance, or Pearson correlation values
- Pearson correlation is near zero for most features (|r| < 0.09), indicating that the distributions are not linearly related
- Cosine similarity values (0.51-0.59) are on a different scale than TMSI (49-74)
- Euclidean distance normalized values are very large and produce negative similarity when converted

**Conclusion:** TMSI uses a fundamentally different approach (Wasserstein distance + KS statistic + IQR normalization) that is not directly comparable to simple correlation or distance metrics.

## 2. Alternative Methods Evaluated

| Method | Formula | Implementation | Source |
|--------|---------|----------------|--------|
| Cosine similarity | cos(θ) = (A·B) / (||A||·||B||) | Custom implementation | Standard vector similarity |
| Euclidean distance | d = √Σ(xᵢ - yᵢ)² | Custom implementation | Standard distance metric |
| Pearson correlation | r = cov(X,Y) / (σₓ·σᵧ) | Custom implementation | Standard correlation |
| Wasserstein distance | W(T,C) = ∫₀¹ |F_T⁻¹(u) - F_C⁻¹(u)| du | scipy.stats.wasserstein_distance | Optimal transport theory |
| KS statistic | KS(T,C) = supₓ |F_T(x) - F_C(x)| | scipy.stats.ks_2samp | Kolmogorov-Smirnov test |

## 3. Results by Comparison

### 3.1 Moon–Mars Comparison

| Feature | TMSI (Wasserstein) | Cosine Similarity | Pearson Correlation | Euclidean Distance | Euclidean Normalized |
|---------|-------------------|-------------------|---------------------|-------------------|---------------------|
| Slope | 50.39 | 0.59 | 0.003 | 18059.00 | 389.95 |
| Local Relief | 50.24 | 0.58 | 0.004 | 17931.80 | 342.49 |
| Terrain Ruggedness | 49.15 | 0.59 | 0.003 | 5894.13 | 352.47 |

**Observation:** Cosine similarity values (0.58-0.59) are on a different scale than TMSI values (49-50). Pearson correlation is near zero (0.003-0.004), indicating that the distributions are not linearly related.

### 3.2 Earth–Moon Comparison

| Feature | TMSI (Wasserstein) | Cosine Similarity | Pearson Correlation | Euclidean Distance | Euclidean Normalized |
|---------|-------------------|-------------------|---------------------|-------------------|---------------------|
| Slope | 61.90 | 0.57 | -0.084 | 30328.64 | 414.45 |
| Local Relief | 62.20 | 0.54 | -0.085 | 30563.82 | 200.32 |
| Terrain Ruggedness | 61.75 | 0.55 | -0.084 | 10330.17 | 184.42 |

**Observation:** Pearson correlation is negative (-0.08 to -0.09), indicating a slight negative linear relationship. Cosine similarity values (0.54-0.57) are on a different scale than TMSI values (62-62).

### 3.3 Earth–Mars Comparison

| Feature | TMSI (Wasserstein) | Cosine Similarity | Pearson Correlation | Euclidean Distance | Euclidean Normalized |
|---------|-------------------|-------------------|---------------------|-------------------|---------------------|
| Slope | 73.14 | 0.53 | 0.004 | 20947.15 | 286.25 |
| Local Relief | 72.36 | 0.51 | 0.005 | 21173.95 | 138.78 |
| Terrain Ruggedness | 72.65 | 0.52 | 0.004 | 7271.00 | 129.80 |

**Observation:** Pearson correlation is near zero (0.004-0.005), indicating no linear relationship. Cosine similarity values (0.51-0.53) are on a different scale than TMSI values (72-73).

## 4. Method Comparison

### 4.1 Cosine Similarity

**Method:** cos(θ) = (A·B) / (||A||·||B||)

**Observations:**
- Values range from 0.51 to 0.59 across all comparisons and features
- Does not directly correspond to TMSI values (49-74)
- Measures angle between vectors, not distribution similarity

**Assessment:** Cosine similarity is a valid similarity measure but measures vector angle, not distribution similarity. It is not directly comparable to TMSI.

### 4.2 Euclidean Distance

**Method:** d = √Σ(xᵢ - yᵢ)²

**Observations:**
- Values range from 7,271 to 30,564 across comparisons
- When normalized by range, values range from 129 to 389
- When converted to similarity (1 - normalized), values are negative (-128 to -389)

**Assessment:** Euclidean distance is not directly comparable to TMSI because it measures absolute differences in value space, not distributional similarity. Normalized Euclidean distance produces negative similarity values when converted.

### 4.3 Pearson Correlation

**Method:** r = cov(X,Y) / (σₓ·σᵧ)

**Observations:**
- Values range from -0.085 to +0.005 across all comparisons
- Near zero, indicating no linear relationship between the distributions

**Assessment:** Pearson correlation measures linear relationship, not distributional similarity. The near-zero values indicate that the terrain feature distributions are not linearly related, which is expected for different planetary bodies.

## 5. Why TMSI Uses Wasserstein + KS

The TMSI methodology uses Wasserstein distance and KS statistic rather than cosine similarity, Euclidean distance, or Pearson correlation because:

| Reason | Explanation |
|--------|-------------|
| **Distribution comparison** | Wasserstein and KS compare full distributions, not just summary statistics |
| **Sensitivity to tails** | Wasserstein distance is sensitive to differences in the tails of distributions |
| **Unit normalization** | IQR normalization makes the distance unitless and comparable across features |
| **Non-parametric** | No assumption of normality or linearity |
| **Interpretability** | TMSI = 100 × exp(-D) gives a bounded score (0-100) with interpretable bounds |

## 6. Classification

**Alternative Method Benchmarking: COMPLETE**

Alternative methods (cosine similarity, Euclidean distance, Pearson correlation) were benchmarked against TMSI. The results show that:

1. TMSI values are not directly comparable to alternative methods
2. Pearson correlation is near zero, indicating that the distributions are not linearly related
3. Cosine similarity values are on a different scale than TMSI
4. Euclidean distance normalized produces negative similarity values

**The TMSI methodology (Wasserstein + KS + IQR normalization + exponential transform) is a distinct approach that measures distribution similarity rather than vector correlation.**

## 7. Recommendations

1. **Do not compare TMSI directly to cosine similarity or Pearson correlation** - they measure different things
2. **Use TMSI as a standalone metric** with its own scale (0-100)
3. **Consider benchmarking against other distribution comparison methods** (e.g., Earth Mover's Distance variants, maximum mean discrepancy)
4. **Document the choice of Wasserstein + KS** as a deliberate methodological choice, not an arbitrary one