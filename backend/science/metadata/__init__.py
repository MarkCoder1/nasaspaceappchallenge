"""Scientific metadata architecture for TMSI comparisons.

Provides a standardized schema, validation, and serialization for every TMSI
comparison so that results are interpretable and reproducible.

Public API:
- :class:`science.metadata.schema.ComparisonMetadata`
- :class:`science.metadata.schema.WindowInfo`
- :class:`science.metadata.schema.SamplingInfo`
- :class:`science.metadata.schema.FeatureComparison`
- :class:`science.metadata.schema.OverlapClassification`
- :class:`science.metadata.schema.SamplingStrategy`
- :func:`science.metadata.validation.validate_metadata`
- :func:`science.metadata.validation.require_complete`
- :func:`science.metadata.serialization.build_comparison_metadata`
- :func:`science.metadata.serialization.merge_metadata_into_export`
- :func:`science.metadata.serialization.validate_export_metadata`
"""

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
from .serialization import (
    build_comparison_metadata,
    feature_comparison_from_engine,
    merge_metadata_into_export,
    sampling_info_from_overlap,
    validate_export_metadata,
    window_info_from_feature_set,
)
from .validation import MetadataValidationError, require_complete, validate_metadata

__all__ = [
    "ComparisonMetadata",
    "FeatureComparison",
    "OverlapClassification",
    "SamplingInfo",
    "SamplingStrategy",
    "WindowInfo",
    "make_comparison_id",
    "now_utc",
    "build_comparison_metadata",
    "feature_comparison_from_engine",
    "merge_metadata_into_export",
    "sampling_info_from_overlap",
    "validate_export_metadata",
    "window_info_from_feature_set",
    "MetadataValidationError",
    "require_complete",
    "validate_metadata",
]
