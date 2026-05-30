"""
NINCore API — Risk Verification Route
========================================
POST /api/v1/verify-risk

The core endpoint. A sector agency submits a NIN + context,
the engine assembles the feature vector, runs ML inference,
logs the event, and returns the risk assessment.
"""

import hashlib
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.db import get_db
from database import crud
from database.models import APIKey
from api.middleware.auth import get_verified_agency
from api.schemas.request import VerifyRiskRequest
from api.schemas.response import RiskAssessmentResponse
from models.risk_engine import RiskEngine

logger = logging.getLogger(__name__)
router = APIRouter()

# Load model once at module level — not on every request
_engine = RiskEngine()

NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa",
    "Benue", "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti",
    "Enugu", "FCT", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina",
    "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo",
    "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara",
]
STATE_INDEX = {s: i for i, s in enumerate(sorted(NIGERIAN_STATES))}

HIGH_RISK_THRESHOLD = 0.7


def _hash_device(device_id: str) -> str:
    """Hash the raw device ID before storing."""
    return hashlib.sha256(device_id.encode()).hexdigest()


def _encode_state(state: str) -> int:
    """Encode state name to integer — mirrors LabelEncoder from training."""
    return STATE_INDEX.get(state, 0)


@router.post(
    "/verify-risk",
    response_model=RiskAssessmentResponse,
    summary="Submit NIN for real-time risk assessment",
    tags=["Verification"],
)
def verify_risk(
    payload: VerifyRiskRequest,
    db: Session = Depends(get_db),
    agency: APIKey = Depends(get_verified_agency),
):
    """
    Core risk assessment endpoint.

    Workflow (mirrors Section 3.7.2 Activity Diagram):
      1. Validate NIN exists in Citizen_Registry
      2. Assemble 18-feature vector from DB + request context
      3. Run Random Forest inference
      4. Log to Risk_Telemetry and System_Audit
      5. Return risk score + decision
    """
    nin = payload.NIN

    # ── Step 1: Validate NIN ─────────────────────────────────────────
    if not crud.citizen.exists(db, nin=nin):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NIN {nin} not found in Citizen_Registry.",
        )

    citizen = crud.citizen.get_by_nin(db, nin=nin)

    # ── Step 2: Assemble feature vector ──────────────────────────────
    now         = datetime.utcnow()
    access_hour = now.hour

    # Real-time behavioral features from DB
    login_freq_24h = crud.telemetry.get_login_frequency_24h(db, nin=nin)
    active_links   = crud.sector.count_active_links(db, nin=nin)
    last_event     = crud.telemetry.get_last_event(db, nin=nin)

    # Geographic velocity — distance proxy using state change
    # If last event was in a different state, flag as potential conflict
    geo_velocity = 0.0
    if last_event and last_event.Location_State:
        if last_event.Location_State != payload.Location_State:
            # Different state since last event — assign elevated velocity
            geo_velocity = 500.0
        else:
            geo_velocity = 10.0
    
    # Sector conflict — active in different state simultaneously
    sector_conflict = 1 if geo_velocity >= 500.0 and login_freq_24h > 3 else 0

    # Sector flags from Sector_Mapping
    sector_flags = {s: 0 for s in
                    ["Banking", "Health", "Education", "Transport", "Telecoms"]}
    for link in crud.sector.get_by_nin(db, nin=nin):
        if link.Sector_Name in sector_flags:
            sector_flags[link.Sector_Name] = 1

    # Failed auth attempts — from recent telemetry
    recent_logs    = crud.telemetry.get_history(db, nin=nin, limit=10)
    failed_attempts = sum(
        1 for log in recent_logs
        if log.ML_Prediction == "High_Risk"
    )

    # Age consistency — derive from citizen DOB vs age on record
    try:
        birth_year     = int(citizen.DOB[:4])
        computed_age   = now.year - birth_year
        age_consistency = min(1.0, max(0.0, 1.0 - abs(computed_age - 40) / 80))
    except Exception:
        age_consistency = 0.75

    # Name mismatch — simplified: flag if sector_conflict already active
    name_mismatch = 1 if sector_conflict == 1 and failed_attempts > 2 else 0

    # Device reputation — new device gets low score, seen device gets high
    device_hash = _hash_device(payload.Device_ID)
    known_device = any(
        log.Device_ID_Hash == device_hash for log in recent_logs
    )
    device_reputation = 0.85 if known_device else 0.45

    feature_vector = {
        "Age":                     now.year - int(citizen.DOB[:4]),
        "State_of_Origin":         _encode_state(citizen.State_of_Origin or "FCT"),
        "Gender":                  0 if citizen.Gender == "F" else 1,
        "NIN_Linkage_Count":       active_links,
        "Login_Frequency":         min(login_freq_24h + 1, 30),
        "Geographic_Velocity":     geo_velocity,
        "Device_Reputation_Score": device_reputation,
        "Sector_Conflict_Flag":    sector_conflict,
        "Failed_Auth_Attempts":    failed_attempts,
        "Access_Hour":             access_hour,
        "BVN_Status":              sector_flags["Banking"],
        "NHIA_Status":             sector_flags["Health"],
        "JAMB_Status":             sector_flags["Education"],
        "FRSC_Status":             sector_flags["Transport"],
        "Voter_ID_Status":         sector_flags["Telecoms"],
        "Age_Consistency_Score":   age_consistency,
        "Name_Mismatch_Flag":      name_mismatch,
        "Sector_Access_Frequency": min(login_freq_24h * 2, 60),
    }

    # ── Step 3: ML Inference ─────────────────────────────────────────
    risk_score, prediction = _engine.predict(feature_vector)

    # ── Step 4: Log to DB ────────────────────────────────────────────
    crud.telemetry.log_event(
        db,
        nin                 = nin,
        sector_requesting   = payload.Sector_Name,
        location_state      = payload.Location_State,
        geographic_velocity = geo_velocity,
        login_frequency_24h = login_freq_24h + 1,
        device_id_hash      = device_hash,
        access_hour         = access_hour,
        risk_score          = risk_score,
        ml_prediction       = prediction,
    )

    crud.audit.log(
        db,
        nin          = nin,
        agency_id    = agency.Agency_ID,
        action_taken = "VERIFY_REQUEST",
        justification= f"Sector={payload.Sector_Name} "
                       f"State={payload.Location_State} "
                       f"Prediction={prediction} "
                       f"Score={risk_score:.4f}",
    )
    db.commit()

    # ── Step 5: Build response ───────────────────────────────────────
    action  = "FLAGGED" if prediction == "High_Risk" else "CLEARED"
    message = (
        "HIGH RISK: Identity flagged for immediate review."
        if prediction == "High_Risk"
        else "LOW RISK: Identity cleared for sector access."
    )

    logger.info(
        "NIN=%s Agency=%s Score=%.4f Prediction=%s",
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