# Terra Twin — Phase 22.0 Audit: Missing-Data Report

**Date:** 2026-11-15 · Enumerates what Terra Twin does **not** have today, and the consequence for scientific claims.

## 1. Elevation data absent

| Candidate | Local elevation | Consequence |
|-----------|-----------------|-------------|
| Atacama Desert | none | Candidate can only display imagery; no DEM-based terrain, slope, or relief measurement is possible. Any elevation-like display would be fabrication. |
| Antarctica Polar Plateau | none | Same. Polar plateau completely unsupported. |
| Hawaii Island Volcanic Landscapes | none | Same (and USGS 1″ public S3 has no n19w155 tile). |
| Grand Canyon | none | Same. |
| Arabian Desert | none | Same. |
| Mojave Desert | none | Same. |
| Sahara Desert | none | Same. |
| Arctic Tundra | none | Same. |
| Alaska Peninsula Volcanics | none | Same. |
| Columbia River Flood Basalts | none | Same. |
| Meteor Crater | none | Same. Note: the crater's own DTM from the HiRISE/CTX archive (outside USGS scope) has not been acquired. |
| Lake Baikal Region | none | Same. |

Only **Death Valley** has any local elevation data (2 USGS 3DEP 1″ tiles → resampled 20 m EPSG:26911; used by EXPLORE via `…/terrain-grid/death_valley`).

## 2. Resolution mismatches (present but weaker than claimed before audit)

- Earth tiles are 1 arc-second (~29.3 m) resampled to 20 m — effective resolution ≈ 29.3 m, not 20 m.
- Lunar window is 20 m nominal but effective-resolution raster reads ~16.06 m / (max ~23.84 m) mean ~16.06 — actually *finer* than nominal at some pixels, but it is an **average** of local resolution and is not a guarantee of 20 m everywhere.
- Mars DTM is 20 m nominal; no effective-resolution ancillary acquired or recorded for it.

## 3. Geographic / CRS gaps

- **n37w117 raw tile no longer matches its documented provenance hash.** The dataset supports "so long as the file on disk is accepted", not "verifiably the file acquired on 2026-11-14".
- Western-hemisphere bounding boxes for Eastern-longitude regions (F-2) — 4 of 13 candidates carry wrong-sign bbox metadata; consumers that respect bbox would clip incorrectly (MAP currently does not use bbox for placement, mitigating visual impact but **data integrity remains**).
- `antartica_polar` point inconsistent with its bbox and with the authoritative plateau anchor (77°S 150°E).
- Two distinct Earth vertical datums conceptually required but never normalized in code: NAVD88 (USGS 3DEP) vs EGM96 (NASADEM, never acquired) vs spherical/planet-specific lunar LOLA vs Mars delta-geoid. **No cross-body elevation comparison can be made without documented datum normalization; none exists in the codebase.**

## 4. Imagery vs elevation confusion risk (documentation finding)

MAP's basemaps (OSM, NASA GIBS Blue Marble) make all 13 candidates *visually* locatable, but none of that content is a terrain measurement. There is a demonstrated user-facing risk of conflating "map visible" with "DEM available" — the UI copy already distinguishes this, and this audit reiterates it: **imagery availability ≠ elevation availability ≠ candidate validity**.

## 5. NASA access gaps

- NASADEM global 1″ (the only globally uniform Earth elevation source identified) is blocked by Earthdata Login (HTTP 401). Consequence: no global Earth terrain for any candidate; all Earth support limited to USGS 1″ tiles (US-only).
- MOLA global 463 m Mars mosaic identified in `docs/datasets.md` but **not downloaded** (≈2.1 GB; explicitly out of acquisition scope). Mars comparison limited to Jezero CTX DTM / LOLA window only.
- PDS Geosciences Node products were not queried for additional bounded windows (out of scope here; audit phase only).

## 6. The most important missing datum

**No elevation data of any kind exists for Moon/Mars candidates outside the single Shackleton/LOLA window and the single Jezero/CTX DTM.** Terra Twin's Moon↔Mars headline experiment is executed entirely on those two bounded windows. It is not a general Earth-comparison instrument, and this audit finds nothing to overturn that conclusion; it reaffirms it.
