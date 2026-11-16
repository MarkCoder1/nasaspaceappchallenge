"""Validation rules for selected preprocessing inputs."""

from pathlib import Path
from typing import Any

import numpy as np
import rasterio


def validate_raster(
    path: Path,
    *,
    expected_body: str,
    expected_resolution: tuple[float, float],
    expected_units: str,
) -> dict[str, Any]:
    with rasterio.open(path) as dataset:
        if dataset.count != 1:
            raise ValueError(f"Expected one elevation band, found {dataset.count}")
        if dataset.crs is None:
            raise ValueError("Selected raster has no CRS")
        wkt = dataset.crs.to_wkt()
        if expected_body.lower() not in wkt.lower():
            raise ValueError(f"CRS does not identify expected body: {expected_body}")
        if not np.allclose(dataset.res, expected_resolution, rtol=0, atol=1e-6):
            raise ValueError(f"Unexpected resolution {dataset.res}; expected {expected_resolution}")
        if expected_units != "meters":
            raise ValueError(f"Unsupported elevation unit declaration: {expected_units}")
        values = dataset.read(1, masked=True)
        valid = np.ma.getdata(values)[~np.ma.getmaskarray(values)]
        if valid.size == 0:
            raise ValueError("Raster contains no valid pixels")
        if not np.isfinite(valid).all():
            raise ValueError("Raster contains non-finite values in the valid mask")
        return {
            "body": expected_body,
            "units": expected_units,
            "shape": [dataset.height, dataset.width],
            "resolution": list(dataset.res),
            "valid_pixel_count": int(valid.size),
            "minimum": float(valid.min()),
            "maximum": float(valid.max()),
        }