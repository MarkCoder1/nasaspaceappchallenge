"""Phase 11 experiment infrastructure: window extraction, overlap detection, comparison runner.

All experiments use only the validated Moon and Mars rasters. No Earth data.
Experimental results are written to data/metadata/ and kept separate from the
official Phase 7 Moon–Mars baseline.
"""

import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.windows import Window

from science.similarity.features.feature_extraction import extract_terrain_features
from science.similarity.scoring.similarity import compare_terrain

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MARS_PATH = REPOSITORY_ROOT / "data/processed/mars_jezero_ctx_elevation_m.tif"
MOON_PATH = REPOSITORY_ROOT / "data/processed/moon_lola_80s_20m_elevation_m.tif"
OUTPUT_DIR = REPOSITORY_ROOT / "data/metadata"
CELL_M = 20.0
WEIGHTS = {"slope": 1.0, "local_relief": 1.0, "terrain_ruggedness": 1.0}


@dataclass(frozen=True)
class WindowSpec:
    label: str
    body: str
    source_id: str
    col_off: int
    row_off: int
    n_cells: int
    width_cells: int
    height_cells: int
    extent_km: float


def window_overlap_fraction(a: WindowSpec, b: WindowSpec) -> float:
    """Fraction of the smaller window overlapped by the larger (0.0 to 1.0)."""
    a_col_start, a_col_end = a.col_off, a.col_off + a.width_cells
    a_row_start, a_row_end = a.row_off, a.row_off + a.height_cells
    b_col_start, b_col_end = b.col_off, b.col_off + b.width_cells
    b_row_start, b_row_end = b.row_off, b.row_off + b.height_cells

    col_overlap = max(0, min(a_col_end, b_col_end) - max(a_col_start, b_col_start))
    row_overlap = max(0, min(a_row_end, b_row_end) - max(a_row_start, b_row_start))
    overlap_area = col_overlap * row_overlap
    if overlap_area == 0:
        return 0.0
    area_a = a.width_cells * a.height_cells
    area_b = b.width_cells * b.height_cells
    return overlap_area / min(area_a, area_b)


def overlap_status(fraction: float) -> str:
    if fraction >= 0.99:
        return "identical"
    if fraction >= 0.5:
        return "high"
    if fraction > 0.0:
        return "partial"
    return "none"


def non_overlapping_grid(width_cells: int, height_cells: int, n_cells: int) -> list[tuple[int, int]]:
    """Return top-left (col_off, row_off) for a non-overlapping n_cells grid."""
    offsets: list[tuple[int, int]] = []
    col = 0
    while col + n_cells <= width_cells:
        row = 0
        while row + n_cells <= height_cells:
            offsets.append((col, row))
            row += n_cells
        col += n_cells
    return offsets


def extract_window(src_path: Path, spec: WindowSpec, out_path: Path) -> Path:
    """Write a windowed subset to a new GeoTIFF preserving CRS/transform."""
    with rasterio.open(src_path) as src:
        window = Window(spec.col_off, spec.row_off, spec.width_cells, spec.height_cells)
        data = src.read(1, window=window, masked=True)
        transform = src.window_transform(window)
        profile = src.profile.copy()
        profile.pop("blockxsize", None)
        profile.pop("blockysize", None)
        profile.pop("tiled", None)
        profile.update(
            width=spec.width_cells,
            height=spec.height_cells,
            transform=transform,
            count=1,
            driver="GTiff",
            dtype="float32",
        )
        with rasterio.open(out_path, "w", **profile) as dst:
            dst.write(data.astype(np.float32), 1)
    return out_path


def compare_windows(
    path_a: Path, spec_a: WindowSpec,
    path_b: Path, spec_b: WindowSpec,
    tmp_dir: Path,
) -> dict[str, Any]:
    """Compare two window rasters and return a structured result."""
    feat_a = extract_terrain_features(
        path_a, body=spec_a.body, source_id=spec_a.source_id,
        effective_resolution_m=16.055973052978516 if spec_a.body == "Moon" else 20.0,
    )
    feat_b = extract_terrain_features(
        path_b, body=spec_b.body, source_id=spec_b.source_id,
        effective_resolution_m=16.055973052978516 if spec_b.body == "Moon" else 20.0,
    )
    result = compare_terrain(feat_a, feat_b, weights=WEIGHTS, include_uncertainty=True)
    ov_frac = window_overlap_fraction(spec_a, spec_b)
    return {
        "label": f"{spec_a.label} vs {spec_b.label}",
        "body_a": spec_a.body,
        "body_b": spec_b.body,
        "source_id_a": spec_a.source_id,
        "source_id_b": spec_b.source_id,
        "extent_km": spec_a.extent_km,
        "n_cells": spec_a.n_cells,
        "window_a_offset": [spec_a.col_off, spec_a.row_off],
        "window_b_offset": [spec_b.col_off, spec_b.row_off],
        "overlap_fraction": round(ov_frac, 4),
        "overlap_status": overlap_status(ov_frac),
        "similarity_index": result.get("similarity_index"),
        "confidence": result.get("confidence"),
        "combined_distance": result.get("combined_distance"),
        "feature_distances": {
            name: c["distance"]["normalized_distance"]
            for name, c in result.get("features", {}).items()
        },
        "statistical_uncertainty": result.get("statistical_uncertainty"),
        "mars_valid_percent": feat_a.valid_percent,
        "moon_valid_percent": feat_b.valid_percent,
    }


def write_json(name: str, payload: dict[str, Any]) -> Path:
    out_path = OUTPUT_DIR / name
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out_path


def build_window_specs(n_cells: int) -> dict[str, list[WindowSpec]]:
    """Build non-overlapping window grids for Mars and Moon at n_cells cells."""
    with rasterio.open(MARS_PATH) as ms, rasterio.open(MOON_PATH) as mo:
        mars_w, mars_h = ms.width, ms.height
        moon_w, moon_h = mo.width, mo.height

    mars_offsets = non_overlapping_grid(mars_w, mars_h, n_cells)
    moon_offsets = non_overlapping_grid(moon_w, moon_h, n_cells)

    mars_specs = [
        WindowSpec(
            label=f"Mars w{i}",
            body="Mars",
            source_id=f"mars_w{i}_{n_cells}",
            col_off=co, row_off=ro,
            n_cells=n_cells, width_cells=n_cells, height_cells=n_cells,
            extent_km=round(n_cells * CELL_M / 1000, 2),
        )
        for i, (co, ro) in enumerate(mars_offsets)
    ]
    moon_specs = [
        WindowSpec(
            label=f"Moon w{i}",
            body="Moon",
            source_id=f"moon_w{i}_{n_cells}",
            col_off=co, row_off=ro,
            n_cells=n_cells, width_cells=n_cells, height_cells=n_cells,
            extent_km=round(n_cells * CELL_M / 1000, 2),
        )
        for i, (co, ro) in enumerate(moon_offsets)
    ]
    return {"mars": mars_specs, "moon": moon_specs}


def run_experiments(n_cells: int = 512) -> dict[str, Any]:
    """Run Experiments A (within-body), B (between-body), C (overlap bias)."""
    specs = build_window_specs(n_cells)
    mars_specs = specs["mars"]
    moon_specs = specs["moon"]
    extent_km = round(n_cells * CELL_M / 1000, 2)

    results: dict[str, Any] = {
        "experiment": "phase11_sampling_framework",
        "cell_m": CELL_M,
        "n_cells": n_cells,
        "extent_km": extent_km,
        "weights": WEIGHTS,
        "mars_window_count": len(mars_specs),
        "moon_window_count": len(moon_specs),
        "mars_windows": [
            {"label": s.label, "offset": [s.col_off, s.row_off]} for s in mars_specs
        ],
        "moon_windows": [
            {"label": s.label, "offset": [s.col_off, s.row_off]} for s in moon_specs
        ],
        "within_body": {"mars": [], "moon": []},
        "between_body": [],
        "overlap_bias": [],
    }

    tmp_dir = REPOSITORY_ROOT / "data/processed" / "phase11_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Extract all windows once.
    window_paths: dict[str, Path] = {}
    for s in mars_specs + moon_specs:
        p = tmp_dir / f"{s.source_id}.tif"
        extract_window(
            MARS_PATH if s.body == "Mars" else MOON_PATH,
            s, p,
        )
        window_paths[s.source_id] = p

    try:
        # Experiment A: within-body pairwise (non-overlapping windows only).
        for body_key, body_specs in (("mars", mars_specs), ("moon", moon_specs)):
            for i in range(len(body_specs)):
                for j in range(i + 1, len(body_specs)):
                    sa, sb = body_specs[i], body_specs[j]
                    res = compare_windows(
                        window_paths[sa.source_id], sa,
                        window_paths[sb.source_id], sb,
                        tmp_dir,
                    )
                    results["within_body"][body_key].append(res)
                    print(
                        f"  within {sa.body}: {sa.label} vs {sb.label} "
                        f"TMSI={res['similarity_index']:.4f} overlap={res['overlap_status']}"
                    )

        # Experiment B: between-body (Mars windows x Moon windows).
        for sa in mars_specs:
            for sb in moon_specs:
                res = compare_windows(
                    window_paths[sa.source_id], sa,
                    window_paths[sb.source_id], sb,
                    tmp_dir,
                )
                results["between_body"].append(res)
        print(f"  between_body: {len(results['between_body'])} comparisons")

        # Experiment C: overlap bias using specific offset pairs.
        # Build candidate windows on Moon at this extent for controlled overlap tests.
        overlap_specs: list[WindowSpec] = []
        with rasterio.open(MOON_PATH) as mo:
            moon_w, moon_h = mo.width, mo.height
        # center, northwest, southeast, plus shifted variants for overlap
        half = n_cells // 2
        candidates = [
            ("center", moon_w // 2 - n_cells // 2, moon_h // 2 - n_cells // 2),
            ("northwest", 0, 0),
            ("southeast", moon_w - n_cells, moon_h - n_cells),
            ("shift_half", moon_w // 2 - n_cells // 2 + half, moon_h // 2 - n_cells // 2 + half),
            ("shift_quarter", moon_w // 2 - n_cells // 2 + n_cells // 4, moon_h // 2 - n_cells // 4),
        ]
        for tag, co, ro in candidates:
            if co + n_cells <= moon_w and ro + n_cells <= moon_h:
                s = WindowSpec(
                    label=f"Moon {tag}",
                    body="Moon",
                    source_id=f"moon_overlap_{tag}_{n_cells}",
                    col_off=co, row_off=ro,
                    n_cells=n_cells, width_cells=n_cells, height_cells=n_cells,
                    extent_km=extent_km,
                )
                overlap_specs.append(s)
                p = tmp_dir / f"{s.source_id}.tif"
                extract_window(MOON_PATH, s, p)
                window_paths[s.source_id] = p

        # Identical (self) control: same window compared to itself via two specs.
        # Pairwise among overlap_specs with overlap status recorded.
        for i in range(len(overlap_specs)):
            for j in range(i + 1, len(overlap_specs)):
                sa, sb = overlap_specs[i], overlap_specs[j]
                res = compare_windows(
                    window_paths[sa.source_id], sa,
                    window_paths[sb.source_id], sb,
                    tmp_dir,
                )
                results["overlap_bias"].append(res)
                print(
                    f"  overlap: {sa.label} vs {sb.label} "
                    f"TMSI={res['similarity_index']:.4f} frac={res['overlap_fraction']} "
                    f"status={res['overlap_status']}"
                )

        # Identical-window self-comparison control (two specs, same location).
        for s in overlap_specs:
            s2 = WindowSpec(
                label=f"{s.label} (self-control)",
                body=s.body,
                source_id=f"{s.source_id}_self",
                col_off=s.col_off, row_off=s.row_off,
                n_cells=s.n_cells, width_cells=s.width_cells, height_cells=s.height_cells,
                extent_km=s.extent_km,
            )
            p2 = tmp_dir / f"{s2.source_id}.tif"
            extract_window(MOON_PATH, s2, p2)
            window_paths[s2.source_id] = p2
            res = compare_windows(
                window_paths[s.source_id], s,
                window_paths[s2.source_id], s2,
                tmp_dir,
            )
            results["overlap_bias"].append(res)
            print(
                f"  overlap self-control: {s.label} vs itself "
                f"TMSI={res['similarity_index']:.4f} frac={res['overlap_fraction']} "
                f"status={res['overlap_status']}"
            )

    finally:
        # Cleanup temp rasters (experiment artifacts, not validated products).
        shutil.rmtree(tmp_dir, ignore_errors=True)

    # Summary statistics.
    def tmsi_values(block):
        return [r["similarity_index"] for r in block if r.get("similarity_index") is not None]

    results["summary"] = {
        "within_body_mars": {
            "count": len(results["within_body"]["mars"]),
            "tmsi_min": min(tmsi_values(results["within_body"]["mars"])) if tmsi_values(results["within_body"]["mars"]) else None,
            "tmsi_max": max(tmsi_values(results["within_body"]["mars"])) if tmsi_values(results["within_body"]["mars"]) else None,
            "tmsi_mean": float(np.mean(tmsi_values(results["within_body"]["mars"]))) if tmsi_values(results["within_body"]["mars"]) else None,
        },
        "within_body_moon": {
            "count": len(results["within_body"]["moon"]),
            "tmsi_min": min(tmsi_values(results["within_body"]["moon"])) if tmsi_values(results["within_body"]["moon"]) else None,
            "tmsi_max": max(tmsi_values(results["within_body"]["moon"])) if tmsi_values(results["within_body"]["moon"]) else None,
            "tmsi_mean": float(np.mean(tmsi_values(results["within_body"]["moon"]))) if tmsi_values(results["within_body"]["moon"]) else None,
        },
        "between_body": {
            "count": len(results["between_body"]),
            "tmsi_min": min(tmsi_values(results["between_body"])) if tmsi_values(results["between_body"]) else None,
            "tmsi_max": max(tmsi_values(results["between_body"])) if tmsi_values(results["between_body"]) else None,
            "tmsi_mean": float(np.mean(tmsi_values(results["between_body"]))) if tmsi_values(results["between_body"]) else None,
        },
    }
    return results


if __name__ == "__main__":
    results = run_experiments(n_cells=512)
    out_path = write_json("phase11_sampling_framework.json", results)
    print(f"\nResults written to {out_path}")
    print(json.dumps(results["summary"], indent=2))
