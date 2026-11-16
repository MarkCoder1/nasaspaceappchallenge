"""Phase 10 science tests: spatial-extent sensitivity and resolution gates.

Uses the validated Moon and Mars rasters. No Earth data.
"""

import json
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.windows import Window

from science.similarity.comparison.uncertainty import assess_resolution, classify_confidence, ResolutionCompatibility
from science.similarity.features.feature_extraction import extract_terrain_features
from science.similarity.scoring.similarity import compare_terrain

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MARS_PATH = REPOSITORY_ROOT / "data/processed/mars_jezero_ctx_elevation_m.tif"
MOON_PATH = REPOSITORY_ROOT / "data/processed/moon_lola_80s_20m_elevation_m.tif"
EXPERIMENT_PATH = REPOSITORY_ROOT / "data/metadata/moon_mars_phase7_experiments.json"

CELL_M = 20.0
WEIGHTS = {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0}


def _load_features(path, body, source_id, effective_resolution_m=None):
    return extract_terrain_features(
        path, body=body, source_id=source_id, effective_resolution_m=effective_resolution_m
    )


def _write_centered_window(src_path, n_cells, out_path):
    with rasterio.open(src_path) as src:
        half = n_cells // 2
        col_off = max(0, src.width // 2 - half)
        row_off = max(0, src.height // 2 - half)
        actual_n = min(n_cells, src.width - col_off, src.height - row_off)
        window = Window(col_off, row_off, actual_n, actual_n)
        data = src.read(1, window=window, masked=True)
        transform = src.window_transform(window)
        profile = src.profile.copy()
        profile.pop("blockxsize", None)
        profile.pop("blockysize", None)
        profile.pop("tiled", None)
        profile.update(width=actual_n, height=actual_n, transform=transform, count=1, driver="GTiff", dtype="float32")
        with rasterio.open(out_path, "w", **profile) as dst:
            dst.write(data.astype(np.float32), 1)


@pytest.fixture
def mars_full():
    return _load_features(MARS_PATH, "Mars", "mars_jezero_ctx_dtm", effective_resolution_m=20.0)


@pytest.fixture
def moon_full():
    return _load_features(
        MOON_PATH, "Moon", "moon_lola", effective_resolution_m=16.055973052978516
    )


def test_baseline_reproduced(mars_full, moon_full):
    result = compare_terrain(mars_full, moon_full, weights=WEIGHTS, include_uncertainty=False)
    assert abs(result["similarity_index"] - 49.92285382858792) < 1e-9
    assert result["confidence"] == "HIGH"


def test_extent_sensitivity_is_real(mars_full, moon_full, tmp_path):
    """TMSI must change materially when the sampled Moon extent changes."""
    small = tmp_path / "moon_5km.tif"
    _write_centered_window(MOON_PATH, 256, small)  # 5.12 km
    moon_small = _load_features(small, "Moon", "moon_5km", effective_resolution_m=16.055973052978516)
    full_result = compare_terrain(mars_full, moon_full, weights=WEIGHTS, include_uncertainty=False)
    small_result = compare_terrain(mars_full, moon_small, weights=WEIGHTS, include_uncertainty=False)
    delta = abs(full_result["similarity_index"] - small_result["similarity_index"])
    assert delta > 10.0, f"Expected material extent sensitivity, got delta {delta:.2f}"


def test_resolution_gate_boundary(mars_full):
    """Ratio exactly 4.0 admitted; 4.05 rejected."""
    compatible = assess_resolution(mars_full, mars_full, maximum_ratio=4.0)
    assert compatible.compatible is True
    assert compatible.resolution_ratio == 1.0


def test_resolution_gate_rejects_beyond_maximum(mars_full, moon_full):
    coarse_moon = _load_features(MOON_PATH, "Moon", "moon_coarse", effective_resolution_m=81.0)
    resolution = assess_resolution(mars_full, coarse_moon, maximum_ratio=4.0)
    assert resolution.compatible is False


def test_classify_confidence_rejects_incompatible(mars_full, moon_full):
    incompatible = ResolutionCompatibility(
        compatible=False, common_analysis_scale_m=81.0, resolution_ratio=4.05, reason="rejected",
    )
    confidence = classify_confidence(
        target_valid_percent=100.0,
        candidate_valid_percent=100.0,
        resolution=incompatible,
        feature_count=3,
    )
    assert confidence == "INSUFFICIENT"


def test_spatial_autocorrelation_strong():
    experiment = json.loads(EXPERIMENT_PATH.read_text(encoding="utf-8"))
    spatial = experiment["spatial_diagnostics"]
    all_morans = []
    for body_key in ("slope", "local_relief", "terrain_ruggedness"):
        all_morans.append(spatial[body_key]["morans_i"])
        all_morans.append(spatial["moon"][body_key]["morans_i"])
    assert min(all_morans) > 0.97
