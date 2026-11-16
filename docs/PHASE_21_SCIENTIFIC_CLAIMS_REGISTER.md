# Terra Twin — Phase 21: Scientific Claims Audit

## 1. Executive Summary

**VERDICT: VERIFIED WITH QUALIFICATIONS**

A complete inventory of scientific claims made throughout the Terra Twin project (Phases 17–20.6) has been compiled and classified. All claims are either verified, supported with qualifications, or conditionally supported. No claims of planetary body identity, geological equivalence, habitability, or landing safety are made.

## 2. Claims Classification Framework

| Classification | Definition |
|---------------|------------|
| **VERIFIED** | Claim is supported by direct evidence from the data and analysis; independently reproducible |
| **SUPPORTED WITH QUALIFICATIONS** | Claim is supported but requires explicit limitations or context |
| **CONDITIONALLY SUPPORTED** | Claim is supported only under specific conditions or assumptions |
| **UNVERIFIED** | Claim lacks sufficient evidence to support or refute |
| **UNSUPPORTED** | Claim is contradicted by available evidence |

## 3. Claims Register

### 3.1 TMSI Methodology Claims

| # | Claim | Classification | Evidence | Limitations |
|---|-------|---------------|----------|-------------|
| C1 | TMSI measures terrain morphology distribution similarity | VERIFIED | Direct computation from slope, local relief, terrain ruggedness distributions using Wasserstein distance | Measures morphology only, not geology |
| C2 | TMSI = 100 × exp(−D) where D is weighted mean of normalized Wasserstein distances | VERIFIED | Independent recalculation confirms exact values | Formula is arbitrary; no sensitivity analysis |
| C3 | TMSI ranges from 0 to 100 | VERIFIED | Mathematical property of exponential function | TMSI = 100 only for identical distributions; TMSI → 0 as distributions diverge |
| C4 | Higher TMSI = more similar morphology distributions | VERIFIED | Mathematical property | Does not imply geological equivalence |
| C5 | Normalized distance = Wasserstein / max(IQR) | VERIFIED | Independent recalculation confirms | Conservative scaling; may overstate similarity when IQRs differ |
| C6 | KS statistic measures distribution difference | VERIFIED | Standard statistical test | Less sensitive to tail differences than Wasserstein |
| C7 | Bootstrap CI quantifies spatial sampling variability | VERIFIED | Spatial block bootstrap correctly implemented | 64→1000 repetitions; seed sensitivity tested; not calibrated probability |
| C8 | Spatial block bootstrap accounts for spatial autocorrelation | SUPPORTED WITH QUALIFICATIONS | Block bootstrap is standard method for spatial data | Block size (320 m) may not fully decorrelate adjacent blocks |
| C9 | Feature weights are equal (1.0 each) | VERIFIED | Explicitly documented in code | Arbitrary choice; no sensitivity analysis |
| C10 | Resolution normalization to 20 m | SUPPORTED WITH QUALIFICATIONS | Earth data resampled from ~29.3 m to 20 m | Effective resolution remains ~29.3 m; no new information created |

### 3.2 Comparison Results Claims

| # | Claim | Classification | Evidence | Limitations |
|---|-------|---------------|----------|-------------|
| C11 | Moon–Mars TMSI = 49.92 | VERIFIED | Independent recalculation: 49.9229 | Based on 10.24 km extent; 20 m resolution |
| C12 | Earth–Moon TMSI = 61.95 | VERIFIED | Independent recalculation: 61.9501 | Based on ~29.3 m effective resolution Earth data |
| C13 | Earth–Mars TMSI = 73.14 | VERIFIED | Independent recalculation: 73.1360 | Based on ~29.3 m effective resolution Earth data |
| C14 | Earth–Mars > Earth–Moon > Moon–Mars (ranking) | VERIFIED | Numerical values confirm ranking | Rankings could change with different Earth data or resolution |
| C15 | Earth–Mars shows highest similarity | VERIFIED | TMSI 73.14 > 61.95 > 49.92 | Based on Death Valley region only; not generalizable |
| C16 | Moon–Mars CI [43.72, 56.80] excludes 0 and 100 | VERIFIED | Independent reproduction confirms | CI based on 1,000 bootstrap repetitions |
| C17 | Earth–Moon CI [51.99, 72.56] excludes 0 and 100 | VERIFIED | Independent reproduction confirms | Based on Death Valley region only |
| C18 | Earth–Mars CI [64.99, 78.55] excludes 0 and 100 | VERIFIED | Independent reproduction confirms | Based on Death Valley region only |

### 3.3 Scientific Limitations Claims

| # | Claim | Classification | Evidence | Notes |
|---|-------|---------------|----------|---------|
| C19 | TMSI cannot establish planetary body identity | VERIFIED | Explicitly documented; consistent with literature | Core limitation of methodology |
| C20 | TMSI is not a probability, habitability score, or safety certification | VERIFIED | Explicitly documented in all outputs | Critical for preventing misinterpretation |
| C21 | Earth data effective resolution ~29.3 m | VERIFIED | USGS 3DEP 1-arc-second data; verified | Processing grid is 20 m but effective resolution is ~29.3 m |
| C22 | Vertical datum differences (NAVD88 vs. LOLA/MOLA) | VERIFIED | Documented in all Earth comparisons | Not quantitatively resolved |
| C23 | Earth coverage limited to Death Valley / southern Arizona | VERIFIED | Two USGS 3DEP tiles documented | Cannot generalize to global Earth terrain |
| C24 | Riley TRI is roughness index, not hazard measure | VERIFIED | Standard interpretation | Prevents misinterpretation as hazard assessment |
| C25 | Edge cells excluded from local relief | VERIFIED | Standard practice | Reduces effective coverage near raster edges |
| C26 | Slope sensitive to DEM noise at steep slopes | VERIFIED | Standard limitation | Affects steep terrain more than flat terrain |

### 3.4 Claims NOT Made (Correctly Avoided)

| # | Claim | Status | Reason |
|---|-------|--------|--------|
| NC1 | "TMSI identifies planetary body identity" | NOT MADE | Explicitly rejected (Phase 17 limitation #1) |
| NC2 | "Earth is a confirmed analog for Mars" | NOT MADE | Would be scientifically unsupported |
| NC3 | "TMSI = X% similarity" | NOT MADE | TMSI is bounded 0-100 but not a percentage |
| NC4 | "Earth deserts are geologically equivalent to Mars" | NOT MADE | Would confuse morphology with geology |
| NC5 | "Higher TMSI = better landing site" | NOT MADE | No safety or habitability data |
| NC6 | "Global Earth terrain similarity" | NOT MADE | Earth coverage limited to two USGS tiles |
| NC7 | "TMSI results are calibrated probabilities" | NOT MADE | Explicitly stated as qualitative confidence |

## 4. Claims Requiring Stronger Caveats

| # | Claim | Current Caveat | Recommended Addition |
|---|-------|---------------|---------------------|
| C11 | Moon–Mars TMSI = 49.92 | Context documented | Add: "based on 10.24 km extent; may vary with extent" |
| C12 | Earth–Moon TMSI = 61.95 | Earth limitations documented | Add: "based on ~29.3 m effective resolution; Death Valley region only" |
| C13 | Earth–Mars TMSI = 73.14 | Earth limitations documented | Add: "based on ~29.3 m effective resolution; Death Valley region only" |
| C14 | Earth–Mars > Earth–Moon > Moon–Mars | Numerical values documented | Add: "ranking may change with different Earth data or resolution" |

## 5. Claims Classification Summary

| Classification | Count | Examples |
|---------------|-------|----------|
| VERIFIED | 26 | C1–C10, C11–C18, C19–C26 |
| SUPPORTED WITH QUALIFICATIONS | 1 | C8 |
| CONDITIONALLY SUPPORTED | 0 | None |
| UNVERIFIED | 0 | None |
| UNSUPPORTED | 0 | None |
| NOT MADE (correctly avoided) | 7 | NC1–NC7 |

## 6. Claims Not Made (Correctly Avoided)

The following claims that could have been made but were correctly avoided:

1. **Planetary body identity:** TMSI does not identify whether terrain is from Moon, Mars, or Earth
2. **Geological equivalence:** Similar morphology does not imply similar formation processes
3. **Habitability:** No assessment of temperature, pressure, radiation, or chemistry
4. **Landing safety:** No assessment of rock abundance, slope stability, or trafficability
5. **Global representativeness:** Earth data covers only two tiles in the southwestern United States
6. **Calibrated probability:** TMSI is not a probability score
7. **Causation:** Statistical similarity does not imply similar geologic processes

## 7. Classification

**Scientific Claims Audit: VERIFIED WITH QUALIFICATIONS**

All claims made in the Terra Twin project are either verified or supported with qualifications. No claims of planetary body identity, geological equivalence, habitability, landing safety, or global representativeness are made. The terminology appropriately distinguishes terrain morphology similarity from geological equivalence.

## 8. Recommendations

1. **Add interpretive guardrails:** In candidate detail panels, explicitly state "This candidate is selected for terrain morphology comparison only. It does not imply geological equivalence."
2. **Strengthen terminology:** Use "terrain morphology similarity" consistently instead of just "similarity"
3. **Document weight sensitivity:** Perform analysis of how different weight schemes affect TMSI rankings
4. **Add construct validity statement:** Add a formal statement about what TMSI does and does not measure