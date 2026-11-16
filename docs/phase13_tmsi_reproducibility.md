# Phase 13: TMSI Reproducibility

## Overview

This document reports on TMSI (Terrain Morphology Similarity Index) reproducibility across independently sourced DEM datasets, per Phase 13 workstreams F and B4.

## Key Phase 12 Findings (Preserved)

Before reporting Phase 13 results, the following Phase 12 findings are preserved and must be acknowledged:

1. **TMSI is extent-sensitive**: 23.71 @ 5.12 km → 49.92 at full 10.24 km extent
2. **Within-body TMSI ranges overlap and exceed between-body range**:
   - Moon: 29.27 – 94.10
   - Mars: 40.99 – 90.90
   - Between-body: 22.38 – 90.60
3. **Within-body ranges overlap with between-body range**: TMSI alone cannot identify planetary body
4. **Identical windows give TMSI = 100** (self-control). High overlap inflates similarity.
5. **Non-overlapping comparisons are independent observations**.

## TMSI Reproducibility Across Independent Datasets

### Dataset Pair: moon_lola vs mars_jezero_ctx_dtm

Since these datasets cover different planetary bodies (Moon vs Mars), TMSI comparison is not scientifically meaningful per Phase 12 findings. The comparison is reported for completeness, with appropriate caveats.

### Cross-Body TMSI Comparison

| Metric | Value | Caveat |
|--------|-------|--------|
| TMSI (Moon dataset, within-body) | 29.27 – 94.10 (range) | Moon-specific; not comparable to Mars |
| TMSI (Mars dataset, within-body) | 40.99 – 90.90 (range) | Mars-specific; not comparable to Moon |
| TMSI (between-body) | 22.38 – 90.60 (range) | Spans both within-body ranges |
| Overlap between within-body and between-body | Substantial overlap confirmed | TMSI does not identify planetary body |

### Within-Body Reproducibility (Same Dataset, Different Windows)

For a single DEM source, TMSI reproducibility depends on:
- **Spatial extent**: 5.12 km vs 10.24 km produce materially different TMSI (23.71 vs 49.92)
- **Window location**: Different window positions within the same DEM yield different TMSI scores
- **Overlap status**: 
  - Identical windows → TMSI = 100 (self-control, not inter-dataset similarity)
  - High overlap → TMSI inflated (78.6–88.0 depending on overlap fraction)
  - No overlap → TMSI describes distributional separation, not similarity

### Between-Body Comparison (Moon vs Mars)

| Finding | Value | Interpretation |
|---------|-------|----------------|
| TMSI range overlap | Moon (29.27–94.10) ∩ Mars (40.99–90.90) ≠ ∅ | Substantial overlap |
| Moon max TMSI > between-body max | 94.10 > 90.60 | Moon TMSI can exceed between-body max |
| Mars max TMSI > between-body max | 90.90 > 90.60 | Mars TMSI can exceed between-body max |
| Body identity from TMSI | Not recoverable | Within-body and between-body ranges overlap |

> **Fundamental limitation**: TMSI does not establish planetary body identity. The within-body TMSI ranges for Moon and Mars both overlap with the between-body range. Two different planetary bodies can produce TMSI values that are statistically indistinguishable.

## Uncertainty Categories for TMSI

Per Phase 13 Section 7, four independent uncertainty categories affect TMSI reproducibility:

1. **Dataset uncertainty**: Differences between independently produced elevation products (Moon vs Mars have different CRS, reference frames, and terrain characteristics). Reported separately; not combined with other categories.

2. **Resolution uncertainty**: Both moon_lola and mars_jezero_ctx_dtm have similar nominal resolution (20 m/pixel), but effective resolution differs. Documented via the resolution_uncertainty category. No resampling was applied in the primary comparison.

3. **Sampling uncertainty**: TMSI is extent-sensitive (5.12 km → 10.24 km changes TMSI from 23.71 to 49.92) and window-location-sensitive. Reported via the sampling_uncertainty category. Multiple window positions and extents should be sampled and reported.

4. **Methodological sensitivity**: TMSI depends on spatial extent, overlap fraction, and algorithm configuration (Phase 12 finding). Reported via the methodological_sensitivity category. Materiality warnings are generated when extent < 10 km or overlap status is "high" or "identical".

## TMSI Reproducibility Protocol (Phase 13)

For any TMSI reproducibility study, the following should be documented:

1. **Dataset identifiers**: Full registry IDs for both datasets (e.g., moon_lola, mars_jezero_ctx_dtm)
2. **Spatial extent**: km extent used for TMSI computation (e.g., 10.24 km)
3. **Window coordinates**: Row/col offsets for each dataset's sampling window
4. **Overlap status**: Classification (identical/high/partial/none/unknown) and overlap fraction
5. **TMSI score**: The computed similarity index value
6. **Confidence level**: Reported alongside the TMSI value
7. **Uncertainty categories**: All four categories reported separately (dataset, resolution, sampling, methodological)
8. **Comparison note**: Whether comparison is within-body or cross-body, with scientific justification
9. **Resampling metadata**: If any resampling was applied, document scale factor, interpolation method, and purpose

> **Never fabricate TMSI scores**. All TMSI values must come from actual computations using the compare_terrain() backend function or equivalent methodology. If rasters are unavailable, the result should be documented as "TMSI not computable: no raster data available" rather than inventing a value.

## Phase 13 TMSI Findings Summary

- **Within-body TMSI ranges preserved**: Moon 29.27–94.10, Mars 40.99–90.90
- **Between-body TMSI range preserved**: 22.38–90.60
- **Overlap confirmed**: Within-body ranges overlap with between-body range
- **Body identity not recoverable**: TMSI alone cannot determine planetary body
- **Extent sensitivity confirmed**: Different extents produce materially different TMSI
- **Overlap bias documented**: Identical windows → TMSI = 100; high overlap → inflated similarity
- **No independent DEM benchmark completed**: No dataset pair currently enables within-pair TMSI reproducibility testing due to lack of overlapping terrain coverage across two+ DEM products
- **Earth data unavailable**: NASADEM blocked by authentication; no Earth TMSI comparisons possible