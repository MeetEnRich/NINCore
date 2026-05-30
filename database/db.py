"""
NINCore Database Connection Handler
=====================================
Provides the SQLAlchemy engine, session factory, and Base class
used by all other database layers (models, crud, API).

Usage:
    from database.db import get_db, engine

    # FastAPI dependency injection
    def some_route(db: Session = Depends(get_db)):
        ...

    # Direct use (scripts, notebooks)
    from database.db import SessionLocal
    with SessionLocal() as db:
        ...
"""

import os
import logging
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base

# ── Logging ───────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

# ── Path resolution ───────────────────────────────────────────────────
# Works whether this file is run from inside /database/ or from project root
_THIS_DIR  = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR  = os.path.dirname(_THIS_DIR)
DB_PATH    = os.path.join(_BASE_DIR, "database", "nincore.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# ── Engine ────────────────────────────────────────────────────────────
# connect_args={"check_same_thread": False} is required for SQLite
# when used with FastAPI's async request handling, because a single
# SQLite connection is otherwise restricted to the thread that created it.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,          # Set True to log every SQL statement (debug only)
    pool_pre_ping=True,  # Verify connection health before each use
)


# ── Enforce foreign keys on every new SQLite connection ───────────────
# SQLite disables FK enforcement by default; this hook re-enables it
# for every connection the pool hands out.
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA journal_mode = WAL;")   # better concurrent reads
    cursor.close()


# ── Session factory ───────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,   # keep attributes accessible after commit
)

# ── Declarative base (imported by models.py) ──────────────────────────
Base = declarative_base()


# ── FastAPI dependency ────────────────────────────────────────────────
def get_db():
    """
    Yield a SQLAlchemy session for use as a FastAPI dependency.

    Example:
        @router.get("/some-route")
        def route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Context manager (scripts / notebooks) ────────────────────────────
@contextmanager
def get_db_context():
    """
    Context manager for non-FastAPI usage (scripts, notebooks, tests).

    Example:
        from database.db import get_db_context
        with get_db_context() as db:
            results = db.query(CitizenRegistry).limit(5).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Health check ──────────────────────────────────────────────────────
def check_connection() -> bool:
    """
    Verify that the database file exists and is reachable.
    Returns True on success, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
        logger.info("Database connection OK: %s", DB_PATH)
        return True
    except Exception as exc:
        logger.error("Database connection FAILED: %s", exc)
        return False


# ── Quick sanity check when run directly ─────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if check_connection():
        print(f"[OK] Connected to {DB_PATH}")
    else:
        print(f"[FAIL] Could not connect to {DB_PATH}")
        print("Run scripts/setup_database.py first.")