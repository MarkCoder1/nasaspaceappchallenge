# Phase 5 validation report

## Verdict: READY WITH LIMITATIONS

Mars and Moon now have validated terrain inputs. Earth NASADEM acquisition is blocked by NASA Earthdata authentication, so Terra Twin is not ready for Earth analog comparisons or all-three-body claims.

## Dataset states

| Dataset                            | State       | Evidence                                                                                                    |
| ---------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------- |
| Mars Jezero CTX DTM                | `VALIDATED` | Existing Phase 3 provenance and QC report; 20 m Mars `ESRI:103885` raster                                   |
| Moon LOLA 80S 20MPP bounded window | `VALIDATED` | PGDA COG range acquisition, DEM/effective-resolution checks, SHA-256 provenance, lunar preprocessing report |
| Earth NASADEM Atacama tiles        | `PENDING`   | Official CMR granules identified; protected download returned HTTP 401 without Earthdata credentials        |

## Processing and validation

- Preserved Mars and Moon native CRS and body-specific coordinate semantics.
- Preserved native 20 m DEM spacing; no upsampling or Earth-to-Moon transform.
- Recorded NASADEM nominal 30 m/1 arc-second and EGM96 reference as pending metadata only.
- Evaluated LOLA effective resolution separately from nominal 20 m spacing.
- Registered raw and processed paths, checksums, source URLs, citations, bounds, dimensions, units, and valid-data percentages.
- Kept raw and processed scientific rasters out of Git while tracking metadata reports.

## Real comparison verified

The live API successfully compared Mars Jezero against the validated lunar LOLA window using slope, 60 m local relief, and 60 m TRI:

- TMSI: `49.92285382858792`
- Confidence: `HIGH`
- Strongest matching features: slope and local relief
- Earth comparison: rejected with HTTP `409`
- Rankings: remain empty

This result is a terrain-morphology index only. It is not a probability, settlement score, landing-site certification, or claim of environmental equivalence.

## API readiness

`GET /api/similarity/status` reports Mars and Moon as `VALIDATED`, Earth as unavailable, and `moon_mars` as the only enabled morphology capability. The frontend displays the pending Earth gate and does not fabricate Earth results.

## Tests and verification

- Full Python suite: `20 passed` after Phase 5 tests.
- Existing Mars smoke test: passed.
- LOLA raw and processed Rasterio validation: passed.
- Provenance SHA-256 checks: passed.
- Effective-resolution compatibility gate: passed.
- Live Moon-Mars comparison: HTTP 200.
- Live Earth comparison rejection: HTTP 409.
- Frontend lint, TypeScript, and production build remain passing from Phase 4 integration.

## Scientific limitations and Phase 6 recommendation

Earth is not locally validated, so Terra Twin must not produce Earth rankings. Phase 6 should authenticate and acquire the CMR-identified NASADEM tiles, process them with EGM96 and latitude-dependent spacing recorded, then enable Earth-Mars/Earth-Moon only after the same quality gates pass.
