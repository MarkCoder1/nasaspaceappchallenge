# Phase 13: Independent DEM Benchmarking & Earth Integration
## Dataset Inventory

## Overview

This document inventorys all candidate elevation datasets investigated during Phase 13, along with their acquisition status, provenance, and validation state. No elevation data was fabricated; all datasets are either officially sourced, accessed via authenticated APIs, or rejected due to lack of access/verification.

## Dataset Inventory

| ID | Body | Name | Institution | Resolution | Access Status | Validation Status | Notes |
|----|------|------|-------------|-----------|---------------|------------------|-------|
| `moon_lola` | Moon | LDEM_80S_20MPP_ADJ bounded south-polar window | NASA GSFC Planetary Geodesy and Altimetry Data Archive | 20 m/pixel | DOWNLOADED | VALIDATED | Windowed subset (2048x2048 pixels, 40.96 km extent) south of 80°S. Effective resolution documented separately. Not the complete 80S-90S parent DEM. SHA256 verified. |
| `mars_jezero_ctx_dtm` | Mars | Mars 2020 Terrain Relative Navigation CTX DTM Mosaic | USGS Astrogeology Science Center / NASA MRO CTX | 20 m pixel spacing | DOWNLOADED | VALIDATED | Jezero-specific; created for terrain-relative navigation. Equirectangular CRS and MOLA control must be preserved. | 
| `earth_nasadem_hgt_v001` | Earth | NASADEM Merged DEM Global 1 arc second V001 | NASA LP DAAC / NASA JPL | 1 arc-second (~30 m nominal) | BLOCKED_BY_EARTHDATA_AUTHENTICATION | REJECTED | NASA Earthdata LP DAAC protected granules return HTTP 401 without user credentials. No local file acquired. Related to, but distinct from, SRTM. |
| `synthetic_flat_dem` | Moon | Synthetic flat DEM benchmark | Terra Twin synthetic test | N/A | ACCESSIBLE | REJECTED | Synthetic test-only dataset; does not represent real terrain. Used for software regression, not scientific inference. |
| `synthetic_gradient_dem` | Moon | Synthetic gradient DEM benchmark | Terra Twin synthetic test | N/A | ACCESSIBLE | REJECTED | Synthetic test-only dataset; does not represent real terrain. Used for software regression, not scientific inference. |

## Planet Coverage

- **Moon**: 1 validated dataset (moon_lola)
- **Mars**: 1 validated dataset (mars_jezero_ctx_dtm)
- **Earth**: 0 validated datasets (blocked by Earthdata authentication)

## Real Benchmark Findings

> **Limitation**: No independently labeled real benchmark dataset was available covering overlapping terrain across two+ DEM products. Existing datasets (moon_lola, mars_jezero_ctx_dtm) are validated observational products but cover different geographical regions. No dataset pair currently enables within-pair TMSI reproducibility testing.

## Key Constraints

1. **Earth remains PENDING** until NASA Earthdata authentication is resolved. Earth comparisons return HTTP 409.
2. **No Earth data was fabricated**. The `earth_nasadem_hgt_v001` dataset is marked REJECTED/BLOCKED, and no alternate DEM was substituted or mislabeled as NASADEM.
3. **Within-body TMSI ranges overlap between Moon (29.27–94.10) and between-body range (22.38–90.60)**. TMSI alone cannot identify planetary body.
4. **Resolution differences must be documented and evaluated** via sensitivity analysis (Phase 13 B3).

## References

- `science/datasets/registry.json` — canonical dataset registry
- `data/metadata/moon_lola.json` — LOLA dataset metadata and provenance
- `data/metadata/mars_jezero_ctx_dtm.json` — Mars CTX DTM metadata and provenance
- `data/metadata/earth_nasadem_hgt_v001.json` — NASADEM manifest (blocked acquisition)
- `docs/phase11_within_body_variability.md` — Phase 12 within-body variability findings
- `docs/phase11_tmsi_interpretation_report.md` — Phase 11 TMSI interpretation findings