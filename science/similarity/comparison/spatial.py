"""Spatial-structure diagnostics kept separate from TMSI."""

from typing import Any

import numpy as np


def morans_i(values: np.ndarray) -> float:
    """Compute Moran's I using rook adjacency on finite raster cells."""
    if values.ndim != 2:
        raise ValueError("Moran's I requires a two-dimensional raster")
    valid = np.isfinite(values)
    if valid.sum() < 3:
        raise ValueError("Moran's I requires at least three valid cells")
    mean = float(values[valid].mean())
    centered = np.where(valid, values - mean, 0.0)
    numerator = 0.0
    weight_sum = 0
    for row_offset, column_offset in ((1, 0), (0, 1)):
        left = valid[:-row_offset or None, :-column_offset or None]
        right = valid[row_offset:, column_offset:]
        numerator += float((centered[:-row_offset or None, :-column_offset or None] * centered[row_offset:, column_offset:])[left & right].sum() * 2)
        weight_sum += int((left & right).sum() * 2)
    denominator = float((centered[valid] ** 2).sum())
    if denominator == 0 or weight_sum == 0:
        return 0.0
    return float((valid.size / weight_sum) * numerator / denominator)


def semivariogram(values: np.ndarray, resolution_m: tuple[float, float], lags_cells: tuple[int, ...] = (1, 2, 4, 8, 16, 32)) -> list[dict[str, float | int | None]]:
    """Estimate directional-averaged semivariance at raster lags."""
    if values.ndim != 2:
        raise ValueError("Semivariogram requires a two-dimensional raster")
    results: list[dict[str, float | int | None]] = []
    for lag in lags_cells:
        pairs: list[np.ndarray] = []
        for row_offset, column_offset in ((lag, 0), (0, lag)):
            first = values[:-row_offset or None, :-column_offset or None]
            second = values[row_offset:, column_offset:]
            valid = np.isfinite(first) & np.isfinite(second)
            if valid.any():
                pairs.append(0.5 * (first[valid] - second[valid]) ** 2)
        combined = np.concatenate(pairs) if pairs else np.array([], dtype=np.float64)
        results.append({
            "lag_cells": lag,
            "lag_m": float(lag * max(resolution_m)),
            "pair_count": int(combined.size),
            "semivariance": float(combined.mean()) if combined.size else None,
        })
    return results


def spatial_feature_diagnostics(feature_values: dict[str, np.ndarray], resolution_m: tuple[float, float]) -> dict[str, Any]:
    return {
        name: {"morans_i": morans_i(values), "semivariogram": semivariogram(values, resolution_m)}
        for name, values in feature_values.items()
    }