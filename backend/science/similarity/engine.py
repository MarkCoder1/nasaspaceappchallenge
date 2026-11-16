"""Reusable raster-to-raster comparison interface."""

from pathlib import Path
from typing import Any

from .features.feature_extraction import extract_terrain_features
from .scoring.similarity import compare_terrain


def compare_rasters(
    target_path: Path,
    target_body: str,
    target_id: str,
    candidate_path: Path,
    candidate_body: str,
    candidate_id: str,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Extract features and compare two validated planetary terrain rasters."""
    target = extract_terrain_features(target_path, body=target_body, source_id=target_id)
    candidate = extract_terrain_features(candidate_path, body=candidate_body, source_id=candidate_id)
    return compare_terrain(target, candidate, weights)