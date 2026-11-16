# Terra Twin — Phase 22.0 Audit: Geographic Coverage Matrix (all 13 candidates)

**Date:** 2026-11-15 · **Local verified rasters only** — imagery (OSM / NASA GIBS) is listed separately and is **never** treated as elevation data.

Classification key:
- **VERIFIED** — a local, independently inspected raster covering the candidate is present and checksummed this audit.
- **PARTIAL** — local data covers only part of the candidate region (e.g. one tile over a multi-tile zone) or serves a downsampled grid; no second independent source.
- **UNAVAILABLE** — no local verified elevation data; imagery may still exist (not measurement).

| # | Candidate | Body | Coords (lat, lon) | Local elevation coverage | Classified | Imagery available (MAP) | Elevation: additional public source plausibly exists? | Notes |
|---|-----------|------|--------------------|--------------------------|------------|------------------------|----------------------------------------------------------|-------|
| 1 | Atacama Desert | Earth | −23.0, −67.75 | None | **UNAVAILABLE** | Yes (OSM + GIBS) | Chile DEM (MOP/CENIDLAB?), SRTM/CopDEM (needs different rights), not USGS | No legitimate public single-tile source adopted; must not be treated as supported. |
| 2 | Antarctica Polar Plateau | Earth | −75.0, +120.0 | None | **UNAVAILABLE** | Yes (OSM + GIBS) | BedMachine / REMA (>2.5 GB, Antarctic-scale) | Polar ice plateau unmapped by any product in repo; requires dedicated acquisition + licence review. |
| 3 | Hawaii Island Volcanic Landscapes | Earth | +19.5, −155.0 | None | **UNAVAILABLE** | Yes (OSM + GIBS) | USGS 3DEP 1 arc-second: tile n19w155 returns **no TIFF** in current public S3 (checked this audit — empty current/TIFF listing). See USGS 3DEP 1/3 arc-second or 1 m (different path, not probed). | Hawaii volcanic candidate currently **not supported by elevation**. |
| 4 | Grand Canyon | Earth | +36.1, −112.1 | None | **UNAVAILABLE** | Yes (OSM + GIBS) | USGS 3DEP 1″ tiles n36w112 and n36w113 exist in public S3 (listed this audit; **not downloaded**); reproject to UTM 12N required | Plausible Phase 22.1 target (both tiles ~52 MB each). |
| 5 | Arabian Desert | Earth | +22.0, +53.0 | None | **UNAVAILABLE** | Yes (OSM + GIBS) | No USGS 3DEP coverage (non-US); SRTM 90 m or Copernicus GLO-30 are candidates after rights review | No authoritative elevation source adopted in repo. |
| 6 | Death Valley | Earth | +36.5, −117.0 | USGS 3DEP n37w117 (processed 20 m EPSG:26911) + n36w117 (processed, same grid) | **PARTIAL** | Yes (OSM + GIBS) | USGS 3DEP n35w117 / n35w118 / n36w118 / n37w118 round out candidate bbox | Only local Earth-DEM-supported candidate; coverage is ~2 tiles ≈ ½ of its bbox, not the full region. |
| 7 | Mojave Desert | Earth | +35.0, −115.5 | None | **UNAVAILABLE** | Yes (OSM + GIBS) | USGS 3DEP tiles n35w115, n35w116, n36w115, n36w116 all exist in public S3 (listed; **not downloaded**) | Plausible Phase 22.1 target. |
| 8 | Sahara Desert | Earth | +23.0, +13.0 | None | **UNAVAILABLE** | Yes (OSM + GIBS) | Non-US; SRTM/CopDEM (rights review) | No adopted source. |
| 9 | Arctic Tundra | Earth | +70.0, −150.0 | None | **UNAVAILABLE** | Yes (OSM + GIBS) | USGS 3DEP n70w150 exists at 1″ **and** 2″ (both listings exist, S3 check this audit); 1″ recommended if accepted | Alaska north slope; plausible target; 1″/2″ decision needed before download. |
| 10 | Alaska Peninsula Volcanics | Earth | +58.5, −155.0 | None | **UNAVAILABLE** | Yes (OSM + GIBS) | USGS 3DEP n58w155 exists in public S3 (listed; **not downloaded**) | Plausible Phase 22.1 target. |
| 11 | Columbia River Flood Basalts | Earth | +47.0, −121.0 | None | **UNAVAILABLE** | Yes (OSM + GIBS) | USGS 3DEP n47w121 exists in public S3 (listed; **not downloaded**) | Plausible Phase 22.1 target. |
| 12 | Meteor Crater | Earth | +35.0, −111.0 | None | **UNAVAILABLE** | Yes (OSM + GIBS) | USGS 3DEP n35w111 exists in public S3 (listed; **not downloaded**) | Plausible Phase 22.1 target; crater footprint < 1 km so any 1° tile is sufficient. |
| 13 | Lake Baikal Region | Earth | +53.5, +108.0 | None | **UNAVAILABLE** | Yes (OSM + GIBS) | Non-US (Russia); no adopted source | No adopted source; no USGS 3DEP. |

**Totals:** VERIFIED 0 · PARTIAL 1 (Death Valley) · UNAVAILABLE 12.

Imagery: 13/13 have imagery (OSM / NASA GIBS basemap). This is **visual context only**, never elevation.

Elevation: 1/13 partial (Death Valley, using 2 USGS 3DEP tiles processed to 20 m EPSG:26911), 0 fully verified against an independent elevation source, 12/13 unsupported locally.
