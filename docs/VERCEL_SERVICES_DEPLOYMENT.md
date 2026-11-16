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

`fastapi>=0.115,<1.0`, `uvicorn[standard]>=0.34,<1.0`, `pydantic>=2.10,<3.0`, `numpy>=2.0,<3.0`, `scipy>=1.14,<2.0`, `rasterio>=1.4,<2.0`, `reportlab>=4.0,<6.0`, `certifi>=2024.8,<2027.0`.

Excluded because unused at runtime (measured by import-graph audit): `pandas` (~72 MB), `geopandas`, `pyogrio` (~75 MB), `xarray`, `botocore` (~27 MB), `earthaccess`, `pytest` (moved to `requirements-dev.txt` with `httpx`), and **`httpx2`** — the suspicious pin is a real package (Tom Christie's "next generation HTTP client", now under Pydantic stewardship, 2.16.0) — it is simply never imported anywhere in backend or science runtime code; it contributed nothing but weight.

## Moved files (integrity-verified, 39/39 data files byte-identical pre/post `mv`)

- `data/` → `backend/data/` (incl. all raw + processed rasters and JSON metadata; hashes in `data/metadata/*.json` records + `/tmp/p1_data_hashes_*.txt` snapshot)
- `science/` → `backend/science/` (runtime closure: `similarity`, `scoring`, `comparison`, `features`, `preprocessing/coordinate_systems.py`, `metadata`, `datasets`)

## Code changes (path rebasing + deployment hardening, no science changes)

`REPOSITORY_ROOT`/`parents[3]` → `parents[2]` in `backend/app/services/similarity.py`, `backend/app/api/similarity.py`, `backend/app/api/candidates.py`, `backend/app/services/export.py`.
`backend/app/main.py`: CORS origins now env-overridable (`FRONTEND_ORIGINS`); default keeps localhost dev origins. Same-origin Service routing makes production CORS a no-op.
Test-harness path fixes required by the move (no assertion weakened): `science/tests/test_phase20_6_scientific.py` (absolute path now `…/nasaspaceapp/backend/data/…`), `test_phase13_validation.py` (subprocess path), `test_phase11_validation.py` (`backend.app.services` → `app.services`).
Frontend: `lib/api.ts` exports `apiUrl` = `NEXT_PUBLIC_API_URL` when set, else `http://localhost:8000` in `development`, else `""` (same-origin `/api`). All 5 production call sites use it (SimilarityReadiness, CandidateTerrainPreview, TerrainViewer, ResearchWorkbench + error strings). ESLint: 8 pre-existing errors only (unchanged baseline), TSC 0, `next build` ✓.

## Measured

- Moved rasters are byte-identical (SHA-256 before/after): 39/39.
- Production venv (fresh, `requirements.txt` only): **269 MB** installed, installs in ~4 s, imports cleanly (`app.main`, `science.similarity.features.feature_extraction`, `science.similarity.scoring.similarity`), rasterio 1.5.2, numpy 2.5.5, scipy 1.18.1, reportlab 5.1.0, FastAPI 0.163.1.
- **Actual estimated backend bundle** = 269 MB (venv, incl. local-dev uvicorn stack) + ~99.9 MB (required processed rasters after exclusions) + ~1.5 MB (app + science code) ≈ **370 MB** — comfortably under the standard 500 MB Python limit; Large Functions NOT required.
- Backend tests: **32/32 pass**. Science tests: **134/134 pass**. `pytest` not in production requirements.
- Frontend: `next build` ✓; MAP loads 13 markers with `BACKEND ONLINE`; 0 console errors; TSC 0.
- Endpoint suite (all HTTP 200 except intentional negative cases):
  `GET /api/health` ✓ · `GET /api/candidates` ✓ · `GET /api/candidates/terrain-grid/death_valley` ✓ (real n37w117 grid) · `GET /api/similarity/status` ✓ · `GET /api/similarity/results` ✓ (Moon↔Mars 49.92 stored experiment) · `GET /api/similarity/sampling-framework` ✓ · `GET /api/similarity/features` ✓ · `GET /api/similarity/methodology` ✓ · `GET /api/similarity/terrain-grid/moon_lola` ✓ · `GET /api/similarity/terrain-grid/mars_jezero_ctx_dtm` ✓ · `GET /api/similarity/terrain-grid/death_valley` → **409 `{"detail":"Dataset is unavailable: death_valley"}` (correct — death_valley is served by `/api/candidates/terrain-grid/death_valley`, not the similarity registry)** · JSON export ✓ · CSV export ✓ · PDF export ✓ (valid `%PDF-1.4`, ReportLab) · `atacama` terrain → 404 with explicit unavailable message ✓.

## Unresolved / honest caveats

1. `npx vercel build` could not be run: CLI is not authenticated (`login_required`). The config is validated structurally + against the current Services spec (schema-valid JSON; framework slugs `nextjs`/`fastapi`; entrypoint module path; top-level rewrites preserve original path). **Production behavior is not verified — this is a preparation, not a deployment.**
2. Repo carries ~486 MB of committed build artifacts (`node_modules/` ~670 MB + `frontend/.next`); cloning will be slow but works. Untrack them later (git history rewrite) if desired — not done in this phase.
3. Science research scripts reference the old repo-root `data/`/`science/` paths (e.g., `data_ingestion/*`, `science/preprocessing/pipeline.py`); they are intentionally untouched and excluded from the function bundle; run research tooling from `backend/` now.
4. Vercel Services is **public Beta on all plans (incl. Hobby)**; timing/limits per Vercel docs may change — re-check Fluid compute defaults and limits at deploy time.
5. No CPU-intensive work happens at request time (grids are raster-read + numpy), so Hobby 2 GB / 300 s are adequate.

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
cd backend  && PYTHONPATH=. .venv/bin/python -m uvicorn app.main:app --reload --port 8000
```
