"use client";

import CandidateMiniMap from "@/components/CandidateMiniMap";
import CandidateTerrainPreview from "@/components/CandidateTerrainPreview";

export interface ProfileCandidate {
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

export interface CandidateProfileProps {
  candidate: ProfileCandidate;
  onClose: () => void;
  onExplore: (candidate: ProfileCandidate) => void;
  onCompare: (candidate: ProfileCandidate) => void;
  onZoom: (candidate: ProfileCandidate) => void;
  verifiedTerrain: boolean;
}

const VERIFIED_TERRAIN_IDS = new Set(["death_valley"]);

export default function CandidateProfile({ candidate, onClose, onExplore, onCompare, onZoom, verifiedTerrain }: CandidateProfileProps) {
  const hasValidGeometry = Number.isFinite(candidate.latitude) && Number.isFinite(candidate.longitude) &&
    candidate.latitude >= -90 && candidate.latitude <= 90 && candidate.longitude >= -180 && candidate.longitude <= 180;
  const terrainAvailable = verifiedTerrain || VERIFIED_TERRAIN_IDS.has(candidate.id);

  return (
    <aside className="candidate-profile" aria-label={`Candidate research profile: ${candidate.name}`} role="complementary">
      <div className="candidate-profile-scroll">
        {/* Identity */}
        <header className="candidate-profile-header">
          <div className="candidate-profile-badges">
            <span className={`status-badge ${candidate.status}`}>{candidate.status}</span>
            <span className="planetary-tag">{candidate.planetary_relevance}</span>
          </div>
          <button type="button" className="close-btn" onClick={onClose} aria-label="Close candidate profile">✕</button>
          <h2>{candidate.name}</h2>
          <p className="candidate-profile-sub">{candidate.country}</p>
        </header>

        {/* Visual exploration */}
        <section className="candidate-profile-section" aria-label="Visual exploration">
          <span className="eyebrow">VISUAL EXPLORATION</span>
          <CandidateTerrainPreview candidateId={candidate.id} layer="elevation" skipFetch={!terrainAvailable} />
          <CandidateMiniMap latitude={candidate.latitude} longitude={candidate.longitude} name={candidate.name} />
          {!terrainAvailable && (
            <p className="integrity-note">
              <strong>Terrain preview:</strong> no verified local raster for this candidate — terrain
              preview intentionally not generated. Coordinate readouts are from the candidate registry
              (<code>science/datasets/registry.json</code>).
            </p>
          )}
        </section>

        {/* Actions */}
        <section className="candidate-profile-section" aria-label="Candidate actions">
          <span className="eyebrow">ACTIONS</span>
          <div className="candidate-actions">
            <button type="button" className="action-btn action-btn--primary" onClick={() => onExplore(candidate)}>
              EXPLORE THIS LOCATION
              <small>{terrainAvailable ? "Terrain viewer with local USGS 3DEP raster" : "Unavailable — no verified raster locally"}</small>
            </button>
            <button type="button" className="action-btn action-btn--secondary" onClick={() => onCompare(candidate)}>
              COMPARE THIS CANDIDATE
              <small>Earth–Moon/Mars comparisons not available for this candidate</small>
            </button>
            <button type="button" className="action-btn action-btn--ghost" onClick={() => onZoom(candidate)}>
              ZOOM TO LOCATION
              <small>{candidate.latitude.toFixed(2)}°, {candidate.longitude.toFixed(2)}°</small>
            </button>
          </div>
        </section>

        {/* Scientific information */}
        <section className="candidate-profile-section" aria-label="Scientific readiness">
          <span className="eyebrow">SCIENTIFIC READINESS</span>
          <dl className="candidate-readouts">
            <div className="candidate-readout"><dt>RELEVANCE</dt><dd>{candidate.planetary_relevance}</dd></div>
            <div className="candidate-readout"><dt>ENVIRONMENT</dt><dd>{candidate.environment_classification.replace(/_/g, " ")}</dd></div>
            <div className="candidate-readout"><dt>DEM AVAILABILITY</dt><dd className={candidate.dem_availability === "known" ? "ok" : "blocked"}>{candidate.dem_availability}</dd></div>
            <div className="candidate-readout"><dt>ACQUISITION</dt><dd>{candidate.data_acquisition_status}</dd></div>
            <div className="candidate-readout"><dt>RESOLUTION</dt><dd>{candidate.spatial_resolution ?? "unknown"}</dd></div>
            <div className="candidate-readout"><dt>CRS</dt><dd>{candidate.coordinate_reference_system ?? "—"}</dd></div>
            <div className="candidate-readout"><dt>COVERAGE</dt><dd>{candidate.elevation_coverage}</dd></div>
            <div className="candidate-readout"><dt>FEATURES</dt><dd>{candidate.terrain_feature_availability}</dd></div>
            <div className="candidate-readout"><dt>VALIDATION</dt><dd>{candidate.scientific_validation_status}</dd></div>
            <div className="candidate-readout"><dt>LAST UPDATED</dt><dd>{candidate.last_updated}</dd></div>
          </dl>
        </section>

        <section className="candidate-profile-section" aria-label="Scientific description">
          <span className="eyebrow">RATIONALE &amp; CONTEXT</span>
          <p className="candidate-description">{candidate.scientific_description}</p>
          <p className="candidate-description"><strong>Geological context:</strong> {candidate.geological_context}</p>
          <p className="candidate-description"><strong>Selection rationale:</strong> {candidate.selection_rationale}</p>
        </section>

        <section className="candidate-profile-section" aria-label="Provenance">
          <span className="eyebrow">PROVENANCE &amp; SOURCE</span>
          <dl className="candidate-readouts">
            <div className="candidate-readout"><dt>SOURCE DATASET</dt><dd>{candidate.source_dataset}</dd></div>
          </dl>
          <a className="candidate-source-link" href={candidate.source_url} target="_blank" rel="noopener noreferrer">{candidate.source_url} ↗</a>
          <p className="chart-note">References: {candidate.supporting_references}</p>
        </section>

        <section className="candidate-profile-section candidate-profile-limitations" aria-label="Known limitations">
          <span className="eyebrow">KNOWN LIMITATIONS</span>
          <p className="candidate-limitation">{candidate.known_limitations}</p>
          <p className="integrity-note">
            <strong>Scientific integrity:</strong> candidate selection does not establish terrain
            similarity. No Earth–Moon/Mars quantitative comparison has been computed for this candidate.
          </p>
          {!hasValidGeometry && (
            <p className="integrity-note"><strong>Warning:</strong> invalid WGS84 coordinates — geographic selection is unreliable.</p>
          )}
        </section>
      </div>
    </aside>
  );
}
