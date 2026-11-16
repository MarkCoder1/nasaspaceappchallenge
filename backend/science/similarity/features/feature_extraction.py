"""Extract comparable terrain morphology features from validated rasters."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

from science.preprocessing.coordinate_systems import describe_coordinate_system

from .local_relief import local_relief_m
from .slope import slope_degrees
from .terrain_ruggedness import terrain_ruggedness_index


@dataclass(frozen=True)
class FeatureLayer:
    name: str
    values: np.ndarray
    units: str
    neighborhood_m: float | None
    definition: str

    def valid_values(self) -> np.ndarray:
        return self.values[np.isfinite(self.values)]


@dataclass(frozen=True)
class TerrainFeatureSet:
    source_id: str
    body: str
    resolution_m: tuple[float, float]
    crs: str
    valid_percent: float
    features: dict[str, FeatureLayer]
    source_metadata: dict[str, Any]
    effective_resolution_m: float | None = None


def summarize(values: np.ndarray) -> dict[str, float | int | None]:
    valid = values[np.isfinite(values)]
    if valid.size == 0:
        return {"count": 0, "mean": None, "median": None, "std": None, "q25": None, "q75": None, "q90": None}
    return {
        "count": int(valid.size),
        "mean": float(valid.mean()),
        "median": float(np.median(valid)),
        "std": float(valid.std()),
        "q25": float(np.percentile(valid, 25)),
        "q75": float(np.percentile(valid, 75)),
        "q90": float(np.percentile(valid, 90)),
    }


def extract_terrain_features(
    path: Path,
    *,
    body: str,
    source_id: str,
    local_neighborhood_m: float = 60.0,
    ruggedness_neighborhood_m: float = 60.0,
    effective_resolution_m: float | None = None,
) -> TerrainFeatureSet:
    with rasterio.open(path) as dataset:
        if dataset.count != 1 or dataset.crs is None:
            raise ValueError("Feature extraction requires one band and a CRS")
        coordinate_system = describe_coordinate_system(dataset, body)
        masked = dataset.read(1, masked=True)
        valid_mask = ~np.ma.getmaskarray(masked)
        elevation = np.ma.getdata(masked).astype(np.float32, copy=False)
        resolution = (float(dataset.res[0]), float(dataset.res[1]))
        slope = slope_degrees(elevation, valid_mask, resolution)
        relief, relief_window = local_relief_m(elevation, valid_mask, resolution, local_neighborhood_m)
        ruggedness, ruggedness_window = terrain_ruggedness_index(elevation, valid_mask, resolution, ruggedness_neighborhood_m)
        features = {
            "slope": FeatureLayer("slope", slope, "degrees", None, "atan of the metre-per-pixel gradient magnitude"),
            "local_relief": FeatureLayer("local_relief", relief, "m", local_neighborhood_m, "maximum elevation minus minimum elevation in a complete square window"),
            "terrain_ruggedness": FeatureLayer("terrain_ruggedness", ruggedness, "m", ruggedness_neighborhood_m, "Riley TRI: sqrt(mean squared center-to-neighbor elevation differences))"),
        }
        metadata = {
            "path": str(path),
            "width": dataset.width,
            "height": dataset.height,
            "bounds": [dataset.bounds.left, dataset.bounds.bottom, dataset.bounds.right, dataset.bounds.top],
            "crs_wkt": coordinate_system.wkt,
            "longitude_convention": coordinate_system.longitude_convention,
            "nodata": dataset.nodata,
            "resolution_m": list(resolution),
            "effective_resolution_m": effective_resolution_m,
            "source_valid_percent": float(valid_mask.mean() * 100),
            "feature_windows_cells": {"local_relief": relief_window, "terrain_ruggedness": ruggedness_window},
            "feature_summaries": {name: summarize(layer.values) for name, layer in features.items()},
        }
    return TerrainFeatureSet(source_id, body, resolution, coordinate_system.identifier, float(valid_mask.mean() * 100), features, metadata, effective_resolution_m)