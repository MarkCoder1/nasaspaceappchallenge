# Similarity API

## Readiness

`GET /api/similarity/status` returns dataset states, enabled pairings, pending datasets, and reasons. Current readiness is:

- Mars: `VALIDATED`
- Moon: `VALIDATED`
- Earth: `PENDING`
- Enabled: `moon_mars`
- Disabled: `earth_moon`, `earth_mars`

## Endpoints

- `GET /api/similarity/status`
- `GET /api/similarity/features`
- `GET /api/similarity/methodology`
- `GET /api/similarity/results`
- `POST /api/similarity/compare`

The compare response includes feature distances, Wasserstein and KS diagnostics, TMSI, confidence, provenance, spatial block-bootstrap uncertainty, and block-size sensitivity. Unsupported pairings return HTTP `409`; rankings remain empty.
