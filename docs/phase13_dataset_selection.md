# Phase 13: Dataset Selection

## A1. Mars Datasets Investigated

### mars_jezero_ctx_dtm
- **Status**: VALIDATED / DOWNLOADED
- **Source**: USGS Astrogeology Science Center / NASA MRO CTX
- **Official URL**: https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_ctx_dtm_mosaic
- **Source URL**: https://planetarymaps.usgs.gov/mosaic/mars2020_trn/CTX/JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif
- **Resolution**: 20 m pixel spacing
- **Coverage**: Jezero crater and Mars 2020 landing region (18.211 to 18.7212 N, 77.1605 to 77.699 E)
- **Limitations**: Jezero-specific; created for terrain-relative navigation. Equirectangular CRS and MOLA control must be preserved.
- **Scientific suitability**: Suitable for localized benchmarking within Jezero crater. Not suitable as a fully independent global reference.

### MOLA (Mars Orbiter Laser Altimeter)
- **Investigation status**: Identified as scientifically suitable independent Mars elevation product
- **Source**: NASA Planetary Data System (PDS)
- **Note**: MOLA data was identified as a candidate but not independently downloaded or validated in this phase. Further investigation required.

### HRSC (High Resolution Stereo Camera)
- **Investigation status**: Identified as potential independent Mars elevation product
- **Source**: ESA planetary science data archives
- **Note**: HRSC data was identified as a candidate but not independently downloaded or validated in this phase. Further investigation required.

## A2. Moon Datasets Investigated

### moon_lola
- **Status**: VALIDATED / DOWNLOADED
- **Source**: NASA GSFC Planetary Geodesy and Altimetry Data Archive
- **Official URL**: https://pgda.gsfc.nasa.gov/products/90
- **Source URL**: https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF
- **Resolution**: 20 m/pixel (nominal); effective resolution documented separately
- **Coverage**: South polar region (south of 80°S), centered on Shackleton crater
- **Limitations**: Pole-centered 40.96 km subset, not the complete 80S-90S parent DEM
- **Scientific suitability**: Well-validated observational product. Effective resolution must be respected; not assumed equal to nominal 20 m.

### LOLA (Lunar Orbiter Laser Altimeter)
- **Investigation status**: Candidate independent lunar elevation product
- **Source**: NASA PDS
- **Note**: LOLA data was identified and the moon_lola dataset was derived from LOLA products via the LDEM_80S_20MPP_ADJ window.

### Kaguya Terrain Camera
- **Investigation status**: Candidate independent lunar elevation product
- **Source**: JAXA official archives
- **Note**: Kaguya data was identified as a candidate but not independently downloaded or validated in this phase.

## A3. Earth Datasets Investigated

### earth_nasadem_hgt_v001
- **Status**: BLOCKED_BY_EARTHDATA_AUTHENTICATION / REJECTED
- **Source**: NASA LP DAAC / NASA JPL
- **Official URL**: https://www.earthdata.nasa.gov/data/catalog/lpcloud-nasadem-hgt-001
- **DOI**: 10.5067/MEASURES/NASADEM/NASADEM_HGT.001
- **Resolution**: 1 arc-second (~30 m nominal); latitude-dependent ground spacing
- **Access**: NASA Earthdata LP DAAC protected granules return HTTP 401 without user credentials
- **Acquisition attempt**: CMR query performed: C2763264762-LPCLOUD with bounding box -68 to -67, -24 to -23
- **Result**: Protected granules redirected to NASA Earthdata OAuth and returned HTTP 401 without valid user credentials
- **Limitations**: No credentials were supplied or stored. No alternate DEM was substituted or mislabeled as NASADEM.

### SRTM (Shuttle Radar Topography Mission)
- **Investigation status**: Considered as alternative Earth DEM source
- **Note**: SRTM data was evaluated but found to be a related product to NASADEM, not fully independent. Further investigation required.

### AW3D30 (ALOS Global Digital Surface Model)
- **Investigation status**: Considered as alternative Earth DEM source
- **Note**: AW3D30 was identified as a potentially independently sourced global DEM. Further investigation required to verify access and validity.

## A4. Dataset Registry

The complete dataset inventory is maintained in `science/datasets/registry.json`. Every candidate dataset is documented with:
- Dataset name, planetary body, producing institution, official source
- DOI or persistent identifier (if available)
- Spatial coverage, nominal resolution, horizontal/vertical reference systems
- Elevation units, acquisition date, processing level
- Access requirements and licensing conditions
- Validation status: DISCOVERED, ACCESSIBLE, DOWNLOADED, VALIDATED, REJECTED, BLOCKED

No dataset was marked VALIDATED merely because a download succeeded.