"""Backend adapter for the scientific similarity engine."""

import json
import html
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from science.similarity.features.feature_extraction import extract_terrain_features
from science.similarity.scoring.similarity import compare_terrain


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DATASET_REGISTRY: dict[str, dict[str, Any]] = {
    "mars_jezero_ctx_dtm": {
        "id": "mars_jezero_ctx_dtm",
        "body": "Mars",
        "role": "target",
        "path": REPOSITORY_ROOT / "data/processed/mars_jezero_ctx_elevation_m.tif",
        "metadata": REPOSITORY_ROOT / "data/metadata/mars_jezero_ctx_dtm.json",
        "preprocessing_report": REPOSITORY_ROOT / "data/metadata/mars_jezero_ctx_preprocessing.json",
        "state": "VALIDATED",
    },
    "moon_lola": {
        "id": "moon_lola",
        "body": "Moon",
        "role": "candidate",
        "path": REPOSITORY_ROOT / "data/processed/moon_lola_80s_20m_elevation_m.tif",
        "metadata": REPOSITORY_ROOT / "data/metadata/moon_lola.json",
        "preprocessing_report": REPOSITORY_ROOT / "data/metadata/moon_lola_preprocessing.json",
        "effective_resolution_m": 16.055973052978516,
        "state": "VALIDATED",
    }
}

UNAVAILABLE_DATASETS = [
    {"id": "earth_nasadem_hgt_v001", "body": "Earth", "reason": "NASADEM has not been acquired and validated."},
]


class DatasetUnavailableError(ValueError):
    pass


def similarity_status() -> dict[str, Any]:
    available = []
    for dataset_id, dataset in DATASET_REGISTRY.items():
        available.append({"id": dataset_id, "body": dataset["body"], "state": dataset["state"], "path": str(dataset["path"]), "validated": dataset["state"] == "VALIDATED" and dataset["path"].is_file()})
    return {
        "engine": "Terrain Morphology Similarity Index (TMSI)",
        "production_comparisons_enabled": False,
        "validated_comparisons": ["moon_mars"],
        "available_real_datasets": available,
        "unavailable_datasets": UNAVAILABLE_DATASETS,
        "comparison_capabilities": {
            "earth_mars": {"enabled": False, "reason": "No validated Earth elevation raster is available."},
            "earth_moon": {"enabled": False, "reason": "No validated Earth or lunar elevation raster is available."},
            "moon_mars": {"enabled": True, "reason": "Validated Moon and Mars terrain inputs are available; morphology-only comparison."},
        },
    }


def feature_definitions() -> list[dict[str, Any]]:
    return [
        {"id": "slope", "units": "degrees", "definition": "Gradient magnitude converted to degrees using projected metre-per-pixel spacing."},
        {"id": "local_relief", "units": "m", "definition": "Maximum minus minimum elevation in a complete 60 m physical window."},
        {"id": "terrain_ruggedness", "units": "m", "definition": "Riley TRI: square root of mean squared center-to-neighbor elevation differences in a 60 m window."},
    ]


def methodology() -> dict[str, Any]:
    return {
        "name": "Terrain Morphology Similarity Index (TMSI)",
        "research_question": "How closely can selected Earth terrain environments approximate measurable surface morphology of selected lunar or Martian exploration regions at consistent physical scales?",
        "distance": "Wasserstein distribution distance normalized by the larger pooled interquartile range; KS statistic is retained as a diagnostic.",
        "score": "100 * exp(-weighted_normalized_distance)",
        "weights": "Equal weights across available valid features by default; weights are configurable and sensitivity-tested.",
        "confidence": "Coverage and native resolution compatibility classification; not a calibrated probability.",
        "uncertainty": "Non-overlapping spatial block bootstrap with 160 m, 320 m, and 640 m sensitivity checks; intervals are not calibrated probabilities.",
        "status": "No production cross-body result is enabled until Earth and/or lunar inputs pass validation.",
    }


def stored_experiment() -> dict[str, Any]:
    artifact = REPOSITORY_ROOT / "data/metadata/moon_mars_phase7_experiments.json"
    return json.loads(artifact.read_text(encoding="utf-8"))


def terrain_grid(dataset_id: str, layer: str = "elevation", resampling: str = "average", max_dim: int = 128) -> dict[str, Any]:
    if dataset_id not in DATASET_REGISTRY:
        raise DatasetUnavailableError(f"Dataset is unavailable: {dataset_id}")
    allowed_layers = {"elevation", "hillshade", "slope", "local_relief", "terrain_ruggedness"}
    if layer not in allowed_layers:
        raise DatasetUnavailableError(f"Unknown layer: {layer}")
    path = DATASET_REGISTRY[dataset_id]["path"]
    if not path.is_file():
        raise DatasetUnavailableError(f"Dataset file is unavailable: {dataset_id}")
    with rasterio.open(path) as dataset:
        src_h = dataset.height
        src_w = dataset.width
        scale = max(src_h / max_dim, src_w / max_dim, 1)
        out_h = max(2, int(round(src_h / scale)))
        out_w = max(2, int(round(src_w / scale)))
        rs = rasterio.enums.Resampling.average if resampling == "average" else rasterio.enums.Resampling.nearest
        values = dataset.read(1, out_shape=(1, out_h, out_w), masked=True, resampling=rs)
        elevation = values.filled(np.nan).astype(float)
        valid = np.isfinite(elevation)
        layer_values = _compute_layer(elevation, valid, layer) if layer != "elevation" else elevation
        finite = valid & np.isfinite(layer_values)
        lo = float(np.nanpercentile(layer_values, 2)) if finite.any() else 0.0
        hi = float(np.nanpercentile(layer_values, 98)) if finite.any() else 1.0
        return {
            "dataset_id": dataset_id,
            "body": DATASET_REGISTRY[dataset_id]["body"],
            "layer": layer,
            "resampling": resampling,
            "source_dimensions": [src_h, src_w],
            "downsampled_dimensions": [out_h, out_w],
            "resolution_m": float(dataset.res[0]),
            "bounds": [float(dataset.bounds.left), float(dataset.bounds.bottom), float(dataset.bounds.right), float(dataset.bounds.top)],
            "crs": str(dataset.crs) if dataset.crs else None,
            "valid_percent": float(valid.mean() * 100),
            "clip_low": float(lo),
            "clip_high": float(hi),
            "elevation_stats": {
                "min": float(np.nanmin(elevation[np.isfinite(elevation)])) if np.isfinite(elevation).any() else None,
                "max": float(np.nanmax(elevation[np.isfinite(elevation)])) if np.isfinite(elevation).any() else None,
                "mean": float(np.nanmean(elevation[np.isfinite(elevation)])) if np.isfinite(elevation).any() else None,
            },
            "sample_grid": [[float(v) if np.isfinite(v) else None for v in row] for row in layer_values],
            "grid_shape": [out_h, out_w],
            "kind": "terrain_grid",
        }


def raster_preview_svg(dataset_id: str, width: int = 360, height: int = 240, layer: str = "elevation") -> str:
    if dataset_id not in DATASET_REGISTRY:
        raise DatasetUnavailableError(f"Dataset is unavailable: {dataset_id}")
    path = DATASET_REGISTRY[dataset_id]["path"]
    if not path.is_file():
        raise DatasetUnavailableError(f"Dataset file is unavailable: {dataset_id}")
    allowed_layers = {"elevation", "hillshade", "slope", "local_relief", "terrain_ruggedness"}
    if layer not in allowed_layers:
        raise DatasetUnavailableError(f"Unknown raster layer: {layer}")
    with rasterio.open(path) as dataset:
        values = dataset.read(1, out_shape=(1, height, width), masked=True, resampling=rasterio.enums.Resampling.average)
        elevation = values.filled(np.nan).astype(float)
        valid = np.isfinite(elevation)
        layer_values = _compute_layer(elevation, valid, layer)
        finite = valid & np.isfinite(layer_values)
        if finite.any():
            minimum = float(np.nanpercentile(layer_values, 2))
            maximum = float(np.nanpercentile(layer_values, 98))
        else:
            minimum = 0.0
            maximum = 1.0
        scale = max(maximum - minimum, 1e-9)
        rects: list[str] = []
        for row in range(height):
            for column in range(width):
                if not finite[row, column]:
                    color = "#171b18"
                else:
                    value = max(0.0, min(1.0, (layer_values[row, column] - minimum) / scale))
                    color = _layer_color(layer, value)
                rects.append(f'<rect x="{column}" y="{row}" width="1.02" height="1.02" fill="{color}"/>')
        safe_id = html.escape(dataset_id)
        if layer == "elevation":
            aria_label = f"Terrain elevation preview for {safe_id}"
        else:
            aria_label = f"{layer} terrain preview for {safe_id}"
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{aria_label}">'
            f'<rect width="{width}" height="{height}" fill="#0c0f0d"/>{"".join(rects)}'
            f'<path d="M0 {height/2}H{width} M{width/2} 0V{height}" stroke="#d7dfca" stroke-opacity=".16" stroke-width=".5"/>'
            f'</svg>'
        )


def _compute_layer(elevation: np.ndarray, valid: np.ndarray, layer: str) -> np.ndarray:
    out = np.full(elevation.shape, np.nan, dtype=float)
    if layer == "elevation":
        out = elevation.copy()
    elif layer == "hillshade":
        out = _hillshade(elevation, valid)
    elif layer == "slope":
        out = _slope_degrees(elevation, valid)
    elif layer == "local_relief":
        out = _local_relief(elevation, valid, window_cells=3)
    elif layer == "terrain_ruggedness":
        out = _terrain_ruggedness(elevation, valid, window_cells=3)
    return out


def _hillshade(elevation: np.ndarray, valid: np.ndarray) -> np.ndarray:
    # Simple shaded relief from central differences (azimuth 315°, altitude 45°).
    gy, gx = np.gradient(np.where(valid, elevation, 0.0))
    shaded = 0.5 * (-gx) + 0.5 * (-gy)
    shaded = np.where(valid, shaded, np.nan)
    return shaded


def _slope_degrees(elevation: np.ndarray, valid: np.ndarray) -> np.ndarray:
    gy, gx = np.gradient(np.where(valid, elevation, 0.0))
    slope = np.degrees(np.arctan(np.sqrt(gx * gx + gy * gy)))
    slope = np.where(valid, slope, np.nan)
    return slope


def _window_extrema(elevation: np.ndarray, valid: np.ndarray, window_cells: int, op: str) -> np.ndarray:
    padded = np.full(
        (elevation.shape[0] + 2 * window_cells, elevation.shape[1] + 2 * window_cells), np.nan, dtype=float
    )
    padded[window_cells:-window_cells, window_cells:-window_cells] = elevation
    out = np.full(elevation.shape, np.nan, dtype=float)
    radius = window_cells // 2
    for row in range(elevation.shape[0]):
        for column in range(elevation.shape[1]):
            if not valid[row, column]:
                continue
            block = padded[row:row + window_cells, column:column + window_cells]
            block = block[np.isfinite(block)]
            if block.size == 0:
                continue
            if op == "max":
                out[row, column] = float(np.max(block))
            elif op == "min":
                out[row, column] = float(np.min(block))
    return out


def _local_relief(elevation: np.ndarray, valid: np.ndarray, window_cells: int) -> np.ndarray:
    maximum = _window_extrema(elevation, valid, window_cells, "max")
    minimum = _window_extrema(elevation, valid, window_cells, "min")
    relief = maximum - minimum
    relief = np.where(valid & np.isfinite(maximum) & np.isfinite(minimum), relief, np.nan)
    return relief


def _terrain_ruggedness(elevation: np.ndarray, valid: np.ndarray, window_cells: int) -> np.ndarray:
    # Riley TRI: sqrt(mean squared center-to-neighbor differences).
    out = np.full(elevation.shape, np.nan, dtype=float)
    radius = window_cells // 2
    for row in range(elevation.shape[0]):
        for column in range(elevation.shape[1]):
            if not valid[row, column]:
                continue
            center = elevation[row, column]
            block = elevation[
                max(0, row - radius):row + radius + 1,
                max(0, column - radius):column + radius + 1,
            ]
            valid_block = block[np.isfinite(block)]
            if valid_block.size < 2:
                continue
            diffs = valid_block - center
            out[row, column] = float(np.sqrt(np.mean(diffs * diffs)))
    return out


def _layer_color(layer: str, value: float) -> str:
    value = max(0.0, min(1.0, value))
    if layer == "elevation":
        # Deep green -> moss -> pale green/amber.
        red = int(20 + value * 120)
        green = int(40 + value * 150)
        blue = int(30 + value * 60)
    elif layer == "hillshade":
        gray = int(30 + value * 200)
        red = green = blue = gray
    elif layer == "slope":
        # Dark amber -> bright amber.
        red = int(150 + value * 105)
        green = int(90 + value * 130)
        blue = int(30 + value * 40)
    elif layer == "local_relief":
        red = int(180 + value * 75)
        green = int(110 + value * 110)
        blue = int(40 + value * 50)
    else:  # terrain_ruggedness
        red = int(200 + value * 55)
        green = int(100 + value * 80)
        blue = int(40 + value * 30)
    return f"rgb({red},{green},{blue})"


def compare_dataset_ids(target_id: str, candidate_id: str, weights: dict[str, float] | None = None) -> dict[str, Any]:
    if target_id not in DATASET_REGISTRY:
        raise DatasetUnavailableError(f"Target dataset is unavailable: {target_id}")
    if candidate_id not in DATASET_REGISTRY:
        raise DatasetUnavailableError(f"Candidate dataset is unavailable: {candidate_id}")
    if target_id == candidate_id:
        raise DatasetUnavailableError("Self-comparison is not a production analog comparison")
    target = DATASET_REGISTRY[target_id]
    candidate = DATASET_REGISTRY[candidate_id]
    target_features = extract_terrain_features(target["path"], body=target["body"], source_id=target_id, effective_resolution_m=target.get("effective_resolution_m"))
    candidate_features = extract_terrain_features(candidate["path"], body=candidate["body"], source_id=candidate_id, effective_resolution_m=candidate.get("effective_resolution_m"))
    result = compare_terrain(target_features, candidate_features, weights, include_uncertainty=True)
    result["data_sources"] = [json.loads(target["metadata"].read_text()), json.loads(candidate["metadata"].read_text())]
    return result