"""Validate and prepare the acquired bounded LOLA lunar DEM."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .inspect_data import inspect_raster
from .quality_control import quality_summary
from .raster_processing import write_masked_elevation
from .validate_data import validate_raster


def process_moon_lola(raw_path: Path, metadata_path: Path, processed_path: Path, report_path: Path) -> dict[str, object]:
    source = json.loads(metadata_path.read_text(encoding="utf-8"))
    validation = validate_raster(raw_path, expected_body="Moon", expected_resolution=(20.0, 20.0), expected_units="meters")
    original = inspect_raster(raw_path, "Moon")
    write_masked_elevation(raw_path, processed_path, body="Moon", variable="elevation", units="m")
    processed = quality_summary(processed_path)
    report: dict[str, object] = {
        "dataset": "moon_lola",
        "state": "VALIDATED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_url": source["source_url"],
        "official_url": source["official_url"],
        "original_file": str(raw_path),
        "processed_file": str(processed_path),
        "original_units": "m",
        "processed_units": "m",
        "original_resolution_m": [20.0, 20.0],
        "processed_resolution_m": [20.0, 20.0],
        "effective_resolution_summary": source["effective_resolution_summary"],
        "coordinate_system": original["coordinate_system"],
        "validation": validation,
        "original_quality": original,
        "processed_quality": processed,
        "processing_operations": [
            "Validated Moon south-polar stereographic CRS and metre units",
            "Preserved native 20 m/pixel raster geometry and values",
            "Preserved the source nodata mask; no missing observations were filled",
            "Created a DEFLATE-compressed processed GeoTIFF",
        ],
        "warnings": [
            "The effective-resolution ancillary is an overview average over the same window, not a 20 m effective-resolution claim",
            "The product is a 40.96 km pole-centered subset, not the complete 80S-90S parent DEM",
            "No Earth-to-Moon coordinate transform was applied",
        ],
        "known_limitations": source["known_limitations"],
        "provenance": {
            "dem_sha256": source["sha256"],
            "effective_resolution_sha256": source["effective_resolution_sha256"],
            "citation": source["citation"],
            "paper_doi": source["paper_doi"],
            "data_doi": source["data_doi"],
        },
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    source["state"] = "VALIDATED"
    metadata_path.write_text(json.dumps(source, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=Path("data/raw/moon_lola_80s_20m_shackleton_window.tif"))
    parser.add_argument("--metadata", type=Path, default=Path("data/metadata/moon_lola.json"))
    parser.add_argument("--processed", type=Path, default=Path("data/processed/moon_lola_80s_20m_elevation_m.tif"))
    parser.add_argument("--report", type=Path, default=Path("data/metadata/moon_lola_preprocessing.json"))
    args = parser.parse_args()
    report = process_moon_lola(args.raw, args.metadata, args.processed, args.report)
    print(json.dumps({"state": report["state"], "processed_file": report["processed_file"]}, indent=2))


if __name__ == "__main__":
    main()