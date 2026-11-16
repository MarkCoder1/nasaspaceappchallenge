# Phase 9 Methodology Review Report

## Scope
Critical review of the existing Terrain Morphology Similarity Index (TMSI) method. No change is made to the official scoring baseline (`TMSI = 100 × exp(-D)`, equal weights, pooled-IQR normalization). Findings are documented; any proposed alternative is experimental only.

## Method under review
- Features: slope (degrees), 60 m local relief (m), 60 m Riley-style TRI (m).
- Distance: Wasserstein distribution distance per feature, normalized by the larger pooled interquartile range (pooled-IQR). Kolmogorov–Smirnov statistic retained as diagnostic only.
- Combined distance D: weighted mean of normalized feature distances; equal weights by default, configurable.
- Score: `TMSI = 100 × exp(-D)`.
- Confidence: coverage + resolution-compatibility classification (HIGH / MODERATE / LOW / INSUFFICIENT), not a calibrated probability.
- Uncertainty: non-overlapping spatial block bootstrap (160/320/640 m), 95% intervals.

## Review findings

### 1. Pooled-IQR normalization
- **Assessment:** Appropriate for heavy-tailed, skewed terrain feature distributions (slope, relief, TRI are right-skewed). IQR is robust to outliers, unlike pooled standard deviation.
- **Evidence:** Phase 7 normalization sensitivity shows pooled-IQR-normalized TMSI = 49.9229 vs a pooled-std diagnostic of 39.0244 — the std-based alternative is materially different and more sensitive to tails. The official IQR choice is defensible.
- **Status:** No change recommended. Pooled-IQR remains the official normalization.

### 2. Feature distributional comparability
- **Assessment:** Features are compared at a common physical scale (60 m neighborhood; 20 m native spacing for both Moon and Mars). No raster upsampling is performed.
- **Caveat:** The Moon's effective resolution (16.056 m) differs from its nominal 20 m spacing and from Mars's 20 m. The resolution gate admits the pair (ratio 1.2456 < 4.0), but effective-resolution differences are not removed by the comparison — they are acknowledged as a limitation.
- **Status:** No change. Limitation documented in results.

### 3. Equal weighting
- **Assessment:** Equal weights are the transparent default; weight sensitivity shows TMSI moves within ~0.3 points under 2× emphasis on any single feature.
- **Status:** No change. Equal weights remain official; alternatives are exposed as sensitivity experiments only.

### 4. Exponential score transformation `100 × exp(-D)`
- **Assessment:** Maps combined distance D ∈ [0, ∞) to TMSI ∈ (0, 100], monotonic and bounded. The interpretation of a specific TMSI value is not linear in D and is not a probability.
- **Risk:** Users may misread TMSI as a percentage of similarity or a probability. The platform already labels it as an index, not a probability.
- **Status:** No change. Strengthen UI/export wording that TMSI is not a probability or safety certification.

### 5. KS statistic diagnostic value
- **Assessment:** KS is retained as a diagnostic alongside Wasserstein. In Phase 7 results, KS statistics are uniformly ~0.49 with p-value 0.0 across all features, reflecting strong distributional separation and large sample sizes — the KS p-value is not informative at these sample sizes.
- **Status:** No change to calculation. Document that KS p-value is sample-size-driven and should not be over-interpreted; Wasserstein + pooled IQR is the operative distance.

### 6. Spatial block dimensions
- **Assessment:** Block sizes 160/320/640 m (8/16/32 cells at 20 m) are tested. Block-size sensitivity shows TMSI means shift modestly across blocks (Phase 7: e.g., all-features 49.7641 / 49.6094 / 49.8570 at 160/320/640 m), but intervals remain wide and overlapping.
- **Status:** No change. Block sizes remain sensitivity-tested options; 320 m is the primary.

### 7. Confidence labels
- **Assessment:** HIGH / MODERATE / LOW / INSUFFICIENT are rule-based on valid coverage and resolution ratio. They are explicitly "not a calibrated probability."
- **Status:** No change. Label semantics are documented.

### 8. Spatial-extent sampling bias
- **Assessment:** Phase 9 Experiment C shows TMSI shifts ~3.5 points when the Moon extent changes from 40.96 km to 20.48 km. Different sample boundaries materially alter the result.
- **Status:** No methodological change. Requirement: every comparison must report the spatial extent used; cross-comparisons with different extents are not directly comparable.

### 9. Planetary differences in direct comparison
- **Assessment:** Earth, Moon, Mars differ in gravity, atmosphere, and geologic process. Morphological distribution similarity does not imply environmental equivalence.
- **Status:** No change. Stated limitation in every result.

## Decision
**No silent methodology change.** The official TMSI baseline, normalization, weighting, confidence, and uncertainty procedures remain unchanged. The review confirms the method is defensible within its stated scope and documents the limitations above. Any future alternative (e.g., alternative normalization) would be implemented as a clearly labeled experimental method alongside — never replacing — the official baseline.
