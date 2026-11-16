"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";

export type TerrainLayer = "elevation" | "hillshade" | "slope" | "local_relief" | "terrain_ruggedness";

export interface TerrainGridData {
  dataset_id: string;
  body: string;
  layer: TerrainLayer;
  resampling: string;
  source_dimensions: [number, number];
  downsampled_dimensions: [number, number];
  resolution_m: number;
  bounds: [number, number, number, number];
  crs: string | null;
  valid_percent: number;
  clip_low: number;
  clip_high: number;
  elevation_stats: { min: number | null; max: number | null; mean: number | null };
  sample_grid: (number | null)[][];
  grid_shape: [number, number];
}

type SupportedDatasetId = "moon_lola" | "mars_jezero_ctx_dtm" | "usgs_3dep_death_valley";

interface TerrainViewerProps {
  datasetId: SupportedDatasetId;
  layer: TerrainLayer;
  onLayerChange: (layer: TerrainLayer) => void;
  gridUrl?: (layer: TerrainLayer) => string;
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
  hot: (t) => {
    const a = Math.max(0, Math.min(1, t));
    return [
      Math.round(30 + 225 * a),
      Math.round(28 + 165 * Math.max(0, Math.min(1, (a - 0.2) * 1.6))),
      Math.round(24 * (1 - a) * 0.6),
    ];
  },
  gray: (t) => {
    const v = Math.round(10 + 215 * Math.max(0, Math.min(1, t)));
    return [v, v, v];
  },
  ocean: (t) => {
    const a = Math.max(0, Math.min(1, t));
    return [Math.round(8 + 18 * a), Math.round(12 + 62 * a), Math.round(24 + 100 * a)];
  },
  magma: (t) => {
    const a = Math.max(0, Math.min(1, t));
    const r = Math.round(20 + 235 * THREE.MathUtils.smoothstep(a, 0.0, 0.9));
    const g = Math.round(10 + 130 * THREE.MathUtils.smoothstep(a, 0.35, 1.0));
    const b = Math.round(34 + 90 * (1 - THREE.MathUtils.smoothstep(a, 0.55, 1.0)));
    return [r, g, b];
  },
  nocturne: (t) => {
    const a = Math.max(0, Math.min(1, t));
    return [Math.round(12 + 60 * a), Math.round(14 + 90 * a), Math.round(18 + 120 * a)];
  },
};

const RAMP_LABELS: Record<string, string> = {
  terrain: "TERRAIN",
  hot: "HOT",
  gray: "GRAYSCALE",
  ocean: "OCEAN",
  magma: "MAGMA",
  nocturne: "NOCTURNE",
};

export const TERRAIN_LAYERS: Array<{ id: TerrainLayer; label: string }> = [
  { id: "elevation", label: "Elevation" },
  { id: "hillshade", label: "Hillshade" },
  { id: "slope", label: "Slope" },
  { id: "local_relief", label: "Local relief" },
  { id: "terrain_ruggedness", label: "Terrain ruggedness" },
];

const layerUnits = (l: TerrainLayer): string => {
  switch (l) {
    case "slope":
      return "degrees";
    case "hillshade":
      return "illumination units";
    default:
      return "m";
  }
};

export default function TerrainViewer({ datasetId, layer, onLayerChange, gridUrl }: TerrainViewerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const threeContainerRef = useRef<HTMLDivElement>(null);

  const [grid, setGrid] = useState<TerrainGridData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"2d" | "3d">("2d");
  const [ramp, setRamp] = useState<string>("terrain");
  const [rangeMin, setRangeMin] = useState(0);
  const [rangeMax, setRangeMax] = useState(1);
  const [view, setView] = useState({ x: 0, y: 0, scale: 1 });
  const [exaggeration, setExaggeration] = useState(1.4);
  const [coords, setCoords] = useState<string>("—");
  const [valueUnderCursor, setValueUnderCursor] = useState<string>("—");
  const [fullscreen, setFullscreen] = useState(false);
  const [showLegend, setShowLegend] = useState(true);

  const dragRef = useRef({ dragging: false, startX: 0, startY: 0, originX: 0, originY: 0 });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      // All setState calls happen after an await boundary; no synchronous cascading render
      try {
        const url = gridUrl ? gridUrl(layer) : `http://localhost:8000/api/similarity/terrain-grid/${encodeURIComponent(datasetId)}?layer=${encodeURIComponent(layer)}&max_dim=192`;
        const res = await fetch(url, { cache: "no-store" });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const payload = (await res.json()) as TerrainGridData;
        if (!cancelled) {
          setGrid(payload);
          setRangeMin(payload.clip_low);
          setRangeMax(payload.clip_high);
          setLoading(false);
        }
        return;
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load terrain grid");
          setLoading(false);
        }
      } finally {
        // intentionally empty; setLoading is called from the resolved branches
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [datasetId, layer]);

  const colorLookup = useMemo(() => {
    if (!grid) return [] as string[];
    const [rows, cols] = grid.grid_shape;
    const span = Math.max(rangeMax - rangeMin, 1e-9);
    const lut: string[] = new Array(256);
    for (let i = 0; i < 256; i += 1) {
      const [r, g, b] = RAMPS[ramp](i / 255);
      lut[i] = `rgb(${r},${g},${b})`;
    }
    const cells: string[] = new Array(rows * cols);
    for (let row = 0; row < rows; row += 1) {
      for (let col = 0; col < cols; col += 1) {
        const v = grid.sample_grid[row]?.[col];
        if (v === null || v === undefined || !Number.isFinite(v)) {
          cells[row * cols + col] = "#161a17";
        } else {
          const t = (v - rangeMin) / span;
          const idx = Math.max(0, Math.min(255, Math.round(t * 255)));
          cells[row * cols + col] = lut[idx];
        }
      }
    }
    return cells;
  }, [grid, ramp, rangeMin, rangeMax]);

  // Redraw 2D canvas with pan/zoom transform
  useEffect(() => {
    if (mode !== "2d" || !canvasRef.current || !grid) return undefined;
    const offscreen = document.createElement("canvas");
    const [rows, cols] = grid.grid_shape;
    offscreen.width = cols;
    offscreen.height = rows;
    const octx = offscreen.getContext("2d");
    if (!octx) return undefined;
    for (let row = 0; row < rows; row += 1) {
      for (let col = 0; col < cols; col += 1) {
        octx.fillStyle = colorLookup[row * cols + col] ?? "#161a17";
        octx.fillRect(col, row, 1, 1);
      }
    }
    const main = canvasRef.current;
    const ctx = main.getContext("2d");
    if (!ctx) return undefined;
    main.width = main.clientWidth;
    main.height = main.clientHeight;
    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, main.width, main.height);
    const drawW = main.width * view.scale;
    const drawH = main.height * view.scale;
    ctx.drawImage(offscreen, 0, 0, cols, rows, view.x * view.scale, view.y * view.scale, drawW, drawH);
    return undefined;
  }, [mode, grid, colorLookup, view]);

  // 3D scene lifecycle
  const sceneRef = useRef<{
    renderer: THREE.WebGLRenderer;
    camera: THREE.PerspectiveCamera;
    scene: THREE.Scene;
    mesh: THREE.Mesh | null;
    controls: { update: () => void; dispose: () => void };
    animId: number;
  } | null>(null);

  useEffect(() => {
    if (mode !== "3d" || !threeContainerRef.current) return undefined;
    const container = threeContainerRef.current;
    const [rows, cols] = grid?.grid_shape ?? [32, 32];
    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#0b0f0c");
    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / Math.max(container.clientHeight, 1), 0.1, 1000);
    camera.position.set(cols * 0.9, Math.max(rows, cols) * 0.35, cols * 1.15);
    camera.lookAt(cols / 2, 0, rows / 2);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.domElement.style.display = "block";
    container.appendChild(renderer.domElement);

    const ambient = new THREE.AmbientLight("#54624f", 1.1);
    scene.add(ambient);
    const dir = new THREE.DirectionalLight("#ffffff", 1.4);
    dir.position.set(cols * 0.7, 80, rows * 0.4);
    scene.add(dir);

    const gridGeo = new THREE.PlaneGeometry(cols, rows, cols - 1, rows - 1);
    gridGeo.rotateX(-Math.PI / 2);
    const material = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.92, metalness: 0.02 });
    const mesh = new THREE.Mesh(gridGeo, material);
    scene.add(mesh);

    let controls: { update: () => void; dispose: () => void } = { update: () => {}, dispose: () => {} };
    let animId = 0;
    let cancelled = false;
    import("three/examples/jsm/controls/OrbitControls.js").then((mod) => {
      if (cancelled) return;
      const OrbitCtor = (mod as { OrbitControls?: typeof import("three/examples/jsm/controls/OrbitControls.js").OrbitControls }).OrbitControls;
      if (!OrbitCtor) return;
      controls = new OrbitCtor(camera, renderer.domElement) as unknown as { update: () => void; dispose: () => void };
      controls.update();
      const animate = () => {
        animId = requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
      };
      animate();
    }).catch(() => {
      const animate = () => {
        animId = requestAnimationFrame(animate);
        renderer.render(scene, camera);
      };
      animate();
    });

    sceneRef.current = { renderer, camera, scene, mesh, controls, animId };

    const handleResize = () => {
      if (!threeContainerRef.current) return;
      const w = threeContainerRef.current.clientWidth;
      const h = Math.max(threeContainerRef.current.clientHeight, 1);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      cancelled = true;
      window.removeEventListener("resize", handleResize);
      const current = sceneRef.current;
      if (current) {
        cancelAnimationFrame(current.animId);
        current.controls?.dispose?.();
        if (current.mesh) {
          current.mesh.geometry?.dispose?.();
          (current.mesh.material as THREE.Material | undefined)?.dispose?.();
        }
        current.renderer?.dispose?.();
        current.renderer?.domElement?.remove();
        sceneRef.current = null;
      }
    };
  }, [mode, datasetId, layer]);

  // Fill 3D mesh vertices and colors when grid/exaggeration/ramp change
  useEffect(() => {
    if (mode !== "3d" || !grid || !sceneRef.current?.mesh) return undefined;
    const mesh = sceneRef.current.mesh;
    const [rows, cols] = grid.grid_shape;
    const position = mesh.geometry.attributes.position as THREE.BufferAttribute;
    const count = position.count;
    const colors: number[] = new Array(count * 3);
    const low = grid.clip_low ?? 0;
    const span = Math.max((grid.clip_high ?? 1) - low, 1e-9);
    for (let i = 0; i < count; i += 1) {
      const col = i % cols;
      const row = Math.floor(i / cols);
      const v = grid.sample_grid[row]?.[col];
      const h = v === null || v === undefined ? -20 : ((v - low) / span) * 42 * exaggeration;
      position.setY(i, h);
      const t = v === null || v === undefined ? 0 : Math.max(0, Math.min(1, (v - low) / span));
      const [r, g, b] = RAMPS[ramp](t);
      colors[i * 3] = r / 255;
      colors[i * 3 + 1] = g / 255;
      colors[i * 3 + 2] = b / 255;
    }
    position.needsUpdate = true;
    mesh.geometry.setAttribute("color", new THREE.BufferAttribute(Float32Array.from(colors), 3));
    mesh.geometry.computeVertexNormals();
    return undefined;
  }, [mode, grid, ramp, exaggeration]);

  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.12 : 0.12;
    setView((v) => ({ ...v, scale: Math.min(6, Math.max(0.6, v.scale + delta)) }));
  };
  const handlePointerDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    dragRef.current = { dragging: true, startX: e.clientX, startY: e.clientY, originX: view.x, originY: view.y };
    (e.target as HTMLCanvasElement).setPointerCapture(e.pointerId);
  };
  const handlePointerMove = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (dragRef.current.dragging) {
      const s = view.scale;
      setView((v) => ({ ...v, x: dragRef.current.originX + (e.clientX - dragRef.current.startX) / s, y: dragRef.current.originY + (e.clientY - dragRef.current.startY) / s }));
      return;
    }
    if (!grid) return;
    const rect = (e.currentTarget as HTMLCanvasElement).getBoundingClientRect();
    const [rows, cols] = grid.grid_shape;
    const col = Math.floor(((e.clientX - rect.left) / rect.width) * cols);
    const row = Math.floor(((e.clientY - rect.top) / rect.height) * rows);
    if (row >= 0 && row < rows && col >= 0 && col < cols) {
      const [left, bottom, right, top] = grid.bounds;
      const px = left + ((right - left) * col) / cols;
      const py = top - ((top - bottom) * row) / rows;
      setCoords(`X ${px.toFixed(1)}  Y ${py.toFixed(1)}  [${col}, ${row}]`);
      const v = grid.sample_grid[row]?.[col];
      setValueUnderCursor(typeof v === "number" && Number.isFinite(v) ? v.toFixed(1) : "no data");
    }
  };
  const handlePointerUp = () => {
    dragRef.current.dragging = false;
  };

  return (
    <div className={`terrain-viewer${fullscreen ? " terrain-viewer-fullscreen" : ""}`}>
      <div className="viewer-toolbar">
        <div>
          <span className="method-tag">{datasetId === "moon_lola" ? "MOON LOLA — VALIDATED" : datasetId === "mars_jezero_ctx_dtm" ? "MARS JEZERO CTX DTM — VALIDATED" : "DEATH VALLEY — USGS 3DEP"}</span>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          <div className="segmented" role="group" aria-label="Terrain view mode">
            <button type="button" className={mode === "2d" ? "selected" : ""} onClick={() => setMode("2d")}>2D MAP</button>
            <button type="button" className={mode === "3d" ? "selected" : ""} onClick={() => setMode("3d")}>3D TERRAIN</button>
          </div>
          {mode === "2d" && (
            <div className="viewer-toolbar-zoom">
              <button type="button" aria-label="Zoom out" onClick={() => setView((v) => ({ ...v, scale: Math.max(0.6, v.scale - 0.3) }))}>−</button>
              <span>{Math.round(view.scale * 100)}%</span>
              <button type="button" aria-label="Zoom in" onClick={() => setView((v) => ({ ...v, scale: Math.min(6, v.scale + 0.3) }))}>+</button>
              <button type="button" onClick={() => setView({ x: 0, y: 0, scale: 1 })}>RESET</button>
              <button type="button" onClick={() => setFullscreen((s) => !s)}>{fullscreen ? "EXIT FULLSCREEN" : "FULLSCREEN"}</button>
            </div>
          )}
          {mode === "3d" && (
            <div className="viewer-toolbar-zoom" aria-label="Vertical exaggeration">
              <span className="control-label">VERTICAL EXAGGERATION</span>
              <input type="range" min={0.4} max={3} step={0.1} value={exaggeration} onChange={(e) => setExaggeration(Number(e.target.value))} aria-label="Vertical exaggeration" />
              <span>{exaggeration.toFixed(1)}×</span>
              <button type="button" onClick={() => setFullscreen((s) => !s)}>{fullscreen ? "EXIT FULLSCREEN" : "FULLSCREEN"}</button>
            </div>
          )}
        </div>
      </div>

      <div className="layer-strip" role="tablist" aria-label="Elevation layers">
        {TERRAIN_LAYERS.map((l) => (
          <button key={l.id} type="button" className={`layer-chip ${layer === l.id ? "selected" : ""}`} role="tab" aria-selected={layer === l.id} onClick={() => onLayerChange(l.id)}>
            {l.label}
          </button>
        ))}
      </div>

      {error ? (
        <div className="grid-unavailable" role="alert">
          <span className="method-tag">LAYER UNAVAILABLE</span>
          <p>{error}. Verify the backend is reachable at http://localhost:8000 and the raster dataset loads (see DATA &amp; METHODS).</p>
        </div>
      ) : null}

      {loading && !grid ? <div className="loading-state">LOADING TERRAIN GRID<span className="pulse-line" /></div> : null}

      {mode === "2d" && (
        <div className="raster-stage-2d">
          <canvas
            ref={canvasRef}
            width={720}
            height={430}
            className="terrain-canvas"
            aria-label={`${layer} visualization for ${datasetId}`}
            onWheel={handleWheel}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerLeave={handlePointerUp}
          />
          <div className="coord-readout" aria-live="polite">
            <span>X/Y {coords}</span>
            <span>VALUE {valueUnderCursor} {layerUnits(layer)}</span>
          </div>
          {showLegend && grid ? (
            <div className="raster-legend">
              <span className="legend-label">{layer.toUpperCase().replace(/_/g, " ")} — {layerUnits(layer)}</span>
              <div className="legend-gradient" style={{ background: `linear-gradient(90deg, ${Array.from({ length: 32 }, (_, i) => { const [r, g, b] = RAMPS[ramp](i / 31); return `rgb(${r},${g},${b})`; }).join(",")})` }} />
              <div className="legend-ticks">
                <span>{rangeMin.toFixed(1)}</span>
                <span>{((rangeMin + rangeMax) / 2).toFixed(1)}</span>
                <span>{rangeMax.toFixed(1)}</span>
              </div>
            </div>
          ) : null}
        </div>
      )}

      {mode === "3d" && (
        <div className="three-container" ref={threeContainerRef} aria-label="3D terrain surface" />
      )}

      <div className="terrain-controls">
        <div className="color-ramp-row" role="group" aria-label="Color ramp">
          <span className="control-label">RAMP</span>
          {Object.keys(RAMP_LABELS).map((key) => (
            <button key={key} type="button" className={`ramp-chip ${ramp === key ? "selected" : ""}`} onClick={() => setRamp(key)}>{RAMP_LABELS[key]}</button>
          ))}
        </div>
        <div className="range-row" role="group" aria-label="Display range">
          <span className="control-label">DISPLAY</span>
          <span className="range-num">{rangeMin.toFixed(1)}</span>
          <input type="range" min={grid?.clip_low ?? 0} max={grid?.clip_high ?? 1} step={Math.max(0.01, ((grid?.clip_high ?? 1) - (grid?.clip_low ?? 0)) / 400)} value={rangeMin} onChange={(e) => setRangeMin(Number(e.target.value))} aria-label="Minimum display value" />
          <input type="range" min={grid?.clip_low ?? 0} max={grid?.clip_high ?? 1} step={Math.max(0.01, ((grid?.clip_high ?? 1) - (grid?.clip_low ?? 0)) / 400)} value={rangeMax} onChange={(e) => setRangeMax(Number(e.target.value))} aria-label="Maximum display value" />
          <span className="range-num">{rangeMax.toFixed(1)}</span>
          <button type="button" className="mini-button" onClick={() => { if (grid) { setRangeMin(grid.clip_low); setRangeMax(grid.clip_high); } }}>RESET RANGE</button>
          <button type="button" className="mini-button" onClick={() => setShowLegend((s) => !s)}>{showLegend ? "HIDE LEGEND" : "SHOW LEGEND"}</button>
        </div>
      </div>

      <div className="terrain-meta">
        <dl>
          <dt>RESOLUTION</dt>
          <dd>{grid?.resolution_m?.toFixed?.(0) ?? "?"} m grid post spacing{datasetId === "usgs_3dep_death_valley" ? " (resampled from ~29.3 m native 1-arc-second source)" : ""}</dd>
          <dt>COVERAGE</dt>
          <dd>{grid ? `${grid.downsampled_dimensions[0]}×${grid.downsampled_dimensions[1]} display samples; elevation ${(grid.elevation_stats.min ?? 0).toFixed(0)} – ${(grid.elevation_stats.max ?? 0).toFixed(0)} m` : "loading…"}</dd>
          <dt>SOURCE</dt>
          <dd>{datasetId === "moon_lola" ? "LOLA south-polar window (LDEM_80S_20MPP_ADJ), windowed; nominal 20 m/pixel" : datasetId === "usgs_3dep_death_valley" ? "USGS 3DEP 1-arc-second tile n37w117 → EPSG:26911 at 20 m grid; native ~29.3 m; vertical datum NAVD88" : "Jezero CTX DTM (JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0), 20 m/pixel"}</dd>
        </dl>
      </div>
    </div>
  );
}
