"""
NINCore API — Risk Verification Route
========================================
POST /api/v1/verify-risk

The core endpoint. A sector agency submits a NIN + context,
the engine assembles the feature vector, runs ML inference,
logs the event, and returns the risk assessment.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from database.db import get_db
from database import crud
from database.models import APIKey
from api.middleware.auth import get_verified_agency
from api.schemas.request import VerifyRiskRequest
from api.schemas.response import RiskAssessmentResponse
from models.risk_engine import RiskEngine
from api.services.feature_store import FeatureStore
from api.services.async_logger import log_verification_event_async

logger = logging.getLogger(__name__)
router = APIRouter()

# Load model once at module level — not on every request
_engine = RiskEngine()

HIGH_RISK_THRESHOLD = 0.7

@router.post(
    "/verify-risk",
    response_model=RiskAssessmentResponse,
    summary="Submit NIN for real-time risk assessment",
    tags=["Verification"],
)
def verify_risk(
    payload: VerifyRiskRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    agency: APIKey = Depends(get_verified_agency),
):
    """
    Core risk assessment endpoint.

    Workflow:
      1. Validate NIN exists in Citizen_Registry
      2. Call FeatureStore to assemble the 18-feature vector
      3. Run Random Forest inference
      4. Dispatch BackgroundTask to log Telemetry and Audit
      5. Return risk score + decision immediately
    """
    nin = payload.NIN

    # ── Step 1: Validate NIN ─────────────────────────────────────────
    if not crud.citizen.exists(db, nin=nin):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NIN {nin} not found in Citizen_Registry.",
        )

    citizen = crud.citizen.get_by_nin(db, nin=nin)

    # ── Step 2: Assemble feature vector via Feature Store ────────────
    now = datetime.utcnow()
    access_hour = now.hour

    feature_vector, device_hash, login_freq_24h, geo_velocity = FeatureStore.build_feature_vector(
        db=db,
        nin=nin,
        citizen=citizen,
        request_location=payload.Location_State,
        request_device=payload.Device_ID,
        access_hour=access_hour,
    )

    # ── Step 3: ML Inference ─────────────────────────────────────────
    risk_score, prediction = _engine.predict(feature_vector)

    # ── Step 4: Dispatch Background Logging ──────────────────────────
    background_tasks.add_task(
        log_verification_event_async,
        nin=nin,
        sector_name=payload.Sector_Name,
        location_state=payload.Location_State,
        geo_velocity=geo_velocity,
        login_freq_24h=login_freq_24h,
        device_hash=device_hash,
        access_hour=access_hour,
        risk_score=risk_score,
        prediction=prediction,
        agency_id=agency.Agency_ID,
    )

    # ── Step 5: Build response ───────────────────────────────────────
    action  = "FLAGGED" if prediction == "High_Risk" else "CLEARED"
    message = (
        "HIGH RISK: Identity flagged for immediate review."
        if prediction == "High_Risk"
        else "LOW RISK: Identity cleared for sector access."
    )

    logger.info(
        "NIN=%s Agency=%s Score=%.4f Prediction=%s [LOGGING_ASYNC]",
        nin, agency.Agency_ID, risk_score, prediction,
    )

    return RiskAssessmentResponse(
        NIN              = nin,
        Risk_Score       = round(risk_score, 4),
        ML_Prediction    = prediction,
        Confidence_Pct   = round(risk_score * 100, 2),
        Sector_Requested = payload.Sector_Name,
        Location_State   = payload.Location_State,
        Timestamp        = now,
        Action           = action,
        Message          = message,
    )