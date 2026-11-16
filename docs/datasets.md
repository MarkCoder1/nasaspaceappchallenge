# TerraMatch dataset catalog

## Scope and selection rule

Phase 2 selects a small, traceable collection for terrain-first preprocessing. The collection does not claim that equal variable names imply equal physical meaning. Earth, Moon, and Mars datasets differ in gravity, body shape, illumination, sensors, calibration, coordinate conventions, and observation time.

## Dataset evaluation table

| Field            | Dataset                                     | Planet | Institution                         | Variable                                        | Units                                          | Resolution                             | Format                   | Coverage                           | Access method                                            | Official URL                                                                                                  | Suitability                               | Limitations                                                                                                        |
| ---------------- | ------------------------------------------- | ------ | ----------------------------------- | ----------------------------------------------- | ---------------------------------------------- | -------------------------------------- | ------------------------ | ---------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Terrain          | NASADEM Merged DEM Global 1 arc second V001 | Earth  | NASA LP DAAC / JPL                  | Elevation                                       | metres                                         | 30 m                                   | HGT or NetCDF4           | 60 N to 56 S global land           | Earthdata Login and granule download                     | [Earthdata catalog](https://www.earthdata.nasa.gov/data/catalog/lpcloud-nasadem-hgt-001)                      | **Essential** Earth terrain baseline      | Does not cover polar Earth; vertical datum and Earth-versus-planet body shape must be documented                   |
| Terrain          | LOLA data products                          | Moon   | NASA Goddard / PDS Geosciences Node | Topography                                      | metres for elevation products                  | Product-dependent, multiple scales     | PDS and derived rasters  | Moon, including south pole         | PDS/ODE query and download                               | [LOLA archive](https://pds-geosciences.wustl.edu/missions/lro/lola.htm)                                       | **Essential** lunar terrain source        | A specific product, projection, scale, and label must be selected; no guessed direct URL is used                   |
| Terrain          | Mars 2020 CTX DTM Mosaic                    | Mars   | USGS Astrogeology / NASA MRO CTX    | Elevation                                       | metres                                         | 20 m pixel spacing                     | GeoTIFF                  | Jezero / Mars 2020 region          | Direct public download                                   | [USGS product](https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_ctx_dtm_mosaic) | **Essential** bounded Mars terrain raster | Equirectangular planetary map; MOLA control; made for navigation and not a global Mars DEM                         |
| Terrain context  | MOLA global DEM mosaic                      | Mars   | USGS Astrogeology / NASA MGS MOLA   | Elevation                                       | metres                                         | 463 m named product resolution         | GeoTIFF                  | Global Mars                        | Direct public download, but regional extraction required | [USGS mosaic](https://planetarymaps.usgs.gov/mosaic/Mars_MGS_MOLA_DEM_mosaic_global_463m.tif)                 | Optional common-scale context             | Verified file is about 2.1 GB, so the acquisition script refuses it by default                                     |
| Thermal          | MODIS/Terra MOD11A2 V061                    | Earth  | NASA LP DAAC / GSFC                 | Land surface temperature and emissivity         | Kelvin after scale factor; emissivity unitless | 1 km; 8-day composite                  | HDF-EOS2                 | Global                             | Earthdata Login and granule download                     | [Earthdata catalog](https://www.earthdata.nasa.gov/data/catalog/lpcloud-mod11a2-061)                          | Optional Earth thermal context            | Not equivalent to Mars THEMIS or lunar Diviner; quality flags, emissivity, clouds, and acquisition time matter     |
| Thermal          | THEMIS archive                              | Mars   | NASA / JPL / ASU / PDS              | Visible and thermal infrared observations       | Product-dependent                              | Product-dependent                      | PDS and derived products | Mars                               | Mars ODE/PDS search                                      | [NASA Odyssey](https://science.nasa.gov/mission/odyssey/) and [Mars ODE](https://ode.rsl.wustl.edu/mars/)     | Optional only after product selection     | “Thermal” is not a single comparable variable; product labels and calibration must be checked                      |
| Thermal          | Diviner archive                             | Moon   | NASA / JPL / PDS Geosciences Node   | Infrared radiance and derived temperatures      | Product-dependent                              | Product-dependent                      | PDS archive              | Moon, including polar observations | PDS/ODE search                                           | [Diviner archive](https://pds-geosciences.wustl.edu/missions/lro/diviner.htm)                                 | Research source, excluded from MVP        | Viewing geometry, emissivity, channel gaps, and brightness-temperature semantics prevent an unqualified comparison |
| Surface property | Unified Geologic Map of the Moon, 1:5M      | Moon   | USGS Astrogeology                   | Categorical geologic units and linework         | Map scale; categorical attributes              | About 3 km vertex spacing at map scale | GIS ZIP/vector           | Global Moon                        | Direct public ZIP                                        | [USGS map](https://astrogeology.usgs.gov/search/map/unified_geologic_map_of_the_moon_1_5m_2020)               | Optional interpretation context           | Not continuous physical data and not a substitute for elevation; download is about 214 MB                          |
| Thermal inertia  | MGS TES archive                             | Mars   | NASA PDS Geosciences Node           | TES observations and derived thermal properties | Product-dependent                              | Product-dependent                      | PDS archive              | Mars                               | PDS/ODE search                                           | [MGS archive](https://pds-geosciences.wustl.edu/missions/mgs/)                                                | Excluded from MVP                         | A specific product, units, grid, and bounded Jezero/Gale subset still require validation                           |

All records are mirrored in the typed catalog at [science/data_ingestion/dataset_catalog.py](../science/data_ingestion/dataset_catalog.py). The catalog records access status honestly: `download_url` is empty for Earthdata/PDS records until a product and credentials are available.

## Minimum viable collection

1. **Earth:** NASADEM tiles for the three Earth regions, subject to Earthdata access. NASADEM is 30 m, global land between 60 N and 56 S, and distributed in 1-degree HGT tiles.
2. **Moon:** one explicitly selected LOLA product covering the south polar working window. The product and projection must be fixed through ODE before download.
3. **Mars:** the acquired Jezero CTX DTM, 20 m GeoTIFF, as a bounded high-resolution terrain source.

Terrain-derived slope and roughness are deferred to Phase 3. They will be computed from each raster in its native body-fixed coordinate system, not copied from an unverified external field.

## Acquired file

The USGS Jezero CTX DTM is the only science raster acquired in this phase. Its 9.3 MB official size, 20 m pixel spacing, elevation units, bounds, equirectangular projection, and MOLA control are documented on the product page. Its SHA-256 and raster-readable metadata are stored in `data/metadata/mars_jezero_ctx_dtm.json` after running the downloader.

## Access and reproducibility

```bash
cd /path/to/nasaspaceapp
source backend/.venv/bin/activate
PYTHONPATH=. python -m science.data_ingestion.download_data mars_jezero_ctx_dtm
PYTHONPATH=. python -m science.data_ingestion.validate_data data/raw/JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif data/metadata/mars_jezero_ctx_dtm.json
```

The downloader never silently replaces raw data, leaves no successful `.part` file, enforces a 100 MB default, and writes provenance only after a complete transfer. NASA Earthdata Login credentials are not stored in this repository.

## Excluded or deferred

- Global MOLA and high-resolution HiRISE mosaics are too large for an unbounded two-day acquisition; use regional extracts or the bounded CTX product.
- MODIS, THEMIS, Diviner, and TES require product-level temporal, calibration, and unit decisions before cross-body use.
- Lunar geology is context, not a continuous analog variable.
- No dataset supports a claim that an Earth site is physically equivalent to a lunar or Martian surface.

## Phase 5 acquisition state

- **Mars:** `VALIDATED`; the Phase 3 Jezero CTX DTM remains the production Mars source.
- **Moon:** `VALIDATED`; the official PGDA `LDEM_80S_20MPP_ADJ.TIF` parent is accessed as a bounded 40.96 km pole-centered COG window. The local raw and processed subsets, effective-resolution ancillary, checksums, and Barker et al. citation are recorded in `data/metadata/moon_lola.json` and `data/metadata/moon_lola_preprocessing.json`.
- **Earth:** `PENDING`; CMR identified the Atacama tiles, but the official protected distribution requires Earthdata OAuth and returned HTTP 401 without credentials. No substitute DEM was acquired.
