"""Phase 12 tests: scientific metadata schema validation and export preservation."""

from fastapi.testclient import TestClient

from app.main import app

from science.metadata.schema import (
    ComparisonMetadata,
    FeatureComparison,
    OverlapClassification,
    SamplingInfo,
    SamplingStrategy,
    WindowInfo,
    make_comparison_id,
)
from science.metadata.serialization import (
    build_comparison_metadata,
    merge_metadata_into_export,
    validate_export_metadata,
    window_info_from_feature_set,
)
from science.metadata.validation import MetadataValidationError, require_complete, validate_metadata


client = TestClient(app)


def _base_window(label: str, body: str, source_id: str, col_off: int = 0, row_off: int = 0) -> WindowInfo:
    return WindowInfo(
        label=label,
        body=body,
        source_id=source_id,
        col_off=col_off,
        row_off=row_off,
        width_cells=512,
        height_cells=512,
        extent_km=10.24,
    )


def test_metadata_schema_required_fields():
    """Required fields must be present; missing them raises."""
    wa = _base_window("Mars w0", "Mars", "mars_jezero_ctx_dtm")
    wb = _base_window("Moon w0", "Moon", "moon_lola")
    si = SamplingInfo(
        overlap_ratio=0.0,
        overlap_classification=OverlapClassification.NONE,
        sampling_strategy=SamplingStrategy.MULTIPLE_WINDOWS,
    )
    md = ComparisonMetadata(
        comparison_id="test_id",
        experiment_id="exp1",
        body_a="Mars",
        body_b="Moon",
        dataset_id_a="mars_jezero_ctx_dtm",
        dataset_id_b="moon_lola",
        window_a=wa,
        window_b=wb,
        spatial_extent_km=10.24,
        sampling=si,
    )
    assert md.comparison_id == "test_id"
    assert md.similarity_index is None  # optional


def test_metadata_missing_required_raises():
    wa = _base_window("Mars w0", "Mars", "mars_jezero_ctx_dtm")
    wb = _base_window("Moon w0", "Moon", "moon_lola")
    si = SamplingInfo(
        overlap_ratio=0.0,
        overlap_classification=OverlapClassification.NONE,
        sampling_strategy=SamplingStrategy.MULTIPLE_WINDOWS,
    )
    try:
        ComparisonMetadata(
            comparison_id="",
            experiment_id="exp1",
            body_a="Mars",
            body_b="Moon",
            dataset_id_a="mars_jezero_ctx_dtm",
            dataset_id_b="moon_lola",
            window_a=wa,
            window_b=wb,
            spatial_extent_km=10.24,
            sampling=si,
        )
        raise AssertionError("expected ValueError for empty comparison_id")
    except ValueError:
        pass


def test_validate_metadata_reports_overlap_inconsistency():
    wa = _base_window("Mars w0", "Mars", "mars_jezero_ctx_dtm")
    wb = _base_window("Moon w0", "Moon", "moon_lola")
    # ratio 1.0 -> identical, but classification says none -> inconsistent
    si = SamplingInfo(
        overlap_ratio=1.0,
        overlap_classification=OverlapClassification.NONE,
        sampling_strategy=SamplingStrategy.MULTIPLE_WINDOWS,
    )
    md = ComparisonMetadata(
        comparison_id="tid",
        experiment_id="exp1",
        body_a="Mars",
        body_b="Moon",
        dataset_id_a="mars_jezero_ctx_dtm",
        dataset_id_b="moon_lola",
        window_a=wa,
        window_b=wb,
        spatial_extent_km=10.24,
        sampling=si,
    )
    problems = validate_metadata(md)
    assert any("inconsistent" in p for p in problems)


def test_require_complete_raises_on_errors():
    wa = _base_window("Mars w0", "Mars", "mars_jezero_ctx_dtm")
    wb = _base_window("Moon w0", "Moon", "moon_lola")
    # ratio 1.0 -> identical, but classification says NONE -> inconsistency error
    si = SamplingInfo(
        overlap_ratio=1.0,
        overlap_classification=OverlapClassification.NONE,
        sampling_strategy=SamplingStrategy.MULTIPLE_WINDOWS,
    )
    md = ComparisonMetadata(
        comparison_id="tid",
        experiment_id="exp1",
        body_a="Mars",
        body_b="Moon",
        dataset_id_a="mars_jezero_ctx_dtm",
        dataset_id_b="moon_lola",
        window_a=wa,
        window_b=wb,
        spatial_extent_km=10.24,
        sampling=si,
    )
    try:
        require_complete(md)
        raise AssertionError("expected MetadataValidationError")
    except MetadataValidationError:
        pass


def test_build_comparison_metadata_roundtrip():
    wa = _base_window("Mars w0", "Mars", "mars_jezero_ctx_dtm")
    wb = _base_window("Moon w0", "Moon", "moon_lola")
    si = SamplingInfo(
        overlap_ratio=0.0,
        overlap_classification=OverlapClassification.NONE,
        sampling_strategy=SamplingStrategy.MULTIPLE_WINDOWS,
    )
    md = build_comparison_metadata(
        experiment_id="exp1",
        body_a="Mars",
        body_b="Moon",
        dataset_id_a="mars_jezero_ctx_dtm",
        dataset_id_b="moon_lola",
        window_a=wa,
        window_b=wb,
        spatial_extent_km=10.24,
        sampling=si,
        similarity_index=49.92285382858792,
        combined_distance=0.694691295520326,
        confidence="HIGH",
        algorithm_version="0.1.0",
        random_seed=42,
    )
    assert md.similarity_index == 49.92285382858792
    assert md.confidence == "HIGH"
    d = md.to_dict()
    assert d["comparison_id"].startswith("mars_mars_jezero_ctx_dtm_vs_moon_moon_lola")
    md2 = ComparisonMetadata.from_dict(d)
    assert md2.comparison_id == md.comparison_id


def test_merge_metadata_into_export_preserves_existing():
    wa = _base_window("Mars w0", "Mars", "mars_jezero_ctx_dtm")
    wb = _base_window("Moon w0", "Moon", "moon_lola")
    si = SamplingInfo(
        overlap_ratio=0.0,
        overlap_classification=OverlapClassification.NONE,
        sampling_strategy=SamplingStrategy.MULTIPLE_WINDOWS,
    )
    md = build_comparison_metadata(
        experiment_id="exp1",
        body_a="Mars",
        body_b="Moon",
        dataset_id_a="mars_jezero_ctx_dtm",
        dataset_id_b="moon_lola",
        window_a=wa,
        window_b=wb,
        spatial_extent_km=10.24,
        sampling=si,
    )
    pkg = {"experiment": "test", "existing_key": "preserved"}
    merged = merge_metadata_into_export(pkg, md)
    assert merged["existing_key"] == "preserved"
    assert "comparison_metadata" in merged
    assert merged["comparison_metadata"]["comparison_id"] == md.comparison_id


def test_validate_export_metadata_missing_block():
    problems = validate_export_metadata({"experiment": "test"})
    assert any("missing" in p.lower() for p in problems)


def test_validate_export_metadata_invalid_block():
    problems = validate_export_metadata({"comparison_metadata": {"not_a_real_field": 1}})
    assert len(problems) > 0


def test_make_comparison_id_deterministic():
    wa = _base_window("Mars w0", "Mars", "mars_jezero_ctx_dtm")
    wb = _base_window("Moon w0", "Moon", "moon_lola")
    id1 = make_comparison_id("Mars", "Moon", "mars_jezero_ctx_dtm", "moon_lola", 10.24, wa, wb)
    id2 = make_comparison_id("Mars", "Moon", "mars_jezero_ctx_dtm", "moon_lola", 10.24, wa, wb)
    assert id1 == id2
    # Different extent -> different id
    id3 = make_comparison_id("Mars", "Moon", "mars_jezero_ctx_dtm", "moon_lola", 20.48, wa, wb)
    assert id3 != id1


def test_api_contracts_unchanged():
    """Existing API contracts still work (backward compatibility)."""
    r = client.get("/api/similarity/status")
    assert r.status_code == 200
    assert r.json()["validated_comparisons"] == ["moon_mars"]
    r = client.post(
        "/api/similarity/compare",
        json={"target_dataset_id": "mars_jezero_ctx_dtm", "candidate_dataset_id": "earth_nasadem_hgt_v001"},
    )
    assert r.status_code == 409
