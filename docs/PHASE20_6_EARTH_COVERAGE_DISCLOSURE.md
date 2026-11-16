# Terra Twin — Phase 20.6: Earth Geographic Coverage Disclosure

## 1. Executive Summary

**CORRECTION: RESOLVED**

Earth comparisons use USGS 3DEP 1-arc-second DEM data from only two tiles covering the Death Valley / southern Arizona region (approximately 35°N–37°N, 116°W–117°W). This limited geographic coverage is now prominently disclosed in all Earth comparison results, candidate detail views, and scientific metadata.

## 2. Earth DEM Coverage Details

| Tile | Latitude Range | Longitude Range | Region |
|------|---------------|-----------------|--------|
| USGS_1_n36w117 | 34.9983°N – 36.0017°N | 117.0017°W – 115.9983°W | Southern Arizona / Death Valley vicinity |
| USGS_1_n37w117 | 35.9983°N – 37.0017°N | 117.0017°W – 115.9983°W | Central Valley, California |

**Combined coverage:** Approximately 35°N–37°N, 116°W–117°W (Death Valley and southern Arizona desert region).

## 3. Code Changes

### 3.1 `science/similarity/scoring/similarity.py`

Added geographic coverage limitation when either target or candidate has `body == "Earth"`:

> "Earth coverage is limited to two USGS 3DEP tiles (Death Valley / southern Arizona region, approximately 35°N–37°N, 116°W–117°W). These samples cannot establish global terrestrial terrain representativeness; results apply only to the sampled regions."

### 3.2 Comparison Limitations

All Earth comparison JSON files now include the coverage disclosure in their `limitations` array.

## 4. Required Scientific Distinction

The following statement is now present in all Earth comparison outputs:

> "The Earth comparisons characterize the available sampled regions, primarily Death Valley and southern Arizona. They do not establish global terrestrial terrain representativeness."

## 5. Impact on Comparisons

| Comparison | Earth Coverage | Generalizability |
|------------|---------------|------------------|
| Moon–Mars | N/A (no Earth data) | N/A |
| Earth–Moon | Two USGS tiles (Death Valley region) | Limited to sampled region |
| Earth–Mars | Two USGS tiles (Death Valley region) | Limited to sampled region |

## 6. Frontend Display

Candidate detail panels and ResearchWorkbench displays now include the geographic coverage limitation when displaying Earth candidate data.

## 7. Classification

**Earth Geographic Coverage Disclosure: RESOLVED**

Limited geographic coverage is now prominently disclosed in all Earth comparison outputs, candidate detail views, and scientific metadata. The distinction between sampled regions and global representativeness is clearly stated.