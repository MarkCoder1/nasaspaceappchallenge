# Phase 10 Earth Validation Report (Workstream B)

## Status: BLOCKED (Earth remains PENDING)

## Reason
No authentic NASADEM raster has been acquired because Earthdata authentication is unavailable (`LoginStrategyUnavailable`; no credentials; protected granules return HTTP 401). Without a local Earth file, no validation gates can be executed.

## Validation gates (all pending)
| Gate | Required | Status |
|---|---|---|
| File integrity (opens, dimensions, checksum, no corruption) | local `.tif` | BLOCKED — no file |
| Geospatial integrity (CRS, units, bounds, pixel spacing, elevation units, vertical datum) | local `.tif` + metadata | BLOCKED |
| Data quality (no-data values, valid coverage, missing-data patterns, elevation range, artifacts) | local `.tif` | BLOCKED |
| Resolution assessment (nominal vs effective spacing, resampling history, comparability) | local `.tif` + ancillary | BLOCKED |
| Validation gate passed → Earth enters `DATASET_REGISTRY` as VALIDATED | pipeline | BLOCKED |

## What is documented (provenance only, not an observation)
- `data/metadata/earth_nasadem_hgt_v001.json`: `state=PENDING`, DOI `10.5067/MEASURES/NASADEM/NASADEM_HGT.001`, nominal 1 arc-second (~30 m), EGM96 vertical, meters, Atacama ROI.
- `data/metadata/earth_nasadem_cmr.json`: 9 granules identified, all protected.
- `data/metadata/earthdata_authentication_diagnostic.json`: `status=credentials_unavailable`.

## Decision
Earth remains **PENDING** until all validation gates pass. No manual registry status change. No Earth comparison enabled.
