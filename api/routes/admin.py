"""
NINCore API — Admin Routes
============================
Administrative endpoints for the governance dashboard.

Routes:
  GET  /api/v1/admin/citizen/{nin}      -- Citizen profile lookup
  GET  /api/v1/admin/sectors/{nin}      -- Sector links for a NIN
  POST /api/v1/admin/revoke-sector      -- Revoke a sector linkage
  GET  /api/v1/admin/api-keys           -- List all registered API keys
  GET  /api/v1/admin/dashboard/kpis     -- Headline KPI metrics
  GET  /api/v1/admin/dashboard/risk-by-state  -- Risk heatmap data
  GET  /api/v1/admin/dashboard/high-risk-nins -- Flagged entities feed
  GET  /api/v1/admin/high-risk-events   -- Recent high risk telemetry
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database.db import get_db
from database import crud
from database.models import APIKey
from api.middleware.auth import get_verified_agency
from api.schemas.request import RevokeRequest
from api.schemas.response import (
    CitizenProfileResponse,
    SectorLinkResponse,
    APIKeyResponse,
    DashboardKPIResponse,
    TelemetryLogResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/citizen/{nin}",
    response_model=CitizenProfileResponse,
    summary="Look up citizen profile by NIN",
    tags=["Admin"],
)
def get_citizen(
    nin: int,
    db: Session = Depends(get_db),
    agency: APIKey = Depends(get_verified_agency),
):
    """Returns the core identity profile for a NIN from Citizen_Registry."""
    citizen = crud.citizen.get_by_nin(db, nin=nin)
    if not citizen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NIN {nin} not found.",
        )

    crud.audit.log(
        db,
        nin          = nin,
        agency_id    = agency.Agency_ID,
        action_taken = "ADMIN_VIEW",
        justification= f"Citizen profile accessed by {agency.Agency_ID}",
    )
    db.commit()

    logger.info("Citizen NIN=%s accessed by %s", nin, agency.Agency_ID)
    return citizen


@router.get(
    "/sectors/{nin}",
    response_model=List[SectorLinkResponse],
    summary="Get all sector linkages for a NIN",
    tags=["Admin"],
)
def get_sectors(
    nin: int,
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db),
    agency: APIKey = Depends(get_verified_agency),
):
    """
    Returns all sector linkages for a NIN from Sector_Mapping.
    Set active_only=false to include revoked links.
    """
    if not crud.citizen.exists(db, nin=nin):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NIN {nin} not found.",
        )

    links = crud.sector.get_by_nin(db, nin=nin, active_only=active_only)

    crud.audit.log(
        db,
        nin          = nin,
        agency_id    = agency.Agency_ID,
        action_taken = "SECTOR_VIEW",
        justification= f"Sector links viewed by {agency.Agency_ID}",
    )
    db.commit()

    return links


@router.post(
    "/revoke-sector",
    summary="Revoke a sector linkage for a NIN",
    tags=["Admin"],
)
def revoke_sector(
    payload: RevokeRequest,
    db: Session = Depends(get_db),
    agency: APIKey = Depends(get_verified_agency),
):
    """
    Marks a sector linkage as Revoked in Sector_Mapping.
    Logs the revocation action to System_Audit with justification.
    """
    if not crud.citizen.exists(db, nin=payload.NIN):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NIN {payload.NIN} not found.",
        )

    updated = crud.sector.revoke(
        db, nin=payload.NIN, sector_name=payload.Sector_Name
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active {payload.Sector_Name} link found for NIN {payload.NIN}.",
        )

    crud.audit.log(
        db,
        nin          = payload.NIN,
        agency_id    = agency.Agency_ID,
        action_taken = "REVOKE_SECTOR_LINK",
        justification= payload.Justification,
    )
    db.commit()

    logger.info(
        "Sector link REVOKED: NIN=%s Sector=%s by %s",
        payload.NIN, payload.Sector_Name, agency.Agency_ID,
    )
    return {
        "status":  "success",
        "message": f"{payload.Sector_Name} link revoked for NIN {payload.NIN}.",
    }


@router.get(
    "/api-keys",
    response_model=List[APIKeyResponse],
    summary="List all registered sector API keys",
    tags=["Admin"],
)
def list_api_keys(
    db: Session = Depends(get_db),
    agency: APIKey = Depends(get_verified_agency),
):
    """Returns all API key records. Used by the admin dashboard."""
    keys = crud.apikey.get_all(db)
    logger.info("API keys listed by %s", agency.Agency_ID)
    return keys


@router.get(
    "/dashboard/kpis",
    response_model=DashboardKPIResponse,
    summary="Get headline KPI metrics for the dashboard",
    tags=["Admin"],
)
def get_dashboard_kpis(
    db: Session = Depends(get_db),
    agency: APIKey = Depends(get_verified_agency),
):
    """Returns the four headline KPIs for the dashboard overview page."""
    kpis = crud.dashboard.system_kpis(db)
    return kpis


@router.get(
    "/dashboard/risk-by-state",
    summary="Get average risk score grouped by state",
    tags=["Admin"],
)
def get_risk_by_state(
    db: Session = Depends(get_db),
    agency: APIKey = Depends(get_verified_agency),
):
    """Powers the National Risk Heatmap on the dashboard."""
    return crud.dashboard.risk_by_state(db)


@router.get(
    "/dashboard/high-risk-nins",
    summary="Get NINs with highest average risk score",
    tags=["Admin"],
)
def get_high_risk_nins(
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    agency: APIKey = Depends(get_verified_agency),
):
    """Powers the Flagged Entities table on the dashboard."""
    return crud.dashboard.recent_high_risk_nins(db, hours=hours, limit=limit)


@router.get(
    "/high-risk-events",
    response_model=List[TelemetryLogResponse],
    summary="Get recent high risk telemetry events",
    tags=["Admin"],
)
def get_high_risk_events(
    threshold: float = Query(default=0.7, ge=0.0, le=1.0),
    limit: int = Query(default=100, ge=1, le=500),
    since_hours: Optional[int] = Query(default=24),
    db: Session = Depends(get_db),
    agency: APIKey = Depends(get_verified_agency),
):
    """Returns recent telemetry events above the risk threshold."""
    return crud.telemetry.get_high_risk_events(
        db,
        threshold   = threshold,
        limit       = limit,
        since_hours = since_hours,
    )