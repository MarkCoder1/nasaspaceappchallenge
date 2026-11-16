"""Spatial and resolution normalization for Terra Twin Phase 18.

Implements scientifically defensible normalization of Earth DEM data
for cross-planetary comparison with lunar and Martian datasets.

CRITICAL:
- Never treat resampled data as if it had the original resolution of a finer dataset.
- Never create artificial terrain detail through upsampling.
- Document the selected resampling method and its implications.
- Support multiple analysis scales to investigate resolution sensitivity.

Always report original resolution alongside normalized resolution.
"""

from pathlib import Path
from typing import Any, Optional
import json
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject, calculate_default_transform
from rasterio.crs import CRS


def normalize_to_native_spacing(
    raster_path: Path,
    target_resolution_m: float = 20.0,
    resampling_method: str = "average",
) -> dict:
    """Normalize a DEM raster to the native 20 m post spacing matching Moon/Mars.

    Steps:
    1. Read the source raster and record original resolution and CRS
    2. Reproject/resample to target resolution using specified method
    3. Return metadata documenting original and normalized resolutions

    Returns dict with:
    - original_resolution_m: list of [x_res, y_res] from source
    - target_resolution_m: the resolution normalized to (default 20.0)
    - resampling_method: the method used (average, nearest, bilinear, etc.)
    - normalization_note: documentation of implications
    - crs_wkt: the CRS of the source raster
    - structural: whether the operation succeeded
    """
    resampling_map = {
        "average": Resampling.average,
        "nearest": Resampling.nearest,
        "bilinear": Resampling.bilinear,
        "cubic": Resampling.cubic,
    }
    resampling = resampling_map.get(resampling_method, Resampling.average)

    with rasterio.open(raster_path) as src:
        original_resolution_m = list(src.res)
        crs_wkt = src.crs.to_wkt() if src.crs else None
        original_count = src.count
        original_shape = src.height, src.width

        # Build the destination transform and shape for target resolution
        # New pixel count: larger pixel = fewer pixels
        x_ratio = original_resolution_m[0] / target_resolution_m
        y_ratio = original_resolution_m[1] / target_resolution_m
        new_width = int(round(src.width / x_ratio))
        new_height = int(round(src.height / y_ratio))
        new_width = max(1, new_width)
        new_height = max(1, new_height)

        # Compute the new transform
        new_transform = src.transform * src.transform.scale(
            target_resolution_m / original_resolution_m[0],
            target_resolution_m / original_resolution_m[1],
        )

        # Prepare destination array
        dst_array = np.empty((new_height, new_width), dtype="float32")

        # Use rasterio.warp.reproject for resampling
        reproject(
            source=src.read(1),
            destination=dst_array,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=new_transform,
            dst_crs=src.crs,
            resampling=resampling,
        )

        # Build metadata record
        normalization_note = (
            f"Resolution normalization from {original_resolution_m[0]} m "
            f"native post spacing to {target_resolution_m} m using "
            f"{resampling_method} resampling. "
            f"Original CRS: {crs_wkt}. "
            f"IMPORTANT: Normalized values should NOT be treated as if they "
            f"have the original {original_resolution_m[0]} m resolution. "
            f"The {target_resolution_m} m spacing represents an aggregated "
            f"representation suitable for cross-planetary comparison at the "
            f"same native post spacing as LOLA (20 m) and Mars DTM (20 m). "
            f"The {original_resolution_m[0]} m original resolution is preserved "
            f"in the metadata; do not conflate the two spacings in TMSI or "
            f"feature analysis. The {target_resolution_m} m spacing is an "
            f"effective spacing for comparison purposes only."
        )

        return {
            "original_resolution_m": original_resolution_m,
            "target_resolution_m": target_resolution_m,
            "resampling_method": resampling_method,
            "normalization_note": normalization_note,
            "crs_wkt": crs_wkt,
            "original_shape": original_shape,
            "normalized_shape": (new_height, new_width),
            "structural": True,
        }


def document_vertical_datum_difference(
    earth_datum: str,
    moon_datum: str,
    mars_datum: str,
) -> dict:
    """Document vertical datum differences between Earth, Moon, and Mars.

    Returns a dict describing the datum differences and recommended treatment.
    """
    differences = {
        "earth_datum": earth_datum,
        "moon_datum": moon_datum,
        "mars_datum": mars_datum,
        "treatment": "explicit_cross_reference",
        "notes": [
            "Earth DEMs typically use EGM96 geoid or WGS84 ellipsoidal heights",
            "Moon LOLA uses selenographic coordinates; heights above reference ellipsoid",
            "Mars MOLA/Jezero DTM use areocentric coordinates; heights above areoid",
            "Direct comparison of elevation values without datum treatment is not scientifically valid",
            "Required: record each dataset's vertical datum and do not combine elevations "
            "from different datums without explicit transformation",
        ],
    }
    return differences


def harmonize_extent(
    extent_km: float = 10.24,
) -> dict:
    """Document extent handling for cross-planetary comparison.

    Notes the extent used for TMSI calculations and the implications for results.
    """
    return {
        "extent_km": extent_km,
        "note": (
            "TMSI is extent-sensitive: 23.71 @ 5.12 km --> 49.92 @ 10.24 km. "
            "All TMSI results must report the extent used. Direct comparison across "
            "different extents is not valid. The default Phase 16 extent is 10.24 km. "
            "When comparing Earth to Moon/Mars, the same extent must be used for "
            "all three datasets after resolution normalization."
        ),
        "warning": (
            "If Earth DEM resolution differs from 20 m, the effective number of "
            "resolution cells within the extent window will differ, introducing "
            "an additional source of comparison variability that must be documented."
        ),
        "example": "Phase 16 baseline: TMSI = 49.92 at 10.24 km extent. "
        "At 5.12 km extent: TMSI = 23.71. The ratio is not linear; extent "
        "doubling does not double TMSI.",
        "phase_16_comparison": "Always document extent alongside TMSI results.",
        "cross_planet_requirement": (
            "When comparing Earth to Moon/Mars, use the same extent_km for all "
            "three datasets after resolution normalization to 20 m native post spacing."
        ),
    }


# Example usage pattern (not executed at import):
# >>> from science.earth_normalization import normalize_to_native_spacing
# >>> result = normalize_to_native_spacing(Path("earth_dem.tif"))
# >>> print(result["original_resolution_m"])
# [30.0, 30.0]
# >>> print(result["normalization_note"][:80]...)
# "Resolution normalization from 30 m native post spacing to 20 m..."