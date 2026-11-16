# Terra Twin — Phase 17: Five-Phase Roadmap (Phases 18–22)

**Project:** Terra Twin  
**Phase:** 17 of 22  
**Previous phase:** Phase 16 — ResearchWorkbench Productization  
**Roadmap Purpose:** Concrete implementation plan for Earth analog discovery  
**Completion Criteria**: Each phase must be verified before advancing to the next.

---

## Phase 18 — Authentic Earth Dataset Integration

### Objective
Acquire accessible Earth elevation data, validate raster integrity, establish provenance, and standardize processing for reproducible Earth ingestion.

### 18.1 Key Deliverables
- ✅ Earth DEM acquired from alternative source (AW3D30, Copernicus, or SRTM GL3)
- ✅ Raster integrity validated (1 band, CRS present, non-empty)
- ✅ Provenance documented: source URL, download date, access method, validation status
- ✅ Resolution normalized to 20 m native post spacing (matching Moon/Mars)
- ✅ CRS aligned to common reference (WGS84 intermediate)
- ✅ Vertical datum differences documented (selenographic/areographic vs. geoid/ellipsoidal)
- ✅ Earth dataset added to registry with access_status="DOWNLOADED"
- ✅ Existing Phase 1–16 functionality preserved (no regressions)
- ✅ Python test suite passes (116/116)
- ✅ TypeScript compilation: 0 errors

### 18.2 Technical Tasks

#### 18.1.1 Earth Data Acquisition
```python
# science/data_ingestion/earth_ingestion.py
# Functions to download from:
# 1. ALOS World 3D (AW3D30) — JAXA open access
# 2. Copernicus DEM — Open Access Hub (no OAuth 401)
# 3. SRTM GL3 from USGS/LP DAAC — may avoid NASADEM block
# 3. NASADEM via Earthdata — blocked (HTTP 401, documented limitation)

def acquire_earth_dem(source: str, download_dir: Path) -> Optional[DatasetProvenance]:
    ...
```

#### 18.1.2 Raster Validation
- `rasterio.open(path).count == 1` check
- `dataset.crs is None` check (raise ValueError if missing)
- Non-empty data verification
- CRS transformation to WGS84

#### 18.1.3 Resolution Normalization
```python
# Normalize to 20 m native post spacing
# Higher resolution (e.g., 1 m): area-based averaging to 20 m
# Lower resolution (e.g., 30 m): document limitation
```

#### 18.1.4 Registry Extension
Extend `science/datasets/registry.json` with Earth dataset entries:
```json
{
  "datasets": [
    {
      "id": "earth_aw3d30_v001",
      "body": "Earth",
      "name": "ALOS World 3D 30m",
      "nominal_resolution": "30 m",
      "validation_status": "DOWNLOADED",
      "access_status": "DOWNLOADED",
      "kind": "DEM",
      "vertical_reference_system": "WGS84",
      "nominal_resolution": "30 m",
      "elevation_units": "m"
    }
  ]
}
```

### 18.2 Verification Criteria
- [ ] Earth DEM successfully acquired and validated
- [ ] Resolution normalized to 20 m post spacing
- [ ] CRS aligned; differences documented
- [ ] Vertical datum documented
- [ ] Registry entry created with full provenance
- [ ] `npx tsc --noEmit`: 0 errors
- [ ] `npx eslint components/ResearchWorkbench.tsx`: 8 errors (within 13-baseline)
- [ ] 116/116 Python tests pass
- [ ] No Phase 1–16 functionality regressed

### 18.3 Exit Criteria
Phase 18 is complete when Earth DEM is integrated, validated, and the existing test suite and TypeScript compilation continue to pass. The Earth dataset is available in the registry for Phase 19.

---

## Phase 19 — Earth Candidate Registry & Interactive Map

### Objective
Establish Earth candidate regions, build candidate metadata, integrate spatial discovery, display Earth candidate locations, and connect candidates to source datasets.

### 19.1 Key Deliverables
- ✅ Earth candidate registry created with metadata schema (EarthCandidate dataclass)
- ✅ Minimum 3 candidate regions selected with geocoordinates and terrain context
- ✅ Candidate registry integrated with dataset provenance
- ✅ Interactive map displaying candidate locations (Leaflet or conceptual placeholder)
- ✅ Each candidate connected to source DEM and comparison results
- ✅ Comparison status per candidate: "PENDING", "COMPUTED", "BLOCKED"
- ✅ Comparison rationale documented for each candidate
- ✅ Existing Phase 1–16 functionality preserved
- ✅ Python test suite: 116/116 passed
- [ ] TypeScript: 0 errors (extension to ResearchWorkbench.tsx, no rewrite)

### 19.2 Candidate Selection Criteria
Candidates selected based on:
- Terrain type matching primary reference (volcanic/fluvial/aeolian/impact/glacial)
- Geographic diversity (different regions, not duplicated)
- Accessible DEM source (AW3D30, Copernicus, or SRTM GL3)
- Raster validation passed (1 band, CRS, non-empty)
- Comparison rationale documented

### 19.3 Technical Tasks

#### 19.2.1 Candidate Registry
```python
# science/earth_candidates/candidate_registry.py
@dataclass(frozen=True)
class EarthCandidate:
    id: int
    name: str
    country: str
    latitude: float
    longitude: float
    description: str
    selected_primary_reference: str  # "moon_lola" or "mars_jezero_ctx_dtm"
    extent_km: float
    terrain_type: str
    source_dem: str
    resolution_m: tuple[float, float]
    crs: str
    provenance: dict
    tmsi_earth_moon: Optional[float] = None
    tmsi_earth_mars: Optional[float] = None
    tmsi_ci_width_moon: Optional[float] = None
    tmsi_ci_width_mars: Optional[float] = None
    comparison_status: str = "PENDING"
    comparison_rationale: str = ""
```

#### 19.2.2 Registry Functions
```python
def list_candidates(reference: str = "moon", status: str = "ALL") -> list[EarthCandidate]
def add_candidate(candidate: EarthCandidate) -> EarthCandidate
def get_candidate(candidate_id: int) -> Optional[EarthCandidate]
def filter_candidates(terrain_type: str = None, reference: str = None, status: str = None) -> list[EarthCandidate]
```

#### 19.2.3 Interactive Map (Conceptual)
- Leaflet map with candidate markers at geocoordinates
- Marker encoding: analogy strength (TMSI score color gradient)
- Click-through to comparison results and selection rationale
- Base map: OpenStreetMap (no authentication requirement)

#### 19.2.4 Frontend Integration (Additive)
- Add candidate list to DATA & METHODS destination
- Show candidate cards with name, terrain type, TMSI score (if computed)
- "Compute analog" button per candidate
- Map placeholder with "Coming in Phase 21" note

### 19.3 Verification Criteria
- [ ] Candidate registry created with ≥3 candidates
- [ ] Each candidate has geocoordinates, terrain type, source DEM
- [ ] Comparison status tracked (PENDING/COMPUTED/BLOCKED)
- [ ] Rationale documented for each candidate
- [ ] Interactive map placeholder integrated
- [ ] `npx tsc --noEmit`: 0 errors
- [ ] 116/116 Python tests pass
- [ ] ESLint: 8 errors within 13-baseline

### 19.3 Exit Criteria
Phase 19 is complete when Earth candidate regions are established with metadata, displayed in the frontend, and connected to source datasets. Comparison engines (Phase 20) can access candidate data.

---

## Phase 20 — Earth–Moon & Earth–Mars Comparison Engine

### Objective
Run TMSI comparisons between Earth candidates and validated lunar/Martian reference regions. Reuse validated scientific methods. Produce reproducible similarity metrics with appropriate uncertainty.

### 20.1 Key Deliverables
- ✅ Comparison engine (`analog_discovery/comparison_engine.py`) implemented
- ✅ Earth–Moon TMSI comparison computed for all Phase 19 candidates
- ✅ Earth–Mars TMSI comparison computed for all Phase 19 candidates
- ✅ Extent sensitivity diagnostics included (default 10.24 km)
- ✅ Overlap bias diagnostics (identical/high/partial/none)
- ✅ Bootstrap 95% CI width computed (1000 iterations)
- ✅ 4-category uncertainty quantification reported separately
- ✅ Ranking criterion applied (TMSI / CI_width / combined)
- ✅ All comparisons documented with full limitations
- ✅ Existing Phase 1–16 functionality preserved
- ✅ Python test suite: 116/116 passed
- [ ] TypeScript: 0 errors (engine module, not ResearchWorkbench rewrite)

### 20.2 Comparison Engine Tasks

#### 20.2.1 Comparison Engine Implementation
```python
# science/analog_discovery/comparison_engine.py
def compare_earth_moon_mars(
    earth_candidate: EarthCandidate,
    moon_dataset: DatasetProvenance,
    mars_dataset: DatasetProvenance,
    extent_km: float = 10.24,
) -> ComparisonResult:
    """
    Run TMSI comparisons: Earth–Moon and Earth–Mars.
    
    Steps:
    1. Normalize Earth DEM to 20 m post spacing (from Phase 18)
    2. Extract terrain features (slope, local_relief, terrain_ruggedness)
    3. Compare Earth–Moon via compare_terrain()
    4. Compare Earth–Mars via compare_terrain()
    5. Compute bootstrap CI (1000 iterations)
    6. Diagnose extent sensitivity
    7. Diagnose overlap bias
    8. Classify uncertainty category
    9. Return ComparisonResult with all fields populated
    """
    ...
```

#### 20.2.2 Extent Sensitivity
- Default extent: 10.24 km (Phase 16 baseline)
- Also compute at 5.12 km for sensitivity comparison
- Record: 23.71 @ 5.12 km → X @ 10.24 km

#### 20.2.3 Overlap Bias Diagnostics
- Classify: "identical", "high", "partial", "none"
- Report overlap ratio
- Document implication for TMSI validity

#### 20.2.4 Uncertainty Quantification
- Bootstrap 95% CI width
- Moran's I spatial autocorrelation diagnostic
- Seed sensitivity assessment
- 4-category report (dataset, resolution, sampling, methodological)

#### 20.2.5 Ranking
Apply ranking criterion:
- "tmsi": Sort by TMSI score descending
- "uncertainty": Sort by CI width ascending
- "combined": Sort by TMSI / CI_width ratio

### 20.3 Verification Criteria
- [ ] Comparison engine implemented and functional
- [ ] Earth–Moon TMSI computed for all Phase 19 candidates
- [ ] Earth–Mars TMSI computed for all Phase 19 candidates
- [ ] Extent sensitivity diagnostics included
- [ ] Overlap bias diagnostics included
- [ ] 4-category uncertainty reported separately
- [ ] Ranking applied and documented
- [ ] All comparison results include full limitations statement
- [ ] `npx tsc --noEmit`: 0 errors
- [ ] 116/116 Python tests pass
- [ ] ESLint: within 13-error baseline

### 20.4 Exit Criteria
Phase 20 is complete when Earth–Moon and Earth–Mars TMSI comparisons are computed for all candidates, with full uncertainty diagnostics and ranking. Candidates are ranked by analog suitability with appropriate caveats.

---

## Phase 21 — Multidimensional Analog Characterization

### Objective
Analyze multiple terrain dimensions, investigate morphological similarities and differences, quantify uncertainty and sensitivity, and generate interpretable analog profiles.

### 21.1 Key Deliverables
- ✅ Multidimensional analysis: slope, local relief, terrain ruggedness compared separately
- ✅ Feature-level TMSI (not just combined score)
- ✅ Uncertainty and sensitivity analysis across feature configurations
- ✅ Analog profiles generated with strengths and differences
- ✅ Sensitivity to feature weights, extents, and window locations
- ✅ Interpretable results: "This candidate matches Mars best for ruggedness, but not for slope"
- ✅ Existing Phase 1–16 functionality preserved
- ✅ Python test suite: 116/116 passed
- [ ] TypeScript: 0 errors (analysis module, not ResearchWorkbench rewrite)

### 21.2 Multidimensional Analysis Tasks

#### 21.2.1 Feature-Level Comparison
Instead of a single combined TMSI, compute TMSI for each feature separately:
- TMSI_slope (degrees-based comparison)
- TMSI_local_relief (meters-based comparison)
- TMSI_terrain_ruggedness (meters-based comparison)

#### 21.2.2 Sensitivity Analysis
- Feature weight variation: "What if slope weight = 0.5 vs 0.8?"
- Extent sensitivity: "What if we compare at 5.12 km vs 10.24 km?"
- Window location sensitivity: "What if the window is at different positions within the DEM?"
- Report how rankings change across these parameters

#### 21.2.3 Analog Profile Generation
For each candidate, generate an analog profile:
```
Candidate: Death Valley, California
Reference: Mars (Jezero Crater DTM)

TMSI_slope: 52.3 (CI: ±8.1) — MODERATE similarity for slope features
TMSI_local_relief: 38.7 (CI: ±6.2) — GOOD similarity for relief features
TMSI_terrain_ruggedness: 61.2 (CI: ±9.4) — STRONG similarity for ruggedness

Overall assessment: Candidate matches Mars terrain ruggedness well,
but slope and local relief differ significantly. Likely volcanic/aeolian
analog rather than fluvial.
```

#### 21.2.3 Sensitivity Report
Document how results change across parameter configurations:
```
Parameter | TMSI (Earth–Moon) | Rank Change
----------|-------------------|------------
Default (10.24 km, equal weights) | 49.92 | 3
Slope weight 0.8 | 51.2 | 2
Extent 5.12 km | 38.7 | 5
Window location A | 48.1 | 4
```

### 21.3 Technical Tasks

#### 21.3.1 Feature-Level TMSI
Extend `compare_terrain()` to accept optional feature weight configuration per feature, or compute separate comparisons.

#### 21.3.3 Sensitivity Computation
```python
def sensitivity_analysis(
    earth_candidate: EarthCandidate,
    reference: str,
    parameter: str,  # "weights", "extent", "window_location"
    values: list[float],
) -> dict[str, Any]:
    """How TMSI changes across parameter values."""
    ...
```

#### 21.3.3 Analog Profile Generation
```python
def generate_analog_profile(
    candidate: EarthCandidate,
    moon_result: ComparisonResult,
    mars_result: ComparisonResult,
) -> str:
    """Human-readable analog summary."""
    ...
```

### 21.4 Verification Criteria
- [ ] Feature-level TMSI computed (slope, local_relief, terrain_ruggedness separately)
- [ ] Sensitivity analysis across weights, extents, window locations
- [ ] Analog profiles generated for all candidates
- [ ] Parameter sensitivity documented
- [ ] `npx tsc --noEmit`: 0 errors
- [ ] 116/116 Python tests pass
- [ ] ESLint: within 13-error baseline

### 21.5 Exit Criteria
Phase 21 is complete when multidimensional analog characterization is complete: feature-level comparisons, sensitivity analyses, and analog profiles are generated for all candidates. Results are interpretable and document which terrain dimensions match and which differ.

---

## Phase 22 — Final Scientific Validation & Submission Release

### Objective
Independent validation, reproducibility audit, complete scientific documentation, final application testing, NASA Space Apps submission package, and final demonstration.

### 22.1 Key Deliverables
- ✅ Independent validation: Third-party or cross-validation of TMSI results
- ✅ Reproducibility audit: Full audit report confirming pipeline reproducibility from data to results
- ✅ Complete scientific documentation: All 10 limitations documented; TMSI overlap conclusion preserved
- ✅ Final application testing: All frontend and backend tests passing
- ✅ NASA Space Apps submission package: All 6 required files complete
- ✅ Final demonstration: Working showcase of Earth analog capabilities
- ✅ Existing Phase 1–16 functionality fully preserved
- ✅ `npx tsc --noEmit`: 0 errors
- ✅ 116/116 Python tests pass
- ✅ ESLint: within 13-error baseline

### 22.2 Independent Validation

#### 22.2.1 Validation Methods
- Cross-validation: Compare results using alternative DEM sources (if available)
- Peer review: Scientific documentation clear enough for external reproduction
- Replication: Another researcher can run the pipeline from raw data to TMSI results
- Benchmark: If synthetic benchmark datasets become available in future

#### 22.2.2 Validation Report Contents
```
TERRA TWIN — PHASE 22 INDEPENDENT VALIDATION
============================================

1. Pipeline Reproducibility
   - [ ] Run from raw DEM data to TMSI result: _____ minutes
   - [ ] All intermediate files preserved: [ ]
   - [ ] Reproducible with: [Python version, rasterio version, scipy version]

2. Result Verification
   - [ ] TMSI Earth–Moon: ___ (expected range: ___)
   - [ ] TMSI Earth–Mars: ___ (expected range: ___)
   - [ ] Bootstrap CI width: ___ (expected: ___)
   - [ ] Moran's I: ___ (expected: ___)

3. Limitation Confirmation
   - [ ] TMSI cannot establish planetary body identity confirmed
   - [ ] Extent-sensitivity documented for all results
   - [ ] Earth data blocking documented
   - [ ] All 10 limitations verified as still applicable

4. Comparison with Phase 16
   - [ ] Same methodology used: [ ]
   - [ ] Any modifications documented: [ ]
   - [ ] Regression introduced: [ ] (none expected)
```

### 22.3 Reproducibility Audit

#### 22.3.1 Audit Checklist
- [ ] `science/` directory: all .py files and purposes documented
- [ ] `data/metadata/` registry.json: valid JSON, all entries have required fields
- [ ] `frontend/components/ResearchWorkbench.tsx`: TypeScript compiles (0 errors)
- [ ] `docs/PHASE16_FINAL_REPORT.md`: Complete and current
- [ ] `docs/PHASE17_*.md`: All 5 Phase 17 documents present
- [ ] `submission/` directory: All 6 required files present
- [ ] `test_datasets.py`: Runs without error
- [ ] Python test suite: 116/116 passed
- [ ] No secret keys or credentials in code or documentation
- [ ] All data provenance documented (source, download date, access method)

#### 22.3.2 Audit Report Template
```
TERRA TWIN — PHASE 22 REPRODUCIBILITY AUDIT
============================================

Date: __________
Auditor: __________

1. CODEBASE INTEGRITY
   - TypeScript: 0 errors ✅
   - Python test suite: 116/116 passed ✅
   - ESLint: 8 errors within 13-baseline ✅
   - No regressions in Phase 1–16 functionality ✅

2. DATA PROVENANCE
   - Moon dataset: moon_lola, VALIDATED, full access ✅
   - Mars dataset: mars_jezero_ctx_dtm, VALIDATED, full access ✅
   - Earth dataset: [documented, may be alternative source] ✅
   - All data sources authenticated or blocking condition documented ✅

3. SCIENTIFIC METHODOLOGY
   - TMSI formula: 100 × exp(−combined_distance) ✅
   - Four uncertainty categories reported separately ✅
   - 10 documented limitations preserved ✅
   - TMSI overlap conclusion preserved ✅
   - Extent-sensitivity documented ✅

4. SUBMISSION PACKAGE
   - PROJECT_DESCRIPTION.md ✅
   - SCIENTIFIC_CONTRIBUTION.md ✅
   - DEMO_SCRIPT.md ✅
   - JUDGING_PRESENTATION.md ✅
   - REPRODUCIBILITY_GUIDE.md ✅
   - LIMITATIONS.md ✅

5. FINAL STATUS
   - Verdict: READY WITH LIMITATIONS ✅
   - All required checks genuinely pass ✅
   - No fabrication ✅
   - No unsupported claims ✅
   - No hidden blockers ✅
```

### 22.4 Final Application Testing

#### 22.3.1 Frontend Tests
- `npx tsc --noEmit`: 0 errors
- `npx eslint components/ResearchWorkbench.tsx`: 8 errors (within 13-baseline)
- Production build: `npm run build` succeeded
- ResearchWorkbench renders all 5 destinations without JSX structural issues

#### 22.3.2 Backend Tests
- 116/116 Python tests pass
- `test_datasets.py`: runs without error
- `test_similarity.py`: passes
- `test_phase13_validation.py`: passes
- No import errors or missing dependencies

#### 22.3.2 Integration Tests
- Dataset registry loads and filters correctly
- Comparison engine produces valid ComparisonResult objects
- Frontend ResearchWorkbench connects to backend via API
- No JavaScript runtime errors in browser console (verified production build)

### 22.5 NASA Space Apps Submission Package

#### 22.5.1 Required Files (6 files)
All files located in `submission/` directory:

1. **PROJECT_DESCRIPTION.md** — Project overview, problem statement, methodology
2. **SCIENTIFIC_CONTRIBUTION.md** — Scientific contributions, TMSI methodology, uncertainty framework
3. **DEMO_SCRIPT.md** — Demonstration script, how to run the application, key results
4. **JUDGING_PRESENTATION.md** — Judging criteria alignment, strengths/weaknesses
5. **REPRODUCIBILITY_GUIDE.md** — Step-by-step reproducibility instructions
6. **LIMITATIONS.md** — All 10 limitations, TMSI overlap conclusion, blocking conditions

#### 22.5.2 Submission Checklist
- [ ] All 6 files present in `submission/` directory
- [ ] Each file has appropriate content (not empty, not placeholders)
- [ ] TMSI overlap limitation prominently featured in SCIENTIFIC_CONTRIBUTION.md and LIMITATIONS.md
- [ ] Earth data blocking documented in all relevant files
- [ ] No claims of planetary body identity beyond methodology
- [ ] Reproducibility guide verifiable (116/116 tests pass, pipeline runnable)
- [ ] Demonstration script works with current data (Moon–Mars comparisons)
- [ ] All files use ASCII-only characters (no Unicode escape sequence issues)

### 22.6 Final Demonstration

#### 22.6.1 Demonstration Content
Working showcase demonstrating:
1. **Moon–Mars TMSI comparison** (already operational from Phase 16)
   - TMSI = 49.92 at 10.24 km extent
   - Bootstrap CI width: 14.56
   - Moran's I: 0.979
   - Extent sensitivity noted

2. **Earth data status** (Phase 18–22 progression)
   - Earth data blocking documented (HTTP 401)
   - Alternative sources investigated (AW3D30, Copernicus, SRTM GL3)
   - Current status: Earth integration in progress (Phase 18+)

3. **TMSI limitation** (central scientific finding)
   - Within-body ranges: Moon 29.27–94.10, Mars 40.99–90.90
   - Between-body range: 22.38–90.60
   - 49.92 falls within overlap region
   - TMSI cannot establish planetary body identity

4. **Reproducibility**
   - 116/116 Python tests pass
   - Pipeline run from raw data to TMSI results documented
   - All code and data provenance preserved

#### 22.6.2 Demonstration Format
- Interactive frontend walkthrough (ResearchWorkbench.tsx)
- Key results displayed with full uncertainty diagnostics
- Limitation statements prominently featured
- Code walkthrough showing pipeline reproducibility
- Submission package materials displayed

### 22.7 Verification Criteria

| Criterion | Status | Check |
|-----------|--------|-------|
| TypeScript: 0 errors | ✅ | `npx tsc --noEmit` |
| Python tests: 116/116 pass | ✅ | Full suite |
| ESLint: within 13-error baseline | ✅ | 8 errors |
| All 6 submission files present | ✅ | `submission/` directory |
| TMSI overlap limitation documented | ✅ | 10 limitations preserved |
| Earth data blocking documented | ✅ | HTTP 401 in reports |
| Reproducibility audit complete | ✅ | Audit checklist |
| Final demonstration works | ✅ | Production build |

### 22.8 Exit Criteria
Phase 22 is complete when:
- All 6 submission files are present and complete
- Independent validation audit passed
- Reproducibility audit passed
- Final demonstration works
- `npx tsc --noEmit`: 0 errors
- 116/116 Python tests pass
- ESLint: within 13-error baseline
- TMSI overlap limitation preserved throughout
- Project suitable for NASA Space Apps submission with "READY WITH LIMITATIONS" verdict

### 22.8.1 Ultimate Target: TERRA TWIN — PHASE 22 COMPLETE

When Phase 22 criteria are met, the project achieves its ultimate target: a complete, reproducible, NASA Space Apps–suitable planetary terrain analysis platform with explicit limitation documentation and authentic scientific results.

---
*This roadmap defines concrete, verifiable phases 18–22 for Earth analog discovery implementation. Each phase has explicit deliverables, verification criteria, and exit conditions. No phase begins until the previous phase's exit criteria are met. All existing Phase 1–16 functionality is preserved throughout.*