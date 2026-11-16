import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/candidates", tags=["candidates"])

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "science" / "datasets" / "registry.json"


def _load_registry() -> dict:
    if not REGISTRY_PATH.is_file():
        raise HTTPException(status_code=404, detail="Candidate registry file not found")
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise HTTPException(status_code=500, detail=f"Invalid candidate registry JSON: {error}") from error


@router.get("")
def list_candidates() -> dict:
    registry = _load_registry()
    candidates = registry.get("candidates", {}).get("list", [])
    return {
        "candidates": candidates,
        "count": len(candidates),
        "by_status": registry.get("candidates", {}).get("by_status", {}),
    }


@router.get("/{candidate_id}")
def get_candidate(candidate_id: str) -> dict:
    registry = _load_registry()
    for candidate in registry.get("candidates", {}).get("list", []):
        if candidate.get("id") == candidate_id:
            return candidate
    raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")


import rasterio
import numpy as np

# Verified Earth candidate terrain previews.
# Only candidates with authentic, locally processed, open-access terrain data are listed.
# death_valley: USGS 3DEP 1-arc-second DEM tile n37w117,
# Source: https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/n37w117/USGS_1_n37w117.tif
# SHA-256 (raw): d6100180753d276b407ec585a872dc41d3515ea838c551ad22ec3aca4e6d8ad1
# Reprojected to EPSG:26911 (UTM Zone 11N) at 20.0 m post spacing.
candidate_terrain_sources = {
    "death_valley": {
        "path": Path(__file__).resolve().parents[2] / "data" / "processed" / "USGS_1_n37w117_20m_utm11n.tif",
        "label": "USGS 3DEP 1-arc-second (processed to 20 m)",
        "provider": "U.S. Geological Survey, 3D Elevation Program",
        "native_resolution_m": 29.3,
        "processed_resolution_m": 20.0,
        "native_resolution_note": "Source data is 1 arc-second (~29.3 m); resampled to 20 m processing grid. Effective measurement resolution remains ~29.3 m.",
        "crs": "EPSG:26911 (UTM Zone 11N)",
        "vertical_datum": "NAVD88",
        "source_url": "https://www.usgs.gov/3d-elevation-program",
        "credit": "U.S. Geological Survey — 3DEP (public domain, USGS Standard Disclaimer)",
        "candidate_id": "death_valley",
        "bounds_label": "Southern California / Death Valley, USA",
    },
}


def _compute_layer(elevation: np.ndarray, valid: np.ndarray, layer: str) -> np.ndarray:
    if layer == "elevation":
        return elevation
    if layer == "hillshade":
        gy, gx = np.gradient(np.where(valid, elevation, 0.0))
        shaded = 0.5 * (-gx) + 0.5 * (-gy)
        shaded = np.where(valid, shaded, np.nan)
        return shaded
    if layer == "slope":
        gy, gx = np.gradient(np.where(valid, elevation, 0.0))
        slope = np.degrees(np.arctan(np.sqrt(gx * gx + gy * gy)))
        return np.where(valid, slope, np.nan)
    if layer in {"local_relief", "terrain_ruggedness"}:
        from scipy import ndimage
        if layer == "local_relief":
            window = 3
            min_input = np.where(valid, elevation, np.inf)
            max_input = np.where(valid, elevation, -np.inf)
            local_min = ndimage.minimum_filter(min_input, size=window, mode="nearest")
            local_max = ndimage.maximum_filter(max_input, size=window, mode="nearest")
            out = local_max - local_min
            return np.where(valid, out, np.nan)
        # terrain_ruggedness — Riley TRI 3x3
        out = np.full(elevation.shape, np.nan, dtype=float)
        for row in range(elevation.shape[0]):
            for col in range(elevation.shape[1]):
                if not valid[row, col]:
                    continue
                center = elevation[row, col]
                r0, r1 = max(0, row - 1), min(elevation.shape[0], row + 2)
                c0, c1 = max(0, col - 1), min(elevation.shape[1], col + 2)
                block = elevation[r0:r1, c0:c1]
                vb = block[np.isfinite(block)]
                if vb.size < 2:
                    continue
                diffs = vb - center
                out[row, col] = float(np.sqrt(np.mean(diffs * diffs)))
        return out
    return elevation


@router.get("/terrain-grid/{candidate_id}")
def get_candidate_terrain_grid(
    candidate_id: str,
    layer: str = "elevation",
    max_dim: int = 128,
) -> dict:
    if candidate_id not in candidate_terrain_sources:
        raise HTTPException(
            status_code=404,
            detail=f"No verified terrain preview is available for candidate '{candidate_id}'. Only candidates with locally verified, open-access rasters are supported.",
        )
    allowed_layers = {"elevation", "hillshade", "slope", "local_relief", "terrain_ruggedness"}
    if layer not in allowed_layers:
        raise HTTPException(status_code=400, detail=f"Unknown layer: {layer}")
    source = candidate_terrain_sources[candidate_id]
    path = source["path"]
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Candidate raster file is missing on the server")
    with rasterio.open(path) as dataset:
        src_h = dataset.height
        src_w = dataset.width
        scale = max(src_h / max_dim, src_w / max_dim, 1)
        out_h = max(2, int(round(src_h / scale)))
        out_w = max(2, int(round(src_w / scale)))
        values = dataset.read(1, out_shape=(1, out_h, out_w), masked=True, resampling=rasterio.enums.Resampling.average)
        elevation = values.filled(np.nan).astype(float)
        valid = np.isfinite(elevation)
        layer_values = _compute_layer(elevation, valid, layer)
        finite = valid & np.isfinite(layer_values)
        lo = float(np.nanpercentile(layer_values, 2)) if finite.any() else 0.0
        hi = float(np.nanpercentile(layer_values, 98)) if finite.any() else 1.0
        return {
            "dataset_id": candidate_id,
            "body": "Earth",
            "layer": layer,
            "resampling": "average",
            "source_dimensions": [src_h, src_w],
            "downsampled_dimensions": [out_h, out_w],
            "resolution_m": source["processed_resolution_m"],
            "native_resolution_m": source["native_resolution_m"],
            "native_resolution_note": source["native_resolution_note"],
            "crs": source["crs"],
            "vertical_datum": source["vertical_datum"],
            "provider": source["provider"],
            "native_resolution_m_display": f"{source['native_resolution_m']} m (1 arc-second)",
            "bounds": [float(dataset.bounds.left), float(dataset.bounds.bottom), float(dataset.bounds.right), float(dataset.bounds.top)],
            "valid_percent": float(valid.mean() * 100),
            "clip_low": lo,
            "clip_high": hi,
            "elevation_stats": {
                "min": float(np.nanmin(elevation[np.isfinite(elevation)])) if np.isfinite(elevation).any() else None,
                "max": float(np.nanmax(elevation[np.isfinite(elevation)])) if np.isfinite(elevation).any() else None,
                "mean": float(np.nanmean(elevation[np.isfinite(elevation)])) if np.isfinite(elevation).any() else None,
            },
            "source_url": source["source_url"],
            "credit": source["credit"],
            "sample_grid": [[float(v) if np.isfinite(v) else None for v in row] for row in layer_values],
            "grid_shape": [out_h, out_w],
            "kind": "candidate_terrain_grid",
        }


@router.get("/terrain-meta/{candidate_id}")
def get_candidate_terrain_meta(candidate_id: str) -> dict:
    if candidate_id not in candidate_terrain_sources:
        raise HTTPException(status_code=404, detail="No verified terrain preview for this candidate")
    source = candidate_terrain_sources[candidate_id]
    return {
        "candidate_id": candidate_id,
        "available": True,
        "label": source["label"],
        "provider": source["provider"],
        "native_resolution_m": source["native_resolution_m"],
        "processed_resolution_m": source["processed_resolution_m"],
        "native_resolution_note": source["native_resolution_note"],
        "crs": source["crs"],
        "vertical_datum": source["vertical_datum"],
        "source_url": source["source_url"],
        "credit": source["credit"],
        "bounds_label": source["bounds_label"],
    }
