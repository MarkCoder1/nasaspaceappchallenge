# Phase 13: DEM Benchmarking

## B1. Benchmark Design

For each planetary body, the benchmarking process follows these steps:

1. **Identify regions covered by at least two suitable DEM products**
   - Moon: moon_lola (VALIDATED) - currently only one validated Moon DEM available
   - Mars: mars_jezero_ctx_dtm (VALIDATED) - single localized dataset
   - Earth: No validated DEMs available (blocked by authentication)

2. **Select comparable spatial windows**
   - Moon: 40.96 km extent south of 80°S (Shackleton crater window)
   - Mars: Jezero crater region (18.211 to 18.7212 N, 77.1605 to 77.699 E)
   - Earth: No comparable windows available

3. **Establish compatible coordinate systems**
   - Moon: Moon (2015) Sphere / Ocentric / South Polar; MOON_DE421 reference frame
   - Mars: Equirectangular planetary CRS; MOLA control preserved
   - Earth: WGS84 geographic; EGM96 vertical reference (but data unavailable)

4. **Verify elevation units and vertical references**
   - Moon: elevation units in metres; reference datum defined by LOLA project
   - Mars: elevation units in metres; referenced to delta geoid
   - Earth: EGM96 geoid; elevation in metres (but data unavailable)

5. **Account for differences in spatial resolution**
   - Moon: 20 m/pixel nominal resolution
   - Mars: 20 m pixel spacing
   - Earth: 1 arc-second (~30 m nominal) (data unavailable)

6. **Identify missing-data regions**
   - Moon: 0% missing (valid_pixel_count == total_pixel_count for full window)
   - Mars: Dataset-specific (Jezero crater coverage)
   - Earth: No data available

7. **Record all preprocessing operations**
   - Documented in each dataset's preprocessing JSON file
   - Includes calibration, coregistration, resampling, and subsetting operations

8. **Calculate terrain metrics independently for each dataset**
   - Slope, local relief, TRI computed separately for moon_lola and mars_jezero_ctx_dtm
   - Results compared via the terrain_metric_benchmark module

## B2. Terrain Metrics Evaluated

The following terrain metrics were computed for benchmarking purposes:

- **Slope in degrees**: Computed using central differences with Sobel-like kernel
- **Local relief**: max(elevation) - min(elevation) within sliding window
- **Terrain Ruggedness Index (TRI)**: mean(|z_i - z_j|) over 4-neighbour pairs
- **Elevation distributions**: min, max, mean, median per dataset
- **Comparative statistics**: mean absolute difference, median absolute difference, RMS difference
- **Correlation statistics**: Pearson r and Spearman rho (-reported but not interpreted as proof of interchangeability)
- **Distribution distance**: Wasserstein distance and Kolmogorov-Smirnov statistic for elevation PDF comparison

> **Important**: A high correlation between two DEMs is not interpreted as proof that they are interchangeable. Correlation describes monotonic relationship, not agreement.

## B3. Resolution Sensitivity

### Evaluated how terrain measurements change with resolution:

- **Preserved original-resolution data**: Full-resolution DEMs kept alongside any resampled versions
- **Recorded every resampling operation**: Scale factor, interpolation method, and purpose documented
- **Documented interpolation methods**: Bilinear used as default; cubic and nearest also noted
- **Avoided implying resampling restores lost information**: Explicit statement that features lost at native resolution cannot be recovered
- **Compared at multiple defensible resolutions**: Where coverage permitted, TMSI and terrain metrics computed at native and coarser resolutions

### Key findings:
- TMSI is extent-sensitive: 23.71 at 5.12 km extent → 49.92 at full 10.24 km extent (Phase 12 finding)
- Within-body TMSI ranges overlap substantially (Moon: 29.27–94.10; Mars: 40.99–90.90)
- Between-body TMSI range: 22.38–90.60
- Resolution differences are documented but not conflated with measurement error

## B4. TMSI Reproducibility

### TMSI reproducibility across independent datasets:

- **How much scores change between DEM sources**: Documented through dataset compatibility checks
- **Whether rankings remain consistent**: Within-body and between-body TMSI ranges overlap substantially
- **Whether extent sensitivity persists**: Confirmed (Phase 12: extent changes materially affect TMSI)
- **Whether window-location sensitivity persists**: Confirmed (window position affects sampled TMSI range)
- **Whether overlap introduces similar biases**: Identical windows → TMSI = 100 (self-control); high overlap inflates similarity
- **Whether dataset resolution changes the conclusions**: Documented via resolution sensitivity analysis

### Within-body TMSI ranges (Phase 12 findings):
- Moon: 29.27 – 94.10
- Mars: 40.99 – 90.90
- Between-body: 22.38 – 90.60

### Key observation:
Within-body TMSI ranges overlap with between-body range, meaning TMSI alone cannot recover planetary body identity. This is a fundamental limitation of the metric.

## Benchmarking Engine

The Phase 13 benchmarking engine is located at `science/benchmarking/` and provides:

- `dataset_loader.py`: Load and filter datasets from registry
- `dataset_validator.py`: Validate dataset metadata and checksums
- `dem_alignment.py`: Check CRS and elevation unit compatibility
- `resolution_analysis.py`: Document resolution differences and sensitivity
- `terrain_metric_benchmark.py`: Compute and compare slope, relief, TRI metrics
- `tmsi_reproducibility.py`: Run TMSI comparisons between datasets
- `uncertainty.py`: Report four independent uncertainty categories
- `benchmark_report.py`: Export results as JSON or CSV

Every experiment has a unique identifier and configuration record for reproducibility.