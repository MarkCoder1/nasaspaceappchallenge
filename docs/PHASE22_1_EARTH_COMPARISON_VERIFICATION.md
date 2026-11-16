# Terra Twin — Phase 22.1: Earth Comparison Verification Report

**Date:** 2026-11-15 · **Purpose:** verify the two Earth-related TMSI results that are claimed in project documentation, and correct the COMPARE page so it does not misstate what was calculated.

## 1. What was verified

| Result | Value | Confidence | Artifact | Inputs (files) |
|--------|-------|-----------|----------|----------------|
| Earth–Moon TMSI | 61.95 (61.9501) | HIGH (stored, Phase 20 panel) | `data/metadata/phase20_earth_moon_comparison.json` | `data/processed/USGS_1_n36w117_20m_utm11n.tif` (Earth), `data/processed/moon_lola_80s_20m_elevation_m.tif` (Moon) |
| Earth–Mars TMSI | 73.14 (73.1360) | HIGH (stored, Phase 20 panel) | `data/metadata/phase20_earth_mars_comparison.json` | `data/processed/USGS_1_n36w117_20m_utm11n.tif` (Earth), `data/processed/mars_jezero_ctx_elevation_m.tif` (Mars) |

Independent re-examination performed this phase (2026-11-15):

1. **Input raster authenticity & integrity**
   - USGS 3DEP `n36w117`: raw SHA-256 `6dad0432701c28fc920befc47cd21c21d4914ff6c3a710d3ab5551ebf489cd40` matches documentation; **byte-identical to current USGS S3 release** (MD5 == single-part ETag `e4fe96ab167f7dd2ed629aba81cc8f33`; Content-Length 54,263,882). Processed tile SHA-256 `8cb8710ac1e6e73e8fdd99e20e440b0fee076dbb0ac6d5aa8533fb22d71b553f` (20 m, EPSG:26911, resampled from ~29.3 m; effective measurement resolution remains ~29.3 m).
   - Moon LOLA: raw SHA-256 `55ff65468068890861a57fecd1f81b64f2f41bc04e0506731530e635aae8b52d` re-verified against `data/metadata/moon_lola.json` and the registry; processed window SHA `f1629938…`.
   - Mars CTX DTM: raw SHA-256 `16a1aa66c3f48c1bca252795827db7b417876217aff0f5e1aff18027fab2327b` re-verified; processed `42eb9c21…`.
2. **Uncertainty quantification present** (Phase 20 block bootstrap, 160/320/640 m blocks): Earth–Moon (64 reps @ seed 42, 320 m) 95% CI ≈ 53.23–72.6; Earth–Mars (64 reps) CI ≈ 65.4–78.8. Phase 20.6 expanded bootstrap (1000 reps, seeds 42/123/456): Earth–Moon CI 51.99–72.56 (seed-sensitivity max diff 0.31); Earth–Mars CI 64.99–78.55 (max diff 0.38). Seed sensitivity is small relative to the CI width.
3. **Interpretation limits preserved everywhere (this report included):** TMSI is a morphology-distribution similarity, not a probability, habitability score, or safety certification. Earth source is ~29.3 m measured, shown at 20 m processed. Vertical datums differ (NAVD88 vs lunar project datum vs Mars delta-geoid) and are unquantified. Earth coverage is **two USGS 3DEP tiles** (southern Arizona / Death Valley vicinity), so no global terrestrial conclusion can be drawn from these numbers.

## 2. Independent validation status — explicitly not granted

- The two Earth values above are project-computed, project-audited (Phase 20 / 20.5 / 20.6), and project-reproduced (1000-rep bootstrap; stable seeds). They are **not third-party/independently validated**, and they are **not candidate-specific** (they characterize the n36w117 window, not "Death Valley the candidate" as a whole).
- The Moon↔Mars 49.92 baseline is likewise project-computed.
- NASADEM (the only globally uniform Earth elevation source) remains unavailable (Earthdata HTTP 401); no global Earth–Moon/Mars experiment has ever been run.

## 3. What the COMPARE page may say (and did not, before this phase)

**Before (inaccurate):** "Earth–Moon / Earth–Mars TMSI is not computed from them."
**After (accurate, in `frontend/components/ResearchWorkbench.tsx`):** it now states that Earth–Moon 61.95 and Earth–Mars 73.14 exist as stored Phase 20 artifacts computed from the USGS 3DEP n36w117 window; that they are confidence-labelled project results (not independently validated, not candidate-specific); and that Earth coverage is limited to two USGS tiles, with NASADEM blocked (HTTP 401). No new number is introduced; no existing limitation is hidden.
