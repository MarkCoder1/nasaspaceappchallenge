# Lunar LOLA validation report

## Decision: VALIDATED WITH LIMITATIONS

The preferred NASA GSFC PGDA `LDEM_80S_20MPP_ADJ.TIF` product was accessed through its official Cloud-Optimized GeoTIFF and a bounded south-polar window was acquired. The complete 2.6 GB parent DEM was not downloaded.

## Source and citation

- Product page: [PGDA product 90](https://pgda.gsfc.nasa.gov/products/90)
- Parent source: [PGDA product 81](https://pgda.gsfc.nasa.gov/products/81)
- DEM: [LDEM_80S_20MPP_ADJ.TIF](https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF)
- Effective resolution: [LDEM_80S_20MPP_ADJ_EFFRES.TIF](https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ_EFFRES.TIF)
- Required citation: Barker et al., 2023, _Planetary Science Journal_, 4, 183, [DOI 10.3847/PSJ/acf3e1](https://doi.org/10.3847/PSJ/acf3e1)
- Data DOI: [10.60903/gsfcpgda-lola-spole](https://doi.org/10.60903/gsfcpgda-lola-spole)

## Acquired subset

- Raw DEM: `data/raw/moon_lola_80s_20m_shackleton_window.tif`
- Processed DEM: `data/processed/moon_lola_80s_20m_elevation_m.tif`
- Window: `[-20480, -20480, 20480, 20480]` metres in native south-polar stereographic coordinates
- Dimensions: `2048 x 2048`
- Native spacing: `20 m/pixel`
- Valid coverage: `100%`
- Elevation range: `-2872.114` to `1959.418 m`
- CRS: Moon 2015 Sphere / Ocentric / South Polar, MOON_ME DE421 reference frame

The source page documents south-polar stereographic X/Y metres and the DE421 reference frame. No Earth-to-Moon coordinate transform was applied.

## Effective resolution

The official effective-resolution COG was read through a 64x overview over the same window because a full-resolution remote tile read failed and the parent file is approximately 3.97 GB. The resulting 32 x 32 ancillary has 100% valid coverage, a mean effective-resolution value of `16.056 m`, and a range of `12.130` to `23.840 m`. This is recorded as an ancillary overview, not as a claim that every DEM pixel has 16 m effective resolution.

## Provenance and processing

Complete source URLs, parent size, window coordinates, SHA-256 checksums, CRS, statistics, citation, and limitations are in [moon_lola.json](../data/metadata/moon_lola.json). The validation/preprocessing record is [moon_lola_preprocessing.json](../data/metadata/moon_lola_preprocessing.json).

## Limitations

- This is a 40.96 km pole-centered subset, not the complete 80S-90S parent DEM.
- LOLA construction includes adjusted/blended/interpolated product behavior documented by PGDA.
- Effective resolution is ancillary information and must be considered separately from nominal pixel spacing.
- The subset supports morphology-only Moon-Mars comparison; it does not establish physical, thermal, gravitational, or operational equivalence.
