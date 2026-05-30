"""
NINCore — API Server Launcher
================================
Single command to start the FastAPI server.

Usage:
    python run_api.py

The API will be available at:
    http://localhost:8000
    http://localhost:8000/docs      (Swagger UI)
    http://localhost:8000/redoc     (ReDoc)
    http://localhost:8000/health    (Health check)
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host        = "0.0.0.0",
        port        = 8000,
        reload      = True,
        log_level   = "info",
    )