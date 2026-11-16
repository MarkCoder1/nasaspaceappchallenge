"""Standardized scientific metadata schema for every TMSI comparison.

Defines Pydantic models that capture comparison identification, spatial
information, sampling information, scientific results, and reproducibility
fields. All fields are optional where information may be unavailable;
unavailable information is represented explicitly as ``None`` rather than
fabricated.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class OverlapClassification(str, Enum):
    IDENTICAL = "identical"
    HIGH = "high"
    PARTIAL = "partial"
    NONE = "none"
    UNKNOWN = "unknown"


class SamplingStrategy(str, Enum):
    SINGLE_WINDOW = "single_fixed_area_window"
    MULTIPLE_WINDOWS = "multiple_non_overlapping_windows"
    STRATIFIED = "stratified_terrain_sampling"
    REPEATED = "repeated_spatial_sampling"
    AGGREGATION = "aggregation_across_window_comparisons"
    UNKNOWN = "unknown"


class WindowInfo(BaseModel):
    """Spatial description of a single terrain window."""

    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., description="Human-readable window label.")
    body: str = Field(..., description="Planetary body (e.g. 'Mars', 'Moon').")
    source_id: str = Field(..., description="Dataset identifier for this window.")
    col_off: int = Field(..., ge=0, description="Window column offset in source raster cells.")
    row_off: int = Field(..., ge=0, description="Window row offset in source raster cells.")
    width_cells: int = Field(..., gt=0, description="Window width in cells.")
    height_cells: int = Field(..., gt=0, description="Window height in cells.")
    extent_km: float = Field(..., gt=0, description="Physical extent of the window in kilometres.")
    crs: Optional[str] = Field(
        None, description="Coordinate reference system identifier (WKT or authority string)."
    )
    resolution_m: Optional[float] = Field(
        None, gt=0, description="Nominal pixel spacing in metres, if known."
    )
    effective_resolution_m: Optional[float] = Field(
        None, gt=0, description="Effective spatial resolution in metres, if known."
    )
    valid_percent: Optional[float] = Field(
        None, ge=0, le=100, description="Percentage of valid (non-nodata) pixels in the window."
    )


class SamplingInfo(BaseModel):
    """Sampling design and overlap information for a comparison."""

    model_config = ConfigDict(extra="forbid")

    overlap_ratio: Optional[float] = Field(
        None, ge=0, le=1, description="Fraction of the smaller window overlapped by the larger."
    )
    overlap_classification: Optional[OverlapClassification] = Field(
        None, description="Classified overlap relationship between the two windows."
    )
    sampling_strategy: SamplingStrategy = Field(
        SamplingStrategy.UNKNOWN, description="Sampling design used to select the windows."
    )
    window_selection_method: Optional[str] = Field(
        None, description="How the windows were chosen (e.g. 'centered grid', 'random')."
    )
    terrain_coverage_percent: Optional[float] = Field(
        None, ge=0, le=100, description="Percentage of the intended terrain actually covered."
    )
    missing_data_percent: Optional[float] = Field(
        None, ge=0, le=100, description="Percentage of missing / nodata pixels across both windows."
    )


class FeatureComparison(BaseModel):
    """Per-feature similarity metrics."""

    model_config = ConfigDict(extra="forbid")

    feature_id: str = Field(..., description="Feature identifier (slope, local_relief, terrain_ruggedness).")
    units: str = Field(..., description="Feature units.")
    wasserstein: Optional[float] = Field(None, description="Wasserstein distribution distance.")
    ks_statistic: Optional[float] = Field(None, description="Kolmogorov–Smirnov statistic.")
    pooled_iqr: Optional[float] = Field(None, description="Larger pooled interquartile range.")
    normalized_distance: Optional[float] = Field(None, description="Pooled-IQR-normalized Wasserstein distance.")
    sample_count_target: Optional[int] = Field(None, ge=0)
    sample_count_candidate: Optional[int] = Field(None, ge=0)


class ComparisonMetadata(BaseModel):
    """Complete standardized metadata for one TMSI comparison.

    Every reported TMSI comparison should carry this metadata so that the
    result is interpretable and reproducible. Fields that are unavailable are
    explicitly ``None``; nothing is fabricated.
    """

    model_config = ConfigDict(extra="forbid")

    # --- Comparison identification ---
    comparison_id: str = Field(..., min_length=1, description="Unique identifier for this comparison.")
    experiment_id: str = Field(..., description="Experiment or run identifier.")
    body_a: str = Field(..., description="Planetary body A.")
    body_b: str = Field(..., description="Planetary body B.")
    dataset_id_a: str = Field(..., description="Dataset identifier for body A.")
    dataset_id_b: str = Field(..., description="Dataset identifier for body B.")

    # --- Spatial information ---
    window_a: WindowInfo = Field(..., description="Spatial description of window A.")
    window_b: WindowInfo = Field(..., description="Spatial description of window B.")
    spatial_extent_km: float = Field(..., gt=0, description="Common physical extent of the comparison in km.")

    # --- Sampling information ---
    sampling: SamplingInfo = Field(..., description="Sampling design and overlap information.")

    # --- Scientific results ---
    similarity_index: Optional[float] = Field(
        None, ge=0, le=100, description="TMSI score (0—100), if computed."
    )
    combined_distance: Optional[float] = Field(
        None, ge=0, description="Combined pooled-IQR-normalized distance D, if computed."
    )
    confidence: Optional[str] = Field(None, description="Confidence classification, if computed.")
    feature_comparisons: list[FeatureComparison] = Field(
        default_factory=list, description="Per-feature similarity metrics."
    )
    weights: dict[str, float] = Field(
        default_factory=dict, description="Feature weights used in the combination."
    )
    statistical_diagnostics: dict[str, Any] = Field(
        default_factory=dict, description="Bootstrap, convergence, or other statistical diagnostics."
    )

    # --- Reproducibility ---
    algorithm_version: Optional[str] = Field(
        None, description="Version of the TMSI algorithm used."
    )
    dataset_version_a: Optional[str] = Field(None, description="Version of dataset A, if known.")
    dataset_version_b: Optional[str] = Field(None, description="Version of dataset B, if known.")
    processing_timestamp_utc: Optional[str] = Field(
        None, description="ISO-8601 timestamp when the comparison was processed."
    )
    configuration: dict[str, Any] = Field(
        default_factory=dict, description="Full configuration parameters used."
    )
    random_seed: Optional[int] = Field(None, description="Random seed, if randomness was used.")

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ComparisonMetadata":
        return cls.model_validate(data)


def make_comparison_id(body_a: str, body_b: str, dataset_id_a: str, dataset_id_b: str,
                       extent_km: float, window_a: WindowInfo, window_b: WindowInfo) -> str:
    """Deterministic, human-readable comparison ID (not a secret/hash of data)."""
    return (
        f"{body_a.lower()}_{dataset_id_a}_vs_{body_b.lower()}_{dataset_id_b}"
        f"_ext{extent_km:g}km_"
        f"wa{window_a.col_off}x{window_a.row_off}_"
        f"wb{window_b.col_off}x{window_b.row_off}"
    )


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()
