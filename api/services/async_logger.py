"""
NINCore - Async Logger Service
==============================
Handles logging telemetry and audit events asynchronously.
"""

import logging
from database.db import SessionLocal
from database import crud

logger = logging.getLogger(__name__)

def log_verification_event_async(
    nin: int,
    sector_name: str,
    location_state: str,
    geo_velocity: float,
    login_freq_24h: int,
    device_hash: str,
    access_hour: int,
    risk_score: float,
    prediction: str,
    agency_id: str,
):
    """
    Logs the telemetry and audit trail for a verification event asynchronously.
    It instantiates its own short-lived DB session since this runs in a background thread.
    """
    db = SessionLocal()
    try:
        crud.telemetry.log_event(
            db,
            nin=nin,
            sector_requesting=sector_name,
            location_state=location_state,
            geographic_velocity=geo_velocity,
            login_frequency_24h=login_freq_24h + 1,
            device_id_hash=device_hash,
            access_hour=access_hour,
            risk_score=risk_score,
            ml_prediction=prediction,
        )

        crud.audit.log(
            db,
            nin=nin,
            agency_id=agency_id,
            action_taken="VERIFY_REQUEST",
            justification=(
                f"Sector={sector_name} "
                f"State={location_state} "
                f"Prediction={prediction} "
                f"Score={risk_score:.4f}"
            ),
        )
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log background telemetry for NIN {nin}: {e}")
        db.rollback()
    finally:
        db.close()
