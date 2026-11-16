# Phase 11 TMSI Interpretation Report (Experiment F)

## Objective
Determine what TMSI actually measures: pairwise terrain-window similarity, broader
terrain-region similarity, or planetary-body similarity. Tested against evidence from
Experiments A–D.

## Evidence reviewed

| Source | Finding |
|---|---|
| Experiment A (within-body) | Moon TMSI 29.27–94.10; Mars 40.99–90.90; means nearly identical (60.51 vs 61.28) |
| Experiment B (between-body) | Moon–Mars TMSI 22.38–90.60, mean 46.85; fully overlaps within-body distributions |
| Experiment C (overlap bias) | Identical windows → 100.0; high overlap → 78.6–88.0; non-overlap → 15.8–70.1 |
| Phase 10 (extent) | TMSI 23.71 (5.12 km) → 49.92 (full extent); ~26-point shift across extents |
| Phase 10 (baseline) | Moon–Mars full extent TMSI = 49.9229, confidence HIGH |

## Evaluation of candidate interpretations

### 1. "TMSI indicates planetary-body similarity"
**Not supported.** Within-body variation (Moon 29.27–94.10) is comparable to or greater than
between-body variation (22.38–90.60). The Moon–Mars baseline (49.92) falls within both
within-body distributions. A TMSI score cannot tell you whether a comparison is within-body
or between-body.

### 2. "TMSI measures broader terrain-region similarity"
**Not supported at current extents.** Score changes ~26 points when extent changes from 5.12 km
to full extent (Phase 10). Two windows of the same body can score 29.27 or 94.10 (Experiment A).
There is no stable "region-level" score without fixing extent and window location.

### 3. "TMSI is a pairwise terrain-window morphology similarity index"
**Supported.** TMSI quantifies distribution similarity of slope, local relief, and TRI between
two specific terrain windows at a specified extent. This is exactly what the formula computes
and what the experiments confirm. It is reproducible (Phase 9/11: baseline reproduced exactly)
and bounded (0–100), but its value is contingent on extent, window location, and overlap.

## What TMSI does NOT measure
- Not a probability (explicitly stated in limitations).
- Not a habitability or landing-safety score.
- Not geological equivalence.
- Not a planetary-body identifier.
- Not robust to extent or window-location changes.

## Recommended interpretation
TMSI = 100 × exp(−D) is a **pairwise terrain-window morphology similarity index** whose value
depends on:
1. Spatial extent (window size),
2. Window location within each body,
3. Overlap between windows (must be non-overlapping for independent comparisons),
4. Feature weighting (default equal),
5. Effective resolution (must pass compatibility gate, max ratio 4.0).

Any scientific claim using TMSI must report all five factors. A single TMSI score without
extent/location/coverage metadata is not interpretable.
