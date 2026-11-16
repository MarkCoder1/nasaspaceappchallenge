import json
from pathlib import Path

import numpy as np

from science.similarity.comparison.spatial import morans_i, semivariogram
from science.similarity.validation.benchmark_registry import validate_registry


ROOT = Path(__file__).resolve().parents[2]


def test_phase7_experiment_artifact_is_reproducibility_complete() -> None:
    artifact = json.loads((ROOT / "data/metadata/moon_mars_phase7_experiments.json").read_text())
    provenance = artifact["provenance"]

    assert artifact["baseline_result"]["similarity_index"] == 49.92285382858792
    assert artifact["primary_bootstrap_320m_1000"]["repetitions"] == 1000
    assert provenance["datasets"][0]["processed_sha256"]
    assert provenance["scoring"]["weights"]
    assert provenance["software_versions"]["numpy"]


def test_spatial_diagnostics_detect_positive_structure() -> None:
    gradient = np.arange(64, dtype="float32").reshape(8, 8)

    assert morans_i(gradient) > 0
    result = semivariogram(gradient, (20.0, 20.0), lags_cells=(1, 2))
    assert result[0]["pair_count"] > 0
    assert result[0]["lag_m"] == 20.0


def test_benchmark_registry_contains_no_production_findings() -> None:
    validate_registry()
    registry = json.loads((ROOT / "data/metadata/benchmark_registry.json").read_text())

    assert registry["real_benchmark_findings"] == []
    assert all(item["production_eligible"] is False for item in registry["benchmarks"])