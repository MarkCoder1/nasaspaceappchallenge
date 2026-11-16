"""TMSI reproducibility benchmarking for Phase 13.

Responsibilities:
- Run TMSI comparisons using independently sourced datasets.
- Determine how much scores change between DEM sources.
- Whether rankings remain consistent.
- Whether extent sensitivity persists.
- Whether window-location sensitivity persists.
- Whether overlap introduces similar biases.
- Whether dataset resolution changes the conclusions.

Use the same scientific methodology wherever possible.
If modifications are necessary, document them and preserve the original
Phase 1-12 methodology as a separate version.

Do not fabricate TMSI scores or claim reproducibility where none exists.
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from app.services.similarity import compare_terrain


def run_tmsi_reproducibility(
    dataset_a_id: str,
    dataset_b_id: str,
    extent_km: float = 10.24,
    window_offset_a: Tuple[int, int] = (0, 0),
    window_offset_b: Tuple[int, int] = (0, 0),
) -> dict:
    """Run TMSI comparison between two datasets for reproducibility analysis.

    This uses the existing compare_terrain() backend function with optional
    window and extent parameters to evaluate how TMSI scores change between
    different dataset sources.

    Returns a dict with:
    - tmsi_a: TMSI score from dataset A (baseline)
    - tmsi_b: TMSI score from dataset B (comparison)
    - absolute_difference: |tmsi_a - tmsi_b|
    - relative_difference: |tmsi_a - tmsi_b| / max(tmsi_a, tmsi_b, 1)
    - extent_km: spatial extent used
    - window_offsets: (offset_a, offset_b) in pixels
    - overlap_status: classification from Phase 12 overlap diagnostics
    - methodology_version: "compare_terrain backend v1" (documented)
    - warnings: list of scientific caveats

    Important: TMSI is extent-sensitive (Phase 12 finding). Always record
    the extent_km used. Different extents produce different scores.
    """
    warnings: List[str] = []

    # Get dataset metadata
    from science.datasets.registry import get_dataset
    a = get_dataset(dataset_a_id)
    b = get_dataset(dataset_b_id)

    if a is None:
        warnings.append(f"Dataset not found: {dataset_a_id}")
    if b is None:
        warnings.append(f"Dataset not found: {dataset_b_id}")

    # Check that we're not comparing across bodies (not scientifically meaningful)
    if a is not None and b is not None and a.get("body") != b.get("body"):
        warnings.append(
            f"Comparing TMSI across different planetary bodies "
            f"({a.get('body')} vs {b.get('body')}). TMSI is not "
            "body-identifiable; only within-body comparisons are valid."
        )

    # Use the existing compare_terrain function with the provided parameters
    # This preserves the Phase 1-12 methodology contract
    try:
        # Build the comparison using the backend service
        # We pass window_a, window_b, and spatial_extent_km as additive params
        result = compare_terrain(
            dataset_a_id=dataset_a_id,
            dataset_b_id=dataset_b_id,
            window_a=window_offset_a,
            window_b=window_offset_b,
            spatial_extent_km=extent_km,
        )

        tmsi_a = result.get("tmsi_a") or result.get("similarity_index")
        tmsi_b = result.get("tmsi_b") or result.get("similarity_index")

        if tmsi_a is None or tmsi_b is None:
            # Fallback: cannot compute TMSI without actual rasters
            # Return structured result with warnings
            return {
                "tmsi_a": None,
                "tmsi_b": None,
                "absolute_difference": None,
                "relative_difference": None,
                "extent_km": extent_km,
                "window_offsets": (window_offset_a, window_offset_b),
                "overlap_status": "unknown",
                "methodology_version": "compare_terrain backend v1",
                "warnings": warnings + ["TMSI could not be computed: no raster data available"],
                "comparability_note": "TMSI computation requires actual elevation raster data. "
                "The comparison_diagnostics field in the result should contain "
                "overlap and extent information where available.",
            }

        absolute_diff = abs(tmsi_a - tmsi_b)
        # Avoid division by zero; use max with 1
        relative_diff = absolute_diff / max(tmsi_a, tmsi_b, 1)

        # Classify overlap status using Phase 12 diagnostics
        overlap_info = result.get("comparison_diagnostics", {})
        overlap_status = overlap_info.get("overlap_status", "unknown")

        return {
            "tmsi_a": float(tmsi_a),
            "tmsi_b": float(tmsi_b),
            "absolute_difference": float(absolute_diff),
            "relative_difference": float(relative_diff),
            "extent_km": extent_km,
            "window_offsets": (window_offset_a, window_offset_b),
            "overlap_status": overlap_status,
            "methodology_version": "compare_terrain backend v1",
            "warnings": warnings,
            "comparability_note": (
                "TMSI is extent-sensitive (Phase 12). Different extents produce "
                "different scores. Within-body TMSI ranges may overlap between "
                "different DEM sources. TMSI does not identify planetary body."
            ),
        }

    except Exception as e:
        # Catch any backend errors and return structured result
        return {
            "tmsi_a": None,
            "tmsi_b": None,
            "absolute_difference": None,
            "relative_difference": None,
            "extent_km": extent_km,
            "window_offsets": (window_offset_a, window_offset_b),
            "overlap_status": "error",
            "methodology_version": "compare_terrain backend v1",
            "warnings": warnings + [f"compare_terrain() raised: {e}"],
            "comparability_note": "Error running TMSI reproducibility comparison.",
        }