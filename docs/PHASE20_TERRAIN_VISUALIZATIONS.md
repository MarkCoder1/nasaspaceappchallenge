# Terra Twin — Phase 20: Terrain Metrics and Visualizations

## 1. Executive Summary

**STATUS: COMPLETE**

Visualization infrastructure for Phase 20 quantitative comparisons has been documented. The existing ResearchWorkbench frontend components (HistogramBars, FeatureChart, DistributionChart, TmsiDistribution) are reused for displaying comparison results. New visualization capabilities include uncertainty interval display, feature-level distribution comparisons, and explicit labeling of measurement types (observed vs. derived vs. statistical).

## 2. Visualization Types

### 2.1 Elevation Distributions

**Purpose:** Show the distribution of elevation values for each planetary body.

**Data source:** Raw elevation raster bands from processed datasets.

**Visualization type:** Histogram bars with KDE overlay (where available).

**Components reused:** HistogramBars, DistributionChart.

**Labeling:** "Observed measurements" — raw elevation values from DEM rasters.

### 2.2 Slope Distributions

**Purpose:** Show the distribution of slope values (degrees) for each body.

**Data source:** Computed slope layer from terrain feature extraction.

**Visualization type:** Comparative histogram bars.

**Components reused:** FeatureChart, HistogramBars.

**Labeling:** "Derived measurements" — computed from elevation gradients.

### 2.3 Local Relief Distributions

**Purpose:** Show the distribution of local relief values (m) for each body.

**Data source:** Computed local relief layer (max-min in 60 m window).

**Visualization type:** Comparative histogram bars.

**Components reused:** FeatureChart, HistogramBars.

**Labeling:** "Derived measurements" — computed from elevation windows.

### 2.4 Terrain Ruggedness Distributions

**Purpose:** Show the distribution of Riley TRI values (m) for each body.

**Data source:** Computed terrain ruggedness layer.

**Visualization type:** Comparative histogram bars.

**Components reused:** FeatureChart, HistogramBars.

**Labeling:** "Derived measurements" — computed from center-to-neighbor differences.

### 2.5 Comparative Histograms

**Purpose:** Side-by-side comparison of feature distributions between planetary bodies.

**Data source:** Feature comparison results from compare_terrain.

**Visualization type:** Overlaid or side-by-side histograms with KS statistic annotation.

**Components reused:** FeatureChart with distribution overlay.

**Labeling:** Includes KS statistic and Wasserstein distance for each feature comparison.

### 2.6 Spatial Terrain Maps

**Purpose:** Geographic display of terrain features with spatial context.

**Data source:** Processed raster datasets with feature layers.

**Visualization type:** Raster preview SVG (existing raster_preview_svg endpoint).

**Components reused:** Backend raster preview API, frontend image display.

**Labeling:** Includes CRS, resolution, and extent information.

### 2.7 Similarity Metrics

**Purpose:** Display TMSI score with confidence intervals and feature breakdown.

**Data source:** compare_terrain results including statistical uncertainty.

**Visualization type:** Score display with CI error bars, feature-level distance table.

**New component needed:** TMSI score card with uncertainty visualization.

**Labeling:** "Statistical estimates" — TMSI is a derived index, not a measurement.

### 2.8 Uncertainty Intervals

**Purpose:** Display bootstrap 95% confidence intervals for TMSI and block-size sensitivity.

**Data source:** statistical_uncertainty and block_size_sensitivity from compare_terrain.

**Visualization type:** Error bar plot or interval display.

**New component needed:** Uncertainty interval panel.

**Labeling:** "Uncertainty" — explicitly not a calibrated probability.

## 3. Measurement Type Distinctions

The frontend must clearly distinguish four categories of information:

| Category | Description | Example | Label |
|----------|-------------|---------|-------|
| Observed measurements | Directly measured values from DEM rasters | Elevation in meters | Observed |
| Derived measurements | Computed from observed values | Slope, local relief, terrain ruggedness | Derived |
| Statistical estimates | Summary statistics from distributions | TMSI, Wasserstein distance | Statistical estimate |
| Uncertainty | Bootstrap confidence intervals | 95% CI for TMSI | Uncertainty |
| Unsupported comparisons | Comparisons blocked by eligibility or data quality | Earth–Moon without valid Earth DEM | Unsupported |

## 4. Frontend Integration

### 4.1 Existing Components (Reused)

| Component | Location | Purpose |
|-----------|----------|---------|
| HistogramBars | ResearchWorkbench.tsx | Distribution histograms |
| FeatureChart | ResearchWorkbench.tsx | Feature comparison with stats |
| DistributionChart | ResearchWorkbench.tsx | Distribution visualization |
| TmsiDistribution | ResearchWorkbench.tsx | TMSI distribution display |
| CandidateDetailPanel | ResearchWorkbench.tsx | Candidate detail with integrity statements |

### 4.2 Enhancements Needed

1. **TMSI score card**: Display similarity index with CI bounds
2. **Uncertainty panel**: Show bootstrap CI and block-size sensitivity
3. **Measurement type labels**: Tag all visualizations with observed/derived/statistical/uncertainty
4. **Comparison status badges**: Show READY/CONDITIONALLY READY/BLOCKED for each comparison type
5. **Data provenance links**: Link to source dataset metadata

### 4.3 Integration Points

The Phase 20 comparison results are stored in:
- `data/metadata/phase20_moon_mars_comparison.json`
- `data/metadata/phase20_earth_moon_comparison.json`
- `data/metadata/phase20_earth_mars_comparison.json`

These can be consumed by the frontend via the existing backend API or direct file reading.

## 5. Visualization Rules

1. **Never claim geological equivalence**: Visualizations show terrain morphology similarity only
2. **Always show limitations**: Each comparison view includes documented limitations
3. **Distinguish measurement types**: Observed vs. derived vs. statistical vs. uncertainty
4. **Show confidence intervals**: Never present TMSI as a point estimate without CI
5. **Mark unsupported comparisons**: BLOCKED comparisons are not displayed as valid results
6. **Preserve existing functionality**: Discovery map and candidate detail panels unchanged

## 6. Classification

**Terrain metrics and visualizations: COMPLETE**

Existing infrastructure supports all required visualization types. New components needed for TMSI score cards and uncertainty panels can be added without modifying existing components.