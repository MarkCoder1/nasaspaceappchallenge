"""Distribution distances used by the terrain morphology comparison."""

from dataclasses import dataclass

import numpy as np
from scipy.stats import ks_2samp, wasserstein_distance


@dataclass(frozen=True)
class DistributionDistance:
    wasserstein: float
    ks_statistic: float
    ks_pvalue: float
    pooled_iqr: float
    normalized_distance: float
    sample_count_target: int
    sample_count_candidate: int


def _sample(values: np.ndarray, maximum: int = 100_000) -> np.ndarray:
    valid = values[np.isfinite(values)].astype(np.float64, copy=False)
    if valid.size <= maximum:
        return valid
    indices = np.linspace(0, valid.size - 1, maximum, dtype=np.int64)
    return valid[indices]


def compare_distributions(target: np.ndarray, candidate: np.ndarray) -> DistributionDistance:
    target_values = _sample(target)
    candidate_values = _sample(candidate)
    if target_values.size == 0 or candidate_values.size == 0:
        raise ValueError("Both distributions need at least one valid value")
    wasserstein = float(wasserstein_distance(target_values, candidate_values))
    ks = ks_2samp(target_values, candidate_values, method="auto")
    pooled_iqr = float(max(np.percentile(target_values, 75) - np.percentile(target_values, 25), np.percentile(candidate_values, 75) - np.percentile(candidate_values, 25)))
    scale = max(pooled_iqr, np.finfo(np.float64).eps)
    return DistributionDistance(
        wasserstein=wasserstein,
        ks_statistic=float(ks.statistic),
        ks_pvalue=float(ks.pvalue),
        pooled_iqr=pooled_iqr,
        normalized_distance=wasserstein / scale,
        sample_count_target=int(target_values.size),
        sample_count_candidate=int(candidate_values.size),
    )