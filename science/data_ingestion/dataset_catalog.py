"""Traceable dataset records used by the TerraMatch acquisition pipeline."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class DatasetSpec:
    id: str
    name: str
    planet: str
    institution: str
    variable: str
    units: str
    resolution: str
    format: str
    coverage: str
    official_url: str
    access_method: str
    download_url: str | None
    license_or_access: str
    suitability: str
    limitations: str
    selected: bool = False
    state: str = "PENDING"


CATALOG: tuple[DatasetSpec, ...] = (
    DatasetSpec(
        id="earth_nasadem_hgt_v001",
        name="NASADEM Merged DEM Global 1 arc second V001",
        planet="Earth",
        institution="NASA LP DAAC / NASA JPL",
        variable="Elevation",
        units="meters; HGT samples use the product's vertical datum",
        resolution="30 m x 30 m",
        format="HGT tiles or NetCDF4",
        coverage="Global land between 60 N and 56 S",
        official_url="https://www.earthdata.nasa.gov/data/catalog/lpcloud-nasadem-hgt-001",
        access_method="Earthdata search/download; Earthdata Login required for granule access",
        download_url=None,
        license_or_access="Openly shared under NASA EOSDIS data guidance; account required for access",
        suitability="Essential Earth elevation baseline for candidate regions within coverage",
        limitations="Does not cover polar Earth candidates; 30 m Earth pixels are not directly equivalent to planetary products",
        selected=True,
        state="PENDING",
    ),
    DatasetSpec(
        id="earth_mod11a2_v061",
        name="MODIS/Terra Land Surface Temperature/Emissivity 8-Day L3 Global 1km SIN Grid V061",
        planet="Earth",
        institution="NASA LP DAAC / NASA GSFC",
        variable="Daytime and nighttime land surface temperature and emissivity",
        units="Kelvin after applying the product scale factor; emissivity is unitless",
        resolution="1 km x 1 km; 8-day composite",
        format="HDF-EOS2",
        coverage="Global land",
        official_url="https://www.earthdata.nasa.gov/data/catalog/lpcloud-mod11a2-061",
        access_method="Earthdata search/download; Earthdata Login required for granule access",
        download_url=None,
        license_or_access="Openly shared under NASA EOSDIS data guidance; account required for granule access",
        suitability="Optional Earth thermal context with explicit temporal compositing",
        limitations="Orbital thermal observations are not equivalent to Mars THEMIS or lunar Diviner; cloud and emissivity quality flags must be honored",
    ),
    DatasetSpec(
        id="moon_lola",
        name="Lunar Orbiter Laser Altimeter (LOLA) data products",
        planet="Moon",
        institution="NASA Goddard / PDS Geosciences Node",
        variable="Lunar surface topography and related altimetry products",
        units="meters for elevation products; product-specific units for derived fields",
        resolution="Product-dependent; LOLA global topography is available at multiple scales",
        format="PDS products and derived raster products",
        coverage="Moon, including the south polar region",
        official_url="https://pds-geosciences.wustl.edu/missions/lro/lola.htm",
        access_method="PDS Geosciences Node or Lunar Orbital Data Explorer query/download",
        download_url="https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF",
        license_or_access="NASA PDS archive; cite the LOLA Science Team and product documentation",
        suitability="Essential lunar terrain source; supports slope and roughness derivation after product selection",
        limitations="Product selection and map projection must be fixed before comparing with Earth or Mars; no single guessed global URL is used",
        selected=True,
        state="VALIDATED",
    ),
    DatasetSpec(
        id="moon_unified_geology_v2",
        name="Unified Geologic Map of the Moon, 1:5M, 2020",
        planet="Moon",
        institution="USGS Astrogeology Science Center",
        variable="Mapped lunar geologic units and linework",
        units="Map scale 1:5,000,000; vector attributes are categorical",
        resolution="Approximately 3 km vertex spacing at map scale; not a DEM",
        format="GIS ZIP with vector layers and documentation",
        coverage="Global Moon",
        official_url="https://astrogeology.usgs.gov/search/map/unified_geologic_map_of_the_moon_1_5m_2020",
        access_method="Direct public ZIP download",
        download_url="https://asc-astropedia.s3.us-west-2.amazonaws.com/Moon/Geology/Unified_Geologic_Map_of_the_Moon_GIS_v2.zip",
        license_or_access="CC0; cite the authors and USGS",
        suitability="Optional geology context for interpreting analogs, not a substitute for elevation",
        limitations="Categorical map units cannot be treated as continuous physical measurements; full ZIP is about 214 MB",
    ),
    DatasetSpec(
        id="mars_jezero_ctx_dtm",
        name="Mars 2020 Terrain Relative Navigation CTX DTM Mosaic",
        planet="Mars",
        institution="USGS Astrogeology Science Center / NASA MRO CTX",
        variable="Digital terrain elevation",
        units="meters",
        resolution="20 m pixel spacing",
        format="GeoTIFF",
        coverage="Jezero crater and Mars 2020 landing region; 18.211 to 18.7212 N, 77.1605 to 77.699 E",
        official_url="https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_ctx_dtm_mosaic",
        access_method="Direct public download",
        download_url="https://planetarymaps.usgs.gov/mosaic/mars2020_trn/CTX/JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif",
        license_or_access="No access constraints; cite USGS authors",
        suitability="Essential bounded Mars terrain raster for the first reproducible study region",
        limitations="Jezero-specific and created for terrain-relative navigation; its equirectangular planetary CRS and MOLA control must be preserved",
        selected=True,
        state="VALIDATED",
    ),
    DatasetSpec(
        id="mars_mola_global",
        name="Mars MGS MOLA DEM mosaic global 463 m",
        planet="Mars",
        institution="USGS Astrogeology Science Center / NASA MGS MOLA",
        variable="Global Martian topography",
        units="meters",
        resolution="463 m product named resolution",
        format="GeoTIFF",
        coverage="Global Mars",
        official_url="https://planetarymaps.usgs.gov/mosaic/Mars_MGS_MOLA_DEM_mosaic_global_463m.tif",
        access_method="Direct public download; bounded regional extraction is required before use",
        download_url="https://planetarymaps.usgs.gov/mosaic/Mars_MGS_MOLA_DEM_mosaic_global_463m.tif",
        license_or_access="Public USGS/NASA product; cite source documentation",
        suitability="Optional common-scale Mars context and source for broader candidate regions",
        limitations="Verified content length is about 2.1 GB; the acquisition tool refuses it by default to avoid an unbounded hackathon download",
    ),
    DatasetSpec(
        id="mars_tes_thermal_inertia",
        name="Mars Global Surveyor Thermal Emission Spectrometer data products",
        planet="Mars",
        institution="NASA PDS Geosciences Node",
        variable="Thermal infrared observations and derived surface thermal properties",
        units="Product-dependent; thermal inertia products require label-level unit verification",
        resolution="Product-dependent",
        format="PDS archive products",
        coverage="Mars, product-dependent",
        official_url="https://pds-geosciences.wustl.edu/missions/mgs/",
        access_method="PDS archive and Mars Orbital Data Explorer",
        download_url=None,
        license_or_access="NASA PDS archive; cite product documentation",
        suitability="Optional research path for thermal inertia after a specific product and label are selected",
        limitations="Not selected for the minimum viable collection because product-level units, grids, and a bounded Jezero/Gale subset require additional validation",
    ),
    DatasetSpec(
        id="mars_themis_archive",
        name="Mars Odyssey Thermal Emission Imaging System (THEMIS) archive",
        planet="Mars",
        institution="NASA / JPL / Arizona State University / PDS",
        variable="Visible and thermal-infrared image observations",
        units="Product-dependent; temperature products require label-level verification",
        resolution="Product-dependent; observation and map products differ",
        format="PDS archive products and derived map products",
        coverage="Mars, product-dependent",
        official_url="https://science.nasa.gov/mission/odyssey/",
        access_method="Mars Orbital Data Explorer and PDS archive",
        download_url=None,
        license_or_access="NASA PDS archive; cite instrument and product documentation",
        suitability="Optional thermal or surface-context source after selecting a specific product",
        limitations="THEMIS visible/infrared observations, MODIS LST, and Diviner brightness temperatures are different measurements and cannot be equated without calibration and temporal matching",
    ),
    DatasetSpec(
        id="moon_diviner_archive",
        name="LRO Diviner Lunar Radiometer Experiment archive",
        planet="Moon",
        institution="NASA / JPL / PDS Geosciences Node",
        variable="Lunar infrared radiance and derived temperature products",
        units="Product-dependent temperature and radiance units",
        resolution="Product-dependent orbital observations and derived grids",
        format="PDS archive products",
        coverage="Moon, including polar terrain and permanently shadowed region observations where available",
        official_url="https://pds-geosciences.wustl.edu/missions/lro/diviner.htm",
        access_method="PDS Geosciences Node and Lunar Orbital Data Explorer",
        download_url=None,
        license_or_access="NASA PDS archive; cite Diviner product documentation",
        suitability="Research source for lunar thermal context, not part of the minimum viable comparison",
        limitations="Brightness temperature and surface temperature depend on channels, viewing geometry, emissivity, and missing-data flags; the archive page documents post-2019 channel data gaps",
    ),
)


def get_dataset(dataset_id: str) -> DatasetSpec:
    for dataset in CATALOG:
        if dataset.id == dataset_id:
            return dataset
    raise KeyError(f"Unknown dataset: {dataset_id}")


def catalog_as_dicts() -> list[dict[str, Any]]:
    return [asdict(dataset) for dataset in CATALOG]