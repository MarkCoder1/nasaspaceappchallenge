"""Benchmark report generation for Phase 13.

Responsibilities:
- Export reproducible benchmark results as JSON, CSV, or structured text.
- Include full experiment configuration (datasets, resolutions, extents,
  window offsets, methodology version).
- Record uncertainties and limitations alongside measurements.
- Never fabricate or invent measurement values.
- Every experiment must have a unique identifier and configuration record.

The report format is JSON by default, with CSV export for tabular metrics.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .terrain_metric_benchmark import benchmark_terrain_metrics


def generate_benchmark_id() -> str:
    """Generate a unique benchmark identifier."""
    return f"benchmark-{uuid.uuid4().hex[:16]}"


def timestamp_utc() -> str:
    """Return current UTC ISO 8601 timestamp."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def export_benchmark_json(
    config: dict,
    tmsi_result: dict,
    terrain_result: Optional[dict] = None,
    filepath: Optional[str] = None,
) -> str:
    """Export a benchmark result as JSON.

    Parameters
    config: experiment configuration dict with keys:
        - benchmark_id: str
        - dataset_a_id: str
        - dataset_b_id: str
        - extent_km: float
        - window_offsets: (ra, ca), (rb, cb)
        - methodology_version: str
        - created_at: str (ISO 8601)
    tmsi_result: dict with tmsi comparison results
    terrain_result: optional result dict from benchmark_terrain_metrics()
    filepath: if provided, write to this file; return the JSON string either way.

    Returns the JSON string.
    """
    benchmark_id = config.get("benchmark_id", generate_benchmark_id())
    experiment = {
        "benchmark_id": benchmark_id,
        "created_at": config.get("created_at", timestamp_utc()),
        "methodology_version": config.get("methodology_version", "phase13_v1"),
        "dataset_a": {
            "id": config.get("dataset_a_id"),
            "body": None,
            "body": None,
        },
        "dataset_b": {
            "id": config.get("dataset_b_id"),
            "body": None,
        },
        "tmsi": tmsi_result,
        "terrain_metrics": terrain_result or {},
        "warnings": tmsi_result.get("warnings", []),
        "comparability_note": tmsi_result.get("comparability_note", ""),
    }

    json_str = json.dumps(experiment, indent=2, default=str)

    if filepath:
        path = pathlib.Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json_str, encoding="utf-8")

    return json_str


def export_benchmark_csv(
    tmsi_result: dict,
    filepath: str,
) -> None:
    """Export TMSI reproducibility results as CSV.

    Parameters
    tmsi_result: dict with tmsi comparison results
    filepath: output CSV path.
    """
    import csv

    fieldnames = [
        "benchmark_id",
        "dataset_a_id",
        "dataset_b_id",
        "tmsi_a",
        "tmsi_b",
        "absolute_difference",
        "relative_difference",
        "extent_km",
        "overlap_status",
        "methodology_version",
        "warnings",
        "created_at",
    ]

    # Generate a benchmark_id if not present in the result
    bid = tmsi_result.get("benchmark_id", generate_benchmark_id())

    row = {
        "benchmark_id": bid,
        "dataset_a_id": tmsi_result.get("dataset_a_id", ""),
        "dataset_b_id": tmsi_result.get("dataset_b_id", ""),
        "tmsi_a": tmsi_result.get("tmsi_a", ""),
        "tmsi_b": tmsi_result.get("tmsi_b", ""),
        "absolute_difference": tmsi_result.get("absolute_difference", ""),
        "relative_difference": tmsi_result.get("relative_difference", ""),
        "extent_km": tmsi_result.get("extent_km", ""),
        "overlap_status": tmsi_result.get("overlap_status", ""),
        "methodology_version": tmsi_result.get("methodology_version", ""),
        "warnings": "; ".join(tmsi_result.get("warnings", [])),
        "created_at": tmsi_result.get("created_at", ""),
    }

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)