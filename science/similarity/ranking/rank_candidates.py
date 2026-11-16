"""Guarded ranking boundary for future validated candidate comparisons."""

from typing import Any


def rank_candidates(comparisons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank only already-valid comparison results; reject empty/fabricated inputs."""
    if not comparisons:
        return []
    if any(result.get("similarity_index") is None or result.get("confidence") == "INSUFFICIENT" for result in comparisons):
        raise ValueError("Cannot rank comparisons with invalid or insufficient evidence")
    return sorted(comparisons, key=lambda result: result["similarity_index"], reverse=True)