# Terra Twin — Phase 21: Limitations and Recommendations

## 1. Executive Summary

This document consolidates all limitations identified across Phases 17–21 and provides recommendations for future work. All Phase 17 scientific limitations are preserved. New limitations identified during Phase 21 audit are documented with recommendations for resolution.

## 2. Phase 17 Scientific Limitations (All Preserved)

| # | Limitation | Status | Relevance to TMSI |
|---|-----------|--------|-------------------|
| 1 | TMSI cannot establish planetary body identity | PRESERVED | Core limitation; prevents overclaiming |
| 2 | Extent-sensitivity (23.71 @ 5.12 km → 49.92 @ 10.24 km) | PRESERVED | Results depend on chosen extent |
| 3 | Earth data blocked by NASA Earthdata authentication | PRESERVED | Limits Earth dataset options |
| 4 | Independent DEM benchmark blocked | PRESERVED | No overlapping-terrain pair for reproducibility testing |
| 5 | Spatial autocorrelation not fully captured (Moran's I = 0.979) | PRESERVED | Bootstrap CI may be slightly too narrow |
| 6 | "HIGH confidence" is qualitative | PRESERVED | Not a calibrated probability |
| 7 | Results design-dependent (10.24 km extent) | PRESERVED | Results may change with different extent |
| 8 | Riley TRI is roughness index, not hazard measure | PRESERVED | Prevents misinterpretation as hazard assessment |
| 9 | Slope sensitive to DEM noise at steep slopes | PRESERVED | Affects steep terrain more than flat terrain |
| 10 | Edge cells excluded from local relief statistics | PRESERVED | Reduces effective coverage near raster edges |

## 3. Phase 20 Limitations (Documented and Preserved)

| # | Limitation | Status | Impact |
|---|-----------|--------|--------|
| P20-1 | Earth DEM effective resolution ~29.3 m (resampled to 20 m) | DOCUMENTED | Earth–Moon/Earth–Mars comparisons use downsampled data |
| P20-2 | Vertical datum differences (NAVD88 vs. LOLA/MOLA/delta geoid) | DOCUMENTED | Not quantitatively resolved; may affect elevation-based features |
| P20-3 | Earth coverage limited to two USGS tiles (Death Valley / southern Arizona) | DOCUMENTED | Cannot generalize to global Earth terrain |
| P20-4 | Bootstrap repetitions = 1,000 (moderate) | ADDRESSED | Increased from 64; adequate for most purposes |
| P20-5 | No seed sensitivity analysis in Phase 20 | ADDRESSED | Added in Phase 20.6; results stable across seeds |
| P20-6 | Equal feature weights (arbitrary) | DOCUMENTED | No sensitivity analysis performed |
| P20-7 | max(IQR) scaling rather than true pooled IQR | DOCUMENTED | Conservative scaling; may overstate similarity |

## 5. Phase 21 New Limitations Identified

| # | Limitation | Severity | Impact | Recommendation |
|---|-----------|----------|--------|---------------|
| P21-1 | Feature correlation not adjusted | Moderate | Slope, relief, ruggedness derived from same elevation data; effectively double-counted | Consider decorrelating features or adjusting weights |
| P21-2 | Systematic (not random) subsampling to 100K values | Low | May miss localized features | Consider random subsampling |
| P21-3 | Exponential transform TMSI = 100 × exp(−D) is arbitrary | Moderate | No alternative functional forms tested | Document as methodological choice; consider alternatives |
| P21-4 | Bootstrap CI uses percentile method | Low | Assumes approximate symmetry; TMSI bounded (0–100) may be skewed | Consider bootstrap-t or BCa intervals |
| P21-5 | No multiple-comparison correction | Low | Three pairwise comparisons; no family-wise error control | Acceptable for exploratory analysis; document clearly |
| P21-6 | Block size 320 m may not fully decorrelate | Moderate | Moran's I ≈ 0.979 indicates strong autocorrelation | Test different block sizes |
| P21-7 | Earth vertical datum (NAVD88) vs. lunar/Martian datums | High | Not quantitatively resolved; may affect elevation-based features | Document as unquantified limitation; consider datum transformation |

## 6. Recommendations for Future Work

### 6.1 High Priority

1. **Quantify vertical datum differences:** Investigate methods for transforming between NAVD88, LOLA project datum, and Martian delta geoid
2. **Expand Earth coverage:** Acquire additional Earth DEM tiles from other regions (not just Death Valley / southern Arizona)
3. **Perform weight sensitivity analysis:** Test how different weight schemes affect TMSI rankings
4. **Increase bootstrap repetitions:** Consider 2,000+ repetitions for more stable CI estimation
5. **Test different block sizes:** Validate that 320 m block size is adequate for spatial autocorrelation

### 6.2 Medium Priority

6. **Consider alternative IQR pooling:** Evaluate true pooled IQR vs. max(IQR) scaling
7. **Address feature correlation:** Consider decorrelating features or adjusting weights for correlation
8. **Add more terrain features:** Consider additional features beyond slope, relief, and ruggedness
9. **Test different subsample sizes:** Validate that 100,000 sample cap doesn't affect results
10. **Document subsampling method:** Explicitly state that systematic (not random) subsampling is used

### 6.3 Low Priority

11. **Consider bootstrap-t or BCa intervals:** May be more appropriate for bounded TMSI
12. **Compare to existing methods:** Benchmark against established terrain similarity metrics in planetary science
13. **Develop formal construct validity statement:** Document what TMSI does and does not measure
14. **Add interpretive guardrails:** In candidate detail panels, explicitly state "This candidate is selected for terrain morphology comparison only. It does not imply geological equivalence."

## 7. Limitations Summary by Category

| Category | Count | Examples |
|----------|-------|----------|
| Resolution | 2 | Earth ~29.3 m native; 20 m processing grid |
| Vertical datum | 1 | NAVD88 vs. LOLA/MOLA/delta geoid |
| Coverage | 1 | Earth limited to two USGS tiles |
| Statistical | 4 | Bootstrap repetitions; seed sensitivity; weight sensitivity; IQR scaling |
| Spatial | 2 | Spatial autocorrelation; block size |
| Construct | 1 | TMSI is morphology similarity, not geological equivalence |
| Methodological | 2 | Exponential transform; systematic subsampling |

## 8. Conclusion

All limitations are explicitly documented. No limitations have been removed or weakened. The Terra Twin project maintains scientific integrity by being transparent about what TMSI can and cannot measure.