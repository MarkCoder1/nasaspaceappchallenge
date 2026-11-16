# Phase 7 scientific validation report

## Verdict: READY WITH LIMITATIONS

The existing Moon-Mars TMSI result is reproducible and has been independently stress-tested with 1,000 spatial-block bootstrap repetitions, feature ablation, weight sensitivity, normalization diagnostics, and spatial autocorrelation measurements. Earth remains `PENDING` because NASADEM authentication is unresolved. No real independent benchmark dataset was available, so benchmark evidence is explicitly incomplete.

## Reproducibility

The generated experiment artifact is [moon_mars_phase7_experiments.json](../data/metadata/moon_mars_phase7_experiments.json). It records input manifests and processed checksums, bounds, dimensions, CRSs, resolutions, effective resolution, feature definitions and parameters, masks, distance metrics, normalization, weights, bootstrap seeds, software versions, and execution time.

The official baseline is reproduced exactly:

- TMSI: `49.92285382858792`
- Confidence: `HIGH`
- Strongest feature matches: slope and local relief

## Bootstrap validation

The primary 320 m experiment used 1,000 repetitions and seed `42`:

- Mean: `49.93214617884011`
- 95% interval: `[42.59005785005729, 57.153579453411744]`

Convergence at 320 m:

| Repetitions |              Mean |         Lower 95% |          Upper 95% |
| ----------: | ----------------: | ----------------: | -----------------: |
|          64 | 49.73796848740175 | 42.65988735789199 |  56.61495993646561 |
|         256 | 50.16995712890419 | 42.90959738120566 |  57.21470112890419 |
|        1000 | 49.93214617884011 | 42.59005785005729 | 57.153579453411744 |

Seed sensitivity was evaluated with seeds `42`, `123`, and `987` at 256 repetitions. Block-size sensitivity used 160 m, 320 m, and 640 m. The resulting intervals overlap substantially, but remain wide enough that the score should not be read as a precise physical equivalence estimate.

Spatial blocks are not assumed independent observations. The bootstrap quantifies variability under a block-resampling assumption; it does not calibrate measurement uncertainty or probability of similarity.

## Feature ablation

| Configuration                |       Direct TMSI |    Bootstrap mean |                            95% interval |
| ---------------------------- | ----------------: | ----------------: | --------------------------------------: |
| Slope only                   | 50.38759096672298 |  50.8859753010354 |   38.18921715850345 to 62.0345960950001 |
| Local relief only            | 50.24460531119791 | 50.50653535227073 |  38.13168134672365 to 61.07225715660336 |
| Terrain ruggedness only      | 49.14566058278336 | 49.70023647876303 | 36.833778828813145 to 60.90961559730554 |
| All three, official baseline | 49.92285382858792 | 49.93214617884011 | 42.59005785005729 to 57.153579453411744 |

Slope and local relief are the strongest individual matches under this configuration. Ruggedness contributes a lower individual index, but the differences are within broad spatial uncertainty intervals.

## Weight and normalization sensitivity

Direct TMSI under alternative weights:

- Equal: `49.92285382858792`
- Slope emphasis: `50.038634712167976`
- Local-relief emphasis: `50.003098019418736`
- Ruggedness emphasis: `49.72741079949528`

The interpretation is directionally stable: no tested reasonable weighting produces a materially different conclusion from the official equal-weight baseline. The official normalization remains pooled IQR. A pooled-standard-deviation diagnostic is recorded in the experiment artifact but is not used as the production score.

## Spatial structure

Moran's I was strongly positive for all measured features:

| Body |  Slope | Local relief | Ruggedness |
| ---- | -----: | -----------: | ---------: |
| Mars | 0.9790 |       0.9826 |     0.9835 |
| Moon | 0.9899 |       0.9947 |     0.9953 |

Semivariograms were also calculated at 20, 40, 80, 160, 320, and 640 m lags. These results confirm strong spatial organization and reinforce that pixel-level independence assumptions would be inappropriate. Spatial diagnostics are intentionally separate from TMSI.

## Benchmarking

The benchmark registry contains only synthetic mathematical fixtures for software tests. No independently labeled real terrain benchmark was available in the verified repository, so no benchmark success claim is made. Synthetic fixtures are never exposed through production API results.

## Scientific interpretation

TMSI compares distributions of slope, local relief, and Riley TRI at compatible physical scales. It does not measure spatial arrangement completely, absolute cross-body elevation equivalence, habitability, atmospheric conditions, gravity, radiation, thermal state, landing safety, or settlement suitability. `HIGH` confidence means valid coverage and native-scale compatibility under the configured evidence rules; it is not a probability.

## Questions for independent reviewers

1. Is a 320 m primary block size appropriate for these two terrain products, given the observed semivariograms?
2. Should the effective-resolution ancillary alter the feature neighborhood or only the compatibility gate?
3. Is pooled IQR the most defensible robust scale for these feature distributions?
4. What independent real benchmark regions and labels would be appropriate without using Terra Twin's own score to define the labels?
5. Which spatial descriptors should be added before interpreting morphology beyond distribution similarity?

## Remaining limitations

- Earth NASADEM is still pending authentication and validation.
- Earth-Moon and Earth-Mars experiments have not executed.
- No independent real benchmark findings exist.
- The Moon input is a bounded 40.96 km subset, not the complete parent DEM.
- The result is not evidence of physical equivalence between Earth, Moon, or Mars.
