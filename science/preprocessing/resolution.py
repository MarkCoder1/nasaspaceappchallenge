"""Resolution decisions for planetary rasters."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResolutionDecision:
    original_resolution_m: tuple[float, float]
    processed_resolution_m: tuple[float, float]
    resampled: bool
    method: str
    rationale: str


def preserve_native_resolution(resolution: tuple[float, float]) -> ResolutionDecision:
    return ResolutionDecision(
        original_resolution_m=resolution,
        processed_resolution_m=resolution,
        resampled=False,
        method="none",
        rationale="The only verified input is processed at native 20 m spacing; no unsupported detail is introduced.",
    )