"""Acquire a bounded native-window subset from the official PGDA LOLA COGs."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.env import Env
from rasterio.enums import Resampling
from rasterio.transform import Affine
from rasterio.windows import Window, from_bounds


LOLA_DEM_URL = "https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF"
LOLA_EFFRES_URL = "https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ_EFFRES.TIF"
PGDA_PRODUCT_URL = "https://pgda.gsfc.nasa.gov/products/90"
HALF_WIDTH_M = 20_480.0


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_window(
    source_url: str,
    bounds: tuple[float, float, float, float],
    overview_divisor: int = 1,
) -> tuple[np.ndarray, rasterio.profiles.Profile, Window, dict[str, Any]]:
    virtual_path = f"/vsicurl/{source_url}"
    with Env(CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".TIF", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open(virtual_path) as source:
            window = from_bounds(*bounds, transform=source.transform).round_offsets().round_lengths()
            output_height = max(1, int(round(window.height / overview_divisor)))
            output_width = max(1, int(round(window.width / overview_divisor)))
            values = source.read(
                1,
                window=window,
                out_shape=(1, output_height, output_width),
                resampling=Resampling.average if overview_divisor > 1 else Resampling.nearest,
                masked=True,
            )
            profile = source.profile.copy()
            profile.update(
                height=output_height,
                width=output_width,
                transform=source.window_transform(window) * Affine.scale(window.width / output_width, window.height / output_height),
                compress="deflate",
                tiled=True,
                blockxsize=256,
                blockysize=256,
                dtype="float32",
                count=1,
                nodata=np.nan,
            )
            valid = values.compressed()
            summary = {
                "source_dimensions": [source.height, source.width],
                "source_resolution_m": list(source.res),
                "source_crs": source.crs.to_wkt() if source.crs else None,
                "source_nodata": source.nodata,
                "window": {"col_off": window.col_off, "row_off": window.row_off, "width": window.width, "height": window.height},
                "read_overview_divisor": overview_divisor,
                "read_shape": [output_height, output_width],
                "window_bounds_m": list(source.window_bounds(window)),
                "valid_pixel_count": int(values.count()),
                "total_pixel_count": int(values.size),
                "valid_percent": float(values.count() / values.size * 100),
                "missing_percent": float(np.ma.count_masked(values) / values.size * 100),
                "minimum": float(valid.min()) if valid.size else None,
                "maximum": float(valid.max()) if valid.size else None,
                "mean": float(valid.mean()) if valid.size else None,
            }
    return values, profile, window, summary


def _write_subset(path: Path, values: np.ndarray, profile: rasterio.profiles.Profile, variable: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    valid_mask = ~np.ma.getmaskarray(values)
    data = np.ma.getdata(values).astype(np.float32, copy=False)
    with rasterio.open(path, "w", **profile) as output:
        output.write(np.where(valid_mask, data, np.nan).astype(np.float32), 1)
        output.write_mask((valid_mask * 255).astype(np.uint8))
        output.update_tags(
            body="Moon",
            variable=variable,
            units="m" if variable == "elevation" else "m effective pixel scale",
            source="NASA GSFC PGDA LOLA south-polar COG window subset",
        )


def acquire_lola_window(raw_dir: Path, metadata_dir: Path) -> dict[str, Any]:
    dem_path = raw_dir / "moon_lola_80s_20m_shackleton_window.tif"
    effres_path = raw_dir / "moon_lola_80s_20m_shackleton_effres_window.tif"
    metadata_path = metadata_dir / "moon_lola.json"
    for path in (dem_path, effres_path, metadata_path):
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite existing LOLA artifact: {path}")

    bounds = (-HALF_WIDTH_M, -HALF_WIDTH_M, HALF_WIDTH_M, HALF_WIDTH_M)
    dem, dem_profile, _, dem_summary = _read_window(LOLA_DEM_URL, bounds)
    effres, effres_profile, _, effres_summary = _read_window(LOLA_EFFRES_URL, bounds, overview_divisor=64)
    _write_subset(dem_path, dem, dem_profile, "elevation")
    _write_subset(effres_path, effres, effres_profile, "effective_resolution")

    record: dict[str, Any] = {
        "dataset": "moon_lola",
        "state": "ACQUIRED",
        "name": "LDEM_80S_20MPP_ADJ bounded south-polar window",
        "planet": "Moon",
        "institution": "NASA GSFC Planetary Geodesy and Altimetry Data Archive",
        "official_url": PGDA_PRODUCT_URL,
        "source_url": LOLA_DEM_URL,
        "effective_resolution_source_url": LOLA_EFFRES_URL,
        "citation": "Barker et al., 2023, Planetary Science Journal, 4, 183",
        "data_doi": "10.60903/gsfcpgda-lola-spole",
        "paper_doi": "10.3847/PSJ/acf3e1",
        "acquisition_method": "Windowed range reads from official Cloud-Optimized GeoTIFFs; full 2.6 GB parent DEM was not downloaded",
        "source_parent_size_bytes": 2_696_082_051,
        "local_file": str(dem_path),
        "local_effective_resolution_file": str(effres_path),
        "file_size_bytes": dem_path.stat().st_size,
        "sha256": _sha256(dem_path),
        "effective_resolution_sha256": _sha256(effres_path),
        "acquired_at_utc": datetime.now(timezone.utc).isoformat(),
        "variable": "surface elevation",
        "units": "meters",
        "nominal_resolution": "20 m/pixel",
        "effective_resolution": "See local effective-resolution raster and summary; not assumed equal to 20 m",
        "coordinate_reference": "Moon (2015) Sphere / Ocentric / South Polar; south polar stereographic X/Y in metres; MOON_ME DE421 reference frame",
        "window_bounds_m": list(bounds),
        "dem_summary": dem_summary,
        "effective_resolution_summary": effres_summary,
        "ancillary_quality": "LDEM_EFFRES records effective resolution; the local ancillary is a 64x overview average over the same native window; LDEM_ERR is not downloaded",
        "known_limitations": [
            "This is a pole-centered 40.96 km subset, not the complete 80S-90S parent DEM.",
            "The subset is native-coordinate bounded; no Earth-to-Moon coordinate transform was applied.",
            "The source product documents interpolation and adjusted/blended construction; effective resolution must be respected.",
        ],
    }
    metadata_dir.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--metadata-dir", type=Path, default=Path("data/metadata"))
    args = parser.parse_args()
    record = acquire_lola_window(args.raw_dir, args.metadata_dir)
    print(json.dumps({"state": record["state"], "file": record["local_file"], "metadata": str(args.metadata_dir / "moon_lola.json")}, indent=2))


if __name__ == "__main__":
    main()