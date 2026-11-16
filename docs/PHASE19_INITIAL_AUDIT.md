# Terra Twin — Phase 19: Initial Audit

**Project:** Terra Twin  
**Phase:** 19 of 22  
**Previous phase:** Phase 18.1 — Authentic Data Acquisition  
**Status:** AUDIT COMPLETE — READY FOR IMPLEMENTATION

---

## 1. Repository State Summary

### 1.1 Existing Reports Consulted
- `docs/PHASE17_ANALOG_DISCOVERY_ARCHITECTURE.md` — Full 10-step scientific workflow design; Earth candidate registry schema designed; ResearchWorkbench.tsx extension design; comparison engine design; all 10 non-negotiable architectural requirements documented.
- `docs/PHASE18_1_AUTHENTIC_DATA_ACQUISITION.md` — Earth data acquisition attempts documented: NASADEM HGT blocked (HTTP 401), SRTM GL3 (not attempted), Copernicus GLO-30 (registration required), USGS 3DEP (path not identified). No authentic Earth DEM acquired.
- `docs/PHASE18_FINAL_REPORT.md` — Phase 18 complete: Earth data ingestion pipeline implemented (validation, feature extraction, provenance recording). 116/116 Python tests pass; 0 TypeScript errors; 8 ESLint errors within 13-error baseline. Earth data blocked; pipeline ready for when credentials available.

### 1.2 Existing Code inspected

#### Frontend
- `frontend/components/ResearchWorkbench.tsx` (923 lines) — Four destinations (EXPLORE/COMPARE/RELIABILITY/DATA & METHODS); `Candidate` interface with 21 fields; `DiscoveryMap` component with candidate card rendering; `CandidateDetailPanel` component; latitude/longitude validation functions (`is_valid_latitude`, `is_valid_longitude`, `formatCoordinate`); map legend with status badges; list-based alternative to map interaction.
- `frontend/app/page.tsx` — Home route renders `ResearchWorkbench`.
- `frontend/app/layout.tsx` — Root layout with Geist typography; metadata: "TerraMatch | Planetary Analog Discovery".

#### Backend
- `backend/app/main.py` — FastAPI app with CORS, health, and similarity routers.
- `backend/app/api/similarity.py` — API endpoints for status, features, methodology, results, sampling framework, raster preview, export (JSON/CSV/PDF); comparison endpoint. Earth comparisons disabled (`earth_mars: enabled: False`, `earth_moon: enabled: False`).
- `backend/app/api/health.py` — Health check endpoint.
- `backend/app/services/similarity.py` — Dataset registry with `moon_lola` and `mars_jezero_ctx_dtm` (both VALIDATED); `UNAVAILABLE_DATASETS` includes `earth_nasadem_hgt_v001`; `compare_dataset_ids()` function; `similarity_status()` reports Earth comparisons disabled.
- `backend/app/schemas/similarity.py` — Pydantic schemas for comparison request/response/status.
- `science/datasets/registry.py` — Dataset registry functions: `list_candidates()`, `add_candidate()`, `update_candidate_status()`, `candidate_eligible_for_evaluation()`, `within_body_candidates()`, `accessible_candidates()`, `candidate_status_counts()`.
- `science/datasets/registry.json` — 6 existing candidates: `atacama_desert`, `antartica_polar`, `hawaii_volcanic`, `grand_canyon`, `arabian_desert`, `death_valley`. All status `CANDIDATE`. Planetary relevance: Mars (5), Moon+Mars (1). All `scientific_validation_status: unvalidated`.
- `science/data_ingestion/acquire_earth_dem.py` — Earth DEM acquisition pipeline. NASADEM HGT blocked (HTTP 401). Alternative sources documented (Copernicus, SRTM GL3, USGS 3DEP). No authentic Earth DEM acquired in this environment.
- `science/tests/test_phase19_candidates.py` — 17 test functions (14 pass, 3 fail due to TypeScript functions not being available in Python namespace: `is_valid_latitude`, `is_valid_longitude`, `formatCoordinate` are defined in ResearchWorkbench.tsx, not exposed to Python).

#### Existing Data Structures
- **Candidate interface** (ResearchWorkbench.tsx:690-715): `id`, `name`, `country`, `environment_classification`, `planetary_relevance`, `status`, `latitude`, `longitude`, `bounding_box`, `scientific_description`, `geological_context`, `selection_rationale`, `supporting_references`, `source_dataset`, `source_url`, `data_acquisition_status`, `dem_availability`, `spatial_resolution`, `coordinate_reference_system`, `elevation_coverage`, `terrain_feature_availability`, `scientific_validation_status`, `known_limitations`, `last_updated`.
- **Status values** (ResearchWorkbench.tsx:696): `"CANDIDATE" | "SOURCE_VERIFIED" | "DATA_AVAILABLE" | "READY_FOR_COMPARISON"`.
- **Registry functions** (registry.py): `list_candidates()`, `add_candidate()`, `update_candidate_status()`, `candidate_eligible_for_evaluation()`, `within_body_candidates()`, `accessible_candidates()`, `candidate_status_counts()`.
- **Candidate eligibility** (registry.py:154-164): Only `READY_FOR_COMPARISON` status makes a candidate eligible for quantitative evaluation; `CANDIDATE` and `DATA_AVAILABLE` are not eligible.

### 1.3 Identified Integration Points

#### Reusable Components
- `Candidate` interface already defined in ResearchWorkbench.tsx with all required Phase 19 fields.
- `DiscoveryMap` component already renders candidate cards with status badges and planetary tags.
- `CandidateDetailPanel` already displays geographic info, scientific context, rationale/provenance, data readiness, and scientific status.
- `registry.py` provides `list_candidates()`, `add_candidate()`, `update_candidate_status()`, `candidate_eligible_for_evaluation()`.
- `registry.json` already contains 6 well-documented candidates with sources and scientific context.

#### New Requirements for Phase 19
- Extend status values to include `QUANTITATIVELY_EVALUATED` (but do not assign it in Phase 19).
- Add filtering by environment category, planetary target, and scientific validation status in the DiscoveryMap.
- Add search functionality for candidate names and geographic regions.
- Enhance CandidateDetailPanel to explicitly state that candidate selection does not establish terrain similarity.
- Ensure candidate metadata can be consumed by Phase 20 (ID, geographic extent, source dataset, DEM location/reference, CRS, spatial resolution, elevation metadata, terrain feature availability, provenance, validation status).
- Enforce that unvalidated candidates cannot enter quantitative comparison workflow.

#### Planned Modifications
- Enhance `DiscoveryMap` with filter controls and search behavior.
- Enhance `CandidateDetailPanel` with explicit scientific integrity statements.
- Add more candidates to reach 12-20 range with diverse environment categories.
- Ensure all candidate status transitions are validated.
- Add TypeScript types and Python schemas for Phase 20 integration.

---

## 2. Workstream A: Earth Candidate Registry

### 2.1 Existing Registry State
The candidate registry is implemented in `science/datasets/registry.json` with 6 candidates and in `science/datasets/registry.py` with supporting functions. Each candidate has the following fields (per the existing `Candidate` interface):

| Field | Present? |
|-------|----------|
| Unique candidate ID | ✅ |
| Candidate name | ✅ |
| Country and geographic region | ✅ |
| Latitude and longitude | ✅ |
| Bounding box or geographic polygon | ✅ |
| Environment classification | ✅ |
| Short scientific description | ✅ |
| Geological or geomorphological context | ✅ |
| Potential relevance to Moon, Mars, or both | ✅ |
| Candidate-selection rationale | ✅ |
| Supporting references | ✅ |
| Source dataset and source URL | ✅ |
| Data acquisition status | ✅ |
| DEM availability | ✅ |
| Spatial resolution, when known | ✅ |
| Coordinate reference system, when known | ✅ |
| Elevation coverage status | ✅ |
| Terrain-feature availability | ✅ |
| Scientific validation status | ✅ |
| Known limitations | ✅ |
| Last updated timestamp | ✅ |

### 2.2 Status Values
Existing status values: `"CANDIDATE" | "SOURCE_VERIFIED" | "DATA_AVAILABLE" | "READY_FOR_COMPARISON"`

Phase 19 requires explicit status values with the additional `QUANTITATIVELY_EVALUATED` value that must NOT be assigned in Phase 19. The existing 4 status values are sufficient for Phase 19; `QUANTITATIVELY_EVALUATED` is a Phase 20 terminal status.

### 2.3 Integration Points
- `registry.py:list_candidates()` — filter by status, environment, planetary target
- `registry.py:candidate_eligible_for_evaluation()` — only `READY_FOR_COMPARISON` is eligible
- `registry.py:update_candidate_status()` — enforces allowed transitions
- `ResearchWorkbench.tsx:DiscoveryMap` — renders status badges
- `ResearchWorkbench.tsx:CandidateDetailPanel` — displays scientific status

---

## 3. Workstream B: Scientifically Grounded Candidate Catalog

### 3.1 Existing Catalog
6 candidates currently exist in `registry.json`:
1. **Atacama Desert** (Chile) — arid desert, Mars relevance
2. **Antarctica Polar Plateau** — polar ice, Moon+Mars relevance
3. **Hawaii Island Volcanic Landscapes** — volcanic basaltic, Moon+Mars relevance
4. **Grand Canyon** — canyon erosional, Mars relevance
5. **Arabian Desert** — arid desert, Mars relevance
6. **Death Valley** — arid desert, Mars relevance

### 3.2 Minimum Catalog Target
Phase 19 aims for 12–20 well-documented candidates across multiple environment categories. Currently have 6 candidates across 3 categories (arid_desert: 3, volcanic_basaltic: 1, canyon_erosional: 1, polar_ice: 1). Need 6–14 more candidates to reach minimum target, prioritizing scientific quality over quantity.

### 3.3 Candidates to Add
Based on reputable scientific sources (NASA, USGS, ESA, peer-reviewed publications), the following candidates are proposed:

1. **Mojave Desert** — arid desert, Mars relevance — documented aeolian processes and playa deposits
2. **Sahara Desert** — arid desert, Mars relevance — largest hot desert, extensive orbiter comparison datasets
3. **Arctic Tundra** — polar ice, Moon relevance (permafrost/PSR analog) + Mars relevance — freeze-thaw cycles
4. **Alaska Peninsula Volcanics** — volcanic basaltic, Alaska volcanic terrain — similar to Hawaii but higher latitude
5. **Columbia River Flood Basalts** — volcanic basaltic, Mars relevance — extensive flood basalt terrain analog
6. **Meteor Crater (Barringer)** — impact crater, Mars relevance — well-studied impact analog
7. **Lake Baikal Region** — fluvial/erosional, Mars relevance — ancient lake basins
8. **Iceland Highlands** — glacial/volcanic, Moon+Mars relevance — unique volcanic-glacial interactions
9. **Yucatan Peninsula** — impact crater, Mars relevance — Chicxulub analog, impact crater studies
10. **Tibetan Plateau** — high mountainous, Moon relevance (regolith processes) + Mars relevance — "Roof of the World"
... (additional candidates may be added to reach 12-20 range)

All candidates will be sourced from authoritative sources (NASA Mars Analog Research Program, USGS, ESA, peer-reviewed publications). No coordinates will be invented — all geographic locators will be defensible and documented.

---

## 4. Workstream C: Interactive Geographic Discovery Map

### 4.1 Existing Map Component
The `DiscoveryMap` component in `ResearchWorkbench.tsx:731-839` already provides:
- Candidate marker rendering via card grid
- Status badges (CANDIDATE, SOURCE_VERIFIED, DATA_AVAILABLE, READY_FOR_COMPARISON)
- Planetary tags (Moon, Mars, Both)
- List-based alternative to map interaction
- Loading/empty states (no valid candidates)
- Accessible keyboard navigation

### 4.2 Enhancements Required
- **Filter controls**: Environment category filter, planetary target filter, scientific validation status filter
- **Search functionality**: Search candidate names and geographic regions
- **Filter synchronization**: URL-state or persistent filter state
- **Visual status distinctions**: Enhanced visual encoding communicating discovery → data readiness → scientific validation → Phase 20 readiness
- **Responsive behavior**: Grid layout adapting to screen size
- **Error states**: Graceful handling of missing/invalid geometry

### 4.3 Technical Requirements
- Use WGS84 coordinates (EPSG:4326) — already the case
- Validate latitude/longitude ranges — already implemented (`is_valid_latitude`, `is_valid_longitude`)
- Handle missing geometry gracefully — already partially implemented
- Avoid duplicate candidate markers — already using `key={c.id}`
- Include loading, empty, and error states — already have empty state

---

## 5. Workstream D: Candidate Detail and Evidence Panel

### 5.1 Existing Detail Panel
The `CandidateDetailPanel` in `ResearchWorkbench.tsx:843-916` already provides:
- Geographic information: name, country, coordinates, bounding box
- Scientific context: environment classification, planetary relevance, scientific description, geological context
- Rationale and provenance: selection rationale, supporting references, source dataset, source URL
- Data readiness: data acquisition status, DEM availability, spatial resolution, CRS, elevation coverage, terrain-feature availability
- Scientific status: validation status, known limitations, last updated

### 5.2 Enhancements Required
- **Explicit integrity statement**: "Candidate selection does not establish terrain similarity" must be displayed
- **Missing-data indicators**: Clear visualization of what data is available vs. missing
- **Data readiness grading**: Visual progression from unvalidized → source verified → data available → ready for comparison
- **DEM availability**: Never display fabricated DEM coverage; show "unknown" or "not acquired" when data not available
- **Provenance retention**: Source organization, title, URL always retained

---

## 6. Workstream E: Phase 20 Integration Contract

### 6.1 Required Interface
Phase 20 must be able to retrieve from the candidate registry:

| Field | Source |
|------|--------|
| Candidate ID | `candidate.id` |
| Geographic extent | `candidate.bounding_box` or lat/lon |
| Source dataset | `candidate.source_dataset` |
| DEM location or dataset reference | `candidate.dem_availability` + implicit reference |
| CRS | `candidate.coordinate_reference_system` |
| Spatial resolution | `candidate.spatial_resolution` |
| Elevation metadata | `candidate.elevation_coverage` |
| Terrain feature availability | `candidate.terrain_feature_availability` |
| Provenance | `candidate.supporting_references` + `candidate.source_url` |
| Validation status | `candidate.scientific_validation_status` |

### 6.2 Validation Contract
- `candidate_eligible_for_evaluation(candidate_id)` must return `True` only for `READY_FOR_COMPARISON` status
- Unvalidated candidates (status `CANDIDATE` or `DATA_AVAILABLE`) must not be eligible for quantitative Earth–Moon/Mars similarity scoring
- A candidate without an authentic, processed Earth DEM must remain ineligible
- The interface may support a preview of candidate metadata but must not manufacture comparison results

### 6.3 Existing Contract
- `registry.py:candidate_eligible_for_evaluation()` already enforces that only `READY_FOR_COMPARISON` is eligible
- `registry.py:update_candidate_status()` enforces allowed transitions: CANDIDATE → SOURCE_VERIFIED → DATA_AVAILABLE → READY_FOR_COMPARISON
- Backend `similarity_status()` reports Earth comparisons as disabled

---

## 7. Workstream F: Scientific Integrity and Challenge Alignment

### 7.1 Traceability to NASA Space Apps Objective
The Phase 19 features help users:
1. **Discover potentially relevant terrestrial environments** — Interactive map with filtered browsing of Earth candidates across environment categories
2. **Organize locations by geological and environmental characteristics** — Candidate registry with environment classification, scientific description, geological context, planetary relevance
3. **Identify evidence and data gaps** — Data readiness panel showing DEM availability, spatial resolution, terrain-feature availability, known limitations
4. **Prepare candidate environments for reproducible quantitative comparison** — Status transition system (CANDIDATE → SOURCE_VERIFIED → DATA_AVAILABLE → READY_FOR_COMPARISON) with eligibility enforcement
5. **Eventually characterize terrestrial analogs for lunar and Martian exploration** — Planetary relevance tagging (Moon/Mars/Both) with scientific rationale

### 7.2 Non-Negotiable Constraints Preserved
- Do not claim visual resemblance proves geological similarity
- Do not treat environment category as a measured terrain result
- Do not claim TMSI identifies planetary body identity
- Do not fabricate missing Earth measurements
- Do not describe a candidate as a confirmed analog before quantitative evaluation
- Preserve dataset provenance and licensing information

### 7.3 UI Distinctions
The UI should distinguish:
- **Discovery**: Candidate registered with geographic location and environment classification
- **Data readiness**: DEM availability indicated, spatial resolution known, terrain features documented
- **Scientific validation**: Validation status shown, explicit limitations stated, no unsupported claims

---

## 8. Workstream G: Testing and Quality Assurance

### 8.1 Test Coverage Areas
- **Registry**: Candidate schema validation, required metadata, valid coordinate ranges, geographic extent validation, duplicate candidate detection, missing provenance rejection, invalid status transitions
- **Discovery**: Category filtering, planetary-target filtering, search behavior, status filtering, empty results, candidate detail retrieval
- **Map**: Candidate marker rendering, missing geometry handling, selection behavior, filter synchronization, loading and error states, responsive behavior
- **Scientific integrity**: Unvalidated candidates cannot receive quantitative validation status; missing DEM data cannot produce real similarity scores; source provenance retained; existing Moon/Mars scientific functionality not broken

### 8.2 Test Execution
- Run relevant new tests
- Full Python test suite: `python3 -m pytest science/tests/`
- TypeScript type checking: `npx tsc --noEmit`
- ESLint: `npx eslint`
- Production build: `next build`
- Compare lint errors with baseline of 13 errors (8 previously reported)

### 8.3 Baseline Comparison
Existing baseline: 13 ESLint errors (8 were previously reported as issues). New Phase 19 changes must not increase this count, and any new errors must be documented and addressed.

---

## 9. Required Documentation
Six documents to produce:
1. `docs/PHASE19_INITIAL_AUDIT.md` — In production
2. `docs/PHASE19_CANDIDATE_REGISTRY.md` — To be created
3. `docs/PHASE19_GEOGRAPHIC_DISCOVERY_MAP.md` — To be created
4. `docs/PHASE19_DATA_PROVENANCE.md` — To be created
5. `docs/PHASE19_CHALLENGE_TRACEABILITY.md` — To be created
6. `docs/PHASE19_FINAL_REPORT.md` — To be created after implementation

---

**End of Initial Audit**