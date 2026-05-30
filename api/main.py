"""
NINCore API — Main Application Entry Point
============================================
FastAPI application that wires together all routes,
middleware, and startup/shutdown events.

Start the server with:
    python run_api.py
or directly:
    uvicorn api.main:app --reload --port 8000
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import verify, audit, admin
from database.db import check_connection
from models.risk_engine import RiskEngine

# ── Logging ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Log directory ─────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR  = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

file_handler = logging.FileHandler(LOG_DIR / "nincore_api.log")
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s"
))
logging.getLogger().addHandler(file_handler)


# ── Lifespan — startup & shutdown ────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once on startup and once on shutdown.
    Validates DB connection and model file before accepting requests.
    """
    logger.info("=" * 55)
    logger.info("  NINCore API — Starting up")
    logger.info("=" * 55)

    # Database check
    if not check_connection():
        logger.error("Database connection failed. Run setup_database.py first.")
        raise RuntimeError("Database unavailable.")
    logger.info("[OK] Database connection verified.")

    # Model check
    try:
        engine = RiskEngine()
        logger.info("[OK] Risk engine loaded: %s", engine)
    except FileNotFoundError as e:
        logger.error("Model file missing: %s", e)
        raise RuntimeError("Risk engine model unavailable.") from e

    logger.info("NINCore API is ready to accept requests.")
    logger.info("=" * 55)

    yield  # Application runs here

    logger.info("NINCore API shutting down.")


# ── FastAPI app ───────────────────────────────────────────────────────
app = FastAPI(
    title       = "NINCore — Identity Governance & Risk Engine",
    description = (
        "ML-powered API for real-time NIN-centric identity risk assessment "
        "across Nigeria's Banking, Health, Education, Transport, and "
        "Telecoms sectors.\n\n"
        "All endpoints require a valid **X-API-Key** header.\n\n"
        "Developed by Stefan Habila Musa — Federal University of Lafia, 2026."
    ),
    version     = "1.0.0",
    lifespan    = lifespan,
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)


# ── CORS ──────────────────────────────────────────────────────────────
# Allows the Streamlit dashboard (running on a different port) to
# call the API without browser CORS errors.
app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],   # tighten in production
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)


# ── Routes ────────────────────────────────────────────────────────────
app.include_router(
    verify.router,
    prefix = "/api/v1",
)
app.include_router(
    audit.router,
    prefix = "/api/v1/audit",
)
app.include_router(
    admin.router,
    prefix = "/api/v1/admin",
)


# ── Health check ──────────────────────────────────────────────────────
@app.get(
    "/health",
    tags    = ["System"],
    summary = "API health check",
)
def health_check():
    """
    Returns the live status of the API, database, and risk engine.
    No authentication required.
    """
    db_ok    = check_connection()
    model_ok = Path(BASE_DIR / "models" / "saved" / "risk_engine.pkl").exists()

    return JSONResponse(content={
        "status":   "healthy" if db_ok and model_ok else "degraded",
        "database": "connected" if db_ok    else "unavailable",
        "model":    "loaded"    if model_ok else "missing",
        "version":  "1.0.0",
    })


# ── Root ──────────────────────────────────────────────────────────────
@app.get("/", tags=["System"], summary="API root")
def root():
    return {
        "system":      "NINCore Identity Governance & Risk Engine",
        "version":     "1.0.0",
        "docs":        "/docs",
        "health":      "/health",
        "author":      "Stefan Habila Musa",
        "institution": "Federal University of Lafia",
    }