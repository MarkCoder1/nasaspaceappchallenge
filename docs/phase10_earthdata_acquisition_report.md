# Phase 10 Earthdata Acquisition Report (Workstream A)

## Objective
Acquire authentic NASADEM Merged DEM Global 1 arc second V001 for the Atacama ROI (longitude -68 to -67, latitude -24 to -23) and advance Earth to VALIDATED.

## Status: BLOCKED

## Acquisition pipeline (existing, reused unchanged)
- `science/data_ingestion/cmr.py` — CMR granule discovery over collection `C2763264762-LPCLOUD`.
- `science/data_ingestion/earthdata_auth.py` — non-secret Earthdata authentication diagnostics.
- `science/data_ingestion/download_data.py` — bounded, checksummed downloader with provenance metadata.
- `science/data_ingestion/dataset_catalog.py` — `earth_nasadem_hgt_v001`, `selected=True`, `state=PENDING`, `download_url=None`.

## CMR discovery result (no auth required)
- Collection: `C2763264762-LPCLOUD` (NASADEM_HGT.001, LP DAAC).
- Live granule count discovered: 9.
- DOI: `10.5067/MEASURES/NASADEM/NASADEM_HGT.001`.
- Nominal resolution: 1 arc-second (~30 m, latitude-dependent ground spacing).
- Vertical reference: NASADEM EGM96, units meters.
- Granule data links on `https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/...` — protected, require Earthdata OAuth.

## Authentication attempt result
- Strategy: `environment`.
- `earthaccess` client: installed.
- Result: `LoginStrategyUnavailable` → `status=credentials_unavailable`.
- No Earthdata Login credentials present in environment, netrc, or repository.
- Protected granules return HTTP 401 without credentials.
- No credentials supplied, stored, or logged. No secrets committed.

## Acquisition outcome
**BLOCKED.** No NASADEM raster acquired. No local Earth file in `data/raw` or `data/processed`. Pipeline exits with `SystemExit(2)` when `diagnostic.status != "authenticated"`.

## Required action to unblock
A user with NASA Earthdata credentials must run locally:
```
cd backend && source .venv/bin/activate
PYTHONPATH=.. python -m science.data_ingestion.acquire_nasadem --login
```
then re-run the diagnostic with `--strategy netrc` or `--strategy environment` once credentials are configured. Only after `diagnostic.status == "authenticated"` can protected granules be downloaded and validated.

## Decision
Earth remains **PENDING**. No alternate DEM substituted. Earth–Moon and Earth–Mars comparisons remain disabled (HTTP 409). Moon–Mars baseline unchanged.
