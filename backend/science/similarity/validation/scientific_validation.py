"""Validation rules that prevent unsupported production comparisons."""


def require_production_ready(*, earth_validated: bool, moon_validated: bool, mars_validated: bool) -> None:
    if not mars_validated:
        raise ValueError("A validated Mars target is required")
    if not earth_validated and not moon_validated:
        raise ValueError("No validated Earth or lunar candidate is available")