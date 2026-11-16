import hashlib
import json
from pathlib import Path

from science.similarity.comparison.uncertainty import assess_resolution
from science.similarity.features.feature_extraction import FeatureLayer, TerrainFeatureSet


ROOT = Path(__file__).resolve().parents[2]


def test_lola_provenance_and_validation_state() -> None:
    metadata = json.loads((ROOT / "data/metadata/moon_lola.json").read_text())
    report = json.loads((ROOT / "data/metadata/moon_lola_preprocessing.json").read_text())
    raw_path = ROOT / metadata["local_file"]

    assert metadata["state"] == "VALIDATED"
    assert report["state"] == "VALIDATED"
    assert hashlib.sha256(raw_path.read_bytes()).hexdigest() == metadata["sha256"]
    assert report["validation"]["body"] == "Moon"


def test_lola_effective_resolution_is_recorded_separately() -> None:
    metadata = json.loads((ROOT / "data/metadata/moon_lola.json").read_text())
    summary = metadata["effective_resolution_summary"]

    assert metadata["nominal_resolution"] == "20 m/pixel"
    assert summary["mean"] < 20.0
    assert summary["minimum"] > 0
    assert summary["read_overview_divisor"] == 64


def test_effective_resolution_enters_compatibility_gate() -> None:
    values = __import__("numpy").array([1.0, 2.0, 3.0])
    layer = FeatureLayer("slope", values, "degrees", None, "synthetic")
    mars = TerrainFeatureSet("mars", "Mars", (20.0, 20.0), "Mars", 100.0, {"slope": layer}, {}, 20.0)
    moon = TerrainFeatureSet("moon", "Moon", (20.0, 20.0), "Moon", 100.0, {"slope": layer}, {}, 16.055973)

    result = assess_resolution(mars, moon)

    assert result.compatible
    assert result.resolution_ratio < 2


def test_earth_manifest_remains_pending_without_a_local_file() -> None:
    metadata = json.loads((ROOT / "data/metadata/earth_nasadem_hgt_v001.json").read_text())

    assert metadata["state"] == "PENDING"
    assert metadata["access_status"] == "BLOCKED_BY_EARTHDATA_AUTHENTICATION"
    assert not (ROOT / "data/raw/NASADEM_HGT_s23w068.zip").exists()