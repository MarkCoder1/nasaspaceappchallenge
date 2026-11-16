import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.similarity import router as similarity_router
from app.api.candidates import router as candidates_router

# Same-origin deployments (Vercel Services rewrite /api/* -> this service) need no CORS.
# Local development (frontend on :3000/:3001) keeps the localhost dev origins.
# Override via FRONTEND_ORIGINS (comma-separated) when needed.
DEFAULT_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"
ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("FRONTEND_ORIGINS", DEFAULT_ORIGINS).split(",") if o.strip()]

app = FastAPI(title="TerraMatch API", version="0.1.0")

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