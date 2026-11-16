"""Centralized, explicit unit conversions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UnitConversion:
    variable: str
    original_unit: str
    processed_unit: str
    formula: str
    applied: bool


def elevation_meters() -> UnitConversion:
    return UnitConversion(
        variable="elevation",
        original_unit="m",
        processed_unit="m",
        formula="identity: elevation_m = elevation_m",
        applied=False,
    )


def kelvin_to_celsius(kelvin: float) -> float:
    return kelvin - 273.15


def temperature_kelvin_to_celsius() -> UnitConversion:
    return UnitConversion(
        variable="surface_temperature",
        original_unit="K",
        processed_unit="degC",
        formula="temperature_degC = temperature_K - 273.15",
        applied=False,
    )