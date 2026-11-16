# Terra Twin — Phase 22.1 Coordinate Correction Log

**Date:** 2026-11-15 · **Status:** applied to `science/datasets/registry.json` in this phase.
**Rule:** only `bounding_box` fields were modified. No `latitude`/`longitude` (point) was changed. No candidate was removed. Original values are preserved in `docs/PHASE22_1_registry_backup_before_bbox_fix.json` and in the table below.

## Corrections (min_lat min_lon max_lat max_lon)

| Candidate | Original `bounding_box` | Corrected `bounding_box` | Point (unchanged) | Reason |
|-----------|------------------------|------------------------|-------------------|--------|
| arabian_desert | `18.0 -55.0 28.0 -42.0` | `18.0 42.0 28.0 55.0` | 22.0, 53.0 | Longitudinal sign error: region is East of Greenwich; original was the mirror-image range (Atlantic). Point (53 E) now lies within its bbox; spatially matches Empty Quarter extent (44.5–56.5 E). |
| sahara_desert | `17.0 -25.0 28.0 -11.0` | `17.0 11.0 28.0 25.0` | 23.0, 13.0 | Same sign error class; Sahara reference point is 13 E (matches Wikipedia). |
| lake_baikal | `48.0 -103.0 58.0 -113.0` | `48.0 103.0 58.0 113.0` | 53.5, 108.0 | Same sign error class; Baikal spans 103.7–110.1 E (Wikipedia). Also normalized ordering to min<max (original had −103 then −113, inverted). |
| antartica_polar | `-80.0 -170.0 -70.0 -110.0` | `-80.0 110.0 -70.0 170.0` | −75.0, 120.0 | Point is declared at +120.0 E (East Antarctic Plateau) while bbox was West-longitude side (Ross Sea). Sign-flipped to East; corrected range (110–170 E) now contains the declared point, the authoritative Antarctic Plateau anchor (77°S 150°E), and consistent latitude band. **Limitation:** the candidate's bbox has no authoritative survey source — it is an approximate study-window envelope; corrected only for internal consistency, never promoted to a measurement. |

## Source of corrections

- Anti-eral sign convention (WGS84; east-positive, per registry `longitude` convention).
- Wikipedia: Sahara 23°N 13°E; Rubʿ al Khali 20°N 50°E (extent 16.5–23 N, 44.5–56.5 E).
- Lake Baikal spans ≈ 53–56.4 N, 103.7–110.1 E.
- Antarctic Plateau (King Haakon VII Plateau) anchor ≈ 77°S 150°E; SCAR Composite Gazetteer of Antarctica.
- All four fixes verified: corrected bbox contains the candidate's unchanged `latitude`/`longitude`.

## Not changed (flagged for future work)

- Point coordinates were **not** moved. `antartica_polar` point (−75, 120) remains flagged as approximate (no authoritative plateau-center survey anchor for that exact point); see coordinate verification report (F-3) and outstanding limitations.
- `atacama_desert` point (−23.0, −67.75) remains divergent from common published centroid (Wikipedia 24.5°S 69.25°W) — documented, not modified.
- `hawaii_volcanic` (19.5, −155.0) remains an approximate regional point, not pinned to a named volcano summit.
- Test-contaminant candidates (`test_candidate_small`, `e2e_test_cand`) have been removed from the registry (previously done); tests are being fixed in this phase to no longer re-pollute `registry.json`.

## Verification

- All corrected bboxes re-read from disk after edit; point-in-bbox assertion passes for the four candidates.
- Full candidate list re-read; count remains 13; `by_status` = `{"CANDIDATE": 13}`.
