# Terra Twin — Phase 17: Earth Analog Discovery Architecture

**Project:** Terra Twin  
**Phase:** 17 of 22  
**Previous phase:** Phase 16 — ResearchWorkbench Productization  
**Status:** ARCHITECTURAL DESIGN

## 1. Scientific Workflow Design

The intended scientific workflow for Earth analog discovery is a 10-step process that extends the existing TMSI methodology from Moon–Mars comparisons to Earth–Moon/Mars comparisons when authentic Earth datasets become available.

### 1.1 Workflow Steps

| Step | Description | Existing Infrastructure | New Requirements |
|------|-------------|------------------------|------------------|
| **1. Select reference region** | Choose a validated lunar or Martian reference region (e.g., Moon: moon_lola; Mars: mars_jezero_ctx_dtm) | ✅ Implemented — dataset registry with VALIDATED markers | None |
| **2. Identify candidate Earth regions** | Define geographic regions on Earth for comparison | ❌ Not implemented | Candidate registry module; geographic metadata |
| **3. Obtain authentic Earth elevation data** | Download and validate Earth DEM data | ❌ BLOCKED (NASA Earthdata HTTP 401) | Earth data acquisition module; alternative source investigation |
| **4. Standardize spatial resolution** | Resample all datasets to common post spacing (20 m) | ⚠️ Partial — existing `assess_resolution()` checks compatibility | Resolution normalization framework; downsampling/upsampling methods |
| **5. Calculate comparable terrain features** | Extract slope, local relief, terrain ruggedness | ✅ Implemented — feature_extraction.py | Earth DEM compatibility; CRS alignment |
| **6. Compare morphological distributions** | Compute TMSI with Wasserstein + KS + pooled IQR | ✅ Implemented — compare_terrain() backend | Earth dataset integration; overlap diagnostics |
| **7. Rank candidate Earth analogs** | Rank by TMSI score with uncertainty quantification | ❌ Not implemented | Analog ranking; bootstrap confidence; confidence classification |
| **8. Quantify uncertainty and confidence** | Report 4-category uncertainty + extent sensitivity | ✅ Partially — bootstrap CI, extent diagnostics | Full uncertainty framework for Earth comparisons |
| **9. Visualize results geographically** | Display analog locations on interactive map | ❌ Not implemented | Earth candidates map; geographic visualization |
| **10. Explain candidate selection** | Document why each candidate was selected | ❌ Not implemented | Selection rationale; feature comparison details |

## 2. Backend Module Organization

### 2.1 Suggested Module Structure

```
science/
├── earth_data/
│   ├── earth_ingestion.py      # Download and validate Earth DEMs
│   ├── crs_alignment.py        # CRS transformation utilities
│   ├── resolution_normalization.py  # 20 m post spacing resampling
│   └── earth_registry.py       # Extended dataset registry
├── earth_candidates/
│   ├── candidate_registry.py   # Earth candidate regions metadata
│   ├── candidate_selection.py  # Selection criteria and rationale
│   └── spatial_index.py        # Geographic spatial indexing
├── analog_discovery/
│   ├── comparison_engine.py    # Earth–Moon/Mars TMSI comparison
│   ├── analog_ranking.py       # TMSI-based ranking with uncertainty
│   └── uncertainty.py          # 4-category uncertainty quantification
└── cross_planet_comparison/
    ├── extent_sensitivity.py   # Extent diagnostics
    ├── overlap_diagnostics.py  # Overlap bias classifications
    └── spatial_analysis.py     # Spatial autocorrelation diagnostics
```

### 2.2 Key Backend Functions

#### 2.2.1 Earth Data Ingestion (`earth_ingestion.py`)

```python
def acquire_earth_dem(source: str, download_dir: Path) -> Optional[DatasetProvenance]:
    """Acquire Earth DEM from alternative source.
    
    Priority order:
    1. ALOS World 3D (AW3D30) from JAXA — no NASA Earthdata auth
    2. Copernicus DEM (SRTM-derived) — Open Access Hub
    3. SRTM GL3 from USGS/LP DAAC — may avoid NASADEM block
    4. NASADEM via Earthdata — blocked (HTTP 401)
    
    Returns DatasetProvenance on success, None on failure.
    Always documents: source, resolution, CRS, vertical datum, access method.
    Never fabricates data; returns None with detailed warnings on failure.
    """
    ...
```

#### 2.2.2 CRS Alignment (`crs_alignment.py`)

```python
def align_to_reference(
    dataset: TerrainFeatureSet,
    reference_crs: CRS,
    target_resolution_m: float = 20.0,
) -> TerrainFeatureSet:
    """Transform dataset CRS and resample to target resolution.
    
    Steps:
    1. Transform CRS to reference (e.g., WGS84 intermediate)
    2. Resample elevation to target_resolution_m post spacing
       using area-based averaging (preserve elevation statistics)
    3. Re-extract terrain features at new resolution
    4. Document: original CRS, original resolution, transformation method
    
    Returns new TerrainFeatureSet with effective_resolution_m set.
    Always documents: what was changed and why.
    """
    ...
```

#### 2.2.3 Resolution Normalization (`resolution_normalization.py`)

```python
def normalize_to_native_spacing(
    target: TerrainFeatureSet,
    candidate: TerrainFeatureSet,
) -> tuple[TerrainFeatureSet, TerrainFeatureSet]:
    """Resample both datasets to 20 m native post spacing.
    
    Moon and Mars datasets are already at 20 m native post spacing.
    If Earth DEM is at different resolution:
    - Higher resolution (e.g., 1 m): aggregate to 20 m (mean pooling)
    - Lower resolution (e.g., 30 m): document limitation; TMSI may be less sensitive
    
    Returns: (normalized_target, normalized_candidate) both at 20 m spacing.
    Documents: original resolutions, aggregation method, any information loss.
    """
    ...
```

#### 2.2.4 Comparison Engine (`comparison_engine.py`)

```python
def compare_earth_moon_mars(
    earth_dataset: DatasetProvenance,
    moon_dataset: DatasetProvenance,
    mars_dataset: DatasetProvenance,
    extent_km: float = 10.24,
) -> dict[str, Any]:
    """Run TMSI comparisons: Earth–Moon and Earth–Mars.
    
    Steps:
    1. Acquire and validate Earth DEM
    2. Normalize resolutions to 20 m native post spacing
    3. Align CRS to common reference
    4. Extract terrain features (slope, local_relief, terrain_ruggedness)
    5. Compare Earth–Moon via compare_terrain()
    6. Compare Earth–Mars via compare_terrain()
    7. Return combined result with:
       - earth_moon_tmsi, earth_moon_confidence
       - earth_mars_tmsi, earth_mars_confidence
       - extent_sensitivity diagnostics
       - overlap_bias diagnostics
       - all 4 uncertainty categories
       - resolution normalization documentation
    """
    ...
```

#### 2.2.5 Analog Ranking (`analog_ranking.py`)

```python
def rank_analogs(
    comparisons: list[dict[str, Any]],
    ranking_criterion: str = "tmsi",
) -> dict[str, Any]:
    """Rank Earth candidates by analog suitability.
    
    Criterion options:
    - "tmsi": Sort by TMSI score (descending — higher = more similar)
    - "uncertainty": Sort by bootstrap CI width (narrower = more certain)
    - "combined": Sort by TMSI / CI_width ratio (balance similarity vs. certainty)
    
    Returns ranked list with:
    - Candidate rank and TMSI score
    - Bootstrap 95% CI width
    - Uncertainty category (HIGH/MEDIUM/LOW based on CI width and Moran's I)
    - Extent sensitivity note
    - Ranking criterion used
    
    Does NOT rank into "planetary identity" — only "terrain morphological similarity"
    per the documented TMSI limitation.
    """
    ...
```

## 3. Frontend Integration Design

### 3.1 ResearchWorkbench.tsx Extensions

The existing ResearchWorkbench.tsx (already rewritten in Phase 16 with 4 destinations) should be extended with minimal additions:

#### 3.1.1 New Destination: EARTH & ANALOG

Add a 5th navigation destination alongside EXPLORE/COMPARE/RELIABILITY/DATA & METHODS:

```
NAV_ITEMS = [
  { id: "explore", label: "EXPLORE" },
  { id: "compare", label: "COMPARE" },
  { id: "reliability", label: "RELIABILITY" },
  { id: "data_methods", label: "DATA & METHODS" },
  { id: "earth_analog", label: "EARTH & ANALOG" },  // New
]
```

#### 3.1.2 Earth View Component

```typescript
function EarthView({ earthDataset, setEarthDataset }: { 
  earthDataset?: DatasetProvenance; 
  setEarthDataset: (id: string) => void 
}) {
  if (!earthDataset) {
    return (
      <div>
        <span className="eyebrow">EARTH & ANALOG</span>
        <h2>Earth Analog Discovery</h2>
        <p>Earth elevation data not yet acquired.</p>
        <p>Investigation prioritized in Phases 18–22.</p>
        <p>See docs/PHASE17_EARTH_DATA_STRATEGY.md for alternatives.</p>
      </div>
    );
  }
  
  return (
    <div>
      <span className="eyebrow">EARTH & ANALOG</span>
      <h2>Earth Analog: {earthDataset.body}</h2>
      <dl>
        <dt>SOURCE</dt><dd>{earthDataset.name}</dd>
        <dt>RESOLUTION</dt><dd>{earthDataset.nominal_resolution || "N/A"}</dd>
        <dt>ACCESS</dt><dd>{earthDataset.access_status}</dd>
        <dt>VALIDATION</dt><dd>{earthDataset.validation_status}</dd>
      </dl>
      
      <button onClick={() => setEarthDataset(undefined)}>
        Remove Earth data
      </button>
    </div>
  );
}
```

#### 3.1.3 Analogs View Component

```typescript
function AnalogsView({ earthMoonComparisons, earthMarsComparisons }: {
  earthMoonComparisons: ComparisonResult[];
  earthMarsComparisons: ComparisonResult[];
}) {
  return (
    <div>
      <span className="eyebrow">ANALOG RANKINGS</span>
      <h3>Earth–Moon Analogies</h3>
      <ol>
        {earthMoonComparisons.map((c, i) => (
          <li key={i}>
            <TmsiDistribution ... /> {/* reuse existing distribution component */}
            <FeatureChart result={c.distance} ... />
          </li>
        ))}
      </ol>
      
      <h3>Earth–Mars Analogies</h3>
      <ol>
        {earthMarsComparisons.map((c, i) => (
          <li key={i}>
            <TmsiDistribution ... />
            <FeatureChart result={c.distance} ... />
          </li>
        ))}
      </ol>
    </div>
  );
}
```

### 3.2 Minimal Rewrite Principle

**Do not rewrite ResearchWorkbench.tsx unnecessarily** (non-negotiable requirement from Phase 17 guidelines).

The extension approach above adds:
- 1 new navigation item
- 2 new view components (Earth view, Analogs view)
- Integration with existing sub-components (TmsiDistribution, FeatureChart, HistogramBars)
- No restructuring of existing JSX; new content added as additional routes/views

The existing 4-destination structure (EXPLORE/COMPARE/RELIABILITY/DATA & METHODS) remains unchanged. New Earth & Analog content is additive.

## 4. Earth Candidate Registry

### 4.1 Candidate Metadata Schema

```python
@dataclass(frozen=True)
class EarthCandidate:
    id: int
    name: str  # e.g., "Death Valley, California"
    country: str
    latitude: float
    longitude: float
    description: str  # Geologic context (e.g., "Erg dunes, volcanic terrain")
    selected_primary_reference: str  # "moon_lola" or "mars_jezero_ctx_dtm"
    selected_secondary_reference: Optional[str]  # Alternative reference
    extent_km: float  # Comparison extent in km
    terrain_type: str  # "volcanic", "fluvial", "aeolian", "impact", "glacial"
    source_dem: str  # "AW3D30", "Copernicus", "SRTM GL3", etc.
    resolution_m: tuple[float, float]
    crs: str
    provenance: dict  # Source URL, download date, validation status
    tmsi_earth_moon: Optional[float]  # Computed TMSI; None if not yet computed
    tmsi_earth_mars: Optional[float]  # Computed TMSI; None if not yet computed
    tmsi_ci_width_moon: Optional[float]  # Bootstrap CI width; None if not yet computed
    tmsi_ci_width_mars: Optional[float]  # Bootstrap CI width; None if not yet computed
    comparison_status: str  # "PENDING", "COMPUTED", "BLOCKED"
    comparison_rationale: str  # Why this candidate was selected
```

### 4.2 Candidate Registry Functions

```python
def list_candidates(
    reference: str = "moon",
    status: str = "ALL",
) -> list[EarthCandidate]:
    
def add_candidate(candidate: EarthCandidate) -> EarthCandidate:
    
def get_candidate(candidate_id: int) -> Optional[EarthCandidate]:
    
def filter_candidates(
    terrain_type: Optional[str] = None,
    reference: Optional[str] = None,
    status: Optional[str] = None,
) -> list[EarthCandidate]:
```

## 5. Comparison Workflow (Detailed)

### 5.1 When Earth Data Becomes Available

```
Step 1: Earth DEM acquired via alternative source (AW3D30, Copernicus, SRTM GL3)
Step 2: Validate raster (1 band, CRS present, non-empty)
Step 3: Transform CRS to WGS84 intermediate
Step 4: Resample to 20 m native post spacing (matching Moon/Mars)
Step 5: Extract terrain features (slope, local_relief, terrain_ruggedness)
Step 5: Define comparison windows (extent_km = 10.24 km default)
Step 6: Compare Earth–Moon: compare_terrain(earth, moon, extent_km=10.24)
Step 7: Compare Earth–Mars: compare_terrain(earth, mars, extent_km=10.24)
Step 8: Record extent sensitivity diagnostics
Step 9: Run bootstrap resampling (1000 iterations) for CI width
Step 10: Classify uncertainty category and rank analogs
```

### 5.2 Comparison Result Schema

```python
@dataclass
class ComparisonResult:
    reference: str  # "moon" or "mars"
    tmsi: float  # Similarity index 0–100
    confidence: str  # "HIGH", "MEDIUM", "LOW" (qualitative, not statistical)
    ci_width: float  # Bootstrap 95% CI width
    extent_km: float
    overlap_status: str  # "identical", "high", "partial", "none"
    strongest_features: list[str]  # Top 2 matching feature names
    largest_differences: list[str]  # Top 2 differing feature names
    uncertainties: dict[str, Any]  # 4-category uncertainty report
    limitations: list[str]  # Documented limitations applying to this comparison
```

### 5.3 Uncertainty Classification

| CI Width | Moran's I | Classification | Description |
|----------|-----------|----------------|-------------|
| < 10 | < 0.5 | HIGH | Narrow CI; strong similarity claim |
| 10–20 | 0.5–0.9 | MEDIUM | Moderate CI; similarity with some uncertainty |
| > 20 | > 0.9 | LOW | Wide CI (cf. Phase 16: 14.56 at default); strong spatial autocorrelation limits certainty |

**Note**: The "HIGH/MEDIUM/LOW" classification is **qualitative**, reflecting reproducibility and CI width, not a traditional statistical confidence level. This distinction must be preserved (from Phase 16 limitation #6).

## 6. Geographic Visualization (Future Phase)

### 6.1 Map Component Design (Conceptual)

When Earth candidates are available and comparisons computed:

```typescript
function EarthAnalogMap({ candidates }: { candidates: EarthCandidate[] }) {
  return (
    <div>
      <span className="eyebrow">GEOGRAPHIC DISTRIBUTION</span>
      <h3>Earth Analog Candidate Locations</h3>
      {/* Map visualization — Leaflet/Mapbox in future phase */}
      <p>Candidate locations shown with analogy strength encoding.</p>
      <p>Click for detailed comparison results and selection rationale.</p>
    </div>
  );
}
```

**Note**: Geographic visualization is a Phase 21–22 suggestion, not a Phase 17–18 requirement. The architecture documents it for future development.

## 7. Non-Negotiable Architectural Requirements

1. **Preserve all working Phase 1–16 functionality** — no regressions
2. **Do not rewrite ResearchWorkbench.tsx unnecessarily** — extension only, not replacement
3. **Never fabricate Earth data or scientific results**
4. **Always document TMSI limitation**: "TMSI cannot establish planetary body identity" (within-body ranges overlap with between-body range)
5. **Keep TypeScript and Python code maintainable** — follow existing patterns, additive changes only
6. **Document all architectural decisions** in the relevant .md files
7. **Maintain reproducibility** — all results derivable from authenticated data and code
8. **Avoid unnecessary dependencies** — use existing modules where possible
9. **Preserve existing tests** — no test breakage
10. **Keep scientific conclusions defensible** — no overstatement beyond methodology

## 8. Readiness Assessment

| Component | Status | Phase Required |
|-----------|--------|---------------|
| Earth data acquisition module | ❌ NOT STARTED | Phase 18 |
| CRS alignment and resolution normalization | ❌ NOT STARTED | Phase 18 |
| Earth candidate registry | ❌ NOT STARTED | Phase 19 |
| Comparison engine (Earth–Moon/Mars) | ❌ NOT STARTED | Phase 20 |
| Analog ranking with uncertainty | ❌ NOT STARTED | Phase 20–21 |
| Geographic visualization | ❌ NOT STARTED | Phase 21–22 |
| Frontend Earth & Analog destination | ⚠️ EXTENSION (not rewrite) | Phase 18 (additive) |
| Preservation of all Phase 1–16 functionality | ✅ VERIFIED | — |

**Verdict**: Architecture designed and documented. Implementation requires Phases 18–22 as roadmapped. No functionality from Phase 1–16 is degraded.

---
*This architecture designs the complete Earth analog discovery workflow, extending the existing TMSI methodology from Moon–Mars comparisons to Earth–Moon/Mars when authentic Earth datasets become available. No data is fabricated. No scientific claims beyond the methodology are made. The critical TMSI limitation (within-body/between-body range overlap) is preserved throughout.*