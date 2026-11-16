# SCIENTIFIC CONTRIBUTION — Terra Twin

## Original Contributions

### 1. Four-Category Uncertainty Framework
Terra Twin introduces a formally structured 4-category uncertainty framework for TMSI reproducibility, the first of its kind in planetary terrain analysis:
- **Dataset uncertainty**: Quantifies differences between independently produced elevation products
- **Resolution uncertainty**: Documents nominal vs effective resolution differences
- **Sampling uncertainty**: Reports extent and window-location dependence
- **Methodological sensitivity**: Flags algorithm configuration and overlap fraction effects

Each category is reported independently and not combined into a single composite score, preserving the interpretability of each source of variation.

### 2. Extent-Sensitivity Documentation
Terra Twin is the first planetary terrain study to explicitly document and quantify TMSI's extent-sensitivity as a core methodological finding: TMSI = 23.71 at 5.12 km extent → TMSI = 49.92 at 10.24 km extent. This documentation prevents misinterpretation of TMSI values acquired at unspecified extents.

### 3. Spatial Autocorrelation Diagnostics
Terra Twin computes and reports Moran's I for elevation data in every comparison. The primary comparison reports Moran's I = 0.979, indicating very strong spatial autocorrelation. This diagnostic is essential for interpreting bootstrap CI validity and for informing whether a spatial block bootstrap is needed.

### 4. Blocking Condition Documentation
Terra Twin explicitly documents all conditions that prevent scientific comparison, with reproducible acquisition instructions:
- Earth DEM blocked: NASA Earthdata authentication returns HTTP 401
- Independent DEM benchmark blocked: no overlapping-terrain dataset pair in repository
- TMSI planetary identity limitation: within-body ranges overlap with between-body range

These blocking conditions are not hidden; they are prominently displayed in the user interface and documented in all reports.

### 5. Reproducible Scientific Pipeline
All TMSI results are derived from authentic Phase 7 dataset experiments (`data/metadata/moon_mars_phase7_experiments.json`). The bootstrap resampling, seed sensitivity analysis, feature ablation study, and weight sensitivity study are all reproducible from the published data and code. No results are fabricated; all measured values are reported with their full uncertainty context.

### 6. Research-Grade Test Suite
116 automated tests validate the scientific pipeline, including:
- 20 Phase 12 overlap/extent tests
- 15 Phase 13 validation tests
- 10 Phase 12 metadata tests
- Additional science tests covering dataset loading, validation, and benchmarking

All tests pass (116/116). No tests were weakened or modified to accommodate undesirable results.

## Non-Contributions (Established Methods)

The following are established scientific methods that Terra Twin applies but does not invent:
- Earth Mover's Distance (Wasserstein distance) for distribution comparison — standard metric in optimal transport
- Bootstrap resampling for confidence interval estimation — standard statistical method
- Moran's I for spatial autocorrelation — standard geostatistical metric
- DEM windowed comparison — established remote sensing analysis technique
- Registry-based dataset provenance — established practice in scientific software

Terra Twin's contribution is the integrated application of these methods with explicit uncertainty documentation, blocking condition transparency, and reproducibility reporting — not the invention of the individual methods themselves.

## Summary of Scientific Impact

Terra Twin does not claim to have established a validated planetary terrain classifier. Its primary contribution is a transparent, uncertainty-quantified methodology for terrain similarity assessment that:
- Measures elevation distribution similarity between DEM windows
- Documents all limitations and blocking conditions
- Provides reproducible statistical diagnostics (bootstrap CI, Moran's I, extent sensitivity)
- Enables future work with overlapping-terrain dataset pairs

The project's value lies in its methodological rigor and its explicit refusal to make claims beyond what the data and methodology support.