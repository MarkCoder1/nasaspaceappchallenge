"""Weight sensitivity analysis for explainable TMSI results."""

from typing import Any

from science.similarity.features.feature_extraction import TerrainFeatureSet

from .similarity import compare_terrain


def run_weight_sensitivity(
    target: TerrainFeatureSet,
    candidate: TerrainFeatureSet,
    weight_sets: dict[str, dict[str, float]],
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for name, weights in weight_sets.items():
        results[name] = compare_terrain(target, candidate, weights)
    valid_scores = {name: result["similarity_index"] for name, result in results.items() if result["similarity_index"] is not None}
    return {
        "weight_sets": weight_sets,
        "results": results,
        "ranking_stable": len(valid_scores) <= 1 or max(valid_scores.values()) - min(valid_scores.values()) < 5,
        "score_range": (max(valid_scores.values()) - min(valid_scores.values())) if valid_scores else None,
    }