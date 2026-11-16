# Terra Twin — Phase 18.1: Provider Access Report

**Project:** Terra Twin  
**Phase:** 18.1 — Pre Phase 19 stabilization  
**Previous phase:** Phase 18 — Authentic Earth Dataset Integration  
**Status:** IN PROGRESS

## 1. Purpose

This report documents the official access methods, authentication requirements, and acquisition procedures for each legitimate Earth data provider investigated during Phase 18.1. No data is fabricated; all access paths and requirements are documented from official sources.

## 2. NASA Earthdata (NASADEM HGT)

### 2.1 Official Provider Information

- **Provider**: NASA LP DAAC / NASA JPL
- **Official URL**: https://www.earthdata.nasa.gov/data/catalog/lpcloud-nasadem-hgt-001
- **Product**: NASADEM HGT V001, 30 m (1 arc-second) global land between 60°N and 56°S
- **Vertical datum**: EGM96
- **Format**: HGT tiles

### 2.2 Authentication Requirements

- **Account type**: NASA Earthdata Login (free account)
- **Registration URL**: https://urs.earthdata.nasa.gov/
- **Required steps**:
  1. Visit the NASA Earthdata Login registration page
  2. Complete the registration form with valid email address
  3. Verify email address through the confirmation link
  4. Log in to the Earthdata Login portal
  5. Obtain an access token or generate credentials
- **Token handling**:
  - Environment variable: `EARTHDATA_TOKEN` or `EARTHDATA_USERNAME`
  - Token must be obtained through the official Earthdata OAuth2 flow
  - Never commit credentials to Git or print to terminal logs
  - Store locally in environment variables or `.env` file (gitignored)
- **Current status in repository**: 
  - `earth_nasadem_hgt_v001` catalog entry: state=PENDING
  - `earthdata_authentication_diagnostic.json`: documents HTTP 401 blocking condition
  - No valid credentials stored in repository

### 2.3 Access Method (OAuth2 / Protected Endpoint)

- The official data distribution endpoint is `https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/`
- This endpoint requires valid Earthdata authentication
- Without credentials, requests return HTTP 401
- The CMR (Collection Management and Retrieval) system also requires authentication for protected granules
- Public search (`https://search.earthdata.nasa.gov/`) is available without account, but actual downloads require login

### 2.4 Required User Action

1. Register for a free NASA Earthdata account at `https://urs.earthdata.nasa.gov/`
2. Verify the registered email address
3. Obtain an access token or generate credentials through the Earthdata portal
4. Configure credentials locally:
   - `export EARTHDATA_TOKEN="your_token_here"` or
   - `export EARTHDATA_USERNAME="your_username"`
5. Re-run the acquisition: `python3 -m science.data_ingestion.acquire_earth_dem nasadem_hgt`
6. Verify the acquisition succeeds and provenance is recorded

## 3. Copernicus Data Space (Copernicus GLO-30 / GLO-90)

### 3.1 Official Provider Information

- **Provider**: European Space Agency / Copernicus Programme
- **Official URL**: https://dataspace.copernicus.eu/
- **Products**:
  - Copernicus GLO-30 DEM: 30 m post spacing global
  - Copernicus GLO-90 DEM: 90 m post spacing global
- **Format**: GeoTIFF
- **Coverage**: Global

### 3.2 Authentication Requirements

- **Account type**: Free Copernicus Data Space account
- **Registration URL**: https://dataspace.copernicus.eu/
- **Required steps**:
  1. Visit `https://dataspace.copernicus.eu/`
  2. Create a free account (provide email, password, etc.)
  3. Verify the registered email address
  4. Log in to the account profile
  5. Navigate to personal information / account settings
  6. Find the option indicating interest in accessing Copernicus Contributing Missions (CCM) data
  7. Select that option and complete the requested registration information
  8. Submit the access request
  9. Wait for confirmation if approval is required (varies by user category)
- **User categories**:
  - **Public user**: May access some datasets immediately after registration
  - **Registered user**: May have additional access after approval
  - **CCM-approved user**: Required for Contributing Missions datasets (GLO-30, GLO-90)
- **Token handling**:
  - OAuth2 token required for OData API access
  - Environment variable suggestion: `COPERNICUS_ACCESS_TOKEN`
  - S3 bulk access: generated credentials after authentication
  - Never print tokens in terminal logs
  - Never commit credentials to Git
- **OData API endpoint**: `https://dataspace.copernicus.eu/odata/v1/`
- **S3 bulk access**: After authentication, generates temporary S3 credentials for direct download

### 3.3 Access Method (OData / S3 Bulk)

- **OData v1 API**: Requires OAuth2 bearer token
  - Query: `https://dataspace.copernicus.eu/odata/v1/Products?$filter=Name%20contains%20%22GLO-30%22&$format=json`
  - Download: Requires token in Authorization header
- **S3 bulk access**: After OAuth2 authentication, generates temporary S3 credentials
  - Download directly from `https://s3-eu-west-1.amazonaws.com/`
  - Faster for large files; no token needed during download
- **Public access**: The Data Space Hub frontend is publicly accessible, but actual data downloads require authentication

### 3.4 Required User Action

1. Register for a free account at `https://dataspace.copernicus.eu/`
2. Verify the registered email address
3. Complete the CCM access request process (select interest in Contributing Missions data)
4. Wait for approval confirmation (may be immediate or require review)
5. Obtain OAuth2 access token from the Copernicus portal
6. Configure the token locally:
   - `export COPERNICUS_ACCESS_TOKEN="your_token_here"`
7. Re-run the acquisition with the Copernicus source:
   - `python3 -m science.data_ingestion.acquire_earth_dem copernicus_glo_30`
8. Verify the downloaded GeoTIFF, run `verify_earth_raster()`, and process through the feature extraction pipeline
9. Record provenance in `earth_dataset_provenance.json`

## 4. USGS 3DEP (3D Elevation Program)

### 4.1 Official Provider Information

- **Provider**: U.S. Geological Survey / The National Map
- **Official URL**: https://www.usgs.gov/3d-elevation-program/
- **Data catalog**: https://data.usgs.gov/datacatalog/
- **Products**:
  - 3DEP DEM: Various resolutions (1 m, 3 m, 10 m, 30 m)
  - 1 arc-second (~30 m) DEM for conterminous US
  - Higher-resolution products for specific regions
- **Vertical datum**: NAVD88 / WGS84 (varies by product)
- **Format**: GeoTIFF,IMG, and other formats

### 4.2 Authentication Requirements

- **Account type**: Generally **no account required** for public data
- **Registration URL**: N/A (public data accessible without account)
- **Required steps**:
  1. Visit the USGS data catalog or S3 bucket
  2. Select the desired product and extent
  3. Download directly — no authentication typically required
  4. Some regional products may have restricted access; verify case-by-case
- **Current environment notes**:
  - DNS resolution for `eftl01.cr.usgs.gov` and `e4ftl01.cr.usgs.gov` fails in current environment
  - S3 bucket `prd-tnm.s3.amazonaws.com` is accessible
  - 3DEP products not findable through S3 directory listing (data may be under different prefix)
  - National Map API returns HTML (frontend-rendered) rather than JSON

### 4.3 Access Method (Direct Download / S3)

- **Direct download**: Through USGS data catalog or direct URLs
- **S3 bucket**: `https://prd-tnm.s3.amazonaws.com/`
  - Publicly accessible; no authentication required for most products
  - Data organization may not be flat; specific product paths needed
- **USGS Elevation API**: `elevation.nationalmap.gov` — may require investigation
- **ScienceBase**: `https://sciencebase.csc.gov/` — alternative access portal

### 4.4 Required User Action

1. Visit the USGS data catalog: `https://data.usgs.gov/datacatalog/`
2. Search for 3DEP DEM products
3. Select the desired product and geographic extent
4. Download the data — no account typically required
5. Verify the downloaded file:
   - Opens in rasterio/gdal
   - Has valid CRS
   - Elevation values are plausible
6. Run `verify_earth_raster(raster_path)` to validate structural integrity
7. Process through the Terra Twin Earth ingestion pipeline
8. Record provenance in `earth_dataset_provenance.json`

## 5. Summary Comparison

| Provider | Account Required | DNS Resolution (current env) | OData/API Access | Direct Download |
|----------|-----------------|------------------------------|------------------|-----------------|
| NASA Earthdata | Yes (free) | N/A (HTTP 401) | OAuth2 protected | No (HTTP 401 without creds) |
| Copernicus Data Space | Yes (free + CCM) | N/A (requires registration) | OData (token required) | After auth + token |
| USGS 3DEP | Generally no | Partial (some domains fail) | Limited (HTML frontend) | Yes (typically no account) |

## 6. Recommended Priority Order

1. **USGS 3DEP** — No account typically required; direct public download; preferred route if accessible from current environment
2. **Copernicus GLO-30** — Free account required; CCM access may be needed; more steps but global coverage
3. **NASADEM HGT** — Requires NASA Earthdata login; currently blocked in repository; roadmap for future when credentials obtained

## 7. Next Steps for Each Provider

### NASA Earthdata:
- [ ] User registers at `https://urs.earthdata.nasa.gov/`
- [ ] User verifies email and obtains token
- [ ] Configure `EARTHDATA_TOKEN` or `EARTHDATA_USERNAME`
- [ ] Re-run: `python3 -m science.data_ingestion.acquire_earth_dem nasadem_hgt`
- [ ] Verify acquisition and process through pipeline

### Copernicus Data Space:
- [ ] User registers at `https://dataspace.copernicus.eu/`
- [ ] User completes CCM access request
- [ ] User obtains OAuth2 token
- [ ] Configure `COPERNICUS_ACCESS_TOKEN`
- [ ] Re-run: `python3 -m science.data_ingestion.acquire_earth_dem copernicus_glo_30`
- [ ] Verify GeoTIFF, run validation, process features, record provenance

### USGS 3DEP:
- [ ] User visits `https://data.usgs.gov/datacatalog/`
- [ ] User searches for 3DEP DEM products
- [ ] User downloads desired product
- [ ] Verify file integrity
- [ ] Re-run: `python3 -m science.data_ingestion.acquire_earth_dem srtm_gl3` (or appropriate source)
- [ ] Verify and process through pipeline

---
*This provider access report documents the official requirements for each Earth data source. No credentials are stored in the repository. User action required for authentication on all major providers.*