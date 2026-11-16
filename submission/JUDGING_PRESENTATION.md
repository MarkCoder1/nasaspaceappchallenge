# JUDGING PRESENTATION — Terra Twin

## 1. The Problem Terra Twin Addresses

- Planetary DEM data exists for the Moon, Mars, and Earth but lacks a standardized, uncertainty-quantified framework for cross-body terrain comparison
- Scientists need to know whether morphological features are similar across planetary bodies or are artifacts of different data acquisition geometries
- Existing analysis methods either omit uncertainty quantification or fail to document blocking conditions (missing data, inapplicable comparisons)

**Terra Twin's answer**: A research-grade platform that computes the Terrain Morphology Similarity Index (TMSI) between DEM windows, with full documentation of what the result establishes and — crucially — what it does not establish.

## 2. Why Comparing Planetary Terrain Matters

- Identifying shared geologic processes (volcanism, impact cratering, fluvial features) across world boundaries
- Preparing for missions that compare multiple planetary targets (sample return site selection, traverse planning)
- Developing universal terrain classification schemes that transcend single-planet frameworks
- Enabling AI/ML models trained on one body's terrain to be evaluated against another body's morphology

**Judge's question to consider**: How can we compare terrain across planets without claiming results we cannot scientifically support? Terra Twin answers this by explicitly documenting limitations.

## 3. The Scientific Question

**How can terrain morphology be quantitatively compared across planetary bodies, and what does TMSI similarity establish — or fail to establish — about planetary identity?**

The Terrain Morphology Similarity Index (TMSI) was developed to address this question. TMSI computes a similarity score between two elevation distribution samples, ranging from 0 (no similarity) to 100 (identical distributions). The index is derived from the Earth Mover's Distance (Wasserstein distance) between empirical cumulative distribution functions of DEM window elevations.

**The critical scientific finding**: TMSI = 49.92 for the Moon–Mars comparison at 10.24 km extent. This value is mathematically well-defined and reproducible within the experimental design. However, the within-body TMSI ranges (Moon: 29.27–94.10, Mars: 40.99–90.90) overlap with the between-body range (22.38–90.60), meaning TMSI does not establish planetary body identity.

## 4. How Terra Twin Works

1. **Dataset Registration** — Planetary DEMs registered with full provenance metadata (validation status, access status, resolution, source, body designation)

2. **Windowed Comparison** — TMSI computed between two spatial windows, each defined by extent (km) and location (row/col offset) within a DEM. Extent-sensitivity explicitly documented (23.71 @ 5.12 km → 49.92 @ 10.24 km)

3. **Uncertainty Quantification** — Four independent categories reported separately:
   - Dataset uncertainty
   - Resolution uncertainty
   - Sampling uncertainty
   - Methodological sensitivity

4. **Spatial Autocorrelation Diagnostics** — Moran's I computed for each dataset (Moran's I = 0.979 in primary comparison)

5. **Blocking Condition Documentation** — All non-scientific comparators explicitly blocked with reproducible reasons

## 5. Authentic NASA and Planetary Datasets Used

| Dataset | Agency | Body | Status |
|---------|--------|------|--------|
| `moon_lola` | NASA LRO/LOLA | Moon | VALIDATED, full access |
| `mars_jezero_ctx_dtm` | NASA MARS/Context DTM | Mars | VALIDATED, full access |
| `earth_nasadem_hgt_v001` | NASA Earthdata | Earth | BLOCKED (HTTP 401 authentication failure) |

No fabricated or synthetic data are presented as authentic NASA measurements. Two synthetic test-only datasets exist for unit testing and are clearly labeled.

## 6. The TMSI Methodology

1. Extract elevation samples from two DEM spatial windows
2. Compute the Wasserstein (Earth Mover's) distance between the empirical CDFs
3. Transform to a 0–100 similarity scale: TMSI = 100 - (Wasserstein distance × scaling factor)
4. Report TMSI alongside: bootstrap 95% CI width, Moran's I, extent, window coordinates, and all four uncertainty categories

**Actual experimental result**: Moon–Mars TMSI = 49.92 (95% bootstrap CI width: 14.56; seed sensitivity: ~0.38 TMSI range; Moran's I = 0.979).

## 7. Actual Experimental Results

| Finding | Value | Interpretation |
|---------|-------|----------------|
| TMSI (Moon–Mars) | 49.92 | Moderate elevation distribution similarity at 10.24 km extent |
| Bootstrap 95% CI width | 14.56 | Substantial sampling uncertainty |
| Moran's I | 0.979 | Strong spatial autocorrelation in elevation data |
| Within-body range (Moon) | 29.27 – 94.10 | Window-dependent; not planet-identifying |
| Within-body range (Mars) | 40.99 – 90.90 | Window-dependent; not planet-identifying |
| Between-body range | 22.38 – 90.60 | Spans both within-body ranges |
| Overlap (within-body ∩ between-body) | Substantial | TMSI cannot recover planetary body |
| Seed sensitivity | ~0.38 TMSI range | Window-location dependence |
| Extent sensitivity | 23.71 @ 5.12 km → 49.92 @ 10.24 km | Design-dependent result |

## 8. What the Results Establish

- The specific Moon–Mars window pairs compared have elevation distributions with moderate TMSI similarity (49.92)
- The bootstrap CI (width 14.56) quantifies sampling uncertainty around this estimate
- The result is reproducible across bootstrap replicates and seed permutations within the documented experimental design
- Spatial autocorrelation (Moran's I = 0.979) is strong and must be considered when interpreting uncertainty

## 9. What the Results Do NOT Establish

1. **Planetary body identity**: TMSI value alone cannot determine whether a terrain sample comes from the Moon, Mars, or another body. Within-body and between-body TMSI ranges overlap substantially.

2. **Geological equivalence**: Similarity of elevation distributions does not imply similarity of geological origin or process.

3. **Generalization to different extents**: TMSI = 49.92 at 10.24 km does not transfer to 5.12 km extent (TMSI = 23.71) without re-computation.

4. **Earth terrain similarity**: Earth comparisons are not performed. Earth data are blocked by NASA Earthdata authentication (HTTP 401). No claim is made about Earth terrain.

5. **Validated planetary classifier**: TMSI is not and was not claimed to be a planetary identity classifier.

## 10. Why the Project Matters for Future Planetary Exploration

- **Methodological transparency**: Terra Twin provides a template for how to quantify and disclose uncertainty in planetary terrain analysis, preventing the common failure mode of overinterpreting similarity metrics.

- **Reproducibility baseline**: All results are derived from authentic NASA datasets with fully reproducible code. Future researchers can acquire overlapping-terrain DEM pairs and apply the same methodology with documented expectations.

- **Informed decision-making**: By explicitly documenting what TMSI does and does not establish, the project enables scientists and mission planners to use terrain similarity metrics without making unwarranted claims about planetary identity.

- **Future extensibility**: The framework is designed for when overlapping-terrain DEM pairs become available (e.g., from future NASA missions). The blocking conditions are documented acquisition instructions, not permanent limitations.

## Summary for Judges

**The problem**: Cross-planetary terrain comparison without standardized uncertainty or limitation disclosure.

**The solution**: Terra Twin — a research platform with TMSI computation, four-category uncertainty framework, spatial autocorrelation diagnostics, and explicit blocking condition documentation.

**The result**: TMSI = 49.92 (Moon–Mars), with full uncertainty context. The result establishes elevation distribution similarity for the specific windows compared but does not establish planetary identity.

**Why it matters**: Terra Twin prevents the overinterpretation of terrain similarity metrics and provides a reproducible, transparent framework that can be extended when overlapping-terrain DEM pairs become available. Its strongest contribution is not a planetary classifier but a methodology that openly discloses its own limitations.

**Verification**: 116/116 tests pass; TypeScript compiles with 0 errors; ESLint at baseline 13 errors; all results authentic; no fabricated NASA data.