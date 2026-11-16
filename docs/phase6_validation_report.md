# Phase 6 validation report

## Verdict: READY WITH LIMITATIONS

Phase 6 implemented secure Earthdata authentication support, exact CMR granule discovery, bounded NASADEM acquisition entry points, spatial uncertainty estimation, and a real validated Moon-Mars experiment. NASADEM itself was not acquired because no Earthdata credentials are available in this environment. Therefore Earth remains `PENDING`, Earth-Moon and Earth-Mars remain disabled, and the definition of done for full three-planet readiness is not met.

## Authentication and acquisition

- `earthaccess 0.19.0` installed and declared in backend requirements.
- Interactive, environment, and netrc strategies supported.
- Credentials remain outside source code and are never logged or exposed to the frontend.
- CMR queried successfully with exact granule IDs and protected distribution URLs.
- Non-interactive environment authentication returned `credentials_unavailable`.
- Protected NASADEM download previously returned HTTP `401` after OAuth redirect.
- No NASADEM file or substitute DEM was written.

Reports: [authentication diagnostic](earthdata_authentication_report.md), [NASADEM acquisition](nasadem_acquisition_report.md).

## Validated datasets

- Mars Jezero CTX DTM: `VALIDATED`, 20 m, Mars `ESRI:103885`.
- Moon PGDA LOLA bounded subset: `VALIDATED`, 2048², native 20 m, Moon south-polar stereographic / DE421, 100% valid.
- Earth NASADEM: `PENDING`.

## Real experiment

The validated Moon-Mars comparison returned:

- TMSI: `49.92285382858792`
- Confidence: `HIGH`
- Primary 320 m block-bootstrap mean: `49.69509289955227`
- 95% spatial uncertainty interval: `[43.719371995087705, 56.79848983967343]`
- Strongest feature matches: slope and local relief

The original Phase 5 TMSI is preserved exactly. The new uncertainty layer does not alter the scoring formula.

## Tests and verification

- Full Python suite: `23 passed`.
- Focused Earthdata/API/bootstrap tests: passed.
- Frontend lint, TypeScript, and production build: passed in the existing integration.
- Live Moon-Mars API comparison: HTTP `200`.
- Live Earth comparison: HTTP `409`.
- API status accurately reports Mars/Moon validated, Earth pending, and only Moon-Mars enabled.
- No production rankings or synthetic results are exposed.

## Remaining limitations

- Earthdata credentials must be configured by a user before NASADEM can be downloaded.
- NASADEM validation, EGM96 handling, metric reprojection, latitude-dependent spacing, Earth feature extraction, Earth-Moon, and Earth-Mars experiments remain pending.
- The current Moon input is a bounded 40.96 km subset, not the complete south-polar parent DEM.
- Bootstrap intervals quantify spatial sampling variability under chosen block assumptions; they are not calibrated probabilities or sensor-error bars.

Phase 7 should begin only after authenticated NASADEM acquisition and Earth validation are complete.
