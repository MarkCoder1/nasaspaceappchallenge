# LIMITATIONS — Terra Twin

## 1. TMSI Does Not Establish Planetary Body Identity

**Finding**: Within-body TMSI ranges overlap with between-body range.

- Moon within-body TMSI: 29.27 – 94.10
- Mars within-body TMSI: 40.99 – 90.90
- Between-body TMSI: 22.38 – 90.60
- Substantial overlap confirmed: TMSI alone cannot identify planetary body

**Impact**: A TMSI value of 49.92 (the Moon–Mars baseline) falls within the overlap region. The same TMSI value could arise from within-Moon, within-Mars, or between-body comparisons. No claim should describe TMSI as a planetary classifier.

**Documented since**: Phase 12 overlap/extent analysis.

## 2. Extent-Sensitivity

**Finding**: TMSI changes materially with spatial extent.

- TMSI = 23.71 at 5.12 km extent
- TMSI = 49.92 at 10.24 km extent (full DEM extent)
- Ratio: extent doubled, TMSI more than doubled

**Impact**: TMSI values are not transferrable between different extents without re-computation. The baseline result of 49.92 applies only to the 10.24 km extent used in the primary comparison. Results at 5.12 km extent would be ~23.71, not 49.92.

**Documented since**: Phase 12 initial audit.

## 3. Window-Location-Sensitivity

**Finding**: Different window positions within the same DEM produce different TMSI values.

- Seed sensitivity: ~0.38 TMSI range across different random seeds
- Window location affects elevation distribution statistics, which TMSI quantifies

**Impact**: The 49.92 result is specific to the documented window coordinates. Re-computation is required for different window locations.

**Documented since**: Phase 13 TMSI reproducibility analysis.

## 4. Spatial Autocorrelation Not Fully Captured in Bootstrap

**Finding**: Moran's I = 0.979 indicates very strong spatial autocorrelation in elevation data.

- Standard bootstrap resampling may understate true uncertainty
- Effective number of independent samples is lower than raw window placement count
- Spatial block bootstrap would be more appropriate but is outside current methodological scope

**Impact**: The bootstrap 95% CI width of 14.56 should be interpreted as approximate; true uncertainty may be larger when spatial dependence is properly accounted for.

**Documented since**: Phase 13 TMSI reproducibility and Phase 16 scientific integrity review.

## 5. Earth Data Unavailable

**Finding**: NASA Earthdata authentication returns HTTP 401 for `earth_nasadem_hgt_v001`.

- No authenticated Earth DEM available in the repository
- No claim is made about Earth terrain similarity
- Status: PENDING until Earthdata authentication is resolved or alternative validated DEM becomes available

**Impact**: The project compares only Moon and Mars. No Earth–Moon or Earth–Mars TMSI comparisons are performed or claimed.

**Documented since**: Phase 13 earth integration analysis.

## 6. Independent DEM Benchmark Blocked

**Finding**: No pair of datasets in the repository covers overlapping terrain.

- `moon_lola` and `mars_jezero_ctx_dtm` cover different planetary regions
- An independent TMSI benchmark (same dataset, different windows with overlap) cannot be created from current data alone
- Reproducible acquisition instructions provided: a future DEM pair would need to cover overlapping terrain

**Impact**: The "Real benchmark findings" section of the BenchmarkingView notes: "No dataset pair currently enables within-pair TMSI reproducibility testing." No within-pair TMSI reproducibility result is claimed.

**Documented since**: Phase 15 initial audit.

## 7. Bootstrap CI May Not Reflect Full Uncertainty

**Finding**: Standard (random) bootstrap does not explicitly account for spatial autocorrelation (Moran's I = 0.979).

**Impact**: The 95% CI width of 14.56 is approximate. A spatial block bootstrap would likely produce wider, more accurate confidence intervals. This is a methodological limitation acknowledged in the scientific integrity review (Phase 16).

**Documented since**: Phase 16 scientific integrity review.

## 7. "HIGH Confidence" Is Qualitative, Not Statistical

**Finding**: The TMSI baseline result of 49.92 is classified as "HIGH confidence" in project documentation.

**Impact**: This label should not be interpreted as a traditional statistical confidence level (e.g., 95% probability that the true value lies in a specific interval). The "HIGH confidence" designation reflects that the result is reproducible across bootstrap replicates and seed permutations within the experimental design, not that the estimate is precise. The wide bootstrap CI (14.56) relative to the point estimate (49.92) indicates substantial uncertainty.

**Documented since**: Phase 16 scientific integrity review.

## 8. No Geological Interpretation Beyond Elevation Distribution

**Finding**: TMSI measures elevation distribution similarity, not geological equivalence.

**Impact**: A TMSI of 49.92 indicates moderate similarity in elevation histogram shapes between the compared windows. It does not imply similar geological origin, process, or feature type. Geological interpretation requires additional data and analysis beyond the scope of Terra Twin.

**Documented since**: Phase 14 research paper and Phase 16 scientific integrity review.

## 9. Results Depend on Documented Experimental Design

**Finding**: All TMSI results are specific to the documented experimental design:
- 10.24 km spatial extent
- Specific window coordinates (row/col offsets)
- No resampling applied
- Authenticated datasets only (moon_lola, mars_jezero_ctx_dtm)

**Impact**: Results cannot be generalized to different extents, window locations, resampled data, or unAuthenticated datasets without re-computation and re-documentation.

**Documented since**: Phase 14 experimental design section.

## 10. Synthetic Test Datasets Are Not for Scientific Comparison

**Finding**: Two datasets in the registry (`test_dataset_synthetic_a`, `test_dataset_synthetic_b`) have `validation_status: TEST_ONLY` and are intended for unit testing only.

**Impact**: These should not be used in any scientific comparison or result presentation. All scientific results use only `moon_lola` and `mars_jezero_ctx_dtm`, both with `validation_status: VALIDATED`.

**Documented since**: Registry schema design (Phase 13).

---

## Summary of Limitations

| Limitation | Severity | Mitigation |
|-----------|----------|------------|
| TMSI cannot establish planetary body identity | High | Explicitly documented; no claim made |
| Extent-sensitivity (23.71 @ 5.12 km → 49.92 @ 10.24 km) | High | Documented extent used; re-computation required for other extents |
| Window-location-sensitivity (~0.38 TMSI range) | Medium | Window coordinates documented; re-computation required for other windows |
| Spatial autocorrelation (Moran's I = 0.979) not fully captured in bootstrap CI | Medium | Acknowledged; CI interpreted as approximate |
| Earth data blocked (HTTP 401) | High | Explicitly documented; no Earth comparisons performed |
| Independent DEM benchmark blocked (no overlapping terrain) | High | Documented; not available in repository |
| Bootstrap CI may understate uncertainty | Medium | Acknowledged in scientific integrity review |
| "HIGH confidence" is qualitative, not statistical | Low/Medium | Clarified in documentation; CI width indicates substantial uncertainty |
| TMSI measures elevation distribution, not geological equivalence | Low | Methodological scope clearly defined |
| Results design-dependent (extent, windows, datasets) | High | All design parameters documented; re-computation required for changes |

**Overall assessment**: All limitations are explicitly documented and transparently reported. The project does not hide or suppress any unresolved blockers. Scientific claims are confined to the documented methodology and results.