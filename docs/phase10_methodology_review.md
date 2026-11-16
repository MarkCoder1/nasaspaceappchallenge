# Phase 10 Methodology Review Report

## Scope
Review of the official Terrain Morphology Similarity Index (TMSI) method in light of Phase 10 experiments (spatial-extent sensitivity, same-body self-consistency benchmark). No silent change is made to the official scoring baseline (`TMSI = 100 × exp(-D)`, equal weights, pooled-IQR normalization).

## Method under review (unchanged)
- Features: slope (degrees), 60 m local relief (m), 60 m Riley-style TRI (m).
- Distance: Wasserstein per feature, normalized by larger pooled IQR; KS diagnostic only.
- Combined distance D: weighted mean of normalized feature distances; equal weights default.
- Score: `TMSI = 100 × exp(-D)`.
- Confidence: coverage + resolution-compatibility (HIGH/MODERATE/LOW/INSUFFICIENT), not a probability.
- Uncertainty: non-overlapping spatial block bootstrap (160/320/640 m), 95% intervals.

## Phase 10 findings relevant to methodology

### 1. Spatial-extent sensitivity (major finding)
Centered square windows of equal extent extracted from both Mars and Moon; TMSI computed per extent:

| Extent | TMSI | Combined D | Bootstrap mean | 95% interval |
|---|---|---|---|---|
| 5.12 km | 23.7099 | 1.4393 | 22.8115 | [14.08, 31.83] |
| 10.24 km | 27.7206 | 1.2830 | 25.3366 | [18.81, 32.84] |
| 20.48 km | 46.4041 | 0.7678 | 43.7518 | [36.66, 50.25] |
| Full (Mars 31.92×30.24 / Moon 40.96 km) | 49.9229 | 0.6947 | 49.7380 | [42.66, 56.61] |
| 30.72 km | skipped (exceeds Mars coverage) | | | |
| 40.96 km | skipped (exceeds Mars coverage) | | | |

Interpretation: TMSI is strongly extent-dependent. Small windows (5–10 km) collapse TMSI to ~24–28; at 20.48 km it reaches 46.4; at full extent 49.92. The choice of sampling window shifts TMSI by up to ~26 points (5.12 km vs full).

### 2. Same-body self-consistency benchmark
Different windows of the same body compared (20.48 km Moon windows; 10.24 km Mars windows):

| Comparison | Overlap | TMSI | Combined D |
|---|---|---|---|
| Moon center vs northwest | yes | 58.1318 | 0.5425 |
| Moon center vs southeast | yes | 83.3207 | 0.1825 |
| Moon northwest vs southeast | no | 54.8968 | 0.5997 |
| Mars center vs northwest | yes | 56.1800 | 0.5766 |
| Mars center vs southeast | yes | 65.5092 | 0.4230 |
| Mars northwest vs southeast | no | 46.5452 | 0.7647 |
| Cross-body Moon vs Mars (ref) | n/a | 49.9229 | 0.6947 |

Interpretation: Overlapping windows artificially inflate TMSI (shared pixels). Non-overlapping same-body windows (46.55–58.13) fall in the same range as cross-body Moon–Mars (49.92). Window location/extent can dominate body identity. This is NOT a fully independent benchmark (same source rasters), but it is a methodological self-consistency check showing spatial sampling drives results as much as planetary difference.

### 3. Pooled-IQR normalization
Confirmed defensible (Phase 9): IQR robust to skewed terrain tails; pooled-std alternative gives materially different TMSI (39.02 vs 49.92). No change.

### 4. Equal weighting
Confirmed defensible (Phase 9/10): alternative weights shift TMSI within ~0.3 of baseline. No change.

### 5. Exponential transformation `100 × exp(-D)`
Bounded, monotonic, not a probability. UI wording already states TMSI is not a probability/safety certification. No change.

### 6. KS diagnostic
KS statistics uniformly ~0.49 with p-value 0.0 at large sample sizes; p-value is sample-size-driven and not informative. Wasserstein + pooled IQR is the operative distance. Documented limitation.

### 7. Spatial block bootstrap
Moran's I min 0.979 (Phase 9) → independent-pixel assumption invalid; block bootstrap justified. Block sizes 160/320/640 m tested; 320 m primary.

## Decision
**No silent methodology change.** The official TMSI, normalization, weighting, confidence, and uncertainty procedures remain unchanged. Phase 10 confirms two hard requirements for defensible use:
1. Every comparison MUST report its spatial extent (window size and location).
2. Cross-comparisons with different extents are NOT directly comparable.

A recommended sampling strategy (fixed physical-area windows, ≥20 km, non-overlapping for same-body checks) is documented in `phase10_sampling_sensitivity_report.md` as an experimental option, not a replacement for the official baseline.
