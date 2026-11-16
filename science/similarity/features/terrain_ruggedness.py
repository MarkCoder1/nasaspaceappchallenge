"""Terrain Ruggedness Index (TRI) implementation."""

import numpy as np
from scipy import ndimage

from .local_relief import window_cells


def terrain_ruggedness_index(
    elevation: np.ndarray,
    valid_mask: np.ndarray,
    resolution_m: tuple[float, float],
    neighborhood_m: float = 60.0,
) -> tuple[np.ndarray, int]:
    """Compute Riley-style TRI: sqrt(mean((neighbor - center)^2)).

    A square odd window is selected from the requested physical size. The
    center-to-neighbor differences use all cells in that window, and a value
    is emitted only where the complete window is valid.
    """
    size = window_cells(neighborhood_m, resolution_m)
    center = elevation.astype(np.float64, copy=False)
    differences_squared = np.zeros_like(center, dtype=np.float64)
    samples = 0
    radius = size // 2
    for row_offset in range(-radius, radius + 1):
        for column_offset in range(-radius, radius + 1):
            if row_offset == 0 and column_offset == 0:
                continue
            shifted = np.roll(center, (row_offset, column_offset), axis=(0, 1))
            differences_squared += (shifted - center) ** 2
            samples += 1
    valid_count = ndimage.uniform_filter(valid_mask.astype(np.float32), size=size, mode="constant", cval=0) * (size**2)
    complete_window = (valid_count >= size**2) & valid_mask
    result = np.sqrt(differences_squared / samples).astype(np.float32)
    return np.where(complete_window, result, np.nan).astype(np.float32), size