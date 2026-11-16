# Phase 4 validation report

## Verdict: READY WITH LIMITATIONS

The explainable morphology engine, feature extraction, statistical distance model, scoring configuration, sensitivity analysis, and honest API status surface are implemented and tested. A real cross-body Earth-Mars or Earth-Moon comparison is not available because NASADEM has not been acquired and no lunar LOLA product has passed validation.

## Implemented features

- Slope in degrees from metre-based projected gradients.
- 60 m local elevation relief.
- 60 m Riley-style terrain ruggedness index.
- Feature distribution summaries.
- Wasserstein distance normalized by pooled IQR.
- Kolmogorov-Smirnov diagnostic statistics.
- Configurable equal-weight baseline.
- TMSI transformation `100 * exp(-D)`.
- Resolution compatibility and coverage confidence classification.
- Explainable strongest matches, largest differences, sources, and limitations.
- Weight sensitivity analysis.

## Datasets actually used

The real processed input is [the Mars Jezero CTX DTM](../data/processed/mars_jezero_ctx_elevation_m.tif), retained in Mars `ESRI:103885` coordinates at 20 m resolution. Earth NASADEM and lunar LOLA remain unavailable. Synthetic DEMs are used only in tests and are explicitly labeled synthetic.

## Comparisons

No production comparison or ranking is returned. The API rejects unavailable Earth/Moon dataset IDs with HTTP 409 and returns an empty result list rather than fabricating a score.

## Backend endpoints

- `GET /api/similarity/status`
- `GET /api/similarity/features`
- `GET /api/similarity/methodology`
- `GET /api/similarity/results`
- `POST /api/similarity/compare`

The service remains separate from scientific calculations in `science/similarity/`.

## Tests

Final full suite: `16 passed` with `PYTHONPATH=. backend/.venv/bin/pytest -q` after the Phase 4 test additions.

Coverage includes feature extraction, flat-DEM sanity behavior, distribution distances, TMSI monotonicity, masking, native-resolution rejection, confidence classification, weight sensitivity, API validation, unavailable datasets, and no fabricated results.

## Remaining limitations

- No real Earth candidate comparison is possible until NASADEM tiles are acquired and processed.
- No lunar comparison is possible until a specific south-polar LOLA product is selected and processed.
- Terrain metrics remain scale-dependent and do not imply environmental, atmospheric, gravitational, radiological, or habitability equivalence.
- TMSI is not a probability, safety score, settlement score, or landing certification.
- Feature extraction currently operates on validated raster windows; candidate-region management and ranking remain deferred.

## Recommendation

Phase 5 should first acquire and validate Earth and lunar terrain inputs, then expose a single real comparison with feature-level explanations. Production ranking should remain disabled until those inputs pass the same provenance, CRS, resolution, and missing-data checks used for Mars.
