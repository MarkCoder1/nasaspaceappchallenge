"""Phase 20.6: Scientific corrections and final validation tests.

Tests cover:
- Bootstrap repetition configuration (>= 1,000)
- Confidence interval reproducibility
- Multiple-seed sensitivity analysis
- Native versus processing resolution labels
- Earth geographic coverage disclosures
- Vertical datum limitation metadata
- TMSI numerical consistency
- Existing candidate eligibility rules
- Scientific metadata completeness

Do not weaken, delete, or silently skip existing tests.
"""

import sys
import json
import warnings
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

warnings.filterwarnings("ignore")

from science.similarity.comparison.bootstrap import bootstrap_tmsi, seed_sensitivity
from science.similarity.features.feature_extraction import extract_terrain_features
from science.similarity.scoring.similarity import compare_terrain
from science.datasets.registry import candidate_eligible_for_evaluation


# --- Paths ---
MOON_PATH = Path(
    "/Users/markadam/Desktop/NASA SPACE APP CHALLENGE/nasaspaceapp/backend/"
    "data/processed/moon_lola_80s_20m_elevation_m.tif"
)
MARS_PATH = Path(
    "/Users/markadam/Desktop/NASA SPACE APP CHALLENGE/nasaspaceapp/backend/"
    "data/processed/mars_jezero_ctx_elevation_m.tif"
)
EARTH_36_PATH = Path(
    "/Users/markadam/Desktop/NASA SPACE APP CHALLENGE/nasaspaceapp/"
    "data/processed/USGS_1_n36w117_20m_utm11n.tif"
)


# --- Fixtures ---

@pytest.fixture
def moon_features():
    return extract_terrain_features(MOON_PATH, body="Moon", source_id="moon_lola")


@pytest.fixture
def mars_features():
    return extract_terrain_features(MARS_PATH, body="Mars", source_id="mars_jezero_ctx_dtm")


@pytest.fixture
def earth_features():
    return extract_terrain_features(EARTH_36_PATH, body="Earth", source_id="usgs_3dep_n36w117")


# --- Bootstrap repetition configuration tests ---

def test_bootstrap_repetitions_at_least_1000(moon_features, mars_features):
    """Bootstrap must use at least 1,000 repetitions for stable CI estimation."""
    result = bootstrap_tmsi(
        mars_features,
        moon_features,
        {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0},
        block_size_m=320.0,
        repetitions=1000,
        seed=42,
    )
    assert result["repetitions"] >= 1000, f"Expected >= 1000 repetitions, got {result['repetitions']}"


def test_bootstrap_repetitions_recorded(moon_features, mars_features):
    """The repetitions count must be explicitly recorded in the result."""
    result = bootstrap_tmsi(
        mars_features,
        moon_features,
        {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0},
        block_size_m=320.0,
        repetitions=1000,
        seed=42,
    )
    assert "repetitions" in result
    assert result["repetitions"] == 1000


def test_bootstrap_seed_recorded(moon_features, mars_features):
    """The random seed must be explicitly recorded for reproducibility."""
    result = bootstrap_tmsi(
        mars_features,
        moon_features,
        {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0},
        block_size_m=320.0,
        repetitions=1000,
        seed=42,
    )
    assert "seed" in result
    assert result["seed"] == 42


# --- Confidence interval reproducibility tests ---

def test_confidence_interval_reproducible(moon_features, mars_features):
    """Identical inputs and seed must produce identical confidence intervals."""
    result1 = bootstrap_tmsi(
        mars_features,
        moon_features,
        {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0},
        block_size_m=320.0,
        repetitions=1000,
        seed=42,
    )
    result2 = bootstrap_tmsi(
        mars_features,
        moon_features,
        {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0},
        block_size_m=320.0,
        repetitions=1000,
        seed=42,
    )
    assert abs(result1["tmsi_lower_95"] - result2["tmsi_lower_95"]) < 1e-10
    assert abs(result1["tmsi_upper_95"] - result2["tmsi_upper_95"]) < 1e-10
    assert abs(result1["tmsi_mean"] - result2["tmsi_mean"]) < 1e-10


def test_confidence_interval_bounds_valid(moon_features, mars_features):
    """CI lower must be <= TMSI mean <= CI upper."""
    result = bootstrap_tmsi(
        mars_features,
        moon_features,
        {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0},
        block_size_m=320.0,
        repetitions=1000,
        seed=42,
    )
    assert result["tmsi_lower_95"] <= result["tmsi_mean"] <= result["tmsi_upper_95"]


def test_confidence_level_recorded(moon_features, mars_features):
    """The confidence level (95%) must be implicit in the percentile keys."""
    result = bootstrap_tmsi(
        mars_features,
        moon_features,
        {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0},
        block_size_m=320.0,
        repetitions=1000,
        seed=42,
    )
    assert "tmsi_lower_95" in result
    assert "tmsi_upper_95" in result


# --- Seed sensitivity analysis tests ---

def test_seed_sensitivity_uses_five_seeds(moon_features, mars_features):
    """Seed sensitivity must use at least five distinct seeds."""
    result = seed_sensitivity(
        mars_features,
        moon_features,
        {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0},
        block_size_m=320.0,
        repetitions=1000,
        seeds=[42, 123, 456, 789, 1011],
    )
    assert len(result["seeds"]) >= 5
    assert len(result["per_seed_results"]) >= 5


def test_seed_sensitivity_reports_aggregate_stats(moon_features, mars_features):
    """Seed sensitivity must report aggregate statistics across seeds."""
    result = seed_sensitivity(
        mars_features,
        moon_features,
        {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0},
        block_size_m=320.0,
        repetitions=1000,
        seeds=[42, 123, 456, 789, 1011],
    )
    agg = result["aggregate"]
    assert "mean_tmsi_across_seeds" in agg
    assert "min_tmsi_across_seeds" in agg
    assert "max_tmsi_across_seeds" in agg
    assert "max_abs_tmsi_diff_across_seeds" in agg


def test_seed_sensitivity_stability(moon_features, mars_features):
    """TMSI estimates across seeds should be stable (max diff < 2.0)."""
    result = seed_sensitivity(
        mars_features,
        moon_features,
        {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0},
        block_size_m=320.0,
        repetitions=1000,
        seeds=[42, 123, 456, 789, 1011],
    )
    agg = result["aggregate"]
    assert agg["max_abs_tmsi_diff_across_seeds"] < 2.0, (
        f"TMSI varies too much across seeds: {agg['max_abs_tmsi_diff_across_seeds']:.4f}"
    )


# --- Native versus processing resolution tests ---

def test_earth_native_resolution_disclosed():
    """Earth DEM native resolution must be distinguished from processing grid."""
    processing_meta_path = Path(
        "/Users/markadam/Desktop/NASA SPACE APP CHALLENGE/nasaspaceapp/backend/"
        "data/processed/phase20_earth_processing_metadata.json"
    )
    assert processing_meta_path.exists(), "Earth processing metadata file missing"
    with open(processing_meta_path) as f:
        meta = json.load(f)
    assert "source_resolution_m" in meta["results"][0]
    assert "target_resolution_m" in meta["results"][0]
    # Native resolution (~29.3 m) differs from processing grid (20 m)
    assert abs(meta["results"][0]["source_resolution_m"] - 0.00027778) < 1e-6  # degrees
    assert meta["results"][0]["target_resolution_m"] == 20.0


def test_earth_resampling_does_not_increase_resolution():
    """Processing metadata must state that resampling does not increase resolution."""
    processing_meta_path = Path(
        "/Users/markadam/Desktop/NASA SPACE APP CHALLENGE/nasaspaceapp/backend/"
        "data/processed/phase20_earth_processing_metadata.json"
    )
    with open(processing_meta_path) as f:
        meta = json.load(f)
    for result in meta["results"]:
        assert "effective resolution remains" in result["important_note"].lower() or \
            "does not increase" in result["important_note"].lower(), \
            f"Missing resolution disclosure in: {result['important_note']}"


# --- Earth geographic coverage disclosure tests ---

def test_earth_coverage_disclosed_in_metadata():
    """Earth coverage limitation must be documented in processing metadata."""
    processing_meta_path = Path(
        "/Users/markadam/Desktop/NASA SPACE APP CHALLENGE/nasaspaceapp/backend/"
        "data/processed/phase20_earth_processing_metadata.json"
    )
    with open(processing_meta_path) as f:
        meta = json.load(f)
    limitations = meta.get("important_limitations", [])
    coverage_found = any(
        "coverage" in lim.lower() and ("us" in lim.lower() or "united states" in lim.lower())
        for lim in limitations
    )
    assert coverage_found, "Earth geographic coverage limitation not documented"


def test_earth_coverage_in_comparison_limitations(moon_features, earth_features):
    """Earth comparison limitations must mention limited geographic coverage."""
    result = compare_terrain(
        moon_features,
        earth_features,
        include_uncertainty=True,
        spatial_extent_km=10.24,
    )
    limitations = result.get("limitations", [])
    coverage_found = any(
        "coverage" in lim.lower() and ("us" in lim.lower() or "united states" in lim.lower() or "arizona" in lim.lower())
        for lim in limitations
    )
    assert coverage_found, f"Earth coverage not disclosed in limitations: {limitations}"


# --- Vertical datum limitation tests ---

def test_vertical_datum_disclosed_in_processing_metadata():
    """Vertical datum difference must be documented in processing metadata."""
    processing_meta_path = Path(
        "/Users/markadam/Desktop/NASA SPACE APP CHALLENGE/nasaspaceapp/backend/"
        "data/processed/phase20_earth_processing_metadata.json"
    )
    with open(processing_meta_path) as f:
        meta = json.load(f)
    limitations = meta.get("important_limitations", [])
    datum_found = any(
        "vertical datum" in lim.lower() or "navd88" in lim.lower()
        for lim in limitations
    )
    assert datum_found, "Vertical datum limitation not documented in processing metadata"


def test_vertical_datum_in_comparison_limitations(moon_features, earth_features):
    """Earth comparison limitations must mention vertical datum difference."""
    result = compare_terrain(
        moon_features,
        earth_features,
        include_uncertainty=True,
        spatial_extent_km=10.24,
    )
    limitations = result.get("limitations", [])
    datum_found = any(
        "vertical datum" in lim.lower() or "navd88" in lim.lower()
        for lim in limitations
    )
    assert datum_found, f"Vertical datum not disclosed in limitations: {limitations}"


# --- TMSI numerical consistency tests ---

def test_tmsi_numerical_consistency(moon_features, mars_features):
    """TMSI must be reproducible with identical inputs."""
    result1 = compare_terrain(mars_features, moon_features, include_uncertainty=True, spatial_extent_km=10.24)
    result2 = compare_terrain(mars_features, moon_features, include_uncertainty=True, spatial_extent_km=10.24)
    assert abs(result1["similarity_index"] - result2["similarity_index"]) < 1e-10


def test_tmsi_in_valid_range(moon_features, mars_features):
    """TMSI must be between 0 and 100."""
    result = compare_terrain(mars_features, moon_features, include_uncertainty=True, spatial_extent_km=10.24)
    assert 0.0 <= result["similarity_index"] <= 100.0


# --- Candidate eligibility rule tests ---

def test_candidate_eligibility_preserved():
    """Phase 19 eligibility rules must remain intact."""
    # A candidate with status CANDIDATE must not be eligible
    assert candidate_eligible_for_evaluation("atacama_desert") is False
    # Non-existent candidate must not be eligible
    assert candidate_eligible_for_evaluation("nonexistent_candidate") is False


# --- Scientific metadata completeness tests ---

def test_scientific_metadata_complete(moon_features, mars_features):
    """Comparison result must contain all required metadata fields."""
    result = compare_terrain(mars_features, moon_features, include_uncertainty=True, spatial_extent_km=10.24)
    required_top_level = [
        "similarity_index", "confidence", "combined_distance", "weights",
        "features", "limitations", "data_sources",
    ]
    for field in required_top_level:
        assert field in result, f"Missing top-level field: {field}"
    assert "statistical_uncertainty" in result
    su = result["statistical_uncertainty"]
    for field in ["tmsi_lower_95", "tmsi_upper_95", "tmsi_mean", "repetitions", "seed"]:
        assert field in su, f"Missing uncertainty field: {field}"
