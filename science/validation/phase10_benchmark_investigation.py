"""Phase 10 Workstream E: independent benchmark / methodological self-consistency investigation.

Tests whether the TMSI engine recognizes same-body terrain as more similar than
cross-body terrain, using different spatial windows of the validated Moon and Mars
rasters. No Earth data and no external downloaded benchmark are used (Earth blocked
by Earthdata auth; alternatives too large or same-source).

Documents whether a fully independent external benchmark was obtainable.
"""

import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window

from science.similarity.features.feature_extraction import extract_terrain_features
from science.similarity.scoring.similarity import compare_terrain

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MARS_PATH = REPOSITORY_ROOT / "data/processed/mars_jezero_ctx_elevation_m.tif"
MOON_PATH = REPOSITORY_ROOT / "data/processed/moon_lola_80s_20m_elevation_m.tif"
OUTPUT_PATH = REPOSITORY_ROOT / "data/metadata/phase10_benchmark_investigation.json"

CELL_M = 20.0
WEIGHTS = {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0}


def _window_at(col_off, row_off, n_cells):
    return Window(col_off, row_off, n_cells, n_cells)


def _write_window(src_path, window, out_path):
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


def _extract(src_path, col_off, row_off, n_cells, tmp_path):
    with rasterio.open(src_path) as src:
        if not (col_off + n_cells <= src.width and row_off + n_cells <= src.height):
            return None
    _write_window(src_path, _window_at(col_off, row_off, n_cells), tmp_path)
    return tmp_path


def _compare_windows(path_a, body_a, id_a, eff_a, path_b, body_b, id_b, eff_b, n_cells, label,
                     offset_a, offset_b):
    feat_a = extract_terrain_features(path_a, body=body_a, source_id=id_a, effective_resolution_m=eff_a)
    feat_b = extract_terrain_features(path_b, body=body_b, source_id=id_b, effective_resolution_m=eff_b)
    result = compare_terrain(feat_a, feat_b, weights=WEIGHTS, include_uncertainty=False)
    return {
        "label": label,
        "n_cells": n_cells,
        "extent_km": round(n_cells * CELL_M / 1000, 2),
        "similarity_index": result["similarity_index"],
        "confidence": result["confidence"],
        "combined_distance": result["combined_distance"],
        "feature_distances": {name: c["distance"]["normalized_distance"] for name, c in result["features"].items()},
        "window_a_offset": offset_a,
        "window_b_offset": offset_b,
    }


def main():
    results = {
        "experiment": "phase10_benchmark_investigation",
        "weights": WEIGHTS,
        "cell_m": CELL_M,
        "finding": "No fully independent external benchmark was obtainable within constraints "
                   "(Earth NASADEM blocked by Earthdata authentication; alternative planetary DEMs "
                   "either require auth or exceed bounded-download limits). Same-body window-vs-window "
                   "methodological self-consistency tests are reported instead, with clear caveats.",
        "benchmark_available": False,
        "same_body_tests": [],
        "cross_body_reference": None,
    }

    MOON_EFF_RES = 16.055973052978516
    MARS_EFF_RES = 20.0

    with rasterio.open(MARS_PATH) as ms, rasterio.open(MOON_PATH) as mo:
        mars_w, mars_h = ms.width, ms.height
        moon_w, moon_h = mo.width, mo.height

    # --- Same-body Moon: three different 20.48 km windows within the 40.96 km raster ---
    n = 1024
    moon_candidates = [
        ("center", moon_w // 2 - n // 2, moon_h // 2 - n // 2),
        ("northwest", 0, 0),
        ("southeast", moon_w - n, moon_h - n),
    ]
    moon_windows = {}
    for tag, co, ro in moon_candidates:
        tmp = REPOSITORY_ROOT / f"data/processed/phase10_moon_{tag}_{n}.tif"
        p = _extract(MOON_PATH, co, ro, n, tmp)
        if p:
            moon_windows[tag] = (tmp, co, ro)

    moon_pairs = [("center", "northwest"), ("center", "southeast"), ("northwest", "southeast")]
    for a_tag, b_tag in moon_pairs:
        pa, aco, aro = moon_windows[a_tag]
        pb, bco, bro = moon_windows[b_tag]
        res = _compare_windows(pa, "Moon", f"moon_{a_tag}", MOON_EFF_RES,
                               pb, "Moon", f"moon_{b_tag}", MOON_EFF_RES,
                               n, f"Moon {a_tag} vs Moon {b_tag} (20.48 km)", [aco, aro], [bco, bro])
        results["same_body_tests"].append(res)
        print(f"Moon {a_tag} vs {b_tag}: TMSI={res['similarity_index']:.4f} conf={res['confidence']} D={res['combined_distance']:.4f}")

    for tmp, _, _ in moon_windows.values():
        tmp.unlink(missing_ok=True)

    # --- Same-body Mars: three different 10.24 km windows (Mars is smaller) ---
    n_mars = 512
    mars_candidates = [
        ("center", mars_w // 2 - n_mars // 2, mars_h // 2 - n_mars // 2),
        ("northwest", 0, 0),
        ("southeast", mars_w - n_mars, mars_h - n_mars),
    ]
    mars_windows = {}
    for tag, co, ro in mars_candidates:
        tmp = REPOSITORY_ROOT / f"data/processed/phase10_mars_{tag}_{n_mars}.tif"
        p = _extract(MARS_PATH, co, ro, n_mars, tmp)
        if p:
            mars_windows[tag] = (tmp, co, ro)

    mars_pairs = [("center", "northwest"), ("center", "southeast"), ("northwest", "southeast")]
    for a_tag, b_tag in mars_pairs:
        pa, aco, aro = mars_windows[a_tag]
        pb, bco, bro = mars_windows[b_tag]
        res = _compare_windows(pa, "Mars", f"mars_{a_tag}", MARS_EFF_RES,
                               pb, "Mars", f"mars_{b_tag}", MARS_EFF_RES,
                               n_mars, f"Mars {a_tag} vs Mars {b_tag} (10.24 km)", [aco, aro], [bco, bro])
        results["same_body_tests"].append(res)
        print(f"Mars {a_tag} vs {b_tag}: TMSI={res['similarity_index']:.4f} conf={res['confidence']} D={res['combined_distance']:.4f}")

    for tmp, _, _ in mars_windows.values():
        tmp.unlink(missing_ok=True)

    # --- Cross-body reference (Moon vs Mars full, historical baseline) ---
    results["cross_body_reference"] = {
        "label": "Moon vs Mars (full validated extents, historical baseline)",
        "similarity_index": 49.92285382858792,
        "confidence": "HIGH",
        "note": "Cross-body TMSI from Phase 7 baseline; a reference point, not a benchmark.",
    }

    OUTPUT_PATH.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nResults written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
