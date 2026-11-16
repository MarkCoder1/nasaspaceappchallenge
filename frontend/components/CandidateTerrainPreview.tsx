"use client";

import { useEffect, useMemo, useState } from "react";
import { apiUrl } from "@/lib/api";

interface CandidateTerrainPreviewProps {
  candidateId: string;
  layer?: "elevation" | "hillshade" | "slope";
  skipFetch?: boolean;
}

interface TerrainGridResponse {
  dataset_id: string;
  layer: string;
  clip_low: number;
  clip_high: number;
  elevation_stats: { min: number | null; max: number | null; mean: number | null };
  sample_grid: (number | null)[][];
  grid_shape: [number, number];
  native_resolution_m?: number;
  processed_resolution_m?: number;
  native_resolution_note?: string;
  provider?: string;
  credit?: string;
}

const RAMPS: Record<string, (t: number) => [number, number, number]> = {
  terrain: (t) => {
    const a = Math.max(0, Math.min(1, t));
    if (a < 0.33) {
      const u = a / 0.33;
      return [Math.round(15 + 176 * u), Math.round(24 + 116 * u), Math.round(18 + 83 * u)];
    }
    if (a < 0.66) {
      const u = (a - 0.33) / 0.33;
      return [Math.round(191 - 96 * u), Math.round(140 - 100 * u), Math.round(101 - 40 * u)];
    }
    const u = (a - 0.66) / 0.34;
    return [Math.round(95 + 130 * u), Math.round(40 + 145 * u), Math.round(61 + 120 * u)];
  },
};

export default function CandidateTerrainPreview({ candidateId, layer = "elevation", skipFetch = false }: CandidateTerrainPreviewProps) {
  const [grid, setGrid] = useState<TerrainGridResponse | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "unavailable">(() => (skipFetch ? "unavailable" : "loading"));
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (skipFetch) {
      // No verified raster for this candidate — skip fetch entirely
      return undefined;
    }
    let cancelled = false;
    fetch(`${apiUrl}/api/candidates/terrain-grid/${encodeURIComponent(candidateId)}?layer=${encodeURIComponent(layer)}&max_dim=144`, { cache: "no-store" })
      .then(async (res) => {
        if (!res.ok) {
          if (!cancelled) setState("unavailable");
          return;
        }
        const payload = (await res.json()) as TerrainGridResponse;
        if (!cancelled) {
          setGrid(payload);
          setState("ready");
        }
      })
      .catch(() => {
        if (!cancelled) {
          setErrorMessage("Terrain service unreachable. The backend may be offline.");
          setState("unavailable");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [candidateId, layer, skipFetch]);

  const cells = useMemo(() => {
    if (!grid) return [] as string[];
    const [rows, cols] = grid.grid_shape;
    const span = Math.max(grid.clip_high - grid.clip_low, 1e-9);
    const out: string[] = new Array(rows * cols);
    for (let r = 0; r < rows; r += 1) {
      for (let c = 0; c < cols; c += 1) {
        const v = grid.sample_grid[r]?.[c];
        if (v === null || v === undefined || !Number.isFinite(v)) {
          out[r * cols + c] = "#161a17";
        } else {
          const t = Math.max(0, Math.min(1, (v - grid.clip_low) / span));
          const [R, G, B] = RAMPS.terrain(t);
          out[r * cols + c] = `rgb(${R},${G},${B})`;
        }
      }
    }
    return out;
  }, [grid]);

  if (state === "loading") {
    return (
      <div className="candidate-terrain candidate-terrain--loading" aria-live="polite">
        <span className="method-tag">VERIFIED TERRAIN — LOADING</span>
      </div>
    );
  }

  if (state === "unavailable") {
    return (
      <div className="candidate-terrain candidate-terrain--unavailable" role="status">
        <span className="method-tag">TERRAIN UNAVAILABLE</span>
        <p className="chart-note">
          No verified terrain raster is available for this candidate in the local data store. Candidate
          imagery and elevation previews are intentionally not fabricated. Current support is limited to
          candidates with open-access local rasters (e.g., USGS 3DEP for Death Valley).
          {errorMessage ? <><br />{errorMessage}</> : null}
        </p>
      </div>
    );
  }

  const [rows, cols] = grid!.grid_shape;
  const width = 280;
  const height = Math.round((rows / cols) * width);
  return (
    <div className="candidate-terrain candidate-terrain--ready">
      <div className="candidate-terrain-meta">
        <span className="method-tag">VERIFIED TERRAIN — {grid!.layer.toUpperCase()}</span>
        <span className="candidate-terrain-stats">{grid!.elevation_stats.min?.toFixed(0)}–{grid!.elevation_stats.max?.toFixed(0)} m</span>
      </div>
      <canvas
        width={width}
        height={height}
        className="candidate-terrain-canvas"
        role="img"
        aria-label={`Terrain preview for ${grid!.dataset_id}`}
        ref={(canvas) => {
          if (canvas) {
            const ctx = canvas.getContext("2d");
            if (ctx) {
              // Paint the grid cell-by-cell
              for (let r = 0; r < rows; r += 1) {
                for (let c = 0; c < cols; c += 1) {
                  ctx.fillStyle = cells[r * cols + c] ?? "#161a17";
                  ctx.fillRect(Math.floor((c / cols) * width), Math.floor((r / rows) * height), Math.ceil(width / cols) + 1, Math.ceil(height / rows) + 1);
                }
              }
            }
          }
        }}
      />
      <p className="candidate-terrain-credit">{grid!.provider ?? ""}{grid!.native_resolution_note ? ` — ${grid!.native_resolution_note}` : ""}</p>
    </div>
  );
}
