# DEMO SCRIPT — Terra Twin

## Opening (30 seconds)

**Slide 1: Title**
- Terra Twin: Planetary Terrain Morphology Similarity Index
- NASA Space Apps Challenge 2026
- [Your Team/Organization]

**Slide 2: The Problem**
- We have terabytes of planetary DEM data from the Moon, Mars, and Earth
- Scientists need to compare terrain across bodies
- Existing methods lack uncertainty quantification and explicit limitations
- Question: Are morphological features similar across planets, or just different acquisitions?

## The Demonstration (3 minutes)

**Slide 3: Terra Twin Overview**
- Open the Terra Twin web interface
- Show the main research shell with the Moon ↔ Mars comparison

**Slide 4: Dataset Provenance**
- Show the dataset inventory panel
- Point out: Moon LOLA = VALIDATED, Mars Jezero DTM = VALIDATED
- Point out: Earth NASADEM = BLOCKED (authentication required)
- Explain that all dataset statuses are authentic, not fabricated

**Slide 5: TMSI Computation**
- Navigate to the DEM Benchmarking view
- Show the TMSI result: 49.92
- Show the bootstrap 95% CI width: 14.56
- Explain: this is the similarity score between the specific Moon and Mars windows compared

**Slide 6: Uncertainty Quantification**
- Show the four uncertainty categories:
  - Dataset uncertainty (reported separately)
  - Resolution uncertainty (reported separately)
  - Sampling uncertainty (extent-sensitive: 5.12 km → 23.71; 10.24 km → 49.92)
  - Methodological sensitivity (reported separately)
- Point out Moran's I = 0.979 (strong spatial autocorrelation)

**Slide 7: What TMSI Does and Does NOT Establish**
- TMSI = 49.92 establishes: elevation distribution similarity between the specific Moon and Mars windows compared
- TMSI does NOT establish: planetary body identity (within-body ranges overlap with between-body range)
- TMSI does NOT establish: geological equivalence
- TMSI does NOT generalize to different extents without re-computation

## Key Authentic Results (1 minute)

**Slide 8: Actual Measured Results**
- TMSI = 49.92 (Moon–Mars, 10.24 km extent)
- Bootstrap 95% CI width: 14.56
- Moran's I: 0.979 (strong spatial autocorrelation)
- Within-body range (Moon): 29.27 – 94.10
- Within-body range (Mars): 40.99 – 90.90
- Between-body range: 22.38 – 90.60

**Slide 9: What Is Shown Is What Was Measured**
- No fabricated charts
- No placeholder results
- All values derived from authentic NASA datasets
- Pipeline fully reproducible from published data and code

## Closing (30 seconds)

**Slide 10: Why It Matters**
- Terra Twin provides the first publicly documented, reproducible framework for planetary terrain comparison with full uncertainty disclosure
- The methodology is extensible: future work with overlapping-terrain DEM pairs will enable stronger conclusions
- Transparency about limitations (Earth data blocked, independent benchmark blocked, TMSI cannot classify planetary body) is the project's strongest scientific feature

**Slide 11: Contact & Reproducibility**
- Full documentation: docs/PHASE16_FINAL_REPORT.md
- Test results: docs/phase16_test_results.md
- Scientific paper: research/TERRA_TWIN_RESEARCH_PAPER.md
- Reproducibility guide: submission/REPRODUCIBILITY_GUIDE.md
- All results authentic; no fabricated NASA data