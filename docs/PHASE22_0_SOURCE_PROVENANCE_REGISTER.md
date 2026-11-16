# Terra Twin — Phase 22.0 Audit: Source & Provenance Register

**Date:** 2026-11-15 · Every raster and every NASA dataset identifier referenced by Terra Twin, with status as of this audit. Nothing here authorizes downloads.

## Rasters & acquisition provenance

| ID | Product | Institution | Public source URL (as recorded) | Access mode | Local file | Status 2026-11-15 |
|----|---------|-------------|-------------------------------|-------------|------------|--------------------|
| `moon_lola` | LDEM_80S_20MPP_ADJ (bounded south-polar window) | NASA GSFC Planetary Geodesy and Altimetry Data Archive (PGDA) | https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF | Windowed range-read of COG (parent not downloaded) | `data/raw/moon_lola_80s_20m_shackleton_window.tif` | VALIDATED (metadata states so); re-hashed 2026-11-15 → matches registry (55ff65…) |
| `moon_lola_effres` | LDEM_80S_20MPP_ADJ_EFFRES (windowed) | NASA GSFC PGDA | https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ_EFFRES.TIF | Windowed range-read | `data/raw/moon_lola_80s_20m_shackleton_effres_window.tif` | VALIDATED; re-hashed → matches `00092bfe…` |
| `mars_jezero_ctx_dtm` | JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0 | USGS Astrogeology / NASA MRO CTX | https://planetarymaps.usgs.gov/mosaic/mars2020_trn/CTX/JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif | Full download (9.66 MB) | `data/raw/JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif` | VALIDATED; re-hashed → matches `16a1aa66…` |
| `usgsn36w117` | USGS 3DEP 1″ tile n36w117 (current) | USGS 3D Elevation Program | https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/n36w117/USGS_1_n36w117.tif | Full download (~51.7 MB) | `data/raw/USGS_1_n36w117.tif` | VALIDATED; re-hashed → matches `6dad0432…` |
| `usgsn37w117` | USGS 3DEP 1″ tile n37w117 (current) | USGS 3D Elevation Program | https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/n37w117/USGS_1_n37w117.tif | Full download (~50.3 MB) | `data/raw/USGS_1_n37w117.tif` | **RESOLVED 2026-11-15 (Phase 22.1)** — local SHA-256 re-derived (`d6100180753d276b407ec585…`); byte-identity to the current USGS S3 release verified (MD5 == ETag `79040a217c743b4f3baa9fec291b284d`; Content-Length match). Docs corrected. Provenance recorded in `data/metadata/usgs_1_n37w117.json`. |
| `earth_nasadem_hgt_v001` | NASADEM Merged DEM Global 1″ V001 | NASA LP DAAC / JPL | https://cmr.earthdata.nasa.gov/search/granules.json?collection_concept_id=C2763264762-LPCLOUD | Earthdata Login required | none | **BLOCKED** — HTTP 401 (no credentials in repo). Never downloaded. |
| processed LOLA | same product, 20 m elevation grid | (derived) | — | derived (copy of raw window) | `data/processed/moon_lola_80s_20m_elevation_m.tif` | Local derivative; not re-verified against parent by independent re-extraction in this audit. |
| processed LOLA central | ±10.24 km subset | (derived) | — | derived | `data/processed/moon_lola_central_20km_window.tif` | Derived; hash recorded for audit only. |
| processed Jezero | same DTM, float32 metres | (derived) | — | derived | `data/processed/mars_jezero_ctx_elevation_m.tif` | Derived; hash recorded. |
| processed USGS n36w117 | EPSG:26911, 20 m | (derived) | — | derived | `data/processed/USGS_1_n36w117_20m_utm11n.tif` | Hash `8cb8710a…` recorded; no documentation previously carried this hash. |
| processed USGS n37w117 | EPSG:26911, 20 m | (derived) | — | derived | `data/processed/USGS_1_n37w117_20m_utm11n.tif` | Hash `51399c39…` recorded; documentation previously carried the *raw* hash, mislabeled. |

## Reference identifiers (NASA dataset citations preserved)

- LOLA: product ID `LDEM_80S_20MPP_ADJ`; PGDA product page https://pgda.gsfc.nasa.gov/products/90; DOI 10.60903/gsfcpgda-lola-spole; paper Barker et al. 2023, PSJ 4 183, DOI 10.3847/PSJ/acf3e1.
- Mars 2020 CTX DTM: USGS product "Mars 2020 Terrain Relative Navigation CTX DTM Mosaic", official page https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_ctx_dtm_mosaic; file `JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif`.
- NASADEM: collection C2763264762-LPCLOUD; DOI 10.5067/MEASURES/NASADEM/NASADEM_HGT.001 — **not acquired**.
- MOLA global 463 m mosaic: referenced in `docs/datasets.md` as context only; never downloaded; ~2.1 GB. Not in EXPLORE.

## Licenses / rights notes (as recorded, not re-adjudicated)

- USGS 3DEP: public domain (USGS); credit required ("USGS 3DEP"). No cost.
- NASA PGDA / PDS Geosciences Node: open, no cost, citation required (PGDA / PDS).
- USGS Astrogeology (Jezero DTM): public domain; credit "USGS".
- NASADEM: public domain but access-gated (Earthdata Login) — rights not the blocker; credentials are.
- OSM tiles: ODbL — attribution retained in app. NASA GIBS Blue Marble: public domain NASA imagery; attribution retained; **imagery, not terrain**.
- No third-partner proprietary data is present in `data/`.

## Provenance gaps found

- **P-1:** `data/metadata/` has no standalone JSON for `USGS_1_n36w117.tif` / `USGS_1_n37w117.tif` / processed counterparts. Provenance lives only in MD docs; the recorded raw n37w117 hash is wrong.
- **P-2:** Processed files carry no internal embedded provenance (no world-file metadata "created by" tag read for this audit; would need GDAL `TAG_DateTime` inspection — not performed).
- **P-3:** Registry (`registry.json`) lists `earth_nasadem_hgt_v001` as `BLOCKED_BY_EARTHDATA_AUTHENTICATION` / `REJECTED` — accurate; must remain so.
- **P-4:** `synthetic_flat_dem` / `synthetic_gradient_dem` in registry are `synthetic_test_only`, never in `data/`; keep rejected.
- **P-5:** No `data/metadata/` record exists for the effective-resolution LOLA ancillary (`…_effres_window.tif`) — it is documented inside `moon_lola.json` only.
