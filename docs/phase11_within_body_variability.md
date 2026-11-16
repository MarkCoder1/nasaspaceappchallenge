# Phase 11 Within-Body Variability Report (Experiment A)

## Objective
Quantify how much TMSI varies when comparing different non-overlapping terrain windows
within the same planetary body. Tests the proposition that TMSI identifies body identity
by measuring within-body score spread.

## Method
- Mars: 6 non-overlapping 10.24 km windows (512 × 512 cells at 20 m), 15 pairwise comparisons.
- Moon: 16 non-overlapping 10.24 km windows, 120 pairwise comparisons.
- Equal weights (slope = local_relief = terrain_ruggedness = 1.0).
- TMSI = 100 × exp(−D), Wasserstein + pooled-IQR normalization.
- All windows non-overlapping within each body (no overlap bias).
- Output: `data/metadata/phase11_sampling_framework.json`.

## Results

| Body | Comparisons | TMSI min | TMSI max | TMSI mean | Range |
|---|---|---|---|---|---|
| Mars | 15 | 40.9877 | 90.8955 | 61.2785 | 49.9077 |
| Moon | 120 | 29.2689 | 94.1007 | 60.5127 | 64.8318 |

## Key findings
1. **Within-body TMSI varies enormously.** Moon spans 29.27–94.10 (64.83-point range); Mars spans 40.99–90.90 (49.91-point range).
2. **Within-body means are similar** (Mars 61.28, Moon 60.51) — no systematic body-level offset.
3. **Within-body ranges overlap completely** and both exceed the cross-body Moon–Mars baseline range.
4. Two different windows of the Moon can be as dissimilar as TMSI 29.27 or as similar as 94.10 — purely due to sampling location.

## Conclusion
Within-body terrain variability is large and swamps any between-body signal. TMSI cannot be interpreted as a planetary-body similarity indicator based on these data.
