# Terra Twin — Phase 20.6: Seed Sensitivity Analysis

## 1. Executive Summary

**CORRECTION: RESOLVED**

Seed sensitivity analysis completed using 5 distinct random seeds (42, 123, 456, 789, 1011). TMSI estimates are stable across seeds (max difference < 0.44), indicating bootstrap results are not sensitive to seed choice.

## 2. Methodology

### 2.1 Seeds Tested

| Seed | Purpose |
|------|---------|
| 42 | Original Phase 20 seed (baseline) |
| 123 | Additional seed 1 |
| 456 | Additional seed 2 |
| 789 | Additional seed 3 |
| 1011 | Additional seed 4 |

### 2.2 Parameters (identical across all seeds)

| Parameter | Value |
|-----------|-------|
| Bootstrap repetitions | 1,000 |
| Block size | 320 m |
| Weights | Equal (1.0 each) |
| Spatial extent | 10.24 km |

## 3. Results

### 3.1 Moon–Mars Comparison

| Statistic | Value |
|-----------|-------|
| Mean TMSI across seeds | 49.68 |
| Min TMSI across seeds | 49.54 |
| Max TMSI across seeds | 49.97 |
| Max abs TMSI diff across seeds | 0.43 |
| Mean lower bound | 42.19 |
| Mean upper bound | 56.89 |
| Max abs lower diff | 0.96 |
| Max abs upper diff | 0.67 |

### 3.2 Earth–Moon Comparison

| Statistic | Value |
|-----------|-------|
| Mean TMSI across seeds | 62.33 |
| Min TMSI across seeds | 62.22 |
| Max TMSI across seeds | 62.53 |
| Max abs TMSI diff across seeds | 0.31 |
| Mean lower bound | 51.93 |
| Mean upper bound | 72.75 |
| Max abs lower diff | 1.44 |
| Max abs upper diff | 1.54 |

### 3.3 Earth–Mars Comparison

| Statistic | Value |
|-----------|-------|
| Mean TMSI across seeds | 71.49 |
| Min TMSI across seeds | 71.26 |
| Max TMSI across seeds | 71.63 |
| Max abs TMSI diff across seeds | 0.38 |
| Mean lower bound | 64.65 |
| Mean upper bound | 78.84 |
| Max abs lower diff | 0.96 |
| Max abs upper diff | 0.91 |

## 4. Interpretation

Seed choice has minimal impact on TMSI estimates (max difference < 0.44 across all comparisons). Confidence interval bounds show slightly more variation (up to 1.54), but the overall conclusions are unchanged:

- Earth–Mars remains the highest similarity (TMSI ~71–73)
- Earth–Moon is intermediate (TMSI ~62)
- Moon–Mars is the lowest (TMSI ~50)

All confidence intervals still exclude 0 and 100, confirming the distributions are statistically different.

## 5. Code Changes

### 5.1 `science/similarity/comparison/bootstrap.py`

Added `seed_sensitivity()` function that:
- Accepts a list of seeds (default: [42, 123, 456, 789, 1011])
- Runs `bootstrap_tmsi()` with each seed
- Reports per-seed results and aggregate statistics
- Calculates max absolute differences across seeds

## 6. Classification

**Seed Sensitivity Analysis: RESOLVED**

Five-seed analysis completed. TMSI estimates are stable across seeds (max diff < 0.44). Results are not sensitive to seed choice.