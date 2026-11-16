"""Run the reproducible Phase 3 preprocessing pipeline for verified inputs."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .inspect_data import inspect_raster
from .quality_control import quality_summary
from .raster_processing import write_masked_elevation
from .resolution import preserve_native_resolution
from .units import elevation_meters
from .validate_data import validate_raster


def process_jezero(
    raw_path: Path,
    processed_path: Path,
    metadata_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    source_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    validation = validate_raster(
        raw_path,
        expected_body="Mars",
        expected_resolution=(20.0, 20.0),
        expected_units="meters",
    )
    original = inspect_raster(raw_path, "Mars")
    processing = write_masked_elevation(raw_path, processed_path)
    processed = quality_summary(processed_path)
    resolution = preserve_native_resolution((20.0, 20.0))
    units = elevation_meters()
    report: dict[str, Any] = {
        "dataset": source_metadata["dataset"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_url": source_metadata["source_url"],
        "original_file": str(raw_path),
        "processed_file": str(processed_path),
        "original_units": source_metadata["units"],
        "processed_units": units.processed_unit,
        "unit_conversion": {
            "formula": units.formula,
            "applied": units.applied,
        },
        "original_resolution": original["resolution"],
        "processed_resolution": resolution.processed_resolution_m,
        "resolution_decision": {
            "resampled": resolution.resampled,
            "method": resolution.method,
            "rationale": resolution.rationale,
        },
        "coordinate_system": original["coordinate_system"],
        "validation": validation,
        "original_quality": original,
        "processed_quality": processed,
        "processing_operations": [
            "Validated Mars CRS, one band, finite values, meters, and native 20 m resolution",
            "Preserved source values, extent, CRS, transform, and native resolution",
            "Represented the source nodata sentinel as NaN plus an internal raster mask",
            "Wrote DEFLATE-compressed GeoTIFF to data/processed",
        ],
        "normalized_variables": [],
        "warnings": [
            "The source contains no observed missing pixels; its nodata sentinel remains documented",
            "No Earth or Moon raster was available for harmonization",
            "No temperature, thermal inertia, geology, slope, or roughness variable was processed",
        ],
        "known_limitations": [
            "This is a Jezero-specific Mars terrain product, not a global Mars elevation model",
            "Mars planetary coordinates are not interchangeable with Earth geographic coordinates",
            "No cross-body normalization was created because compatible Earth and Moon inputs are unavailable",
        ],
        "source_metadata_file": str(metadata_path),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=Path("data/raw/JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif"))
    parser.add_argument("--metadata", type=Path, default=Path("data/metadata/mars_jezero_ctx_dtm.json"))
    parser.add_argument("--processed", type=Path, default=Path("data/processed/mars_jezero_ctx_elevation_m.tif"))
    parser.add_argument("--report", type=Path, default=Path("data/metadata/mars_jezero_ctx_preprocessing.json"))
    args = parser.parse_args()
    report = process_jezero(args.raw, args.processed, args.metadata, args.report)
    print(json.dumps({"processed_file": report["processed_file"], "report_file": str(args.report)}, indent=2))


if __name__ == "__main__":
    main()