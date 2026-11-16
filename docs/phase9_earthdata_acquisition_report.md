# Phase 9 Earthdata Acquisition Report

## Objective
Acquire authentic NASADEM Merged DEM Global 1 arc second V001 for the Atacama ROI near 23.0 S, 67.75 W, and move Earth to VALIDATED.

## Acquisition pipeline (existing, reused unchanged)
- `science/data_ingestion/cmr.py` — CMR granule discovery over collection `C2763264762-LPCLOUD`.
- `science/data_ingestion/earthdata_auth.py` — non-secret Earthdata authentication diagnostics (`diagnose_earthdata_auth`, `login_interactive`).
- `science/data_ingestion/download_data.py` — bounded, checksummed downloader with provenance metadata.
- `science/data_ingestion/dataset_catalog.py` — dataset records (`earth_nasadem_hgt_v001`, `selected=True`, `state=PENDING`, `download_url=None`).

## CMR discovery result (no authentication required)
- Collection: `C2763264762-LPCLOUD` (NASADEM_HGT.001, LP DAAC).
- ROI bounding box (west, south, east, north): `-68.0, -24.0, -67.0, -23.0`.
- Live granule count discovered: 9.
- Representative granules: `NASADEM_HGT_s23w067` (G2816779962-LPCLOUD), `NASADEM_HGT_s23w068`, `NASADEM_HGT_s24w068`.
- Granule data links point to `https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/...` — protected distribution requiring Earthdata OAuth.
- DOI: `10.5067/MEASURES/NASADEM/NASADEM_HGT.001`.
- Nominal resolution: 1 arc-second (~30 m, latitude-dependent ground spacing).
- Vertical reference: NASADEM EGM96, units meters.

## Authentication attempt result
- Strategy attempted: `environment`.
- `earthaccess` client: installed.
- Result: `LoginStrategyUnavailable` → `status=credentials_unavailable`.
- No Earthdata Login credentials (username/password/token/netrc) are present in the environment or repository.
- Protected granule redirects to NASA Earthdata OAuth and returns HTTP 401 without credentials.
- No credentials were supplied, stored, or logged. No authentication secrets were committed.

## Acquisition outcome
**BLOCKED.** No NASADEM raster was acquired. No local Earth file exists in `data/raw` or `data/processed`. The acquisition pipeline stops at `raise SystemExit(2)` when `diagnostic.status != "authenticated"`.

## Required action to unblock
A user with NASA Earthdata credentials must run, locally and interactively:
```
cd backend && source .venv/bin/activate
PYTHONPATH=.. python -m science.data_ingestion.acquire_nasadem --login
```
followed by re-running the diagnostic with `--strategy netrc` or `--strategy environment` once `~/.netrc` / environment credentials are configured. Only after `diagnostic.status == "authenticated"` can protected granules be downloaded.

## Decision
Earth remains **PENDING**. No alternate DEM was substituted or mislabeled as NASADEM. No Earth–Moon or Earth–Mars comparison is enabled. The Moon–Mars baseline is unchanged and remains the only validated comparison.
