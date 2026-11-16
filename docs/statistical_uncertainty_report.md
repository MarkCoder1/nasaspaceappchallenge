# Statistical uncertainty report

## Method

Terra Twin uses a non-overlapping spatial block bootstrap rather than treating every raster pixel as independent. Each feature raster is partitioned into valid blocks, blocks are sampled with replacement, and Wasserstein-normalized feature distances are recombined with the existing configured TMSI weights.

The primary experiment uses 320 m physical blocks, 64 repetitions, and seed `42`. Block-size sensitivity uses 160 m, 320 m, and 640 m blocks with 32 repetitions each.

These intervals represent spatial sampling variability under the selected block-size assumptions. They are not calibrated probabilities, sensor-error bars, or statistical significance claims. KS p-values remain diagnostics and are not interpreted as evidence of physical equivalence.

## Existing Moon-Mars experiment

- TMSI: `49.92285382858792`
- Bootstrap mean: `49.69509289955227`
- Bootstrap median: `49.830589674742086`
- 95% interval: `[43.719371995087705, 56.79848983967343]`
- Feature distance means:
  - Local relief: `0.6890919897418846`
  - Slope: `0.7068406087886738`
  - Terrain ruggedness: `0.7093909235157432`

## Block-size sensitivity

| Block size |          Mean TMSI |                           95% interval |
| ---------: | -----------------: | -------------------------------------: |
|      160 m | 49.674917905206485 | 42.30786013176713 to 55.43887888816635 |
|      320 m |  49.62664143306004 | 44.33815539252149 to 55.78433528605889 |
|      640 m |  49.75193772070786 | 45.33198779027313 to 54.35141771300922 |

The result is directionally stable across these block sizes, but the interval width demonstrates meaningful spatial uncertainty. No claim of statistical significance is made.
