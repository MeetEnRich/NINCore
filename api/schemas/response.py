"""
NINCore API — Response Schemas
================================
Pydantic models that define every API response structure.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RiskAssessmentResponse(BaseModel):
    """
    Response for POST /api/v1/verify-risk
    """
    NIN:              int
    Risk_Score:       float = Field(..., ge=0.0, le=1.0)
    ML_Prediction:    str   # "Low_Risk" or "High_Risk"
    Confidence_Pct:   float = Field(..., description="Risk score as percentage")
    Sector_Requested: str
    Location_State:   str
    Timestamp:        datetime
    Action:           str   # "CLEARED" or "FLAGGED"
    Message:          str

    model_config = {"from_attributes": True}


class CitizenProfileResponse(BaseModel):
    """
    Citizen identity summary returned by admin lookup.
    """
    NIN:             int
    Full_Name:       str
    DOB:             str
    Gender:          str
    State_of_Origin: str

    model_config = {"from_attributes": True}


class SectorLinkResponse(BaseModel):
    """
    Single sector linkage record.
    """
    Sector_Name:    str
    Sector_ID:      str
    Linkage_Date:   Optional[str]
    Linkage_Status: str

    model_config = {"from_attributes": True}


class AuditLogResponse(BaseModel):
    """
    Single audit log entry.
    """
    Audit_ID:     int
    NIN:          int
    Agency_ID:    Optional[str]
    Action_Taken: Optional[str]
    Timestamp:    datetime

    model_config = {"from_attributes": True}


class TelemetryLogResponse(BaseModel):
    """
    Single telemetry event entry.
    """
    Log_ID:             int
    NIN:                int
    Sector_Requesting:  Optional[str]
    Risk_Score:         Optional[float]
    ML_Prediction:      Optional[str]
    Timestamp:          datetime

    model_config = {"from_attributes": True}


class APIKeyResponse(BaseModel):
    """
    API key record for admin dashboard.
    """
    Key_ID:      int
    Agency_ID:   str
    Sector_Name: str
    Status:      str
    Created_At:  datetime
    Last_Used:   Optional[datetime]

    model_config = {"from_attributes": True}


class DashboardKPIResponse(BaseModel):
    """
    Headline KPI metrics for the dashboard overview page.
    """
    total_citizens:       int
    total_sectors_linked: int
    high_risk_events:     int
    audit_entries:        int


class HealthResponse(BaseModel):
    """
    GET /health — system health check.
    """
    status:   str
    database: str
    model:    str
    version:  str