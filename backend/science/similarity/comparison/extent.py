"""Extent-sensitivity diagnostics for terrain-window comparisons.

Phase 11 showed that TMSI varies strongly with spatial extent (e.g. 23.71 at
5.12 km vs 49.92 at full extent). This module provides helpers to compute,
record, and flag extent sensitivity so that every reported score is
communicated alongside its spatial extent.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ExtentSensitivityDiagnostic:
    """Result of extent-sensitivity analysis for a comparison."""

    extent_km: float
    """Physical extent of this comparison in kilometres."""
    reference_extent_km: Optional[float]
    """Reference extent (e.g. the full validated dataset extent), if known."""
    extent_delta_km: Optional[float]
    """Absolute difference between this extent and the reference extent."""
    extent_ratio: Optional[float]
    """Ratio of this extent to the reference extent."""
    sensitivity_flag: bool
    """True when the extent differs materially from the reference (ratio
    outside [0.5, 2.0] or delta > 5 km), meaning the score is not directly
    comparable to the reference."""
    reason: str
    """Human-readable explanation."""


# Thresholds for "material" extent difference.
_EXTENT_RATIO_LOW = 0.5
_EXTENT_RATIO_HIGH = 2.0
_EXTENT_DELTA_KM = 5.0


def diagnose_extent_sensitivity(
    extent_km: float,
    reference_extent_km: Optional[float] = None,
) -> ExtentSensitivityDiagnostic:
    """Diagnose whether a comparison extent is materially different from a
    reference extent.

    When no reference is provided, the diagnostic is informational only
    (sensitivity_flag False) but still records the extent.
    """
    if extent_km <= 0:
        raise ValueError("extent_km must be positive")

    if reference_extent_km is None:
        return ExtentSensitivityDiagnostic(
            extent_km=extent_km,
            reference_extent_km=None,
            extent_delta_km=None,
            extent_ratio=None,
            sensitivity_flag=False,
            reason=f"Extent {extent_km:g} km recorded; no reference extent for comparison.",
        )

    if reference_extent_km <= 0:
        raise ValueError("reference_extent_km must be positive")

    delta = abs(extent_km - reference_extent_km)
    ratio = extent_km / reference_extent_km
    flag = (ratio < _EXTENT_RATIO_LOW or ratio > _EXTENT_RATIO_HIGH) or delta > _EXTENT_DELTA_KM

    if flag:
        reason = (
            f"Extent {extent_km:g} km differs materially from reference "
            f"{reference_extent_km:g} km (ratio {ratio:.2f}, delta {delta:g} km); "
            "the score is not directly comparable to the reference extent."
        )
    else:
        reason = (
            f"Extent {extent_km:g} km is consistent with reference "
            f"{reference_extent_km:g} km (ratio {ratio:.2f}, delta {delta:g} km)."
        )

    return ExtentSensitivityDiagnostic(
        extent_km=extent_km,
        reference_extent_km=reference_extent_km,
        extent_delta_km=delta,
        extent_ratio=ratio,
        sensitivity_flag=flag,
        reason=reason,
    )


def cells_to_extent_km(n_cells: int, cell_m: float = 20.0) -> float:
    """Convert a square window cell count to physical extent in kilometres."""
    if n_cells <= 0 or cell_m <= 0:
        raise ValueError("n_cells and cell_m must be positive")
    return n_cells * cell_m / 1000.0


def extent_km_to_cells(extent_km: float, cell_m: float = 20.0) -> int:
    """Convert a physical extent in kilometres to square window cell count."""
    if extent_km <= 0 or cell_m <= 0:
        raise ValueError("extent_km and cell_m must be positive")
    return int(round(extent_km * 1000.0 / cell_m))
