from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from science.preprocessing.coordinate_systems import describe_coordinate_system
from science.preprocessing.inspect_data import inspect_raster
from science.preprocessing.normalization import min_max_normalize
from science.preprocessing.raster_processing import write_masked_elevation
from science.preprocessing.resolution import preserve_native_resolution
from science.preprocessing.units import kelvin_to_celsius
from science.preprocessing.validate_data import validate_raster


def create_synthetic_mars_raster(path: Path) -> None:
    values = np.array([[10, 20], [30, -9999]], dtype="float32")
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=2,
        height=2,
        count=1,
        dtype="float32",
        crs="ESRI:103885",
        transform=from_origin(0, 2, 20, 20),
        nodata=-9999,
    ) as dataset:
        dataset.write(values, 1)


def test_inspection_and_validation_preserve_missing_data(tmp_path: Path) -> None:
    source = tmp_path / "synthetic_mars.tif"
    create_synthetic_mars_raster(source)

    summary = inspect_raster(source, "Mars")
    validation = validate_raster(
        source,
        expected_body="Mars",
        expected_resolution=(20.0, 20.0),
        expected_units="meters",
    )

    assert summary["valid_pixel_count"] == 3
    assert summary["missing_percent"] == 25.0
    assert summary["finite_min"] == 10.0
    assert validation["shape"] == [2, 2]


def test_processed_raster_preserves_mask_and_geometry(tmp_path: Path) -> None:
    source = tmp_path / "synthetic_mars.tif"
    processed = tmp_path / "processed.tif"
    create_synthetic_mars_raster(source)
    write_masked_elevation(source, processed)

    with rasterio.open(source) as original, rasterio.open(processed) as output:
        original_values = original.read(1, masked=True)
        processed_values = output.read(1, masked=True)
        assert output.crs == original.crs
        assert output.transform == original.transform
        assert output.res == original.res
        assert np.array_equal(np.ma.getmaskarray(original_values), np.ma.getmaskarray(processed_values))
        assert np.allclose(original_values.filled(np.nan), processed_values.filled(np.nan), equal_nan=True)


def test_coordinate_resolution_units_and_normalization() -> None:
    with rasterio.io.MemoryFile() as memory:
        with memory.open(
            driver="GTiff",
            width=1,
            height=1,
            count=1,
            dtype="float32",
            crs="ESRI:103885",
            transform=from_origin(0, 20, 20, 20),
        ) as dataset:
            coordinate_system = describe_coordinate_system(dataset, "Mars")
            assert coordinate_system.identifier == "ESRI:103885"

    decision = preserve_native_resolution((20.0, 20.0))
    assert decision.resampled is False
    assert kelvin_to_celsius(273.15) == 0.0

    normalized = min_max_normalize(
        np.array([10.0, 20.0, np.nan], dtype="float32"),
        np.array([True, True, False]),
    )
    assert np.allclose(normalized[:2], [0.0, 1.0])
    assert np.isnan(normalized[2])