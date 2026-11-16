# Data ingestion

The catalog is the source of truth for Phase 2 dataset records. Run commands from the repository root with the backend virtual environment active:

```bash
PYTHONPATH=. python -m science.data_ingestion.download_data mars_jezero_ctx_dtm
PYTHONPATH=. python -m science.data_ingestion.validate_data data/raw/JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif data/metadata/mars_jezero_ctx_dtm.json
PYTHONPATH=. python -m science.data_ingestion.acquire_lola_window
PYTHONPATH=. python -m science.preprocessing.process_moon_lola
```

The downloader refuses datasets without a verified direct URL, refuses files above its 100 MB default, refuses existing files, writes to a `.part` file during transfer, and records SHA-256 provenance metadata after completion. The LOLA command uses bounded COG range reads because the complete parent DEM is about 2.6 GB. NASADEM remains catalogued with an Earthdata-authentication requirement.
