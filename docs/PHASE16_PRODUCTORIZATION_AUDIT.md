# Phase 16: Productization Audit

## Frontend Inventory

### Routes and Pages
| Route | Component | Status |
|-------|-----------|--------|
| `/` (root) | `ResearchWorkbench` (via `Home`) | Active |
| `/explorer` | `ResearchWorkbench` view "explorer" | Active |
| `/features` | `ResearchWorkbench` view "features" | Active |
| `/uncertainty` | `ResearchWorkbench` view "uncertainty" | Active |
| `/provenance` | `ResearchWorkbench` view "provenance" | Active |
| `/sampling` | `ResearchWorkbench` view "sampling" | Active |
| `/benchmarking` | `ResearchWorkbench` view "benchmarking" | Active |

**Default route**: `/` → renders `ResearchWorkbench` as `Home`

**Navigation** (research-nav, always present at bottom):
1. EXPLORER (01 / EXPLORER) — Terrain viewer
2. FEATURE LAB (02 / FEATURE LAB) — Feature laboratory
3. UNCERTAINTY (03 / UNCERTAINTY) — Uncertainty laboratory
4. PROVENANCE (04 / PROVENANCE) — Research record
5. SAMPLING (05 / SAMPLING) — Sampling framework
6. DEM BENCHMARKING (06 / DEM BENCHMARKING) — Independent dataset comparison

### Implemented Features

| Feature | View(s) | Status | Scientific Workflow Support |
|---------|---------|--------|---------------------------|
| Terrain viewer (elevation/hillshade/slope/local_relief/terrain_ruggedness) | explorer | ✅ Fully implemented | ✅ Yes — core terrain exploration |
| TMSI baseline display (49.9229) | features, uncertainty | ✅ Implemented | ✅ Yes — central scientific result |
| Feature-level comparison chart (3 terrain signals) | features | ✅ Implemented | ✅ Yes — slope, local relief, TRI |
| Histogram distributions (within/Mars vs between/Moon) | uncertainty | ✅ Implemented | ✅ Yes — overlap diagnostics |
| Bootstrap mean + 95% CI | uncertainty | ✅ Implemented | ✅ Yes — statistical robustness |
| Moran's I spatial autocorrelation | uncertainty | ✅ Implemented | ✅ Yes — spatial dependence |
| Extent sensitivity (23.71 @ 5.12 km → 49.92 @ 10.24 km) | uncertainty | ✅ Implemented | ✅ Yes — documented limitation |
| Seed sensitivity (~0.38 TMSI range) | uncertainty | ✅ Implemented | ✅ Yes — window location dependence |
| Feature ablation TMSI range (49.146–50.388) | uncertainty | ✅ Implemented | ✅ Yes — algorithm config variation |
| Weight sensitivity TMSI range (49.727–50.039) | uncertainty | ✅ Implemented | ✅ Yes — dataset weighting |
| Dataset provenance (moon_lola, mars_jezero, earth_nasadem) | provenance | ✅ Implemented | ✅ Yes — dataset status & blocking |
| Earth data BLOCKED status (HTTP 401) | explorer, provenance | ✅ Implemented | ✅ Yes — explicitly documented |
| Independent DEM benchmark BLOCKED note | provenance, benchmarking | ✅ Implemented | ✅ Yes — no overlapping-terrain pair |
| JSON / CSV / PDF export | global (footer) | ✅ Implemented | ✅ Yes — authentic results only |
| Sampling framework display (Phase 11 real experiment data) | sampling | ✅ Implemented | ✅ Yes — real experiment data |
| DEM benchmarking view (Phase 13 real experiment data) | benchmarking | ✅ Implemented | ✅ Yes — real experiment data |
| Interpretation safeguards (TMSI does NOT establish planetary identity) | uncertainty | ✅ Implemented | ✅ Yes — explicit scientific boundary |
| Combined distance + strongest matches | explorer | ✅ Implemented | ✅ Yes — comparison results |
| Ranking indicator (DISABLED) | explorer | ✅ Implemented (but marked) | ⚠️ Marked as disabled |
| Phase 08 / Phase 11 / Phase 13 labels | multiple views | ⚠️ Present | ⚠️ Productization target |
| Development phase references | multiple views | ⚠️ Present | ⚠️ Productization target |
| Debug indicators / internal metric names | multiple views | ⚠️ Present | ⚠️ Productization target |
| Ranking "DISABLED" badge | explorer | ⚠️ Present | ⚠️ Productization target |
| Earth pending appearing in multiple places | explorer, provenance | ⚠️ Present | ⚠️ Productization target |
| Raw SHA-256 hashes in UI | provenance | ⚠️ Present | ⚠️ Productization target |
| Raster image URLs with localhost:8000 | explorer (TerrainViewer) | ⚠️ Present | ⚠️ Critical — production URL issue |
| CORS / production API config | global | ⚠️ Present | ⚠️ Critical — must be fixed |

### Partially Implemented / Non-Functional Features

| Feature | View | Issue |
|---------|------|-------|
| Ranking control | explorer | Marked "DISABLED" — no interactive ranking functionality |
| PDF export | global | May have completeness issues — verify |
| CSV export | global | May have completeness issues — verify |
| JSON export | global | May have completeness issues — verify |
| Ranking "strongest matches" display | explorer | Displayed but ranking disabled |
| Earth comparison functionality | explorer | Disabled — BLOCKED by HTTP 401 |
| Raster image rendering at production URL | explorer | Uses localhost:8000 URLs — critical for deployment |

### API Connections
| Endpoint | Purpose | Status |
|----------|---------|--------|
| `GET /api/health` | Backend health check | ✅ Working |
| `GET /api/similarity/status` | Similarity engine readiness | ✅ Working |
| `GET /api/similarity/results` | Experiment data (baseline, bootstrap, features) | ✅ Working |
| `GET /api/similarity/raster/${datasetId}` | Raster image tile URL | ⚠️ localhost:8000 — production issue |
| `GET /api/similarity/export/${format}` | JSON/CSV/PDF export | ✅ Working (client download) |
| `POST /api/similarity/sampling-framework` | Sampling framework data | ✅ Working |

### Charts and Visualizations
| Chart | View | Data Source |
|-------|------|-------------|
| TMSI distribution (within Mars, within Moon, between Mars↔Moon) | uncertainty | `sampling.within_body.mars`, `sampling.within_body.moon`, `sampling.between_body` |
| Bootstrap distribution (representative) | uncertainty | `convergence` entries |
| Semivariogram (slope) | uncertainty | `spatial.slope.semivariogram` |
| Feature comparison bars (Mars/Moon) | features | `baseline.features[].target_summary`, `candidate_summary` |
| Feature detail histogram | features | Synthetic-free histogram from summary quartiles |
| Histogram bars (feature distribution) | features, uncertainty | Computed from quartile-based synthetic samples |
| Interval panel (95% CI) | uncertainty | `uncertainty.tmsi_lower_95`, `uncertainty.tmsi_upper_95` |
| Convergence readout | uncertainty | `convergence` entries with repetition counts |
| Seed sensitivity readout | uncertainty | `seedSens` entries with seed number + TMSI mean |
| Block size sensitivity readout | uncertainty | `bss` entries (160 M, 320 M, 640 M) |
| Moran's I readout | uncertainty | `spatial.slope.morans_i`, `spatial.moon.morans_i` |
| Semivariogram chart | uncertainty | `spatial.slope.semivariogram` points |
| Distribution charts (Mars/Moon/between) | uncertainty | `DistributionChart` component with counts |
| Planetary coverage dashboard | benchmarking | `planetCoverage` keys/values |
| Dataset provenance cards | benchmarking | `datasets` with body, validation_status, access_status |
| Real benchmark findings list | benchmarking | `realBenchmarkFindings` |

### Development-Only / Non-Scientific Elements (to be removed)

| Element | Location | Purpose | Productization Action |
|---------|----------|---------|----------------------|
| "PHASE 08" label | header-status (`research-header`) | Platform branding | Remove / replace with neutral label |
| "PHASE 11 / REAL EXPERIMENT DATA" | sampling view heading | Phase attribution | Remove or generalize |
| "PHASE 13 / REAL EXPERIMENT DATA" | benchmarking view heading | Phase attribution | Remove or generalize |
| "LIVE DATA / PHASE 08" | research-header `.live-dot` | Platform branding | Remove / replace |
| "60 PHYSICAL WINDOW" | features view heading | Technical specification | Generalize / remove |
| "MORPHOLOGY ENGINE" | SimilarityReadiness panel | Engine branding | Remove or neutralize |
| "PHASE 11 / REAL EXPERIMENT DATA" | SamplingView heading | Phase attribution | Remove |
| "BLOCK BOOTSTRAP / 320 M" | uncertainty view heading | Technical specification | Generalize |
| Disabled "RANKING" badge | explorer view | UI state indication | Remove / rephrase |
| Internal metric names (e.g., "tmsi_mean", "tmsi_lower_95") | uncertainty view | Technical metric names | Rename / explain for non-specialists |
| Raw SHA-256 hashes in provenance cards | provenance | Technical identifiers | Summarize / remove |
| Duplicate "EARTH PENDING" indicators | explorer, provenance, footer | Redundant status display | Consolidate |
| Development labels (various "PHASE" tags) | multiple views | Development tracking | Remove |
| Unused technical controls | various | Not implemented | Remove |
| Placeholder content | various | Empty/loading states | Clean up or implement |

### Unused Components
| Component | Reason |
|-----------|--------|
| SimilarityReadiness.tsx | Not rendered in current ResearchWorkbench navigation; standalone panel not integrated |
| BackendStatus.tsx | Not rendered in current ResearchWorkbench layout; standalone badge not integrated |

### Scientific Workflow Support Assessment

**Fully supported** (keep, may need UI refinement):
- Terrain exploration with 5 layer types
- TMSI baseline display and interpretation
- Feature-level comparison (3 terrain signals)
- Bootstrap uncertainty quantification (mean, 95% CI)
- Spatial autocorrelation (Moran's I)
- Extent and seed sensitivity display
- Feature ablation and weight sensitivity
- Dataset provenance and blocking status
- Interpretation safeguards (TMSI does NOT establish planetary identity)
- Export functionality (JSON/CSV/PDF)
- Sampling framework (Phase 11 real data)
- DEM benchmarking (Phase 13 real data)

**Requires productization adjustment** (remove/devise elements):
- Phase/step labels that imply development progress
- Duplicate Earth pending indicators
- Disabled ranking badge
- Raw technical metric names without context
- Raster URLs pointing to localhost
- Development-phase branding ("PHASE 08", etc.)

### Critical Issues for Productization

1. **Raster URLs expose localhost:8000** — Must be configured for production backend
2. **Phase/step labels** — Imply ongoing development, not competition-ready
3. **Disabled ranking** — Either implement or remove with explanation
4. **Earth pending dominance** — Should not dominate the homepage; move to Data & Methods
5. **Multiple "EARTH PENDING"** indicators — Consolidate into single authoritative source
6. **Development-phase branding** — Replace with neutral planetary science aesthetic
7. **Technical metric names** — Rename or explain for non-specialist visitors

### Recommended UI Restructuring

Per the Phase 16 requirements, reorganize around four destinations:

**A. EXPLORE** — Prominent terrain viewer as main attraction
**B. COMPARE** — TMSi baseline, methodology, feature comparisons prominently displayed
**C. RELIABILITY** — Uncertainty transparency (bootstrap, spatial autocorrelation, extent/seed sensitivity)
**D. DATA & METHODS** — Dataset provenance, acquisition sources, reproducibility, Earth blocking status

Each destination should minimize development-phase language and technical identifiers, replacing them with visitor-friendly scientific explanations.