# NASA Earthdata authentication diagnostic

## Result: CREDENTIALS UNAVAILABLE

The preferred `earthaccess` client is installed at version `0.19.0`. The configured non-interactive `environment` strategy was run without prompting and returned `LoginStrategyUnavailable`. No username, password, token, cookie, or authorization header was logged or persisted.

The diagnostic is stored in [earthdata_authentication_diagnostic.json](../data/metadata/earthdata_authentication_diagnostic.json). The acquisition command supports:

```bash
PYTHONPATH=. python -m science.data_ingestion.acquire_nasadem --strategy environment
PYTHONPATH=. python -m science.data_ingestion.acquire_nasadem --strategy netrc
PYTHONPATH=. python -m science.data_ingestion.acquire_nasadem --login --strategy interactive
```

Interactive login is intentionally not invoked by this automated run because it would require user input. Credentials remain outside source control and are not exposed through the frontend.

## Failure classification

- Earthdata client: installed
- CMR metadata: reachable and successfully queried
- Granule URLs: identified and protected
- Credential state: unavailable
- Network failure: not indicated
- Corrupt download: not applicable; no download was attempted
- Unauthorized endpoint: previously confirmed with HTTP `401` after OAuth redirect

## Security behavior

Authentication code uses `earthaccess`, never hardcodes secrets, never prints secret values, and uses the project CA bundle for CMR HTTPS requests.
