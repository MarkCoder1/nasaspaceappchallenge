"""Local elevation relief using a physical-size neighborhood."""

import numpy as np
from scipy import ndimage


def window_cells(neighborhood_m: float, resolution_m: tuple[float, float]) -> int:
    if neighborhood_m <= 0:
        raise ValueError("Neighborhood size must be positive")
    cell_size = max(resolution_m)
    cells = max(3, int(round(neighborhood_m / cell_size)))
    return cells if cells % 2 else cells + 1


def local_relief_m(
    elevation: np.ndarray,
    valid_mask: np.ndarray,
    resolution_m: tuple[float, float],
    neighborhood_m: float = 60.0,
) -> tuple[np.ndarray, int]:
    """Return max-minus-min relief and the odd window width in cells."""
    size = window_cells(neighborhood_m, resolution_m)
    minimum_input = np.where(valid_mask, elevation, np.inf)
    maximum_input = np.where(valid_mask, elevation, -np.inf)
    local_min = ndimage.minimum_filter(minimum_input, size=size, mode="nearest")
    local_max = ndimage.maximum_filter(maximum_input, size=size, mode="nearest")
    valid_count = ndimage.uniform_filter(valid_mask.astype(np.float32), size=size, mode="constant", cval=0) * (size**2)
    complete_window = valid_count >= size**2
    relief = (local_max - local_min).astype(np.float32)
    return np.where(complete_window, relief, np.nan).astype(np.float32), size