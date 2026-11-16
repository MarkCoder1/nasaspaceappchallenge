"""Provenance metadata helpers for acquired files."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .dataset_catalog import DatasetSpec


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_acquisition_metadata(
    dataset: DatasetSpec,
    file_path: Path,
    metadata_dir: Path,
    source_url: str,
) -> Path:
    metadata_dir.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "dataset": dataset.id,
        "name": dataset.name,
        "planet": dataset.planet,
        "institution": dataset.institution,
        "official_url": dataset.official_url,
        "source_url": source_url,
        "local_file": str(file_path),
        "file_size_bytes": file_path.stat().st_size,
        "sha256": sha256_file(file_path),
        "acquired_at_utc": datetime.now(timezone.utc).isoformat(),
        "variable": dataset.variable,
        "units": dataset.units,
        "resolution": dataset.resolution,
        "format": dataset.format,
        "coverage": dataset.coverage,
        "limitations": dataset.limitations,
    }
    output = metadata_dir / f"{dataset.id}.json"
    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return output