# Phase 11 External Benchmark Report (Experiment G)

## Objective
Obtain an independently sourced planetary DEM to externally validate the TMSI methodology.

## Status: Not attempted — no suitable independent benchmark available

## Investigation
Candidate source classes considered:
- NASA PDS planetary DEMs.
- USGS planetary products.
- ESA planetary science archives.
- Published planetary geomorphology comparisons.

## Constraints
1. **Earth NASADEM blocked:** Earthdata authentication unavailable (`LoginStrategyUnavailable`; no credentials; protected LP DAAC granules return HTTP 401). No Earth reference obtainable.
2. **Planetary alternatives not independent or too large:**
   - Mars MOLA global 463 m DEM (~2.1 GB) exceeds the bounded downloader's 100 MB limit and is the same mission/instrument family (not independent).
   - No bounded COG subset with range reads was identified for an independent planetary DEM within scope.

## Substitute performed (Phase 10, documented with caveats)
Same-body window-vs-window methodological self-consistency tests on the validated Moon and Mars rasters (same source — NOT independent):
- Non-overlapping same-body windows: TMSI 46.55–58.13.
- Cross-body Moon–Mars baseline (reference, not benchmark): TMSI 49.92.
- These overlap, showing window sampling can dominate body identity.

## Benchmark availability
`benchmark_available: false`. No independently labeled real-world benchmark dataset was obtained.
Synthetic benchmarks (existing `benchmark_registry.json`) are marked `synthetic_test_only,
production_eligible=false` and excluded from scientific findings.

## Limitation
Independent external validation of TMSI against a published reference or independently sourced
DEM remains pending. Suitable candidates: a publicly downloadable, bounded, independently
processed planetary DEM with documented CRS, resolution, provenance, and relevance to terrain
morphology comparison.
