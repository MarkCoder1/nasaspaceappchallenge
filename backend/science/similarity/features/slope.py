"""Scale-aware slope extraction from projected planetary elevation rasters."""

import numpy as np
from scipy import ndimage


def slope_degrees(
    elevation: np.ndarray,
    valid_mask: np.ndarray,
    resolution_m: tuple[float, float],
) -> np.ndarray:
    """Return slope in degrees using projected metre-per-pixel spacing.

    The gradient is taken in raster row/column axes after the caller has
    validated that the CRS is a body-appropriate projected CRS in metres.
    A 3x3 valid neighborhood is required around each reported pixel.
    """
    if elevation.shape != valid_mask.shape:
        raise ValueError("Elevation and valid mask must have identical shapes")
    if resolution_m[0] <= 0 or resolution_m[1] <= 0:
        raise ValueError("Raster resolution must be positive")
    filled = np.where(valid_mask, elevation, 0.0).astype(np.float64, copy=False)
    gradient_y, gradient_x = np.gradient(filled, resolution_m[1], resolution_m[0])
    slope = np.degrees(np.arctan(np.hypot(gradient_x, gradient_y))).astype(np.float32)
    neighborhood_valid = ndimage.binary_erosion(valid_mask, structure=np.ones((3, 3), dtype=bool), border_value=0)
    return np.where(neighborhood_valid & valid_mask, slope, np.nan).astype(np.float32)