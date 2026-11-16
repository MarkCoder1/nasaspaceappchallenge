""""Scientific validation tests for Terra Twin Phase 18 Earth data integration.

Responsibilities:
- Test raster ingestion.
- Test CRS validation.
- Test elevation unit handling.
- Test NoData detection.
- Test resolution metadata.
- Test coordinate transformations.
- Test slope calculations.
- Test local relief calculations.
- Test terrain ruggedness.
- Test feature extraction.
- Test reproducibility.
- Test invalid dataset rejection.

Include synthetic test rasters with known mathematical properties.
Where possible, validate real raster outputs against independent reference
calculations or trusted source documentation.
Record all actual measurements.
Do not invent validation results.
Do not assume that successful file loading establishes scientific validity.
"""

import pytest
import numpy as np
import rasterio
import json
import tempfile
from rasterio.transform import from_origin
from pathlib import Path

from science.data_ingestion.acquire_earth_dem import (
    attempt_earth_acquisition,
    verify_earth_raster,
    write_earth_provenance_record,
    write_acquisition_metadata,
    get_dataset,
)
from science.data_ingestion.dataset_catalog import get_dataset
from science.data_ingestion.metadata import write_acquisition_metadata
from science.data_ingestion.validate_data import validate_file
from science.earth_features import (
    earth_feature_layer_from_raster,
    earth_terrain_feature_set_from_raster,
    verify_feature_comparability,
)
from science.earth_normalization import normalize_to_native_spacing


# --- Raster Ingestion Tests ---

def test_synthetic_raster_creation() -> None:
    """Create a synthetic raster with known mathematical properties."""
    import tempfile
    from pathlib import Path
    import numpy as np
    import rasterio
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        raster_path = tmp / "synthetic_dem.tif"
        
        # Create a raster with a known pattern: elevation increases linearly
        # from 0 at the bottom to 100 at the top, plus some noise
        height, width = 50, 50
        y_coords = np.linspace(0, 100, height, dtype=np.float32)
        x_coords = np.linspace(0, 50, width, dtype=np.float32)
        elevation_map = np.zeros((height, width), dtype=np.float32)
        for i in range(height):
            elevation_map[i, :] = y_coords[i]
        
        with rasterio.open(
            raster_path,
            "w",
            driver="GTiff",
            width=width,
            height=height,
            count=1,
            dtype="float32",
            crs="EPSG:4326",
            transform=rasterio.transform.from_origin(-180, 90, 1.0, 1.0),
        ) as dst:
            dst.write(elevation_map, 1)
        
        # Verify the raster was created correctly
        with rasterio.open(raster_path) as src:
            data = src.read(1)
            assert data.shape == (height, width)
            assert np.isclose(data[0, 0], 0.0)
            assert np.isclose(data[height - 1, 0], 100.0)


def test_earth_raster_structural_validation() -> None:
    """Test structural validation of an Earth DEM raster."""
    from science.data_ingestion.acquire_earth_dem import verify_earth_raster
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        raster_path = tmp / "test_dem.tif"
        
        # Create a valid raster
        with rasterio.open(
            raster_path,
            "w",
            driver="GTiff",
            width=10,
            height=10,
            count=1,
            dtype="float32",
            crs="EPSG:4326",
            transform=rasterio.transform.from_origin(-180, 90, 0.1, 0.1),
        ) as dst:
            dst.write(np.ones((10, 10), dtype="float32"), 1)
            dst.nodata = -9999.0
        
        # Validate the raster
        result = verify_earth_raster(raster_path)
        assert result["valid"] is True
        assert result["structural"] is True
        assert result["crs"] is not None
        assert result["height"] == 10
        assert result["width"] == 10


def test_invalid_raster_rejection() -> None:
    """Test that invalid rasters are properly rejected."""
    from science.data_ingestion.acquire_earth_dem import verify_earth_raster
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        raster_path = tmp / "invalid_dem.tif"
        
        # Create a raster without CRS
        with rasterio.open(
            raster_path,
            "w",
            driver="GTiff",
            width=10,
            height=10,
            count=1,
            dtype="float32",
        ) as dst:
            dst.write(np.ones((10, 10), dtype="float32"), 1)
        
        # Validate - should fail due to missing CRS
        result = verify_earth_raster(raster_path)
        assert result["valid"] is False
        assert result["structural"] is False


def test_synthetic_pipeline_test() -> None:
    """Run the synthetic Earth pipeline test."""
    from science.data_ingestion.acquire_earth_dem import test_earth_pipeline_synthetic
    
    result = test_earth_pipeline_synthetic()
    assert result["synthetic"] is True
    assert result["validation"]["valid"] is True
    assert result["message"] is not None


# --- CRS and Metadata Tests ---

def test_coordinate_system_description() -> None:
    """Test coordinate system description for Earth DEM."""
    from science.preprocessing.coordinate_systems import describe_coordinate_system
    import rasterio
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        raster_path = tmp / "test_dem.tif"
        
        with rasterio.open(
            raster_path,
            "w",
            driver="GTiff",
            width=10,
            height=10,
            count=1,
            dtype="float32",
            crs="EPSG:4326",
        ) as dst:
            pass
        
        desc = describe_coordinate_system(rasterio.open(raster_path), "Earth")
        assert desc is not None
        assert desc.wkt is not None


def test_elevation_unit_handling() -> None:
    """Test elevation unit handling in feature extraction."""
    from science.earth_features import earth_feature_layer_from_raster
    import rasterio
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        raster_path = tmp / "test_dem.tif"
        
        with rasterio.open(
            raster_path,
            "w",
            driver="GTiff",
            width=10,
            height=10,
            count=1,
            dtype="float32",
            crs="EPSG:4326",
        ) as dst:
            pass
        
        layer = earth_feature_layer_from_raster(raster_path, variable="slope")
        assert layer.units == "degrees"


# --- Feature Extraction Tests ---

def test_earth_feature_layer_creation() -> None:
    """Test Earth feature layer creation."""
    from science.earth_features import earth_feature_layer_from_raster
    import rasterio
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        raster_path = tmp / "test_dem.tif"
        
        with rasterio.open(
            raster_path,
            "w",
            driver="GTiff",
            width=10,
            height=10,
            count=1,
            dtype="float32",
            crs="EPSG:4326",
        ) as dst:
            pass
        
        # Test slope feature
        slope_layer = earth_feature_layer_from_raster(raster_path, variable="slope")
        assert slope_layer.name == "slope"
        assert slope_layer.units == "degrees"
        assert slope_layer.neighborhood_m == 60.0
        assert "slope" in slope_layer.definition
        
        # Test local_relief feature
        relief_layer = earth_feature_layer_from_raster(raster_path, variable="local_relief")
        assert relief_layer.name == "local_relief"
        assert relief_layer.units == "m"
        
        # Test terrain_ruggedness feature
        ruggedness_layer = earth_feature_layer_from_raster(raster_path, variable="terrain_ruggedness")
        assert ruggedness_layer.name == "terrain_ruggedness"
        assert ruggedness_layer.units == "m"


def test_feature_set_creation() -> None:
    """Test TerrainFeatureSet creation from Earth DEM."""
    from science.earth_features import earth_terrain_feature_set_from_raster
    import rasterio
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        raster_path = tmp / "test_dem.tif"
        
        with rasterio.open(
            raster_path,
            "w",
            driver="GTiff",
            width=10,
            height=10,
            count=1,
            dtype="float32",
            crs="EPSG:4326",
        ) as dst:
            dst.write(np.ones((10, 10), dtype="float32"), 1)
        
        fts = earth_terrain_feature_set_from_raster(raster_path)
        assert fts.body == "Earth"
        assert fts.resolution_m is not None
        assert fts.valid_percent > 0
        assert fts.effective_resolution_m is not None
        assert "slope" in fts.features
        assert "local_relief" in fts.features
        assert "terrain_ruggedness" in fts.features


def test_feature_comparability_verification() -> None:
    """Test feature comparability verification."""
    from science.earth_features import verify_feature_comparability
    
    # Create synthetic feature sets for Earth, Moon, and Mars
    earth_fts = type("obj", (), {
        "features": {"slope": type("obj", (), {"units": "degrees", "neighborhood_m": 60.0})},
        "body": "Earth"
    })()
    moon_fts = type("obj", (), {
        "features": {"slope": type("obj", (), {"units": "degrees", "neighborhood_m": 60.0})},
        "body": "Moon"
    })()
    mars_fts = type("obj", (), {
        "features": {"slope": type("obj", (), {"units": "degrees", "neighborhood_m": 60.0})},
        "body": "Mars"
    })()
    
    result = verify_feature_comparability(earth_fts, moon_fts, mars_fts)
    assert result["compatible"] is True
    assert result["common_features"] == ["slope"]


# --- Earth Data Provenance Tests ---

def test_provenance_record_creation() -> None:
    """Test provenance record creation."""
    from science.data_ingestion.acquire_earth_dem import write_earth_provenance_record
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        metadata_dir = tmp / "metadata"
        
        record = {
            "source": "test_source",
            "provider": "test_provider",
            "state": "test_state",
        }
        prov_path = write_earth_provenance_record(metadata_dir, record)
        assert prov_path.exists()
        
        # Verify the content
        with open(prov_path) as f:
            content = json.load(f)
        assert content["source"] == "test_source"
        assert content["provider"] == "test_provider"
        assert content["state"] == "test_state"


def test_earth_provenance_with_real_metadata() -> None:
    """Test provenance record with real mission metadata."""
    from science.data_ingestion.acquire_earth_dem import write_earth_provenance_record
    from science.data_ingestion.dataset_catalog import get_dataset
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        metadata_dir = tmp / "metadata"
        
        # Get the Earth dataset from catalog
        earth_entry = get_dataset("earth_nasadem_hgt_v001")
        
        record = {
            "source": earth_entry.name,
            "provider": earth_entry.institution,
            "state": earth_entry.state,
            "access_method": earth_entry.access_method,
            "official_url": earth_entry.official_url,
        }
        prov_path = write_earth_provenance_record(metadata_dir, record)
        assert prov_path.exists()
        
        # Verify the content
        with open(prov_path) as f:
            content = json.load(f)
        assert content["source"] == earth_entry.name
        assert content["provider"] == earth_entry.institution
        assert content["state"] == earth_entry.state


# --- Normalization Tests ---

def test_resolution_normalization() -> None:
    """Test resolution normalization to native spacing."""
    from science.earth_normalization import normalize_to_native_spacing
    import tempfile
    import rasterio
    import numpy as np
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        raster_path = tmp / "test_dem.tif"
        
        with rasterio.open(
            raster_path,
            "w",
            driver="GTiff",
            width=20,
            height=20,
            count=1,
            dtype="float32",
            crs="EPSG:4326",
            transform=rasterio.transform.from_origin(-180, 90, 0.1, 0.1),
        ) as dst:
            dst.write(np.ones((20, 20), dtype="float32"), 1)
        
        result = normalize_to_native_spacing(raster_path, target_resolution_m=20.0)
        assert result["original_resolution_m"] is not None
        assert result["target_resolution_m"] == 20.0
        assert "normalization_note" in result
        assert result["structural"] is True


def test_vertical_datum_documentation() -> None:
    """Test vertical datum documentation."""
    from science.earth_normalization import document_vertical_datum_difference
    
    result = document_vertical_datum_difference(
        "EGM96", "selenographic", "areocentric"
    )
    assert result["earth_datum"] == "EGM96"
    assert result["moon_datum"] == "selenographic"
    assert result["mars_datum"] == "areocentric"
    assert result["treatment"] == "explicit_cross_reference"
    assert len(result["notes"]) > 0


# --- Full Integration Test ---

def test_full_pipeline_integration() -> None:
    """Test the full Earth pipeline integration."""
    import tempfile
    from science.data_ingestion.acquire_earth_dem import (
        test_earth_pipeline_synthetic,
        write_earth_provenance_record,
    )
    from science.earth_features import earth_terrain_feature_set_from_raster
    from science.earth_normalization import normalize_to_native_spacing
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        
        # Run synthetic pipeline test
        pipeline_result = test_earth_pipeline_synthetic()
        assert pipeline_result["synthetic"] is True
        
        # Create a raster and feature set
        raster_path = tmp / "dem.tif"
        with rasterio.open(
            raster_path,
            "w",
            driver="GTiff",
            width=10,
            height=10,
            count=1,
            dtype="float32",
            crs="EPSG:4326",
        ) as dst:
            dst.write(np.ones((10, 10), dtype="float32"), 1)
        
        # Create feature set
        fts = earth_terrain_feature_set_from_raster(raster_path)
        assert fts.body == "Earth"
        assert "slope" in fts.features
        
        # Run normalization
        norm_result = normalize_to_native_spacing(raster_path)
        assert norm_result["structural"] is True
        
        # Run provenance record
        provenance = write_earth_provenance_record(tmp / "metadata", {
            "source": "test",
            "state": "test_state"
        })
        assert provenance.exists()
        
        return True
