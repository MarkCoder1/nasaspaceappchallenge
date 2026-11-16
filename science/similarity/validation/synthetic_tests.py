"""Small mathematical sanity checks used by automated tests."""

import numpy as np

from ..comparison.distance import compare_distributions


def identical_distributions_have_zero_distance() -> bool:
    distance = compare_distributions(np.array([1.0, 2.0]), np.array([1.0, 2.0]))
    return distance.wasserstein == 0.0 and distance.ks_statistic == 0.0