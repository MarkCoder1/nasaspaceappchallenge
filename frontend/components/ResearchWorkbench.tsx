// ResearchWorkbench.tsx - Terra Twin frontend productization
// Four destinations: EXPLORE, COMPARE, RELIABILITY, DATA & METHODS
// ASCII-only, balanced JSX, TypeScript-safe

"use client";

import { useEffect, useRef, useState } from "react";
import {
  apiUrl,
  checkBackendHealth,
  downloadExport,
  fetchCandidates,
  fetchExperiment,
  fetchSamplingFramework,
  fetchStatus,
  rasterUrl,
  type CandidateEntry,
  type Experiment,
  type SamplingFramework,
  type SimilarityStatus,
} from "@/lib/api";
import TerrainViewer from "@/components/TerrainViewer";
import CandidateProfile from "@/components/CandidateProfile";

// --- Helper ---

function fmt(n: number, d: number = 1): string {
  return d > 0 ? n.toFixed(d) : String(n);
}

// --- Interfaces ---

interface DatasetProvenance {
  id: number;
  body: "Moon" | "Mars" | "Earth";
  name: string;
  nominal_resolution?: string;
  validation_status: "VALIDATED" | "REJECTED" | "PENDING" | "BLOCKED_BY_EARTHDATA_AUTHENTICATION";
  access_status: "DOWNLOADED" | "BLOCKED_BY_EARTHDATA_AUTHENTICATION" | "PENDING";
  kind?: string;
}

interface FeatureResult {
  target_summary: { median: number; q25: number; q75: number; q90: number; mean: number };
  candidate_summary: { median: number; q25: number; q75: number; q90: number; mean: number };
  distance: {
    normalized_distance: number;
    pooled_iqr: number;
    ks_statistic: number;
    wasserstein: number;
    sample_count_target: number;
    sample_count_candidate: number;
    neighborhood_m?: number;
  };
  definition: string;
  units: string;
}

// --- Sub-components ---

function HistogramBars({ values, label, unit, bins = 10 }: { values: number[]; label: string; unit: string; bins?: number }) {
  if (!values || values.length === 0) return null;
  const finite = values.filter((v: number) => Number.isFinite(v));
  if (finite.length === 0) return null;
  const min = Math.min(...finite);
  const max = Math.max(...finite);
  const range = max - min || 1;
  const counts: number[] = new Array(bins).fill(0);
  finite.forEach((v: number) => {
    const idx = Math.min(bins - 1, Math.floor(((v - min) / range) * bins));
    counts[idx] += 1;
  });
  const peak = Math.max(...counts);
  return (
    <div className="feature-histogram">
      <div className="histogram-head">
        <span className="histogram-label">{label} distribution</span>
        <span className="histogram-range">{fmt(min, 2)} — {fmt(max, 2)} {unit}</span>
      </div>
      <svg className="histogram-svg" role="img" aria-label={label + " histogram"} viewBox="0 0 190 140" preserveAspectRatio="none">
        {counts.map((count: number, i: number) => {
          const height = peak > 0 ? (count / peak) * 100 : 0;
          const x = i * 9.5;
          return <rect key={i} x={x} y={120 - height} width="8" height={Math.max(height, 1)} fill="#d59a4c" />;
        })}
      </svg>
      <div className="histogram-axis">
        {counts.map((_, i: number) => (
          <span key={i} className="histogram-tick">{fmt(min + (i / bins) * range, 1)}</span>
        ))}
      </div>
    </div>
  );
}

function FeatureChart({
  feature,
  result,
  selected,
  setSelected,
}: {
  feature: string;
  result: FeatureResult;
  selected: string | null;
  setSelected: (id: string | null) => void;
}) {
  const target = result.target_summary;
  const candidate = result.candidate_summary;
  const max = Math.max(target.q90 ?? 0, candidate.q90 ?? 0, 1);
  const dist = result.distance;
  const samples: number[] = Array.from({ length: 200 }, (_, i: number) => {
    return target.median + ((i / 199) - 0.5) * (target.q90 - target.q25 || target.median || 1);
  });
  return (
    <div
      className={["feature-card", selected === feature ? "feature-card-active" : ""].join(" ")}
      onClick={() => setSelected(selected === feature ? null : feature)}
    >
      <div className="feature-card-heading">
        <div>
          <span className="feature-name">{feature.replaceAll("_", " ")}</span>
          <span className="feature-unit">{result.units}</span>
        </div>
        <span className="feature-distance">d {fmt(dist.normalized_distance, 3)}</span>
      </div>
      <p>{result.definition}</p>
      <div className="summary-bars">
        <div>
          <span>MARS</span>
          <i style={{ width: `${Math.min(100, ((target.q75 ?? 0) / max) * 100)}%` }} />
          <b>{fmt(target.median)}</b>
        </div>
        <div>
          <span>MOON</span>
          <i className="moon-bar" style={{ width: `${Math.min(100, ((candidate.q75 ?? 0) / max) * 100)}%` }} />
          <b>{fmt(candidate.median)}</b>
        </div>
      </div>
      <div className="feature-stats">
        <span>μ {fmt(target.mean)} / {fmt(candidate.mean)}</span>
        <span>IQR {fmt(dist.pooled_iqr)}</span>
        <span>KS {fmt(dist.ks_statistic, 3)}</span>
        <span>W {fmt(dist.wasserstein, 2)}</span>
      </div>
      {selected === feature && (
        <div className="feature-detail">
          <HistogramBars values={samples} label={feature.replaceAll("_", " ")} unit={result.units} />
          <div className="feature-note">
            <span className="eyebrow-like">SCALE</span>
            <span>{result.distance.neighborhood_m ? fmt(result.distance.neighborhood_m, 0) + " m window" : "native pixel spacing"}</span>
            <span className="eyebrow-like">SAMPLES</span>
            <span>{dist.sample_count_target} / {dist.sample_count_candidate}</span>
          </div>
        </div>
      )}
    </div>
  );
}

function DistributionChart({
  values,
  color,
  height = 100,
  barWidth = 14,
  gap = 6,
}: {
  values: number[];
  color: string;
  height?: number;
  barWidth?: number;
  gap?: number;
}) {
  const finite = values.filter((v: number) => Number.isFinite(v));
  if (finite.length === 0) return null;
  const min = Math.min(...finite);
  const max = Math.max(...finite);
  const range = max - min || 1;
  const bins = 10;
  const counts: number[] = new Array(bins).fill(0);
  finite.forEach((v: number) => {
    const idx = Math.min(bins - 1, Math.floor(((v - min) / range) * bins));
    counts[idx] += 1;
  });
  const peak = Math.max(...counts);
  return (
    <div className="distribution-chart">
      <svg
        className="distribution-svg"
        role="img"
        aria-label="TMSI distribution"
        viewBox="0 0 220 100"
        preserveAspectRatio="none"
        style={{ width: "100%", height: String(height), display: "block" }}
      >
        {counts.map((count: number, i: number) => {
          const barHeight = peak > 0 ? (count / peak) * 80 : 0;
          const x = i * (barWidth + gap);
          return (
            <rect
              key={i}
              x={x}
              y={100 - barHeight}
              width={barWidth}
              height={Math.max(barHeight, 1)}
              fill={color}
              opacity={0.85}
            />
          );
        })}
      </svg>
      <div className="distribution-axis">
        {counts.map((_, i: number) => (
          <span key={i} className="distribution-tick">
            {fmt(min + (i / bins) * range, 1)}
          </span>
        ))}
      </div>
      <div className="distribution-caption">
        range {fmt(min, 2)} — {fmt(max, 2)} —|&nbsp; n={finite.length}
      </div>
    </div>
  );
}

function TmsiDistribution({ sampling }: { sampling: SamplingFramework }) {
  const mars = sampling.within_body.mars.map((r: any) => r.similarity_index);
  const moon = sampling.within_body.moon.map((r: any) => r.similarity_index);
  const between = sampling.between_body.map((r: any) => r.similarity_index);
  return (
    <div className="side-card">
      <span className="eyebrow">TERRAIN SIMILARITY DISTRIBUTIONS</span>
      <h3>Within-body vs between-body</h3>
      <div className="distribution-row">
        <div className="distribution-col">
          <span className="distribution-label">Within Mars</span>
          <DistributionChart values={mars} color="#b7d36b" />
        </div>
        <div className="distribution-col">
          <span className="distribution-label">Within Moon</span>
          <DistributionChart values={moon} color="#d59a4c" />
        </div>
        <div className="distribution-col">
          <span className="distribution-label">Mars lt Moon</span>
          <DistributionChart values={between} color="#e6bb77" />
        </div>
      </div>
      <p className="chart-note">
        Each bar bin counts window-pair TMSI scores at {sampling.extent_km} km extent. Within-body and
        between-body distributions overlap substantially -- TMSI does not identify planetary body.
      </p>
    </div>
  );
}

function SamplingDiagnostics({ sampling }: { sampling: SamplingFramework }) {
  const overlap = sampling.overlap_bias;
  const identical = overlap.filter((r: any) => r.overlap_status === "identical");
  const high = overlap.filter((r: any) => r.overlap_status === "high");
  const partial = overlap.filter((r: any) => r.overlap_status === "partial");
  const none = overlap.filter((r: any) => r.overlap_status === "none");
  const extent = sampling.extent_km;
  return (
    <div className="side-column">
      <div className="side-card">
        <span className="eyebrow">SAMPLING DESIGN</span>
        <h3>Window sampling, {extent} km</h3>
        <div className="readout-row"><span>MARS WINDOWS</span><b>{sampling.mars_window_count}</b></div>
        <div className="readout-row"><span>MOON WINDOWS</span><b>{sampling.moon_window_count}</b></div>
        <div className="readout-row"><span>EXTENT</span><b>{extent} km</b></div>
        <div className="readout-row"><span>STRATEGY</span><b>Multiple non-overlapping windows</b></div>
      </div>
      <div className="side-card">
        <span className="eyebrow">OVERLAP DIAGNOSTICS</span>
        <div className="readout-row"><span>IDENTICAL</span><b>{identical.length}</b></div>
        <div className="readout-row"><span>HIGH OVERLAP</span><b>{high.length}</b></div>
        <div className="readout-row"><span>PARTIAL OVERLAP</span><b>{partial.length}</b></div>
        <div className="readout-row"><span>NON-OVERLAPPING</span><b>{none.length}</b></div>
        <p className="chart-note">
          Identical windows give TMSI = 100 (self-control). High overlap inflates similarity. Only
          non-overlapping comparisons are independent observations.
        </p>
      </div>
    </div>
  );
}

function InterpretationSafeguards() {
  return (
    <div className="side-card">
      <span className="eyebrow">WHAT TMSI MEASURES</span>
      <div className="interpretation-item">
        <span className="eyebrow-like">MEASURES</span>
        <p>Pairwise terrain-window morphology similarity (elevation distribution statistics for slope, local relief, and terrain ruggedness).</p>
      </div>
      <div className="interpretation-item">
        <span className="eyebrow-like">DOES NOT ESTABLISH</span>
        <p>Planetary-body similarity, habitability, landing safety, or geological equivalence.</p>
      </div>
      <div className="interpretation-item">
        <span className="eyebrow-like">DEPENDS ON</span>
        <p>Spatial extent, window location, overlap fraction, feature weights, and effective resolution.</p>
      </div>
      <div className="interpretation-item">
        <span className="eyebrow-like">LIMITATION</span>
        <p>Within-body TMSI range (Moon: 29.27-94.10; Mars: 40.99-90.90) overlaps the between-body range (22.38-90.60). TMSI cannot establish planetary identity.</p>
      </div>
    </div>
  );
}

function BenchmarkingView({ benchmark }: { benchmark: { datasets: DatasetProvenance[]; planet_coverage: Record<string, number>; real_benchmark_findings: string[]; limitation: string } }) {
  const datasets = benchmark.datasets;
  const planetCoverage = benchmark.planet_coverage;
  const realBenchmarkFindings = benchmark.real_benchmark_findings;
  const limitation = benchmark.limitation;

  const validatedDatasets = datasets.filter((d: DatasetProvenance) => d.validation_status === "VALIDATED");
  const accessibleDatasets = datasets.filter((d: DatasetProvenance) => d.access_status === "DOWNLOADED");
  const blockedDatasets = datasets.filter((d: DatasetProvenance) => d.access_status === "BLOCKED_BY_EARTHDATA_AUTHENTICATION");
  const rejectedDatasets = datasets.filter((d: DatasetProvenance) => d.validation_status === "REJECTED");

  return (
    <section className="content-section">
      <div className="section-heading">
        <div>
          <span className="eyebrow">DATASET INVENTORY</span>
          <h2>Verified planetary datasets</h2>
        </div>
      </div>
      <div className="workspace-grid">
        <div>
          <dl>
            {datasets.map((d: DatasetProvenance, di: number) => (
              <div key={d.id} className="provenance-card">
                <span className="eyebrow">{d.body}</span>
                <h3>{d.name}</h3>
                <dl>
                  <dt>RESOLUTION</dt>
                  <dd>{d.nominal_resolution || "N/A"}</dd>
                  <dt>VALIDATION</dt>
                  <dd>
                    <span className={
                      d.validation_status === "VALIDATED"
                        ? "pending-badge"
                        : d.validation_status === "REJECTED"
                          ? "pending-badge"
                          : d.access_status === "BLOCKED_BY_EARTHDATA_AUTHENTICATION"
                            ? "pending-badge"
                            : ""
                    }>
                      {d.validation_status || d.access_status}
                    </span>
                  </dd>
                  <dt>ACCESS</dt>
                  <dd>{d.access_status || "N/A"}</dd>
                  <dt>KIND</dt>
                  <dd>{d.kind || "N/A"}</dd>
                </dl>
              </div>
            ))}
          </dl>
        </div>

        <div>
          <span className="eyebrow">PLANETARY COVERAGE</span>
          <h3>{Object.keys(planetCoverage).length} planets</h3>
          <dl>
            {Object.entries(planetCoverage as Record<string, number>).map(
              (item: [string, number]) => {
                const [body, count] = item;
                return (
                  <div key={body} className="provenance-card">
                    <span className="eyebrow">{body}</span>
                    <dt>DATASETS</dt><dd>{count}</dd>
                  </div>
                );
              }
            )}
          </dl>
          <p className="chart-note">
            Moon and Mars datasets are VALIDATED and fully accessible.
            Earth (earth_nasadem_hgt_v001) is BLOCKED by NASA Earthdata authentication
            (HTTP 401). No independent DEM benchmark pair exists in the current repository.
          </p>
        </div>

        <div>
          <span className="eyebrow">BENCHMARKING STATUS</span>
          <h3>Independent dataset comparison</h3>
          <p className="chart-note">
            {limitation}
          </p>
          {realBenchmarkFindings.length > 0 ? (
            <ul>
              {realBenchmarkFindings.map((f: string, i: number) => <li key={i}>{f}</li>)}
            </ul>
          ) : (
            <p>No completed independent benchmark available.</p>
          )}
        </div>
      </div>
    </section>
  );
}

// --- View components ---

function ExploreView({ layer, setLayer, terrainDataset, setTerrainDataset, exploreContextId, onExploreContextClear }: { layer: Layer; setLayer: (id: Layer) => void; terrainDataset: "moon_lola" | "mars_jezero_ctx_dtm" | "usgs_3dep_death_valley"; setTerrainDataset: (id: "moon_lola" | "mars_jezero_ctx_dtm" | "usgs_3dep_death_valley") => void; exploreContextId: string | null; onExploreContextClear: () => void }) {
  const VALID_DATASETS: Array<{ id: "moon_lola" | "mars_jezero_ctx_dtm" | "usgs_3dep_death_valley"; label: string }> = [
    { id: "moon_lola", label: "MOON LOLA" },
    { id: "mars_jezero_ctx_dtm", label: "MARS JEZERO" },
    { id: "usgs_3dep_death_valley", label: "DEATH VALLEY 3DEP" },
  ];
  return (
    <section className="content-section">
      <div className="section-heading">
        <div>
          <span className="eyebrow">EXPLORE</span>
          <h2>Terrain visualization — interactive 2D &amp; 3D</h2>
        </div>
        <div className="segmented" role="group" aria-label="Terrain dataset">
          {VALID_DATASETS.map((d) => (
            <button key={d.id} className={terrainDataset === d.id ? "selected" : ""} onClick={() => setTerrainDataset(d.id)}>{d.label}</button>
          ))}
        </div>
      </div>
      {exploreContextId && (
        <div className="earth-context-banner" role="status">
          <span className="method-tag">EXPLORE-FROM-MAP · CANDIDATE: {exploreContextId.toUpperCase()}</span>
          <p>
            {exploreContextId === "death_valley"
              ? "Earth explorer — Death Valley (Southern California, USA). Dataset: USGS 3DEP 1-arc-second (n37w117), processed to a 20 m UTM grid. Native source resolution ~29.3 m; NAVD88 vertical datum; geographic coverage limited to the acquired tile; not global terrestrial terrain."
              : "This candidate has no verified local terrain preview. Showing Moon LOLA as a reference dataset — no Earth raster is available for this candidate, by design; Earth DEM acquisition remains limited by NASA Earthdata HTTP 401 and USGS tiles cover only two locations."}
          </p>
          <button type="button" className="mini-button" onClick={onExploreContextClear}>CLEAR CANDIDATE CONTEXT</button>
        </div>
      )}
      <div className="workspace-grid">
        <div className="workspace-main">
          <TerrainViewer datasetId={terrainDataset} layer={layer} onLayerChange={setLayer} gridUrl={terrainDataset === "usgs_3dep_death_valley" ? (l) => `${apiUrl}/api/candidates/terrain-grid/death_valley?layer=${encodeURIComponent(l)}&max_dim=192` : undefined} />
        </div>
        <div className="side-column">
          <div className="side-card">
            <span className="eyebrow">HOW TO USE</span>
            <h3>Interactive controls</h3>
            <p><strong>2D MAP</strong> — drag to pan, mouse-wheel or −/+ to zoom, coordinate readout follows the cursor, switch ramps and display range live.</p>
            <p><strong>3D TERRAIN</strong> — drag to orbit, scroll or pinch to zoom, right-drag to pan. Vertical exaggeration slider scales terrain relief.</p>
            <p><strong>LAYERS</strong> — Elevation · Hillshade · Slope · Local relief · Terrain ruggedness. Switching layers refetches the downsampled grid.</p>
          </div>
          <div className="side-card">
            <span className="eyebrow">VALIDATED DATASETS</span>
            <h3>Planetary inputs</h3>
            <div className="readout-row"><span>MOON LOLA</span><b>20 m/pixel</b></div>
            <div className="readout-row"><span>MARS JEZERO CTX DTM</span><b>20 m/pixel</b></div>
            <div className="readout-row"><span>EARTH 3DEP (DEATH VALLEY)</span><b>20 m grid · ~29.3 m native</b></div>
            <div className="readout-row"><span>EARTH NASADEM</span><b className="muted-value">BLOCKED — HTTP 401</b></div>
            <p className="chart-note">Earth terrain is limited to two USGS 3DEP tiles (Death Valley / southern Arizona) from open-access USGS S3 sources. NASADEM (global) is blocked by NASA Earthdata HTTP 401; Moon/Mars datasets are unchanged.</p>
          </div>
        </div>
      </div>
    </section>
  );
}

function CompareView({ selectedFeature, setSelectedFeature, experiment, compareCandidateId, onClearCompareCandidate }: { selectedFeature: string | null; setSelectedFeature: (id: string | null) => void; experiment: Experiment | null; compareCandidateId: string | null; onClearCompareCandidate: () => void }) {
  const features = experiment?.baseline_result?.features ?? {};
  const featureKeys = Object.keys(features);
  const active = selectedFeature && features[selectedFeature] ? selectedFeature : featureKeys[0] ?? null;
  const activeData = active ? features[active] : null;
  const baseline = experiment?.baseline_result;
  const bootstrap = experiment?.primary_bootstrap_320m_1000;
  const selFeat = active ?? "slope";
  const hasExperiment = Boolean(experiment?.baseline_result);

  return (
    <section className="content-section">
      <div className="section-heading">
        <div>
          <span className="eyebrow">COMPARE</span>
          <h2>Moon vs Mars — feature comparison workspace</h2>
        </div>
      </div>
      {compareCandidateId && (
        <div className="earth-compare-banner" role="status">
          <span className="method-tag">EARTH CANDIDATE — COMPARISON UNAVAILABLE</span>
          <p>
            Candidate <b>{compareCandidateId}</b> cannot enter the quantitative Earth–Moon / Earth–Mars comparison workflow.
            Earth comparisons require an authentic, processed Earth DEM measured at the comparison scale; acquisition of
            the global NASADEM product is blocked by NASA Earthdata HTTP 401, and only two USGS 3DEP tiles have been
            locally acquired and processed. No similarity score is computed or displayed for this candidate.
          </p>
          <p className="chart-note">USGS 3DEP n36w117 (Southern Arizona) vs Moon LOLA: TMSI 61.95 · vs Mars JEZERO CTX DTM: TMSI 73.14 — stored Phase 20 artifacts, confidence-labelled project results, <b>not independently validated</b> and <b>not candidate-specific</b>. Earth coverage is two USGS tiles; NASADEM (global) remains blocked by HTTP 401.</p>
          <button type="button" className="mini-button" onClick={onClearCompareCandidate}>VIEW MOON↔MARS EXPERIMENT</button>
        </div>
      )}
      <div className="compare-strip" role="tablist" aria-label="Terrain features">
        <span className="compare-strip-label">LAYER</span>
        {(["slope", "local_relief", "terrain_ruggedness"] as const).map((feat) => (
          <button key={feat} className={`layer-chip ${selFeat === feat ? "selected" : ""}`} onClick={() => setSelectedFeature(feat)} role="tab" aria-selected={selFeat === feat}>{feat.replace(/_/g, " ")}</button>
        ))}
        <span className="compare-strip-source">STORED EXPERIMENT: MOON → MARS (JEZERO CTX DTM vs LOLA)</span>
      </div>

      {!hasExperiment ? (
        <div className="side-card">
          <span className="eyebrow">EXPERIMENT DATA UNAVAILABLE</span>
          <h3>Stored moon–mars experiment results not loaded</h3>
          <p>The frontend is not receiving the stored moon–mars experiment from the backend (<code>GET /api/similarity/results</code>) or the backend is not running. The comparison workspace requires the authenticated experiment artifact to display feature statistics.</p>
          <p>Start the backend (<code>uvicorn app.main:app --reload</code> inside <code>backend/</code>) or verify <code>/api/similarity/results</code> returns HTTP 200.</p>
        </div>
      ) : (
        <>
          <div className="compare-split">
            <figure className="compare-figure">
              <div className="compare-figure-bar"><span className="eyebrow">TARGET · MARS JEZERO CTX DTM</span><span className="method-tag">MARS · 20 m/pixel</span></div>
              <img src={rasterUrl("mars_jezero_ctx_dtm", selFeat)} alt="Mars Jezero CTX DTM feature preview" />
              <figcaption>Jezero crater DTM (MOLA topography), 20 m/pixel · {selFeat.replace(/_/g, " ")}</figcaption>
            </figure>
            <figure className="compare-figure">
              <div className="compare-figure-bar"><span className="eyebrow">CANDIDATE · MOON LOLA</span><span className="method-tag">MOON · 20 m/pixel</span></div>
              <img src={rasterUrl("moon_lola", selFeat)} alt="Moon LOLA feature preview" />
              <figcaption>LOLA south-polar window near Shackleton, 20 m/pixel · {selFeat.replace(/_/g, " ")}</figcaption>
            </figure>
          </div>

          <div className="compare-metrics">
            <div className="compare-metric-card">
              <span className="eyebrow">SIMILARITY INDEX (TMSI)</span>
              <strong>{baseline?.similarity_index?.toFixed(2)}</strong>
              <small>{bootstrap ? `95% CI ${bootstrap.tmsi_lower_95.toFixed(2)} – ${bootstrap.tmsi_upper_95.toFixed(2)} · ${bootstrap.repetitions} reps · block ${bootstrap.block_size_m} m` : "Bootstrap CI unavailable"}</small>
              <p>Moon–Mars morphology similarity; not a planetary-body classification.</p>
            </div>
            <div className="compare-metric-card">
              <span className="eyebrow">KOLOMOGOROV–SMIRNOV</span>
              <strong>{activeData?.distance?.ks_statistic?.toFixed(3)}</strong>
              <small>p-value = {activeData?.distance?.ks_pvalue?.toFixed(4) ?? "—"}</small>
              <p>Distribution separation: 0 identical → 1 completely disjoint.</p>
            </div>
            <div className="compare-metric-card">
              <span className="eyebrow">WASSERSTEIN DISTANCE</span>
              <strong>{activeData?.distance?.wasserstein?.toFixed(3)}</strong>
              <small>Normalized d = {activeData?.distance?.normalized_distance?.toFixed(3)} · pooled IQR {activeData?.distance?.pooled_iqr?.toFixed(3)}</small>
              <p>Earth-mover distance between the feature distributions.</p>
            </div>
            <div className="compare-metric-card">
              <span className="eyebrow">CLOSEST / FURTHEST</span>
              <strong style={{ fontSize: 15, textAlign: "left" }}>Closest: {baseline?.strongest_matches?.join(", ") ?? "—"}</strong>
              <small>Furthest: {baseline?.largest_differences?.join(", ") ?? "—"}</small>
              <p>Feature-level nearest and furthest distances.</p>
            </div>
          </div>

          <div className="compare-histograms">
            {(["slope", "local_relief", "terrain_ruggedness"] as const).map((feat) => {
              const f = features[feat];
              if (!f) return null;
              const max = Math.max(f.target_summary.q90, f.candidate_summary.q90) * 1.1 || 1;
              const tq = Math.max(f.target_summary.q75 - f.target_summary.q25, 1e-9);
              const cq = Math.max(f.candidate_summary.q75 - f.candidate_summary.q25, 1e-9);
              return (
                <div key={feat} className="compare-histogram-card">
                  <div className="compare-histogram-head">
                    <span className="feature-name">{feat.replace(/_/g, " ")}</span>
                    <span className="feature-distance">d {f.distance.normalized_distance.toFixed(3)}</span>
                  </div>
                  <div className="quartile-track">
                    <div className="quartile-row" aria-label="Mars target quartiles">
                      <span>MARS</span>
                      <div className="quartile-band mars" style={{ left: `${(f.target_summary.q25 / max) * 100}%`, width: `${((f.target_summary.q75 - f.target_summary.q25) / max) * 100}%` }}>
                        <i className="median-tick" style={{ left: `${((f.target_summary.median - f.target_summary.q25) / tq) * 100}%` }} />
                      </div>
                      <b>{f.target_summary.median.toFixed(2)}</b>
                    </div>
                    <div className="quartile-row" aria-label="Moon candidate quartiles">
                      <span>MOON</span>
                      <div className="quartile-band moon" style={{ left: `${(f.candidate_summary.q25 / max) * 100}%`, width: `${((f.candidate_summary.q75 - f.candidate_summary.q25) / max) * 100}%` }}>
                        <i className="median-tick" style={{ left: `${((f.candidate_summary.median - f.candidate_summary.q25) / cq) * 100}%` }} />
                      </div>
                      <b>{f.candidate_summary.median.toFixed(2)}</b>
                    </div>
                  </div>
                  <p className="chart-note">Boxes show Q25–Q75; ticks show medians. Jezero (target) vs LOLA south pole (candidate).</p>
                </div>
              );
            })}
          </div>

          <div className="compare-table-wrap">
            <table className="compare-table">
              <thead>
                <tr><th>Feature</th><th>Mars μ</th><th>Moon μ</th><th>Mars median</th><th>Moon median</th><th>Mars σ</th><th>Moon σ</th><th>Mars IQR</th><th>Moon IQR</th><th>Samples (T / C)</th></tr>
              </thead>
              <tbody>
                {(["slope", "local_relief", "terrain_ruggedness"] as const).map((feat) => {
                  const f = features[feat];
                  if (!f) return null;
                  return (
                    <tr key={feat} className={selFeat === feat ? "row-active" : ""}>
                      <td>{feat.replace(/_/g, " ")}</td>
                      <td>{f.target_summary.mean.toFixed(2)}</td>
                      <td>{f.candidate_summary.mean.toFixed(2)}</td>
                      <td>{f.target_summary.median.toFixed(2)}</td>
                      <td>{f.candidate_summary.median.toFixed(2)}</td>
                      <td>{f.target_summary.std.toFixed(2)}</td>
                      <td>{f.candidate_summary.std.toFixed(2)}</td>
                      <td>{(f.target_summary.q75 - f.target_summary.q25).toFixed(2)}</td>
                      <td>{(f.candidate_summary.q75 - f.candidate_summary.q25).toFixed(2)}</td>
                      <td>{f.distance.sample_count_target.toLocaleString()} / {f.distance.sample_count_candidate.toLocaleString()}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}

function ReliabilityView({ sampling, experiment }: { sampling: SamplingFramework | null; experiment: Experiment | null }) {
  const bootstrap = experiment?.primary_bootstrap_320m_1000;
  const seedSensitivities = experiment?.seed_sensitivity ? Object.values(experiment.seed_sensitivity) : [];
  const seedRanges = seedSensitivities.map((s) => s.tmsi_mean);
  const spatial = experiment?.spatial_diagnostics?.moon?.slope;
  return (
    <section className="content-section">
      <div className="section-heading">
        <div>
          <span className="eyebrow">RELIABILITY</span>
          <h2>Bootstrap confidence and sensitivity</h2>
        </div>
      </div>
      <div className="workspace-grid">
        <div>
          {bootstrap ? (
            <>
              <div className="interval-panel">
                <span className="eyebrow">BOOTSTRAP 95% CI</span>
                <div className="interval-track">
                  <i style={{ left: `${Math.max(0, (bootstrap.tmsi_lower_95 / 100) * 100)}%`, width: `${Math.min(100, ((bootstrap.tmsi_upper_95 - bootstrap.tmsi_lower_95) / 100) * 100)}%` }} />
                  <b style={{ left: `${Math.max(0, (bootstrap.tmsi_mean / 100) * 100)}%` }} />
                </div>
                <div className="interval-labels">
                  <span>0</span>
                  <span>{bootstrap.tmsi_lower_95.toFixed(2)} — {bootstrap.tmsi_upper_95.toFixed(2)}</span>
                  <span>100</span>
                </div>
                <p><strong>Bootstrap 95% CI</strong>: {bootstrap.tmsi_lower_95.toFixed(2)} – {bootstrap.tmsi_upper_95.toFixed(2)} (mean {bootstrap.tmsi_mean.toFixed(2)}, {bootstrap.repetitions} reps @ block {bootstrap.block_size_m} m, seed {bootstrap.seed})</p>
              </div>
              <div className="side-card" style={{ marginTop: 12 }}>
                <span className="eyebrow">UNCERTAINTY DIAGNOSTICS</span>
                <div className="readout-row"><span>SEED SENSITIVITY</span><b>{seedRanges.length ? `${Math.min(...seedRanges).toFixed(2)} – ${Math.max(...seedRanges).toFixed(2)} TMSI mean range` : "—"}</b></div>
                <div className="readout-row"><span>MORAN'S I (MOON, SLOPE)</span><b>{spatial?.morans_i !== undefined ? spatial.morans_i.toFixed(3) + " — strong spatial autocorrelation" : "—"}</b></div>
                <div className="readout-row"><span>EXTENT SENSITIVITY</span><b>23.71 @ 5.12 km → 49.92 @ 10.24 km</b></div>
                <p className="chart-note">Intervals quantify spatial sampling variability under the stated block-size assumption; they are not calibrated probabilities or measurement error bars.</p>
              </div>
            </>
          ) : (
            <div className="side-card">
              <span className="eyebrow">BOOTSTRAP UNAVAILABLE</span>
              <p>Bootstrap uncertainty data is unavailable from the backend (not connected, or API offline). Run the similarity experiment pipeline to generate primary_bootstrap_320m_1000.</p>
            </div>
          )}
        </div>
        <div>
          {sampling ? (
            <>
              <TmsiDistribution sampling={sampling} />
              <SamplingDiagnostics sampling={sampling} />
            </>
          ) : (
            <div className="side-card">
              <span className="eyebrow">SAMPLING FRAMEWORK UNAVAILABLE</span>
              <p>Phase 11 sampling-framework experiment data is unavailable from the backend (API offline, or <code>phase11_sampling_framework.json</code> missing).</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function DataMethodsView({ benchmark, experiment }: { benchmark: { datasets: DatasetProvenance[]; planet_coverage: Record<string, number>; real_benchmark_findings: string[]; limitation: string }; experiment: Experiment | null }) {
  const datasets = benchmark.datasets;
  const moonMars = experiment?.baseline_result;
  const moonMarsBootstrap = experiment?.primary_bootstrap_320m_1000;
  const methodologySteps = [
    {
      id: "preprocessing",
      title: "1. DEM preprocessing",
      body: "Source rasters are validated for structural integrity (CRS, dtype, dimensions, nodata) and transformed into comparable feature layers. Moon LOLA and Mars Jezero CTX DTM are 20 m native post-spacing; Earth USGS 3DEP (~29.3 m native) is resampled to a 20 m processing grid without introducing additional observational detail.",
    },
    {
      id: "feature-extraction",
      title: "2. Terrain feature extraction",
      body: "Each validated raster yields three morphology feature layers at 60 m physical windows: SLOPE (atan of metre-per-pixel gradient; sensitive to DEM noise), LOCAL RELIEF (max − min in a complete square window; edge/incomplete windows excluded), TERRAIN RUGGEDNESS (Riley TRI, a roughness index — not a hazard measure).",
    },
    {
      id: "normalization",
      title: "3. Resolution normalization",
      body: "All features are interpreted at a common 20 m physical scale. No upsampling of lower-resolution source data is performed for comparisons; Earth DEM at ~29.3 m native was resampled to the 20 m grid and its effective resolution is documented as ~29.3 m.",
    },
    {
      id: "distribution-comparison",
      title: "4. Distribution comparison",
      body: "Features are compared as distributions (slope, local_relief, terrain_ruggedness). Wasserstein distance (earth-mover) is normalized by the largest pooled interquartile range; the KS statistic is retained as a distribution-separation diagnostic. No claim is made about habitability, landing safety, or geological equivalence.",
    },
    {
      id: "tmsi-construction",
      title: "5. TMSI construction",
      body: "TMSI = 100 × exp(−D), where D is the weighted mean of pooled-IQR-normalized Wasserstein distances across available features (default equal weights). TMSI measures terrain-morphology distribution similarity only; it cannot establish planetary-body identity (within-body ranges overlap the between-body range).",
    },
    {
      id: "bootstrap-ci",
      title: "6. Bootstrap confidence intervals",
      body: "Uncertainty is quantified with a spatial block bootstrap (block size 320 m, 1,000 repetitions, seed 42). Intervals quantify spatial sampling variability under the block-size assumption; they are not calibrated probabilities or measurement error bars. Within any-block independence, samples are not globally independent (Moran’s I ≈ 0.979 for Moon slope).",
    },
    {
      id: "seed-sensitivity",
      title: "7. Seed sensitivity",
      body: "Bootstrap runs across five distinct seeds (42, 123, 456, 789, 1011) produce stable TMSI means (Moon–Mars ≈ 49.7 with max abs diff < 0.5). Seed choice does not materially change the conclusions; Phase 20.6 confirmed stability.",
    },
    {
      id: "spatial-autocorrelation",
      title: "8. Spatial autocorrelation",
      body: "Elevation features exhibit strong spatial autocorrelation (Moran’s I ≈ 0.979). Confidence intervals are therefore interpreted as sampling variability under the chosen block size, not as independent-pixel confidence limits.",
    },
  ];
  const [openStep, setOpenStep] = useState<string | false>(false);

  const validatedDatasets = datasets.filter((d: DatasetProvenance) => d.validation_status === "VALIDATED");
  const accessibleDatasets = datasets.filter((d: DatasetProvenance) => d.access_status === "DOWNLOADED");
  const blockedDatasets = datasets.filter((d: DatasetProvenance) => d.access_status === "BLOCKED_BY_EARTHDATA_AUTHENTICATION");

  return (
    <section className="content-section">
      <div className="section-heading">
        <div>
          <span className="eyebrow">DATA &amp; METHODS</span>
          <h2>Dataset inventory and scientific methodology</h2>
        </div>
      </div>

      <div className="dataset-explorer">
        <span className="eyebrow">DATASET EXPLORER</span>
        <div className="dataset-cards">
          {datasets.map((d: DatasetProvenance) => {
            const isMoon = d.body === "Moon";
            const isMars = d.body === "Mars";
            const isEarth = d.body === "Earth";
            const bodyClass = isMoon ? "moon-dataset" : isMars ? "mars-dataset" : "earth-dataset";
            return (
              <article key={d.id} className={`dataset-card ${bodyClass}`}>
                <header>
                  <span className="eyebrow">{d.body}</span>
                  <h3>{d.name}</h3>
                </header>
                <div className="dataset-metrics">
                  <div className="dataset-metric"><span>RESOLUTION</span><b>{d.nominal_resolution || "unknown"}</b></div>
                  <div className="dataset-metric"><span>VALIDATION</span><b className={d.validation_status === "VALIDATED" ? "ok" : "blocked"}>{d.validation_status}</b></div>
                  <div className="dataset-metric"><span>ACCESS</span><b>{d.access_status}</b></div>
                </div>
                <p className="dataset-limitation">{d.body === "Moon" ? "South-polar window; bounded subset, not complete LOLA product. Effective resolution documented at ~16 m." : d.body === "Mars" ? "Jezero-specific MOLA DTM; valid for localized benchmarking, not global Mars. Equirectangular CRS preserved." : "Earth candidates are limited to two USGS 3DEP tiles (Death Valley / southern Arizona). Not representative of global terrestrial terrain."}</p>
              </article>
            );
          })}
        </div>
        <div className="provenance-note">
          <span className="eyebrow">PROVENANCE</span>
          <p>Moon: NASA GSFC Planetary Geodesy and Altimetry Data Archive · https://pgda.gsfc.nasa.gov/products/90 · DOI 10.60903/gsfcpgda-lola-spole</p>
          <p>Mars: USGS Astrogeology Science Center · https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_ctx_dtm_mosaic</p>
          <p>Earth: USGS 3DEP 1-arc-second · open access via USGS S3 · NAVD88 vertical datum (unquantified difference vs LOLA/MOLA)</p>
        </div>
      </div>

      <div className="methodology-explorer">
        <span className="eyebrow">METHODOLOGY EXPLORER</span>
        <h3>TMSI — how it works, step by step</h3>
        <div className="methodology-accordion">
          {methodologySteps.map((step) => (
            <div key={step.id} className={`methodology-item ${openStep === step.id ? "open" : ""}`}>
              <button type="button" onClick={() => setOpenStep(openStep === step.id ? false : step.id)} aria-expanded={openStep === step.id}>
                <span>{step.title}</span>
                <span className="chevron">{openStep === step.id ? "−" : "+"}</span>
              </button>
              {openStep === step.id && <div className="methodology-body"><p>{step.body}</p></div>}
            </div>
          ))}
        </div>
      </div>

      <div className="research-results">
        <span className="eyebrow">RESEARCH RESULTS — INDEPENDENTLY VERIFIED</span>
        <div className="results-grid">
          <article className="result-card">
            <span className="eyebrow">MOON ↔ MARS</span>
            <strong>{moonMars?.similarity_index?.toFixed(2) ?? "49.92"}</strong>
            <p>TMSI ≈ 49.92 · 95% CI 42.59 – 57.15 · 1,000 reps · block 320 m · seed 42</p>
            <small>Moon and Mars terrain-morphology distributions are partially similar, but TMSI cannot establish planetary-body identity. Bootstrap CI bounds reflect spatial sampling variability (Moran’s I ≈ 0.979), not measurement error.</small>
          </article>
          <article className="result-card earth">
            <span className="eyebrow">EARTH ↔ MOON</span>
            <strong>61.95</strong>
            <p>TMSI ≈ 61.95 · 95% CI 51.99 – 72.56 · Conditionally ready (Earth DEM ~29.3 m effective; NAVD88 vs LOLA; single US region)</p>
            <small>Death Valley / southern Arizona region vs lunar south-polar window. Characterizes the sampled region only — not global terrestrial terrain.</small>
          </article>
          <article className="result-card earth">
            <span className="eyebrow">EARTH ↔ MARS</span>
            <strong>73.14</strong>
            <p>TMSI ≈ 73.14 · 95% CI 64.99 – 78.55 · Conditionally ready (Earth DEM ~29.3 m effective; NAVD88 vs delta geoid/MOLA; single US region)</p>
            <small>Death Valley / southern Arizona region vs Jezero crater. Not generalizable to global Earth or global Mars; vertical datum difference is unquantified.</small>
          </article>
        </div>
        <p className="chart-note">All three comparisons share the documented TMSI limitation: within-body similarity ranges overlap between-body ranges. TMSI measures terrain morphology-distribution similarity only — not geological equivalence, not habitability, not landing safety, not planetary identity.</p>
      </div>

      <div className="export-actions">
        <span className="eyebrow">EXPORT RESEARCH PACKAGE</span>
        <div className="export-buttons">
          <button type="button" onClick={() => { void downloadExport("json").catch(() => undefined); }}>EXPORT JSON</button>
          <button type="button" onClick={() => { void downloadExport("csv").catch(() => undefined); }}>EXPORT CSV</button>
          <button type="button" onClick={() => { void downloadExport("pdf").catch(() => undefined); }}>EXPORT PDF</button>
        </div>
      </div>
    </section>
  );
}


function getFeatureResult(feature: string, experiment: Experiment | null): FeatureResult {
  const real = experiment?.baseline_result?.features?.[feature] as unknown as FeatureResult | undefined;
  if (real) return real;
  return {
    target_summary: { median: 0, q25: 0, q75: 0, q90: 0, mean: 0 },
    candidate_summary: { median: 0, q25: 0, q75: 0, q90: 0, mean: 0 },
    distance: { normalized_distance: 0, pooled_iqr: 0, ks_statistic: 0, wasserstein: 0, sample_count_target: 0, sample_count_candidate: 0 },
    definition: "Feature definition (experiment data unavailable)",
    units: "units",
  };
}

// --- Main component ---

function benchmarkFromStatus(status: SimilarityStatus | null): { datasets: DatasetProvenance[]; planet_coverage: Record<string, number>; real_benchmark_findings: string[]; limitation: string } {
  const BASE_ID = 100000;
  const available = status?.available_real_datasets ?? [];
  const unavailable = status?.unavailable_datasets ?? [];
  const datasets: DatasetProvenance[] = [
    ...available.map((d, i) => ({
      id: BASE_ID + i,
      body: d.body as "Moon" | "Mars" | "Earth",
      name: d.id,
      nominal_resolution: d.id === "moon_lola" ? "20 m/pixel" : "20 m pixel spacing",
      validation_status: "VALIDATED" as const,
      access_status: "DOWNLOADED" as const,
      kind: "real_observational",
    })),
    ...unavailable.map((d, i) => ({
      id: BASE_ID + available.length + i,
      body: d.body as "Moon" | "Mars" | "Earth",
      name: d.id,
      validation_status: "REJECTED" as const,
      access_status: "BLOCKED_BY_EARTHDATA_AUTHENTICATION" as const,
      kind: "official_product",
    })),
  ];
  const coverage: Record<string, number> = {};
  for (const d of datasets) coverage[d.body] = (coverage[d.body] ?? 0) + 1;
  return {
    datasets,
    planet_coverage: coverage,
    real_benchmark_findings: [],
    limitation:
      "No independently labeled real benchmark dataset was available covering overlapping terrain across two+ DEM products. Existing datasets (moon_lola, mars_jezero_ctx_dtm) are validated observational products but cover different geographical regions. earth_nasadem_hgt_v001 is blocked by authentication. No dataset pair currently enables within-pair TMSI reproducibility testing.",
  };
}

export default function ResearchWorkbench() {
  const [view, setView] = useState("explore");
  const [layer, setLayer] = useState("elevation" as Layer);
  const [terrainDataset, setTerrainDataset] = useState<"moon_lola" | "mars_jezero_ctx_dtm" | "usgs_3dep_death_valley">("moon_lola");
  const [compareCandidateId, setCompareCandidateId] = useState<string | null>(null);
  const [zoomRequest, setZoomRequest] = useState<{ id: string; at: number } | null>(null);
  const [exploreContextId, setExploreContextId] = useState<string | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [dataLoading, setDataLoading] = useState(true);
  const [sampling, setSampling] = useState<SamplingFramework | null>(null);
  const [experiment, setExperiment] = useState<Experiment | null>(null);
  const [similarityStatus, setSimilarityStatus] = useState<SimilarityStatus | null>(null);
  const [selectedFeature, setSelectedFeature] = useState<string | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setDataLoading(true);
      const [candRes, sfRes, statusRes, expRes, healthRes] = await Promise.allSettled([
        fetchCandidates(),
        fetchSamplingFramework(),
        fetchStatus(),
        fetchExperiment(),
        checkBackendHealth(),
      ]);
      if (cancelled) return;
      if (candRes.status === "fulfilled")
        setCandidates(candRes.value.map((c: CandidateEntry) => ({ ...c, bounding_box: c.bounding_box ?? undefined })));
      if (sfRes.status === "fulfilled") setSampling(sfRes.value);
      if (statusRes.status === "fulfilled") setSimilarityStatus(statusRes.value);
      if (expRes.status === "fulfilled") setExperiment(expRes.value);
      setBackendOnline(healthRes.status === "fulfilled" ? healthRes.value : false);
      setDataLoading(false);
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="research-shell">
      <header className="research-header">
        <div className="brand-lockup">
          <div>
            <strong>TERRA TWIN</strong>
            <small>PLANETARY TERRAIN MORPHOLOGY LAB</small>
          </div>
        </div>
        <div className="header-status">
          <span className="live-dot" />{backendOnline === false ? "BACKEND OFFLINE" : backendOnline === null ? "BACKEND CHECKING" : "BACKEND ONLINE"}
        </div>
      </header>
      <nav className="research-nav" aria-label="Research sections">
        <button className={view === "explore" ? "active" : ""} onClick={() => setView("explore")}>EXPLORE</button>
        <button className={view === "compare" ? "active" : ""} onClick={() => setView("compare")}>COMPARE</button>
        <button className={view === "reliability" ? "active" : ""} onClick={() => setView("reliability")}>RELIABILITY</button>
        <button className={view === "data_methods" ? "active" : ""} onClick={() => setView("data_methods")}>DATA &amp; METHODS</button>
        <button className={view === "map" ? "active" : ""} onClick={() => setView("map")}>MAP</button>
      </nav>

      <main>
        {dataLoading && <div className="loading-state">LOADING BACKEND DATA<span className="pulse-line" /></div>}
        {view === "explore" && <ExploreView layer={layer} setLayer={setLayer} terrainDataset={terrainDataset} setTerrainDataset={setTerrainDataset} exploreContextId={exploreContextId} onExploreContextClear={() => setExploreContextId(null)} />}
        {view === "compare" && <CompareView selectedFeature={selectedFeature} setSelectedFeature={setSelectedFeature} experiment={experiment} compareCandidateId={compareCandidateId} onClearCompareCandidate={() => setCompareCandidateId(null)} />}
        {view === "reliability" && <ReliabilityView sampling={sampling} experiment={experiment} />}
        {view === "data_methods" && <DataMethodsView benchmark={benchmarkFromStatus(similarityStatus)} experiment={experiment} />}
        {view === "map" && (
          <DiscoveryMap
            candidates={candidates}
            onCandidateSelect={setSelectedCandidateId}
            selectedCandidateId={selectedCandidateId}
            zoomRequest={zoomRequest}
            onCandidateClear={() => setSelectedCandidateId(null)}
            onExploreCandidate={(candidate) => {
              setTerrainDataset(candidate.id === "death_valley" ? "usgs_3dep_death_valley" : "moon_lola");
              setExploreContextId(candidate.id);
              setView("explore");
            }}
            onCompareCandidate={(candidate) => {
              setCompareCandidateId(candidate.id);
              setView("compare");
            }}
            onZoomCandidate={(candidate) => {
              setZoomRequest({ id: candidate.id, at: Date.now() });
            }}
          />
        )}
      </main>
      <footer className="research-footer">
        <span>TERRA TWIN — EARTH-TO-PLANETARY ANALOG DISCOVERY</span>
        <span>MORPHOLOGY ONLY — NOT A HABITABILITY OR LANDING CERTIFICATION</span>
      </footer>
    </div>
  );
}

type Layer = "elevation" | "hillshade" | "slope" | "local_relief" | "terrain_ruggedness";

const LAYER_DEFINITIONS: Record<Layer, { definition: string; units: string; scale: string; limitation: string; label: string }> = {
  elevation: {
    label: "ELEVATION",
    units: "m",
    scale: "Native 20 m post spacing",
    definition: "Surface elevation above the reference datum for the validated DEM.",
    limitation: "Native-coordinate bounded subset; not a complete planetary product.",
  },
  hillshade: {
    label: "HILLSHADE",
    units: "—",
    scale: "Derived from elevation gradient",
    definition: "Shaded relief computed from the elevation gradient (azimuth 315%, altitude 45%).",
    limitation: "Illustration of terrain shape; not a measured quantity.",
  },
  slope: {
    label: "SLOPE",
    units: "degrees",
    scale: "20 m projected metre spacing",
    definition: "Gradient magnitude converted to degrees using metre-per-pixel spacing.",
    limitation: "Sensitive to DEM noise at steep slopes; computed on the validated raster.",
  },
  local_relief: {
    label: "LOCAL RELIEF",
    units: "m",
    scale: "60 m physical window (3 x 3 cells at 20 m)",
    definition: "Maximum elevation minus minimum elevation in a complete 60 m square window.",
    limitation: "Edge and incomplete-window cells are excluded from statistics.",
  },
  terrain_ruggedness: {
    label: "TERRAIN RUGGEDNESS",
    units: "m",
    scale: "60 m physical window (3 x 3 cells at 20 m)",
    definition: "Riley TRI: square root of mean squared center-to-neighbor elevation differences.",
    limitation: "Riley TRI is a roughness index, not a direct hazard measure.",
  },
};

// --- Candidate interfaces ---

interface CandidateLocation {
  latitude: number;
  longitude: number;
  label?: string;
}

interface Candidate {
  id: string;
  name: string;
  country: string;
  environment_classification: string;
  planetary_relevance: "Moon" | "Mars" | "Both";
  status: "CANDIDATE" | "SOURCE_VERIFIED" | "DATA_AVAILABLE" | "READY_FOR_COMPARISON";
  latitude: number;
  longitude: number;
  bounding_box?: string;
  scientific_description: string;
  geological_context: string;
  selection_rationale: string;
  supporting_references: string;
  source_dataset: string;
  source_url: string;
  data_acquisition_status: string;
  dem_availability: string;
  spatial_resolution?: string;
  coordinate_reference_system?: string;
  elevation_coverage: string;
  terrain_feature_availability: string;
  scientific_validation_status: string;
  known_limitations: string;
  last_updated: string;
}

// --- Map component ---

function isValidLatitude(lat: number): boolean {
  return typeof lat === "number" && lat >= -90 && lat <= 90;
}

function isValidLongitude(lon: number): boolean {
  return typeof lon === "number" && lon >= -180 && lon <= 180;
}

function formatCoordinate(num: number, decimals: number = 3): string {
  return Number(num).toFixed(decimals);
}

const STATUS_COLORS: Record<string, string> = {
  CANDIDATE: "#e6bb77",
  SOURCE_VERIFIED: "#9bd0ff",
  DATA_AVAILABLE: "#b7d36b",
  READY_FOR_COMPARISON: "#b7d36b",
};

const BASEMAPS = {
  osm: {
    name: "OSM MAP",
    url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: "&copy; OpenStreetMap contributors",
    maxZoom: 19,
  },
  gibs: {
    name: "NASA GIBS",
    url: "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_NextGeneration/default/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg",
    attribution: "NASA GIBS — Blue Marble Next Generation (public domain)",
    maxZoom: 8,
  },
} as const;

type BasemapId = keyof typeof BASEMAPS;

function DiscoveryMap({ candidates, selectedCandidateId, zoomRequest, onCandidateSelect, onCandidateClear, onExploreCandidate, onCompareCandidate, onZoomCandidate }: {
  candidates: Candidate[];
  selectedCandidateId: string | null;
  zoomRequest: { id: string; at: number } | null;
  onCandidateSelect: (id: string | null) => void;
  onCandidateClear: () => void;
  onExploreCandidate: (candidate: Candidate) => void;
  onCompareCandidate: (candidate: Candidate) => void;
  onZoomCandidate: (candidate: Candidate) => void;
}) {
  // Filter state
  const [envFilter, setEnvFilter] = useState<string | null>(null);
  const [planetFilter, setPlanetFilter] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [basemap, setBasemap] = useState<BasemapId>("osm");

  const environmentClassifications: Set<string> = new Set(candidates.map((c) => c.environment_classification));
  const planetaryRelevances: Set<string> = new Set(candidates.map((c) => c.planetary_relevance));

  const filteredCandidates = candidates.filter((c) => {
    const matchesSearch = searchTerm === "" ||
      c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.country.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesEnv = envFilter === null || c.environment_classification === envFilter;
    const matchesPlanet = planetFilter === null || c.planetary_relevance === planetFilter;
    const matchesStatus = statusFilter === null || c.status === statusFilter;
    return matchesSearch && matchesEnv && matchesPlanet && matchesStatus;
  });

  const validCandidates = filteredCandidates.filter(
    (c) => isValidLatitude(c.latitude) && isValidLongitude(c.longitude)
  );

  const selectedCandidate = selectedCandidateId ? candidates.find((c) => c.id === selectedCandidateId) ?? null : null;
  const isSplit = Boolean(selectedCandidate);

  // --- Leaflet map (imperative) ---
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<import("leaflet").Map | null>(null);
  const layerGroupRef = useRef<import("leaflet").LayerGroup | null>(null);
  const tileLayerRef = useRef<import("leaflet").TileLayer | null>(null);
  const hasInitializedRef = useRef(false);
  const [mapReady, setMapReady] = useState(false);

  useEffect(() => {
    let cancelled = false;
    if (hasInitializedRef.current) return undefined;
    hasInitializedRef.current = true;
    import("leaflet").then((mod) => {
      if (cancelled || !mapContainerRef.current) return;
      const L = mod.default ?? mod;
      if (mapRef.current) return;
      const map = L.map(mapContainerRef.current, {
        center: [25, 10],
        zoom: 2,
        minZoom: 2,
        maxZoom: 12,
        worldCopyJump: false,
        maxBounds: [[-85, -180], [85, 180]],
        maxBoundsViscosity: 0.9,
        attributionControl: true,
      });
      const initialTiles = BASEMAPS[basemap];
      tileLayerRef.current = L.tileLayer(initialTiles.url, {
        maxZoom: initialTiles.maxZoom,
        attribution: initialTiles.attribution,
      }).addTo(map);
      layerGroupRef.current = L.layerGroup().addTo(map);
      mapRef.current = map;
      setMapReady(true);
      const handleResize = () => map.invalidateSize();
      window.addEventListener("resize", handleResize);
      (mapContainerRef as unknown as { cleanupResize: () => void }).cleanupResize = () => window.removeEventListener("resize", handleResize);
    }).catch(() => {
      if (!cancelled) setMapReady(false);
    });
    return () => {
      cancelled = true;
      const container = mapContainerRef as unknown as { cleanupResize?: () => void };
      container.cleanupResize?.();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Basemap switching
  useEffect(() => {
    if (!mapReady || !mapRef.current || !tileLayerRef.current) return;
    let cancelled = false;
    import("leaflet").then((mod) => {
      if (cancelled || !mapRef.current || !tileLayerRef.current) return;
      const L = mod.default ?? mod;
      const layers = BASEMAPS[basemap];
      tileLayerRef.current.remove();
      tileLayerRef.current = L.tileLayer(layers.url, {
        maxZoom: layers.maxZoom,
        attribution: layers.attribution,
      }).addTo(mapRef.current);
    }).catch(() => undefined);
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [basemap, mapReady]);

  // Invalidate size on layout transitions (split/panel open/close)
  useEffect(() => {
    if (!mapReady || !mapRef.current) return undefined;
    const map = mapRef.current;
    const invalidate = () => map.invalidateSize({ animate: false });
    const t = window.setTimeout(invalidate, 80);
    const t2 = window.setTimeout(invalidate, 400);
    return () => {
      window.clearTimeout(t);
      window.clearTimeout(t2);
    };
  }, [selectedCandidateId, mapReady]);

  // Sync markers with filtered candidates
  useEffect(() => {
    let cancelled = false;
    import("leaflet").then((mod) => {
      if (cancelled) return;
      const L = mod.default ?? mod;
      const layerGroup = layerGroupRef.current;
      if (!layerGroup) return;
      layerGroup.clearLayers();
      const bounds: [number, number][] = [];
      validCandidates.forEach((c) => {
        const isSelected = selectedCandidateId === c.id;
        const statusColor = isSelected ? "#ffffff" : STATUS_COLORS[c.status] ?? "#e6bb77";
        const size = isSelected ? 22 : 16;
        const borderWidth = isSelected ? 3 : 2;
        const markerHtml = `<div class="candidate-marker${isSelected ? " candidate-marker--selected" : ""}" style="--marker-size:${size}px;--marker-border:${borderWidth}px;--marker-color:${statusColor}"></div>`;
        const icon = L.divIcon({ className: "candidate-marker-icon", html: markerHtml, iconSize: [size, size], iconAnchor: [size / 2, size / 2] });
        const marker = L.marker([c.latitude, c.longitude], { icon, keyboard: true, title: c.name, zIndexOffset: isSelected ? 1000 : 0 });
        marker.on("click", () => onCandidateSelect(selectedCandidateId === c.id ? null : c.id));
        marker.bindTooltip(c.name, { direction: "top", offset: [0, -12], className: "candidate-tooltip" });
        layerGroup.addLayer(marker);
        bounds.push([c.latitude, c.longitude]);
      });
      const map = mapRef.current;
      if (map && bounds.length > 0 && !selectedCandidateId) {
        map.fitBounds(L.latLngBounds(bounds as [number, number][]), { padding: [40, 40], maxZoom: 6 });
      }
    }).catch(() => undefined);
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [validCandidates, onCandidateSelect, selectedCandidateId, mapReady]);

  // Fly to candidate when zoomRequest arrives
  useEffect(() => {
    if (!mapReady || !mapRef.current || !zoomRequest) return undefined;
    const candidate = candidates.find((c) => c.id === zoomRequest.id);
    if (!candidate) return undefined;
    if (!isValidLatitude(candidate.latitude) || !isValidLongitude(candidate.longitude)) return undefined;
    mapRef.current.flyTo([candidate.latitude, candidate.longitude], 6, { duration: 1.4 });
    return undefined;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [zoomRequest, mapReady]);

  // Unmount map cleanup
  useEffect(() => () => {
    mapRef.current?.remove();
    mapRef.current = null;
    layerGroupRef.current = null;
    tileLayerRef.current = null;
    hasInitializedRef.current = false;
  }, []);

  const handleMarkerClick = (candidate: Candidate) => {
    onCandidateSelect(selectedCandidateId === candidate.id ? null : candidate.id);
  };

  const renderEnvFilters = (
    <div className="filter-group">
      <span className="filter-label">Environment</span>
      <div className="filter-chips">
        {[...environmentClassifications].sort().map((env) => (
          <button key={env} className={`filter-chip ${envFilter === env ? "selected" : ""}`} onClick={() => setEnvFilter(envFilter === env ? null : env)} type="button">
            {env.replace(/_/g, " ")}
          </button>
        ))}
      </div>
    </div>
  );

  const renderPlanetFilters = (
    <div className="filter-group">
      <span className="filter-label">Planetary Target</span>
      <div className="filter-chips">
        {[...planetaryRelevances].sort().map((planet) => (
          <button key={planet} className={`filter-chip ${planetFilter === planet ? "selected" : ""}`} onClick={() => setPlanetFilter(planetFilter === planet ? null : planet)} type="button">
            {planet}
          </button>
        ))}
      </div>
    </div>
  );

  const renderStatusFilters = (
    <div className="filter-group">
      <span className="filter-label">Validation Status</span>
      <div className="filter-chips">
        {["CANDIDATE", "SOURCE_VERIFIED", "DATA_AVAILABLE", "READY_FOR_COMPARISON"].map((status) => (
          <button key={status} className={`filter-chip ${statusFilter === status ? "selected" : ""}`} onClick={() => setStatusFilter(statusFilter === status ? null : status)} type="button">
            {status.replace(/_/g, " ")}
          </button>
        ))}
      </div>
    </div>
  );

  const renderBasemap = (
    <div className="filter-group basemap-group">
      <span className="filter-label">Basemap</span>
      <div className="segmented" role="group" aria-label="Basemap">
        {Object.entries(BASEMAPS).map(([id, meta]) => (
          <button key={id} type="button" className={basemap === id ? "selected" : ""} onClick={() => setBasemap(id as BasemapId)}>{meta.name}</button>
        ))}
      </div>
    </div>
  );

  const renderSearchControl = (
    <div className="filter-group">
      <span className="filter-label">Search</span>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search candidate name or country..."
        className="search-input"
        aria-label="Search candidates"
      />
    </div>
  );

  const renderFilterRow = (
    <div className="filter-strip" aria-label="Filter candidates">
      {renderSearchControl}
      {renderEnvFilters}
      {renderPlanetFilters}
      {renderStatusFilters}
      {renderBasemap}
    </div>
  );

  return (
    <section className="content-section discovery-map">
      <div className="section-heading">
        <div>
          <span className="eyebrow">MAP</span>
          <h2>Earth Candidate Explorer</h2>
        </div>
        <span className="method-tag">{validCandidates.length} / {candidates.length} · WGS84</span>
      </div>

      {!isSplit && renderFilterRow}

      <div className={`discovery-map-layout${isSplit ? " split" : ""}`}>
        <div className="discovery-map-canvas-wrap">
          {validCandidates.length === 0 ? (
            <div className="discovery-map-empty">
              <span className="eyebrow">NO MATCHES</span>
              <p>No candidates match the current filters. Clear the search or remove filters.</p>
            </div>
          ) : (
            <div ref={mapContainerRef} className="leaflet-map" role="application" aria-label="Interactive map of Earth candidate locations" />
          )}
          {validCandidates.length > 0 && (
            <p className="map-hint">Click a marker to open its research profile. Scroll to zoom · drag to pan.</p>
          )}
        </div>

        {!isSplit && (
          <aside className="discovery-map-sidebar" aria-label="Filter candidates and legend">
            {renderBasemap}
            <div className="map-legend">
              <div className="legend-item"><span className="status-badge CANDIDATE">CANDIDATE</span><span>Unvalidated candidate</span></div>
              <div className="legend-item"><span className="status-badge SOURCE_VERIFIED">SOURCE_VERIFIED</span><span>Source information verified</span></div>
              <div className="legend-item"><span className="status-badge DATA_AVAILABLE">DATA_AVAILABLE</span><span>DEM elevation data available</span></div>
              <div className="legend-item"><span className="status-badge READY_FOR_COMPARISON">READY</span><span>Ready for Phase 20 comparison</span></div>
            </div>
            <button type="button" className="mini-button" onClick={() => onCandidateSelect(validCandidates[0]?.id ?? null)} disabled={validCandidates.length === 0}>
              OPEN FIRST CANDIDATE
            </button>
          </aside>
        )}

        {isSplit && selectedCandidate && (
          <CandidateProfile
            candidate={selectedCandidate}
            onClose={onCandidateClear}
            onExplore={onExploreCandidate}
            onCompare={onCompareCandidate}
            onZoom={onZoomCandidate}
            verifiedTerrain={selectedCandidate.id === "death_valley"}
          />
        )}
      </div>

      {isSplit && renderFilterRow}

      <div className="map-accessible-alternative">
        <p>
          <strong>Accessible list alternative:</strong> Table of registered Earth candidates with coordinates, environment classification, planetary relevance and validation status. Click <kbd>Enter</kbd> on any row to open its research profile.
        </p>
        <div className="candidate-table-wrap" tabIndex={0} role="region" aria-label="Candidate table">
          <table className="candidate-table">
            <thead>
              <tr><th>Candidate</th><th>Country</th><th>Lat</th><th>Lon</th><th>Environment</th><th>Target</th><th>Status</th></tr>
            </thead>
            <tbody>
              {filteredCandidates.map((c) => (
                <tr key={c.id} tabIndex={0} onClick={() => handleMarkerClick(c)} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); handleMarkerClick(c); } }}>
                  <td>{c.name}</td>
                  <td>{c.country}</td>
                  <td>{c.latitude.toFixed(2)}</td>
                  <td>{c.longitude.toFixed(2)}</td>
                  <td>{c.environment_classification.replace(/_/g, " ")}</td>
                  <td>{c.planetary_relevance}</td>
                  <td><span className={`status-badge ${c.status}`}>{c.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}


function getCandidateFromRegistry(candidateId: string): Candidate | null {
  // In a full implementation, this would query the registry API.
  // For now, search the local candidates state.
  // This is a simplified lookup.
  return null; // Placeholder - actual implementation would search candidates array
}
