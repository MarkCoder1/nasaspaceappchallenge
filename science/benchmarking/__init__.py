"""Terra Twin Phase 13 Benchmarking Engine.

Provides reusable infrastructure for independent DEM benchmarking,
resolution sensitivity analysis, and TMSI reproducibility experiments.

See Phase 13 specification for scientific constraints and uncertainty
categories.
"""

from . import dataset_loader, dataset_validator, dem_alignment
from . import resolution_analysis, terrain_metric_benchmark