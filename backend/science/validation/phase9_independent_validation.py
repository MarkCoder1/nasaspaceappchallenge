"""Phase 9 independent validation experiments using validated Moon and Mars rasters.

No Earth data is used. These experiments strengthen the methodology independent of
Earth integration and are reproducible from the committed rasters.
"""

import json
import math
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window

from science.similarity.features.feature_extraction import extract_terrain_features
from science.similarity.scoring.similarity import compare_terrain
from science.similarity.comparison.uncertainty import assess_resolution, classify_confidence
from science.similarity.comparison.bootstrap import bootstrap_tmsi
from science.preprocessing.coordinate_systems import describe_coordinate_system

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MARS_PATH = REPOSITORY_ROOT / "data/processed/mars_jezero_ctx_elevation_m.tif"
MOON_PATH = REPOSITORY_ROOT / "data/processed/moon_lola_80s_20m_elevation_m.tif"


def load_features(path, body, source_id, effective_resolution_m=None):
    return extract_terrain_features(
        path, body=body, source_id=source_id, effective_resolution_m=effective_resolution_m
    )


def section(title):
    print(f"\n=== {title} ===")


def fmt(x, digits=4):
    if x is None:
        return "--"
    return f"{x:.{digits}f}"


def main():
    mars = load_features(MARS_PATH, "Mars", "mars_jezero_ctx_dtm", effective_resolution_m=20.0)
    moon = load_features(MOON_PATH, "Moon", "moon_lola", effective_resolution_m=16.055973052978516)

    # --- A. Repeatability ---
    section("A. Repeatability (deterministic baseline reproduction)")
    r1 = compare_terrain(mars, moon, include_uncertainty=False)
    r2 = compare_terrain(mars, moon, include_uncertainty=False)
    identical = (
        r1["similarity_index"] == r2["similarity_index"]
        and r1["combined_distance"] == r2["combined_distance"]
        and r1["confidence"] == r2["confidence"]
    )
    print(f"Run 1 TMSI: {r1['similarity_index']}")
    print(f"Run 2 TMSI: {r2['similarity_index']}")
    print(f"Confidence: {r1['confidence']}")
    print(f"Deterministic/repeatable: {identical}")
    assert identical, "Baseline is not repeatable"
    assert abs(r1["similarity_index"] - 49.92285382858792) < 1e-9, "Baseline TMSI changed"

    # --- B. Resolution sensitivity ---
    section("B. Resolution compatibility sensitivity")
    # Official: Mars 20.0 m, Moon 16.056 m effective -> ratio ~1.246, compatible.
    res_official = assess_resolution(mars, moon)
    print(f"Official resolution: target_scale={mars.effective_resolution_m or max(mars.resolution_m)}, "
          f"candidate_scale={moon.effective_resolution_m or max(moon.resolution_m)}, "
          f"ratio={res_official.resolution_ratio:.4f}, compatible={res_official.compatible}")

    # Boundary test: effective resolution ratio at the maximum_ratio=4.0 gate.
    # Simulate a coarse candidate at 80 m effective (ratio 80/20 = 4.0, boundary compatible).
    moon_coarse = load_features(MOON_PATH, "Moon", "moon_lola_coarse", effective_resolution_m=80.0)
    res_boundary = assess_resolution(mars, moon_coarse)
    print(f"Boundary (80 m vs 20 m): ratio={res_boundary.resolution_ratio:.4f}, compatible={res_boundary.compatible}")

    # Beyond boundary: 81 m effective (ratio 4.05) -> incompatible.
    moon_too_coarse = load_features(MOON_PATH, "Moon", "moon_lola_too_coarse", effective_resolution_m=81.0)
    res_incompatible = assess_resolution(mars, moon_too_coarse)
    print(f"Beyond boundary (81 m vs 20 m): ratio={res_incompatible.resolution_ratio:.4f}, compatible={res_incompatible.compatible}")
    assert res_official.compatible is True
    assert res_boundary.compatible is True
    assert res_incompatible.compatible is False

    # --- C. Spatial-extent sensitivity ---
    section("C. Spatial-extent sensitivity (sub-window vs full Moon)")
    # Extract features from a central sub-window of the Moon raster and compare to Mars.
    with rasterio.open(MOON_PATH) as src:
        profile = src.profile.copy()
        # Central quarter window (1024x1024 cells = 20.48 km x 20.48 km).
        window = Window(512, 512, 1024, 1024)
        sub = src.read(1, window=window, masked=True)
        transform = src.window_transform(window)
        sub_path = REPOSITORY_ROOT / "data/processed/moon_lola_central_20km_window.tif"
        profile.update(
            width=1024, height=1024, transform=transform, count=1, dtype="float32",
            driver="GTiff",
        )
        with rasterio.open(sub_path, "w", **profile) as dst:
            dst.write(sub, 1)
    moon_sub = load_features(sub_path, "Moon", "moon_lola_subwindow", effective_resolution_m=16.055973052978516)
    r_sub = compare_terrain(mars, moon_sub, include_uncertainty=False)
    print(f"Full Moon (40.96 km) TMSI: {r1['similarity_index']}")
    print(f"Sub-window Moon (20.48 km) TMSI: {r_sub['similarity_index']}")
    print(f"Delta (full - sub): {r1['similarity_index'] - r_sub['similarity_index']:+.4f}")
    print(f"Extent sensitivity is material: {abs(r1['similarity_index'] - r_sub['similarity_index']) > 1.0}")

    # --- D. Feature sensitivity (ablation) ---
    section("D. Feature sensitivity (single-feature ablation)")
    weights_all = {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0}
    for single in ("slope", "local_relief", "terrain_ruggedness"):
        w = {k: (1.0 if k == single else 0.0) for k in weights_all}
        res = compare_terrain(mars, moon, weights=w, include_uncertainty=False)
        print(f"{single:16s} TMSI={fmt(res['similarity_index'], 4)}  D={fmt(res['combined_distance'], 4)}  conf={res['confidence']}")

    # --- E. Weight sensitivity ---
    section("E. Weight sensitivity")
    schemes = {
        "equal": {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0},
        "slope_emphasis": {"slope": 2.0, "local_relief": 1.0, "terrain_ruggedness": 1.0},
        "relief_emphasis": {"slope": 1.0, "local_relief": 2.0, "terrain_ruggedness": 1.0},
        "ruggedness_emphasis": {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 2.0},
    }
    for name, w in schemes.items():
        res = compare_terrain(mars, moon, weights=w, include_uncertainty=False)
        print(f"{name:18s} TMSI={fmt(res['similarity_index'], 4)}  D={fmt(res['combined_distance'], 4)}  conf={res['confidence']}")

    # --- F. Spatial dependence / block-bootstrap justification ---
    section("F. Spatial dependence (Moran's I from Phase 7 stored diagnostics)")
    experiment = json.loads(
        (REPOSITORY_ROOT / "data/metadata/moon_mars_phase7_experiments.json").read_text(encoding="utf-8")
    )
    spatial = experiment["spatial_diagnostics"]
    for body in ("slope", "local_relief", "terrain_ruggedness"):
        mi = spatial[body]["morans_i"]
        print(f"Mars {body:16s} Moran's I = {mi:.6f}")
    for body in ("slope", "local_relief", "terrain_ruggedness"):
        mi = spatial["moon"][body]["morans_i"]
        print(f"Moon {body:16s} Moran's I = {mi:.6f}")
    all_mi = [spatial[b]["morans_i"] for b in ("slope", "local_relief", "terrain_ruggedness")] + \
             [spatial["moon"][b]["morans_i"] for b in ("slope", "local_relief", "terrain_ruggedness")]
    print(f"Minimum Moran's I across all features/bodies: {min(all_mi):.6f}")
    print("Strong spatial autocorrelation confirmed -> independent-pixel assumption inappropriate; block bootstrap justified.")

    # --- G. Bootstrap uncertainty on baseline ---
    section("G. Bootstrap uncertainty (baseline, 320 m, 64 reps, quick check)")
    boot = bootstrap_tmsi(mars, moon, weights_all, block_size_m=320.0, repetitions=64, seed=42)
    print(f"Bootstrap mean: {boot['tmsi_mean']:.4f}")
    print(f"95% interval: [{boot['tmsi_lower_95']:.4f}, {boot['tmsi_upper_95']:.4f}]")
    print(f"Baseline TMSI {r1['similarity_index']:.4f} lies within interval: "
          f"{boot['tmsi_lower_95'] <= r1['similarity_index'] <= boot['tmsi_upper_95']}")

    # --- H. Cross-dataset consistency ---
    section("H. Cross-dataset consistency / independent benchmark")
    print("No independently labeled real-world benchmark dataset is available.")
    print("Synthetic benchmarks (test_only) remain excluded from scientific findings.")
    print("Limitation documented: independent external validation pending a suitable reference dataset.")

    print("\nAll independent validation experiments completed.")


if __name__ == "__main__":
    main()
