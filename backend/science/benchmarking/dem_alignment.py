"""DEM alignment and coordinate compatibility for Phase 13 benchmarking.

Responsibilities:
- Verify that two datasets share compatible coordinate reference systems.
- Document CRS differences and their implications for terrain metrics.
- Provide alignment parameters (translation, rotation) when compatible.
- Never imply that aligning different geographical regions represents the same terrain.
- Document all preprocessing operations applied during alignment.
"""

from typing import Any, Dict, List, Optional, Tuple


def crs_compatible(a: dict, b: dict) -> dict:
    """Check whether two datasets have compatible CRS.

    Returns
    - compatible: bool
    - a_crs: the CRS string from dataset a
    - b_crs: the CRS string from dataset b
    - transform_needed: bool (always False for now; actual transforms
      would require pyproj and are beyond this module's scope)
    - warnings: list of str
    """
    a_crs = a.get("horizontal_reference_system") or a.get("coordinate_reference", "")
    b_crs = b.get("horizontal_reference_system") or b.get("coordinate_reference", "")

    warnings: List[str] = []

    # Same body generally implies compatible CRS, but we still check
    if a.get("body") != b.get("body"):
        warnings.append("CRS comparison across different planetary bodies is not defined.")
        return {
            "compatible": False,
            "a_crs": a_crs,
            "b_crs": b_crs,
            "transform_needed": False,
            "warnings": warnings,
        }

    if a_crs == b_crs:
        return {
            "compatible": True,
            "a_crs": a_crs,
            "b_crs": b_crs,
            "transform_needed": False,
            "warnings": warnings,
        }

    # Different CRS but same body — document the mismatch
    warnings.append(
        f"CRS mismatch within same body: {a_crs} vs {b_crs}. "
        "Terrain metrics (slope, relief, TMSI) may differ due to "
        "coordinate system differences. Document and evaluate sensitivity."
    )

    return {
        "compatible": False,
        "a_crs": a_crs,
        "b_crs": b_crs,
        "transform_needed": False,
        "warnings": warnings,
    }


def elevation_unit_consistent(a: dict, b: dict) -> dict:
    """Check whether two datasets have consistent elevation units.

    Returns
    - consistent: bool
    - a_units: elevation units from dataset a
    - b_units: elevation units from dataset b
    - warnings: list of str
    """
    a_units = a.get("elevation_units")
    b_units = b.get("elevation_units")

    warnings: List[str] = []

    if a_units is None or b_units is None:
        warnings.append("One or both datasets lack elevation_units metadata.")
        return {
            "consistent": False,
            "a_units": a_units,
            "b_units": b_units,
            "warnings": warnings,
        }

    if a_units == b_units:
        return {
            "consistent": True,
            "a_units": a_units,
            "b_units": b_units,
            "warnings": warnings,
        }

    warnings.append(f"Elevation unit mismatch: {a_units} vs {b_units}.")
    return {
        "consistent": False,
        "a_units": a_units,
        "b_units": b_units,
        "warnings": warnings,
    }


def alignment_warnings(a: dict, b: dict) -> List[str]:
    """Return a list of all scientific warnings that should be recorded
    when comparing these two datasets.

    This aggregates CRS compatibility, elevation unit consistency,
    resolution differences, and body mismatches.
    """
    warnings: List[str] = []

    # Body mismatch
    if a.get("body") != b.get("body"):
        warnings.append(
            f"Comparing different planetary bodies ({a.get('body')} vs {b.get('body')}). "
            "TMSI and terrain metrics are not comparable across bodies."
        )

    # CRS compatibility
    crs = crs_compatible(a, b)
    if not crs["compatible"]:
        warnings.extend(crs["warnings"])

    # Elevation unit consistency
    eu = elevation_unit_consistent(a, b)
    if not eu["consistent"]:
        warnings.extend(eu["warnings"])

    # Resolution difference
    a_res = a.get("nominal_resolution")
    b_res = b.get("nominal_resolution")
    if a_res is not None and b_res is not None and a_res != b_res:
        warnings.append(
            f"Resolution difference: {a_res} vs {b_res}. "
            "Benchmark must evaluate resolution sensitivity (Phase 13 B3)."
        )

    return warnings