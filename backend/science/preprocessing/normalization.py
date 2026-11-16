"""Optional within-dataset normalization utilities; not used for cross-body scores."""

import numpy as np


def min_max_normalize(values: np.ndarray, valid_mask: np.ndarray) -> np.ndarray:
    """Normalize valid values to [0, 1], preserving invalid cells as NaN."""
    if values.shape != valid_mask.shape:
        raise ValueError("Values and valid mask must have identical shapes")
    valid_values = values[valid_mask]
    if valid_values.size == 0:
        raise ValueError("Cannot normalize an array with no valid values")
    minimum = float(valid_values.min())
    maximum = float(valid_values.max())
    result = np.full(values.shape, np.nan, dtype=np.float32)
    if maximum == minimum:
        result[valid_mask] = 0.0
    else:
        result[valid_mask] = ((values[valid_mask] - minimum) / (maximum - minimum)).astype(np.float32)
    return result