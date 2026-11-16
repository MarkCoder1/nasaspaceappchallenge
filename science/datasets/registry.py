"""Dataset registry for Phase 13 benchmarking.

Reads :file:`registry.json` and provides functions for filtering,
accessing, and validating datasets.

Never mark a dataset VALIDATED merely because a download succeeded.
Never fabricate dataset identifiers or observational data.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE = Path(__file__).resolve().parent / "registry.json"


def _load() -> dict:
    """Load the registry JSON."""
    if not BASE.is_file():
        return {"datasets": []}
    return json.loads(BASE.read_text(encoding="utf-8"))


def list_datasets(
    body: Optional[str] = None,
    validation_status: Optional[str] = None,
    access_status: Optional[str] = None,
    kind: Optional[str] = None,
) -> List[dict]:
    """Return datasets matching the given filters."""
    registry = _load()
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
    registry = _load()
    for d in registry.get("datasets", []):
        if d.get("id") == dataset_id:
            return d
    return None


def within_body_datasets(body: str) -> List[dict]:
    """Return all VALIDATED datasets for a given planetary body."""
    return list_datasets(body=body, validation_status="VALIDATED")


def accessible_datasets(body: str) -> List[dict]:
    """Return all ACCESSIBLE/DOWNLOADED datasets for a given body,
    excluding BLOCKED ones (e.g. Earth NASADEM without auth)."""
    return list_datasets(
        body=body,
        access_status="DOWNLOADED",
    )


def get_dataset(dataset_id: str) -> Optional[dict]:
    """Return the dataset dict matching *dataset_id*, or None."""
    registry = _load()
    for d in registry.get("datasets", []):
        if d.get("id") == dataset_id:
            return d
    return None


def within_body_datasets(body: str) -> List[dict]:
    """Return all VALIDATED datasets for a given planetary body."""
    return list_datasets(body=body, validation_status="VALIDATED")


def accessible_datasets(body: str) -> List[dict]:
    """Return all ACCESSIBLE/DOWNLOADED datasets for a given body,
    excluding BLOCKED ones (e.g. Earth NASADEM without auth)."""
    return list_datasets(
        body=body,
        access_status="DOWNLOADED",
    )



def get_candidate(candidate_id: str) -> Optional[dict]:
    """Return the candidate dict matching *candidate_id*, or None."""
    registry = _load()
    for c in registry.get("candidates", {}).get("list", []):
        if c.get("id") == candidate_id:
            return c
    return None



def list_candidates(
    status: Optional[str] = None,
    environment: Optional[str] = None,
    planetary_target: Optional[str] = None,
) -> List[dict]:
    """Return candidates matching the given filters."""
    registry = _load()
    candidates = registry.get("candidates", {}).get("list", [])
    filtered = candidates
    if status is not None:
        filtered = [c for c in filtered if c.get("status") == status]
    if environment is not None:
        filtered = [c for c in filtered if c.get("environment_classification") == environment]
    if planetary_target is not None:
        filtered = [c for c in filtered if c.get("planetary_relevance") == planetary_target]
    return filtered


def within_body_candidates(planetary_target: str) -> List[dict]:
    """Return candidates relevant to the given planetary target (Moon or Mars)."""
    return list_candidates(planetary_target=planetary_target)


def accessible_candidates() -> List[dict]:
    """Return candidates with status DATA_AVAILABLE or READY_FOR_COMPARISON."""
    return list_candidates(status="DATA_AVAILABLE") + list_candidates(status="READY_FOR_COMPARISON")


def candidate_status_counts() -> dict:
    """Return counts of candidates by status."""
    registry = _load()
    counts: dict = {"CANDIDATE": 0, "SOURCE_VERIFIED": 0, "DATA_AVAILABLE": 0, "READY_FOR_COMPARISON": 0}
    for c in registry.get("candidates", {}).get("list", []):
        s = c.get("status", "CANDIDATE")
        if s in counts:
            counts[s] += 1
    return counts


def candidates() -> List[dict]:
    """Return all Earth candidates from the registry."""
    registry = _load()
    return registry.get("candidates", {}).get("list", [])
def earth_blocked() -> bool:
    """Return True if Earth has no VALIDATED/DOWNLOADED datasets."""
    return not any(
        d.get("body") == "Earth"
        and d.get("validation_status") in ("VALIDATED", "DOWNLOADED")
        for d in _load().get("datasets", [])
    )


def candidate_eligible_for_evaluation(candidate_id: str) -> bool:
    """Return True if a candidate may enter the quantitative comparison workflow.

    In Phase 19, only candidates with status READY_FOR_COMPARISON may proceed.
    Unvalidated candidates must not receive quantitative Earth--Moon/Mars similarity scoring.
    This function enforces that constraint.
    """
    c = get_candidate(candidate_id)
    if c is None:
        return False
    return c.get("status") == "READY_FOR_COMPARISON"


def candidate_status_counts() -> dict:
    """Return counts of candidates by status."""
    registry = _load()
    counts: dict = {"CANDIDATE": 0, "SOURCE_VERIFIED": 0, "DATA_AVAILABLE": 0, "READY_FOR_COMPARISON": 0}
    for c in registry.get("candidates", {}).get("list", []):
        s = c.get("status", "CANDIDATE")
        if s in counts:
            counts[s] += 1
    return counts


def update_candidate_status(candidate_id: str, new_status: str) -> bool:
    """Attempt to transition a candidate to a new status.

    Only allowed transitions in Phase 19:
    - CANDIDATE -> SOURCE_VERIFIED (when source is documented and verified)
    - SOURCE_VERIFIED -> DATA_AVAILABLE (when DEM is acquired and validated)
    - DATA_AVAILABLE -> READY_FOR_COMPARISON (when candidate is prepared for Phase 20)

    Returns True on success, False if the transition is not allowed.
    """
    registry = _load()
    candidates_list = registry.get("candidates", {}).get("list", [])
    for c in candidates_list:
        if c.get("id") == candidate_id:
            current = c.get("status", "CANDIDATE")
            # Define allowed transitions
            allowed = {
                "CANDIDATE": ["SOURCE_VERIFIED"],
                "SOURCE_VERIFIED": ["DATA_AVAILABLE"],
                "DATA_AVAILABLE": ["READY_FOR_COMPARISON"],
                "READY_FOR_COMPARISON": [],  # terminal status in Phase 19
            }
            if new_status not in allowed.get(current, []):
                return False
            c["status"] = new_status
            c["last_updated"] = "__UPDATE_TIMESTAMP__"  # placeholder; real system uses ISO timestamp
            # Update counts
            counts = registry.get("candidates", {}).get("by_status", {})
            counts[current] = max(0, counts.get(current, 0) - 1)
            counts[new_status] = counts.get(new_status, 0) + 1
            registry["candidates"]["by_status"] = counts
            BASE.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
            return True
    return False


def add_candidate(candidate: dict) -> bool:
    """Add a new candidate to the registry.

    Requires: candidate ID must be unique; all required fields must be populated.
    Returns True on success, False if the candidate ID already exists.
    """
    registry = _load()
    candidates_list = registry.get("candidates", {}).get("list", [])
    # Check for duplicate ID
    if any(c.get("id") == candidate.get("id") for c in candidates_list):
        return False
    # Set default count
    registry["candidates"]["count"] = registry.get("candidates", {}).get("count", 0) + 1
    # Initialize status counts if needed
    if registry.get("candidates", {}).get("by_status") is None:
        registry["candidates"]["by_status"] = {"CANDIDATE": 0, "SOURCE_VERIFIED": 0, "DATA_AVAILABLE": 0, "READY_FOR_COMPARISON": 0}
    # Ensure status is one of the allowed values
    if candidate.get("status") not in ("CANDIDATE", "SOURCE_VERIFIED", "DATA_AVAILABLE", "READY_FOR_COMPARISON"):
        candidate["status"] = "CANDIDATE"
    candidates_list.append(candidate)
    registry["candidates"]["list"] = candidates_list
    # Update counts
    status = candidate.get("status", "CANDIDATE")
    counts = registry.get("candidates", {}).get("by_status", {})
    counts[status] = counts.get(status, 0) + 1
    registry["candidates"]["by_status"] = counts
    BASE.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return True


def candidate_eligible_for_evaluation(candidate_id: str) -> bool:
    """Return True if a candidate may enter the quantitative comparison workflow.

    In Phase 19, only candidates with status READY_FOR_COMPARISON may proceed.
    Unvalidated candidates must not receive quantitative Earth--Moon/Mars similarity scoring.
    """
    c = get_candidate(candidate_id)
    if c is None:
        return False
    return c.get("status") == "READY_FOR_COMPARISON"
    return False


def add_candidate(candidate: dict) -> bool:
    """Add a new candidate to the registry.

    Requires: candidate ID must be unique; all required fields must be populated.
    Returns True on success, False if the candidate ID already exists.
    """
    registry = _load()
    candidates_list = registry.get("candidates", {}).get("list", [])
    # Check for duplicate ID
    if any(c.get("id") == candidate.get("id") for c in candidates_list):
        return False
    # Set default count
    registry["candidates"]["count"] = registry.get("candidates", {}).get("count", 0) + 1
    # Initialize status counts if needed
    if registry.get("candidates", {}).get("by_status") is None:
        registry["candidates"]["by_status"] = {"CANDIDATE": 0, "SOURCE_VERIFIED": 0, "DATA_AVAILABLE": 0, "READY_FOR_COMPARISON": 0}
    # Ensure status is one of the allowed values
    if candidate.get("status") not in ("CANDIDATE", "SOURCE_VERIFIED", "DATA_AVAILABLE", "READY_FOR_COMPARISON"):
        candidate["status"] = "CANDIDATE"
    candidates_list.append(candidate)
    registry["candidates"]["list"] = candidates_list
    # Update counts
    status = candidate.get("status", "CANDIDATE")
    counts = registry.get("candidates", {}).get("by_status", {})
    counts[status] = counts.get(status, 0) + 1
    registry["candidates"]["by_status"] = counts
    BASE.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return True


def metadata_compatibility(a_id: str, b_id: str) -> dict:
    """Check whether two datasets have compatible metadata for benchmarking.

    Returns a dict with keys:
    - compatible: bool
    - reasons: list of str
    - warnings: list of str
    """
    from science.benchmarking.dataset_validator import validate_dataset

    a = get_dataset(a_id)
    b = get_dataset(b_id)
    if a is None or b is None:
        return {
            "compatible": False,
            "reasons": [f"Dataset not found: a_id={a_id}, b_id={b_id}"],
            "warnings": [],
        }

    # Use the shared validator logic plus body check
    a_check = validate_dataset(a)
    b_check = validate_dataset(b)

    reasons: List[str] = []
    warnings: List[str] = []

    # Check same planetary body
    if a.get("body") != b.get("body"):
        reasons.append(f"Different bodies: {a.get('body')} vs {b.get('body')}")
        warnings.append(
            "TMSI comparisons across different planetary bodies are not scientifically meaningful; "
            "only within-body comparisons are valid."
        )

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

    # Incorporate validator warnings
    all_warnings = warnings + a_check.get("warnings", []) + b_check.get("warnings", [])

    return {
        "compatible": compatible,
        "reasons": reasons,
        "warnings": all_warnings,
    }