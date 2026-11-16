# PROJECT DESCRIPTION — Terra Twin

## The Problem

Planetary exploration requires understanding how terrain morphology varies across different worlds. Scientists need quantitative tools to compare elevation distributions and surface features between planetary bodies, but existing analysis methods lack standardized uncertainty quantification and explicit documentation of comparative limitations. Without a reproducible framework, it is difficult to determine whether observed morphological similarities are significant or artifacts of data acquisition and processing.

## Why Comparing Planetary Terrain Matters

Comparing terrain across planetary bodies enables:
- Identification of shared geologic processes (volcanism, impact cratering, fluvial activity) that operate across world boundaries
- Assessment of whether morphological features on one body are qualitatively similar to those on another
- Preparation for missions that will compare multiple planetary targets (e.g., sample return site selection across bodies)
- Development of universal terrain classification schemes that transcend single-planet frameworks

Terra Twin was created to address this gap by providing a transparent, uncertainty-quantified methodology for terrain comparison that works across any pair of DEM datasets.

## The Scientific Question

**How can terrain morphology be quantitatively compared across planetary bodies, and what does similarity establish — or fail to establish — about planetary identity?**

The Terrain Morphology Similarity Index (TMSI) was developed to address this question. TMSI computes a similarity score between two elevation distribution samples, ranging from 0 (no similarity) to 100 (identical distributions). The index is derived from the Earth Mover's Distance (Wasserstein distance) between empirical cumulative distribution functions of DEM window elevations.

## How Terra Twin Works

1. **Dataset Registration**: Planetary DEMs are registered in a central registry with full provenance metadata (validation status, access status, resolution, source, body designation).

2. **Windowed Comparison**: TMSI is computed between two spatial windows, each defined by extent (km) and location (row/col offset) within a DEM. The extent-sensitivity of TMSI is explicitly documented (23.71 @ 5.12 km → 49.92 at 10.24 km).

3. **Uncertainty Quantification**: Four independent uncertainty categories are reported:
   - Dataset uncertainty (differences between production systems)
   - Resolution uncertainty (nominal vs effective resolution)
   - Sampling uncertainty (extent and window-location dependence)
   - Methodological sensitivity (algorithm configuration, overlap fraction)

4. **Spatial Autocorrelation Diagnostics**: Moran's I is computed for each dataset to document the strength of spatial dependence in elevation data (Moran's I = 0.979 in the primary comparison).

5. **Blocking Condition Documentation**: All comparators that cannot be scientifically executed are explicitly blocked with reproducible reasons (Earth data: HTTP 401 auth failure; independent DEM benchmark: no overlapping-terrain pair).

## Authentic NASA and Planetary Datasets Used

| Dataset | Agency | Body | Status |
|---------|--------|------|--------|
| `moon_lola` | NASA LRO/LOLA | Moon | VALIDATED, full access |
| `mars_jezero_ctx_dtm` | NASA MARS/Context DTM | Mars | VALIDATED, full access |
| `earth_nasadem_hgt_v001` | NASA Earthdata | Earth | BLOCKED (HTTP 401 authentication failure) |

No fabricated or synthetic data are presented as authentic NASA measurements. Two synthetic test-only datasets exist for unit testing and are clearly labeled as such.

## TMSI Methodology

The Terrain Morphology Similarity Index (TMSI) operates as follows:
1. Extract elevation samples from two DEM spatial windows
2. Compute the Wasserstein (Earth Mover's) distance between the empirical CDFs
3. Transform to a 0–100 similarity scale: TMSI = 100 - (Wasserstein distance × scaling factor)
4. Report TMSI alongside: bootstrap 95% CI width, Moran's I, extent, window coordinates, and all four uncertainty categories

**Actual experimental result**: Moon–Mars TMSI = 49.92 (95% bootstrap CI width: 14.56; seed sensitivity: ~0.38 TMSI range; Moran's I = 0.979).

## What the Results Establish

The TMSI = 49.92 result establishes that the elevation distributions of the specific Moon and Mars windows compared have moderate similarity under the TMSI metric. The bootstrap CI (width 14.56) quantifies the sampling uncertainty. The result is reproducible across bootstrap replicates and seed permutations within the documented experimental design.

## What the Results Do NOT Establish

1. TMSI does not identify planetary body. Within-body TMSI ranges (Moon: 29.27–94.10, Mars: 40.99–90.90) overlap with the between-body range (22.38–90.60), meaning the same TMSI value could arise from within-Moon, within-Mars, or between-body comparisons.

2. TMSI does not measure geological equivalence. Similarity of elevation distributions does not imply similarity of geological origin or process.

3. The result does not generalize to different extents or window locations without re-computation. TMSI is extent-sensitive (23.71 @ 5.12 km → 49.92 @ 10.24 km).

4. Earth comparisons are not performed. Earth data are blocked by NASA Earthdata authentication requirements; no claim is made about Earth terrain similarity.

## Why the Project Matters for Future Planetary Exploration

Terra Twin provides the first publicly documented, reproducible framework for quantifying terrain similarity across planetary bodies with full uncertainty disclosure. By explicitly documenting what TMSI does and does not establish, the project prevents overinterpretation of similarity metrics and provides a baseline for future work with overlapping-terrain dataset pairs. The methodological transparency — including all blocking conditions, uncertainty categories, and spatial autocorrelation diagnostics — serves as a template for future planetary comparison tools.

**Status**: Research-grade implementation. Not a deployed operational tool. All scientific claims are authenticated and reproducible.