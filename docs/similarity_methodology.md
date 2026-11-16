# TerraMatch similarity methodology

## Research question

How closely can selected Earth terrain environments approximate the measurable surface morphology of selected lunar or Martian exploration regions when compared using consistent, scale-aware topographic indicators?

The output is an analog assessment of terrain morphology. It is not a probability, habitability score, landing-site certification, or claim that Earth reproduces extraterrestrial conditions.

## Available data decision

The verified input inventory currently contains one Mars Jezero CTX DTM. NASADEM is not acquired and a lunar LOLA south-polar product is not selected. Therefore the production API exposes the engine and methodology but disables cross-body comparisons and rankings. Synthetic DEMs are used only in automated mathematical tests.

## Features

### Slope

For elevation $z$ and projected metre-per-pixel spacings $\Delta x$ and $\Delta y$:

$$
s = \arctan\left(\sqrt{\left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2}\right)
$$

The result is reported in degrees. The code uses the raster's projected metre axes and rejects rasters without an appropriate body CRS; it does not treat planetary degrees as Earth distances.

### Local relief

For a complete square neighborhood $W$ with a documented physical width of 60 m:

$$
R_{local} = \max_{p \in W}(z_p) - \min_{p \in W}(z_p)
$$

The window is converted to an odd number of native pixels. Missing cells invalidate the neighborhood rather than being filled.

### Terrain Ruggedness Index

The implemented Riley-style TRI is:

$$
TRI = \sqrt{\frac{1}{n}\sum_{p \in W, p \ne c}(z_p - z_c)^2}
$$

where $c$ is the center cell and $W$ is the complete 60 m physical window. TRI is reported in metres. This exact definition must be retained for every future dataset.

## Distribution comparison

Each feature is compared as a distribution, not by raw pixel-to-pixel alignment. The primary distance is the 1D Wasserstein distance because it has the same units as the feature and captures shifts in the full distribution. The Kolmogorov-Smirnov statistic and p-value are retained as diagnostics, not used as a scientific probability of equivalence.

The Wasserstein distance is normalized by the larger pooled interquartile range of the two feature distributions:

$$
d_i = \frac{W_i}{\max(IQR_{target}, IQR_{candidate}, \epsilon)}
$$

This makes feature distances dimensionless while retaining robust scale information. It does not erase differences in physical interpretation.

## TMSI score

For valid feature weights $w_i$:

$$
D = \frac{\sum_i w_i d_i}{\sum_i w_i}
$$

$$
TMSI = 100e^{-D}
$$

The default is equal weighting across available features. Weights are configurable and sensitivity-tested. TMSI is an index on this chosen feature set, not a percent probability or physical equivalence.

Comparisons with no shared valid features, incompatible scale, or insufficient coverage are not scored.

## Scale and coordinates

Each raster keeps its native CRS and resolution. Feature neighborhoods are specified in physical metres and converted to native pixels. No upsampling is performed. Comparisons are rejected when the coarser native pixel scale is more than four times the finer scale. A future implementation may downsample only when a scientifically justified common scale is selected.

Planetary CRSs are never transformed into Earth semantics. The current Mars raster remains in Mars 2000 Equirectangular `ESRI:103885`.

## Confidence

- `HIGH`: at least 95% valid coverage, native resolution ratio at most 2, and at least one valid feature.
- `MODERATE`: at least 80% valid coverage with identifiable scale or coverage limitations.
- `LOW`: at least 50% valid coverage but substantial missing-data limitations.
- `INSUFFICIENT`: no shared features, incompatible resolution, or less than 50% valid coverage.

These are evidence-quality labels, not calibrated probabilities.

## Missing data and uncertainty

Missing cells remain masked. No missing value is replaced with zero or an invented observation. A feature neighborhood containing missing cells is excluded from that feature distribution. Source coverage, resolution, feature definitions, and limitations are returned with each result.

## Explicit non-comparisons

Temperature, thermal inertia, reflectance, and categorical geology are not included in TMSI. Their measurement methods and physical meanings are not aligned in the verified data inventory. Absolute elevation is not compared directly across bodies; only morphology distributions can be considered after body-aware preprocessing.
