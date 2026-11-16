import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.api.health import router as health_router
from app.api.similarity import router as similarity_router
from app.api.candidates import router as candidates_router

logger = logging.getLogger("terramatch")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

REQUIRED_RASTERS = [
    "data/processed/mars_jezero_ctx_elevation_m.tif",
    "data/processed/moon_lola_80s_20m_elevation_m.tif",
    "data/processed/USGS_1_n37w117_20m_utm11n.tif",
]


def _service_root() -> Path:
    return Path(__file__).resolve().parents[1]


@asynccontextmanager
async def lifespan(app: FastAPI):
    root = _service_root()
    missing = [rel for rel in REQUIRED_RASTERS if not (root / rel).is_file()]
    if missing:
        logger.error("startup probe: required raster(s) missing: %s (root=%s)", ", ".join(missing), root)
    else:
        logger.info("startup probe: all required rasters present (root=%s)", root)
    yield


app = FastAPI(title="TerraMatch API", version="0.1.0", lifespan=lifespan)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error", "error_type": type(exc).__name__})


# Same-origin deployments (Vercel Services rewrite /api/* -> this service) need no CORS.
# Local development (frontend on :3000/:3001) keeps the localhost dev origins.
# Override via FRONTEND_ORIGINS (comma-separated) when needed.
DEFAULT_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"
ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("FRONTEND_ORIGINS", DEFAULT_ORIGINS).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(similarity_router)
app.include_router(candidates_router)