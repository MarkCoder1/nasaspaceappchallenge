"""Phase 9 independent validation tests using validated Moon and Mars rasters."""

import json
from pathlib import Path

import numpy as np
import pytest
import rasterio

from science.similarity.comparison.uncertainty import assess_resolution, classify_confidence
from science.similarity.features.feature_extraction import extract_terrain_features
from science.similarity.scoring.similarity import compare_terrain

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MARS_PATH = REPOSITORY_ROOT / "data/processed/mars_jezero_ctx_elevation_m.tif"
MOON_PATH = REPOSITORY_ROOT / "data/processed/moon_lola_80s_20m_elevation_m.tif"
EXPERIMENT_PATH = REPOSITORY_ROOT / "data/metadata/moon_mars_phase7_experiments.json"


def _load_features(path, body, source_id, effective_resolution_m=None):
    return extract_terrain_features(
        path, body=body, source_id=source_id, effective_resolution_m=effective_resolution_m
    )


@pytest.fixture
def mars_features():
    return _load_features(MARS_PATH, "Mars", "mars_jezero_ctx_dtm", effective_resolution_m=20.0)


@pytest.fixture
def moon_features():
    return _load_features(
        MOON_PATH, "Moon", "moon_lola", effective_resolution_m=16.055973052978516
    )


def test_baseline_is_repeatable(mars_features, moon_features):
    result_a = compare_terrain(mars_features, moon_features, include_uncertainty=False)
    result_b = compare_terrain(mars_features, moon_features, include_uncertainty=False)
    assert result_a["similarity_index"] == result_b["similarity_index"]
    assert result_a["combined_distance"] == result_b["combined_distance"]
    assert result_a["confidence"] == result_b["confidence"]
    assert abs(result_a["similarity_index"] - 49.92285382858792) < 1e-9
    assert result_a["confidence"] == "HIGH"


def test_resolution_gate_admits_official_pair(mars_features, moon_features):
    resolution = assess_resolution(mars_features, moon_features)
    assert resolution.compatible is True
    assert resolution.resolution_ratio < 4.0


def test_resolution_gate_rejects_beyond_maximum_ratio(mars_features, moon_features):
    coarse_moon = _load_features(MOON_PATH, "Moon", "moon_coarse", effective_resolution_m=81.0)
    resolution = assess_resolution(mars_features, coarse_moon)
    assert resolution.compatible is False


def test_classify_confidence_rejects_incompatible_resolution(mars_features, moon_features):
    from science.similarity.comparison.uncertainty import ResolutionCompatibility

    incompatible = ResolutionCompatibility(
        compatible=False, common_analysis_scale_m=81.0, resolution_ratio=4.05,
        reason="rejected",
    )
    confidence = classify_confidence(
        target_valid_percent=100.0,
        candidate_valid_percent=100.0,
        resolution=incompatible,
        feature_count=3,
    )
    assert confidence == "INSUFFICIENT"


def test_feature_ablation_matches_phase7(mars_features, moon_features):
    expected = {
        "slope": 50.38759096672298,
        "local_relief": 50.24460531119791,
        "terrain_ruggedness": 49.14566058278336,
    }
    for feature, expected_score in expected.items():
        weights = {name: (1.0 if name == feature else 0.0) for name in expected}
        result = compare_terrain(mars_features, moon_features, weights=weights, include_uncertainty=False)
        assert abs(result["similarity_index"] - expected_score) < 1e-6


def test_weight_sensitivity_within_bounds(mars_features, moon_features):
    schemes = {
        "equal": {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0},
        "slope_emphasis": {"slope": 2.0, "local_relief": 1.0, "terrain_ruggedness": 1.0},
        "relief_emphasis": {"slope": 1.0, "local_relief": 2.0, "terrain_ruggedness": 1.0},
        "ruggedness_emphasis": {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 2.0},
    }
    baseline = compare_terrain(
        mars_features, moon_features,
        weights=schemes["equal"], include_uncertainty=False,
    )["similarity_index"]
    for name, weights in schemes.items():
        result = compare_terrain(mars_features, moon_features, weights=weights, include_uncertainty=False)
        assert abs(result["similarity_index"] - baseline) < 1.0


def test_spatial_autocorrelation_strong(mars_features, moon_features):
    experiment = json.loads(EXPERIMENT_PATH.read_text(encoding="utf-8"))
    spatial = experiment["spatial_diagnostics"]
    all_morans = []
    for body_key in ("slope", "local_relief", "terrain_ruggedness"):
        all_morans.append(spatial[body_key]["morans_i"])
        all_morans.append(spatial["moon"][body_key]["morans_i"])
    assert min(all_morans) > 0.97


def test_raster_has_crs_and_single_band(mars_features, moon_features):
    assert mars_features.crs
    assert moon_features.crs
    assert mars_features.resolution_m == (20.0, 20.0)
    assert moon_features.resolution_m == (20.0, 20.0)


def test_invalid_raster_rejected(tmp_path):
    invalid = tmp_path / "invalid.txt"
    invalid.write_text("not a raster")
    with pytest.raises(Exception):
        extract_terrain_features(invalid, body="Mars", source_id="invalid")
