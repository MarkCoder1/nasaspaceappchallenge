# Terra Twin — Phase 22.0: Geospatial Data Integrity & Coverage Audit — Verdict

**Date:** 2026-11-15 · **Status: Audit executed against all registered candidates (13/13) and all rasters used by EXPLORE/MAP (5 raw + 5 processed + 2 ancillary reads = all files present in `data/raw` and `data/processed`).** No file was modified, no data was downloaded, no registry entry was corrected in this phase.

## 1. Scientific Audit Verdict

**Terra Twin's geospatial data layer is *operational but materially weaker than its documentation implies.* It is fit for a bounded Moon↔Mars benchmark experiment on two calibrated raster windows. It is NOT yet fit to support the Earth-analog candidate programme it presents in EXPLORE/MAP.**

- All 13 candidates are Earth-body points. None has a verified-in-this-audit local DEM beyond the two USGS 3DEP tiles (Death Valley/southern Arizona, via `n37w117`/`n36w117`).
- Only Death Valley has ANY local elevation data, and even that is a 1° tilepair (≈110×110 km each), partially covering its own declared bounding box — it is a **point sample, not a survey of the candidate region**.
- The headline Earth coverage limitation persists exactly as Phase 20/20.6 disclosed; this audit found two additional *silent* integrity breaks (see R-1, F-2) that had not been caught: a hash that no longer matches the stored raw file, and 4 of 13 candidate bounding boxes with reversed longitude sign for East-longitude regions.
- The five application destinations are functionally intact (re-probed 2026-11-15: frontend 200, backend restarted and `/api/health` returns 200; no candidate data was changed this phase).

**Verdict: CONDITIONALLY SUITABLE — for the documented bounded Benchmark use-case only. NOT scientifically supportable as a validated multi-candidate Earth-exploration platform without the Phase 22.1 remediation below.** No candidate result, no map, and no Earth-analog claim should be presented to a general audience as if it were validated candidate terrain.

## 2. What is verified (this audit, independently re-measured)

- Lunar benchmark raster (LOLA `LDEM_80S_20MPP_ADJ` windowed product): re-hash matches registry; CRS/bounds/resolution re-read; citation preserved; effective-resolution ancillary consistent. **Sound.**
- Jezero CTX DTM (Mars): re-hash matches registry; CRS ESRI:103885 preserved; bounds as documented. **Sound.**
- USGS 3DEP n36w117 (Earth): re-hash matches docs; CRS EPSG:4269; bounds as documented; processed tile is derived and mislabelled in docs as sharing the raw hash (R-2/label error), but the file itself is coherent.
- Death Valley raster group integrity (n37w117 pair): **fails** — see R-1.
- Candidate coordinates: see coordinate verification report — 7 named-tolerance verified, 5 region points, 1 questionable (antartica_polar), multiple bbox integrity defects.

## 3. Acceptance criteria — status

| Criterion | Result |
|---|---|
| All 13 candidates accounted for | **PASS** (report covers #1–13; nothing skipped) |
| Every verified coordinate has an authoritative source | **PASS with flags** — verified points carry named sources (NPS, Wikipedia/GPS fix, DCP, mindat); no coordinate was invented; flags F-1/F-4/F-5 recorded; no correction applied |
| Every raster has documented provenance | **FAIL** — processed USGS tiles were never documented with their own hashes; n37w117 documentation hash mismatches the live file (R-1, P-1) |
| Coverage classifications are evidence-based | **PASS** — classifications derive from files opened and hashed in this audit (see coverage matrix), not from assumptions |
| No fabricated data | **PASS** — no downloads, no synthetic values introduced; NASADEM remains BLOCKED; no imagery used as elevation |
| Existing tests continue passing | **PASS with caveat** — Python suite ran at the start of this session: 117/117 (run again post-audit expected green since no source files changed; see §6) |
| No regression to the five application destinations | **PASS** — no application code modified; frontend 200; backend health 200 after clean restart |

## 4. Deliverables produced (7 + this verdict)

1. `docs/PHASE22_0_CANDIDATE_COORDINATE_VERIFICATION.md`
2. `docs/PHASE22_0_RASTER_INVENTORY.md`
3. `docs/PHASE22_0_GEOGRAPHIC_COVERAGE_MATRIX.md`
4. `docs/PHASE22_0_SOURCE_PROVENANCE_REGISTER.md`
5. `docs/PHASE22_0_MISSING_DATA_REPORT.md`
6. `docs/PHASE22_0_COVERAGE_EXPANSION_PLAN.md`
7. `docs/PHASE22_0_INTEGRITY_TEST_PLAN.md`
8. `docs/PHASE22_0_AUDIT_VERDICT.md` (this file)

## 5. Recommended Phase 22.1 scope (in priority order)

1. **Repair the data plane first.** Re-acquire `USGS_1_n37w117.tif` to restore provenance; add `data/metadata/usgs_1_n3*_20m_utm11n.json` records with verified hashes; correct the stale hash in `backend/app/api/candidates.py` + the 3 MD docs (documented, not silent).
2. **Fix the four bounding-box sign errors** (arabian_desert, sahara_desert, lake_baikal, antartica_polar) — document each correction with source; add T-2/T-3 automated tests to prevent regression.
3. **Acquire Tier-1 coverage** (Meteor Crater, Grand Canyon, Mojave Desert core, Columbia River Flood Basalts, Alaska Peninsula volcanics) per the expansion plan — all 1″ public USGS 3DEP, ≈300–390 MB raw, each with verified S3 listing already done this audit.
4. **Re-verify EXPLORE/COMPARE scientific claims** once Earth coverage widens: re-run TMSI with expanded windows; record whether the Moon–Mars 49.92 baseline is sensitive to Earth-tile widening (it isn't expected to change — n37w117 is used by EXPLORE only, experiment used n36w117 — but verify).
5. **No planetary (Moon/Mars) expansion in 22.1.** Keep both working windows bounded and the headline result unchanged.
6. **Update the COMPARE-page Earth banner** (small text fix): the current wording says USGS tiles are *not* used for Earth–Moon/Mars TMSI, but Phase 20/20.5 computed exactly that with n36w117 (Earth–Moon 61.95; Earth–Mars 73.14). Decide one of: (a) surface the Phase 20 Earth comparison artifact in the UI honestly, or (b) keep the banner but correct the sentence to "Earth–Moon / Earth–Mars TMSI **is** computed from the Southern-Arizona USGS n36w117 window only; no candidate-specific Earth comparison exists in the current product." Silence or misstatement in scientific copy is a defect.
7. **Correct `antartica_polar`** anchoring or demote it: either anchor to a published Polar-Plateau location (e.g. 77°S 150°E) or label it a study-window centroid, not a "candidate site".

## 6. Regression note & remaining limitations

- This audit mutated **no code, no data, no registry** — only new docs were added. The 117-test Python suite result from earlier this session (117/117 pass) therefore remains valid as a statement of pre-audit state; it is not being re-run as part of this audit (nothing changed), and no new test is introduced by this phase.
- Backend was restarted during this audit after it was found down (EADDRINUSE/zombie process); service verified healthy again (`/api/health` → `{"status":"ok"}`). EXPLORE/COMPARE/MAP were not re-screenshotted this phase (no UI change made).
- NASADEM remains blocked (HTTP 401) — no global Earth terrain is possible until credentials are configured by the user; no alternative global product is adopted by this audit.
- Imagery (OSM/GIBS) is used by MAP purely for visual orientation and is explicitly not terrain measurement.
- The Earth-analog candidate programme is **not validated**; all candidate conclusions remain open pending Phase 22.1+.

## 7. Final statement

Phase 22.0 is complete as an audit: every registered candidate and every local raster has been inspected and either hashed or read back from disk. Discrepancies are recorded, not hidden. No claim in the application exceeds what the measured rasters and documented sources support — except the two integrity defects called out above, which Phase 22.1 must repair before any broader scientific or public use of the MAP/EXPLORE Earth-candidate story.
