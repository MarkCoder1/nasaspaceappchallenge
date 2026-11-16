"""Serialization helpers for scientific comparison metadata.

Builds :class:`~science.metadata.schema.ComparisonMetadata` objects from
engine outputs and window specifications, and merges metadata into export
packages without fabricating unavailable information.
"""

from typing import Any

from science.similarity.features.feature_extraction import TerrainFeatureSet

from .schema import (
    ComparisonMetadata,
    FeatureComparison,
    OverlapClassification,
    SamplingInfo,
    SamplingStrategy,
    WindowInfo,
    make_comparison_id,
    now_utc,
)
from .validation import MetadataValidationError, require_complete, validate_metadata


def window_info_from_feature_set(
    feature_set: TerrainFeatureSet,
    *,
    label: str,
    col_off: int,
    row_off: int,
    n_cells: int,
    extent_km: float,
    valid_percent: float | None = None,
) -> WindowInfo:
    """Construct a :class:`WindowInfo` from a :class:`TerrainFeatureSet`."""
    metadata = feature_set.source_metadata or {}
    resolution = metadata.get("resolution_m")
    res_m: float | None = None
    if isinstance(resolution, list) and len(resolution) == 2:
        res_m = float(resolution[0])
    elif isinstance(resolution, (int, float)):
        res_m = float(resolution)

    return WindowInfo(
        label=label,
        body=feature_set.body,
        source_id=feature_set.source_id,
        col_off=int(col_off),
        row_off=int(row_off),
        width_cells=int(n_cells),
        height_cells=int(n_cells),
        extent_km=float(extent_km),
        crs=metadata.get("crs_wkt"),
        resolution_m=res_m,
        effective_resolution_m=feature_set.effective_resolution_m,
        valid_percent=(
            float(valid_percent) if valid_percent is not None
            else float(metadata.get("source_valid_percent")) if metadata.get("source_valid_percent") is not None
            else None
        ),
    )


def sampling_info_from_overlap(
    *,
    overlap_ratio: float | None,
    overlap_classification: OverlapClassification | None = None,
    strategy: SamplingStrategy = SamplingStrategy.UNKNOWN,
    selection_method: str | None = None,
    terrain_coverage_percent: float | None = None,
    missing_data_percent: float | None = None,
) -> SamplingInfo:
    """Construct a :class:`SamplingInfo` with validated overlap classification."""
    if overlap_classification is None and overlap_ratio is not None:
        if overlap_ratio >= 0.99:
            overlap_classification = OverlapClassification.IDENTICAL
        elif overlap_ratio >= 0.5:
            overlap_classification = OverlapClassification.HIGH
        elif overlap_ratio > 0.0:
            overlap_classification = OverlapClassification.PARTIAL
        else:
            overlap_classification = OverlapClassification.NONE

    return SamplingInfo(
        overlap_ratio=overlap_ratio,
        overlap_classification=overlap_classification,
        sampling_strategy=strategy,
        window_selection_method=selection_method,
        terrain_coverage_percent=terrain_coverage_percent,
        missing_data_percent=missing_data_percent,
    )


def feature_comparison_from_engine(
    feature_id: str,
    comparison: dict[str, Any],
) -> FeatureComparison:
    """Build a :class:`FeatureComparison` from an engine feature-comparison dict."""
    distance = comparison.get("distance", {}) or {}
    return FeatureComparison(
        feature_id=feature_id,
        units=comparison.get("units", ""),
        wasserstein=distance.get("wasserstein"),
        ks_statistic=distance.get("ks_statistic"),
        pooled_iqr=distance.get("pooled_iqr"),
        normalized_distance=distance.get("normalized_distance"),
        sample_count_target=distance.get("sample_count_target"),
        sample_count_candidate=distance.get("sample_count_candidate"),
    )


def build_comparison_metadata(
    *,
    experiment_id: str,
    body_a: str,
    body_b: str,
    dataset_id_a: str,
    dataset_id_b: str,
    window_a: WindowInfo,
    window_b: WindowInfo,
    spatial_extent_km: float,
    sampling: SamplingInfo,
    similarity_index: float | None = None,
    combined_distance: float | None = None,
    confidence: str | None = None,
    feature_comparisons: list[FeatureComparison] | None = None,
    weights: dict[str, float] | None = None,
    statistical_diagnostics: dict[str, Any] | None = None,
    algorithm_version: str | None = None,
    dataset_version_a: str | None = None,
    dataset_version_b: str | None = None,
    configuration: dict[str, Any] | None = None,
    random_seed: int | None = None,
) -> ComparisonMetadata:
    """Assemble and validate a full :class:`ComparisonMetadata`."""
    comparison_id = make_comparison_id(
        body_a, body_b, dataset_id_a, dataset_id_b,
        spatial_extent_km, window_a, window_b,
    )
    metadata = ComparisonMetadata(
        comparison_id=comparison_id,
        experiment_id=experiment_id,
        body_a=body_a,
        body_b=body_b,
        dataset_id_a=dataset_id_a,
        dataset_id_b=dataset_id_b,
        window_a=window_a,
        window_b=window_b,
        spatial_extent_km=float(spatial_extent_km),
        sampling=sampling,
        similarity_index=similarity_index,
        combined_distance=combined_distance,
        confidence=confidence,
        feature_comparisons=feature_comparisons or [],
        weights=weights or {},
        statistical_diagnostics=statistical_diagnostics or {},
        algorithm_version=algorithm_version,
        dataset_version_a=dataset_version_a,
        dataset_version_b=dataset_version_b,
        processing_timestamp_utc=now_utc(),
        configuration=configuration or {},
        random_seed=random_seed,
    )
    require_complete(metadata)
    return metadata


def merge_metadata_into_export(
    package: dict[str, Any],
    metadata: ComparisonMetadata,
) -> dict[str, Any]:
    """Add a ``comparison_metadata`` block to an export package without
    altering existing keys."""
    package = dict(package)
    package["comparison_metadata"] = metadata.to_dict()
    return package


def validate_export_metadata(package: dict[str, Any]) -> list[str]:
    """Validate the comparison_metadata block of an export package."""
    metadata_dict = package.get("comparison_metadata")
    if metadata_dict is None:
        return ["ERROR: comparison_metadata is missing from export package"]
    try:
        metadata = ComparisonMetadata.from_dict(metadata_dict)
    except Exception as exc:  # pydantic ValidationError
        return [f"ERROR: comparison_metadata is invalid: {exc}"]
    return validate_metadata(metadata)
