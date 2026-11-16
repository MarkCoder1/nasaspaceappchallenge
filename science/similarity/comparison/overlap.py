"""Overlap and extent diagnostics for terrain-window comparisons.

Provides mathematically defined overlap classification and extent-sensitivity
helpers. Overlap is only meaningful when both windows are expressed in the same
coordinate system (same body / same raster). Cross-body comparisons report
``overlap_classification = unknown`` because pixel offsets within different
rasters are not spatially comparable.
"""

from dataclasses import dataclass
from typing import Optional

from science.metadata.schema import OverlapClassification, WindowInfo


# Mathematically defined overlap thresholds.
_IDENTICAL_THRESHOLD = 0.99
_HIGH_THRESHOLD = 0.5


@dataclass(frozen=True)
class OverlapDiagnostic:
    """Result of overlap analysis between two windows."""

    overlap_ratio: Optional[float]
    """Fraction of the smaller window overlapped by the larger (0 to 1), or
    ``None`` when the windows are not in a comparable coordinate system."""
    classification: OverlapClassification
    """Classified overlap relationship."""
    comparable: bool
    """Whether the two windows share a coordinate system in which overlap is
    meaningful."""
    reason: str
    """Human-readable explanation of the classification."""


def compute_overlap_fraction(window_a: WindowInfo, window_b: WindowInfo) -> Optional[float]:
    """Return the overlap fraction between two windows.

    Only meaningful when both windows are on the same body and share a CRS.
    Returns ``None`` for cross-body or cross-CRS comparisons, where pixel
    offsets within different rasters are not spatially comparable.
    """
    if window_a.body != window_b.body:
        return None
    if window_a.crs is not None and window_b.crs is not None and window_a.crs != window_b.crs:
        return None

    a_col_start, a_col_end = window_a.col_off, window_a.col_off + window_a.width_cells
    a_row_start, a_row_end = window_a.row_off, window_a.row_off + window_a.height_cells
    b_col_start, b_col_end = window_b.col_off, window_b.col_off + window_b.width_cells
    b_row_start, b_row_end = window_b.row_off, window_b.row_off + window_b.height_cells

    col_overlap = max(0, min(a_col_end, b_col_end) - max(a_col_start, b_col_start))
    row_overlap = max(0, min(a_row_end, b_row_end) - max(a_row_start, b_row_start))
    overlap_area = col_overlap * row_overlap
    if overlap_area == 0:
        return 0.0
    area_a = window_a.width_cells * window_a.height_cells
    area_b = window_b.width_cells * window_b.height_cells
    return overlap_area / min(area_a, area_b)


def classify_overlap(overlap_ratio: Optional[float]) -> OverlapClassification:
    """Classify an overlap ratio using mathematically defined thresholds.

    Thresholds:
    - ``identical``: ratio >= 0.99
    - ``high``: ratio >= 0.5
    - ``partial``: ratio > 0
    - ``none``: ratio == 0
    - ``unknown``: ratio is None
    """
    if overlap_ratio is None:
        return OverlapClassification.UNKNOWN
    if overlap_ratio >= _IDENTICAL_THRESHOLD:
        return OverlapClassification.IDENTICAL
    if overlap_ratio >= _HIGH_THRESHOLD:
        return OverlapClassification.HIGH
    if overlap_ratio > 0.0:
        return OverlapClassification.PARTIAL
    return OverlapClassification.NONE


def diagnose_overlap(window_a: WindowInfo, window_b: WindowInfo) -> OverlapDiagnostic:
    """Run full overlap diagnosis for two windows."""
    comparable = window_a.body == window_b.body and (
        window_a.crs is None or window_b.crs is None or window_a.crs == window_b.crs
    )
    if not comparable:
        return OverlapDiagnostic(
            overlap_ratio=None,
            classification=OverlapClassification.UNKNOWN,
            comparable=False,
            reason=(
                "Windows are on different bodies or different CRSs; "
                "pixel offsets are not spatially comparable."
            ),
        )
    ratio = compute_overlap_fraction(window_a, window_b)
    classification = classify_overlap(ratio)
    if classification == OverlapClassification.IDENTICAL:
        reason = "Windows occupy the same cells (identical comparison)."
    elif classification == OverlapClassification.HIGH:
        reason = f"Windows share {ratio:.0%} of the smaller window (high overlap)."
    elif classification == OverlapClassification.PARTIAL:
        reason = f"Windows share {ratio:.0%} of the smaller window (partial overlap)."
    else:
        reason = "Windows do not overlap (non-overlapping comparison)."
    return OverlapDiagnostic(
        overlap_ratio=ratio,
        classification=classification,
        comparable=True,
        reason=reason,
    )


def is_identical_window(window_a: WindowInfo, window_b: WindowInfo) -> bool:
    """Return True if the two windows are the same body and occupy the same cells."""
    if window_a.body != window_b.body:
        return False
    if window_a.col_off != window_b.col_off or window_a.row_off != window_b.row_off:
        return False
    if window_a.width_cells != window_b.width_cells or window_a.height_cells != window_b.height_cells:
        return False
    return True
