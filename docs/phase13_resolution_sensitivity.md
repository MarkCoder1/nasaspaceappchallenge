# Phase 13: Resolution Sensitivity

## B3. Resolution Sensitivity Analysis

This workstream evaluates how terrain measurements change when datasets with different spatial resolutions are compared. Per Phase 13 Section B3, the following requirements are key:

### Preserve original-resolution data
- Full-resolution DEMs are kept alongside any resampled versions
- Original file SHA256 and metadata are documented

### Record every resampling operation
- Scale factor (target/original resolution)
- Interpolation method (bilinear, cubic, nearest)
- Purpose of resampling (comparison, visualization, etc.)
- All operations logged in benchmark configuration

### Avoid implying that resampling restores lost information
- Explicit statement that features lost at native resolution cannot be recovered
- Resampling is a transformation, not a reconstruction

### Compare at multiple defensible resolutions when coverage permits
- TMSI and terrain metrics computed at native resolution
- Where feasible, also computed at coarser resolutions
- Results documented with clear notation of which resolution each value corresponds to

### Evaluated Resolution Differences

#### Moon (moon_lola) vs Mars (mars_jezero_ctx_dtm)

| Metric | Moon (20 m/pixel) | Mars (20 m pixel spacing) | Notes |
|--------|-------------------|---------------------------|-------|
| Nominal resolution | 20 m/pixel | 20 m pixel spacing | Similar nominal resolution; exact comparison requires CRS alignment |
| Elevation range | -2872.11 to 1959.42 m | (Jezero-specific range) | Different geographical terrain |
| Slope statistics | Computed at native 20 m | Computed at native 20 m | Direct comparison feasible due to similar resolution |
| TRI statistics | Computed at native 20 m | Computed at native 20 m | Direct comparison feasible |

### Resolution Ratio Analysis

The resolution ratio between Mars and Moon datasets is approximately 1.0 (both ~20 m/pixel), meaning no aggressive resampling was needed for direct comparison. However, the following should be noted:

1. **Exact resolution matching**: "20 m/pixel" vs "20 m pixel spacing" may differ in how effective resolution is computed. The moon_lola dataset documents effective resolution separately from nominal resolution.

2. **No resampling applied**: Both datasets were used at their native resolution for comparison. No interpolation was applied.

3. **If resampling were needed**: 
   - Scale factor would be target_resolution / 20 m
   - Bilinear interpolation would be the default method
   - The resulting TMSI would be documented with a note: "TMSI at resampled resolution; interpolation method: bilinear; scale factor: X"

### Moon (various resolutions) - Hypothetical

If the moon_lola data were resampled to coarser resolutions:

| Target resolution | Scale factor | Expected TMSI change | Notes |
|-------------------|-------------|---------------------|-------|
| 40 m | 2.0× | Would decrease or increase depending on terrain variation | Finer details lost |
| 10 m | 0.5× | Would increase if 20 m captures fine detail | Interpolation artifacts possible |
| 20 m (native) | 1.0× | Baseline TMSI value | No resampling |

### Resolution Sensitivity Warnings (Phase 13)

Per the scientific uncertainty framework:

- **Resolution difference**: If comparing datasets with different nominal resolutions, document the ratio and expect potential TMSI variation.
- **Resampling artifacts**: Bilinear interpolation assumes gradual terrain variation; does not preserve cliffs or sharp features.
- **Native resolution preferred**: All primary comparisons should use native-resolution data. Resampled results are supplementary.
- **Document scale factor**: Any resampled comparison must record the scale factor in the benchmark config.

### Empirical Finding from Phase 12

TMSI is extent-sensitive: at 5.12 km extent, TMSI ≈ 23.71; at full 10.24 km extent, TMSI ≈ 49.92. This material change (factor of ~2.1) demonstrates that spatial extent can be as significant a source of variation as resolution. Both factors must be reported independently per the Phase 13 uncertainty framework.