"""Generate reproducible Phase 7 validation experiments for the real Moon-Mars pair."""

import hashlib
import importlib.metadata
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from science.similarity.comparison.bootstrap import block_size_sensitivity, bootstrap_tmsi
from science.similarity.comparison.distance import compare_distributions
from science.similarity.comparison.spatial import spatial_feature_diagnostics
from science.similarity.features.feature_extraction import extract_terrain_features
from science.similarity.scoring.similarity import compare_terrain
from science.similarity.scoring.weights import DEFAULT_WEIGHTS, validate_weights

from .benchmark_registry import BENCHMARKS, validate_registry


ROOT = Path(__file__).resolve().parents[3]
MARS_PATH = ROOT / "data/processed/mars_jezero_ctx_elevation_m.tif"
MOON_PATH = ROOT / "data/processed/moon_lola_80s_20m_elevation_m.tif"
MARS_METADATA = ROOT / "data/metadata/mars_jezero_ctx_dtm.json"
MOON_METADATA = ROOT / "data/metadata/moon_lola.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _versions() -> dict[str, str]:
    names = ("numpy", "scipy", "rasterio", "geopandas", "pandas", "earthaccess")
    return {name: importlib.metadata.version(name) for name in names}


def _provenance(mars, moon) -> dict[str, Any]:
    return {
        "datasets": [
            {"id": "mars_jezero_ctx_dtm", "body": "Mars", "manifest": json.loads(MARS_METADATA.read_text()), "processed_sha256": _sha256(MARS_PATH), "feature_metadata": mars.source_metadata},
            {"id": "moon_lola", "body": "Moon", "manifest": json.loads(MOON_METADATA.read_text()), "processed_sha256": _sha256(MOON_PATH), "feature_metadata": moon.source_metadata},
        ],
        "feature_definitions": {
            "slope": "gradient magnitude in degrees using native projected metre spacing",
            "local_relief": "max minus min elevation in a complete 60 m physical window",
            "terrain_ruggedness": "Riley TRI sqrt(mean squared center-to-neighbor differences) in a complete 60 m window",
        },
        "feature_parameters": {"local_neighborhood_m": 60.0, "ruggedness_neighborhood_m": 60.0},
        "masking": "finite values and raster masks only; invalid feature neighborhoods excluded",
        "distance": "Wasserstein distance with KS diagnostics",
        "normalization": "Wasserstein divided by larger pooled IQR",
        "scoring": {"formula": "100 * exp(-D)", "weights": DEFAULT_WEIGHTS},
        "software_versions": _versions(),
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def _normalization_sensitivity(mars, moon) -> dict[str, Any]:
    diagnostics: dict[str, Any] = {}
    weighted_iqr_distance = 0.0
    weighted_std_distance = 0.0
    for name in DEFAULT_WEIGHTS:
        target = mars.features[name].valid_values()
        candidate = moon.features[name].valid_values()
        distance = compare_distributions(target, candidate)
        pooled_std = max(float(target.std()), float(candidate.std()))
        std_normalized = distance.wasserstein / max(pooled_std, 1e-12)
        diagnostics[name] = {
            "wasserstein": distance.wasserstein,
            "pooled_iqr": distance.pooled_iqr,
            "pooled_iqr_normalized": distance.normalized_distance,
            "pooled_std": pooled_std,
            "pooled_std_normalized": std_normalized,
        }
        weighted_iqr_distance += distance.normalized_distance
        weighted_std_distance += std_normalized
    return {
        "feature_diagnostics": diagnostics,
        "official_pooled_iqr_tmsi": float(100.0 * __import__("math").exp(-weighted_iqr_distance / 3.0)),
        "diagnostic_pooled_std_tmsi": float(100.0 * __import__("math").exp(-weighted_std_distance / 3.0)),
        "official_normalization": "Wasserstein divided by larger pooled IQR",
        "alternative_diagnostic": "Wasserstein divided by larger feature standard deviation; not the official score",
    }


def run_phase7(output_path: Path) -> dict[str, Any]:
    validate_registry()
    mars = extract_terrain_features(MARS_PATH, body="Mars", source_id="mars_jezero_ctx_dtm", effective_resolution_m=20.0)
    moon = extract_terrain_features(MOON_PATH, body="Moon", source_id="moon_lola", effective_resolution_m=16.055973052978516)
    equal_weights = validate_weights()
    baseline = compare_terrain(mars, moon, equal_weights)
    primary = bootstrap_tmsi(mars, moon, equal_weights, block_size_m=320.0, repetitions=1000, seed=42)
    convergence = {
        "repetitions": [64, 256, 1000],
        "results": {
            str(repetitions): bootstrap_tmsi(mars, moon, equal_weights, block_size_m=320.0, repetitions=repetitions, seed=42)
            for repetitions in (64, 256, 1000)
        },
        "endpoint_stability_1000_vs_64": {
            "lower_delta": primary["tmsi_lower_95"] - bootstrap_tmsi(mars, moon, equal_weights, block_size_m=320.0, repetitions=64, seed=42)["tmsi_lower_95"],
            "upper_delta": primary["tmsi_upper_95"] - bootstrap_tmsi(mars, moon, equal_weights, block_size_m=320.0, repetitions=64, seed=42)["tmsi_upper_95"],
        },
    }
    seeds = {str(seed): bootstrap_tmsi(mars, moon, equal_weights, block_size_m=320.0, repetitions=256, seed=seed) for seed in (42, 123, 987)}
    ablation: dict[str, Any] = {}
    for feature in DEFAULT_WEIGHTS:
        weights = {name: 1.0 if name == feature else 0.0 for name in DEFAULT_WEIGHTS}
        ablation[feature] = {"weights": weights, "score": compare_terrain(mars, moon, weights), "bootstrap": bootstrap_tmsi(mars, moon, weights, block_size_m=320.0, repetitions=256, seed=42), "block_size_sensitivity": block_size_sensitivity(mars, moon, weights)}
    ablation["all_features"] = {"weights": DEFAULT_WEIGHTS, "score": baseline, "bootstrap": primary, "block_size_sensitivity": block_size_sensitivity(mars, moon, DEFAULT_WEIGHTS)}
    weight_sets = {
        "equal": DEFAULT_WEIGHTS,
        "slope_emphasis": {"slope": 2.0, "local_relief": 1.0, "terrain_ruggedness": 1.0},
        "local_relief_emphasis": {"slope": 1.0, "local_relief": 2.0, "terrain_ruggedness": 1.0},
        "ruggedness_emphasis": {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 2.0},
    }
    weighting = {name: {"weights": weights, "score": compare_terrain(mars, moon, weights), "bootstrap": bootstrap_tmsi(mars, moon, weights, block_size_m=320.0, repetitions=256, seed=42)} for name, weights in weight_sets.items()}
    spatial = spatial_feature_diagnostics({name: layer.values for name, layer in mars.features.items()}, mars.resolution_m) | {"moon": spatial_feature_diagnostics({name: layer.values for name, layer in moon.features.items()}, moon.resolution_m)}
    report: dict[str, Any] = {
        "experiment": "moon_mars_phase7_validation",
        "baseline_result": baseline,
        "primary_bootstrap_320m_1000": primary,
        "bootstrap_convergence": convergence,
        "seed_sensitivity": seeds,
        "feature_ablation": ablation,
        "weight_sensitivity": weighting,
        "normalization_sensitivity": _normalization_sensitivity(mars, moon),
        "spatial_diagnostics": spatial,
        "benchmarks": {"registry": BENCHMARKS, "real_benchmark_findings": [], "limitation": "No independently labeled real benchmark dataset was available; synthetic entries remain test-only."},
        "provenance": _provenance(mars, moon),
        "interpretation": [
            "TMSI compares terrain-feature distributions, not complete spatial geomorphology.",
            "Bootstrap intervals reflect spatial block sampling assumptions, not physical equivalence probabilities.",
            "No Earth experiment is executed because NASADEM remains pending.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    output = ROOT / "data/metadata/moon_mars_phase7_experiments.json"
    report = run_phase7(output)
    print(json.dumps({"output": str(output), "baseline_tmsi": report["baseline_result"]["similarity_index"], "bootstrap_repetitions": report["primary_bootstrap_320m_1000"]["repetitions"]}, indent=2))


if __name__ == "__main__":
    main()