"""Terrain Morphology Similarity Index (TMSI) scoring."""

import math
from typing import Any, Optional

from science.similarity.comparison.distribution import compare_available_features
from science.similarity.comparison.extent import diagnose_extent_sensitivity
from science.similarity.comparison.overlap import diagnose_overlap
from science.similarity.comparison.uncertainty import assess_resolution, classify_confidence
from science.similarity.features.feature_extraction import TerrainFeatureSet
from science.metadata.schema import WindowInfo

from .weights import validate_weights


def compare_terrain(
    target: TerrainFeatureSet,
    candidate: TerrainFeatureSet,
    weights: dict[str, float] | None = None,
    include_uncertainty: bool = False,
    window_a: Optional[WindowInfo] = None,
    window_b: Optional[WindowInfo] = None,
    spatial_extent_km: Optional[float] = None,
) -> dict[str, Any]:
    resolution = assess_resolution(target, candidate)
    if not resolution.compatible:
        return {
            "target": {"id": target.source_id, "body": target.body},
            "candidate": {"id": candidate.source_id, "body": candidate.body},
            "similarity_index": None,
            "confidence": "INSUFFICIENT",
            "features": {},
            "strongest_matches": [],
            "largest_differences": [],
            "limitations": [resolution.reason],
            "data_sources": [target.source_metadata, candidate.source_metadata],
        }
    feature_comparisons = compare_available_features(target, candidate)
    chosen_weights = validate_weights(weights)
    usable = [(name, comparison) for name, comparison in feature_comparisons.items() if chosen_weights.get(name, 0) > 0]
    if not usable:
        raise ValueError("No shared features have positive weights")
    weighted_distance = sum(chosen_weights[name] * comparison["distance"]["normalized_distance"] for name, comparison in usable)
    weight_total = sum(chosen_weights[name] for name, _ in usable)
    combined_distance = weighted_distance / weight_total
    similarity_index = 100.0 * math.exp(-combined_distance)
    confidence = classify_confidence(
        target_valid_percent=target.valid_percent,
        candidate_valid_percent=candidate.valid_percent,
        resolution=resolution,
        feature_count=len(usable),
    )
    ordered = sorted(((name, comparison["distance"]["normalized_distance"]) for name, comparison in usable), key=lambda item: item[1])
    strongest = [name for name, _ in ordered[:2]]
    largest = [name for name, _ in ordered[-2:][::-1]]
    limitations = [
        "TMSI is a terrain-morphology index, not a probability, habitability score, or safety certification.",
        f"Features are interpreted at a common physical scale of {resolution.common_analysis_scale_m:g} m; no raster upsampling was performed.",
        "Earth and planetary environmental conditions remain physically different even when morphology distributions are similar.",
    ]
    if target.body == "Earth" or candidate.body == "Earth":
        limitations.append(
            "Earth DEM source data has approximately 29.3 m native resolution and was resampled "
            "to a 20 m processing grid; the resampling does not create additional observational detail. "
            "Effective measurement resolution remains constrained by the ~29.3 m source data."
        )
        limitations.append(
            "Vertical datum difference: Earth uses NAVD88; Moon uses LOLA project datum; Mars uses "
            "delta geoid (MOLA control). Vertical datum differences are unquantified and may affect "
            "elevation-based feature comparisons (slope, local relief, terrain ruggedness)."
        )
        limitations.append(
            "Earth coverage is limited to two USGS 3DEP tiles (Death Valley / southern Arizona region, "
            "approximately 35°N–37°N, 116°W–117°W). These samples cannot establish global terrestrial "
            "terrain representativeness; results apply only to the sampled regions."
        )
    result = {
        "target": {"id": target.source_id, "body": target.body, "resolution_m": target.resolution_m},
        "candidate": {"id": candidate.source_id, "body": candidate.body, "resolution_m": candidate.resolution_m},
        "similarity_index": similarity_index,
        "confidence": confidence,
        "combined_distance": combined_distance,
        "weights": {name: chosen_weights[name] for name, _ in usable},
        "features": feature_comparisons,
        "strongest_matches": strongest,
        "largest_differences": largest,
        "limitations": limitations,
        "data_sources": [target.source_metadata, candidate.source_metadata],
    }
    if include_uncertainty:
        from science.similarity.comparison.bootstrap import block_size_sensitivity, bootstrap_tmsi

        result["statistical_uncertainty"] = bootstrap_tmsi(target, candidate, result["weights"])
        result["block_size_sensitivity"] = block_size_sensitivity(target, candidate, result["weights"])

    # --- Comparison diagnostics (additive; only present when window info given) ---
    diagnostics: dict[str, Any] = {}
    if window_a is not None and window_b is not None:
        overlap = diagnose_overlap(window_a, window_b)
        diagnostics["overlap"] = {
            "overlap_ratio": overlap.overlap_ratio,
            "classification": overlap.classification.value,
            "comparable": overlap.comparable,
            "reason": overlap.reason,
        }
    if spatial_extent_km is not None:
        # Reference extent is informational only when not supplied externally;
        # the diagnostic still records the extent used.
        extent = diagnose_extent_sensitivity(float(spatial_extent_km), None)
        diagnostics["extent"] = {
            "extent_km": extent.extent_km,
            "reference_extent_km": extent.reference_extent_km,
            "extent_delta_km": extent.extent_delta_km,
            "extent_ratio": extent.extent_ratio,
            "sensitivity_flag": extent.sensitivity_flag,
            "reason": extent.reason,
        }
    if diagnostics:
        result["comparison_diagnostics"] = diagnostics
    return result