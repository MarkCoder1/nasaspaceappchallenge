"""Dataset loading and registry access for Phase 13 benchmarking.

Responsibilities:
- Load datasets from science/datasets/registry.json
- Filter by planetary body, validation status, and access status
- Provide metadata summaries for comparison eligibility
- Never fabricate or invent dataset identifiers
- Never mark a dataset VALIDATED merely because a download succeeded
"""

import json
import pathlib
from typing import Any, Dict, List, Optional

import numpy as np

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "data" / "metadata"


def _load_registry() -> dict:
    """Load the dataset registry from science/datasets/registry.json."""
    registry_path = pathlib.Path(__file__).resolve().parent / "registry.json"
    if not registry_path.is_file():
        return {"datasets": []}
    return json.loads(registry_path.read_text(encoding="utf-8"))


def list_datasets(
    body: Optional[str] = None,
    validation_status: Optional[str] = None,
    access_status: Optional[str] = None,
    kind: Optional[str] = None,
) -> List[dict]:
    """Return datasets matching the given filters.

    Parameters
    body: Planetary body ("Earth", "Moon", "Mars").
    validation_status: One of "VALIDATED", "REJECTED", "BLOCKED", etc.
    access_status: One of "DOWNLOADED", "ACCESSIBLE", "BLOCKED_BY_EARTHDATA_AUTHENTICATION", etc.
    kind: One of "real_observational", "synthetic_test_only", "official_product".

    Returns
    List of dataset dicts from the registry.
    """
    registry = _load_registry()
    datasets = registry.get("datasets", [])

    filtered = datasets
    if body is not None:
        filtered = [d for d in filtered if d.get("body") == body]
    if validation_status is not None:
        filtered = [d for d in filtered if d.get("validation_status") == validation_status]
    if access_status is not None:
        filtered = [d for d in filtered if d.get("access_status") == access_status]
    if kind is not None:
        filtered = [d for d in filtered if d.get("kind") == kind]

    return filtered


def get_dataset(dataset_id: str) -> Optional[dict]:
    """Return the dataset dict matching *dataset_id*, or None."""
    registry = _load_registry()
    for d in registry.get("datasets", []):
        if d.get("id") == dataset_id:
            return d
    return None


def within_body_datasets(body: str) -> List[dict]:
    """Return all VALIDATED datasets for a given planetary body.

    This is used to identify candidate datasets for within-body
    benchmarking (Phase 12 finding: TMSI is extent-sensitive but
    reproducible within a single DEM source).
    """
    return list_datasets(body=body, validation_status="VALIDATED")


def accessible_datasets(body: str) -> List[dict]:
    """Return all ACCESSIBLE/DOWNLOADED datasets for a given body,
    excluding BLOCKED ones (e.g. Earth NASADEM without auth).
    """
    return list_datasets(
        body=body,
        access_status="DOWNLOADED",
    )


def earth_blocked() -> bool:
    """Return True if Earth has no VALIDATED/DOWNLOADED datasets.

    This gate is used by the ResearchWorkbench to return HTTP 409
    when Earth comparisons are requested.
    """
    return not any(
        d.get("body") == "Earth"
        and d.get("validation_status") in ("VALIDATED", "DOWNLOADED")
        for d in _load_registry().get("datasets", [])
    )


def metadata_compatibility(a_id: str, b_id: str) -> dict:
    """Check whether two datasets have compatible metadata for benchmarking.

    Returns a dict with keys:
    - compatible: bool
    - reasons: list of str
    - warnings: list of str
    """
    a = get_dataset(a_id)
    b = get_dataset(b_id)
    if a is None or b is None:
        return {
            "compatible": False,
            "reasons": [f"Dataset not found: a_id={a_id}, b_id={b_id}"],
            "warnings": [],
        }

    reasons: List[str] = []
    warnings: List[str] = []

    # Check same planetary body
    if a.get("body") != b.get("body"):
        reasons.append(f"Different bodies: {a.get('body')} vs {b.get('body')}")
        warnings.append("TMSI comparisons across different planetary bodies are not scientifically meaningful; only within-body comparisons are valid.")

    # Check elevation units match
    a_units = a.get("elevation_units")
    b_units = b.get("elevation_units")
    if a_units is not None and b_units is not None and a_units != b_units:
        reasons.append(f"Different elevation units: {a_units} vs {b_units}")
        warnings.append("Elevation unit mismatch may affect TMSI and terrain metric calculations.")

    # Check nominal resolution
    a_res = a.get("nominal_resolution")
    b_res = b.get("nominal_resolution")
    if a_res is not None and b_res is not None and a_res != b_res:
        reasons.append(f"Different nominal resolutions: {a_res} vs {b_res}")
        warnings.append("Resolution difference is expected; benchmark should document and evaluate resolution sensitivity.")

    # Check vertical reference systems
    a_vref = a.get("vertical_reference_system")
    b_vref = b.get("vertical_reference_system")
    if a_vref is not None and b_vref is not None and a_vref != b_vref:
        reasons.append(f"Different vertical reference systems: {a_vref} vs {b_vref}")
        warnings.append("Vertical reference mismatch may affect slope and relief calculations.")

    compatible = len(reasons) == 0 or len([r for r in reasons if "Different bodies" not in r]) == 0
    # If the only difference is body, they're inherently not comparable for TMSI
    if any("Different bodies" in r for r in reasons):
        compatible = False

    return {
        "compatible": compatible,
        "reasons": reasons,
        "warnings": warnings,
    }