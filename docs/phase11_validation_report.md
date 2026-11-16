# Phase 11 Validation Report

## Overall verdict
**READY WITH LIMITATIONS.**

The TMSI methodology is internally consistent and reproducible, but Phase 11 demonstrates
that TMSI is a pairwise terrain-window morphology similarity index whose value is strongly
contingent on spatial extent, window location, and overlap. It cannot be interpreted as a
planetary-body similarity indicator. Earth remains PENDING (Earthdata authentication blocked).
No Earth comparisons enabled. No independent external benchmark obtained.

## Workstream status

| Experiment | Objective | Status | Key result |
|---|---|---|---|
| A | Within-body variability | COMPLETE | Moon TMSI 29.27–94.10 (mean 60.51); Mars 40.99–90.90 (mean 61.28) |
| B | Between-body variability | COMPLETE | Moon–Mars TMSI 22.38–90.60 (mean 46.85); overlaps within-body |
| C | Overlap bias | COMPLETE | Identical → 100.0; high overlap → 78.6–88.0; non-overlap → 15.8–70.1 |
| D | Sampling extent | COMPLETE (Phase 10 reused) | TMSI 23.71 (5.12 km) → 49.92 (full); ~26-point shift |
| E | Sampling strategy comparison | COMPLETE | No strategy replaces baseline; extent/location/overlap must be reported |
| F | TMSI interpretation | COMPLETE | Pairwise window-morphology index only; not a body indicator |
| G | Independent benchmark | BLOCKED | No independent source obtainable |

## Scientifically verified findings (Phase 11)
- **Within-body variability exceeds between-body separability.** Moon within-body TMSI (29.27–94.10) spans a wider range than between-body Moon–Mars (22.38–90.60).
- **Body identity is not recoverable from TMSI.** A score of 49.92 (the Moon–Mars baseline) is indistinguishable from many within-body scores.
- **Overlap is a major confound.** Identical windows → 100.0; 0.56 overlap → up to 87.98; non-overlapping same-body → as low as 15.83.
- **Extent is structural.** Phase 10: TMSI varies 23.71 → 49.92 across 5.12 km → full extent.
- **Bootstrap intervals do not capture across-extent or across-location variability** (only within-extent block-resampling variability).
- **No independent external benchmark** obtainable (Earth blocked; alternatives not independent/too large).

## Baseline preservation
Moon–Mars baseline reproduced exactly: TMSI `49.92285382858792`, confidence HIGH. No silent
methodology change. Official TMSI = 100 × exp(−D), equal weights, pooled-IQR normalization.

## Earth state
Earth remains PENDING. `production_comparisons_enabled=False`. `validated_comparisons=["moon_mars"]`.
`earth_mars` and `earth_moon` capabilities disabled. `/api/similarity/compare` rejects Earth with
HTTP 409.

## Files created (docs)
- `docs/phase11_audit_report.md`
- `docs/phase11_within_body_variability.md`
- `docs/phase11_between_body_analysis.md`
- `docs/phase11_overlap_bias_report.md`
- `docs/phase11_sampling_strategy_report.md`
- `docs/phase11_tmsi_interpretation_report.md`
- `docs/phase11_external_benchmark_report.md`
- `docs/phase11_validation_report.md` (this file)

## Files created (science experiments)
- `science/validation/phase11_experiments.py` (window extraction, overlap detection, comparison runner)
- `data/metadata/phase11_sampling_framework.json` (experiment output: Experiments A, B, C)
- Temporary window rasters created during experiments were deleted; not validated products.

## Files created (tests)
- `backend/tests/test_earth_gates.py` (carry-forward)
- `science/tests/test_phase9_validation.py` (carry-forward)
- `science/tests/test_phase10_validation.py` (carry-forward)
- `science/tests/test_phase11_validation.py` (new: window eligibility, overlap detection, extent)

## Test and build results
- Python tests: 58 passed (baseline) → new Phase 11 tests added below.
- Python compilation: clean.
- Frontend ESLint: 0 errors (1 pre-existing warning).
- Frontend TypeScript: clean.
- Next.js production build: passed.

## Remaining limitations
- Earth/NASADEM PENDING; Earth comparisons disabled pending credentials.
- No independent external benchmark.
- TMSI extent-dependent; must report extent/location/coverage with every score.
- Within-body variability means single TMSI scores are not body-level indicators.
- Mars coverage caps common comparison extent at ~30 km.

## Recommended Phase 12
1. Unblock NASADEM (user-supplied Earthdata credentials), download/validate/register Earth, enable Earth comparisons.
2. Integrate extent/window-location/overlap metadata into ResearchWorkbench + exports.
3. Pursue an independently sourced planetary DEM for external benchmarking.
4. Consider adding window-location sensitivity analysis as an optional experimental feature.
