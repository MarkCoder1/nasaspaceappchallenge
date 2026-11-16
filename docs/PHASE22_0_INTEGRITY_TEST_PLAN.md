# Terra Twin — Phase 22.0 Audit: Automated Integrity Test Plan

**Date:** 2026-11-15 · No tests were added or modified in this phase; this is the plan. Each proposed check is implementable with `pytest`/`rasterio`/`requests`. None of the tests below change methodology.

## Objective

Catch silent integrity regressions of the class found in this audit (hash mismatch, wrong-sign bounding boxes, stale docs) in CI, not in a manual review.

## Test groups (proposed)

### G-1 — Registry consistency (no I/O)

- T-1 `test_candidates_count_and_ids` — exactly 13 authentic candidate ids; reject the test-contaminant ids (`test_candidate_small`, `e2e_test_cand`) unless explicitly in a fixtures allow-list.
- T-2 `test_candidate_point_within_bbox` — parse `bounding_box` as `min_lat min_lon max_lat max_lon`; assert `min_lat ≤ latitude ≤ max_lat` and `min_lon ≤ longitude ≤ max_lon` for every candidate with a parseable bbox. (This test FAILS on #2, #5, #8, #13 as of 2026-11-15 — intentional; it becomes the gate after Phase 22.1 fixes the bboxes.)
- T-3 `test_bounding_box_sign_convention` — for candidates with |lon| ≤ 180 and point lon sign known, assert bbox longitude sign matches the point's hemisphere (catches F-2/F-3 automatically).
- T-4 `test_latitude_longitude_ranges` — −90 ≤ lat ≤ 90; −180 ≤ lon ≤ 180.
- T-5 `test_planetary_relevance_vocabulary` — relevance ∈ {Moon, Mars, Earth, Both}; unknown values fail.

### G-2 — Raster inventory & provenance (local files, no network)

- T-6 `test_all_documented_rasters_exist` — every filename referenced by `data/metadata/*.json` exists on disk.
- T-7 `test_documented_sha256_match` — for each metadata JSON with `sha256`/`file_sha256`, recompute and compare. (**FAILS today for `n37w117`** — intentional, becomes pass after re-acquisition.)
- T-8 `test_no_orphan_rasters` — every `.tif` under `data/` is either referenced by metadata or in a documented allow-list (the synthetic benchmark rasters, if any are ever added).
- T-9 `test_crs_and_resolution_annotated` — every `data/processed/*_20m*.tif` reads back CRS, resolution (uniform post spacing), and bounds via rasterio; assert EPSG 26911 for the US tiles and Moon 2015 stereographic for LOLA.
- T-10 `test_nodata_sentinel_present` — USGS processed tiles retain `-999999`-or-NaN nodata; LOLA/CTX retain NaN.
- T-11 `test_grid_bounds_within_source_bounds` — processed grid's WGS84-projected bounds lie inside the raw source tile's bounds (catches accidental clipping to wrong region).

### G-3 — Documentation hash consistency (static)

- T-12 `test_docs_hashes_are_labeled_correctly` — grep `docs/PHASE*` and `backend/app/api/candidates.py` for the raw SHA strings; assert each n36w117/n37w117 hash appears only in contexts labeled raw-vs-processed correctly (or, simpler: assert the known-good current hashes appear at least once in docs; assert the stale documented n37w117 hash appears **nowhere** after Phase 22.1).

### G-4 — Scientific contract tests (existing behavior, pinned)

- T-13 `test_tmsi_results_unchanged` — recompute TMSI for the three benchmarks from the re-hashed rasters (Moon LOLA, Mars CTX, Death Valley processing) and assert equality within float tolerance with the Phase 20 baselines (Moon–Mars 49.92, Earth–Moon 61.95, Earth–Mars 73.14). Requires n37w117 re-acquisition; tolerance ±1e-6 relative.
- T-14 `test_candidate_registry_status_vocabulary` — every candidate `scientific_validation_status == "unvalidated"` and `validation_status` stays `unvalidated` until a named validation phase promotes one; guard against accidental "verified" copy-paste in docs/tests.

### G-5 — Map/EXPLORE regression smoke tests (headless, already-supported stack)

- T-15 `test_map_loads_13_markers` — Playwright: MAP destination shows 13 markers; selecting each does not raise console errors; close restores full-width map.
- T-16 `test_death_valley_terrain_grid_endpoint` — `/api/candidates/terrain-grid/death_valley` returns 200 with finite clipped grid; switching to a non-verified candidate returns the honest unavailable state.
- T-17 `test_five_destinations_health` — EXPLORE, COMPARE, RELIABILITY, DATA & METHODS, MAP all return HTTP 200 and zero console errors (extends the existing Phase 21.1 acceptance harness).

## Execution & gating

- G-1/G-2/G-3 run on every commit (fast, offline).
- T-13 gated to the integration CI lane (requires ~2 min raster reads).
- T-15/17 run pre-merge for frontend changes.
- **All proposed tests are additive.** No existing test may be weakened or deleted. The two suites that fail today because of real findings (T-2 sign errors, T-7 n37w117 hash) are introduced with `@pytest.mark.skip(reason="blocked by Phase 22.1)"`-style markers only if they would otherwise gate unrelated work — never by editing the assertions.

## Backfill after implementation

When Phase 22.1 fixes F-2/F-3 and R-1, flip T-2/T-7 from known-fail to pass, then delete any skip markers. Document each in the Phase 22.1 changelog with before/after hash and bbox values.
