"""
NINCore API — Audit Routes
============================
Endpoints for querying the tamper-evident governance trail.

Routes:
  GET  /api/v1/audit/{nin}         -- Full audit history for a NIN
  GET  /api/v1/audit/recent        -- Most recent audit entries (all NINs)
  GET  /api/v1/audit/telemetry/{nin} -- Risk telemetry history for a NIN
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database.db import get_db
from database import crud
from database.models import APIKey
from api.middleware.auth import get_verified_agency
from api.schemas.response import AuditLogResponse, TelemetryLogResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/{nin}",
    response_model=List[AuditLogResponse],
    summary="Get full audit history for a NIN",
    tags=["Audit"],
)
def get_audit_by_nin(
    nin: int,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
    agency: APIKey = Depends(get_verified_agency),
):
    """
    Returns the complete governance audit trail for a given NIN.
    Ordered newest first.
    """
    if not crud.citizen.exists(db, nin=nin):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NIN {nin} not found.",
        )

    logs = crud.audit.get_by_nin(db, nin=nin, limit=limit)

    crud.audit.log(
        db,
        nin          = nin,
        agency_id    = agency.Agency_ID,
        action_taken = "AUDIT_VIEW",
        justification= f"Audit history viewed by {agency.Agency_ID}",
    )
    db.commit()

    logger.info("Audit history for NIN=%s viewed by %s", nin, agency.Agency_ID)
    return logs


@router.get(
    "/recent/all",
    response_model=List[AuditLogResponse],
    summary="Get most recent audit entries across all NINs",
    tags=["Audit"],
)
def get_recent_audit(
    limit: int = Query(default=100, ge=1, le=500),
    agency_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    agency: APIKey = Depends(get_verified_agency),
):
    """
    Returns the most recent audit log entries system-wide.
    Optionally filter by agency_id.
    Used by the Streamlit Governance Trail dashboard page.
    """
    logs = crud.audit.get_recent(db, limit=limit, agency_id=agency_id)
    logger.info(
        "Recent audit logs fetched by %s (limit=%s)", agency.Agency_ID, limit
    )
    return logs


@router.get(
    "/telemetry/{nin}",
    response_model=List[TelemetryLogResponse],
    summary="Get risk telemetry history for a NIN",
    tags=["Audit"],
)
def get_telemetry_by_nin(
    nin: int,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    agency: APIKey = Depends(get_verified_agency),
):
    """
    Returns the behavioral event log (Risk_Telemetry) for a NIN.
    Shows risk scores, ML predictions, and access patterns over time.
    """
    if not crud.citizen.exists(db, nin=nin):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NIN {nin} not found.",
        )

    logs = crud.telemetry.get_history(db, nin=nin, limit=limit)

    crud.audit.log(
        db,
        nin          = nin,
        agency_id    = agency.Agency_ID,
        action_taken = "TELEMETRY_VIEW",
        justification= f"Telemetry history viewed by {agency.Agency_ID}",
    )
    db.commit()

    logger.info("Telemetry for NIN=%s viewed by %s", nin, agency.Agency_ID)
    return logs