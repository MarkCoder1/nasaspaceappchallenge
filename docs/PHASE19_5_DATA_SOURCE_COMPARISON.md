# Terra Twin — Phase 19.5: Data Source Comparison

## 1. Overview

This document compares available Earth DEM data sources for Terra Twin Phase 19.5, evaluating them against the requirements of the existing Terra Twin framework: WGS84 compatibility, 20 m post spacing normalization, CRS alignment with LOLA/Mars datasets, and authentic (non-fabricated) data provenance.

## 2. Comparison Table

| Source | Provider | Resolution | Coverage | Vertical Datum | Horizontal CRS | Auth Access | State | Key Limitations |
|--------|----------|------------|----------|----------------|----------------|-------------|-------|-----------------|
| **NASADEM HGT** | NASA LP DAAC / NASA JPL | 30 m (1 arc-sec) | Global land 60°N–56°S | EGM96 geoid | WGS84 geographic | NASA Earthdata (HTTP 401) | `BLOCKED_BY_EARTHDATA_AUTHENTICATION` | HTTP 401 without credentials; no alternate validated Earth DEM in repository; does not cover polar Earth candidates |
| **Copernicus GLO-30** | ESA / Copernicus Programme | 30 m | Global | ETRS89 / UTM zone | WGS84 geographic | Copernicus Data Space Hub (registration) | `AVAILABLE_ALTERNATIVE` | Resolution coarser than LOLA/MARS 20 m native post spacing; resolution normalization required; vertical datum differs from lunar/Martian products; may require registration; not immediately downloadable without account |
| **SRTM GL3** | NASA LP DAAC / USGS | 30 m | 56°S–60°N land areas; polar gaps | WGS84 | WGS84 geographic | USGS LP DAAC (may require Earthdata login) | `MAY_CIRCUMVENT_BLOCK` | Polar gaps; may not cover all candidate regions; may still require Earthdata authentication depending on tile; 30 m resolution; normalization to 20 m required |
| **USGS 3DEP** | USGS | 1 m–30 m (varies) | US-focused; global coverage incomplete | Varies by product | Varies by product | S3 bucket (varies) | Path not identified | S3 bucket verified; 3DEP products not under discoverable prefix; USGS elevation domains fail to resolve in current environment; global coverage not confirmed |
| **ALOS AW3D30** | JAXA | 30 m | Global | — | — | Not configured | Not configured | Most promising open access global DEM; would require source configuration addition |

## 3. Compatibility Analysis

### 3.1 Resolution Normalization

All three available sources (NASADEM HGT, Copernicus GLO-30, SRTM GL3) are at 30 m resolution, while the existing LOLA and Mars datasets are at 20 m native post spacing. Resolution normalization to 20 m is required for all three:

- **Higher resolution aggregation**: If a source were at 1 m resolution, aggregate to 20 m using mean pooling (preserve elevation statistics)
- **Lower resolution documentation**: Document limitation; TMSI may be less sensitive at coarser resolution
- **Current state**: All three sources require downsampling/aggregation from 30 m to 20 m post spacing

### 3.2 CRS Alignment

| Source | CRS | Alignment with LOLA/Mars | Required Transformation |
|--------|-----|-------------------------|----------------------|
| NASADEM HGT | WGS84 geographic | Incompatible (different reference frames) | Transform to WGS84 intermediate; already WGS84 but different datum |
| Copernicus GLO-30 | ETRS89 / UTM zone | Incompatible (European terrestrial reference vs. global WGS84) | Reproject WGS84 intermediate; different datum requires explicit treatment |
| SRTM GL3 | WGS84 geographic | Partially compatible (same CRS class) | Minimal transformation; same WGS84 geographic CRS |

**Key issue**: Vertical datum differences must be explicitly documented and treated separately, not implicitly compared. The existing Terra Twin pipeline (`crs_alignment.py`) handles CRS transformation but requires explicit vertical datum documentation.

### 3.3 Authentication Requirements

| Source | Credentials Required | Registration | Key Restriction |
|--------|----------------------|--------------|-----------------|
| NASADEM HGT | Yes — Earthdata Login `urs.earthdata.nasa.gov` | Required | HTTP 401 without valid credentials; blocking condition confirmed |
| Copernicus GLO-30 | Yes — Copernicus Data Space Hub account | Free registration at `https://dataspace.copernicus.eu/` | OData API requires OAuth2 token; anonymous access returns HTTP 404 |
| SRTM GL3 | Possibly — depends on tile | Varies by tile | DNS resolution issues for USGS elevation domains (`eftl01.cr.usgs.gov`, `e4ftl01.cr.usgs.gov`); S3 bucket accessible but 3DEP products not findable |

### 3.4 Provenance and Licensing

| Source | Official URL | Licensing Notes |
|--------|-------------|-----------------|
| NASADEM HGT | `https://www.earthdata.nasa.gov/data/catalog/lpcloud-nasadem-hgt-001` | NASA Earthdata LP DAAC; requires valid credentials; licensing terms apply |
| Copernicus GLO-30 | `https://land.copernicus.eu/global-digital-elevation-model` | ESA Copernicus Programme; free data; CC-BY-4.0 or similar; registration required |
| SRTM GL3 | `https://e4ftl01.cr.usgs.gov/SRTM/SRTMGL3.003/` | USGS LP DAAC; open access; USGS terms apply |

## 4. Source Recommendation Priority

### 4.1 Priority 1: NASADEM HGT (with Credentials)

- **Pros**: Global coverage; 30 m resolution; same vertical datum (EGM96) as the existing Earth dataset entry; compatible horizontal CRS (WGS84); same provider as the blocked entry (pipeline already configured)
- **Cons**: Requires NASA Earthdata Login credentials; HTTP 401 blocking condition; must obtain and configure user credentials
- **Recommendation**: Obtain user credentials and attempt acquisition; pipeline ready

### 4.2 Priority 2: Copernicus GLO-30 (No NASA Earthdata Auth)

- **Pros**: No NASA Earthdata authentication required; global coverage; 30 m resolution; free data (registration only); ESA source aligns with existing international collaboration framework
- **Cons**: Requires Copernicus Data Space Hub account registration; vertical datum ETRS89 differs from lunar/Martian products (explicit treatment required); resolution normalization from 30 m to 20 m required
- **Recommendation**: Register for Copernicus account; attempt acquisition without NASA Earthdata credentials; document vertical datum differences

### 4.3 Priority 3: SRTM GL3 (If Accessible)

- **Pros**: Same WGS84 geographic CRS; NASA/USGS source; 30 m resolution; may circumvent NASADEM block
- **Cons**: Polar gaps (56°S–60°N); may still require Earthdata authentication depending on tile; DNS resolution issues in current environment; 30 m normalization required
- **Recommendation**: Verify tile availability from user environment; if DNS resolves, attempt acquisition; document polar gap limitations

### 4.4 Priority 4: USGS 3DEP

- **Pros**: Highest resolution (1 m–30 m); USGS authoritative source
- **Cons**: Global coverage not confirmed; S3 bucket path not identified; USGS elevation domains fail to resolve; variable vertical datum; significant integration effort
- **Recommendation**: User verifies 3DEP product path from their environment; if accessible, integrate with explicit datum documentation

## 5. No Fabricated or Synthetic Data

All source configurations and states reflect actual access situations:

- NASADEM HGT: `BLOCKED_BY_EARTHDATA_AUTHENTICATION` — confirmed HTTP 401, documented
- Copernicus GLO-30: `AVAILABLE_ALTERNATIVE` — acquisition not performed in this environment (registration required), not fabricated
- SRTM GL3: `MAY_CIRCUMVENT_BLOCK` — acquisition not performed (DNS issues), not fabricated
- USGS 3DEP: Path not identified — not fabricated

The `attempt_earth_acquisition()` function in `acquire_earth_dem.py` correctly:
- Returns appropriate state based on source availability
- Documents blocking conditions with detailed warnings
- Never fabricates downloaded datasets, benchmark results, or scientific measurements
- Always documents: source, resolution, CRS, vertical datum, access method
- Returns `None` with detailed warnings on failure

## 5. Conclusion

No currently configured Earth DEM source provides authentic, immediately accessible data without user action:

1. **NASADEM HGT** is blocked by confirmed HTTP 401 authentication requirement
2. **Copernicus GLO-30** requires registration (alternative access path available)
3. **SRTM GL3** has DNS resolution issues in current environment
4. **USGS 3DEP** path not identified in current environment

The Terra Twin Phase 18 ingestion pipeline is infrastructure-complete and ready for when authentic Earth DEM data becomes available through any of the above sources. Phase 20 quantitative Earth–Moon/Mars comparisons remain blocked for any candidate without authentic, processed Earth elevation data.

**Verdict**: `PHASE19_5_DATA_SOURCE_COMPARISON.md` — Complete with source comparison table, compatibility analysis, and priority recommendations.