"""Scientific uncertainty framework for Phase 13 benchmarking.

Distinguishes four independent uncertainty categories as specified in
Phase 13 Section 7. Each category is reported separately; they are
not combined into an arbitrary uncertainty percentage.

Do not combine these into one arbitrary uncertainty percentage.
Report each separately.

Where possible, use repeated sampling, bootstrap confidence intervals,
and sensitivity analysis.

Document assumptions and limitations.
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def dataset_uncertainty(
    datasets_a: List[dict],
    datasets_b: List[dict],
) -> Dict[str, any]:
    """Report uncertainty arising from independently produced elevation products.

    This category quantifies differences between DEM datasets that are
    produced independently (different missions, processing pipelines,
    reference frames). It is not a measure of "error" but of dataset
    diversity.

    Returns a dict with:
    - per_dataset: dict mapping dataset id to its metadata summary
    - elevation_range_per_dataset: (min, max) elevation values per dataset
    - resolution_spread_m: spread of nominal resolutions
    - vertical_reference_diversity: count of distinct vertical refs
    - warnings: list of scientific caveats
    """
    per_dataset: Dict[str, dict] = {}
    all_elevations: List[float] = []
    resolutions: List[float] = []
    vertical_refs: set = set()

    for ds in datasets_a + datasets_b:
        vid = ds.get("id", "unknown")
        elevation_units = ds.get("elevation_units", "")
        nominal_res = ds.get("nominal_resolution")
        vref = ds.get("vertical_reference_system") or ds.get("horizontal_reference_system", "")

        # Parse nominal resolution string (e.g., "20 m/pixel", "20 m pixel spacing", "1 arc-second")
        res_val = 1.0
        if nominal_res is not None and isinstance(nominal_res, str):
            # Extract leading numeric value
            import re
            match = re.match(r"[\d.]+", nominal_res)
            if match:
                res_val = float(match.group())
        resolutions.append(res_val)
        vertical_refs.add(vref)

        # Try to extract elevation range from local file or metadata
        # (placeholder: in full implementation would load the raster)
        per_dataset[vid] = {
            "elevation_units": elevation_units,
            "nominal_resolution_m": nominal_res,
            "vertical_reference_system": vref,
        }

    # Compute spread
    resolution_spread_m = max(resolutions) - min(resolutions) if len(resolutions) > 1 else 0.0

    return {
        "category": "dataset_uncertainty",
        "per_dataset": per_dataset,
        "resolution_spread_m": resolution_spread_m,
        "vertical_reference_diversity_count": len(vertical_refs),
        "vertical_references": sorted(vertical_refs),
        "warnings": [
            "Dataset uncertainty quantifies differences between independently "
            "produced elevation products. It is not a measure of 'error.'",
            "Different vertical reference systems may affect slope and relief "
            "calculations in ways that are not easily corrected.",
            "Resolution differences should be evaluated via sensitivity analysis "
            "(Phase 13 B3), not conflated with measurement error.",
        ],
    }


def resolution_uncertainty(
    elevations_a: np.ndarray,
    elevations_b: np.ndarray,
    resolution_m_a: float,
    resolution_m_b: float,
) -> Dict[str, any]:
    """Report uncertainty arising from spatial resolution differences.

    Evaluates how terrain measurements change when datasets are
    resampled to compatible resolutions.

    Important requirements (Phase 13 B3):
    - Preserve original-resolution data.
    - Record every resampling operation.
    - Document interpolation methods.
    - Avoid implying that resampling restores lost information.
    - Compare results at multiple defensible resolutions when coverage
      permits.

    Returns a dict with:
    - resolution_ratio: target/original
    - notes: scientific cautions about resampling
    - comparison_metrics: dict of metric differences at each resolution
    """
    ratio = resolution_m_b / resolution_m_a if resolution_m_a > 0 else float("inf")

    return {
        "category": "resolution_uncertainty",
        "resolution_a_m": resolution_m_a,
        "resolution_b_m": resolution_m_b,
        "resolution_ratio": ratio,
        "notes": [
            f"Comparing data at {resolution_m_a} m vs {resolution_m_b} m "
            "resolution.",
            f"Resolution ratio (B/A) = {ratio:.2f}. A ratio > 1 means B is "
            "coarser; < 1 means B is finer.",
            "Preserve original-resolution data. Do not imply that resampling "
            "restores lost information.",
            "Record the interpolation method used for any resampling.",
            "Compare results at multiple resolutions when coverage permits "
            "(Phase 13 B3).",
        ],
        "comparison_metrics": {
            "note": "Actual metric comparisons would require loaded raster data. "
            "This structure records what would be compared at each resolution.",
        },
    }


def sampling_uncertainty(
    n_windows_a: int,
    n_windows_b: int,
    window_offset_a: Tuple[int, int],
    window_offset_b: Tuple[int, int],
    extent_km: float,
) -> Dict[str, any]:
    """Report uncertainty arising from window location and selection.

    Effects of window location and selection on TMSI and terrain metrics.

    Returns a dict with:
    - n_windows_a, n_windows_b: number of sampling windows per dataset
    - window_offsets: (row, col) offsets for each dataset
    - extent_km: spatial extent used for TMSI computation
    - notes: scientific caveats about window selection
    - sensitivity_warning: whether window location may significantly affect results
    """
    # Phase 12 finding: TMSI is extent-sensitive (23.71 @ 5.12 km → 49.92 at full)
    # and window-location-sensitive. Report these as separate uncertainties.

    return {
        "category": "sampling_uncertainty",
        "n_windows_a": n_windows_a,
        "n_windows_b": n_windows_b,
        "window_offset_a": window_offset_a,
        "window_offset_b": window_offset_b,
        "extent_km": extent_km,
        "notes": [
            "TMSI is extent-sensitive (Phase 12). Different extents produce "
            "different scores (e.g., 23.71 @ 5.12 km → 49.92 at full 10.24 km extent).",
            "TMSI is window-location-sensitive. Different window positions "
            "within the same DEM may yield different scores.",
            "Within-body TMSI ranges overlap between Moon (29.27–94.10) and "
            "between-body range (22.38–90.60). Window selection affects which "
            "portion of the range is sampled.",
            "Non-overlapping windows provide independent observations; "
            "identical or highly overlapping windows inflate similarity (TMSI → 100).",
        ],
        "sensitivity_warning": True,
    }


def methodological_sensitivity(
    extent_km: float,
    overlap_status: str,
    confidence: str = "HIGH",
) -> Dict[str, any]:
    """Report methodological sensitivity from spatial extent, overlap, and algorithm configuration.

    Effects of spatial extent, overlap, and algorithm configuration on
    TMSI and terrain metric results.

    Returns a dict with:
    - extent_km: spatial extent used
    - overlap_status: classification (identical/high/partial/none/unknown)
    - confidence: reported confidence level
    - notes: scientific caveats
    - materiality_warning: whether the parameter choice materially affects results
    """
    # Phase 12 findings:
    # - TMSI is extent-sensitive
    # - Identical windows → TMSI = 100 (self-control)
    # - High overlap inflates similarity
    # - Within-body ranges exceed between-body ranges
    # - Body identity not recoverable from TMSI alone

    materiality_map = {
        "identical": "Identical windows give TMSI = 100 (self-control). "
        "Does not establish inter-dataset similarity.",
        "high": "High overlap inflates similarity. Only non-overlapping "
        "comparisons are independent observations.",
        "partial": "Partial overlap: TMSI is meaningful but diminished. "
        "Report overlap fraction and classify accordingly.",
        "none": "No overlap: TMSI compares non-overlapping windows. "
        "Results describe distributional separation, not similarity.",
        "unknown": "Overlap status unknown. Cannot classify similarity "
        "without overlap information.",
    }

    note = materiality_map.get(
        overlap_status,
        f"Overlap status '{overlap_status}': report with caution.",
    )

    # Extent materiality: Phase 12 found TMSI changes from 23.71 @ 5.12 km
    # to 49.92 at full 10.24 km extent — a material change.
    extent_material = extent_km < 10.0  # below full extent is potentially material

    return {
        "category": "methodological_sensitivity",
        "extent_km": extent_km,
        "overlap_status": overlap_status,
        "confidence": confidence,
        "notes": [
            note,
            f"Spatial extent of {extent_km} km may materially affect TMSI "
            "results (Phase 12: 5.12 km → 10.24 km changed TMSI from 23.71 "
            "to 49.92).",
            "Overlap introduces bias: identical windows → TMSI = 100; high "
            "overlap → 78.6–88.0 depending on overlap fraction.",
            "Body identity is not recoverable from TMSI alone (within-body "
            "and between-body TMSI ranges overlap substantially).",
            "Confidence level should be reported alongside the TMSI value.",
        ],
        "materiality_warning": extent_material,
    }


def full_uncertainty_report(
    dataset_uncert: Dict[str, any],
    resolution_uncert: Dict[str, any],
    sampling_uncert: Dict[str, any],
    methodological_uncert: Dict[str, any],
) -> Dict[str, any]:
    """Combine the four uncertainty categories into a single structured report.

    Does NOT combine them into one arbitrary uncertainty percentage.
    Report each category separately as required by Phase 13 Section 7.

    Returns a dict with all four categories and a summary.
    """
    return {
        "dataset_uncertainty": dataset_uncert,
        "resolution_uncertainty": resolution_uncert,
        "sampling_uncertainty": sampling_uncert,
        "methodological_sensitivity": methodological_uncert,
        "summary": {
            "reporting_framework": "Phase 13 Section 7 — four independent "
            "categories, not combined into one percentage.",
            "dataset_uncertainty_reported": dataset_uncert.get("category")
            == "dataset_uncertainty",
            "resolution_uncertainty_reported": resolution_uncert.get(
                "category"
            )
            == "resolution_uncertainty",
            "sampling_uncertainty_reported": sampling_uncert.get("category")
            == "sampling_uncertainty",
            "methodological_sensitivity_reported": methodological_uncert.get(
                "category"
            )
            == "methodological_sensitivity",
            "all_four_categories_present": all(
                [
                    dataset_uncert.get("category"),
                    resolution_uncert.get("category"),
                    sampling_uncert.get("category"),
                    methodological_uncert.get("category"),
                ]
            ),
        },
    }