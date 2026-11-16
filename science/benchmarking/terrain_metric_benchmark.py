"""Terrain metric benchmarking for Phase 13.

Responsibilities:
- Compute slope, local relief, and terrain ruggedness index (TRI) for
  DEM windows.
- Compare metric values between two datasets covering the same geographical
  region (not different regions passed off as equivalent).
- Report Pearson and Spearman correlations, but do not interpret high
  correlation as proof of interchangeability.
- Report mean absolute difference, median absolute difference, and RMS
  difference for each metric.
- Include Wasserstein distance and Kolmogorov-Smirnov diagnostics
  for elevation distribution comparison.
- Explain which metrics are appropriate for each comparison.

Do not interpret a high correlation as proof that two DEMs are interchangeable.
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def compute_slope( elevation_data: np.ndarray,
                   resolution_m: float,
                   ) -> np.ndarray:
    """Compute slope in degrees using central differences.

    Uses the standard 3x3 Sobel-like kernel for gradient estimation.
    Slope = arctan(|gradient|) in degrees.

    Parameters
    elevation_data: 2D array, NaN for missing data.
    resolution_m: ground sampling distance in metres.

    Returns
    slope_deg: 2D array of slope values in degrees (same shape).
    """
    # Pad to handle borders
    padded = np.pad(elevation_data, 1, mode='constant', constant_values=np.nan)

    # Compute gradients using central differences
    # Gx = partial derivative in x direction
    # Gy = partial derivative in y direction
    gx = (padded[1:-1, 2:] - padded[1:-1, 0:-2]) / (2 * resolution_m)
    gy = (padded[2:, 1:-1] - padded[0:-2, 1:-1]) / (2 * resolution_m)

    # Gradient magnitude
    magnitude = np.sqrt(gx**2 + gy**2)

    # Slope in degrees
    slope_deg = np.degrees(np.arctan(magnitude))

    return slope_deg


def compute_local_relief( elevation_data: np.ndarray,
                          resolution_m: float,
                          window_size: int = 3) -> np.ndarray:
    """Compute local relief within a sliding window.

    Local relief = max(elevation) - min(elevation) within each window.

    Parameters
    elevation_data: 2D array, NaN for missing data.
    resolution_m: ground sampling distance in metres.
    window_size: odd integer, window diameter in pixels.

    Returns
    relief: 2D array of local relief values in metres.
    """
    if window_size % 2 == 0:
        raise ValueError("window_size must be an odd integer")

    pad = window_size // 2
    # Use nan-aware min/max via finite mask
    padded = np.pad(elevation_data, pad, mode='constant', constant_values=np.nan)

    rows, cols = elevation_data.shape
    relief = np.full((rows, cols), np.nan, dtype=float)

    for i in range(rows):
        for j in range(cols):
            # Extract window
            win = padded[i:i + window_size, j:j + window_size]
            # Get finite values only
            finite = win[~np.isnan(win)]
            if len(finite) > 0:
                relief[i, j] = float(np.max(finite) - np.min(finite))
            else:
                relief[i, j] = np.nan

    return relief


def compute_terrain_ruggedness_index(
    elevation_data: np.ndarray,
    resolution_m: float,
) -> np.ndarray:
    """Compute Terrain Ruggedness Index (TRI).

    TRI = mean(|z_i - z_j|) over all pairs of adjacent cells.
    Adjacency: 4-neighbourhood (N, S, E, W).

    Parameters
    elevation_data: 2D array, NaN for missing data.
    resolution_m: ground sampling distance in metres (for context only).

    Returns
    tri: 2D array of TRI values (same shape as input).
    """
    padded = np.pad(elevation_data, 1, mode='constant', constant_values=np.nan)

    rows, cols = elevation_data.shape
    tri = np.full((rows, cols), np.nan, dtype=float)

    for i in range(1, rows + 1):
        for j in range(1, cols + 1):
            center = padded[i, j]
            if np.isnan(center):
                tri[i - 1, j - 1] = np.nan
                continue

                neighbours = [
                    padded[i - 1, j],   # N
                    padded[i + 1, j],   # S
                    padded[i, j - 1],   # W
                    padded[i, j + 1],   # E
                ]

                diffs = []
                for n in neighbours:
                    if not np.isnan(n):
                        diffs.append(abs(center - n))

                if len(diffs) > 0:
                    tri[i - 1, j - 1] = float(np.mean(diffs))
                else:
                    tri[i - 1, j - 1] = np.nan

    return tri


def benchmark_terrain_metrics(
    dem_a: dict,
    dem_b: dict,
    window_bounds: Optional[Tuple[int, int, int, int]] = None,
) -> dict:
    """Compute and compare terrain metrics between two DEM datasets.

    Parameters
    dem_a: dataset dict from the registry (must contain local_file or
      elevation data pathway).
    dem_b: dataset dict from the registry.
    window_bounds: (row_min, row_max, col_min, col_max) in pixel indices.
      If None, uses the full extent of the smaller dataset.

    Returns
    - dict with computed metrics for each dataset and comparative statistics.
    - All NaN-containing regions are excluded from correlation/RMS calculations.
    - Comparative statistics include: mean absolute difference, median
      absolute difference, RMS difference, Pearson r, Spearman rho,
      Wasserstein distance, and KS statistic.
    """
    # Placeholder: in a full implementation, would load the actual rasters,
    # align them, and compute metrics. Here we document the structure.

    a_id = dem_a.get("id", "unknown")
    b_id = dem_b.get("id", "unknown")

    warnings = dem_alignment.alignment_warnings(dem_a, dem_b)

    result: Dict[str, any] = {
        "dataset_a": a_id,
        "dataset_b": b_id,
        "window_bounds": window_bounds,
        "warnings": warnings,
        "metrics": {},
    }

    # Compute metrics for each dataset independently
    for label, dem in [("a", dem_a), ("b", dem_b)]:
        resolution = dem.get("nominal_resolution", 1.0)
        body = dem.get("body", "unknown")

        # If local_file exists, we would load it here
        # For now, record that metrics would be computed
        result["metrics"][label] = {
            "body": body,
            "resolution_m": resolution,
            "slope_deg_mean": None,
            "slope_deg_std": None,
            "local_relief_mean_m": None,
            "local_relief_std_m": None,
            "tri_mean": None,
            "tri_std": None,
            "elevation_distribution": {
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
            },
            "comparative_stats": {
                "mean_absolute_difference": None,
                "median_absolute_difference": None,
                "rms_difference": None,
                "pearson_r": None,
                "spearman_rho": None,
                "wasserstein_distance": None,
                "ks_statistic": None,
                "ks_pvalue": None,
            },
        }

    return result