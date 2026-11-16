# Three-planet experiment report

## Execution state

Only one of the three requested pairings is currently supported:

| Experiment | State    | Reason                                                        |
| ---------- | -------- | ------------------------------------------------------------- |
| Earth-Moon | BLOCKED  | NASADEM requires Earthdata authentication and is not acquired |
| Earth-Mars | BLOCKED  | NASADEM requires Earthdata authentication and is not acquired |
| Moon-Mars  | EXECUTED | Both bounded terrain inputs are validated                     |

## Moon-Mars result

- Target: validated Mars Jezero CTX DTM
- Candidate: validated bounded NASA PGDA LOLA south-polar DEM
- Features: slope, 60 m local relief, 60 m Riley TRI
- Resolution gate: passed; Mars native 20 m and LOLA effective resolution recorded separately
- TMSI: `49.92285382858792`
- Confidence: `HIGH`
- Strongest feature matches: slope and local relief
- Statistical uncertainty: [documented separately](statistical_uncertainty_report.md)

The result is reproducible through `POST /api/similarity/compare` with target `mars_jezero_ctx_dtm` and candidate `moon_lola`. It is a morphology-only index and does not imply atmospheric, gravitational, thermal, radiological, habitability, or operational equivalence.

## Provenance

The API response includes the Mars and Moon provenance manifests, preprocessing reports, source URLs, checksums, feature configuration, TMSI weights, confidence, and statistical uncertainty metadata.

## Ranking state

Production rankings remain empty. A single validated Moon-Mars comparison is not an Earth candidate ranking and does not justify settlement or landing recommendations.
