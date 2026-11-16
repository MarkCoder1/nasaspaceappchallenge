"""Phase 11 tests: sampling framework, overlap detection, extent sensitivity,
within-body / between-body comparisons, reproducibility, and Earth gates."""

import json
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.windows import Window

from science.similarity.comparison.uncertainty import assess_resolution, classify_confidence, ResolutionCompatibility
from science.similarity.features.feature_extraction import extract_terrain_features
from science.similarity.scoring.similarity import compare_terrain
from science.validation.phase11_experiments import (
    build_window_specs,
    extract_window,
    non_overlapping_grid,
    overlap_status,
    run_experiments,
    window_overlap_fraction,
    WindowSpec,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MARS_PATH = REPOSITORY_ROOT / "data/processed/mars_jezero_ctx_elevation_m.tif"
MOON_PATH = REPOSITORY_ROOT / "data/processed/moon_lola_80s_20m_elevation_m.tif"
EXPERIMENT_PATH = REPOSITORY_ROOT / "data/metadata/moon_mars_phase7_experiments.json"
PHASE11_OUTPUT = REPOSITORY_ROOT / "data/metadata/phase11_sampling_framework.json"

CELL_M = 20.0
WEIGHTS = {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0}


def _load_features(path, body, source_id, effective_resolution_m=None):
    return extract_terrain_features(
        path, body=body, source_id=source_id, effective_resolution_m=effective_resolution_m
    )


# ---------- Window eligibility and extent ----------

def test_window_eligibility_mars_and_moon():
    specs = build_window_specs(512)  # 10.24 km
    assert len(specs["mars"]) > 0
    assert len(specs["moon"]) > 0
    for s in specs["mars"] + specs["moon"]:
        assert s.n_cells == 512
        assert s.extent_km == 10.24
        assert s.width_cells == 512 and s.height_cells == 512


def test_physical_extent_calculation():
    assert round(512 * CELL_M / 1000, 2) == 10.24
    assert round(1024 * CELL_M / 1000, 2) == 20.48
    assert round(256 * CELL_M / 1000, 2) == 5.12


def test_non_overlapping_grid_covers_without_overlap():
    offsets = non_overlapping_grid(2048, 2048, 512)
    assert len(offsets) == 16  # 4x4 grid
    seen = set()
    for co, ro in offsets:
        key = (co, ro)
        assert key not in seen, f"overlapping grid offset {key}"
        seen.add(key)
        assert co + 512 <= 2048
        assert ro + 512 <= 2048


# ---------- Overlap detection ----------

def test_overlap_fraction_identical_is_one():
    a = WindowSpec("a", "Moon", "a", 0, 0, 512, 512, 512, 10.24)
    b = WindowSpec("b", "Moon", "b", 0, 0, 512, 512, 512, 10.24)
    assert window_overlap_fraction(a, b) == 1.0
    assert overlap_status(window_overlap_fraction(a, b)) == "identical"


def test_overlap_fraction_none_is_zero():
    a = WindowSpec("a", "Moon", "a", 0, 0, 512, 512, 512, 10.24)
    b = WindowSpec("b", "Moon", "b", 512, 0, 512, 512, 512, 10.24)  # adjacent, no overlap
    assert window_overlap_fraction(a, b) == 0.0
    assert overlap_status(window_overlap_fraction(a, b)) == "none"


def test_overlap_fraction_partial():
    a = WindowSpec("a", "Moon", "a", 0, 0, 512, 512, 512, 10.24)
    b = WindowSpec("b", "Moon", "b", 256, 0, 512, 512, 512, 10.24)  # half overlap
    frac = window_overlap_fraction(a, b)
    assert abs(frac - 0.5) < 1e-9
    assert overlap_status(frac) == "high"


# ---------- Reproducibility / deterministic ----------

def test_within_body_comparison_is_reproducible(tmp_path):
    specs = build_window_specs(512)
    sa, sb = specs["mars"][0], specs["mars"][1]
    pa = tmp_path / f"{sa.source_id}.tif"; pb = tmp_path / f"{sb.source_id}.tif"
    extract_window(MARS_PATH, sa, pa)
    extract_window(MARS_PATH, sb, pb)
    r1 = compare_terrain(
        extract_terrain_features(pa, body="Mars", source_id=sa.source_id, effective_resolution_m=20.0),
        extract_terrain_features(pb, body="Mars", source_id=sb.source_id, effective_resolution_m=20.0),
        weights=WEIGHTS, include_uncertainty=False,
    )
    r2 = compare_terrain(
        extract_terrain_features(pa, body="Mars", source_id=sa.source_id, effective_resolution_m=20.0),
        extract_terrain_features(pb, body="Mars", source_id=sb.source_id, effective_resolution_m=20.0),
        weights=WEIGHTS, include_uncertainty=False,
    )
    assert r1["similarity_index"] == r2["similarity_index"]
    assert r1["combined_distance"] == r2["combined_distance"]


# ---------- Within-body variability quantified ----------

def test_within_body_mars_range_is_material(mars_full, moon_full):
    specs = build_window_specs(512)
    mars_specs = specs["mars"]
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        scores = []
        for i in range(len(mars_specs)):
            for j in range(i + 1, len(mars_specs)):
                sa, sb = mars_specs[i], mars_specs[j]
                pa = td / f"{sa.source_id}.tif"; pb = td / f"{sb.source_id}.tif"
                extract_window(MARS_PATH, sa, pa)
                extract_window(MARS_PATH, sb, pb)
                res = compare_terrain(
                    extract_terrain_features(pa, body="Mars", source_id=sa.source_id, effective_resolution_m=20.0),
                    extract_terrain_features(pb, body="Mars", source_id=sb.source_id, effective_resolution_m=20.0),
                    weights=WEIGHTS, include_uncertainty=False,
                )
                scores.append(res["similarity_index"])
    assert len(scores) == 15
    assert max(scores) - min(scores) > 10.0, "Within-body Mars variability should be material"


# ---------- Between-body overlaps within-body ----------

def test_between_body_overlaps_within_body(mars_full, moon_full):
    # Between-body min is below within-body Moon min; ranges overlap substantially.
    specs = build_window_specs(512)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        mars_paths = []
        for i, s in enumerate(specs["mars"]):
            p = td / f"{s.source_id}.tif"
            extract_window(MARS_PATH, s, p)
            mars_paths.append((s, p))
        moon_paths = []
        for i, s in enumerate(specs["moon"]):
            p = td / f"{s.source_id}.tif"
            extract_window(MOON_PATH, s, p)
            moon_paths.append((s, p))
        between = []
        for sa, pa in mars_paths:
            for sb, pb in moon_paths:
                res = compare_terrain(
                    extract_terrain_features(pa, body="Mars", source_id=sa.source_id, effective_resolution_m=20.0),
                    extract_terrain_features(pb, body="Moon", source_id=sb.source_id, effective_resolution_m=16.055973052978516),
                    weights=WEIGHTS, include_uncertainty=False,
                )
                between.append(res["similarity_index"])
    assert len(between) == 96
    assert min(between) < 30.0, "Some between-body scores should be very low"
    assert max(between) > 70.0, "Some between-body scores should be high"
    # Between-body range overlaps within-body range: min between <= max within-body moon.
    assert min(between) <= 94.10067849332381


# ---------- Overlap bias: identical windows give 100 ----------

def test_identical_windows_tmsi_is_100(tmp_path):
    spec = WindowSpec("ctrl", "Moon", "ctrl", 512, 512, 512, 512, 512, 10.24)
    pa = tmp_path / "ctrl_a.tif"; pb = tmp_path / "ctrl_b.tif"
    extract_window(MOON_PATH, spec, pa)
    spec_b = WindowSpec("ctrl_b", "Moon", "ctrl_b", 512, 512, 512, 512, 512, 10.24)
    extract_window(MOON_PATH, spec_b, pb)
    res = compare_terrain(
        extract_terrain_features(pa, body="Moon", source_id="ctrl", effective_resolution_m=16.055973052978516),
        extract_terrain_features(pb, body="Moon", source_id="ctrl_b", effective_resolution_m=16.055973052978516),
        weights=WEIGHTS, include_uncertainty=False,
    )
    assert abs(res["similarity_index"] - 100.0) < 1e-6
    assert abs(res["combined_distance"]) < 1e-6


# ---------- Resolution gate ----------

def test_resolution_gate_admits_official_pair(mars_full, moon_full):
    resolution = assess_resolution(mars_full, moon_full)
    assert resolution.compatible is True
    assert resolution.resolution_ratio < 4.0


# ---------- Baseline reproduction ----------

def test_moon_mars_baseline_reproduced(mars_full, moon_full):
    result = compare_terrain(mars_full, moon_full, weights=WEIGHTS, include_uncertainty=False)
    assert abs(result["similarity_index"] - 49.92285382858792) < 1e-9
    assert result["confidence"] == "HIGH"


# ---------- Phase 11 experiment output provenance ----------

def test_phase11_output_exists_and_has_structure():
    assert PHASE11_OUTPUT.is_file(), "phase11_sampling_framework.json must exist"
    payload = json.loads(PHASE11_OUTPUT.read_text(encoding="utf-8"))
    assert payload["experiment"] == "phase11_sampling_framework"
    assert payload["n_cells"] == 512
    assert payload["mars_window_count"] == 6
    assert payload["moon_window_count"] == 16
    assert "within_body" in payload
    assert "between_body" in payload
    assert "overlap_bias" in payload
    assert "summary" in payload


def test_phase11_within_body_counts():
    payload = json.loads(PHASE11_OUTPUT.read_text(encoding="utf-8"))
    assert len(payload["within_body"]["mars"]) == 15  # C(6,2)
    assert len(payload["within_body"]["moon"]) == 120  # C(16,2)


def test_phase11_between_body_count():
    payload = json.loads(PHASE11_OUTPUT.read_text(encoding="utf-8"))
    assert len(payload["between_body"]) == 96  # 6 x 16


# ---------- Earth remains PENDING / gates ----------

def test_earth_remains_pending():
    from backend.app.services.similarity import similarity_status, UNAVAILABLE_DATASETS, DATASET_REGISTRY
    status = similarity_status()
    assert status["production_comparisons_enabled"] is False
    assert status["validated_comparisons"] == ["moon_mars"]
    assert "earth_nasadem_hgt_v001" not in DATASET_REGISTRY
    earth = [d for d in UNAVAILABLE_DATASETS if d["id"] == "earth_nasadem_hgt_v001"]
    assert len(earth) == 1
    assert earth[0]["body"] == "Earth"


# ---------- Fixtures ----------

@pytest.fixture
def mars_full():
    return _load_features(MARS_PATH, "Mars", "mars_jezero_ctx_dtm", effective_resolution_m=20.0)


@pytest.fixture
def moon_full():
    return _load_features(
        MOON_PATH, "Moon", "moon_lola", effective_resolution_m=16.055973052978516
    )
