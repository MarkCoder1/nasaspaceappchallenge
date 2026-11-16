"""Feature-by-feature distribution comparison."""

from typing import Any

from science.similarity.features.feature_extraction import FeatureLayer, TerrainFeatureSet, summarize

from .distance import compare_distributions


def compare_feature_layers(target: FeatureLayer, candidate: FeatureLayer) -> dict[str, Any]:
    if target.units != candidate.units:
        raise ValueError(f"Unit mismatch for {target.name}: {target.units} vs {candidate.units}")
    distance = compare_distributions(target.values, candidate.values)
    return {
        "units": target.units,
        "target_summary": summarize(target.values),
        "candidate_summary": summarize(candidate.values),
        "distance": {
            "wasserstein": distance.wasserstein,
            "ks_statistic": distance.ks_statistic,
            "ks_pvalue": distance.ks_pvalue,
            "pooled_iqr": distance.pooled_iqr,
            "normalized_distance": distance.normalized_distance,
            "sample_count_target": distance.sample_count_target,
            "sample_count_candidate": distance.sample_count_candidate,
        },
        "neighborhood_m": target.neighborhood_m,
        "definition": target.definition,
    }


def compare_available_features(target: TerrainFeatureSet, candidate: TerrainFeatureSet) -> dict[str, dict[str, Any]]:
    shared = sorted(set(target.features).intersection(candidate.features))
    if not shared:
        raise ValueError("No shared feature names are available for comparison")
    return {name: compare_feature_layers(target.features[name], candidate.features[name]) for name in shared}