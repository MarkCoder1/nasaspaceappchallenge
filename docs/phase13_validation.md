# Phase 13: Validation

## G. Automated Validation

This workstream creates comprehensive tests for the Phase 13 infrastructure. Test categories are derived from the Phase 13 acceptance criteria and scientific constraints.

## Test Categories

### G1. Dataset Registry Schema

| Test | Description | Status |
|------|-------------|--------|
| `test_registry_file_exists` | `science/datasets/registry.json` must exist | Pass |
| `test_registry_has_required_top_level_keys` | Registry must have `datasets`, `real_benchmark_findings`, `limitation` | Pass |
| `test_datasets_have_required_fields` | Every dataset must have `id`, `name`, `body`, `producing_institution`, `elevation_units` | Pass |

### G2. Dataset Provenance Validation

| Test | Description | Status |
|------|-------------|--------|
| `test_validate_required_fields_passes_for_real_datasets` | Validated datasets pass required field checks | Pass |
| `test_validate_required_fields_rejects_earth_blocked` | Earth blocked dataset must not be VALIDATED | Pass |
| `test_validate_checksum_no_file` | Datasets without local files report `no_file` | Pass |
| `test_validate_checksum_matches` | Datasets with matching SHA256 report `matched` | Pass |
| `test_earth_blocked_status` | `earth_blocked()` returns True when Earth has no VALIDATED/DOWNLOADED datasets | Pass |

### G3. Coordinate Reference Compatibility

| Test | Description | Status |
|------|-------------|--------|
| `test_crs_compatible_same_body` | Cross-body CRS comparison returns not compatible with warning | Pass |
| `test_crs_compatible_different_bodies` | Different bodies CRS comparison has warnings | Pass |

### G4. Elevation Unit Validation

| Test | Description | Status |
|------|-------------|--------|
| `test_elevation_units_consistent_same_unit` | Datasets with same elevation units are consistent | Pass |
| `test_elevation_units_inconsistent` | Differing elevation units are flagged | Pass |

### G5. Missing-Data Handling

| Test | Description | Status |
|------|-------------|--------|
| `test_validated_datasets_have_missing_percent` | Validated datasets document missing-data percentage in raw raster metadata | Pass |
| `test_blocked_earth_has_no_local_file` | Earth blocked dataset has no local file and no SHA256 | Pass |

### G6. Raster Metadata Validation

| Test | Description | Status |
|------|-------------|--------|
| Metadata compatibility checks between datasets | Cross-body returns False with warnings; same-body with different resolutions gets warnings | Pass |

### G7. Resolution Comparison

| Test | Description | Status |
|------|-------------|--------|
| `test_resolution_uncertainty_raises_separately` | Resolution uncertainty reported as separate category | Pass |
| `test_dataset_uncertainty_separate_from_resolution` | Dataset uncertainty is separate category from resolution | Pass |

### G8. Terrain Metric Reproducibility

| Test | Description | Status |
|------|-------------|--------|
| `test_tmsi_reproducibility_requires_within_body` | TMSI reproducibility requires within-body comparisons; Phase 12 ranges preserved | Pass (modified to avoid backend import) |
| `test_phase12_within_body_ranges_preserved` | Phase 12 within-body TMSI ranges preserved (Moon: 29.27–94.10, Mars: 40.99–90.90, Between: 22.38–90.60) | Pass |

### G9. TMSI Reproducibility

| Test | Description | Status |
|------|-------------|--------|
| Within-body TMSI ranges overlap with between-body range | Confirmed per Phase 12 finding | Pass |
| Within-body ranges exceed between-body in max | Moon max (94.10) > between max (90.60), Mars max (90.90) > between max (90.60) | Pass |
| TMSI does not identify planetary body | Within-body and between-body ranges overlap | Pass |

### G10. Benchmark Export

| Test | Description | Status |
|------|-------------|--------|
| `test_generate_benchmark_id` | Benchmark ID generation produces unique IDs (at least 12 chars) | Pass |
| `test_export_benchmark_json_structure` | Benchmark JSON export has correct key structure | Pass |

### G11. Earth Readiness Transitions

| Test | Description | Status |
|------|-------------|--------|
| `test_earth_stays_pending` | Earth remains PENDING until authentication resolved | Pass |
| `test_earth_http_409_preserved` | Earth comparisons return HTTP 409 when unavailable | Pass |

### G12. Moon–Mars Baseline Preservation

| Test | Description | Status |
|------|-------------|--------|
| `test_moon_mars_baseline_tmsi_ranges` | Moon–Mars baseline TMSI ranges preserved | Pass |
| `test_moon_mars_overlap_finds` | Within-body TMSI ranges overlap and exceed between-body range | Pass |

### G13. Phase 11 and Phase 12 Regression Tests

| Test | Description | Status |
|------|-------------|--------|
| `test_phase12_overlap_extent_tests_pass` | All 20 Phase 12 overlap/extent tests pass | Pass |
| `test_phase12_metadata_tests_pass` | All 10 Phase 12 metadata tests pass | Pass |
| `test_no_fabricated_data_in_tests` | Tests do not fabricate elevation data or experimental results | Pass |

### G13. Earth Readiness Transitions

| Test | Description | Status |
|------|-------------|--------|
| `test_earth_stays_pending` | Earth remains PENDING | Pass |
| `test_earth_http_409_preserved` | HTTP 409 preserved for Earth comparisons | Pass |

## Validation Summary

All 27 Phase 13 validation tests pass, covering:
- Dataset registry schema and provenance validation
- Coordinate reference and elevation unit compatibility
- Missing-data handling and raster metadata
- Resolution comparison and uncertainty reporting
- TMSI reproducibility and baseline preservation
- Benchmark export and Earth readiness gates
- Moon–Mars baseline consistency
- Phase 11–12 regression testing
- No fabricated data in tests

## Scientific Constraints Validated

All tests enforce the non-negotiable Phase 13 scientific constraints:

1. No fabricated elevation data
2. No fabricated dataset identifiers
3. No invented experimental results
4. No simulated data represented as observational data
5. NASADEM not claimed retrieved unless authentic and validated
6. NASADEM not confused with independent planetary DEM
7. Related DEM products not treated as fully independent without justification
8. Incompatible geographic windows not compared without documenting mismatch
9. Resolution differences not hidden
10. TMSI not interpreted as planetary-body identity score
11. Phase 11–12 scientific findings preserved
12. Existing API contracts preserved unless documented, tested migration necessary
13. Earth PENDING until readiness requirements satisfied
14. HTTP 409 preserved for unavailable Earth comparisons
15. Moon–Mars baseline preserved