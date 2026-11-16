# Phase 3 preprocessing report

## Verdict: READY WITH LIMITATIONS

The verified Jezero CTX DTM was successfully inspected, validated, and transformed into an analysis-ready Mars elevation raster without changing the source observation. The project is not ready for unrestricted Earth-Moon-Mars similarity work because NASADEM and a selected LOLA product have not been acquired, and temperature/geology products remain product-selection dependent.

## Dataset successfully processed

| Dataset                                              | Body | Variable  | Source                                                                                                        | Status                 |
| ---------------------------------------------------- | ---- | --------- | ------------------------------------------------------------------------------------------------------------- | ---------------------- |
| Mars 2020 Terrain Relative Navigation CTX DTM Mosaic | Mars | Elevation | [USGS product](https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_ctx_dtm_mosaic) | Processed successfully |

Raw provenance is recorded in [mars_jezero_ctx_dtm.json](../data/metadata/mars_jezero_ctx_dtm.json). The raw GeoTIFF remains unchanged in `data/raw/`.

## Inspection and QC findings

- Raw format: GeoTIFF, one `float32` band, `1512 x 1596` pixels.
- Original nodata declaration: `-3.4028226550889045e+38`.
- Observed missing pixels: `0`; valid pixels: `2,413,152` (`100.0%`).
- Observed finite range: `-2710.69580078125` to `-1515.53955078125` metres.
- Original checksum: Rasterio band checksum `19489`; SHA-256 is recorded in the provenance JSON.
- Duplicate-value check: unique-value and duplicate-value percentages are emitted in the QC report; repeated floating-point elevations are not treated as corruption.
- File readability: Rasterio opened the raw and processed products successfully.

The complete machine-readable report is [mars_jezero_ctx_preprocessing.json](../data/metadata/mars_jezero_ctx_preprocessing.json).

## Operations performed

1. Validated one-band structure, finite valid values, Mars CRS, metres, and native 20 m resolution.
2. Preserved `ESRI:103885`, its Mars 2000 Equirectangular WKT, affine transform, bounds, dimensions, and 20 m spacing.
3. Preserved the original float32 elevation values exactly.
4. Converted the source nodata sentinel into `NaN` plus an internal GeoTIFF mask. No observed pixel was removed or filled.
5. Wrote a DEFLATE-compressed processed GeoTIFF.

## Units and resolution

Elevation remained in metres using the identity formula `elevation_m = elevation_m`. No temperature conversion was applied because no temperature raster was acquired. No resampling was performed; native 20 m spacing was retained to avoid unsupported detail or scale mixing.

## Coordinates

The processed raster retains the source Mars 2000 spherical equirectangular CRS (`ESRI:103885`). Its coordinates are not transformed into Earth longitude/latitude semantics. The original CRS WKT and planetary notes are stored in the report.

## Normalized variables

No normalized scientific variable was created. A reusable min-max utility is tested for future within-dataset diagnostic use, but it is not applied to the production raster and must not be interpreted as physical equivalence.

## Excluded datasets

- NASADEM: catalogued but Earthdata access and granule acquisition are still pending.
- LOLA: catalogued, but a specific south-polar product, grid, projection, and download have not been selected.
- MOLA global: approximately 2.1 GB and intentionally not downloaded; a regional extract is preferable.
- MODIS, THEMIS, Diviner, and TES: measurement methods and product-level units/quality flags are not harmonized enough for this phase.
- Lunar geology: useful categorical context, not a continuous terrain variable.

## Comparability result

The conservative variable classifications are documented in [comparability_matrix.md](comparability_matrix.md). Elevation, slope, and roughness are `CONDITIONAL`; temperature, thermal inertia, reflectance, and geological units are `NOT COMPARABLE` for direct use with the currently available inputs. QA masks are `DIRECT` only as metadata conventions, not as similarity variables.

## Tests and generated files

- Full Python suite: `7 passed` with `PYTHONPATH=. backend/.venv/bin/pytest -q`.
- Existing raw smoke test: use `backend/.venv/bin/python test_datasets.py`; the bare `python` command is unavailable in this environment.
- Generated raster: `data/processed/mars_jezero_ctx_elevation_m.tif`.
- Generated QC report: `data/metadata/mars_jezero_ctx_preprocessing.json`.
- Test coverage: raster loading, metadata extraction, nodata detection, CRS preservation, native resolution, unit conversion, masking, normalization behavior, and processed-file integrity.

## Recommendation for Phase 4

Acquire and product-select one NASADEM tile set and one LOLA south-polar terrain product, then repeat this pipeline separately for Earth and Moon. Only after body-aware terrain derivatives have been validated should Phase 4 define the similarity methodology. Do not compare raw cross-body elevation values or add thermal variables until product-level calibration and temporal semantics are documented.
