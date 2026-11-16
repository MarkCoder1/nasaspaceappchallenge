from pathlib import Path

import pytest
import numpy as np
import rasterio
from rasterio.transform import from_origin

from science.data_ingestion.dataset_catalog import get_dataset
from science.data_ingestion.download_data import download_dataset
from science.data_ingestion.metadata import write_acquisition_metadata
from science.data_ingestion.validate_data import validate_file


def test_catalog_distinguishes_direct_and_credentialed_access() -> None:
    assert get_dataset("mars_jezero_ctx_dtm").download_url
    assert get_dataset("earth_nasadem_hgt_v001").download_url is None


def test_metadata_and_raster_validation(tmp_path: Path) -> None:
    dataset = get_dataset("mars_jezero_ctx_dtm")
    raster_path = tmp_path / "sample.tif"
    with rasterio.open(
        raster_path,
        "w",
        driver="GTiff",
        width=2,
        height=2,
        count=1,
        dtype="float32",
        transform=from_origin(0, 2, 1, 1),
    ) as raster:
        raster.write(np.array([[1, 2], [3, 4]], dtype="float32"), 1)

    metadata_path = write_acquisition_metadata(dataset, raster_path, tmp_path, "https://example.test/data.tif")
    result = validate_file(raster_path, metadata_path)

    assert result["driver"] == "GTiff"
    assert result["width"] == 2
    assert metadata_path.exists()


def test_download_refuses_existing_raw_file(tmp_path: Path) -> None:
    dataset = get_dataset("mars_jezero_ctx_dtm")
    existing = tmp_path / Path(dataset.download_url).name
    existing.write_bytes(b"existing")

    with pytest.raises(FileExistsError):
        download_dataset(dataset.id, tmp_path, tmp_path / "metadata")