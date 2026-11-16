"""Resolution sensitivity analysis for Phase 13 benchmarking.

Responsibilities:
- Evaluate how terrain measurements change when datasets are
  resampled to compatible resolutions.
- Preserve original-resolution data; record every resampling operation.
- Document interpolation methods used.
- Avoid implying that resampling restores lost information.
- Compare results at multiple defensible resolutions when coverage permits.

Key design decisions are documented per Phase 13 Section B3.
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def resample_dem_elevation(
    elevation_data: np.ndarray,
    original_resolution_m: float,
    target_resolution_m: float,
    interpolation: str = "bilinear",
) -> dict:
    """Describe a resampling operation; does not actually resample.

    Returns a dict documenting the operation. Actual resampling should
    use rasterio, scipy, or xarray with the documented parameters.

    Parameters
    elevation_data: 2D numpy array of elevation values.
    original_resolution_m: native ground sampling distance in metres.
    target_resolution_m: desired ground sampling distance in metres.
    interpolation: one of "nearest", "bilinear", "cubic".

    Returns
    - original_shape: tuple (rows, cols)
    - original_resolution_m: input resolution
    - target_resolution_m: output resolution
    - scale_factor: target / original
    - interpolation_method: chosen method
    - notes: scientific cautions about resampling.
    """
    rows, cols = elevation_data.shape
    scale_factor = target_resolution_m / original_resolution_m

    return {
        "original_shape": (rows, cols),
        "original_resolution_m": original_resolution_m,
        "target_resolution_m": target_resolution_m,
        "scale_factor": scale_factor,
        "interpolation_method": interpolation,
        "notes": (
            f"Resampling from {original_resolution_m} m to "
            f"{target_resolution_m} m introduces interpolation artifacts. "
            f"The {interpolation} method assumes gradual terrain variation. "
            f"Do not use resampling to recover features lost at the native "
            f"resolution. Record the scale factor in the benchmark config."
        ),
    }


def resolution_sensitivity_report(
    elevations_a: dict,
    elevations_b: dict,
    resolutions: Tuple[float, float, float] = (None, None, None),
) -> dict:
    """Report terrain metric differences at multiple resolutions.

    Parameters
    elevations_a: dict with keys "data" (numpy array), "resolution_m"
    elevations_b: dict with keys "data" (numpy array), "resolution_m"
    resolutions: tuple of (native, target1, target2) in metres; None means
      use each dataset's native resolution.

    Returns
    - dict with resolution-keyed metrics and scientific notes.
    """
    native_a = elevations_a.get("resolution_m", 1.0)
    native_b = elevations_b.get("resolution_m", 1.0)

    if resolutions[0] is None:
        resolutions = (native_a, native_b, max(native_a, native_b) * 2)

    report: Dict[str, any] = {}
    for label, res in zip(["native_a", "native_b", "comparison"], resolutions):
        if res is None:
            continue
        report[label] = {
            "resolution_m": res,
            "note": (
                f"Comparison at {res} m resolution. "
                "If this is a resampled value, the interpolation method "
                "and scale factor must be recorded."
            ),
        }

    return report