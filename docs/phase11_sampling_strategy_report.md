# Phase 11 Sampling Strategy Comparison Report (Experiment E)

## Objective
Evaluate candidate sampling strategies for planetary terrain comparison and recommend
one only where supported by evidence. Experimental strategies are kept separate from
the official TMSI baseline.

## Strategies evaluated

### A. Single fixed-area window
- **Rationale:** Simple, reproducible, matches the existing Phase 7 baseline (full validated extents).
- **Required data:** One window per body.
- **Advantages:** Simple; no arbitrary window-location choice if full extent used; reproducible.
- **Limitations:** Score is highly extent-dependent (Phase 10: 23.71 at 5.12 km → 49.92 at full); one window may not represent the body; Mars coverage caps common extent at ~30 km.
- **Sampling bias:** High — single location may be unrepresentative.
- **Reproducibility:** High (if extent fixed).
- **Computational cost:** Low.
- **Suitability:** Baseline reporting only; not sufficient for scientific claims about body similarity.

### B. Multiple non-overlapping fixed-area windows
- **Rationale:** Covers more terrain; quantifies within-body variability (Experiment A).
- **Required data:** Multiple windows per body; grid layout.
- **Advantages:** Reveals within-body spread; avoids overlap bias; enables within-body vs between-body comparison.
- **Limitations:** Windows reused across pairwise comparisons → not independent; grid placement is arbitrary; Mars coverage limits window count/size.
- **Sampling bias:** Moderate — grid alignment may align with terrain features.
- **Reproducibility:** Moderate (grid offsets must be recorded).
- **Computational cost:** Moderate (n² comparisons).
- **Suitability:** Characterizing within-body variability; showing that body identity is not separable.

### C. Stratified terrain sampling
- **Rationale:** Sample different terrain types (e.g., high vs low relief) to ensure representativeness.
- **Required data:** Terrain-type classification; windows per stratum.
- **Advantages:** Reduces representativeness bias; captures terrain heterogeneity.
- **Limitations:** Requires independent terrain classification (not currently available); stratum boundaries introduce their own bias.
- **Sampling bias:** Low (if strata well-defined); high (if strata mis-specified).
- **Reproducibility:** Low (depends on classification).
- **Computational cost:** High.
- **Suitability:** Future work; not currently implementable without terrain classification data.

### D. Repeated spatial sampling
- **Rationale:** Resample windows with replacement to estimate sampling variability.
- **Required data:** Multiple windows; randomization seed.
- **Advantages:** Quantifies window-location uncertainty; accounts for spatial dependence.
- **Limitations:** Windows are spatially correlated → bootstrap assumptions needed; computational cost.
- **Sampling bias:** Low (randomization).
- **Reproducibility:** High (with fixed seed).
- **Computational cost:** High.
- **Suitability:** Uncertainty quantification; future work.

### E. Aggregation across multiple window comparisons
- **Rationale:** Report distribution of pairwise TMSI rather than one score.
- **Required data:** Multiple windows per body.
- **Advantages:** Shows full distribution; avoids over-reliance on one pair; reveals overlap between within-body and between-body.
- **Limitations:** Comparisons reuse windows → not independent; mean TMSI can be misleading.
- **Sampling bias:** Moderate.
- **Reproducibility:** High (if windows fixed).
- **Computational cost:** Moderate.
- **Suitability:** Recommended for reporting variability alongside any single score.

## Recommendation (evidence-supported)
**No single strategy is recommended as a replacement for the official baseline.** Evidence shows:

1. Within-body TMSI range (Moon 29.27–94.10) overlaps and exceeds between-body range (22.38–90.60).
2. Body identity is not separable from window-location effects.
3. Extent strongly affects score (Phase 10).
4. Overlap strongly inflates score (Experiment C).

**Recommended reporting practice:**
- Always report spatial extent, window location, overlap status, and valid coverage alongside any TMSI.
- Report within-body variability when making cross-body claims.
- Treat a single TMSI as a pairwise window-morphology index, not a body-level indicator.
- Use strategy B (multiple non-overlapping windows) + strategy E (distribution reporting) for variability characterization, clearly labeled as experimental.

All experimental strategies remain separate from the official TMSI baseline (Moon–Mars full extent, TMSI 49.9229).
