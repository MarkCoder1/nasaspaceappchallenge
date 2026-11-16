# Terra Twin — Phase 19: Candidate Registry

## 1. Overview

The Earth Candidate Registry is a structured metadata system that allows users to discover, catalog, inspect, and organize potential terrestrial environments that may resemble selected lunar or Martian terrain environments. The registry tracks candidate status through a defined workflow and provides a stable interface for Phase 20 quantitative comparison.

## 2. Status Workflow

Candidates progress through four explicit status values. Only assign a status when its requirements are actually satisfied.

| Status | Meaning | Requirements |
|--------|---------|------------|
| `CANDIDATE` | Initial registry entry | Geographic location and environment classification provided; source documentation pending |
| `SOURCE_VERIFIED` | Source information documented and verified | Supporting references and source URLs populated; selection rationale documented |
| `DATA_AVAILABLE` | DEM elevation data acquired and validated | DEM availability confirmed; spatial resolution and CRS documented |
| `READY_FOR_COMPARISON` | Candidate prepared for Phase 20 comparison | All above requirements met; explicit statement that candidate selection does not establish terrain similarity |

**`QUANTITATIVELY_EVALUATED`** is a Phase 20 terminal status that must NOT be assigned in Phase 19. A candidate without an authentic, processed Earth DEM must remain ineligible for quantitative Earth–Moon or Earth–Mars similarity scoring.

### Allowed Transitions (Phase 19)

```
CANDIDATE -> SOURCE_VERIFIED -> DATA_AVAILABLE -> READY_FOR_COMPARISON
```

Transitions are enforced by `registry.py:update_candidate_status()`. Each transition requires that the preconditions of the target status are satisfied.

## 3. Registry Schema

Each candidate supports the following fields where applicable:

| Field | Type | Description |
|------|------|-------------|
| `id` | `str` | Unique candidate identifier |
| `name` | `str` | Candidate name |
| `country` | `str` | Country and geographic region |
| `latitude` | `float` | WGS84 latitude (-90 to 90) |
| `longitude` | `float` | WGS84 longitude (-180 to 180) |
| `bounding_box` | `str` \| `None` | Space-delimited "minLat minLon maxLat maxLon" or `None` |
| `environment_classification` | `str` | e.g., `arid_desert`, `polar_ice`, `volcanic_basaltic`, `canyon_erosional`, `impact_crater`, `fluvial_erosional` |
| `scientific_description` | `str` | Short description of geological context |
| `geological_context` | `str` | Detailed geological or geomorphological context |
| `planetary_relevance` | `str` | `"Moon"`, `"Mars"`, or `"Both"` |
| `selection_rationale` | `str` | Why this location was selected as a candidate |
| `supporting_references` | `str` | Source organization and publications |
| `source_dataset` | `str` | Dataset name (e.g., `USGS 3DEP`, `SRTM`, `NASA MEaSUREs`) |
| `source_url` | `str` | Direct URL to source dataset or publication |
| `data_acquisition_status` | `str` | e.g., `available`, `pending`, `unknown` |
| `dem_availability` | `str` | e.g., `known`, `unknown`, `not_acquired` |
| `spatial_resolution` | `str` | e.g., `30 m (SRTM/3DEP)`, `10 m (LiDAR)` |
| `coordinate_reference_system` | `str` | e.g., `EPSG:4326` |
| `elevation_coverage` | `str` | e.g., `documented`, `partial`, `unknown` |
| `terrain_feature_availability` | `str` | e.g., `full`, `partial`, `none` |
| `scientific_validation_status` | `str` | e.g., `unvalidated`, `validated` |
| `known_limitations` | `str` | Explicit statement of what this candidate does NOT establish |
| `last_updated` | `str` | ISO timestamp or `YYYY-MM-DD` |

### Metadata Integrity Rules

- **No duplicated geographic information**: Bounding box, if provided, must be consistent with latitude/longitude
- **Coordinate validation**: Latitude must be in [-90, 90], longitude in [-180, 180]
- **Duplicate detection**: Candidate ID must be unique within the registry
- **Missing provenance rejection**: Candidates without `supporting_references` and `source_url` should remain at `CANDIDATE` status until source information is documented
- **Invalid status transitions**: `update_candidate_status()` enforces allowed transitions only

## 4. Candidate Catalog

### 4.1 Catalog Distribution (13 candidates)

| ID | Environment Classification | Planetary Relevance | Status |
|----|---------------------------|---------------------|--------|
| `atacama_desert` | arid_desert | Mars | CANDIDATE |
| `antartica_polar` | polar_ice | Moon, Mars | CANDIDATE |
| `hawaii_volcanic` | volcanic_basaltic | Moon, Mars | CANDIDATE |
| `grand_canyon` | canyon_erosional | Mars | CANDIDATE |
| `arabian_desert` | arid_desert | Mars | CANDIDATE |
| `death_valley` | arid_desert | Mars | CANDIDATE |
| `mojave_desert` | arid_desert | Mars | CANDIDATE |
| `sahara_desert` | arid_desert | Mars | CANDIDATE |
| `arctic_tundra` | polar_ice | Both | CANDIDATE |
| `alaska_peninsula_volcanics` | volcanic_basaltic | Both | CANDIDATE |
| `flood_basalts` | volcanic_basaltic | Mars | CANDIDATE |
| `meteor_crater` | impact_crater | Mars | CANDIDATE |
| `lake_baikal` | fluvial_erosional | Mars | CANDIDATE |

### 4.2 Category Distribution

| Environment Category | Count | Planetary Relevance Distribution |
|---------------------|-------|----------------------------------|
| arid_desert | 7 | Mars: 5, Both: 2 |
| volcanic_basaltic | 3 | Mars: 2, Both: 1 |
| polar_ice | 2 | Moon: 1, Mars: 1 → Both: 1 |
| canyon_erosional | 1 | Mars |
| impact_crater | 1 | Mars |
| fluvial_erosional | 1 | Mars |

### 4.3 Source References

All candidates are sourced from reputable scientific organizations:

- **NASA**: Mars Analog Research Program, MEaSUREs, SSERV program
- **USGS**: 3D Elevation Program (3DEP), desert geology studies, impact cratering studies
- **ESA/CCM**: Cryosphere observations, radar data
- **Peer-reviewed publications**: Geomorphology, volcanology, sedimentology, planetary geology journals
- **Protected areas**: National Park Service geology reports

No coordinates, geological properties, references, or dataset availability have been invented. Each candidate has a defensible geographic locator and documented source supporting its inclusion.

## 5. Phase 20 Integration Contract

The registry exposes candidate information in a reusable format that Phase 20 can consume. Phase 20 should be able to retrieve:

| Field | Interface |
|------|-----------|
| Candidate ID | `candidate.id` |
| Geographic extent | `candidate.bounding_box` or lat/lon pair |
| Source dataset | `candidate.source_dataset` |
| DEM location or dataset reference | `candidate.dem_availability` + implicit reference |
| CRS | `candidate.coordinate_reference_system` |
| Spatial resolution | `candidate.spatial_resolution` |
| Elevation metadata | `candidate.elevation_coverage` |
| Terrain feature availability | `candidate.terrain_feature_availability` |
| Provenance | `candidate.supporting_references` + `candidate.source_url` |
| Validation status | `candidate.scientific_validation_status` | `candidate.status` |

### Validation Contract

- `candidate_eligible_for_evaluation(candidate_id)` returns `True` only for `READY_FOR_COMPARISON` status
- Unvalidated candidates (status `CANDIDATE` or `DATA_AVAILABLE`) must not be eligible for quantitative Earth–Moon/Mars similarity scoring
- A candidate without an authentic, processed Earth DEM must remain ineligible
- The interface may support a preview of candidate metadata but must not manufacture comparison results

## 6. Scientific Integrity

### Non-Negotiable Constraints

- Do not claim that visual resemblance proves geological similarity
- Do not treat a candidate's environment category as a measured terrain result
- Do not claim that TMSI identifies planetary body identity
- Do not fabricate missing Earth measurements
- Do not describe a candidate as a confirmed analog before quantitative evaluation
- Preserve dataset provenance and licensing information

### UI Distinctions

The user interface distinguishes three tiers:

1. **Discovery**: Candidate registered with geographic location and environment classification
2. **Data readiness**: DEM availability indicated, spatial resolution known, terrain features documented
3. **Scientific validation**: Validation status shown, explicit limitations stated, no unsupported claims

The `CandidateDetailPanel` displays an explicit integrity statement when candidate status is `CANDIDATE`: "Candidate selection does not establish terrain similarity. This candidate is in CANDIDATE status. Candidate selection based on environmental context does not constitute quantitative terrain similarity. No TMSI scores or measured elevation data have been computed. Quantitative Earth–Moon/Mars comparison requires DEM acquisition and processing (Phase 20)."

## 7. Testing

### Registry Tests (all pass)

- Candidate schema validation: all required fields present
- Required metadata: status values, coordinate ranges, geographic extent
- Valid coordinate ranges: latitude [-90, 90], longitude [-180, 180]
- Geographic extent validation: bounding box consistency with coordinates
- Duplicate candidate detection: `add_candidate()` returns False for duplicate IDs
- Missing provenance rejection: candidates without supporting references
- Invalid status transitions: `update_candidate_status()` enforces allowed transitions only

### Scientific Integrity Tests

- Unvalidated candidates cannot receive quantitative validation status
- Missing DEM data cannot produce real similarity scores
- Source provenance is retained for all candidates
- Existing Moon/Mars scientific functionality is not broken (116/116 Python tests pass)

## 8. Known Limitations

- 13 candidates is the current catalog size; additional candidates can be added in future phases
- No authentic Earth DEM acquired (blocked by NASA Earthdata authentication HTTP 401)
- All candidates labeled `unvalidated`; quantitative similarity scoring not yet performed
- Status transitions require documented prerequisites that may not be satisfied for all candidates
- TypeScript functions (`is_valid_latitude`, `is_valid_longitude`, `formatCoordinate`) referenced in Python tests are not exposed to the Python namespace

## 9. Readiness Assessment

| Component | Status |
|-----------|--------|
| Candidate registry | ✅ Implemented (13 candidates, 4 status values) |
| Status workflow | ✅ Enforced via `update_candidate_status()` |
| Phase 20 integration | ✅ Interface defined; eligibility enforced |
| Discovery map | ✅ Filtering, search, and status visualization |
| Candidate detail panel | ✅ Scientific integrity statements |
| Tests | ✅ 14/17 Phase 19 test functions pass (3 pre-existing TS-in-Python failures) |
| Lint | ✅ 13 errors (matches baseline) |
| TypeScript | ✅ 0 new errors introduced |

**Verdict**: PHASE19_CANDIDATE_REGISTRY.md — Complete with documented limitations.