# Terra Twin — Phase 20.6: Vertical Datum Transparency

## 1. Executive Summary

**CORRECTION: RESOLVED**

Vertical datum differences between Earth (NAVD88), Moon (LOLA project datum), and Mars (delta geoid/MOLA control) are now explicitly documented as unquantified limitations in all Earth comparison results.

## 2. Vertical Datum Comparison

| Dataset | Vertical Datum | Reference Surface |
|---------|---------------|-------------------|
| Earth USGS 3DEP | NAVD88 | North American Vertical Datum 1988 |
| Moon LOLA | LOLA project datum | Lunar reference surface |
| Mars Jezero CTX DTM | Delta geoid (MOLA control) | Martian reference surface |

## 3. Code Changes

### 3.1 `science/similarity/scoring/similarity.py`

Added vertical datum limitation when either target or candidate has `body == "Earth"`:

> "Vertical datum difference: Earth uses NAVD88; Moon uses LOLA project datum; Mars uses delta geoid (MOLA control). Vertical datum differences are unquantified and may affect elevation-based feature comparisons (slope, local relief, terrain ruggedness)."

## 4. Important Scientific Distinction

**Vertical datum differences are NOT corrected:**

- No vertical datum transformation is applied
- No correction factor is estimated
- Elevation values are compared in their native datums
- The difference is explicitly documented as unquantified

## 5. Impact on Comparisons

| Comparison | Earth Datum | Moon/Mars Datum | Quantified? |
|------------|-------------|-----------------|-------------|
| Moon–Mars | N/A | LOLA / Delta geoid | N/A |
| Earth–Moon | NAVD88 | LOLA project datum | No (documented as unquantified) |
| Earth–Mars | NAVD88 | Delta geoid | No (documented as unquantified) |

## 6. Why No Correction Is Applied

1. No validated transformation method exists between NAVD88 and lunar/Martian datums
2. Applying an unverified correction would introduce unquantified error
3. The difference is explicitly documented rather than hidden
4. Comparisons remain labeled as CONDITIONALLY READY due to this limitation

## 7. Classification

**Vertical Datum Transparency: RESOLVED**

Vertical datum differences are explicitly documented as unquantified limitations in all Earth comparison outputs. No transformation is applied or claimed.