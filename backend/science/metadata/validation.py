"""Validation for scientific comparison metadata.

Ensures required fields are present, overlap classifications are consistent
with their ratios, and unavailable information is represented explicitly
rather than fabricated.
"""

from typing import Any

from .schema import ComparisonMetadata, OverlapClassification, SamplingStrategy


class MetadataValidationError(ValueError):
    """Raised when comparison metadata fails validation."""


def validate_metadata(metadata: ComparisonMetadata) -> list[str]:
    """Validate a ComparisonMetadata instance.

    Returns a list of human-readable problem descriptions. An empty list means
    the metadata is valid. Warnings (e.g. missing optional fields) are included
    as descriptions prefixed with "NOTE:"; hard failures are prefixed with
    "ERROR:".
    """
    problems: list[str] = []

    # --- Identification ---
    if not metadata.comparison_id:
        problems.append("ERROR: comparison_id is required")
    if not metadata.experiment_id:
        problems.append("ERROR: experiment_id is required")
    if not metadata.body_a or not metadata.body_b:
        problems.append("ERROR: body_a and body_b are required")
    if metadata.body_a == metadata.body_b:
        problems.append("NOTE: body_a and body_b are the same body (within-body comparison)")
    if not metadata.dataset_id_a or not metadata.dataset_id_b:
        problems.append("ERROR: dataset_id_a and dataset_id_b are required")

    # --- Spatial ---
    if metadata.spatial_extent_km is None or metadata.spatial_extent_km <= 0:
        problems.append("ERROR: spatial_extent_km must be a positive number")
    if metadata.window_a.label == metadata.window_b.label and metadata.body_a == metadata.body_b:
        problems.append(
            "ERROR: identical window labels on the same body may indicate a duplicate window"
        )

    # --- Sampling / overlap consistency ---
    if metadata.sampling.overlap_ratio is not None:
        ratio = metadata.sampling.overlap_ratio
        if not 0.0 <= ratio <= 1.0:
            problems.append("ERROR: overlap_ratio must be between 0 and 1")
        expected = _classify_from_ratio(ratio)
        if metadata.sampling.overlap_classification is not None:
            if metadata.sampling.overlap_classification != expected:
                problems.append(
                    f"ERROR: overlap_classification "
                    f"{metadata.sampling.overlap_classification.value} inconsistent "
                    f"with overlap_ratio {ratio} (expected {expected.value})"
                )
        else:
            problems.append(
                "NOTE: overlap_classification is missing though overlap_ratio is provided"
            )
    else:
        if metadata.sampling.overlap_classification is not None:
            problems.append(
                "NOTE: overlap_classification provided without overlap_ratio"
            )
        if metadata.sampling.overlap_classification == OverlapClassification.UNKNOWN:
            problems.append(
                "NOTE: overlap is unknown; treat cross-window interpretation with caution"
            )

    # --- Strategy ---
    if metadata.sampling.sampling_strategy == SamplingStrategy.UNKNOWN:
        problems.append("NOTE: sampling_strategy is unknown; reproducibility is limited")

    # --- Coverage ---
    for name, value in (
        ("terrain_coverage_percent", metadata.sampling.terrain_coverage_percent),
        ("missing_data_percent", metadata.sampling.missing_data_percent),
        ("window_a.valid_percent", metadata.window_a.valid_percent),
        ("window_b.valid_percent", metadata.window_b.valid_percent),
    ):
        if value is not None and not 0.0 <= value <= 100.0:
            problems.append(f"ERROR: {name} must be between 0 and 100")

    # --- Results ---
    if metadata.similarity_index is not None and not 0.0 <= metadata.similarity_index <= 100.0:
        problems.append("ERROR: similarity_index must be between 0 and 100")
    if metadata.combined_distance is not None and metadata.combined_distance < 0:
        problems.append("ERROR: combined_distance must be non-negative")
    if metadata.confidence is not None:
        allowed = {"HIGH", "MODERATE", "LOW", "INSUFFICIENT"}
        if metadata.confidence not in allowed:
            problems.append(f"ERROR: confidence must be one of {sorted(allowed)}")

    # --- Reproducibility ---
    if metadata.processing_timestamp_utc is None:
        problems.append("NOTE: processing_timestamp_utc is missing")
    if metadata.random_seed is None and metadata.sampling.sampling_strategy in (
        SamplingStrategy.REPEATED, SamplingStrategy.STRATIFIED
    ):
        problems.append(
            "NOTE: random_seed is recommended for repeated or stratified sampling"
        )

    return problems


def _classify_from_ratio(ratio: float) -> OverlapClassification:
    if ratio >= 0.99:
        return OverlapClassification.IDENTICAL
    if ratio >= 0.5:
        return OverlapClassification.HIGH
    if ratio > 0.0:
        return OverlapClassification.PARTIAL
    return OverlapClassification.NONE


def require_complete(metadata: ComparisonMetadata) -> None:
    """Raise MetadataValidationError if any hard errors exist."""
    problems = validate_metadata(metadata)
    errors = [p for p in problems if p.startswith("ERROR:")]
    if errors:
        raise MetadataValidationError("; ".join(errors))
