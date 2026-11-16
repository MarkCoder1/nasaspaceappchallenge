"""Feature-weight configuration."""

DEFAULT_WEIGHTS: dict[str, float] = {
    "slope": 1.0,
    "local_relief": 1.0,
    "terrain_ruggedness": 1.0,
}


def validate_weights(weights: dict[str, float] | None = None) -> dict[str, float]:
    chosen = dict(DEFAULT_WEIGHTS if weights is None else weights)
    if not chosen or any(value < 0 for value in chosen.values()) or sum(chosen.values()) <= 0:
        raise ValueError("Weights must contain at least one non-negative value with a positive sum")
    return chosen