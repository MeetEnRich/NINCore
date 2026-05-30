"""
NINCore database package
=========================
Exposes the three core database objects so any module in the project
can import them with a single, clean line:

    from database import engine, get_db, Base
    from database import crud
    from database.models import CitizenRegistry, RiskTelemetry, ...

Import order matters here: db.py must be imported before models.py
(models need Base), and models.py before crud.py (crud needs models).
"""

from database.db import Base, engine, get_db, get_db_context, SessionLocal
from database import models   # registers all ORM classes against Base
from database import crud     # exposes crud.citizen, crud.sector, etc.

__all__ = [
    "Base",
    "engine",
    "get_db",
    "get_db_context",
    "SessionLocal",
    "models",
    "crud",
]