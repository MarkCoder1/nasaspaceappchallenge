# Phase 11 Between-Body Variability Report (Experiment B)

## Objective
Compare multiple Mars windows against multiple Moon windows to build a cross-body
TMSI distribution, rather than relying on one selected pair. Tests whether cross-body
scores are separable from within-body scores.

## Method
- Mars: 6 non-overlapping 10.24 km windows.
- Moon: 16 non-overlapping 10.24 km windows.
- 6 × 16 = 96 cross-body comparisons.
- Equal weights, TMSI = 100 × exp(−D).
- Windows are reused across comparisons → not statistically independent (documented limitation).
- Output: `data/metadata/phase11_sampling_framework.json`.

## Results

| Statistic | Value |
|---|---|
| Comparisons | 96 |
| TMSI min | 22.3777 |
| TMSI max | 90.6029 |
| TMSI mean | 46.8493 |

## Comparison with within-body and reference

| Distribution | TMSI min | TMSI max | TMSI mean |
|---|---|---|---|
| Within-body Mars | 40.9877 | 90.8955 | 61.2785 |
| Within-body Moon | 29.2689 | 94.1007 | 60.5127 |
| Between-body Moon–Mars | 22.3777 | 90.6029 | 46.8493 |
| Cross-body baseline (full extent) | 49.9229 | 49.9229 | 49.9229 |

## Key findings
1. **Between-body TMSI range (22.38–90.60) nearly spans the full 0–100 index.**
2. **The between-body distribution fully overlaps both within-body distributions.** A between-body score of 49.92 (the baseline) is indistinguishable from many within-body scores.
3. **The minimum between-body score (22.38) is lower than the minimum within-body Moon score (29.27), but the distributions overlap substantially.**
4. **No separation exists:** knowing a TMSI score does not tell you whether the comparison is within-body or between-body.

## Conclusion
Cross-body comparisons are not separable from within-body comparisons at 10.24 km extent. The Moon–Mars baseline (49.92) sits in the middle of the between-body distribution and within both within-body distributions. TMSI measures pairwise window morphology similarity, not planetary-body difference.
