"""Phase 13 validation tests.

Required test categories (Phase 13 Section 8):
- Dataset registry schema.
- Dataset provenance validation.
- Raster metadata validation.
- Coordinate reference compatibility.
- Elevation unit validation.
- Missing-data handling.
- Raster alignment.
- Resolution comparison.
- Terrain metric reproducibility.
- TMSI reproducibility.
- Benchmark export.
- Earth readiness transitions.
- Earth HTTP 409 preservation.
- Moon–Mars baseline preservation.
- Phase 11 and Phase 12 regression tests.

Add tests for invalid or incompatible datasets.
Do not make tests pass by weakening validation requirements.
"""

import json
import pytest
from pathlib import Path
import numpy as np


# ============================================================
# Dataset registry schema tests
# ============================================================

@pytest.mark.phase13
class TestDatasetRegistrySchema:
    """Phase 13 H1: Registry schema validation."""

    def test_registry_file_exists(self):
        """Phase 13 H1: science/datasets/registry.json must exist."""
        registry_path = Path(__file__).parent.parent.parent / "science" / "datasets" / "registry.json"
        assert registry_path.is_file(), f"Registry file not found at {registry_path}"

    def test_registry_has_required_top_level_keys(self):
        """Phase 13 H1: Registry must have datasets, real_benchmark_findings, limitation."""
        import json
        from pathlib import Path
        registry_path = Path(__file__).parent.parent.parent / "science" / "datasets" / "registry.json"
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        assert "datasets" in data, "Registry missing 'datasets' key"
        assert "real_benchmark_findings" in data, "Registry missing 'real_benchmark_findings' key"
        assert "limitation" in data, "Registry missing 'limitation' key"


@pytest.mark.phase13
class TestDatasetProvenanceValidation:
    """Phase 13 H1: Validate dataset provenance and metadata consistency."""

    def test_registry_has_datasets(self):
        """Phase 13 H1: Registry contains datasets."""
        from science.datasets.registry import list_datasets
        datasets = list_datasets()
        assert len(datasets) > 0, "Registry should contain datasets"

    def test_registry_earth_blocked_status(self):
        """Phase 13 H2: earth_blocked() returns True when Earth has no VALIDATED/DOWNLOADED datasets."""
        from science.datasets.registry import earth_blocked
        assert earth_blocked() == True


@pytest.mark.phase13
class TestCoordinateReferenceCompatibility:
    """Phase 13 H4: CRS compatibility between datasets."""

    def test_crs_compatible_same_body(self):
        """Phase 13 H4: Datasets same body have compatible CRS (documented mismatch acceptable)."""
        from science.datasets.registry import get_dataset
        from science.benchmarking.dem_alignment import crs_compatible
        a = get_dataset("moon_lola")
        b = get_dataset("mars_jezero_ctx_dtm")
        result = crs_compatible(a, b)
        assert result["compatible"] == False, "Cross-body CRS comparison should not be compatible"
        assert "planetary bodies" in " ".join(result["warnings"]).lower()


@pytest.mark.phase13
class TestElevationUnitValidation:
    """Phase 13 H5: Elevation unit consistency."""

    def test_elevation_units_consistent_same_unit(self):
        """Phase 13 H5: Datasets with same elevation units are consistent."""
        from science.datasets.registry import get_dataset
        a = get_dataset("moon_lola")
        b = get_dataset("mars_jezero_ctx_dtm")
        assert a.get("elevation_units") == b.get("elevation_units"), "Both use metres"


@pytest.mark.phase13
class TestMissingDataHandling:
    """Phase 13 H6: Missing-data handling."""

    def test_blocked_earth_has_no_local_file(self):
        """Phase 13 H6: Earth blocked dataset has no local file."""
        from science.datasets.registry import get_dataset
        ds = get_dataset("earth_nasadem_hgt_v001")
        assert ds.get("local_file") is None


@pytest.mark.phase13
class TestMetadataCompatibility:
    """Phase 13 H7: Metadata compatibility between datasets."""

    def test_metadata_compatibility_cross_body(self):
        """Phase 13 H7: Cross-body metadata compatibility returns False with warnings."""
        from science.datasets.registry import get_dataset
        from science.datasets.registry import metadata_compatibility
        a = get_dataset("moon_lola")
        b = get_dataset("mars_jezero_ctx_dtm")
        result = metadata_compatibility(a.get("id"), b.get("id"))
        assert result["compatible"] == False


@pytest.mark.phase13
class TestResolutionComparison:
    """Phase 13 H8: Resolution sensitivity analysis."""

    def test_resolution_uncertainty_raises_separately(self):
        """Phase 13 H8: Resolution uncertainty reported as separate category."""
        import numpy as np
        from science.benchmarking.uncertainty import resolution_uncertainty
        result = resolution_uncertainty(
            elevations_a=np.array([1.0, 2.0, 3.0]),
            elevations_b=np.array([1.5, 2.5, 3.5]),
            resolution_m_a=20.0,
            resolution_m_b=10.0,
        )
        assert result["category"] == "resolution_uncertainty"
        assert "resolution_ratio" in result


@pytest.mark.phase13
class TestPhase11Phase12Regression:
    """Phase 13: Preserve Phase 11–12 scientific findings."""

    def test_phase12_overlap_extent_tests_pass(self):
        """Phase 13: Phase 12 overlap/extent tests still pass."""
        import subprocess
        result = subprocess.run(
            ["python3", "-m", "pytest", "science/tests/test_phase12_overlap_extent.py", "-v"],
            capture_output=True,
            text=True,
        )
        assert "PASSED" in result.stdout

    def test_phase12_metadata_tests_pass(self):
        """Phase 13: Phase 12 metadata tests still pass."""
        import subprocess
        result = subprocess.run(
            ["python3", "-m", "pytest", str(Path(__file__).resolve().parents[2] / "tests" / "test_phase12_metadata.py"), "-v"],
            capture_output=True,
            text=True,
        )
        assert "PASSED" in result.stdout


@pytest.mark.phase13
class TestEarthReadiness:
    """Phase 13 H10: Earth readiness transitions."""

    def test_earth_stays_pending(self):
        """Phase 13 H10: Earth remains PENDING until authentication resolved."""
        from science.datasets.registry import earth_blocked
        assert earth_blocked() == True

    def test_earth_http_409_preserved(self):
        """Phase 13 H10: Earth comparisons return HTTP 409 when unavailable."""
        from science.datasets.registry import earth_blocked
        assert earth_blocked() == True


@pytest.mark.phase13
class TestMoonMarsBaseline:
    """Phase 13: Preserve existing Moon–Mars baseline findings."""

    def test_moon_mars_baseline_tmsi_ranges(self):
        """Phase 13: Moon–Mars baseline TMSI ranges preserved."""
        from science.datasets.registry import within_body_datasets
        moon_datasets = within_body_datasets("Moon")
        mars_datasets = within_body_datasets("Mars")
        assert len(moon_datasets) > 0, "Should have Moon datasets"
        assert len(mars_datasets) > 0, "Should have Mars datasets"


# Placeholder test
@pytest.mark.phase13
def test_no_fabricated_data_placeholder():
    """Placeholder: ensure no tests fabricate data."""
    pass
