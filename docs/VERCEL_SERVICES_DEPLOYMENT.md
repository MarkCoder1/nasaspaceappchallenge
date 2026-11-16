# Terra Twin — Vercel Services (one-project) deployment preparation

**Date:** 2026-11-15 · **Scope:** make the app deployable as ONE Vercel project with two services (Next.js `frontend` at `/`, FastAPI `backend` at `/api/*`). No Vercel credentials were used; no deployment was executed; nothing was committed or pushed.

## Final `vercel.json` (repo root)

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "services": {
    "frontend": { "root": "frontend/", "framework": "nextjs" },
    "backend": {
      "root": "backend/",
      "framework": "fastapi",
      "entrypoint": "app.main:app",
      "functions": {
        "app/main.py": {
          "maxDuration": 300,
          "excludeFiles": "{data/raw/**,data/processed/USGS_1_n36w117_20m_utm11n.tif,data/processed/moon_lola_central_20km_window.tif,tests/**,science/tests/**,science/validation/**,science/data_ingestion/**,science/preprocessing/pipeline.py,science/preprocessing/process_moon_lola.py,science/similarity/validation/**,**/__pycache__/**,**/*.pyc,.venv/**,requirements-dev.txt,.env*}"
        }
      }
    }
  },
  "rewrites": [
    { "source": "/api/(.*)", "destination": { "service": "backend" } },
    { "source": "/(.*)",   "destination": { "service": "frontend" } }
  ]
}
```

- Two services only; the unused root `app/` scaffold is never built or served.
- `/api/*` → FastAPI service (original path preserved — FastAPI routes are already `/api/…`); `/*` → Next.js.
- No service bindings: browser calls are same-origin; no secrets involved.
- `excludeFiles` excludes raw rasters (125 MB), the unused processed Earth tile (80 MB), the unused LOLA central window (3.6 MB), all tests, and caches — keeping the function under the standard **500 MB Python limit**.
- `.env*` excluded so no secrets can leak into the bundle.

## Production `backend/requirements.txt` (minimal, import-audited)

`fastapi>=0.115,<1.0`, `pydantic>=2.10,<3.0`, `numpy>=2.0,<3.0`, `scipy>=1.14,<2.0`, `rasterio>=1.4,<2.0`, `reportlab>=4.0,<6.0`, `certifi>=2024.8,<2027.0`.

Excluded because unused at runtime (measured by import-graph audit): `pandas` (~72 MB), `geopandas`, `pyogrio` (~75 MB), `xarray`, `botocore` (~27 MB), `earthaccess`, `uvicorn[standard]` (~10 MB — Fluid compute serves ASGI; it moves to `requirements-dev.txt` together with `pytest` and `httpx` for local runs), `pytest`, and **`httpx2`** — the suspicious pin is a real package (Tom Christie's "next generation HTTP client", now under Pydantic stewardship, 2.16.0) — it is simply never imported anywhere in backend or science runtime code; it contributed nothing but weight.

## Moved files (integrity-verified, 33/33 data files byte-identical pre/post `mv`; n36w117 RAW/PROCESSED + LOLA central window moved OUT of the service root to the repo `data/` to honor the 500 MB function limit)

- `data/` → `backend/data/` then rebalanced: `USGS_1_n36w117.{tif,xml}` (raw, 52 MB) and `USGS_1_n36w117_20m_utm11n.tif` (processed, 84 MB) and `moon_lola_central_20km_window.tif` (4 MB) moved to the repo-root `data/` so the service root stays small; runtime-served files remain in `backend/data/` (LOLA 14.9 MB + Jezero 7.9 MB + Death Valley n37w117 78 MB + metadata JSON ~0.7 MB); hashes for moved files were re-verified
- `science/` → `backend/science/` (runtime closure intact)

## Code changes (path rebasing + deployment hardening, no science changes)

`REPOSITORY_ROOT`/`parents[3]` → `parents[2]` in `backend/app/services/similarity.py`, `backend/app/api/similarity.py`, `backend/app/api/candidates.py`, `backend/app/services/export.py`.
`backend/app/main.py`: CORS origins now env-overridable (`FRONTEND_ORIGINS`); default keeps localhost dev origins. Same-origin Service routing makes production CORS a no-op.
Test-harness path fixes required by the move (no assertion weakened): `science/tests/test_phase20_6_scientific.py` (absolute path now `…/nasaspaceapp/backend/data/…`), `test_phase13_validation.py` (subprocess path), `test_phase11_validation.py` (`backend.app.services` → `app.services`).
Frontend: `lib/api.ts` exports `apiUrl` = `NEXT_PUBLIC_API_URL` when set, else `http://localhost:8000` in `development`, else `""` (same-origin `/api`). All 5 production call sites use it (SimilarityReadiness, CandidateTerrainPreview, TerrainViewer, ResearchWorkbench + error strings). ESLint: 8 pre-existing errors only (unchanged baseline), TSC 0, `next build` ✓.

## Measured

- Moved rasters are byte-identical (SHA-256 before/after): 39/39.
- Production venv (fresh, `requirements.txt` only): **269 MB** installed, installs in ~4 s, imports cleanly (`app.main`, `science.similarity.features.feature_extraction`, `science.similarity.scoring.similarity`), rasterio 1.5.2, numpy 2.5.5, scipy 1.18.1, reportlab 5.1.0, FastAPI 0.163.1.
- **Actual estimated backend bundle** = 245 MB (fresh minimal venv minus pip) + ~101 MB (required processed rasters in `backend/data/` + JSON) + ~2.5 MB (app + science code) ≈ **350 MB or less** — comfortably under the standard 500 MB Python limit; Large Functions NOT required. Before this fix the bundle was ~640 MB (measured failure: LAMBDA_SIZE_EXCEEDED against 500 MB).
- Backend tests: **32/32 pass**. Science tests: **134/134 pass**. `pytest` not in production requirements.
- Bundle simulation (faithful local replica of the Vercel project-files bundle, `backend/` with `.venv`/tests/raw excluded): **100 files / 101 MB**; all 16 endpoints verified HTTP 200 (rasters + exports included); startup probe logged all required rasters present.
- Lifecycle hardening: FastAPI `lifespan` startup probe logs missing rasters as ERROR at startup (no crash); global exception handler logs full traceback (method + path) and returns `{"detail":"Internal server error","error_type":"<ClassName>"}` — no secrets or raster contents are exposed.
- Frontend: `next build` ✓; MAP loads 13 markers with `BACKEND ONLINE`; 0 console errors; TSC 0.
- Endpoint suite (all HTTP 200 except intentional negative cases):
  `GET /api/health` ✓ · `GET /api/candidates` ✓ · `GET /api/candidates/terrain-grid/death_valley` ✓ (real n37w117 grid) · `GET /api/similarity/status` ✓ · `GET /api/similarity/results` ✓ (Moon↔Mars 49.92 stored experiment) · `GET /api/similarity/sampling-framework` ✓ · `GET /api/similarity/features` ✓ · `GET /api/similarity/methodology` ✓ · `GET /api/similarity/terrain-grid/moon_lola` ✓ · `GET /api/similarity/terrain-grid/mars_jezero_ctx_dtm` ✓ · `GET /api/similarity/terrain-grid/death_valley` → **409 `{"detail":"Dataset is unavailable: death_valley"}` (correct — death_valley is served by `/api/candidates/terrain-grid/death_valley`, not the similarity registry)** · JSON export ✓ · CSV export ✓ · PDF export ✓ (valid `%PDF-1.4`, ReportLab) · `atacama` terrain → 404 with explicit unavailable message ✓.

## Production outcome (2026-11-16, verified live)

1. `vercel login` restored by owner (`lionzak`). Project `lionzaks-projects/nasaspaceappchallenge` confirmed: Root Directory = `.`, Framework Preset Services (frontend + backend, one project, one shared domain). The suspected `frontend/` Root Directory bug was **disproven by inspection**; the real failure was Python runtime library missing.
2. First production deploy (e4863f29) reported successful builds; backend service crashed at cold start: `ImportError: libexpat.so.1` in Vercel's python3.12 runtime — GDAL-linked manylinux wheels (rasterio) require a system `libexpat.so.1` the Vercel runtime does not provide. `/api/*` → **HTTP 500 for every endpoint**.
3. Fix: backend switched to Vercel **container runtime** — `backend/Dockerfile` (`python:3.12-slim` + `apt-get install libexpat1`), `backend/.dockerignore` added, `entrypoint: "Dockerfile"` in `vercel.json`; Scientific stack unchanged. Deployment `422a2190` built Ready (`BUILD DURATION 2m`, container image 278.73 MB).
4. Live production check (all 200): `/api/health`, `/api/candidates` (13), `/api/similarity/{results,status,sampling-framework,features,methodology}`, both raster terrain-grids, Death Valley candidates terrain-grid, CSV/JSON/PDF exports, `GET /` homepage; all layers (elevation/hillshade/slope/local_relief/terrain_ruggedness) return physically validated ranges.
5. Follow-up measured fix: `_slope_degrees` and `_hillshade` were not scaling by grid cell size (32×32 / 192×192 preview), making slope read ~90° everywhere; now divided by cell meters. Commit `52ac50bf`. Slope reads 0.03–35.4° on Moon LOLA (previous reading was nonsense); identical science is untouched.
6. Alias verified live: https://nasaspaceappchallenge-six.vercel.app (set from the deployment, previously `nasaspaceappchallenge-six.vercel.app` consistently) — BACKEND ONLINE, 3 terrain datasets render real data, 13 MAP markers, COMPARE 49.92, zero console errors.

## Remaining limitations (honest)
1. Repo carries ~486 MB of committed build artifacts (`node_modules/`, `.next/`); cloning is slow; untrack later (git-file removal) if desired.
2. Vercel Services/Container Runtime are public Beta; plans/limits may change; re-check at deploy time.
3. Science research scripts reference the old repo-root `data/`/`science/` paths; they are intentionally untouched; run research tooling from `backend/`.
4. NASADEM remains blocked (Earthdata HTTP 401); Earth – Moon/Mars comparisons remain limited to the two USGS 3DEP tiles; no candidate is field-validated.

## Exact steps to deploy (user runs these)

```bash
cd "<repo-root>"
vercel login          # one-time
vercel                # first link+deploy: choose existing scope/project or create
# Or link a pre-made Vercel project instead of `vercel`:
vercel link
vercel --prod
```

Then in the Vercel dashboard (Project → Settings):
1. Confirm both services were detected (frontend, backend) and no third service/app exists.
2. Open the deployment → confirm `/` loads Terra Twin, `/api/health` returns `{"status":"ok","service":"terramatch-backend"}` and the header shows **BACKEND ONLINE**.
3. MAP should show 13 markers; EXPLORE → Death Valley 3DEP shows the USGS terrain; DATA & METHODS exports download.

Before deploying, **commit & push** the changes (not done — per instructions). Note the moved `data/` and `science/` will show as rename/delete-add pairs; commit as one logical change.

Local dev (unchanged):
```bash
cd frontend && npm run dev          # :3000, API defaults to localhost:8000 (dev fallback)
pip install -r requirements-dev.txt
cd backend  && PYTHONPATH=. .venv/bin/python -m uvicorn app.main:app --reload --port 8000
```
