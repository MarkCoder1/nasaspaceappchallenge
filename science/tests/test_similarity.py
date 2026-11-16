from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from science.similarity.comparison.distance import compare_distributions
from science.similarity.features.feature_extraction import FeatureLayer, TerrainFeatureSet, extract_terrain_features
from science.similarity.scoring.sensitivity import run_weight_sensitivity
from science.similarity.scoring.similarity import compare_terrain


def write_synthetic_dem(path: Path, values: np.ndarray, resolution: float = 20.0) -> None:
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=values.shape[1],
        height=values.shape[0],
        count=1,
        dtype="float32",
        crs="ESRI:103885",
        transform=from_origin(0, values.shape[0] * resolution, resolution, resolution),
        nodata=-9999,
    ) as dataset:
        dataset.write(values.astype("float32"), 1)


def make_feature_set(source_id: str, body: str, values: np.ndarray, resolution: float = 20.0, valid_percent: float = 100.0) -> TerrainFeatureSet:
    layers = {
        "slope": FeatureLayer("slope", values, "degrees", None, "synthetic slope"),
        "local_relief": FeatureLayer("local_relief", values, "m", 60.0, "synthetic relief"),
        "terrain_ruggedness": FeatureLayer("terrain_ruggedness", values, "m", 60.0, "synthetic TRI"),
    }
    return TerrainFeatureSet(source_id, body, (resolution, resolution), "synthetic", valid_percent, layers, {"synthetic": True})


def test_synthetic_flat_dem_has_zero_slope_relief_and_ruggedness(tmp_path: Path) -> None:
    path = tmp_path / "flat_mars.tif"
    write_synthetic_dem(path, np.full((9, 9), 100.0))
    features = extract_terrain_features(path, body="Mars", source_id="synthetic-flat")

    assert np.nanmax(features.features["slope"].values) == 0.0
    assert np.nanmax(features.features["local_relief"].values) == 0.0
    assert np.nanmax(features.features["terrain_ruggedness"].values) == 0.0


def test_identical_distributions_have_zero_distance() -> None:
    distance = compare_distributions(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0]))
    assert distance.wasserstein == 0.0
    assert distance.ks_statistic == 0.0


def test_larger_feature_difference_reduces_similarity() -> None:
    identical = compare_terrain(make_feature_set("a", "Mars", np.array([1.0, 2.0, 3.0])), make_feature_set("b", "Earth", np.array([1.0, 2.0, 3.0])))
    different = compare_terrain(make_feature_set("a", "Mars", np.array([1.0, 2.0, 3.0])), make_feature_set("c", "Earth", np.array([10.0, 20.0, 30.0])))

    assert identical["similarity_index"] == 100.0
    assert different["similarity_index"] < identical["similarity_index"]


def test_resolution_and_coverage_reject_unreliable_comparisons() -> None:
    incompatible = compare_terrain(
        make_feature_set("a", "Mars", np.array([1.0, 2.0, 3.0]), resolution=20.0),
        make_feature_set("b", "Earth", np.array([1.0, 2.0, 3.0]), resolution=100.0),
    )
    missing = compare_terrain(
        make_feature_set("a", "Mars", np.array([1.0, 2.0, 3.0]), valid_percent=40.0),
        make_feature_set("b", "Earth", np.array([1.0, 2.0, 3.0]), valid_percent=100.0),
    )

    assert incompatible["similarity_index"] is None
    assert incompatible["confidence"] == "INSUFFICIENT"
    assert missing["confidence"] == "INSUFFICIENT"


def test_weight_sensitivity_reports_configurations() -> None:
    target = make_feature_set("a", "Mars", np.array([1.0, 2.0, 3.0]))
    candidate = make_feature_set("b", "Earth", np.array([1.0, 2.0, 4.0]))
    sensitivity = run_weight_sensitivity(
        target,
        candidate,
        {"equal": {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0}, "slope_only": {"slope": 1.0}},
    )

    assert set(sensitivity["results"]) == {"equal", "slope_only"}
    assert sensitivity["score_range"] is not None