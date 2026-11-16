import json
from pathlib import Path

import numpy as np

from science.data_ingestion.earthdata_auth import diagnose_earthdata_auth, earthdata_ssl_cafile
from science.similarity.comparison.bootstrap import bootstrap_tmsi
from science.similarity.features.feature_extraction import FeatureLayer, TerrainFeatureSet


ROOT = Path(__file__).resolve().parents[2]


def test_earthdata_diagnostic_is_non_secret_and_client_available() -> None:
    diagnostic = diagnose_earthdata_auth("environment")

    assert diagnostic.client_installed is True
    assert diagnostic.status in {"credentials_unavailable", "authenticated", "authentication_error"}
    assert "password" not in diagnostic.message.lower()
    assert Path(earthdata_ssl_cafile()).is_file()


def test_cmr_manifest_records_exact_granule_ids_and_protected_links() -> None:
    manifest = json.loads((ROOT / "data/metadata/earth_nasadem_cmr.json").read_text())
    assert len(manifest["granules"]) >= 4
    assert all(item["granule_id"].startswith("G") for item in manifest["granules"])
    assert all("lp-prod-protected" in item["data_links"][0] for item in manifest["granules"])


def test_spatial_bootstrap_returns_uncertainty_interval() -> None:
    grid = np.arange(64, dtype="float32").reshape(8, 8)
    layer = FeatureLayer("slope", grid, "degrees", None, "synthetic")
    target = TerrainFeatureSet("target", "Mars", (20.0, 20.0), "Mars", 100.0, {"slope": layer}, {}, 20.0)
    candidate = TerrainFeatureSet("candidate", "Moon", (20.0, 20.0), "Moon", 100.0, {"slope": layer}, {}, 20.0)

    result = bootstrap_tmsi(target, candidate, {"slope": 1.0}, block_size_m=40.0, repetitions=8)

    assert result["repetitions"] == 8
    assert result["tmsi_lower_95"] <= result["tmsi_upper_95"]
    assert result["target_block_size_cells"] == 2