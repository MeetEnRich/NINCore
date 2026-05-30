"""
NINCore API package
====================
FastAPI application exposing three route groups:
  - /api/v1/verify-risk  → verify.py
  - /api/v1/audit        → audit.py
  - /api/v1/admin        → admin.py

Entry point: api/main.py
"""

from api import schemas, middleware, routes

__all__ = ["schemas", "middleware", "routes"]