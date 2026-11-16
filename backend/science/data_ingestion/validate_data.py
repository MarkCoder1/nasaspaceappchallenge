"""Validate acquired files and their recorded provenance."""

import argparse
import json
from pathlib import Path

import rasterio


def validate_file(file_path: Path, metadata_path: Path) -> dict[str, object]:
    if not file_path.is_file() or file_path.stat().st_size == 0:
        raise ValueError(f"Missing or empty file: {file_path}")
    if file_path.suffix.lower() not in {".tif", ".tiff", ".hgt"}:
        raise ValueError(f"Unsupported raster format for validation: {file_path.suffix}")
    with rasterio.open(file_path) as raster:
        result: dict[str, object] = {
            "driver": raster.driver,
            "width": raster.width,
            "height": raster.height,
            "count": raster.count,
            "dtype": raster.dtypes[0],
            "crs": raster.crs.to_string() if raster.crs else None,
            "transform": tuple(raster.transform),
        }
    recorded = json.loads(metadata_path.read_text(encoding="utf-8"))
    if recorded["file_size_bytes"] != file_path.stat().st_size:
        raise ValueError("Metadata file size does not match the acquired file")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("metadata", type=Path)
    args = parser.parse_args()
    import json as _json

    print(_json.dumps(validate_file(args.file, args.metadata), indent=2, default=str))


if __name__ == "__main__":
    main()