"use client";

import { useEffect, useState } from "react";
import { apiUrl } from "@/lib/api";

type SimilarityStatus = {
  engine: string;
  production_comparisons_enabled: boolean;
  validated_comparisons: string[];
  available_real_datasets: Array<{ id: string; body: string; validated: boolean }>;
  unavailable_datasets: Array<{ id: string; body: string; reason: string }>;
};



export default function SimilarityReadiness() {
  const [status, setStatus] = useState<SimilarityStatus | null>(null);

  useEffect(() => {
    fetch(`${apiUrl}/api/similarity/status`, { cache: "no-store" })
      .then((response) => (response.ok ? response.json() as Promise<SimilarityStatus> : Promise.reject()))
      .then(setStatus)
      .catch(() => setStatus(null));
  }, []);

  const available = status?.available_real_datasets ?? [];
  const unavailable = status?.unavailable_datasets ?? [];

  return (
    <section className="engine-panel" aria-label="Similarity engine readiness">
      <div className="engine-panel-heading">
        <p className="eyebrow">MORPHOLOGY ENGINE</p>
        <span className="engine-state">{status?.validated_comparisons?.length ? "MARS / MOON READY" : "VALIDATION GATE ACTIVE"}</span>
      </div>
      <div className="engine-panel-content">
        <div>
          <h2>Terrain Morphology Similarity Index</h2>
          <p>Feature-level comparisons will use slope, local relief, and terrain ruggedness at defensible physical scales.</p>
        </div>
        <div className="dataset-readiness">
          <div><span className="readiness-label">VERIFIED INPUTS</span><strong>{available.length ? available.map((dataset) => dataset.body).join(" / ") : "Checking backend"}</strong></div>
          <div><span className="readiness-label">PENDING INPUTS</span><strong>{unavailable.map((dataset) => dataset.body).join(" / ") || "None"}</strong></div>
        </div>
      </div>
      <p className="engine-note">No production ranking is displayed until Earth and lunar terrain datasets pass the same provenance, CRS, resolution, and quality checks as Mars.</p>
    </section>
  );
}