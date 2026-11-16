# Earth NASADEM validation report

## Decision: PENDING

NASADEM remains unavailable for local validation because the official Atacama ROI granule requires NASA Earthdata authentication. No alternate DEM was substituted.

## Target ROI

The selected Earth candidate is the Atacama volcanic high desert near 23.0 S, 67.75 W. The CMR query identified the relevant 1-degree granules, including `NASADEM_HGT_s23w068` and neighboring tiles needed to avoid edge ambiguity.

## Official source

- Product: NASADEM Merged DEM Global 1 arc second V001
- DOI: [10.5067/MEASURES/NASADEM/NASADEM_HGT.001](https://doi.org/10.5067/MEASURES/NASADEM/NASADEM_HGT.001)
- Documentation: [NASADEM User Guide V1.3](https://lpdaac.usgs.gov/documents/2237/NASADEM_User_Guide_V13.pdf)
- Catalog: [NASA Earthdata product page](https://www.earthdata.nasa.gov/data/catalog/lpcloud-nasadem-hgt-001)
- CMR collection: `C2763264762-LPCLOUD`

NASA documents 1 arc-second HGT tiles, approximately 30 m nominal spacing, global land coverage from 60 N to 56 S, and EGM96-referenced elevation. Ground spacing varies with latitude and must not be treated as a constant 30 m physical footprint.

## Acquisition result

CMR returned the official protected distribution URL for the Atacama tile. A request without credentials redirected to NASA Earthdata OAuth and returned HTTP `401 Unauthorized`. No ZIP, HGT, or fabricated Earth raster was written to `data/raw/`.

The attempted acquisition and required tiles are recorded in [earth_nasadem_hgt_v001.json](../data/metadata/earth_nasadem_hgt_v001.json).

## Consequence

Earth-Mars and Earth-Moon comparisons remain disabled. NASADEM can be acquired later by a user with Earthdata access, then validated with the existing ingestion/preprocessing pipeline before any Earth analog result is enabled.
