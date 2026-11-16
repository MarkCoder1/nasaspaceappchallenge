# Terra Twin — Phase 20.6: Bootstrap Expansion

## 1. Executive Summary

**CORRECTION: RESOLVED**

Bootstrap repetitions increased from 64 to 1,000 for stable confidence interval estimation. The default `repetitions` parameter in `bootstrap_tmsi()` now defaults to 1,000.

## 2. Configuration Change

| Parameter | Phase 20 Value | Phase 20.6 Value |
|-----------|---------------|------------------|
| Bootstrap repetitions | 64 | 1,000 |
| Random seed | 42 | 42 (preserved) |
| Block size | 320 m | 320 m (preserved) |
| Resampling method | Spatial block bootstrap | Spatial block bootstrap (preserved) |

## 3. Code Changes

### 3.1 `science/similarity/comparison/bootstrap.py`

Changed the default `repetitions` parameter from 64 to 1,000:

```python
def bootstrap_tmsi(
    target: TerrainFeatureSet,
    candidate: TerrainFeatureSet,
    weights: dict[str, float],
    *,
    block_size_m: float = 320.0,
    repetitions: int = 1000,   # was 64
    seed: int = 42,
) -> dict[str, Any]:
```

The `block_size_sensitivity()` function also updated to use 1,000 repetitions for consistency.

## 4. Recalculated Results

| Comparison | Phase 20 CI (64 reps) | Phase 20.6 CI (1,000 reps) | TMSI Change |
|------------|----------------------|----------------------------|-------------|
| Moon–Mars | [43.72, 56.80] | [42.69, 56.92] | 49.92 → 49.92 (identical) |
| Earth–Moon | [53.23, 74.81] | [51.99, 72.56] | 61.95 → 61.95 (identical) |
| Earth–Mars | [65.41, 78.40] | [64.99, 78.55] | 73.14 → 73.14 (identical) |

TMSI values are identical (deterministic). Confidence intervals shifted slightly due to increased repetitions, reflecting more stable quantile estimation.

## 5. Recorded Metadata

Each bootstrap result now records:
- Number of repetitions: 1,000
- Random seed: 42
- Resampling method: non-overlapping spatial block bootstrap with replacement
- Block size: 320 m
- Confidence level: 95% (2.5th–97.5th percentiles)
- Confidence interval method: percentile method

## 6. Important Distinction

Increased repetitions do NOT constitute increased sample size or additional independent observations. The bootstrap resamples from the same spatial blocks; more repetitions only improve the precision of the quantile estimation, not the underlying data quantity.

## 7. Classification

**Bootstrap Expansion: RESOLVED**

Bootstrap repetitions increased from 64 to 1,000. All metadata recorded. TMSI values unchanged. Confidence intervals slightly adjusted to reflect more stable estimation.