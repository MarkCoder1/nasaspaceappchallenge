# Phase 13: Earth Integration

## C1. Authentication Investigation

### Existing Authentication Implementation
The Terra Twin backend implements NASA Earthdata Login authentication for accessing protected LP DAAC granules. The current status is:

- **Authentication status**: UNAVAILABLE
- **Error encountered**: HTTP 401 (Unauthorized) when attempting to access protected granules
- **CMR query performed**: `https://cmr.earthdata.nasa.gov/search/granules.json?collection_concept_id=C2763264762-LPCLOUD&bounding_box=-68,-24,-67,-23&page_size=10`
- **Result**: Protected granules redirect to NASA Earthdata OAuth and return HTTP 401 without valid user credentials

### Error Diagnostic
The earthdata_authentication_diagnostic.json file documents the authentication failure:

```json
{
  "access_status": "BLOCKED_BY_EARTHDATA_AUTHENTICATION",
  "message": "The official lp-prod-protected granule redirects to NASA Earthdata OAuth and returns HTTP 401 without user credentials.",
  "details": "No credentials were supplied or stored. This manifest is provenance for an attempted acquisition, not an observation file."
}
```

### Investigated Solutions
1. **NASA Earthdata Login credentials**: Not available in the current repository environment
2. **Alternative authentication flows**: Investigated but not successfully configured
3. **Publicly accessible datasets**: Sought but NASADEM is a protected product requiring LP DAAC credentials

### Current Position
- Earthdata authentication remains blocked
- No authentic NASADEM raster was acquired or validated locally
- Earth stays in PENDING status
- Earth–Moon and Earth–Mars comparisons return HTTP 409 (Conflict)

## C2. NASADEM Retrieval

### Attempted Acquisition
- **Dataset**: NASADEM Merged DEM Global 1 arc second V001
- **Source**: NASA Earthdata LP DAAC
- **CMR Collection**: C2763264762-LPCLOUD
- **Query performed**: Bounding box -68 to -67, -24 to -23 (Atacama region)
- **Result**: Protected granules returned HTTP 401. No local file acquired.

### What "Authentic NASADEM" Means
- Must be retrieved from official NASA Earthdata LP DAAC
- Must have valid CMR metadata and granule provenance
- Must not be substituted with an alternate dataset (e.g., SRTM, AW3D30)
- Must be validated for file integrity (SHA256 checksum), coordinate reference, and elevation units

> **Never represent simulated data as observational data.** Never confuse NASADEM with an independent planetary DEM. Never treat related DEM products as fully independent without justification.

## C3. Earth Readiness

### Current Status: PENDING

Earth will only transition from PENDING when all required checks pass:

- [ ] Authentic dataset acquired (currently blocked by Earthdata authentication)
- [ ] Dataset provenance recorded (CMR collection, granule ID, access logistics)
- [ ] Raster successfully validated (SHA256, CRS, elevation units)
- [ ] Coordinate systems verified (WGS84 geographic, EGM96 vertical)
- [ ] Elevation units verified (meters, EGM96 geoid)
- [ ] Required terrain metrics successfully computed (would require acquired data)
- [ ] Regression tests pass (currently Phase 11–12 tests pass)

### Until Then:
- Earth stays PENDING
- Earth–Moon comparisons return HTTP 409
- Earth–Mars comparisons return HTTP 409
- No Earth results are displayed as completed experiments
- The ResearchWorkbench shows Earth status as "PENDING · Earthdata authentication unresolved"

### Path to READY
When NASA Earthdata authentication is resolved:

1. Acquire a small test region of NASADEM data
2. Verify the response is a real raster (valid GeoTIFF/HDF)
3. Validate file integrity (SHA256 checksum matches)
4. Inspect raster metadata (resolution, CRS, extent)
5. Verify spatial reference information (WGS84, EGM96)
6. Verify elevation units (meters, EGM96 geoid)
7. Compute required terrain metrics (slope, relief, TRI, TMSI)
8. Run all regression tests (Phase 11, Phase 12, Phase 13)
9. Transition Earth status from PENDING to VALIDATED
10. Enable Earth–Moon and Earth–Mars comparisons (remove HTTP 409)

> **Note**: Even after Earth data is acquired, the principle of independent dataset benchmarking (Phase 13 B1–B4) must be upheld. Earth DEM results should be benchmarked against independent datasets where possible, and all uncertainty categories should be reported.

## Earth Comparison Gates

The backend implements HTTP 409 for unavailable Earth comparisons:

```python
# Earth gate - from backend similarity service
if dataset_a.body == "Earth" or dataset_b.body == "Earth":
    if earth_blocked():
        raise HTTPException(status_code=409, detail="Earth comparisons unavailable: NASADEM authentication required")
```

This gate is enforced in the ResearchWorkbench UI, where Earth comparisons are disabled with the message: "Earth ↔ Moon and Earth ↔ Mars disabled. Earthdata authentication unavailable; protected granules returned HTTP 401."