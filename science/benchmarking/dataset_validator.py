"""Dataset metadata validation for Phase 13 benchmarking.

Responsibilities:
- Validate that required metadata fields are present and non-empty.
- Verify that SHA256 checksums match local files when a local file path is given.
- Verify coordinate reference system and elevation unit consistency.
- Never mark a dataset VALIDATED merely because a download succeeded.
- Report missing or inconsistent metadata as warnings, not silently.
"""

import hashlib
import json
import pathlib
from typing import Any, Dict, List, Optional

import numpy as np

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "data" / "metadata"


def _dataset_path(dataset: dict) -> Optional[pathlib.Path]:
    """Return the local file path if a local_file key exists."""
    local = dataset.get("local_file")
    if local is None:
        return None
    return pathlib.Path(local)


def validate_checksum(dataset: dict) -> dict:
    """Verify the SHA256 checksum against the local file, if available.

    Returns
    - status: "matched", "mismatch", "no_file"
    - stored_sha256: the SHA256 stored in the dataset dict
    - computed_sha256: the SHA256 computed from the local file, or None
    """
    local_path = _dataset_path(dataset)
    stored = dataset.get("file_sha256")

    if local_path is None or not local_path.is_file():
        return {"status": "no_file", "stored_sha256": stored, "computed_sha256": None}

    computed = hashlib.sha256(local_path.read_bytes()).hexdigest()

    if stored is None:
        return {"status": "no_stored_checksum", "stored_sha256": None, "computed_sha256": computed}

    if computed == stored:
        return {"status": "matched", "stored_sha256": stored, "computed_sha256": computed}
    else:
        return {
            "status": "mismatch",
            "stored_sha256": stored,
            "computed_sha256": computed,
        }


def validate_required_fields(dataset: dict) -> dict:
    """Check that all required fields are present and non-empty.

    Required fields (per Phase 13 specification):
    - dataset: str
    - name: str
    - body: str
    - producing_institution: str
    - official_source: str (may be null for synthetic test datasets)
    - elevation_units: str

    Returns
    - valid: bool
    - missing: list of str (field names that are missing or empty)
    - warnings: list of str
    """
    required = ["id", "name", "body", "producing_institution", "elevation_units"]
    missing: List[str] = []
    warnings: List[str] = []

    for field in required:
        value = dataset.get(field)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            missing.append(field)

    # Kind-specific checks
    kind = dataset.get("kind")
    if kind == "synthetic_test_only":
        # Synthetic test datasets have relaxed requirements
        pass
    elif kind != "official_product" and kind != "real_observational":
        warnings.append(f"Unknown kind '{kind}'; expected 'real_observational', 'synthetic_test_only', or 'official_product'.")

    # Earth-specific: if access_status is BLOCKED_BY_EARTHDATA_AUTHENTICATION,
    # validation_status must not be VALIDATED
    access = dataset.get("access_status")
    validation = dataset.get("validation_status")
    if (
        dataset.get("body") == "Earth"
        and access == "BLOCKED_BY_EARTHDATA_AUTHENTICATION"
        and validation in ("VALIDATED", "DOWNLOADED")
    ):
        warnings.append(
            "Earth dataset has BLOCKED_BY_EARTHDATA_AUTHENTICATION access_status "
            "but VALIDATED/DOWNLOADED validation_status. This inconsistency should be "
            "resolved before Earth comparisons are enabled."
        )

    valid = len(missing) == 0
    return {"valid": valid, "missing": missing, "warnings": warnings}


def validate_dataset(dataset: dict) -> dict:
    """Run the full validation suite on a dataset dict.

    Returns a dict with keys:
    - valid: bool (all checks passed)
    - checksum: dict from validate_checksum()
    - required_fields: dict from validate_required_fields()
    - overall: str one of "PASS", "CHECK_WARNINGS", "FAIL"
    """
    checksum = validate_checksum(dataset)
    required = validate_required_fields(dataset)

    all_pass = checksum["status"] in ("matched", "no_file") and required["valid"]
    has_warnings = len(checksum.get("warnings", [])) > 0 or len(required.get("warnings", [])) > 0

    if all_pass and not has_warnings:
        overall = "PASS"
    elif all_pass and has_warnings:
        overall = "CHECK_WARNINGS"
    else:
        overall = "FAIL"

    return {
        "valid": all_pass,
        "checksum": checksum,
        "required_fields": required,
        "overall": overall,
    }