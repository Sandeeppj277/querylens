"""
QueryLens — FastAPI Application Entry Point

Starts the server with:  uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import APP_TITLE, APP_VERSION, APP_DESCRIPTION
from app.routes.query import router as query_router

# ── Create FastAPI App ───────────────────────────────────
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)

# ── CORS — allow the frontend to talk to the API ────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],             # in production, lock this down
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register API Routes ─────────────────────────────────
app.include_router(query_router)

# ── Health Check ─────────────────────────────────────────
@app.get("/health", tags=["system"])
async def health_check():
    return {
        "status": "healthy",
        "app": APP_TITLE,
        "version": APP_VERSION,
    }

# ── Serve Frontend Static Files ─────────────────────────
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
frontend_dir.mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
