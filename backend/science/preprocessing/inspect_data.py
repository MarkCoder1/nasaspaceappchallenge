"""Extract reproducible raster metadata and scientific summary statistics."""

import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

from .coordinate_systems import describe_coordinate_system


def inspect_raster(path: Path, body: str) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Missing or empty raster: {path}")
    with rasterio.open(path) as dataset:
        masked = dataset.read(1, masked=True)
        valid = np.ma.getdata(masked)[~np.ma.getmaskarray(masked)]
        finite = valid[np.isfinite(valid)]
        coordinate_system = describe_coordinate_system(dataset, body)
        return {
            "file": str(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "driver": dataset.driver,
            "width": dataset.width,
            "height": dataset.height,
            "bands": dataset.count,
            "dtype": dataset.dtypes[0],
            "nodata": dataset.nodata,
            "bounds": [dataset.bounds.left, dataset.bounds.bottom, dataset.bounds.right, dataset.bounds.top],
            "resolution": [dataset.res[0], dataset.res[1]],
            "valid_pixel_count": int(finite.size),
            "total_pixel_count": int(masked.size),
            "valid_percent": float(finite.size / masked.size * 100),
            "missing_percent": float((masked.size - finite.size) / masked.size * 100),
            "finite_min": float(finite.min()) if finite.size else None,
            "finite_max": float(finite.max()) if finite.size else None,
            "finite_mean": float(finite.mean()) if finite.size else None,
            "nonfinite_valid_count": int(valid.size - finite.size),
            "coordinate_system": {
                "body": coordinate_system.body,
                "identifier": coordinate_system.identifier,
                "wkt": coordinate_system.wkt,
                "longitude_convention": coordinate_system.longitude_convention,
                "notes": coordinate_system.notes,
            },
            "tags": dataset.tags(),
            "band_tags": dataset.tags(1),
            "raster_checksum": dataset.checksum(1),
        }