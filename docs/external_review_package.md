# Terra Twin external review package

## Research question

How closely can selected terrain environments approximate the measurable surface morphology of selected lunar or Martian regions using consistent, scale-aware topographic indicators?

## Scientific motivation

Terrain morphology can support transparent analog research, but similarity in terrain distributions does not establish similarity in atmosphere, gravity, radiation, temperature, geology, habitability, or operational safety.

## Data provenance

- Mars: validated USGS/NASA MRO CTX Jezero DTM.
- Moon: validated bounded NASA GSFC PGDA LOLA south-polar COG window with effective-resolution ancillary.
- Earth: NASADEM CMR granules identified but not acquired because Earthdata credentials are unavailable.

See [phase7_scientific_validation_report.md](phase7_scientific_validation_report.md) and [phase6_validation_report.md](phase6_validation_report.md).

## Method

Features are slope, 60 m local relief, and 60 m Riley TRI. Feature distributions use Wasserstein distance, with KS statistics as diagnostics. Distances are normalized by pooled IQR and combined using configurable weights. The official equal-weight index is `TMSI = 100 * exp(-D)`.

Spatial block bootstrap uncertainty, block-size sensitivity, feature ablation, weight sensitivity, normalization diagnostics, and Moran/semivariogram structure are all recorded in [moon_mars_phase7_experiments.json](../data/metadata/moon_mars_phase7_experiments.json).

## Review boundary

The official Moon-Mars result is reproducible, but it is a morphology-distribution result only. Earth comparisons, independent real benchmarks, and complete geomorphological equivalence claims are outside the current evidence.
