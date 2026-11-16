# Terra Twin — Phase 19: Challenge Traceability

## 1. NASA Space Apps Challenge Objective Alignment

Terra Twin Phase 19 addresses the NASA Space Apps Challenge objective through the following mapped features:

### 1.1 Discover Potentially Relevant Terrestrial Environments

**How Terra Twin helps**: Users can browse an interactive registry of 13 Earth candidates across 6 environment categories (arid_desert, volcanic_basaltic, polar_ice, canyon_erosional, impact_crater, fluvial_erosional), each with a defensible geographic locator and scientific rationale.

**Feature support**:
- Interactive discovery map with filtering by environment category and planetary target
- Search functionality for candidate names and geographic regions
- Candidate detail panel with scientific description and geological context
- Planetary relevance tagging (Moon, Mars, Both)

**API/supporting code**: `DiscoveryMap` component with environment and planetary filters; `list_candidates()` with `environment` and `planetary_target` filters; `within_body_candidates()` function.

### 1.2 Organize Locations by Geological and Environmental Characteristics

**How Terra Twin helps**: The candidate registry classifies locations by environment classification, provides scientific descriptions, geological context, and planetary relevance tags. Users can organize and sort candidates by these characteristics.

**Feature support**:
- Environment classification for each candidate (arid_desert, polar_ice, volcanic_basaltic, canyon_erosional, impact_crater, fluvial_erosional)
- Planetary relevance: Moon, Mars, or Both
- Scientific description and geological context for each candidate
- Status tracking (CANDIDATE → SOURCE_VERIFIED → DATA_AVAILABLE → READY_FOR_COMPARISON)

**API/supporting code**: `Candidate` interface with 21 fields; `registry.py:list_candidates()` with `environment` and `planetary_target` filters; `candidate_status_counts()`.

### 1.3 Identify Evidence and Data Gaps

**How Terra Twin helps**: The data readiness panel explicitly identifies what data is available and what is missing for each candidate. DEM availability, spatial resolution, terrain-feature availability, and known limitations are clearly stated.

**Feature support**:
- Data acquisition status per candidate
- DEM availability (known, unknown, not_acquired)
- Spatial resolution documentation
- Coordinate reference system (EPSG:4326)
- Terrain-feature availability (full, partial, none)
- Scientific validation status (unvalidated, validated)
- Known limitations explicit statement

**API/supporting code**: `CandidateDetailPanel` data readiness section; `data_acquisition_status`, `dem_availability`, `spatial_resolution`, `coordinate_reference_system`, `elevation_coverage`, `terrain_feature_availability`, `scientific_validation_status`, `known_limitations` fields.

### 1.4 Prepare Candidate Environments for Reproducible Quantitative Comparison

**How Terra Twin helps**: The status transition system (CANDIDATE → SOURCE_VERIFIED → DATA_AVAILABLE → READY_FOR_COMPARISON) prepares candidates for Phase 20. Only candidates with `READY_FOR_COMPARISON` status are eligible for quantitative Earth–Moon/Mars similarity scoring. Unvalidated candidates are explicitly prevented from entering the comparison workflow.

**Feature support**:
- Enforced status transitions with prerequisites
- Eligibility enforcement via `candidate_eligible_for_evaluation()`
- Explicit ineligibility of CANDIDATE and DATA_AVAILABLE candidates for quantitative comparison
- Metadata interface for Phase 20 consumption (ID, geographic extent, source dataset, CRS, spatial resolution, elevation metadata, terrain feature availability, provenance, validation status)

**API/supporting code**: `registry.py:update_candidate_status()` with allowed transitions; `registry.py:candidate_eligible_for_evaluation()`; backend `similarity_status()` disabling Earth comparisons; `Candidate` interface fields for Phase 20.

### 1.5 Eventually Characterize Terrestrial Analogs for Lunar and Martian Exploration

**How Terra Twin helps**: The registry provides a structured foundation for eventual quantitative characterization. Candidates tagged with planetary relevance (Moon, Mars, Both) provide the geographic and scientific context needed for future analog characterization when Earth DEM data becomes available.

**Feature support**:
- Planetary relevance tagging
- Selection rationale documenting why each candidate was chosen
- Scientific context with geological/geomorphological explanation
- Explicit statement that candidate selection does not establish terrain similarity
- Data readiness grading supporting future quantitative analysis

**API/supporting code**: `planetary_relevance` field; `selection_rationale`; `scientific_description`; `geological_context`.

## 2. Preserved Scientific Limitations

Phase 19 maintains all existing scientific limitations from Phases 17 and 18.1:

| # | Limitation | Preserved Status |
|---|-----------|-----------------|
| 1 | TMSI cannot establish planetary body identity | ✅ Preserved |
| 2 | Extent-sensitivity (23.71 @ 5.12 km → 49.92 @ 10.24 km) | ✅ Preserved |
| 3 | Earth data unavailable (HTTP 401) | ✅ Preserved |
| 4 | Independent DEM benchmark blocked | ✅ Preserved |
| 5 | Spatial autocorrelation not fully captured (Moran's I = 0.979) | ✅ Preserved |
| 6 | "HIGH confidence" is qualitative | ✅ Preserved |
| 7 | Results design-dependent (10.24 km extent) | ✅ Preserved |
| 8 | Riley TRI is roughness index, not hazard measure | ✅ Preserved |
| 9 | Slope sensitive to DEM noise at steep slopes | ✅ Preserved |
| 10 | Edge cells excluded from local relief statistics | ✅ Preserved |

## 3. Traceability Matrix

| Objective | Feature | Implementation |
|-----------|---------|----------------|
| Discover relevant environments | Interactive map with filtering | `DiscoveryMap` component with env/planet/status filters |
| Organize by characteristics | Candidate registry with classification | `Candidate` interface; 13 candidates across 6 categories |
| Identify evidence gaps | Data readiness panel | `CandidateDetailPanel` with 6 data readiness fields |
| Prepare for quantitative comparison | Status transition system | `update_candidate_status()`; `candidate_eligible_for_evaluation()` |
| Characterize for exploration | Planetary relevance tagging | `planetary_relevance`: Moon/Mars/Both; `selection_rationale` |

## 4. what Terra Twin Does NOT Do

The following are explicitly stated and documented — not implemented:

- Does not claim visual resemblance proves geological similarity
- Does not treat environment category as a measured terrain result
- Does not claim TMSI identifies planetary body identity
- Does not fabricate missing Earth measurements
- Does not describe a candidate as a confirmed analog before quantitative evaluation
- Does not claim NASA endorsement or validation
- Earth comparisons remain disabled until authentic DEM data is acquired

## 5. User Interface Distinctions

The project maintains a clear distinction between three tiers in the user interface:

1. **Discovery**: Candidate registered with geographic location and environment classification; visible on the map and searchable
2. **Data readiness**: DEM availability indicated, spatial resolution known, terrain features documented; candidate may progress toward `DATA_AVAILABLE` status
3. **Scientific validation**: Validation status shown, explicit limitations stated, no unsupported claims; only `READY_FOR_COMPARISON` candidates are eligible for Phase 20

The UI communicates these distinctions through status badges, detail panel sections, and explicit integrity statements.

**Verdict**: PHASE19_CHALLENGE_TRACEABILITY.md — Complete with full traceability to NASA Space Apps objective.