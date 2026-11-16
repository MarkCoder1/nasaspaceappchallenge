"""Coordinate-system descriptions that preserve planetary CRS semantics."""

from dataclasses import dataclass

import rasterio


@dataclass(frozen=True)
class CoordinateSystem:
    body: str
    identifier: str
    wkt: str
    longitude_convention: str
    notes: str


def describe_coordinate_system(dataset: rasterio.DatasetReader, body: str) -> CoordinateSystem:
    if dataset.crs is None:
        raise ValueError("Raster has no coordinate reference system")
    identifier = dataset.crs.to_string()
    wkt = dataset.crs.to_wkt()
    if body.lower() == "mars" and "Mars" not in wkt:
        raise ValueError("Expected a Mars CRS for a Mars dataset")
    return CoordinateSystem(
        body=body,
        identifier=identifier,
        wkt=wkt,
        longitude_convention="Planetocentric longitude; source longitude domain is preserved",
        notes="Planetary body-fixed CRS; do not reinterpret coordinates as terrestrial latitude/longitude.",
    )