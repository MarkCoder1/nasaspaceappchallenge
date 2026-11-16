# TERRA TWIN: Planetary Terrain Morphology Similarity Index

## Abstract

Terra Twin is a research platform for comparing planetary terrain morphology using the Terrain Morphology Similarity Index (TMSI). The project analyzes elevation distribution similarity between DEM (Digital Elevation Model) datasets from the Moon and Mars, using authenticated NASA and planetary datasets. The core scientific finding is that TMSI, while measurable and reproducible within a documented experimental design, does not establish planetary body identity: within-body TMSI ranges for Moon and Mars overlap with the between-body range, meaning TMSI measures terrain similarity rather than planetary identity. The baseline TMSI result for Moon–Mars comparison is 49.92 (95% bootstrap CI width: 14.56; Moran's I = 0.979 for strong spatial autocorrelation). The project explicitly documents blocking conditions: Earth DEM data are unavailable due to NASA Earthdata authentication requirements (HTTP 401), and independent DEM benchmarking is blocked by the absence of overlapping-terrain dataset pairs.

## 1. Introduction

Terra Twin addresses the scientific need to quantify and compare terrain morphology across planetary bodies. By providing a reproducible framework for terrain similarity assessment, the project enables researchers to explore questions about planetary surface evolution, geologic processes, and the extent to which morphological features are shared or unique across different worlds. The Terra Twin platform integrates dataset management, terrain feature extraction, TMSI computation, and uncertainty quantification into a single scientific research environment.

## 2. Research Question

**How can terrain morphology be quantitatively compared across planetary bodies, and what does TMSI similarity establish — or fail to establish — about planetary identity?**

## 3. Background and Related Work

Terrain similarity assessment across planetary bodies has been explored through various metrics including correlation of elevation distributions, fractal dimension comparison, and spectral analysis of terrain properties. The Terrain Morphology Similarity Index (TMSI) introduced in this project operates on the principle that statistically similar elevation distributions between two DEM windows indicate morphological similarity. However, TMSI does not inherently encode planetary identity; its value depends on dataset extent, resolution, and spatial overlap.

Previous work on interplanetary terrain comparison has typically focused on qualitative visual comparison or single-metric analysis without comprehensive uncertainty quantification. Terra Twin advances the state of the art by providing: (a) a complete 4-category uncertainty framework (dataset, resolution, sampling, methodological); (b) bootstrap resampling with documented CI width; (c) spatial autocorrelation diagnostics (Moran's I); and (d) explicit documentation of all blocking conditions and limitations.

## 4. Scientific Methodology

### 4.1 Dataset Provenance

All datasets used in Terra Twin are authenticated and their provenance is fully documented:

| Dataset | body | validation_status | access_status | Source |
|---------|------|-------------------|---------------|--------|
| `moon_lola` | Moon | VALIDATED | VALIDATED | NASA LOLA |
| `mars_jezero_ctx_dtm` | Mars | VALIDATED | VALIDATED | NASA Context DTM |
| `earth_nasadem_hgt_v001` | Earth | BLOCKED | BLOCKED_BY_EARTHDATA_AUTHENTICATION | NASA Earthdata (HTTP 401) |

Two additional synthetic test-only datasets are included for unit testing and are not used in any scientific comparison.

**Earth data status**: `earth_nasadem_hgt_v001` is blocked by NASA Earthdata authentication. HTTP 401 is returned for Earthdata API access. No alternative validated Earth DEM is available in the repository. The project explicitly states that Earth remains PENDING until authentic validated Earth data becomes available.

### 4.2 Terrain Feature Extraction

TMSI operates on elevation distribution statistics computed from DEM windows. The extraction process:

1. Load a DEM dataset from the registry
2. Define a spatial extent (km) and window location (row/col offset)
3. Compute the elevation histogram for each window
4. Compute statistical features: mean, standard deviation, skewness, and distributional overlap fraction
5. Record provenance metadata: dataset ID, body, extent, window coordinates, overlap status

No resampling was applied in the primary comparison. Both `moon_lola` and `mars_jezero_ctx_dtm` have nominal resolution of approximately 20 m/pixel, but effective resolution differs due to different acquisition geometries and processing levels.

### 4.3 TMSI Methodology

The Terrain Morphology Similarity Index (TMSI) computes a similarity score between two elevation distributions. The index ranges from 0 (no similarity) to 100 (identical distributions). The computation:

1. Extract elevation samples from two DEM windows
2. Compute the Earth Mover's Distance (Wasserstein distance) between the empirical CDFs
3. Transform the Wasserstein distance to a similarity score: TMSI = 100 - (Wasserstein distance × scaling factor)
4. Report the TMSI value alongside uncertainty categories

**TMSI is extent-sensitive**: at 5.12 km extent, TMSI ≈ 23.71; at full 10.24 km extent, TMSI ≈ 49.92. This dependence must be documented for any comparison.

### 4.4 Experimental Design

The primary experiment compares `moon_lola` vs `mars_jezero_ctx_dtm` using:

- **Spatial extent**: 10.24 km (full DEM extent)
- **Window placement**: Documented coordinates for each dataset
- **Bootstrap resampling**: 1000 iterations for 95% CI estimation
- **Spatial diagnostics**: Moran's I computed for elevation autocorrelation
- **Uncertainty reporting**: All four categories (dataset, resolution, sampling, methodological)

### 4.5 Results

| Metric | Value | Notes |
|--------|-------|-------|
| TMSI (Moon–Mars) | 49.92 | Baseline result at 10.24 km extent |
| Bootstrap 95% CI width | 14.56 | indicates substantial uncertainty |
| Seed sensitivity | ~0.38 TMSI range | across different random seeds |
| Moran's I (spatial autocorrelation) | 0.979 | strong spatial autocorrelation in elevation |
| Within-body TMSI range (Moon) | 29.27 – 94.10 | Moon-specific; window-dependent |
| Within-body TMSI range (Mars) | 40.99 – 90.90 | Mars-specific; window-dependent |
| Between-body TMSI range | 22.38 – 90.60 | spans both within-body ranges |
| Overlap (within-body ∩ between-body) | Substantial | TMSI does not identify planetary body |
| Wasserstein distance (elevation) | slope = 8.777 | local_relief = 8.539 |
| Feature ablation TMSI range | 49.146 – 50.388 | varies with algorithm configuration |
| Weight sensitivity TMSI range | 49.727 – 50.039 | varies with dataset weighting |

### 4.6 Statistical Uncertainty

Four independent uncertainty categories affect TMSI reproducibility:

1. **Dataset uncertainty**: Differences between independently produced elevation products (Moon vs Mars have different CRS, reference frames, and terrain characteristics). Reported separately; not combined with other categories.

2. **Resolution uncertainty**: Both moon_lola and mars_jezero_ctx_dtm have similar nominal resolution (20 m/pixel), but effective resolution differs. Documented via the resolution_uncertainty category. No resampling was applied in the primary comparison.

3. **Sampling uncertainty**: TMSI is extent-sensitive (5.12 km → 10.24 km changes TMSI from 23.71 to 49.92) and window-location-sensitive. Reported via the sampling_uncertainty category. Multiple window positions and extents should be sampled and reported.

4. **Methodological sensitivity**: TMSI depends on spatial extent, overlap fraction, and algorithm configuration. Reported via the methodological_sensitivity category. Materiality warnings are generated when extent < 10 km or overlap status is "high" or "identical."

### 4.7 Spatial Autocorrelation

Moran's I = 0.979 indicates very strong spatial autocorrelation in the elevation data. This means:
- Consecutive sample points are highly dependent
- The effective number of independent samples is much lower than the raw sample count
- The bootstrap CI width of 14.56 may be affected by spatial dependence
- Spatial block bootstrap would be more appropriate but is outside the current methodological scope

### 4.8 Limitations

The following limitations are explicitly documented and should be considered when interpreting results:

1. **TMSI does not establish planetary body identity**: Within-body TMSI ranges for Moon (29.27–94.10) and Mars (40.99–90.90) overlap with the between-body range (22.38–90.60). A TMSI value alone cannot determine which planetary body a terrain sample comes from.

2. **Extent-sensitivity**: TMSI changes from 23.71 at 5.12 km to 49.92 at 10.24 km. Results are not transferrable to different extents without re-computation.

3. **Window-location-sensitivity**: Different window positions within the same DEM produce different TMSI values. Seed sensitivity of ~0.38 TMSI range confirms this.

4. **Earth data unavailable**: NASA Earthdata authentication returns HTTP 401. No authenticated Earth DEM is available in the repository.

5. **Independent DEM benchmark blocked**: No pair of datasets in the repository covers overlapping terrain. `moon_lola` and `mars_jezero_ctx_dtm` cover different planetary regions. A benchmark pair would require acquiring DEMs that overlap geographically, which is outside the current repository scope.

6. **Bootstrap CI may understate uncertainty**: Standard bootstrap resampling does not fully account for spatial autocorrelation (Moran's I = 0.979). A spatial block bootstrap would produce more appropriate confidence intervals but requires methodological change.

### 4.9 Future Research

Future work addressing the documented limitations could include:

- Acquiring overlapping-terrain DEM pairs to create an independent benchmark for TMSI validation
- Implementing a spatial block bootstrap for more accurate uncertainty quantification
- Extending the uncertainty framework with additional categories (e.g., temporal stability, instrument-specific effects)
- Applying TMSI to within-body comparisons (multiple Moon windows, multiple Mars windows) to further map within-body TMSI ranges
- Resolving NASA Earthdata authentication for Earth DEM integration

### 4.10 Conclusion

Terra Twin provides a reproducible framework for planetary terrain morphology comparison using the TMSI index. The baseline result — TMSI = 49.92 for the Moon–Mars comparison at 10.24 km extent — is mathematically well-defined and reproducible within the experimental design. However, the fundamental limitation that within-body TMSI ranges overlap with between-body ranges means that TMSI does not establish planetary body identity. The project's primary contribution is not a planetary classifier but rather a transparent, uncertainty-quantified methodology for terrain similarity assessment, with all blocking conditions, limitations, and reproducibility instructions explicitly documented.

## 5. References

- Phase 12 Initial Audit (docs/phase12_initial_audit.md). Overlap classification and extent diagnostics.
- Phase 13 Final Report (docs/phase13_final_report.md). Dataset registry, benchmarking engine, uncertainty framework.
- Phase 14 Initial Audit (docs/phase14_initial_audit.md). Scientific validation and TMSI reproducibility.
- Phase 15 Final Report (docs/PHASE15_FINAL_REPORT.md). Code quality fixes, finalization.
- TMSI Reproducibility (docs/phase13_tmsi_reproducibility.md). Bootstrap CI, seed sensitivity, Moran's I.
- Uncertainty Analysis (docs/phase13_uncertainty_analysis.md). Four-category uncertainty framework.
- Research Paper (docs/Phase_14_Research_Paper.md). Phase 14 draft.

## Appendix: Dataset Registry (registry.json Summary)

```json
{
  "datasets": [
    {
      "id": "moon_lola",
      "name": "Moon LOLA DEM",
      "body": "Moon",
      "validation_status": "VALIDATED",
      "access_status": "DOWNLOADED",
      "nominal_resolution_m": 20,
      "kind": "elevation"
    },
    {
      "id": "mars_jezero_ctx_dtm",
      "name": "Mars Jezero Crater DTM",
      "body": "Mars",
      "validation_status": "VALIDATED",
      "access_status": "DOWNLOADED",
      "nominal_resolution_m": 20,
      "kind": "elevation"
    },
    {
      "id": "earth_nasadem_hgt_v001",
      "name": "NASADEM HGT v001",
      "body": "Earth",
      "validation_status": "REJECTED",
      "access_status": "BLOCKED_BY_EARTHDATA_AUTHENTICATION",
      "nominal_resolution_m": 30,
      "kind": "elevation"
    },
    {
      "id": "test_dataset_synthetic_a",
      "name": "Synthetic Test Dataset A",
      "body": "—",
      "validation_status": "TEST_ONLY",
      "access_status": "DOWNLOADED",
      "nominal_resolution_m": "N/A",
      "kind": "elevation"
    },
    {
      "id": "test_dataset_synthetic_b",
      "name": "Synthetic Test Dataset B",
      "body": "—",
      "validation_status": "TEST_ONLY",
      "access_status": "DOWNLOADED",
      "nominal_resolution_m": "N/A",
      "kind": "elevation"
    }
  ],
  "planet_coverage": {
    "Moon": 1,
    "Mars": 1
  },
  "real_benchmark_findings": [
    "No dataset pair currently enables within-pair TMSI reproducibility testing. Existing validated datasets (moon_lola, mars_jezero_ctx_dtm) cover different geographical regions."
  ],
  "limitation": "No independently labeled real benchmark dataset was available in the verified repository. Earth data blocked by NASA Earthdata authentication (HTTP 401). Independent DEM benchmark blocked by absence of overlapping-terrain dataset pairs."
}
```