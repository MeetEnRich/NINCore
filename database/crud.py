"""
NINCore CRUD Operations
=========================
All database read/write operations for the NINCore system, organized
by table. Every function accepts a SQLAlchemy Session as its first
argument so callers control transaction boundaries.

Modules:
  citizen   -- CitizenRegistry queries
  sector    -- SectorMapping queries
  telemetry -- RiskTelemetry writes (runtime event logging)
  audit     -- SystemAudit writes (governance trail, append-only)
  apikey    -- APIKey lookups (auth middleware)
  dashboard -- Aggregate queries for the Streamlit dashboard

Usage example:
    from database.db import get_db_context
    from database import crud

    with get_db_context() as db:
        citizen = crud.citizen.get_by_nin(db, nin=12345678901)
        print(citizen)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from database.models import (
    APIKey,
    CitizenRegistry,
    RiskTelemetry,
    SectorMapping,
    SystemAudit,
)


# ══════════════════════════════════════════════════════════════════════
# CITIZEN REGISTRY
# ══════════════════════════════════════════════════════════════════════

class _CitizenCRUD:
    """Read operations for the Citizen_Registry table.

    The registry is seeded once by seed_database.py; the API layer
    reads it but never directly modifies it (write operations are
    intentionally omitted from the public interface to guard data
    integrity in this prototype).
    """

    def get_by_nin(self, db: Session, nin: int) -> Optional[CitizenRegistry]:
        """Return the citizen record for the given NIN, or None."""
        return db.query(CitizenRegistry).filter(CitizenRegistry.NIN == nin).first()

    def exists(self, db: Session, nin: int) -> bool:
        """Return True if a citizen record exists for this NIN."""
        return (
            db.query(CitizenRegistry.NIN)
            .filter(CitizenRegistry.NIN == nin)
            .first()
            is not None
        )

    def get_many(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        state: Optional[str] = None,
        gender: Optional[str] = None,
    ) -> List[CitizenRegistry]:
        """
        Paginated fetch with optional demographic filters.
        Used by the admin dashboard for bulk exploration.
        """
        q = db.query(CitizenRegistry)
        if state:
            q = q.filter(CitizenRegistry.State_of_Origin == state)
        if gender:
            q = q.filter(CitizenRegistry.Gender == gender)
        return q.offset(skip).limit(limit).all()

    def count(self, db: Session) -> int:
        """Total number of registered citizens."""
        return db.query(func.count(CitizenRegistry.NIN)).scalar()


# ══════════════════════════════════════════════════════════════════════
# SECTOR MAPPING
# ══════════════════════════════════════════════════════════════════════

class _SectorCRUD:
    """Read and write operations for the Sector_Mapping (linkage) table."""

    def get_by_nin(
        self,
        db: Session,
        nin: int,
        *,
        active_only: bool = True,
    ) -> List[SectorMapping]:
        """Return all sector links for a NIN.

        Args:
            active_only: If True (default), only return 'Active' links.
        """
        q = db.query(SectorMapping).filter(SectorMapping.NIN == nin)
        if active_only:
            q = q.filter(SectorMapping.Linkage_Status == "Active")
        return q.all()

    def get_sector_id(
        self,
        db: Session,
        nin: int,
        sector_name: str,
    ) -> Optional[str]:
        """Return the sector-specific ID for a given NIN + sector, or None."""
        row = (
            db.query(SectorMapping.Sector_ID)
            .filter(
                SectorMapping.NIN == nin,
                SectorMapping.Sector_Name == sector_name,
                SectorMapping.Linkage_Status == "Active",
            )
            .first()
        )
        return row.Sector_ID if row else None

    def count_active_links(self, db: Session, nin: int) -> int:
        """Number of active sector links for a NIN (used in feature vector)."""
        return (
            db.query(func.count(SectorMapping.Link_ID))
            .filter(
                SectorMapping.NIN == nin,
                SectorMapping.Linkage_Status == "Active",
            )
            .scalar()
        )

    def sector_distribution(self, db: Session) -> List[dict]:
        """
        Returns a list of {sector_name, count} dicts, ordered by count desc.
        Used by the dashboard overview page.
        """
        rows = (
            db.query(
                SectorMapping.Sector_Name,
                func.count(SectorMapping.Link_ID).label("count"),
            )
            .filter(SectorMapping.Linkage_Status == "Active")
            .group_by(SectorMapping.Sector_Name)
            .order_by(desc("count"))
            .all()
        )
        return [{"sector": r.Sector_Name, "count": r.count} for r in rows]

    def revoke(self, db: Session, nin: int, sector_name: str) -> int:
        """
        Mark a sector link as 'Revoked'.
        Returns the number of rows updated (0 or 1).
        """
        updated = (
            db.query(SectorMapping)
            .filter(
                SectorMapping.NIN == nin,
                SectorMapping.Sector_Name == sector_name,
                SectorMapping.Linkage_Status == "Active",
            )
            .update({"Linkage_Status": "Revoked"})
        )
        return updated


# ══════════════════════════════════════════════════════════════════════
# RISK TELEMETRY
# ══════════════════════════════════════════════════════════════════════

class _TelemetryCRUD:
    """Write and read operations for the Risk_Telemetry event log."""

    def log_event(
        self,
        db: Session,
        *,
        nin: int,
        sector_requesting: str,
        location_state: str,
        geographic_velocity: float,
        login_frequency_24h: int,
        device_id_hash: str,
        access_hour: int,
        risk_score: float,
        ml_prediction: str,
    ) -> RiskTelemetry:
        """
        Append one behavioral event to the telemetry log.
        Called by the API layer after every verification request.

        Returns the newly created (and committed) RiskTelemetry row.
        """
        row = RiskTelemetry(
            NIN                 = nin,
            Sector_Requesting   = sector_requesting,
            Location_State      = location_state,
            Geographic_Velocity = geographic_velocity,
            Login_Frequency_24h = login_frequency_24h,
            Device_ID_Hash      = device_id_hash,
            Access_Hour         = access_hour,
            Risk_Score          = risk_score,
            ML_Prediction       = ml_prediction,
        )
        db.add(row)
        db.flush()   # assign Log_ID without committing; caller commits
        return row

    def get_history(
        self,
        db: Session,
        nin: int,
        *,
        limit: int = 50,
    ) -> List[RiskTelemetry]:
        """Most recent telemetry events for a NIN, newest first."""
        return (
            db.query(RiskTelemetry)
            .filter(RiskTelemetry.NIN == nin)
            .order_by(desc(RiskTelemetry.Timestamp))
            .limit(limit)
            .all()
        )

    def get_login_frequency_24h(self, db: Session, nin: int) -> int:
        """
        Count verification events for this NIN in the last 24 hours.
        Used as a real-time feature when building the inference vector.
        """
        since = datetime.utcnow() - timedelta(hours=24)
        return (
            db.query(func.count(RiskTelemetry.Log_ID))
            .filter(
                RiskTelemetry.NIN == nin,
                RiskTelemetry.Timestamp >= since,
            )
            .scalar()
        )

    def get_last_event(
        self,
        db: Session,
        nin: int,
    ) -> Optional[RiskTelemetry]:
        """
        Most recent telemetry row for a NIN.
        Used to calculate geographic velocity between requests.
        """
        return (
            db.query(RiskTelemetry)
            .filter(RiskTelemetry.NIN == nin)
            .order_by(desc(RiskTelemetry.Timestamp))
            .first()
        )

    def get_high_risk_events(
        self,
        db: Session,
        *,
        threshold: float = 0.7,
        limit: int = 200,
        since_hours: Optional[int] = None,
    ) -> List[RiskTelemetry]:
        """
        Fetch recent high-risk events for the dashboard alert feed.

        Args:
            threshold:    Risk score cutoff (default 0.7, from Section 3.7.2).
            limit:        Max rows to return.
            since_hours:  If set, restrict to events within the last N hours.
        """
        q = (
            db.query(RiskTelemetry)
            .filter(RiskTelemetry.Risk_Score > threshold)
            .order_by(desc(RiskTelemetry.Timestamp))
        )
        if since_hours:
            since = datetime.utcnow() - timedelta(hours=since_hours)
            q = q.filter(RiskTelemetry.Timestamp >= since)
        return q.limit(limit).all()

    def risk_score_distribution(self, db: Session) -> List[dict]:
        """
        Returns a list of {prediction, count} for the dashboard KPIs.
        """
        rows = (
            db.query(
                RiskTelemetry.ML_Prediction,
                func.count(RiskTelemetry.Log_ID).label("count"),
            )
            .group_by(RiskTelemetry.ML_Prediction)
            .all()
        )
        return [{"prediction": r.ML_Prediction, "count": r.count} for r in rows]

    def count_events_by_sector(self, db: Session) -> List[dict]:
        """Per-sector verification volume — used by the dashboard charts."""
        rows = (
            db.query(
                RiskTelemetry.Sector_Requesting,
                func.count(RiskTelemetry.Log_ID).label("count"),
            )
            .group_by(RiskTelemetry.Sector_Requesting)
            .order_by(desc("count"))
            .all()
        )
        return [{"sector": r.Sector_Requesting, "count": r.count} for r in rows]


# ══════════════════════════════════════════════════════════════════════
# SYSTEM AUDIT
# ══════════════════════════════════════════════════════════════════════

class _AuditCRUD:
    """
    Append-only audit log operations.

    IMPORTANT: This table must never be updated or deleted from.
    Rows represent the tamper-evident governance record required
    under Section 3.7.2 and the NDPA 2023 audit mandate.
    """

    def log(
        self,
        db: Session,
        *,
        nin: int,
        agency_id: str,
        action_taken: str,
        admin_user_id: Optional[str] = None,
        justification: Optional[str] = None,
    ) -> SystemAudit:
        """
        Append one governance event to the audit trail.

        Args:
            nin:           NIN being accessed/actioned.
            agency_id:     Agency or system component taking the action.
            action_taken:  Short description (e.g. 'VERIFY_REQUEST',
                           'REVOKE_SECTOR_LINK', 'ADMIN_VIEW').
            admin_user_id: Dashboard user, if a human initiated the action.
            justification: Free-text reason (required for sensitive actions).

        Returns the newly created SystemAudit row.
        """
        row = SystemAudit(
            NIN           = nin,
            Agency_ID     = agency_id,
            Admin_UserID  = admin_user_id,
            Action_Taken  = action_taken,
            Justification = justification,
        )
        db.add(row)
        db.flush()
        return row

    def get_by_nin(
        self,
        db: Session,
        nin: int,
        *,
        limit: int = 100,
    ) -> List[SystemAudit]:
        """Full audit history for one NIN, newest first."""
        return (
            db.query(SystemAudit)
            .filter(SystemAudit.NIN == nin)
            .order_by(desc(SystemAudit.Timestamp))
            .limit(limit)
            .all()
        )

    def get_recent(
        self,
        db: Session,
        *,
        limit: int = 200,
        agency_id: Optional[str] = None,
    ) -> List[SystemAudit]:
        """
        Most recent audit rows, optionally filtered by agency.
        Used by the Governance Trail dashboard page.
        """
        q = db.query(SystemAudit).order_by(desc(SystemAudit.Timestamp))
        if agency_id:
            q = q.filter(SystemAudit.Agency_ID == agency_id)
        return q.limit(limit).all()

    def count(self, db: Session) -> int:
        """Total number of audit log entries."""
        return db.query(func.count(SystemAudit.Audit_ID)).scalar()


# ══════════════════════════════════════════════════════════════════════
# API KEYS
# ══════════════════════════════════════════════════════════════════════

class _APIKeyCRUD:
    """API key lookup operations for the auth middleware."""

    def get_by_key(self, db: Session, api_key: str) -> Optional[APIKey]:
        """
        Look up an API key row by the key value itself.
        Returns None if not found or if the key is Revoked.
        Used by api/middleware/auth.py on every incoming request.
        """
        return (
            db.query(APIKey)
            .filter(
                APIKey.API_Key == api_key,
                APIKey.Status  == "Active",
            )
            .first()
        )

    def get_by_agency(self, db: Session, agency_id: str) -> Optional[APIKey]:
        """Fetch the API key record for a specific agency."""
        return (
            db.query(APIKey)
            .filter(APIKey.Agency_ID == agency_id)
            .first()
        )

    def get_all(self, db: Session) -> List[APIKey]:
        """All registered API keys — used by the admin dashboard."""
        return db.query(APIKey).order_by(APIKey.Sector_Name).all()

    def update_last_used(self, db: Session, api_key: str) -> None:
        """
        Stamp Last_Used on the API key row after a successful auth check.
        The caller is responsible for committing the session.
        """
        db.query(APIKey).filter(APIKey.API_Key == api_key).update(
            {"Last_Used": datetime.utcnow()}
        )

    def revoke(self, db: Session, agency_id: str) -> bool:
        """
        Revoke all active keys for an agency.
        Returns True if at least one row was updated.
        """
        updated = (
            db.query(APIKey)
            .filter(
                APIKey.Agency_ID == agency_id,
                APIKey.Status    == "Active",
            )
            .update({"Status": "Revoked"})
        )
        return updated > 0


# ══════════════════════════════════════════════════════════════════════
# DASHBOARD AGGREGATES
# ══════════════════════════════════════════════════════════════════════

class _DashboardCRUD:
    """
    Composite / aggregate queries that span multiple tables.
    Used exclusively by the Streamlit dashboard pages.
    """

    def system_kpis(self, db: Session) -> dict:
        """
        Returns the four headline KPI metrics displayed at the top of
        the Overview page.

        Returns:
            {
                "total_citizens":    int,
                "total_sectors_linked": int,
                "high_risk_events":  int,   # all-time
                "audit_entries":     int,
            }
        """
        total_citizens      = db.query(func.count(CitizenRegistry.NIN)).scalar()
        total_sector_links  = (
            db.query(func.count(SectorMapping.Link_ID))
            .filter(SectorMapping.Linkage_Status == "Active")
            .scalar()
        )
        high_risk_count     = (
            db.query(func.count(RiskTelemetry.Log_ID))
            .filter(RiskTelemetry.ML_Prediction == "High_Risk")
            .scalar()
        )
        audit_count         = db.query(func.count(SystemAudit.Audit_ID)).scalar()

        return {
            "total_citizens":       total_citizens      or 0,
            "total_sectors_linked": total_sector_links  or 0,
            "high_risk_events":     high_risk_count     or 0,
            "audit_entries":        audit_count         or 0,
        }

    def risk_by_state(self, db: Session) -> List[dict]:
        """
        Average risk score grouped by Location_State.
        Powers the National Risk Heatmap on the dashboard.

        Returns: [{state, avg_risk, event_count}, ...]
        """
        rows = (
            db.query(
                RiskTelemetry.Location_State,
                func.avg(RiskTelemetry.Risk_Score).label("avg_risk"),
                func.count(RiskTelemetry.Log_ID).label("event_count"),
            )
            .filter(RiskTelemetry.Location_State.isnot(None))
            .group_by(RiskTelemetry.Location_State)
            .order_by(desc("avg_risk"))
            .all()
        )
        return [
            {
                "state":        r.Location_State,
                "avg_risk":     round(r.avg_risk, 4) if r.avg_risk else 0.0,
                "event_count":  r.event_count,
            }
            for r in rows
        ]

    def recent_high_risk_nins(
        self,
        db: Session,
        *,
        limit: int = 20,
        hours: int = 24,
    ) -> List[dict]:
        """
        NINs with the highest average risk score over the last N hours.
        Powers the 'Flagged Entities' table on the dashboard.

        Returns: [{nin, avg_risk, event_count, last_seen}, ...]
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        rows = (
            db.query(
                RiskTelemetry.NIN,
                func.avg(RiskTelemetry.Risk_Score).label("avg_risk"),
                func.count(RiskTelemetry.Log_ID).label("event_count"),
                func.max(RiskTelemetry.Timestamp).label("last_seen"),
            )
            .filter(
                RiskTelemetry.Timestamp >= since,
                RiskTelemetry.ML_Prediction == "High_Risk",
            )
            .group_by(RiskTelemetry.NIN)
            .order_by(desc("avg_risk"))
            .limit(limit)
            .all()
        )
        return [
            {
                "nin":         r.NIN,
                "avg_risk":    round(r.avg_risk, 4),
                "event_count": r.event_count,
                "last_seen":   r.last_seen,
            }
            for r in rows
        ]

    def hourly_risk_volume(
        self,
        db: Session,
        *,
        hours: int = 24,
    ) -> List[dict]:
        """
        Event counts per hour for the last N hours.
        Powers the real-time activity timeline chart.

        Returns: [{hour, total_events, high_risk_events}, ...]
        """
        since = datetime.utcnow() - timedelta(hours=hours)

        # SQLite strftime for hour-level grouping
        rows = (
            db.query(
                func.strftime("%Y-%m-%d %H:00", RiskTelemetry.Timestamp).label("hour"),
                func.count(RiskTelemetry.Log_ID).label("total"),
                func.sum(
                    func.iif(RiskTelemetry.ML_Prediction == "High_Risk", 1, 0)
                ).label("high_risk"),
            )
            .filter(RiskTelemetry.Timestamp >= since)
            .group_by("hour")
            .order_by("hour")
            .all()
        )
        return [
            {
                "hour":       r.hour,
                "total":      r.total,
                "high_risk":  r.high_risk or 0,
            }
            for r in rows
        ]


# ══════════════════════════════════════════════════════════════════════
# Public singleton instances
# ══════════════════════════════════════════════════════════════════════
# Import pattern:
#   from database import crud
#   citizen = crud.citizen.get_by_nin(db, nin=...)

citizen   = _CitizenCRUD()
sector    = _SectorCRUD()
telemetry = _TelemetryCRUD()
audit     = _AuditCRUD()
apikey    = _APIKeyCRUD()
dashboard = _DashboardCRUD()