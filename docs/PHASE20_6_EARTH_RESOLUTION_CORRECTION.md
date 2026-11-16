# Terra Twin — Phase 20.6: Earth Resolution Correction

## 1. Executive Summary

**CORRECTION: RESOLVED**

Earth DEM source data has approximately 29.3 m native resolution (1 arc-second USGS 3DEP). The processed data uses a 20 m processing grid via bilinear interpolation resampling. **Resampling does not create additional observational detail.** Effective measurement resolution remains constrained by the ~29.3 m source data.

This correction addresses the Phase 20.5 audit finding that the native vs. processing resolution distinction was not sufficiently prominent.

## 2. Native vs. Processing Resolution

| Attribute | Value | Source |
|-----------|-------|--------|
| Native observational resolution | ~29.3 m (1 arc-second) | USGS 3DEP 1-arc-second DEM |
| Processing grid resolution | 20 m | Bilinear interpolation resampling |
| Effective measurement resolution | ~29.3 m | Constrained by source data |
| Resampling method | Bilinear interpolation | Does not increase information |

## 3. Code Changes

### 3.1 `science/similarity/scoring/similarity.py`

Added Earth-specific limitation when either target or candidate has `body == "Earth"`:

> "Earth DEM source data has approximately 29.3 m native resolution and was resampled to a 20 m processing grid; the resampling does not create additional observational detail. Effective measurement resolution remains constrained by the ~29.3 m source data."

### 3.2 `data/processed/phase20_earth_processing_metadata.json`

Already contained the resolution disclosure, now reinforced in comparison-level limitations.

### 3.3 Comparison Output Files

All Earth comparison JSON files (`phase20_6_earth_moon_comparison.json`, `phase20_6_earth_mars_comparison.json`) now include the Earth resolution disclosure in their `limitations` array.

## 4. Required Wording

The following statement is now present in all Earth comparison limitations:

> "Earth DEM source data has approximately 29.3 m native resolution and was resampled to a 20 m processing grid. The resampling does not create additional observational detail. Effective measurement resolution remains constrained by the ~29.3 m source data."

## 5. Impact on Comparisons

| Comparison | Earth Data Resolution | Impact |
|------------|----------------------|--------|
| Moon–Mars | N/A (no Earth data) | No change |
| Earth–Moon | ~29.3 m native → 20 m grid | Resolution limitation documented |
| Earth–Mars | ~29.3 m native → 20 m grid | Resolution limitation documented |

## 6. Frontend Labeling

The ResearchWorkbench frontend displays candidate metadata including `spatial_resolution`. Candidates using USGS 3DEP data now show the resolution disclosure in their detail panels.

## 7. Classification

**Earth Resolution Correction: RESOLVED**

The native vs. processing resolution distinction is now explicit in code, metadata, comparison outputs, and candidate detail panels. Resampling is correctly described as not creating additional observational detail.