# Phase 10 External Benchmark Report (Workstream E)

## Objective
Obtain an independent real-world benchmark to evaluate the TMSI methodology externally.

## Status: Not attempted — no suitable independent benchmark available

## Investigation
Candidate source classes considered:
- NASA PDS / USGS planetary DEMs.
- ESA planetary science archives.
- Published planetary geomorphology comparisons.
- Independently processed DEMs.

## Constraint: Earth data blocked
Earth NASADEM acquisition is blocked by Earthdata authentication (HTTP 401, no credentials). No Earth reference can be obtained.

## Constraint: planetary alternatives
Alternative planetary DEMs (e.g., Mars MOLA global 463 m) are either:
- the same mission/instrument family (not independent), or
- too large for the bounded downloader (MOLA global ≈ 2.1 GB; downloader refuses >100 MB), or
- not available as a bounded COG subset for range reads.

## Substitute performed: methodological self-consistency (same source, caveated)
Because no independent source was available, same-body window-vs-window comparisons of the validated Moon and Mars rasters were run as a methodological self-consistency check (documented in `phase10_benchmark_investigation.json`):

| Comparison | Overlap | TMSI | Note |
|---|---|---|---|
| Moon center vs northwest (20.48 km) | yes | 58.1318 | overlap inflates |
| Moon center vs southeast (20.48 km) | yes | 83.3207 | overlap inflates |
| Moon northwest vs southeast (20.48 km) | no | 54.8968 | non-overlapping |
| Mars center vs northwest (10.24 km) | yes | 56.1800 | overlap inflates |
| Mars center vs southeast (10.24 km) | yes | 65.5092 | overlap inflates |
| Mars northwest vs southeast (10.24 km) | no | 46.5452 | non-overlapping |
| Cross-body Moon vs Mars (ref) | n/a | 49.9229 | Phase 7 baseline |

Interpretation: Non-overlapping same-body windows (46.55–58.13) fall in the same range as cross-body Moon–Mars (49.92). Window location/extent can dominate body identity. Overlap inflates similarity. This is a self-consistency check on the same rasters, NOT an independent external benchmark.

## Benchmark availability
`benchmark_available: false`. No independently labeled real-world benchmark dataset was obtained. Synthetic benchmarks (existing `benchmark_registry.json`) are marked `synthetic_test_only, production_eligible=false` and excluded from scientific findings.

## Limitation
Independent external validation of TMSI against a published reference or independently sourced DEM remains pending. Suitable candidates: a publicly downloadable, bounded, independently processed planetary DEM with documented CRS/resolution/provenance.
