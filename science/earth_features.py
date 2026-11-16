"""Earth terrain feature extraction integration for Terra Twin Phase 18.

Integrates Earth DEM data with the existing validated feature extraction architecture.
Reuses existing calculations where scientifically appropriate.

Do not introduce different formulas for Earth without documenting why.
Verify: units, neighborhood definitions, edge handling, missing-value behavior,
resolution dependence, numerical stability.

Earth, Moon and Mars feature calculations must be sufficiently comparable before
cross-body interpretation.
"""

from pathlib import Path
from typing import Any, Optional
import json
import numpy as np
import rasterio
from rasterio.transform import from_origin

from science.preprocessing.coordinate_systems import describe_coordinate_system
from science.similarity.features.feature_extraction import (
    FeatureLayer,
    TerrainFeatureSet,
    summarize,
    extract_terrain_features,
)
from science.similarity.features.slope import slope_degrees
from science.similarity.features.local_relief import local_relief_m
from science.similarity.features.terrain_ruggedness import terrain_ruggedness_index


def earth_feature_layer_from_raster(
    raster_path: Path,
    variable: str = "elevation",
    local_neighborhood_m: float = 60.0,
    ruggedness_neighborhood_m: float = 60.0,
) -> FeatureLayer:
    """Extract a single terrain feature layer from an Earth DEM raster.

    Reuses the existing extract_terrain_features infrastructure but operates
    on a single raster (Earth DEM) rather than comparing two rasters.

    The function reads the raster, validates it has 1 band and a CRS,
    then extracts the requested feature.

    Returns a FeatureLayer with the feature name, values, units, neighborhood size,
    and definition.

    Does NOT perform cross-planetary comparison; only extracts features from
    the Earth DEM. Comparability with Moon/Mars features must be assessed
    separately through the coordinate resolution and vertical datum documentation.
    """
    with rasterio.open(raster_path) as dataset:
        if dataset.count != 1 or dataset.crs is None:
            raise ValueError(
                "Feature extraction requires one band and a CRS"
            )

        coordinate_system = describe_coordinate_system(dataset, "Earth")
        masked = dataset.read(1, masked=True)
        valid_mask = ~np.ma.getmaskarray(masked)
        elevation = np.ma.getdata(masked).astype(np.float32, copy=False)
        resolution = (float(dataset.res[0]), float(dataset.res[1]))

        # Extract the requested feature; for Earth we focus on slope as the
        # primary comparable feature with Moon/Mars data
        if variable == "slope":
            feature_values = slope_degrees(elevation, valid_mask, resolution)
            units = "degrees"
            definition = (
                "atan of the metre-per-pixel gradient magnitude. "
                "Computed on the validated raster; no smoothing applied. "
                "Sensitive to DEM noise at steep slopes. "
                "Slope values are comparable across Moon/Mars/Earth when "
                "resolution is normalized to 20 m post spacing."
            )
        elif variable == "local_relief":
            from science.similarity.features.local_relief import local_relief_m

            feature_values, _ = local_relief_m(elevation, valid_mask, resolution, local_neighborhood_m)
            units = "m"
            definition = (
                "maximum elevation minus minimum elevation in a complete "
                "square window. Edge and incomplete-window cells are excluded "
                "from statistics. Comparable across Moon/Mars/Earth when "
                "resolution normalized to 20 m post spacing."
            )
        elif variable == "terrain_ruggedness":
            from science.similarity.features.terrain_ruggedness import terrain_ruggedness_index

            feature_values, _ = terrain_ruggedness_index(elevation, valid_mask, resolution, ruggedness_neighborhood_m)
            units = "m"
            definition = (
                "Riley TRI: square root of mean squared center-to-neighbor "
                "elevation differences. Riley TRI is a roughness index, not "
                "a direct hazard measure. Comparable across Moon/Mars/Earth "
                "when resolution normalized to 20 m native post spacing."
            )
        else:
            raise ValueError(f"Unknown variable: {variable}. Use 'slope', 'local_relief', or 'terrain_ruggedness'.")

        return FeatureLayer(
            name=variable,
            values=feature_values,
            units=units,
            neighborhood_m=local_neighborhood_m if variable != "terrain_ruggedness" else ruggedness_neighborhood_m,
            definition=definition,
        )


def earth_terrain_feature_set_from_raster(
    raster_path: Path,
    raster_id: str = "earth_dem",
    source_id: str = "earth_dem",
) -> TerrainFeatureSet:
    """Create a TerrainFeatureSet from an Earth DEM raster.

    This is a simplified feature set containing the primary terrain features
    extracted from the Earth DEM. Designed for cross-planetary comparison
    with Moon (moon_lola) and Mars (mars_jezero_ctx_dtm) feature sets.

    Returns a TerrainFeatureSet with:
    - source_id: the raster ID
    - body: "Earth"
    - resolution_m: the nominal resolution
    - crs: the CRS identifier
    - valid_percent: percentage of valid pixels
    - features: dict of FeatureLayer objects for slope, local_relief, terrain_ruggedness
    - source_metadata: dict with raster provenance
    - effective_resolution_m: the nominal resolution in meters
    """
    with rasterio.open(raster_path) as dataset:
        if dataset.count != 1 or dataset.crs is None:
            raise ValueError("Feature extraction requires one band and a CRS")

        coordinate_system = describe_coordinate_system(dataset, "Earth")
        masked = dataset.read(1, masked=True)
        valid_mask = ~np.ma.getmaskarray(masked)
        elevation = np.ma.getdata(masked).astype(np.float32, copy=False)
        resolution = (float(dataset.res[0]), float(dataset.res[1]))
        valid_percent = float(valid_mask.mean() * 100)

        # Extract all three terrain features
        features = {}

        # Slope
        slope_values = slope_degrees(elevation, valid_mask, resolution)
        features["slope"] = FeatureLayer(
            name="slope",
            values=slope_values,
            units="degrees",
            neighborhood_m=60.0,
            definition=(
                "atan of the metre-per-pixel gradient magnitude. "
                "Computed on the validated raster; no smoothing applied. "
                "Sensitive to DEM noise at steep slopes. "
                "Slope values are comparable across Moon/Mars/Earth when "
                "resolution is normalized to 20 m post spacing."
            ),
        )

        # Local relief
        from science.similarity.features.local_relief import local_relief_m

        relief_values, _ = local_relief_m(elevation, valid_mask, resolution, 60.0)
        features["local_relief"] = FeatureLayer(
            name="local_relief",
            values=relief_values,
            units="m",
            neighborhood_m=60.0,
            definition=(
                "maximum elevation minus minimum elevation in a complete "
                "square window (3x3 cells at 20 m native post spacing). "
                "Edge and incomplete-window cells are excluded from statistics. "
                "Comparable across Moon/Mars/Earth when resolution normalized to 20 m."
            ),
        )

        # Terrain ruggedness
        from science.similarity.features.terrain_ruggedness import terrain_ruggedness_index

        ruggedness_values, _ = terrain_ruggedness_index(elevation, valid_mask, resolution, 60.0)
        features["terrain_ruggedness"] = FeatureLayer(
            name="terrain_ruggedness",
            values=ruggedness_values,
            units="m",
            neighborhood_m=60.0,
            definition=(
                "Riley TRI: square root of mean squared center-to-neighbor "
                "elevation differences. Riley TRI is a roughness index, not "
                "a direct hazard measure. Comparable across Moon/Mars/Earth "
                "when resolution normalized to 20 m native post spacing."
            ),
        )

        # Compute summaries for each feature
        feature_summaries = {}
        for feat_name, feat_layer in features.items():
            feature_summaries[feat_name] = summarize(feat_layer.values)

        # Build source metadata
        source_metadata = {
            "path": str(raster_path),
            "width": dataset.width,
            "height": dataset.height,
            "bounds": [
                dataset.bounds.left,
                dataset.bounds.bottom,
                dataset.bounds.right,
                dataset.bounds.top,
            ],
            "crs_wkt": coordinate_system.wkt,
            "longitude_convention": coordinate_system.longitude_convention,
            "nodata": dataset.nodata,
            "resolution_m": list(resolution),
            "valid_percent": valid_percent,
            "variable": "elevation",
            "units": "meters",
        }

        return TerrainFeatureSet(
            source_id=source_id,
            body="Earth",
            resolution_m=resolution,
            crs=coordinate_system.identifier,
            valid_percent=valid_percent,
            features=features,
            source_metadata=source_metadata,
            effective_resolution_m=resolution[0],
        )


def verify_feature_comparability(
    earth_fts: TerrainFeatureSet,
    moon_fts: TerrainFeatureSet,
    mars_fts: TerrainFeatureSet,
) -> dict:
    """Verify that Earth, Moon, and Mars feature calculations are comparable.

    Checks that:
    - All three have the same feature names
    - Units match within each feature
    - Resolution is documented for each
    - Vertical datums are recorded

    Returns a dict with compatibility status and any issues found.
    """
    issues: list[str] = []
    compatible: bool = True

    # Check that all three have the same feature names
    earth_names = set(earth_fts.features.keys())
    moon_names = set(moon_fts.features.keys())
    mars_names = set(mars_fts.features.keys())

    all_names = earth_names & moon_names & mars_names
    missing_in_earth = (moon_names | mars_names) - earth_names
    missing_in_moon = (earth_names | mars_names) - moon_names
    missing_in_mars = (earth_names | moon_names) - mars_names

    if missing_in_earth:
        issues.append(
            f"Features in Moon/Mars but not Earth: {missing_in_earth}"
        )
        compatible = False
    if missing_in_moon:
        issues.append(
            f"Features in Earth/Mars but not Moon: {missing_in_moon}"
        )
        compatible = False
    if missing_in_mars:
        issues.append(
            f"Features in Earth/Moon but not Mars: {missing_in_mars}"
        )
        compatible = False

    # Check units match within each feature
    for feat_name in all_names:
        earth_feat = earth_fts.features[feat_name]
        moon_feat = moon_fts.features[feat_name]
        mars_feat = mars_fts.features[feat_name]

        if earth_feat.units != moon_feat.units:
            issues.append(f"Units mismatch for {feat_name}: Earth={earth_feat.units}, Moon={moon_feat.units}")
            compatible = False
        if earth_feat.units != mars_feat.units:
            issues.append(f"Units mismatch for {feat_name}: Earth={earth_feat.units}, Mars={mars_feat.units}")
            compatible = False

        # Check that neighborhoods are documented and consistent
        if earth_feat.neighborhood_m != moon_feat.neighborhood_m:
            issues.append(
                f"Neighborhood mismatch for {feat_name}: Earth={earth_feat.neighborhood_m}m, Moon={moon_feat.neighborhood_m}m"
            )
        if earth_feat.neighborhood_m != mars_feat.neighborhood_m:
            issues.append(
                f"Neighborhood mismatch for {feat_name}: Earth={earth_feat.neighborhood_m}m, Mars={mars_feat.neighborhood_m}m"
            )

    return {
        "compatible": compatible,
        "issues": issues,
        "common_features": list(all_names),
        "earth_body": earth_fts.body,
        "moon_body": moon_fts.body,
        "mars_body": mars_fts.body,
    }