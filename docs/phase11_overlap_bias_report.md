# Phase 11 Overlap Bias Report (Experiment C)

## Objective
Quantify how spatial overlap between compared windows inflates TMSI, and verify that
overlapping comparisons must not be treated as independent observations.

## Method
Controlled Moon window pairs at 10.24 km extent:
- Identical (self-comparison control): same location, two raster copies → overlap fraction 1.0.
- High overlap (~0.56): shifted by half a window.
- Partial overlap (~0.25): shifted by a quarter window.
- Non-overlapping: distinct locations.
- Overlap fraction = overlap_area / min(area_A, area_B).
- Output: `data/metadata/phase11_sampling_framework.json`.

## Results

| Pair | Overlap fraction | Overlap status | TMSI | Combined D |
|---|---|---|---|---|
| Moon center vs itself (control) | 1.0000 | identical | 100.0000 | 0.0000 |
| Moon northwest vs itself (control) | 1.0000 | identical | 100.0000 | 0.0000 |
| Moon southeast vs itself (control) | 1.0000 | identical | 100.0000 | 100.0000 → 0.0000 |
| Moon shift_half vs itself (control) | 1.0000 | identical | 100.0000 | 0.0000 |
| Moon shift_quarter vs itself (control) | 1.0000 | identical | 100.0000 | 0.0000 |
| Moon center vs shift_quarter | 0.5625 | high | 78.6150 | 0.2403 |
| Moon shift_half vs shift_quarter | 0.5625 | high | 87.9842 | 0.1285 |
| Moon center vs shift_half | 0.2500 | partial | 84.9862 | 0.1626 |
| Moon center vs northwest | 0.0000 | none | 32.6995 | 1.1188 |
| Moon center vs southeast | 0.0000 | none | 70.0514 | 0.3564 |
| Moon northwest vs southeast | 0.0000 | none | 63.8208 | 0.4496 |
| Moon northwest vs shift_half | 0.0000 | none | 40.1807 | 0.9123 |
| Moon northwest vs shift_quarter | 0.0000 | none | 15.8286 | 1.8427 |
| Moon southeast vs shift_half | 0.0000 | none | 66.9298 | 0.4029 |
| Moon southeast vs shift_quarter | 0.0000 | none | 59.3926 | 0.5209 |

## Key findings
1. **Identical windows → TMSI = 100.0** (self-comparison control confirms D = 0 for identical distributions).
2. **High overlap strongly inflates TMSI:** 0.5625 overlap → TMSI 78.62–87.98; 0.25 overlap → TMSI 84.99.
3. **Non-overlapping same-body windows span 15.83–70.05** — overlap status alone does not determine score; location matters too.
4. **Non-overlapping scores can be lower (15.83) than some high-overlap scores (87.98).** Overlap is a larger driver than body identity.
5. **Overlap and body identity are confounded:** a high-TMSI "between-body" result may simply reflect window overlap or shared terrain, not morphological similarity.

## Conclusion
Spatial overlap is a major confound. Overlapping window comparisons must be excluded from independent validation. TMSI scores cannot be compared across pairs with different overlap fractions.
