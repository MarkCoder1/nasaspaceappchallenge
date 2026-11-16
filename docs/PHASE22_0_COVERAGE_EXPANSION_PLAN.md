# Terra Twin — Phase 22.0 Audit: Recommended Coverage Expansion Plan

**Date:** 2026-11-15 · Planning only. **Nothing below has been downloaded or implemented.** Each step requires Phase 22.1 authorization. Licensing/rights are noted as recorded in the existing register; any new source needs the same rights review before download.

## Ground rules for any expansion

1. Verify target tile existence in official public buckets **before** downloading — already done for items below by listing S3 keys this audit (metadata only, no bits downloaded).
2. Enforce the existing acquisition discipline: windowed range-reads where possible, full downloads ≤ ~100 MB per product, SHA-256 recorded at receipt, FGDC XML retained, provenance written to `data/metadata/`.
3. Reproject to a per-region UTM zone (or keep native EPSG:26911 grid for the California tile); **document**, never silently transform.
4. Preserve original products; processed grids are derived artifacts.
5. Do not alter the 20 m methodology; adding Earth tiles does not widen the Moon/Mars evidence base or relax the Earth-data limitations.

## Tier 1 — immediate US candidates with verified public tiles (all 1″ USGS 3DEP, ~50–57 MB each)

| Candidate | Target tiles (existence verified 2026-11-15) | Post-download action |
|-----------|----------------------------------------------|----------------------|
| Meteor Crater | `n35w111` | Reproject to UTM 12N → 20 m grid; ~48.8×55 km window covers crater + surroundings (metre crater is at lon −111°, i.e. zone 12N) |
| Grand Canyon | `n36w112`, `n36w113` (both exist) | Reproject to UTM 12N → 20 m grid (lon −112…−111) |
| Mojave Desert | `n35w115`, `n35w116` (and optionally n36w115/116 for northern portion) | Reproject to UTM 11N → 20 m grid (lon −117…−114) |
| Death Valley (complete candidate bbox) | `n35w117`, `n35w118`, `n36w118`, `n37w118` (n36w117 & n37w117 already in repo) + re-acquire n37w117 to repair R-1 | Same UTM 11N pipeline |
| Columbia River Flood Basalts | `n47w121` | UTM 10N → 20 m grid (lon −121) |
| Alaska Peninsula Volcanics | `n58w155` (also note `n59w155` may be needed later) | Reproject to UTM 5N (typical for ~155°W, verify EPSG) |
| Arctic Tundra (Alaska portion only) | `n70w150` — choose 1″ or 2″ deliberately; 2″ is the documented 3DEP scale for most of Alaska | EPSG per tile; document choice |

Estimated raw download: **≈300–390 MB** (6–8 tiles). Processed outputs ≈ same total ×~1.5 in float32. Storage is trivial vs current repo size. CPU: reprojection of one 3612×3612 tile is seconds.

## Tier 2 — Hawaii/Arctic feasibility follow-ups (no download authorized yet)

- **Hawaii:** probe USGS 3DEP current S3 for `StagedProducts/Elevation/1/TIFF/current/n19w155/` (returned empty) and `/13/` (1/3 arc-second) and `/1M/` (1 m) paths; also check `StagedProducts/Elevation/10/…` (Alaska sea-surface? no). Only after a listed tile exists do we estimate size. **Do not assume Hawaii coverage from the empty 1″ listing.**
- **Arctic Tundra beyond Alaska:** requires Canadian/Russian national DEMs (not public domain USGS) — out of scope for USGS-only expansion; needs separate rights review.

## Tier 3 — non-US candidates (all require new source classes; no USGS 3DEP)

| Candidate | Candidate public source (unverified availability) | Gate |
|-----------|--------------------------------------------------|------|
| Atacama | Chile DEM from Cartografía Nacional / or SRTM 1″ (NASA) or Copernicus GLO-30 | Licence & access review; not automatically "public download" |
| Arabian | SRTM 1″/3″ (public NASA) or Copernicus GLO-30 | Rights review |
| Sahara | SRTM 1″/3″ or Copernicus GLO-30 | Rights review |
| Lake Baikal | SRTM 1″ or Copernicus GLO-30; Russian federal sources not portable | Rights review |
| Antarctica Polar Plateau | BedMachine Antarctica (NASA/NSIDC) or REMA 2 m (NSIDC; ~2.5 GB national) | Explicit size authorization + licence check; likely Phase 22.x, **not** 22.1 |

Do **not** download any Tier 3 product until rights and storage are explicitly approved.

## Planetary-side expansion (explicit non-goal for this phase)

No Moon/Mars candidate can be "expanded" without acquiring new bounded DEM windows:
- Moon: would require additional LDEM windows (e.g., equatorial mare for basalt-candidate matching), each a new PGDA product ID, each a new acquisition + validation cycle.
- Mars: additional bounded CTX DTMs (e.g., Gale: JEZ_*_gale…) require ODE product selection by a domain reviewer; the repo has deliberately not authorized them.

**Recommendation: do not expand planetary scope in Phase 22.1.** Fix Earth-side coverage first; keep the Moon↔Mars headline experiment bounded.

## Mandatory Phase 22.1 prerequisites before any Tier-1 download

1. Re-acquire `USGS_1_n37w117.tif` (and optionally n36w117) and record SHA-256 at receipt; update the four docs + `candidates.py` comment that carry the stale hash.
2. Fix the four bounding_box longitude sign errors (F-2/F-3) **in the same documented change**, listing each change and source.
3. Decide EPSG per new tile (UTM 10N/11N/12N/5N as applicable) **before** running the pipeline; document choice.
4. Add the `data/metadata/*.json` records for all new acquisitions so every future raster has machine-readable provenance (fixes P-1).
5. Re-run full Python test suite and the five destinations; confirm no regression.
