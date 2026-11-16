"""Phase 12 tests: overlap classification, identical-window detection, extent mismatch,
resolution warnings, and missing-data handling."""

import json
from pathlib import Path

import pytest

from science.metadata.schema import (
    ComparisonMetadata,
    OverlapClassification,
    SamplingInfo,
    SamplingStrategy,
    WindowInfo,
)
from science.metadata.serialization import window_info_from_feature_set
from science.metadata.validation import validate_metadata
from science.similarity.comparison.extent import (
    diagnose_extent_sensitivity,
    cells_to_extent_km,
    extent_km_to_cells,
)
from science.similarity.comparison.overlap import (
    classify_overlap,
    compute_overlap_fraction,
    diagnose_overlap,
    is_identical_window,
)
from science.similarity.features.feature_extraction import TerrainFeatureSet

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PHASE11_OUTPUT = REPOSITORY_ROOT / "data/metadata/phase11_sampling_framework.json"
PHASE10_EXTENT_OUTPUT = REPOSITORY_ROOT / "data/metadata/phase10_extent_sensitivity.json"


def _win(label, body, source_id, col_off, row_off, n=512, extent=10.24):
    return WindowInfo(
        label=label, body=body, source_id=source_id,
        col_off=col_off, row_off=row_off,
        width_cells=n, height_cells=n, extent_km=extent,
    )


# ---------- Overlap classification ----------

def test_classify_overlap_thresholds():
    assert classify_overlap(1.0) == OverlapClassification.IDENTICAL
    assert classify_overlap(0.99) == OverlapClassification.IDENTICAL
    assert classify_overlap(0.5) == OverlapClassification.HIGH
    assert classify_overlap(0.51) == OverlapClassification.HIGH
    assert classify_overlap(0.01) == OverlapClassification.PARTIAL
    assert classify_overlap(0.0) == OverlapClassification.NONE
    assert classify_overlap(None) == OverlapClassification.UNKNOWN


def test_compute_overlap_fraction_identical():
    wa = _win("a", "Mars", "s1", 0, 0)
    wb = _win("b", "Mars", "s2", 0, 0)
    assert compute_overlap_fraction(wa, wb) == 1.0


def test_compute_overlap_fraction_none():
    wa = _win("a", "Mars", "s1", 0, 0, n=512)
    wb = _win("b", "Mars", "s2", 512, 0, n=512)
    assert compute_overlap_fraction(wa, wb) == 0.0


def test_compute_overlap_fraction_partial():
    wa = _win("a", "Mars", "s1", 0, 0, n=512)
    wb = _win("b", "Mars", "s2", 256, 0, n=512)
    assert abs(compute_overlap_fraction(wa, wb) - 0.5) < 1e-9


def test_compute_overlap_fraction_cross_body_is_none():
    wa = _win("a", "Mars", "s1", 0, 0)
    wb = _win("b", "Moon", "s2", 0, 0)
    assert compute_overlap_fraction(wa, wb) is None


def test_diagnose_overlap_cross_body_unknown():
    wa = _win("a", "Mars", "s1", 0, 0)
    wb = _win("b", "Moon", "s2", 0, 0)
    d = diagnose_overlap(wa, wb)
    assert d.classification == OverlapClassification.UNKNOWN
    assert d.comparable is False


# ---------- Identical-window detection ----------

def test_is_identical_window_true():
    wa = _win("a", "Mars", "s1", 100, 200, n=512)
    wb = _win("b", "Mars", "s2", 100, 200, n=512)
    assert is_identical_window(wa, wb) is True


def test_is_identical_window_false_different_offset():
    wa = _win("a", "Mars", "s1", 0, 0, n=512)
    wb = _win("b", "Mars", "s2", 100, 0, n=512)
    assert is_identical_window(wa, wb) is False


def test_is_identical_window_false_different_body():
    wa = _win("a", "Mars", "s1", 0, 0)
    wb = _win("b", "Moon", "s2", 0, 0)
    assert is_identical_window(wa, wb) is False


# ---------- Extent mismatch detection ----------

def test_extent_sensitivity_flags_material_difference():
    d = diagnose_extent_sensitivity(10.24, 31.92)
    assert d.sensitivity_flag is True
    assert abs(d.extent_ratio - (10.24 / 31.92)) < 1e-9


def test_extent_sensitivity_consistent():
    d = diagnose_extent_sensitivity(30.0, 31.92)
    assert d.sensitivity_flag is False


def test_cells_to_extent_km_roundtrip():
    assert abs(cells_to_extent_km(512) - 10.24) < 1e-9
    assert extent_km_to_cells(10.24) == 512


def test_extent_zero_raises():
    try:
        diagnose_extent_sensitivity(0.0, 31.92)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


# ---------- Missing-data handling ----------

def test_metadata_missing_data_percent_valid_range():
    wa = _win("a", "Mars", "s1", 0, 0)
    wb = _win("b", "Moon", "s2", 0, 0)
    try:
        SamplingInfo(
            overlap_ratio=0.0,
            overlap_classification=OverlapClassification.NONE,
            sampling_strategy=SamplingStrategy.MULTIPLE_WINDOWS,
            missing_data_percent=150.0,
        )
        raise AssertionError("expected ValueError for missing_data_percent > 100")
    except ValueError:
        pass


# ---------- Window info from feature set ----------

def test_window_info_from_feature_set():
    fset = TerrainFeatureSet(
        source_id="test",
        body="Mars",
        resolution_m=(20.0, 20.0),
        crs="EPSG:4326",
        valid_percent=100.0,
        features={},
        source_metadata={
            "path": str(Path(__file__)),
            "width": 100,
            "height": 100,
            "bounds": [0, 0, 2000, 2000],
            "crs_wkt": "EPSG:4326",
            "resolution_m": [20.0, 20.0],
            "source_valid_percent": 100.0,
        },
    )
    wi = window_info_from_feature_set(
        fset, label="test w", col_off=10, row_off=20, n_cells=50, extent_km=1.0,
    )
    assert wi.label == "test w"
    assert wi.body == "Mars"
    assert wi.col_off == 10
    assert wi.row_off == 20
    assert wi.width_cells == 50
    assert wi.resolution_m == 20.0
    assert wi.valid_percent == 100.0


# ---------- Phase 11 findings reproducibility ----------

def test_phase11_identical_windows_self_control_is_100():
    payload = json.loads(PHASE11_OUTPUT.read_text(encoding="utf-8"))
    self_controls = [
        r for r in payload["overlap_bias"] if r["overlap_status"] == "identical"
    ]
    assert len(self_controls) > 0
    for r in self_controls:
        assert abs(r["similarity_index"] - 100.0) < 1e-6
        assert r["overlap_fraction"] == 1.0


def test_phase11_overlapping_windows_identified():
    payload = json.loads(PHASE11_OUTPUT.read_text(encoding="utf-8"))
    high = [r for r in payload["overlap_bias"] if r["overlap_status"] == "high"]
    assert len(high) > 0
    for r in high:
        assert r["overlap_fraction"] >= 0.5


def test_phase11_non_overlapping_distinguishable():
    payload = json.loads(PHASE11_OUTPUT.read_text(encoding="utf-8"))
    none_ = [r for r in payload["overlap_bias"] if r["overlap_status"] == "none"]
    assert len(none_) > 0
    scores = {r["similarity_index"] for r in none_}
    assert len(scores) > 1


def test_phase11_extent_changes_visible():
    """Phase 10 extent data: 5.12 km differs materially from full reference."""
    payload = json.loads(PHASE10_EXTENT_OUTPUT.read_text(encoding="utf-8"))
    ref = payload["reference_full_datasets"]
    extents = [e for e in payload["extents"] if e.get("comparable")]
    assert len(extents) >= 2
    small = [e for e in extents if e["extent_km"] == 5.12][0]
    assert abs(small["tmsi"] - ref["tmsi"]) > 10.0


def test_phase11_no_body_level_inference():
    """Between-body scores overlap within-body scores; no body indicator."""
    payload = json.loads(PHASE11_OUTPUT.read_text(encoding="utf-8"))
    wb = payload["within_body"]
    bb = payload["between_body"]  # this is a list
    wb_mars_scores = [r["similarity_index"] for r in wb["mars"]]
    wb_moon_scores = [r["similarity_index"] for r in wb["moon"]]
    bb_scores = [r["similarity_index"] for r in bb]
    assert min(bb_scores) <= max(wb_mars_scores)
    assert min(bb_scores) <= max(wb_moon_scores)
    assert max(bb_scores) >= min(wb_mars_scores)
    assert max(bb_scores) >= min(wb_moon_scores)
