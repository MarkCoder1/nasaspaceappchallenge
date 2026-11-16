# Phase 13: Scientific Uncertainty Analysis

## F. Scientific Uncertainty Framework

This workstream introduces an explicit uncertainty framework that distinguishes four independent categories per Phase 13 Section 7. Each category is reported separately; they are not combined into an arbitrary uncertainty percentage.

## Four Independent Uncertainty Categories

### 1. Dataset Uncertainty

**What it quantifies**: Differences between independently produced elevation products.

- **Arises from**: Different missions, processing pipelines, reference frames, and data processing levels
- **Not a measure of "error"**: Quantifies dataset diversity, not measurement error
- **Reported separately**: Per-dataset metadata, elevation range per dataset, resolution spread, vertical reference diversity

**Phase 13 Example** (moon_lola vs mars_jezero_ctx_dtm):
- Dataset 1 (moon_lola): Moon (2015) Sphere / Ocentric / South Polar; MOON_DE421 reference frame; 20 m/pixel nominal
- Dataset 2 (mars_jezero_ctx_dtm): Equirectangular planetary CRS; MOLA control preserved; 20 m pixel spacing
- Vertical reference diversity: 2 distinct vertical references (Moon vs Mars datums)
- Resolution spread: Both ~20 m/pixel, but effective resolution treatment differs
- **Warning**: "Dataset uncertainty quantifies differences between independently produced elevation products. It is not a measure of 'error.'"

### 2. Resolution Uncertainty

**What it quantifies**: Effects of spatial resolution and resampling.

- **Arises from**: Different nominal resolutions, interpolation methods, scale factors
- **Not conflated with measurement error**: Evaluated via sensitivity analysis (Phase 13 B3)
- **Key requirements** (Phase 13 B3):
  - Preserve original-resolution data
  - Record every resampling operation (scale factor, interpolation method)
  - Avoid implying resampling restores lost information
  - Compare at multiple defensible resolutions when coverage permits

**Reporting structure**:
- Resolution_a_m, resolution_b_m, resolution_ratio
- Notes on interpolation method and scale factor
- Comparison metrics at each resolution (with clear notation)

**Phase 13 Example**:
- Both moon_lola and mars_jezero_ctx_dtm have ~20 m/pixel nominal resolution
- No resampling was applied in primary comparison
- If resampling were needed: document scale factor and interpolation method
- **Warning**: "Preserve original-resolution data. Do not imply that resampling restores lost information."

### 3. Sampling Uncertainty

**What it quantifies**: Effects of window location and selection on TMSI and terrain metrics.

- **Arises from**: Different window positions, extents, and selection within the same DEM
- **Phase 12 documented findings**:
  - TMSI is extent-sensitive: 23.71 @ 5.12 km → 49.92 at 10.24 km
  - TMSI is window-location-sensitive: different positions yield different scores
  - Within-body TMSI ranges overlap with between-body range (22.38–90.60)
  - Non-overlapping windows provide independent observations
  - Identical windows → TMSI = 100 (self-control, not inter-dataset similarity)

**Reporting structure**:
- n_windows_a, n_windows_b
- window_offset_a, window_offset_b (in pixels)
- extent_km used for TMSI computation
- Sensitivity warning: True (window position and extent materially affect results)

**Phase 13 Example**:
- Different window positions within moon_lola would yield different TMSI values
- Extent of 10.24 km vs 5.12 km changes TMSI by factor of ~2.1
- **Warning**: "TMSI is extent-sensitive and window-location-sensitive. Different extents produce different scores."

### 4. Methodological Sensitivity

**What it quantifies**: Effects of spatial extent, overlap, and algorithm configuration on TMSI and terrain metrics.

- **Arises from**: Spatial extent, overlap fraction, algorithm configuration
- **Phase 12 documented findings**:
  - TMSI depends on spatial extent (5.12 km → 10.24 km changes TMSI from 23.71 to 49.92)
  - Identical windows → TMSI = 100 (self-control, does not establish inter-dataset similarity)
  - High overlap inflates similarity (78.6–88.0 depending on overlap fraction)
  - No overlap → TMSI compares non-overlapping windows (distributional separation)
  - Body identity not recoverable from TMSI alone (within-body and between-body ranges overlap)
  - Confidence level should be reported alongside TMSI value

**Reporting structure**:
- extent_km: spatial extent used
- overlap_status: classification (identical/high/partial/none/unknown)
- confidence: reported confidence level (e.g., "HIGH")
- materiality_warning: True if extent < 10 km or overlap is "high"/"identical"

**Phase 13 Example**:
- Extent 10.24 km: materiality_warning = False (full extent)
- Overlap "high": materiality_warning = True (high overlap inflates similarity)
- Overlap "identical": materiality_warning = True (TMSI = 100, self-control)
- **Warning**: "Spatial extent of 5.12 km may materially affect TMSI results (Phase 12: 5.12 km → 10.24 km changed TMSI from 23.71 to 49.92)."

## Full Uncertainty Report Structure

The `full_uncertainty_report()` function combines all four categories into a single structured document without combining them into one percentage:

```json
{
  "dataset_uncertainty": {
    "category": "dataset_uncertainty",
    "per_dataset": {...},
    "resolution_spread_m": 0.0,
    "vertical_reference_diversity_count": 2,
    "vertical_references": [...],
    "warnings": [...]
  },
  "resolution_uncertainty": {
    "category": "resolution_uncertainty",
    "resolution_a_m": 20.0,
    "resolution_b_m": 20.0,
    "resolution_ratio": 1.0,
    "notes": [...],
    "comparison_metrics": {...}
  },
  "sampling_uncertainty": {
    "category": "sampling_uncertainty",
    "n_windows_a": 15,
    "n_windows_b": 120,
    "window_offset_a": [0, 0],
    "window_offset_b": [0, 0],
    "extent_km": 10.24,
    "notes": [...],
    "sensitivity_warning": true
  },
  "methodological_sensitivity": {
    "category": "methodological_sensitivity",
    "extent_km": 10.24,
    "overlap_status": "high",
    "confidence": "HIGH",
    "notes": [...],
    "materiality_warning": false
  },
  "summary": {
    "reporting_framework": "Phase 13 Section 7 — four independent categories, not combined into one percentage.",
    "all_four_categories_present": true
  }
}
```

## Key Principles

1. **Report each category separately**: Do not combine into one arbitrary uncertainty percentage
2. **Document assumptions and limitations**: Each category section includes scientific caveats
3. **Use repeated sampling and bootstrap where possible**: For confidence intervals around TMSI values
4. **Never fabricate uncertainty values**: Report what can be genuinely computed from dataset metadata and raster properties
5. **Preserve Phase 12 findings**: Extent sensitivity, overlap bias, and within-body/between-body range overlap are preserved and reported
6. **Earth remains PENDING**: Until NASADEM is authenticated, Earth contributes no uncertainty categories (blocked status)