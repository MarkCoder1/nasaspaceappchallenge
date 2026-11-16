"""Phase 10 Workstream C: systematic spatial-extent sensitivity experiments.

Extracts centered square windows of multiple physical extents from the validated
Mars and Moon rasters, computes terrain features, TMSI, and bootstrap uncertainty
for each extent. No Earth data is used.

Outputs are written to data/metadata/phase10_extent_sensitivity.json for the report.
"""

import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window

from science.similarity.features.feature_extraction import extract_terrain_features
from science.similarity.scoring.similarity import compare_terrain
from science.similarity.comparison.bootstrap import bootstrap_tmsi

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MARS_PATH = REPOSITORY_ROOT / "data/processed/mars_jezero_ctx_elevation_m.tif"
MOON_PATH = REPOSITORY_ROOT / "data/processed/moon_lola_80s_20m_elevation_m.tif"
OUTPUT_PATH = REPOSITORY_ROOT / "data/metadata/phase10_extent_sensitivity.json"

CELL_M = 20.0
MARS_EFF_RES = 20.0
MOON_EFF_RES = 16.055973052978516
WEIGHTS = {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0}

# Proposed extents (km). Adapted to valid coverage below.
PROPOSED_EXTENTS_KM = [5.12, 10.24, 20.48, 30.72, 40.96]


def _center_window(dataset, n_cells):
    """Return a centered square Window of n_cells x n_cells, clipped to dataset bounds."""
    width, height = dataset.width, dataset.height
    half = n_cells // 2
    col_off = max(0, min(width - n_cells, width // 2 - half))
    row_off = max(0, min(height - n_cells, height // 2 - half))
    actual_n = min(n_cells, width - col_off, height - row_off)
    return Window(col_off, row_off, actual_n, actual_n), (col_off, row_off, actual_n)


def _write_window(src_path, window, out_path, label):
    """Write a windowed subset to a new GeoTIFF, preserving CRS and transform."""
    with rasterio.open(src_path) as src:
        profile = src.profile.copy()
        data = src.read(1, window=window, masked=True)
        transform = src.window_transform(window)
        profile.update(
            width=window.width,
            height=window.height,
            transform=transform,
            count=1,
            driver="GTiff",
            dtype="float32",
        )
        with rasterio.open(out_path, "w", **profile) as dst:
            dst.write(data.astype(np.float32), 1)
    return out_path


def _extent_fits(dataset, n_cells):
    return n_cells <= dataset.width and n_cells <= dataset.height


def main():
    results = {
        "experiment": "phase10_spatial_extent_sensitivity",
        "cell_m": CELL_M,
        "weights": WEIGHTS,
        "note": "Centered square windows extracted from both Mars and Moon at equal physical extent. "
                "Extents exceeding a dataset's coverage are skipped for that dataset; the largest "
                "common square extent is used where proposed extents do not fit.",
        "extents": [],
    }

    with rasterio.open(MARS_PATH) as mars_src, rasterio.open(MOON_PATH) as moon_src:
        mars_w, mars_h = mars_src.width, mars_src.height
        moon_w, moon_h = moon_src.width, moon_src.height
        print(f"Mars: {mars_w}x{mars_h} cells ({mars_w*CELL_M/1000:.2f} km x {mars_h*CELL_M/1000:.2f} km)")
        print(f"Moon: {moon_w}x{moon_h} cells ({moon_w*CELL_M/1000:.2f} km x {moon_h*CELL_M/1000:.2f} km)")

        for extent_km in PROPOSED_EXTENTS_KM:
            n_cells = int(round(extent_km * 1000 / CELL_M))
            entry = {
                "extent_km": extent_km,
                "n_cells": n_cells,
                "mars_available": _extent_fits(mars_src, n_cells),
                "moon_available": _extent_fits(moon_src, n_cells),
            }

            can_compare = _extent_fits(mars_src, n_cells) and _extent_fits(moon_src, n_cells)
            entry["comparable"] = can_compare

            if not can_compare:
                entry["skip_reason"] = (
                    f"Extent {extent_km} km ({n_cells} cells) exceeds one or both dataset coverages "
                    f"(Mars {mars_w}x{mars_h}, Moon {moon_w}x{moon_h})."
                )
                print(f"\n{extent_km} km ({n_cells} cells): {entry['skip_reason']}")
                results["extents"].append(entry)
                continue

            # Extract centered windows.
            mars_win, mars_offset = _center_window(mars_src, n_cells)
            moon_win, moon_offset = _center_window(moon_src, n_cells)

            mars_tmp = REPOSITORY_ROOT / f"data/processed/phase10_mars_{extent_km}km_window.tif"
            moon_tmp = REPOSITORY_ROOT / f"data/processed/phase10_moon_{extent_km}km_window.tif"
            _write_window(MARS_PATH, mars_win, mars_tmp, "mars")
            _write_window(MOON_PATH, moon_win, moon_tmp, "moon")

            entry["mars_window_cells"] = [mars_win.col_off, mars_win.row_off, mars_win.width, mars_win.height]
            entry["moon_window_cells"] = [moon_win.col_off, moon_win.row_off, moon_win.width, moon_win.height]

            # Features.
            mars_feat = extract_terrain_features(
                mars_tmp, body="Mars", source_id=f"mars_{extent_km}km",
                effective_resolution_m=MARS_EFF_RES,
            )
            moon_feat = extract_terrain_features(
                moon_tmp, body="Moon", source_id=f"moon_{extent_km}km",
                effective_resolution_m=MOON_EFF_RES,
            )

            # TMSI + bootstrap.
            comp = compare_terrain(mars_feat, moon_feat, weights=WEIGHTS, include_uncertainty=True)
            boot = bootstrap_tmsi(mars_feat, moon_feat, weights=WEIGHTS, block_size_m=320.0, repetitions=64, seed=42)

            entry["tmsi"] = comp["similarity_index"]
            entry["confidence"] = comp["confidence"]
            entry["combined_distance"] = comp["combined_distance"]
            entry["feature_distances"] = {
                name: c["distance"]["normalized_distance"] for name, c in comp["features"].items()
            }
            entry["bootstrap_mean"] = boot["tmsi_mean"]
            entry["bootstrap_lower_95"] = boot["tmsi_lower_95"]
            entry["bootstrap_upper_95"] = boot["tmsi_upper_95"]
            entry["mars_valid_percent"] = mars_feat.valid_percent
            entry["moon_valid_percent"] = moon_feat.valid_percent

            print(
                f"{extent_km:6.2f} km ({n_cells:4d} cells): "
                f"TMSI={comp['similarity_index']:.4f} conf={comp['confidence']} "
                f"D={comp['combined_distance']:.4f} "
                f"boot_mean={boot['tmsi_mean']:.4f} 95%[{boot['tmsi_lower_95']:.4f},{boot['tmsi_upper_95']:.4f}]"
            )

            # Cleanup temp rasters (experiment artifacts, not validated products).
            for p in (mars_tmp, moon_tmp):
                p.unlink(missing_ok=True)

            results["extents"].append(entry)

    # Full-dataset reference (historical baseline).
    mars_full = extract_terrain_features(
        MARS_PATH, body="Mars", source_id="mars_jezero_ctx_dtm", effective_resolution_m=MARS_EFF_RES,
    )
    moon_full = extract_terrain_features(
        MOON_PATH, body="Moon", source_id="moon_lola", effective_resolution_m=MOON_EFF_RES,
    )
    ref = compare_terrain(mars_full, moon_full, weights=WEIGHTS, include_uncertainty=True)
    boot_ref = bootstrap_tmsi(mars_full, moon_full, weights=WEIGHTS, block_size_m=320.0, repetitions=64, seed=42)
    results["reference_full_datasets"] = {
        "mars_extent_km": round(mars_w * CELL_M / 1000, 2),
        "moon_extent_km": round(moon_w * CELL_M / 1000, 2),
        "tmsi": ref["similarity_index"],
        "confidence": ref["confidence"],
        "combined_distance": ref["combined_distance"],
        "bootstrap_mean": boot_ref["tmsi_mean"],
        "bootstrap_lower_95": boot_ref["tmsi_lower_95"],
        "bootstrap_upper_95": boot_ref["tmsi_upper_95"],
    }

    OUTPUT_PATH.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nResults written to {OUTPUT_PATH}")
    print(f"Reference full-dataset TMSI: {ref['similarity_index']:.4f} (historical baseline 49.92285382858792)")


if __name__ == "__main__":
    main()
