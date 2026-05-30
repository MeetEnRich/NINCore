"""
NINCore API — Request Schemas
================================
Pydantic models that validate and document every incoming request body.
FastAPI uses these for automatic input validation and OpenAPI docs.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class VerifyRiskRequest(BaseModel):
    """
    POST /api/v1/verify-risk
    Submitted by a sector agency to request a risk assessment for a NIN.
    """
    NIN: int = Field(
        ...,
        description="11-digit National Identification Number",
        ge=10_000_000_000,
        le=99_999_999_999,
    )
    Sector_Name: str = Field(
        ...,
        description="Requesting sector name",
    )
    Location_State: str = Field(
        ...,
        description="Nigerian state where the access is occurring",
    )
    Device_ID: str = Field(
        ...,
        description="Unique device identifier of the accessing device",
    )
    Activity_Type: Optional[str] = Field(
        default="VERIFICATION",
        description="Type of activity being performed",
    )

    @field_validator("Sector_Name")
    @classmethod
    def validate_sector(cls, v):
        allowed = {"Banking", "Health", "Education", "Transport", "Telecoms"}
        if v not in allowed:
            raise ValueError(f"Sector_Name must be one of {allowed}")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "NIN": 45829301827,
                "Sector_Name": "Banking",
                "Location_State": "Lagos",
                "Device_ID": "device-abc-123",
                "Activity_Type": "VERIFICATION",
            }
        }
    }


class AuditQueryRequest(BaseModel):
    """
    POST /api/v1/audit/query
    Admin query for audit logs by NIN.
    """
    NIN: int = Field(
        ...,
        ge=10_000_000_000,
        le=99_999_999_999,
    )
    limit: Optional[int] = Field(default=50, ge=1, le=500)


class RevokeRequest(BaseModel):
    """
    POST /api/v1/admin/revoke-sector
    Revoke a sector linkage for a NIN.
    """
    NIN: int = Field(
        ...,
        ge=10_000_000_000,
        le=99_999_999_999,
    )
    Sector_Name: str
    Justification: str = Field(
        ...,
        min_length=10,
        description="Reason for revocation (min 10 characters)",
    )

    @field_validator("Sector_Name")
    @classmethod
    def validate_sector(cls, v):
        allowed = {"Banking", "Health", "Education", "Transport", "Telecoms"}
        if v not in allowed:
            raise ValueError(f"Sector_Name must be one of {allowed}")
        return v