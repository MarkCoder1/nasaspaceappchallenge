from typing import Any

from pydantic import BaseModel, Field


class SimilarityCompareRequest(BaseModel):
    target_dataset_id: str = Field(min_length=1)
    candidate_dataset_id: str = Field(min_length=1)
    weights: dict[str, float] | None = None


class SimilarityResponse(BaseModel):
    target: dict[str, Any]
    candidate: dict[str, Any]
    similarity_index: float | None
    confidence: str
    features: dict[str, Any]
    strongest_matches: list[str]
    largest_differences: list[str]
    limitations: list[str]
    data_sources: list[dict[str, Any]]
    statistical_uncertainty: dict[str, Any] | None = None
    block_size_sensitivity: dict[str, Any] | None = None


class SimilarityStatusResponse(BaseModel):
    engine: str
    production_comparisons_enabled: bool
    validated_comparisons: list[str]
    available_real_datasets: list[dict[str, Any]]
    unavailable_datasets: list[dict[str, Any]]
    comparison_capabilities: dict[str, dict[str, Any]]