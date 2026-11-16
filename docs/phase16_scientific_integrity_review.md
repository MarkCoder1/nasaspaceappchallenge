# Phase 16: Scientific Integrity Review

## TMSI Methodology Integrity Assessment

This review examines the Terrain Morphology Similarity Index (TMSI) methodology and associated statistical claims against the Phase 1–15 audit findings. No methodological changes are proposed; all findings are reported as-is with appropriate caveats.

### Baseline Results (Phase 13–14)

| Metric | Value | Source |
|--------|-------|--------|
| Moon–Mars baseline TMSI | 49.92285382858792 | Phase 14 analysis using authentic Phase 7 data |
| Bootstrap 95% CI width | 14.56 | Phase 14 reproducibility analysis |
| Seed sensitivity | ~0.38 TMSI range | Phase 14 bootstrap replication across random seeds |
| Moran's I (spatial autocorrelation) | 0.979 | Phase 13 spatial diagnostics |
| Within-body TMSI range (Moon) | 29.27 – 94.10 | Phase 12 overlap/extent analysis |
| Within-body TMSI range (Mars) | 40.99 – 90.90 | Phase 12 overlap/extent analysis |
| Between-body TMSI range | 22.38 – 90.60 | Phase 12 overlap/extent analysis |
| TMSI extent sensitivity | 23.71 @ 5.12 km → 49.92 @ 10.24 km | Phase 12 finding |

---

### A. Bootstrap Method and Spatial Dependence

**Finding**: The bootstrap 95% CI width is 14.56. The bootstrap resamples window placements within the available DEM extent.

**Assessment**: The standard (random) bootstrap does not explicitly account for spatial autocorrelation. However, the high Moran's I = 0.979 indicates that elevation values are strongly spatially correlated, which means:
- Consecutive window placements are not independent
- The effective number of independent samples is lower than the raw number of window placements
- The bootstrap CI width of 14.56 may be **understating** true uncertainty if spatial dependence is ignored

**Documentation**: The Phase 13–14 reports note seed sensitivity (~0.38 TMSI range) and window-location dependence as separate uncertainty categories. The bootstrap is reported alongside these categories, not as a standalone confidence interval. The 14.56 CI width should be interpreted in conjunction with the other uncertainty categories, particularly sampling uncertainty and methodological sensitivity.

**Conclusion**: The bootstrap method provides an approximate CI but does not fully account for spatial dependence. A spatial block bootstrap would be more appropriate, but the existing method is documented and reported with appropriate caveats. No change to the methodology is proposed.

---

### B. Spatial Block Bootstrap Assessment

**Finding**: Given Moran's I = 0.979, elevation values within each DEM are extremely strongly spatially autocorrelated.

**Assessment**: A spatial block bootstrap would partition the DEM into spatial blocks smaller than the autocorrelation range, then resample blocks rather than individual windows. This would:
- Reduce the effective number of resampling units
- Typically produce wider confidence intervals that more accurately reflect spatial dependence
- Require specification of block size relative to the autocorrelation range

**Constraint**: The existing Phase 13–14 analysis used a standard bootstrap across window placements. Converting to a spatial block bootstrap would be a methodological change requiring re-analysis and documentation. Given the Phase 16 rule "Do not change the scientific methodology without documenting and justifying the change," no such change is proposed.

**Conclusion**: A spatial block bootstrap would likely produce more appropriate uncertainty quantification, but converting the methodology is outside the scope of this Phase 16 workstream. The existing bootstrap results are reported with explicit acknowledgement of spatial autocorrelation (Moran's I = 0.979) as a limiting factor.

---

### C. Confidence Classification Justification

**Finding**: The TMSI baseline result of 49.92 is classified as "HIGH confidence."

**Assessment**: The "HIGH confidence" classification should be understood in context:
- The bootstrap 95% CI width of 14.56 means the true TMSI could reasonably be anywhere in the range approximately 49.92 ± 7.28 (approximately 42.64 to 57.20)
- This wide CI reflects both sampling variability and the inherent properties of the TMSI index (extent-sensitivity, spatial autocorrelation)
- The classification is not a statistical confidence level in the traditional sense; it is a qualitative assessment that the result is reproducible across bootstrap replicates and seed permutations
- The large CI width (14.56) relative to the point estimate (49.92) indicates substantial uncertainty

**Conclusion**: The "HIGH confidence" label should not be interpreted as a strong statistical guarantee. It reflects that the result is reproducible and meaningful within the project's experimental design, not that the estimate is precise. The wide bootstrap CI (14.56) and the overlap of within-body/between-body TMSI ranges are more informative than the confidence label.

---

### D. TMSI: Terrain Similarity vs. Planetary Identity

**Finding**: TMSI = 49.92 for the Moon–Mars comparison. Within-body ranges (Moon: 29.27–94.10, Mars: 40.99–90.90) overlap with the between-body range (22.38–90.60).

**Assessment**: This is the most critical methodological finding:

1. **TMSI measures terrain similarity, not planetary identity**. The overlap of within-body and between-body ranges means that a TMSI value alone cannot determine which planetary body a terrain sample comes from.

2. **Moon–Mars TMSI = 49.92 falls within the overlap region**. The value 49.92 is:
   - Above the between-body minimum (22.38)
   - Below the within-body maxima for both Moon (94.10) and Mars (90.90)
   - Within the overlap interval shared by both within-body ranges

3. **Implication**: The Moon–Mars TMSI of 49.92 does not scientifically establish "similarity between Moon and Mars terrain" in a planetary-identity sense. It establishes a terrain similarity metric for the specific windows compared, with the fundamental limitation that the same TMSI value could arise from within-Moon, within-Mars, or between-body comparisons.

4. **No claim made that TMSI classifies planetary body**. The documentation explicitly states: "TMSI does not identify planetary body" and "Within-body TMSI ranges overlap with between-body range: TMSI cannot recover planetary body."

**Conclusion**: TMSI measures elevation distribution similarity between terrain windows. The 49.92 result is a terrain similarity metric with the documented limitation that it does not establish planetary identity. No claim should describe TMSI as a planetary classifier.

---

### E. Robustness to Sampling Design and Geographic Window Selection

**Finding**: TMSI is extent-sensitive (23.71 @ 5.12 km → 49.92 at 10.24 km) and window-location-sensitive.

**Assessment**: The 49.92 result is not robust to the choice of geographic window in the following senses:

1. **Extent dependence**: Halving the extent from 10.24 km to 5.12 km changes TMSI from 49.92 to 23.71 (a factor of ~2.1). The result is highly extent-dependent.

2. **Window location**: Different window positions within the same DEM produce different TMSI values. The seed sensitivity of ~0.38 TMSI range confirms this.

3. **Overlap status**: Identical windows give TMSI = 100; high overlap inflates TMSI (78.6–88.0); no overlap changes the interpretive framework.

4. **Robustness within design**: Within the Phase 13–14 experimental design (full 10.24 km extent, documented window coordinates), the result is reproducible (bootstrap CI 14.56 width across seeds). But the result does not generalize to different extents or window locations without re-computation.

**Conclusion**: The 49.92 result is valid within the documented experimental design (10.24 km extent, specific window coordinates). It is not transferable to different extents or window locations without re-computation and reporting. The extent-sensitivity and window-location-sensitivity are documented limitations, not flaws.

---

### Summary of Integrity Assessment

| Issue | Status | Mitigation |
|-------|--------|------------|
| Bootstrap accounts for spatial dependence | Not fully (Moran's I = 0.979) | Reported with caveats; spatial block bootstrap would be more appropriate but outside scope |
| "HIGH confidence" classification | Qualitative, not statistical | Interpreted alongside CI width (14.56) and overlap limitations |
| TMSI as planetary classifier | ❌ Cannot establish identity | Documentation explicitly states this limitation; no claim to the contrary |
| 49.92 robustness to window/extent | Not robust; extent-sensitive | Design-dependent; documented for the specific 10.24 km extent used |
| Methodological changes | ❌ Not proposed per Phase 16 rules | All findings reported as-documented |

**Final Determination**: The TMSI methodology and results are scientifically valid within their documented scope. The limitations (extent-sensitivity, overlap of within-body/between-body ranges, inability to identify planetary body, spatial autocorrelation not fully captured in bootstrap) are explicitly documented and reported. No fabrication or unsupported claims are present.