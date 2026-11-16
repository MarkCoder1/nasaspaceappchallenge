"""Confidence and resolution compatibility rules."""

from dataclasses import dataclass

from science.similarity.features.feature_extraction import TerrainFeatureSet


@dataclass(frozen=True)
class ResolutionCompatibility:
    compatible: bool
    common_analysis_scale_m: float
    resolution_ratio: float
    reason: str


def assess_resolution(target: TerrainFeatureSet, candidate: TerrainFeatureSet, maximum_ratio: float = 4.0) -> ResolutionCompatibility:
    target_scale = target.effective_resolution_m or max(target.resolution_m)
    candidate_scale = candidate.effective_resolution_m or max(candidate.resolution_m)
    ratio = max(target_scale, candidate_scale) / min(target_scale, candidate_scale)
    compatible = ratio <= maximum_ratio
    reason = (
        "Features are compared at their physical neighborhood sizes; no resampling is required."
        if compatible
        else "Native pixel scales differ by more than the configured maximum ratio; comparison is rejected."
    )
    return ResolutionCompatibility(compatible, max(target_scale, candidate_scale), ratio, reason)


def classify_confidence(
    *,
    target_valid_percent: float,
    candidate_valid_percent: float,
    resolution: ResolutionCompatibility,
    feature_count: int,
) -> str:
    if feature_count == 0 or not resolution.compatible or min(target_valid_percent, candidate_valid_percent) < 50:
        return "INSUFFICIENT"
    if min(target_valid_percent, candidate_valid_percent) < 80:
        return "LOW"
    if min(target_valid_percent, candidate_valid_percent) < 95 or resolution.resolution_ratio > 2:
        return "MODERATE"
    return "HIGH"