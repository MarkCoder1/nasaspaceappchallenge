"""Quality-control summaries for raw and processed rasters."""

from pathlib import Path
from typing import Any

import numpy as np
import rasterio


def quality_summary(path: Path) -> dict[str, Any]:
    with rasterio.open(path) as dataset:
        values = dataset.read(1, masked=True)
        valid_mask = ~np.ma.getmaskarray(values)
        raw = np.ma.getdata(values)
        valid = raw[valid_mask]
        finite_mask = np.isfinite(valid)
        finite = valid[finite_mask]
        unique_value_count = int(np.unique(finite).size) if finite.size else 0
        return {
            "file": str(path),
            "shape": [dataset.height, dataset.width],
            "dtype": dataset.dtypes[0],
            "nodata": dataset.nodata,
            "valid_pixel_count": int(finite.size),
            "missing_pixel_count": int(values.size - finite.size),
            "valid_percent": float(finite.size / values.size * 100),
            "missing_percent": float((values.size - finite.size) / values.size * 100),
            "nonfinite_count": int(valid.size - finite.size),
            "minimum": float(finite.min()) if finite.size else None,
            "maximum": float(finite.max()) if finite.size else None,
            "mean": float(finite.mean()) if finite.size else None,
            "unique_value_count": unique_value_count,
            "duplicate_value_percent": float((finite.size - unique_value_count) / finite.size * 100) if finite.size else 0.0,
            "checksum": dataset.checksum(1),
        }