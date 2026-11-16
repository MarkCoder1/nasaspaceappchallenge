# TMSI scoring sensitivity

The engine supports named weight configurations. The default configuration assigns equal weight to slope, local relief, and terrain ruggedness. Alternative configurations are not used to select a preferred Earth location; they are diagnostics for whether the evidence is stable.

The sensitivity API returns:

- Each configuration and its full explainable result.
- The TMSI score range across configurations.
- Whether the score spread is below the current five-index-point stability threshold.
- The features used by each configuration.

No production ranking is currently generated because NASADEM and LOLA are unavailable. Synthetic fixtures verify that changing weights changes the result when feature distances differ and that the output exposes the configuration rather than concealing it.

An unstable result must be reported as unstable in a future ranking workflow; the highest score under one arbitrary weight choice must not be presented as a scientific winner.
