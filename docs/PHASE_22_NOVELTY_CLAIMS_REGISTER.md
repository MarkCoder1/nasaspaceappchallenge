# Terra Twin — Phase 22: Novelty Claims Register

## 1. Executive Summary

**VERDICT: COMPLETE**

This document presents a formal novelty claim register for the Terra Twin Terrain Morphology Similarity Index (TMSI). Each novelty claim is classified as:

- **ORIGINAL CONTRIBUTION** — Novel contribution not found in prior art
- **NOVEL APPLICATION** — Established method applied to a new domain
- **METHODOLOGICAL ADAPTATION** — Established method adapted to a new context
- **ESTABLISHED TECHNIQUE** — Standard method from literature
- **INSUFFICIENT EVIDENCE** — Not enough evidence to classify

## 2. Novelty Claims Register

| Claim ID | Claim | Classification | Evidence of Distinction | Supporting Experiment | Confidence | Remaining Uncertainty |
|----------|-------|---------------|------------------------|----------------------|------------|----------------------|
| NC-01 | Combination of Wasserstein distance + KS statistic + pooled IQR normalization into composite terrain similarity index | NOVEL APPLICATION | Not found in 20-publication prior art review; no single publication combines all three distance metrics into a composite terrain similarity index | PHASE_22_PRIOR_ART_REVIEW.md; PHASE_22_METHOD_COMPARISON_MATRIX.md | MEDIUM | Individual components are established; combination may exist in unpublished work |
| C2 | Spatial block bootstrap for terrain feature comparison uncertainty quantification | NOVEL APPLICATION | Spatial block bootstrap is established (Politis & Romano 1994; Politis et al. 1999) but not documented for planetary terrain comparison | PHASE_22_PRIOR_ART_REVIEW.md | MEDIUM | Applied to planetary terrain comparison for first time in Terra Twin |
| C3 | Explicit documentation of Earth DEM resolution limitations (~29.3 m native vs. 20 m processing grid) | NOVEL APPLICATION | Not found in prior art review; most planetary DEM studies do not document resolution limitations explicitly | PHASE_22_DATA_PROVENANCE_AUDIT.md | HIGH | Limited to two USGS 3DEP tiles; may not generalize |
| C4 | Explicit documentation of vertical datum differences (NAVD88 vs. LOLA/MOLA/delta geoid) | NOVEL APPLICATION | Not found in prior art review; most planetary DEM studies do not document vertical datum differences explicitly | PHASE_22_GEOSPATIAL_VALIDITY_AUDIT.md | HIGH | Unquantified; no transformation applied |
| C5 | End-to-end pipeline for cross-planetary terrain morphology comparison | NOVEL APPLICATION | Not found in prior art review; no single publication combines all elements into a complete pipeline | PHASE_22_BASELINE_REPORT.md | MEDIUM | Individual components are established; pipeline integration is novel |
| C6 | Equal feature weights (1.0 each) | ESTABLISHED TECHNIQUE | Equal weighting is standard practice in composite indices | PHASE_22_ABLATION_STUDY.md | HIGH | Arbitrary; no sensitivity analysis |
| C7 | max(IQR) scaling for normalization | METHODOLOGICAL ADAPTATION | max(IQR) rather than true pooled IQR is a conservative but undocumented choice | PHASE_22_MATHEMATICAL_REVIEW.md | MEDIUM | Not justified in documentation; may overstate similarity when IQRs differ |
| C8 | Exponential transform TMSI = 100 × exp(−D) | METHODOLOGICAL ADAPTATION | Exponential decay is common in similarity indices; no alternative forms tested | PHASE_22_MATHEMATICAL_REVIEW.md | MEDIUM | Arbitrary choice; no sensitivity analysis |
| C9 | Spatial block bootstrap with 1,000 repetitions | NOVEL APPLICATION | Bootstrap resampling is established (Efron 1979); spatial block bootstrap is established (Politis & Romano 1994); application to planetary terrain comparison with 1,000 repetitions is novel | PHASE_22_STATISTICAL_ROBUSTNESS_REPORT.md | MEDIUM | 1,000 repetitions is moderate; seed sensitivity tested |
| C10 | Seed sensitivity analysis (5 seeds) | METHODOLOGICAL ADAPTATION | Seed sensitivity analysis is established in computational statistics; application to planetary terrain comparison is novel | PHASE_22_STATISTICAL_ROBUSTNESS_REPORT.md | MEDIUM | 5 seeds is moderate; more seeds would provide stronger evidence |

## 3. Classification Summary

| Classification | Count | Claims |
|---------------|-------|--------|
| ORIGINAL CONTRIBUTION | 0 | None |
| NOVEL APPLICATION | 5 | C1, C2, C3, C4, C5 |
| METHODOLOGICAL ADAPTATION | 3 | C7, C8, C9 |
| ESTABLISHED TECHNIQUE | 1 | C6 |
| INSUFFICIENT EVIDENCE | 0 | None |

## 4. Detailed Claim Assessments

### C1: Combination of Wasserstein distance + KS statistic + pooled IQR normalization into composite terrain similarity index

**Classification:** NOVEL APPLICATION

**Evidence:** Prior art review of 20 publications found no single publication that combines Wasserstein distance, KS statistic, and pooled IQR normalization into a composite terrain similarity index. Individual components are established (Villani 2009; Kolmogorov 1933; Smirnov 1939), but their combination into TMSI is novel.

**Supporting Experiment:** Phase 22 Method Comparison Matrix (PHASE_22_METHOD_COMPARISON_MATRIX.md) compares TMSI against KS-only, Wasserstein-only, multivariate statistical, morphometric classification, and composite terrain similarity index approaches.

**Confidence:** MEDIUM — Individual components are established; combination may exist in unpublished work.

### C2: Spatial block bootstrap for terrain feature comparison uncertainty quantification

**Classification:** NOVEL APPLICATION

**Evidence:** Spatial block bootstrap is established (Politis & Romano 1994; Politis et al. 1999), but application to planetary terrain comparison is novel. Prior art review found no publication applying spatial block bootstrap to cross-planetary terrain comparison.

**Supporting Experiment:** Phase 22 Statistical Robustness Report (PHASE_21_STATISTICAL_ROBUSTNESS_REPORT.md) documents bootstrap implementation and sensitivity analysis.

**Confidence:** MEDIUM — Applied to planetary terrain comparison for first time in Terra Twin.

### C3: Explicit documentation of Earth DEM resolution limitations (~29.3 m native vs. 20 m processing grid)

**Classification:** NOVEL APPLICATION

**Evidence:** Prior art review found no publication that explicitly documents Earth DEM resolution limitations (29.3 m native vs. 20 m processing grid) in planetary terrain comparison. Most planetary DEM studies do not document resolution limitations explicitly.

**Supporting Experiment:** Phase 22 Geographic Validity Audit (PHASE_21_GEOSPATIAL_VALIDITY_AUDIT.md) documents resolution limitations.

**Confidence:** HIGH — Limited to two USGS 3DEP tiles; may not generalize to other Earth regions or DEM products.

### C4: Explicit documentation of vertical datum differences (NAVD88 vs. LOLA/MOLA/delta geoid)

**Classification:** NOVEL APPLICATION

**Evidence:** Prior art review found no publication that explicitly documents vertical datum differences (NAVD88 vs. LOLA/MOLA/delta geoid) in planetary terrain comparison. Most planetary DEM studies do not document vertical datum differences explicitly.

**Supporting Experiment:** Phase 22 Geographic Validity Audit (PHASE_21_GEOSPATIAL_VALIDITY_AUDIT.md) documents vertical datum differences.

**Confidence:** HIGH — Unquantified; no transformation applied; may affect elevation-based feature comparisons.

### C5: End-to-end pipeline for cross-planetary terrain morphology comparison

**Classification:** NOVEL APPLICATION

**Evidence:** Prior art review found no single publication that combines all elements (data acquisition, preprocessing, feature extraction, distribution comparison, uncertainty quantification, limitation documentation) into a complete pipeline for cross-planetary terrain morphology comparison.

**Supporting Experiment:** Phase 22 Baseline Report (PHASE_22_BASELINE_REPORT.md) documents complete pipeline.

**Confidence:** MEDIUM — Individual components are established; pipeline integration is novel; limited to three planetary bodies (Moon, Mars, Earth).

## 6. Claims Not Supported

| Claim | Reason for Exclusion |
|-------|---------------------|
| TMSI is a novel mathematical formula | All components (Wasserstein, KS, bootstrap, exponential transform) are established techniques |
| TMSI measures geological similarity | TMSI measures terrain morphology distribution similarity, not geological equivalence |
| TMSI identifies planetary body identity | Explicitly rejected as a limitation (Phase 17 limitation #1) |
| TMSI is better than existing methods | No benchmarking against established methods performed; no evidence of superiority |
| TMSI can be used for landing site certification | TMSI does not assess safety, trafficability, or hazard |

## 7. Overall Novelty Assessment

**The primary contribution of Terra Twin is a NOVEL APPLICATION** of established statistical methods (Wasserstein distance, KS statistic, spatial block bootstrap) to cross-planetary terrain morphology comparison, with explicit documentation of limitations (resolution, vertical datum, coverage).

**Not novel:**
- Individual statistical methods (all established in literature)
- Feature extraction (slope, relief, ruggedness) (established in planetary geomorphometry)
- Equal feature weights (standard practice)
- Exponential transform (common in similarity indices)

**Novel application:**
- Combination of Wasserstein + KS + IQR normalization into composite terrain similarity index
- Spatial block bootstrap for terrain feature comparison uncertainty quantification
- Explicit documentation of Earth DEM resolution limitations
- Explicit documentation of vertical datum differences
- End-to-end pipeline for cross-planetary terrain morphology comparison

## 8. Recommendations

1. **Document prior art explicitly** in any publication to acknowledge existing methods
2. **Highlight the combination** of Wasserstein + KS + bootstrap as the potential novel application
3. **Benchmark against established methods** from the literature to demonstrate added value
4. **Document vertical datum and resolution limitations** explicitly, as these are not commonly addressed in planetary terrain comparison literature
5. **Avoid overstating novelty** — TMSI combines established methods; it does not invent new statistical techniques