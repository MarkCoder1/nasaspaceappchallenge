const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type CandidateEntry = {
  id: string;
  name: string;
  country: string;
  environment_classification: string;
  planetary_relevance: "Moon" | "Mars" | "Both";
  status: "CANDIDATE" | "SOURCE_VERIFIED" | "DATA_AVAILABLE" | "READY_FOR_COMPARISON";
  latitude: number;
  longitude: number;
  bounding_box?: string | null;
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
};

export async function fetchCandidates(): Promise<CandidateEntry[]> {
  const response = await fetch(`${apiUrl}/api/candidates`, { cache: "no-store" });
  if (!response.ok) throw new Error(`candidates ${response.status}`);
  const payload = (await response.json()) as { candidates: CandidateEntry[] };
  return payload.candidates ?? [];
}

export type HealthResponse = { status: string; service: string };

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${apiUrl}/api/health`, { cache: "no-store" });
    if (!response.ok) return false;
    const payload = (await response.json()) as HealthResponse;
    return payload.status === "ok";
  } catch {
    return false;
  }
}

export type SimilarityStatus = {
  engine: string;
  production_comparisons_enabled: boolean;
  validated_comparisons: string[];
  available_real_datasets: Array<{ id: string; body: string; state: string; path: string; validated: boolean }>;
  unavailable_datasets: Array<{ id: string; body: string; reason: string }>;
  comparison_capabilities: Record<string, { enabled: boolean; reason: string }>;
};

export type Distance = {
  wasserstein: number;
  ks_statistic: number;
  ks_pvalue: number;
  pooled_iqr: number;
  normalized_distance: number;
  sample_count_target: number;
  sample_count_candidate: number;
};

export type FeatureSummary = {
  count: number;
  mean: number;
  median: number;
  std: number;
  q25: number;
  q75: number;
  q90: number;
};

export type FeatureResult = {
  units: string;
  neighborhood_m: number | null;
  definition: string;
  target_summary: FeatureSummary;
  candidate_summary: FeatureSummary;
  distance: Distance;
};

export type BaselineResult = {
  target: { id: string; body: string; resolution_m: number[] };
  candidate: { id: string; body: string; resolution_m: number[] };
  similarity_index: number;
  confidence: string;
  combined_distance: number;
  weights: Record<string, number>;
  features: Record<string, FeatureResult>;
  strongest_matches: string[];
  largest_differences: string[];
  limitations: string[];
  data_sources: Array<Record<string, unknown>>;
};

export type BootstrapResult = {
  method: string;
  block_size_m: number;
  repetitions: number;
  seed: number;
  tmsi_mean: number;
  tmsi_median: number;
  tmsi_lower_95: number;
  tmsi_upper_95: number;
  feature_distance_means: Record<string, number>;
  interpretation: string;
};

export type SensitivityBlock = {
  tmsi_mean: number;
  tmsi_median: number;
  tmsi_lower_95: number;
  tmsi_upper_95: number;
  feature_distance_means: Record<string, number>;
  interpretation: string;
};

export type SpatialDiag = {
  morans_i: number;
  semivariogram: Array<{ lag_cells: number; lag_m: number; pair_count: number; semivariance: number | null }>;
};

export type Experiment = {
  baseline_result: BaselineResult;
  primary_bootstrap_320m_1000: BootstrapResult;
  bootstrap_convergence: { results: Record<string, BootstrapResult> };
  seed_sensitivity: Record<string, BootstrapResult>;
  block_size_sensitivity: { results: Record<string, SensitivityBlock> };
  feature_ablation: Record<string, { score: { similarity_index: number; combined_distance: number; weights: Record<string, number> }; bootstrap: BootstrapResult }>;
  weight_sensitivity: Record<string, { score: { similarity_index: number; combined_distance: number; weights: Record<string, number> }; bootstrap: BootstrapResult }>;
  spatial_diagnostics: {
    slope: SpatialDiag;
    local_relief: SpatialDiag;
    terrain_ruggedness: SpatialDiag;
    moon: { slope: SpatialDiag; local_relief: SpatialDiag; terrain_ruggedness: SpatialDiag };
  };
  provenance: {
    datasets: Array<{
      id: string;
      body: string;
      state: string;
      manifest: Record<string, string | number>;
      processed_sha256: string;
      feature_metadata: Record<string, unknown>;
    }>;
    software_versions: Record<string, string>;
    executed_at_utc: string;
    feature_definitions: Record<string, string>;
    feature_parameters: Record<string, number>;
    normalization: string;
    scoring: { formula: string; weights: Record<string, number> };
  };
  interpretation: string[];
};

export async function fetchStatus(): Promise<SimilarityStatus> {
  const response = await fetch(`${apiUrl}/api/similarity/status`, { cache: "no-store" });
  if (!response.ok) throw new Error(`status ${response.status}`);
  return response.json();
}

export async function fetchExperiment(): Promise<Experiment> {
  const response = await fetch(`${apiUrl}/api/similarity/results`, { cache: "no-store" });
  if (!response.ok) throw new Error(`status ${response.status}`);
  const payload = await response.json();
  return payload.experiment;
}

export function rasterUrl(datasetId: string, layer = "elevation"): string {
  return `${apiUrl}/api/similarity/raster/${encodeURIComponent(datasetId)}?layer=${encodeURIComponent(layer)}`;
}

export type ExportFormat = "json" | "csv" | "pdf";

export function exportUrl(format: ExportFormat): string {
  return `${apiUrl}/api/similarity/export/${format}`;
}

export async function downloadExport(format: ExportFormat): Promise<void> {
  const response = await fetch(exportUrl(format), { cache: "no-store" });
  if (!response.ok) throw new Error(`export ${format} failed ${response.status}`);
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const fileName =
    format === "json"
      ? "terratwin_research_package.json"
      : format === "csv"
        ? "terratwin_export.csv"
        : "terratwin_research_report.pdf";
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = fileName;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

// ---------- Sampling framework (Phase 11 real experiment data) ----------

export type OverlapStatus = "identical" | "high" | "partial" | "none" | "unknown";

export type SamplingFrameworkComparison = {
  label: string;
  body_a: string;
  body_b: string;
  source_id_a: string;
  source_id_b: string;
  extent_km: number;
  n_cells: number;
  window_a_offset: [number, number];
  window_b_offset: [number, number];
  overlap_fraction: number;
  overlap_status: OverlapStatus;
  similarity_index: number;
  confidence: string;
  combined_distance: number;
  feature_distances: Record<string, number>;
  statistical_uncertainty: Record<string, unknown> | null;
  mars_valid_percent: number;
  moon_valid_percent: number;
};

export type SamplingFrameworkSummary = {
  within_body_mars: {
    count: number;
    tmsi_min: number;
    tmsi_max: number;
    tmsi_mean: number;
  };
  within_body_moon: {
    count: number;
    tmsi_min: number;
    tmsi_max: number;
    tmsi_mean: number;
  };
  between_body: {
    count: number;
    tmsi_min: number;
    tmsi_max: number;
    tmsi_mean: number;
  };
};

export type SamplingFramework = {
  experiment: string;
  cell_m: number;
  n_cells: number;
  extent_km: number;
  weights: Record<string, number>;
  mars_window_count: number;
  moon_window_count: number;
  mars_windows: Array<{ label: string; offset: [number, number] }>;
  moon_windows: Array<{ label: string; offset: [number, number] }>;
  within_body: {
    mars: SamplingFrameworkComparison[];
    moon: SamplingFrameworkComparison[];
  };
  between_body: SamplingFrameworkComparison[];
  overlap_bias: SamplingFrameworkComparison[];
  summary: SamplingFrameworkSummary;
};

export async function fetchSamplingFramework(): Promise<SamplingFramework> {
  const response = await fetch(`${apiUrl}/api/similarity/sampling-framework`, {
    cache: "no-store",
  });
  if (!response.ok) throw new Error(`sampling framework ${response.status}`);
  return response.json();
}

const format = (value: number | undefined, digits = 2): string =>
  value === undefined ? "--" : value.toFixed(digits);

export { format };

