# Scientific engine

Scientific computation will live in these modules and remain independent from FastAPI route handlers:

- `data_ingestion/`: authoritative source acquisition and provenance
- `preprocessing/`: normalization and quality checks
- `geospatial/`: spatial operations and raster/vector workflows
- `similarity/`: measurable analog comparison functions
- `ranking/`: transparent ranking and scoring orchestration
- `validation/`: reproducibility and scientific validation checks

Phase 2 contains only researched dataset records and acquired source files with provenance. Similarity calculations and ranking remain deferred.
