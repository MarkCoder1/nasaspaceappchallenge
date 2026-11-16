# Terra Twin — Phase 22: Method Comparison Matrix

## 1. Executive Summary

This document compares the Terra Twin Terrain Morphology Similarity Index (TMSI) against at least five relevant existing methodological approaches for terrain similarity analysis. The comparison evaluates input data, terrain features, statistical framework, normalization, weighting, spatial information, uncertainty estimation, interpretability, computational requirements, planetary applicability, and limitations.

**Key Finding:** TMSI combines established statistical methods (Wasserstein distance, KS statistic, spatial block bootstrap) into a cohesive pipeline for cross-planetary terrain morphology comparison. No identical methodology was found in the prior art review. The individual components are established techniques, but their combination into a coherent cross-planetary comparison framework represents a potential novel application.

## 2. Method Comparison Matrix

| Criterion | TMSI | Kolmogorov–Smirnov Only | Wasserstein Distance Only | Multivariate Statistical Comparison (e.g., Mahalanobis distance) | Morphometric Classification (e.g., terrain classification systems) | Composite Terrain Similarity Indices (e.g., terrain similarity metrics in geomorphology) |
|-----------|------|------------------------|---------------------------|-----------------------------------------------------------------|------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| **Input data** | Elevation DEM rasters; extracted terrain features (slope, local relief, terrain ruggedness) | Elevation or terrain feature values | Elevation or terrain feature values | Multivariate feature vectors (slope, relief, ruggedness, curvature, aspect, etc.) | Elevation, slope, curvature, texture, land cover | Elevation, slope, relief, roughness, various terrain metrics |
| **Terrain features** | Slope, local relief, terrain ruggedness (Riley TRI) | Any single terrain feature | Any single terrain feature | Multiple terrain features; elevation derivatives | Elevation derivatives; land surface parameters | Elevation derivatives; land surface parameters; texture measures |
| **Statistical framework** | Wasserstein distance + KS statistic + pooled IQR normalization; spatial block bootstrap | KS test only; empirical distribution functions | Wasserstein distance only; optimal transport | Multivariate statistics; Mahalanobis distance; PCA; discriminant analysis | Classification rules; decision trees; rule-based systems | Composite indices; weighted sums; fuzzy logic |
| **Normalization** | Pooled IQR (max of individual IQRs); no upsampling | None (raw KS statistic) | None (raw Wasserstein distance) | Standardization (z-scores); covariance matrix | Classification thresholds; normalization by reference values | Various normalization schemes; index normalization |
| **Weighting** | Equal weights (1.0 each) by default; configurable | Not applicable (single feature) | Not applicable (single feature) | Equal weights or covariance-based weights | Classification rule weights; expert weights | Composite weights; expert-defined weights |
| **Spatial information** | Spatial block bootstrap for uncertainty; geographic extent (10.24 km) | Point-based or pixel-based comparison; no spatial structure | Point-based or pixel-based comparison; no spatial structure | Feature-space comparison; no explicit spatial structure | Spatial classification rules; map units | Spatial analysis; map units; landscape metrics |
| **Uncertainty estimation** | Spatial block bootstrap CI (1,000 repetitions); seed sensitivity analysis | None (point estimate) | None (point estimate) | Confidence intervals from multivariate statistics; bootstrap | Classification accuracy; confusion matrix | Various uncertainty methods; expert judgment |
| **Interpretability** | TMSI score (0-100); feature-level distances; limitations documented | KS statistic (0-1); distribution difference | Wasserstein distance (feature units) | Mahalanobis distance; discriminant scores | Classification labels; membership scores | Composite index value; interpretability varies |
| **Computational requirements** | Moderate (feature extraction; distribution comparison; bootstrap resampling) | Low (single statistic computation) | Low (single distance computation) | Moderate to high (multivariate statistics; matrix operations) | Low to moderate (rule-based classification) | Low to moderate (composite index computation) |
| **Planetary applicability** | Explicitly designed for cross-planetary comparison (Moon, Mars, Earth) | General; applicable to any 1D distributions | General; applicable to any 1D distributions | General; applicable to multivariate feature vectors | General; applicable to any terrain classification | General; applicable to any terrain comparison |
| **Limitations** | Earth effective resolution ~29.3 m (resampled to 20 m); vertical datum differences; Earth coverage limited to two USGS tiles; equal weights arbitrary; max(IQR) scaling; bootstrap repetitions = 1,000 | Single feature only; no uncertainty quantification; sensitive to sample size | Single feature only; no uncertainty quantification; units depend on feature | Requires multivariate normality assumption; sensitive to outliers; requires feature selection | Classification accuracy depends on training data; may not generalize | Composite index may mask feature-level differences; weighting arbitrary |

## 3. Detailed Comparison Notes

### 3.1 TMSI vs. Kolmogorov–Smirnov Only

**Similarities:** Both use KS statistic to compare distribution shapes; both are non-parametric.

**Differences:** TMSI combines KS with Wasserstein distance and IQR normalization into a composite index; KS-only approaches use a single statistic without normalization or aggregation.

**Advantage of TMSI:** Wasserstein distance is more sensitive to differences in the tails of distributions; KS statistic is more sensitive to differences near the median. Combining both provides a more complete picture of distribution differences.

**Limitation of TMSI:** More computationally expensive; requires more parameter choices (weights, normalization method).

### 3.2 TMSI vs. Wasserstein Distance Only

**Similarities:** Both use Wasserstein distance as the core distance metric.

**Differences:** TMSI combines Wasserstein with KS statistic and IQR normalization into a composite index; Wasserstein-only approaches use a single distance measure.

**Advantage of TMSI:** KS statistic provides complementary information (most sensitive near median; Wasserstein more sensitive to tails). Combined approach captures more aspects of distribution differences.

**Limitation of TMSI:** More complex; requires tuning of weights and normalization.

### 3.3 TMSI vs. Multivariate Statistical Comparison

**Similarities:** Both compare multiple terrain features simultaneously.

**Differences:** TMSI compares feature distributions individually and aggregates distances; multivariate methods (e.g., Mahalanobis distance) compare feature vectors directly in multivariate space.

**Advantage of TMSI:** More interpretable (feature-level distances); handles different units naturally through normalization; does not assume multivariate normality.

**Limitation of TMSI:** Does not capture correlations between features; may double-count correlated features.

### 3.4 TMSI vs. Morphometric Classification Methods

**Similarities:** Both classify terrain based on elevation-derived features.

**Differences:** TMSI compares distributions between two terrains; morphometric classification assigns terrain to predefined classes.

**Advantage of TMSI:** Directly compares two terrains; provides a continuous similarity score; no training data required.

**Limitation of TMSI:** Does not provide terrain classification; does not identify terrain types.

### 3.5 TMSI vs. Composite Terrain Similarity Indices

**Similarities:** Both combine multiple terrain metrics into a single similarity index.

**Differences:** TMSI uses explicit statistical distances (Wasserstein, KS) with explicit normalization and uncertainty quantification; composite indices often use ad hoc weighting and normalization.

**Advantage of TMSI:** More statistically principled; explicit uncertainty quantification; explicit limitation documentation.

**Limitation of TMSI:** More complex; requires more parameter choices.

## 4. Originality Assessment

| Aspect | Assessment | Evidence |
|--------|------------|----------|
| **Individual methods** (Wasserstein, KS, bootstrap) | Not novel | All established in literature (Villani 2009; Kolmogorov 1933; Efron 1979) |
| **Feature extraction** (slope, relief, ruggedness) | Not novel | Established in planetary geomorphometry (Smith 2001; Zuber 1998) |
| **Combination of Wasserstein + KS + IQR normalization** | Potential novel application | Not found in prior art review; no single publication combines all three |
| **Spatial block bootstrap for terrain comparison uncertainty** | Potential novel application | Not found in prior art review; Politis & Romano (1994) established bootstrap but not for terrain comparison |
| **Explicit documentation of Earth DEM resolution limitations** | Potential novel application | Not found in prior art review; most planetary DEM studies do not document resolution limitations explicitly |
| **Explicit documentation of vertical datum differences** | Potential novel application | Not found in prior art review; most planetary DEM studies do not document vertical datum differences explicitly |
| **End-to-end pipeline for cross-planetary terrain morphology comparison** | Potential novel application | Not found in prior art review; no single publication combines all elements |

## 5. Classification

**Method Comparison Matrix: COMPLETE**

TMSI combines established statistical methods (Wasserstein distance, KS statistic, spatial block bootstrap) into a cohesive pipeline for cross-planetary terrain morphology comparison. No identical methodology was found in the prior art review. The individual components are established techniques, but their combination into a coherent cross-planetary comparison framework with explicit uncertainty quantification and limitation documentation represents a potential novel application.

## 6. Recommendations

1. **Document prior art explicitly** in any publication to acknowledge existing methods
2. **Highlight the combination** of Wasserstein + KS + bootstrap as the potential novel contribution
3. **Benchmark against established methods** from the literature to demonstrate added value
4. **Document vertical datum and resolution limitations** explicitly, as these are not commonly addressed in planetary terrain comparison literature