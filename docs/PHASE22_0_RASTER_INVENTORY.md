# Terra Twin — Phase 22.0 Audit: Raster Inventory

**Date:** 2026-11-15 · **Scope:** every raster consumed by EXPLORE and MAP at runtime, plus the raw predecessors. No files were modified.

Conventions: SHA-256 computed locally on 2026-11-15. CRS/units read back with `rasterio`. "Used by" reflects code paths in `backend/app/api/candidates.py`, `backend/app/api/similarity.py`, `backend/app/services/similarity.py`.

## A. Raw rasters (`data/raw/`)

| File | Institution | Dataset ID / label | Size | CRS | Extent (bounds) | Resolution | Dims | Units | No-data | SHA-256 |
|------|-------------|--------------------|------|-----|-----------------|------------|------|-------|---------|---------|
| `moon_lola_80s_20m_shackleton_window.tif` | NASA GSFC PGDA (LOLA) | LDEM_80S_20MPP_ADJ, windowed | 13.59 MB | Moon (2015) Sphere/Ocentric/South Polar stereographic, IAU 30135 | ±20480 m (40.96 km) centered on pole | 20.0 m | 2048×2048 | metres | NaN | `55ff65468068890861a57fecd1f81b64f2f41bc04e0506731530e635aae8b52d` |
| `moon_lola_80s_20m_shackleton_effres_window.tif` | NASA GSFC PGDA (LOLA) | LDEM_80S_20MPP_ADJ_EFFRES, windowed | ~0.01 MB | same | ±20480 m | 1280.0 m (grid of the effective-resolution product) | 32×32 | metres (effective resolution in m/px) | NaN | `00092bfe33dda58689f3a52fb342d4ce2ccfcc80d3ea05ccc9d77adac0b2cadc` |
| `JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif` | USGS Astrogeology / NASA MRO-CTX | JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0 | 9.21 MB | ESRI:103885 (Mars 2000, equirectangular, lat_0=0, lon_0=0, MOLA control) | L 4573663.25, R 4605583.25, B 1079453.14, T 1109693.14 (metres) | 20.0 m | 1512×1596 | metres | sentinel `-3.4028e+38` (float32 max) | `16a1aa66c3f48c1bca252795827db7b417876217aff0f5e1aff18027fab2327b` |
| `USGS_1_n36w117.tif` | USGS 3DEP | 1-arc-second tile n36w117, current release | 51.75 MB | EPSG:4269 (NAD83 geographic) | L −117.0017, R −115.9983, B 34.9983, T 36.0017 | 0.0002778° (~29.3 m) | 3612×3612 | metres (NAVD88) | −999999 | `6dad0432701c28fc920befc47cd21c21d4914ff6c3a710d3ab5551ebf489cd40` |
| `USGS_1_n37w117.tif` | USGS 3DEP | 1-arc-second tile n37w117, current release | 50.25 MB | EPSG:4269 | L −117.0017, R −115.9983, B 35.9983, T 37.0017 | 0.0002778° (~29.3 m) | 3612×3612 | metres (NAVD88) | −999999 | `d6100180753d276b407ec585a872dc41d3515ea838c551ad22ec3aca4e6d8ad1` (see Finding R-1) |

## B. Processed rasters (`data/processed/`) — what the app actually serves

| File | Derivation | CRS | Extent | Resolution | Dims | Elevation range | Valid px | SHA-256 |
|------|------------|-----|--------|-----------|------|------------------|-----------|---------|
| `moon_lola_80s_20m_elevation_m.tif` | Copy/processing of raw LOLA window (no reprojection) | Moon 2015 South Polar stereographic | ±20480 m | 20.0 m | 2048×2048 | −2872.1 … +1959.4 m | 4,194,304 (100%) | `f16299380131ae17e6519bcd031e2332d576b7db768d784924c8516aab646de1` |
| `moon_lola_central_20km_window.tif` | Subset of LOLA window: ±10240 m | same | ±10240 m | 20.0 m | 1024×1024 | −2872.1 … +1738.4 m | 1,048,576 (100%) | `d94875692301f44fd589a89f06faa11c88d31636fac5a93bb7a388740f8c8dab` |
| `mars_jezero_ctx_elevation_m.tif` | Copy/processing of raw CTX DTM | ESRI:103885 | same as raw | 20.0 m | 1512×1596 | −2710.7 … −1515.5 m | 2,413,152 (100%) | `42eb9c214de93c48295543eebdd29e749d2320d72fdae1b41296189520516503` |
| `USGS_1_n36w117_20m_utm11n.tif` | Locked to UTM Zone 11N (EPSG:26911), resampled 29.3 m → 20 m (does not add detail) | EPSG:26911 (UTM 11N) | 499848–591428, 3872837–3984597 | 20.0 m | 5588×4579 | −72.9 … +1868.8 | 25,315,828 (98.94%) | `8cb8710ac1e6e73e8fdd99e20e440b0fee076dbb0ac6d5aa8533fb22d71b553f` |
| `USGS_1_n37w117_20m_utm11n.tif` | Locked to UTM Zone 11N, resampled 29.3 m → 20 m | EPSG:26911 | 499850–590290, 3983766–4095526 | 20.0 m | 5588×4522 | −85.1 … +2176.4 | 25,002,423 (98.95%) | `51399c39250ce30d546df7a57650b69c960ebd5bc8f43f81c71830b9016ff9dd` |

## C. Independent verification of the Death Valley 3DEP raster (as requested)

Verification steps performed 2026-11-15 against the locally stored files:

1. **CRS read-back:** raw tile reports EPSG:4269 / file n37w117 (matches USGS product convention for 1 arc-second seamless tiles: geographic, NAD83).
2. **Bounds read-back:** raw tile — west −117.0017, east −115.9983, south 35.9983, north 37.0017. XML metadata (`data/raw/USGS_1_n37w117.xml`) independently reports identical bounding coordinates. **Consistent.**
3. **Grid:** 1/3600° post spacing read back; XML FGDC metadata confirms "1 arc second" and "meters" vertical units with NAVD88. **Consistent.**
4. **Processed output re-measured:** 5588×4522 px at 20 m post spacing EPSG:26911; extent covers the same W/E lons area in UTM metres (499,850–590,290 m E). Resampling adds interpolated values (bilinear); the label in the app correctly states native ~29.3 m is the effective resolution.
5. **Vertical datum:** NAVD88 (per FGDC XML). **Not interchangeable** with lunar/Martian vertical references without documented normalization.
6. **Completeness:** 98.95% valid (1.05% nodata, edge/gigapixel clip), documented.
7. **SHA-256 of the file on disk (raw):** `d6100180753d276b407ec585a872dc41d3515ea838c551ad22ec3aca4e6d8ad1` — see Finding R-1 below.

## Findings

- **R-1 (documentation hash mismatch) — RESOLVED Phase 22.1.** `USGS_1_n37w117.tif` was verified byte-identical to the current official USGS S3 release (MD5 == ETag, Content-Length 52,691,013) — the file on disk is authentic; the *documented* hash was wrong. All documentation and `backend/app/api/candidates.py` were corrected to the on-disk SHA-256 `d6100180753d276b407ec585a872dc41d3515ea838c551ad22ec3aca4e6d8ad1`; processed-file hashes (`8cb8710a…` n36w117, `51399c39…` n37w117) were added to `data/metadata/usgs_1_n36w117.json` and `data/metadata/usgs_1_n37w117.json` with full provenance; Phase 22 reproducibility/integrity docs re-labelled raw vs processed. n36w117's documentation hash had always matched. The processed 20 m (`51399c…`) is now recorded for the first time.
- **R-2 (processing grid resampled twice):** n36/n37w117 native 1 arc-second ≈ 29.3 m → processed at 20.0 m. This is *required* to align with LOLA/CTX post spacing but adds no information; docs already disclose this. The Death Valley preview therefore cannot claim better than ~29.3 m effective resolution.
- **R-3 (Antarctic candidate unsupported by any raster):** no Antarctic elevation data exists locally; the Polar Plateau is ice-covered and unmapped by any product in `data/`.
- **R-4 (geographic candidates outside USGS coverage entirely):** Atacama, Arabian, Sahara, Baikal are not public USGS domains (3DEP is US + national map territories only). No elevation raster for these is legally/publicly available as USGS 3DEP; none exists locally.
- **R-5 (imagery ≠ elevation):** MAP's basemap (OSM + NASA GIBS Blue Marble) is imagery only. It must not be read as terrain measurement; noted for coverage analysis.
- **R-6 (Moon product):** the "shackleton" raw LOLA window and the 20 m elevation product are both centred on Shackleton crater (around 89.9°S 0°E), NOT on any candidate location. It is used as the lunar benchmark, not as a candidate profile source.
- **R-7 (Mars product):** CTX DTM bounds 18.2–18.7°N, 77.2–77.7°E matches Jezero working region only. It does not cover candidate Earth sites or Mars globally.
- **R-8 (synthetic rasters):** no synthetic rasters are stored as files; `synthetic_flat_dem`/`synthetic_gradient_dem` are registry metadata only, `synthetic_test_only`, rejected for science use.

## Processing provenance (as documented, not independently re-executed)

- LOLA: windowed range-read from official PGDA Cloud-Optimized GeoTIFF; parent 2.6 GB NOT downloaded; effective-resolution ancillary windowed likewise; Barker et al. 2023 citation recorded (`10.60903/gsfcpgda-lola-spole` / paper `10.3847/PSJ/acf3e1`).
- Jezero CTX DTM: official USGS GeoTIFF downloaded in full (9.66 MB); SHA recorded at acquisition (now recomputed above).
- USGS 3DEP tiles: official USGS S3 direct paths (`prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/…`); FGDC XML metadata retained alongside raw files.
- Processing scripts/verification: not inspected (out of audit scope); processed files read back directly for this audit.
