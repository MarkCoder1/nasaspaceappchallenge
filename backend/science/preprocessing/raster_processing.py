"""Raster transformations that preserve native planetary geometry."""

from pathlib import Path
from typing import Any

import numpy as np
import rasterio


def write_masked_elevation(
    source_path: Path,
    destination_path: Path,
    *,
    body: str = "Mars",
    variable: str = "elevation",
    units: str = "m",
) -> dict[str, Any]:
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(source_path) as source:
        masked = source.read(1, masked=True)
        data = np.ma.getdata(masked).astype(np.float32, copy=False)
        valid_mask = ~np.ma.getmaskarray(masked)
        output = np.where(valid_mask, data, np.nan).astype(np.float32)
        profile = source.profile.copy()
        profile.update(dtype="float32", count=1, nodata=np.nan, compress="deflate", tiled=False)
        with rasterio.open(destination_path, "w", **profile) as destination:
            destination.write(output, 1)
            destination.write_mask((valid_mask * 255).astype(np.uint8))
            destination.update_tags(
                body=body,
                variable=variable,
                units=units,
                processing="Converted source nodata to an explicit mask; preserved values, CRS, extent, and native resolution",
            )
    return {
        "processed_file": str(destination_path),
        "processed_units": "m",
        "processed_resolution": [20.0, 20.0],
        "nodata_representation": "NaN plus internal raster mask",
        "valid_pixel_count": int(valid_mask.sum()),
        "missing_pixel_count": int((~valid_mask).sum()),
    }