# Terra Twin — Phase 19: Interactive Geographic Discovery Map

## 1. Overview

The Interactive Geographic Discovery Map is a map-based interface integrated into the Terra Twin Research Workbench that allows users to view, filter, and explore registered Earth candidate locations. The map communicates candidate status through visual distinctions without implying unsupported scientific certainty.

The map uses a list-based alternative for keyboard navigation and accessibility, with candidate cards shown in a grid layout. All geographic coordinates use WGS84 (EPSG:4326).

## 2. Component Architecture

### 2.1 DiscoveryMap Component

**Location**: `frontend/components/ResearchWorkbench.tsx`

The `DiscoveryMap` component receives:
- `candidates`: `Candidate[]` — the full registry of Earth candidates
- `onCandidateSelect`: `(id: string) => void` — callback when a candidate is selected

The component manages its own filter state:
- `envFilter`: `string | null` — environment classification filter
- `planetFilter`: `string | null` — planetary target filter (Moon, Mars, Both)
- `statusFilter`: `string | null` — validation status filter (CANDIDATE, SOURCE_VERIFIED, DATA_AVAILABLE, READY_FOR_COMPARISON)
- `searchTerm`: `string` — search input for candidate names and regions

### 2.2 Filter Controls

Users can filter candidates by:

| Filter Type | Available Options | Behavior |
|------------|------------------|----------|
| **Environment** | All unique `environment_classification` values from the catalog | Radio buttons; shows only candidates matching the selected environment. "All" (no selection) shows every environment. |
| **Planetary Target** | All unique `planetary_relevance` values (Moon, Mars, Both) | Radio buttons; shows only candidates matching the selected planetary relevance. |
| **Validation Status** | CANDIDATE, SOURCE_VERIFIED, DATA_AVAILABLE, READY_FOR_COMPARISON | Radio buttons; shows only candidates with the selected status. |
| **Search** | Free text input | Matches against candidate `name` and `country` (case-insensitive substring search). |

Filters are applied simultaneously using AND logic. A candidate must match ALL active filters to be displayed.

### 2.3 Candidate Card Rendering

Each candidate is shown as a card with:

- **Status badge**: Color-coded badge showing the candidate's status (`CANDIDATE`, `SOURCE_VERIFIED`, `DATA_AVAILABLE`, `READY_FOR_COMPARISON`)
- **Planetary tag**: Tag showing `planetary_relevance` (Moon, Mars, Both)
- **Name**: Candidate name as heading
- **Location**: Formatted WGS84 coordinates (latitude, longitude)
- **Environment**: Environment classification label

### 2.4 Status Visual Encoding

The map communicates status through the following visual distinctions:

| Status | Badge Class | Label | Description |
|--------|-------------|-------|-------------|
| `CANDIDATE` | `status-badge CANDIDATE` | CANDIDATE | Unvalidated candidate; no quantitative comparison yet |
| `SOURCE_VERIFIED` | `status-badge SOURCE_VERIFIED` | SOURCE_VERIFIED | Source information verified; documentation complete |
| `DATA_AVAILABLE` | `status-badge DATA_AVAILABLE` | DATA_AVAILABLE | DEM elevation data available; ready for feature extraction |
| `READY_FOR_COMPARISON` | `status-badge READY_FOR_COMPARISON` | READY_FOR_COMPARISON | Prepared for Phase 20 quantitative comparison |

### 2.5 Empty and Error States

- **No valid candidates**: displayed when no candidates have valid WGS84 coordinates
  - Message: "No candidates with valid WGS84 coordinates are available. Add candidates with latitude and longitude to populate the map."
  - Optional search hint: "No candidates matched '{search_term}'. Clear the search term or adjust filters."

- **Empty results after filtering**: displayed when filters exclude all candidates
  - Message indicates that the filter combination matched no candidates

## 3. Accessible List-Based Alternative

When keyboard navigation or screen reader users interact with the map, a list-based alternative is provided:

```html
<strong>List-based alternative:</strong> Use the candidate cards above to
explore registered Earth environments. Each card shows name, location,
environment classification, and planetary relevance. Click a card to
view detailed candidate information.

<strong>Keyboard navigation:</strong> Tab through candidate cards; Enter
or Space to select. Focus remains within the map component.
```

The list-based alternative ensures that all users can navigate candidates regardless of input device or accessibility requirements.

## 4. Filter Synchronization

Filter controls update the component's internal state, which re-renders the candidate grid. The filter state is not persisted to URL parameters; filters are transient within a Research Workbench session.

Filter behavior:
- **Radio button selection**: Toggling a selected radio button clears the filter (sets to `null`), showing all candidates for that category
- **AND logic**: Multiple filters are applied simultaneously; a candidate must match all active filters
- **Clear all**: Selecting "All" (no filter) for each category displays every candidate

## 5. Missing Geometry Handling

Candidates with invalid WGS84 coordinates (latitude outside [-90, 90] or longitude outside [-180, 180]) are excluded from the map display but remain in the registry. A warning indicator is shown in the CandidateDetailPanel when invalid geometry is detected.

## 6. Technical Requirements

| Requirement | Implementation |
|-------------|----------------|
| WGS84 coordinates (EPSG:4326) | All candidate lat/lon stored in EPSG:4326; validated on load |
| Latitude/longitude validation | `is_valid_latitude()` and `is_valid_longitude()` functions |
| Bounding box/polygon geometry | Optional; if provided, must be consistent with lat/lon |
| Handle missing geometry gracefully | Candidates with invalid coordinates excluded from map; shown in detail panel with warning |
| Avoid duplicate candidate markers | Each candidate's `key={c.id}` ensures unique card keys |
| Responsive behavior | Grid layout adapts to screen size via CSS `map-grid` |
| Loading states | Shown during initial candidate data fetch |
| Empty states | Displayed when no candidates match filter criteria or have valid geometry |
| Error states | Graceful handling of missing/invalid geometry; warnings in detail panel |
| Accessible list alternative | Keyboard-navitable card grid with descriptive alt text |

## 7. Scientific Integrity

The UI distinguishes three tiers of data readiness:

1. **Discovery**: Candidate registered with geographic location and environment classification
2. **Data readiness**: DEM availability indicated, spatial resolution known, terrain features documented
3. **Scientific validation**: Validation status shown, explicit limitations stated, no unsupported claims

The map legend explicitly labels each status, and the CandidateDetailPanel includes an integrity statement for CANDIDATE-status candidates: "Candidate selection does not establish terrain similarity."

## 8. Known Limitations

- No interactive map provider (e.g., Leaflet, Mapbox) integrated — candidate cards shown in grid layout; a future phase may integrate a full map provider
- Filter state is transient (not URL-persisted) within a session
- Search matches against name and country only; does not search environment classification or scientific description
- Visual status distinctions communicate data readiness without implying scientific certainty or terrain similarity
- 13 candidates currently registered; map scales appropriately for this count
- No authentic Earth DEM acquired (blocked by NASA Earthdata authentication HTTP 401)

**Verdict**: PHASE19_GEOGRAPHIC_DISCOVERY_MAP.md — Complete with documented limitations.