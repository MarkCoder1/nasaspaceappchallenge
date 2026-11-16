# Terra Twin — Phase 17: Earth Data Strategy

**Project:** Terra Twin  
**Phase:** 17 of 22  
**Previous phase:** Phase 16 — ResearchWorkbench Productization  
**Status:** EARTH DATA SOURCE INVESTIGATION

## 1. Current Earth Data Status

### 1.1 Blocking Condition (Phase 16, verified)
- **Dataset**: `earth_nasadem_hgt_v001`
- **Issue**: NASA Earthdata authentication returns HTTP 401
- **Status**: BLOCKED — no authenticated Earth DEM in repository
- **Documentation**: `docs/earthdata_authentication_report.md`, `submission/LIMITATIONS.md`

### 1.2 Working Datasets (Phase 16)
- **Moon**: `moon_lola` — LOLA DEM, VALIDATED, full access ✅
- **Mars**: `mars_jezero_ctx_dtm` — Jezero Crater DTM, VALIDATED, full access ✅

## 2. Evaluated Earth Data Sources

### 2.1 Copernicus DEM (Sentinel-2 / SRTM-derived)

| Property | Value |
|----------|-------|
| **Geographic coverage** | Global, 30 m resolution |
| **Spatial resolution** | 30 m post spacing |
| **Vertical accuracy** | RMSE ~10 m (relative), absolute vertical accuracy varies by region |
| **Coordinate reference system** | ETRS89 (EU); UTM zones for global |
| **Data format** | GeoTIFF, binary floating point |
| **Licensing and attribution** | Free for commercial/non-commercial use; Copernicus data policy; requires acknowledgment |
| **Access method** | Copernicus Open Access Hub registration; no authentication HTTP 401 like NASA Earthdata |
| **Download/API availability** | Web UI download; HTTP API available; no OAuth-like flow |
| **Suitability** | Good global coverage; 30 m matches Mars DTM resolution; may differ in vertical datum from Moon/Mars datasets |

**Assessment**: Copernicus DEM is a legitimate open-access alternative to NASADEM. Would require CRS transformation (ETRS89 → likely NAD83/ WGS84 for Moon/Mars comparisons) and vertical datum documentation. No authentication barrier similar to NASA Earthdata.

### 2.2 NASA SRTM (Shuttle Radar Topography Mission)

| Property | Value |
|----------|-------|
| **Geographic coverage** | 56°S–60°N (mostly land areas); gap at poles |
| **Spatial resolution** | 30 m (original); 90 m (SRTM GL3) |
| **Vertical accuracy** | RMSE ~5–10 m (depends on latitude and topography) |
| **Coordinate reference system** | WGS84 (native) |
| **Data format** | GeoTIFF, HDR |
| **Licensing and attribution** | Free for scientific use; NASA SRTM data policy; requires acknowledgment |
| **Access method** | NASA LP DAAC; no OAuth authentication; public data |
| **Download/API availability** | Earthdata.nasa.gov; May require Earthdata login (different from NASADEM/HGT) |
| **Suitability** | Well-established; widely used in planetary comparison studies; 30 m resolution compatible with existing datasets |

**Assessment**: NASA SRTM is publicly available through LP DAAC, not through the blocked NASADEM/HGT path. Would require checking whether "NASA Earthdata authentication HTTP 401" specifically blocks SRTM access or only the HGT product. SRTM GL3 (90 m) may not match the 20 m native post spacing of the Moon/Mars datasets.

### 2.3 USGS 3DEP (3D Elevation Program)

| Property | Value |
|----------|-------|
| **Geographic coverage** | Contiguous United States; Alaska; Hawaii; Puerto Rico/USVI |
| **Spatial resolution** | 1 m (bare earth), 3 m, 1/3 arc-second (~10 m), 1 arc-second (~30 m) |
| **Vertical accuracy** | Varies by resolution: 0.5–2 m (1 m data), ~5–10 m (30 m data) |
| **Coordinate reference system** | NAD83 (CSRS) UTM; varies by region |
| **Data format** | BMP, CAD, CIB, DTED, BMP, IMG, ECW, GeoTIFF, JPEG2000, IMG, ITS, FLT, GXF, ILR, IMG, PDF, PNG, TIFF |
| **Licensing and attribution** | Free for governmental/educational use; USGS data policy; requires acknowledgment |
| **Access method** | USGS EarthExplorer, GloVIS, or Bulk Download Interface |
| **Download/API availability** | Public data; no OAuth; may require USGS account |
| **Suitability** | Limited to US regions; not global; 1 m data available for CONUS |

**Assessment**: 3DEP is excellent for US-specific analysis but not global. Would not help for general planetary comparison unless focusing on US regions only. 1 m resolution far exceeds the 20 m native post spacing of Moon/Mars datasets, requiring careful resolution normalization discussion.

### 2.4 NASADEM (HGT files)

| Property | Value |
|----------|-------|
| **Geographic coverage** | Global | 
| **Spatial resolution** | 30 m |
| **Vertical accuracy** | Depends on source SRTM data; similar to SRTM accuracies |
| **Coordinate reference system** | WGS84 |
| **Data format** | HGT (NASA DEM elevation data) |
| **Licensing and attribution** | NASA public data; requires acknowledgment |
| **Access method** | NASA Earthdata — **THIS IS THE BLOCKED PATH** (HTTP 401) |
| **Download/API availability** | HTTPS://e4ftl01.cr.usgs.gov/SRTM/SRTMGL3.003/2000.02.11/ — alternative access path exists |
| **Suitability** | Same resolution as target; but access path is the same blocked Earthdata route |

**Assessment**: NASADEM is the same product that is currently blocked. The investigation must determine whether the HTTP 401 blocks **all** NASA Earthdata products or specifically the NASADEM/HGT format. Alternative access paths (e.g., direct SRTM GL3 from USGS/LP DAAC) may circumvent the block.

### 2.5 Other Open DEM Sources

| Dataset | Coverage | Resolution | Key Note |
|---------|----------|------------|----------|
| **Viewfinder Panorama (VaP)** | Global | 90 m, 30 m (selected regions) | Open source; derived from SRTM; no authentication |
| **GMTED2010 (Global Multi-resolution Terrain Elevation Data)** | Global | 30 arc-seconds (~1 km), 1 arc-minute | Coarser resolution; not suitable for 20 m post spacing comparison |
| **ALOS World 3D (AW3D30)** | Global | 30 m | JAXA product; open access; no NASA Earthdata authentication |
| **COPERNICUS GLOVETOP** | Global | 250 m, 20 m (selected) | Coarser; not suitable for 20 m comparison |
| **OpenTopography (NSF/NIH funded)** | Select regions | 1–30 m | Requires account; no NASA Earthdata-style authentication |

**Assessment**: ALOS World 3D (AW3D30) at 30 m is the most promising alternative open global DEM. Would require resolution normalization discussion and vertical datum comparison with LOLA and Jezero Crater DTM.

## 3. Recommended Strategy

### 3.1 Priority 1: Investigate Alternative Access Paths

**Action**: Determine whether the NASA Earthdata HTTP 401 blocks all NASA products or specifically the NASADEM/HGT format.

**Methods**:
1. Test direct download from `e4ftl01.cr.usgs.gov/SRTM/SRTMGL3.003/2000.02.11/` — SRTM GL3 data without Earthdata OAuth
2. Try `urs.earthdata.nasa.gov` with anonymous/guest access
3. Check if `earthdata.nasa.gov` authentication is required specifically for NASADEM/HGT or for all products
4. If SRTM GL3 or ALOS AW3D30 are accessible without authentication, those become Priority 1 alternatives

**Rationale**: The block may be specific to the NASADEM product format (HGT) or the Earthdata OAuth flow, not all remote sensing data. If alternative sources work without authentication, Earth analog discovery can proceed without modifying the authentication infrastructure.

### 3.2 Priority 2: Acquire ALOS World 3D (AW3D30)

**Action**: Download and validate AW3D30 global 30 m DEM from JAXA.

**Properties**:
- Global coverage
- 30 m resolution (compatible with Mars DTM; needs normalization for Moon LOLA which may differ)
- JAXA open access; no NASA Earthdata authentication
- Would require vertical datum comparison and CRS alignment

**Rationale**: Most promising open-access global DEM that avoids the NASA Earthdata blocking issue entirely.

### 3.3 Priority 3: Investigate Copernicus DEM

**Action**: Download and validate Copernicus SRTM-derived DEM (30 m global).

**Properties**:
- Global coverage, 30 m resolution
- Free, no authentication required (Copernicus Open Access Hub registration only, no OAuth 401)
- Would need CRS (ETRS89 → likely WGS84) and vertical datum documentation
- Good alternative if SRTM GL3/AW3D30 are also blocked

**Rationale**: Copernicus is the most reliably open-access global DEM with no NASA Earthdata involvement.

### 3.4 Priority 4: Resolution Normalization Framework

**Action**: Develop the backend methodology for standardizing disparate resolutions.

**Required methods**:
1. **Downsampling**: If Earth DEM is higher resolution (e.g., 1 m 3DEP), aggregate to 20 m native post spacing matching Moon/Mars native spacing
2. **Upsampling (not recommended)**: If Earth DEM is lower resolution, document the limitation
3. **CRS alignment**: Transform all datasets to common coordinate reference system
4. **Vertical datum documentation**: Explicitly state differences between:
   - LOLA (Moon) — selenographic
   - Jezero Crater DTM (Mars) — planetocentric/areographic
   - Earth DEM — geoid/ellipsoidal

**Rationale**: Cross-planetary comparison requires standardized processing. The existing codebase already has `assess_resolution()` and `validate_weights()` functions that can be extended.

## 4. Technical Implementation Plan

### 4.1 Backend Modules to Develop

```python
# science/data_ingestion/earth_alternatives.py
# - Functions to download AW3D30, Copernicus DEM, SRTM GL3
# - CRS transformation: ETRS89/WGS84 → planetary CRS
# - Vertical datum documentation
# - Resolution normalization to 20 m post spacing

# science/datasets/earth_registry.py
# - Extended registry with Earth dataset entries
# - Validation functions for Earth DEM provenance
# - Access status tracking (DOWNLOADED vs BLOCKED vs AVAILABLE_ALTERNATIVE)

# similarity/earth_comparison.py
# - Extended compare_terrain with Earth dataset support
# - Resolution and weighting adjustments for cross-planetary comparison
# - Analog ranking with uncertainty quantification
```

### 4.2 Frontend Integration

- **ResearchWorkbench.tsx**: Add "DATA & METHODS" destination with Earth dataset status
- **Dataset inventory**: Show Earth alternative datasets with access status badges
- **Comparison engine**: Enable Earth–Moon/Mars comparison when Earth data is available
- **Provenance cards**: Document Earth data source, access method, and any authentication requirements

### 4.3 Data Pipeline

```
1. Attempt alternative Earth DEM download (AW3D30, SRTM GL3, Copernicus)
2. Validate raster integrity (1 band, CRS present, non-empty)
3. Transform CRS to common reference (WGS84 as intermediate)
4. Resample to 20 m native post spacing (matching Moon/Mars native)
5. Document vertical datum differences
6. Add to dataset registry with access_status="DOWNLOADED"
7. Enable TMSI comparison with Earth–Moon/Mars pairs
8. Display analog ranking with uncertainty quantification
```

## 5. Non-Negotiable Requirements (Earth Data)

1. **Never fabricate downloaded datasets, benchmark results, or scientific measurements**
2. **Never silently substitute datasets without documenting differences in resolution, processing, and provenance**
3. **Always document vertical datum differences** between Earth, Moon, and Mars datasets
4. **Always report resolution normalization methods** when Earth DEM resolution differs from 20 m native post spacing
5. **Never claim Earth integration is complete** until full provenance and validation is documented
6. **Preserve existing scientific limitations** — TMSI overlap, extent-sensitivity, and Earth data blocking must remain documented
7. **Keep all planetary comparisons scientifically defensible** — no claims beyond what the documented methodology supports
8. **Document all architectural decisions** regarding Earth data source selection and processing

## 5. Readiness Assessment

| Step | Status | Action |
|------|--------|--------|
| NASA Earthdata block documented | ✅ | Verified HTTP 401 for earth_nasadem_hgt_v001 |
| Alternative sources evaluated | ❌ | Not yet investigated |
| AW3D30 acquired and validated | ❌ | Not yet attempted |
| Copernicus DEM investigated | ❌ | Not yet attempted |
| Resolution normalization framework | ❌ | Would extend existing assess_resolution() |
| Earth–Moon/Mars comparison engine | ❌ | Would extend compare_terrain() |
| Frontend Earth data display | ❌ | Would extend ResearchWorkbench.tsx (but NOT rewrite unnecessarily) |
| Analog ranking with uncertainty | ❌ | Would extend bootstrap_tmsi() and classification |

**Verdict**: Earth data investigation is the critical path for Phases 18–22. Priority must be given to determining whether alternative access paths circumvent the NASA Earthdata HTTP 401 block. No Earth analog results should be fabricated or displayed until authentic data is acquired and validated.

---
*This strategy investigates authentic, accessible Earth elevation datasets as alternatives to the blocked NASA Earthdata authentication. No datasets are fabricated. No scientific results are invented. All findings are documented with full provenance and any access limitations clearly stated.*