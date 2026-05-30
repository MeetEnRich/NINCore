"""
NINCore SQLAlchemy ORM Models
================================
Mirrors the 5 SQLite tables created by scripts/setup_database.py.

Tables:
  1. CitizenRegistry   → Citizen_Registry
  2. SectorMapping     → Sector_Mapping
  3. RiskTelemetry     → Risk_Telemetry
  4. SystemAudit       → System_Audit
  5. APIKey            → API_Keys

All models use __table_args__ = {"extend_existing": True} so they are
safe to import in multiple modules without collision.

Relationships are declared for convenience (back_populates) but are
lazy-loaded by default — they never fire unexpected queries.
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from database.db import Base


# ── 1. CitizenRegistry ────────────────────────────────────────────────
class CitizenRegistry(Base):
    """
    Master NIN identity record.
    One row per citizen; NIN is the primary key and anchor for all
    other tables.
    """
    __tablename__ = "Citizen_Registry"
    __table_args__ = (
        CheckConstraint("Gender IN ('M', 'F')", name="ck_citizen_gender"),
        {"extend_existing": True},
    )

    NIN             = Column(BigInteger, primary_key=True, index=True)
    Full_Name       = Column(String(100), nullable=False)
    DOB             = Column(String(10),  nullable=False)   # ISO date: YYYY-MM-DD
    Gender          = Column(String(1),   nullable=False)
    State_of_Origin = Column(String(50),  nullable=True)
    Biometric_Hash  = Column(String(255), nullable=False)
    Created_At      = Column(DateTime, default=datetime.utcnow)

    # Relationships (lazy-loaded — safe to leave unloaded)
    sector_links    = relationship(
        "SectorMapping",
        back_populates="citizen",
        cascade="all, delete-orphan",
        lazy="select",
    )
    telemetry_logs  = relationship(
        "RiskTelemetry",
        back_populates="citizen",
        cascade="all, delete-orphan",
        lazy="select",
    )
    audit_logs      = relationship(
        "SystemAudit",
        back_populates="citizen",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self):
        return (
            f"<CitizenRegistry NIN={self.NIN} "
            f"Name='{self.Full_Name}' "
            f"State='{self.State_of_Origin}'>"
        )


# ── 2. SectorMapping ─────────────────────────────────────────────────
class SectorMapping(Base):
    """
    NIN-to-sector linkage bridge.
    One row per (NIN, Sector) pair; stores the sector-specific ID
    (BVN number, NHIA ID, JAMB number, etc.) and linkage metadata.
    """
    __tablename__ = "Sector_Mapping"
    __table_args__ = (
        CheckConstraint(
            "Sector_Name IN ('Banking','Health','Education','Transport','Telecoms')",
            name="ck_sector_name",
        ),
        CheckConstraint(
            "Linkage_Status IN ('Active','Revoked')",
            name="ck_linkage_status",
        ),
        Index("idx_sector_mapping_nin", "NIN"),
        {"extend_existing": True},
    )

    Link_ID        = Column(Integer, primary_key=True, autoincrement=True)
    NIN            = Column(
        BigInteger,
        ForeignKey("Citizen_Registry.NIN", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    Sector_Name    = Column(String(50),  nullable=False)
    Sector_ID      = Column(String(50),  nullable=False)
    Linkage_Date   = Column(String(10),  nullable=True)   # ISO date
    Linkage_Status = Column(String(20),  default="Active")

    citizen = relationship("CitizenRegistry", back_populates="sector_links")

    def __repr__(self):
        return (
            f"<SectorMapping Link_ID={self.Link_ID} "
            f"NIN={self.NIN} "
            f"Sector='{self.Sector_Name}' "
            f"Status='{self.Linkage_Status}'>"
        )


# ── 3. RiskTelemetry ─────────────────────────────────────────────────
class RiskTelemetry(Base):
    """
    Behavioral event log — the runtime feed for the ML risk engine.

    Every identity verification request processed by the API writes
    one row here with the extracted feature vector, the computed
    risk score, and the model's prediction.

    This table is NOT seeded; it is populated at runtime.
    """
    __tablename__ = "Risk_Telemetry"
    __table_args__ = (
        CheckConstraint("Access_Hour BETWEEN 0 AND 23", name="ck_access_hour"),
        CheckConstraint("Risk_Score BETWEEN 0.0 AND 1.0", name="ck_risk_score"),
        CheckConstraint(
            "ML_Prediction IN ('Low_Risk','High_Risk')",
            name="ck_ml_prediction",
        ),
        Index("idx_telemetry_nin",       "NIN"),
        Index("idx_telemetry_timestamp", "Timestamp"),
        {"extend_existing": True},
    )

    Log_ID              = Column(Integer, primary_key=True, autoincrement=True)
    NIN                 = Column(
        BigInteger,
        ForeignKey("Citizen_Registry.NIN", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    Sector_Requesting   = Column(String(50),  nullable=True)
    Timestamp           = Column(DateTime,    default=datetime.utcnow)
    Location_State      = Column(String(50),  nullable=True)
    Geographic_Velocity = Column(Float,       nullable=True)
    Login_Frequency_24h = Column(Integer,     nullable=True)
    Device_ID_Hash      = Column(String(255), nullable=True)
    Access_Hour         = Column(Integer,     nullable=True)
    Risk_Score          = Column(Float,       nullable=True)
    ML_Prediction       = Column(String(10),  nullable=True)

    citizen = relationship("CitizenRegistry", back_populates="telemetry_logs")

    def __repr__(self):
        return (
            f"<RiskTelemetry Log_ID={self.Log_ID} "
            f"NIN={self.NIN} "
            f"Risk={self.Risk_Score:.3f} "
            f"Pred='{self.ML_Prediction}'>"
        )


# ── 4. SystemAudit ───────────────────────────────────────────────────
class SystemAudit(Base):
    """
    Tamper-evident governance trail.

    Every administrative action and agency data-access event is
    appended here. Rows are intentionally append-only; the application
    layer must never UPDATE or DELETE rows from this table.
    """
    __tablename__ = "System_Audit"
    __table_args__ = (
        Index("idx_audit_nin",       "NIN"),
        Index("idx_audit_timestamp", "Timestamp"),
        {"extend_existing": True},
    )

    Audit_ID      = Column(Integer, primary_key=True, autoincrement=True)
    NIN           = Column(
        BigInteger,
        ForeignKey("Citizen_Registry.NIN", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    Agency_ID     = Column(String(50),  nullable=True)
    Admin_UserID  = Column(String(50),  nullable=True)
    Action_Taken  = Column(String(100), nullable=True)
    Justification = Column(Text,        nullable=True)
    Timestamp     = Column(DateTime,    default=datetime.utcnow)

    citizen = relationship("CitizenRegistry", back_populates="audit_logs")

    def __repr__(self):
        return (
            f"<SystemAudit Audit_ID={self.Audit_ID} "
            f"NIN={self.NIN} "
            f"Action='{self.Action_Taken}' "
            f"Agency='{self.Agency_ID}'>"
        )


# ── 5. APIKey ─────────────────────────────────────────────────────────
class APIKey(Base):
    """
    Sector agency API key registry.

    Each sector agency is issued exactly one API key.  The middleware
    layer (api/middleware/auth.py) validates incoming requests against
    this table.

    Note: API_Key values are stored in plaintext here because this is a
    prototype. A production system would store only a salted hash.
    """
    __tablename__ = "API_Keys"
    __table_args__ = (
        CheckConstraint(
            "Status IN ('Active','Revoked')",
            name="ck_apikey_status",
        ),
        Index("idx_apikeys_agency", "Agency_ID"),
        {"extend_existing": True},
    )

    Key_ID      = Column(Integer,    primary_key=True, autoincrement=True)
    Agency_ID   = Column(String(50), nullable=False, unique=True)
    Sector_Name = Column(String(50), nullable=False)
    API_Key     = Column(String(64), nullable=False, unique=True)
    Status      = Column(String(10), default="Active")
    Created_At  = Column(DateTime,   default=datetime.utcnow)
    Last_Used   = Column(DateTime,   nullable=True)

    def __repr__(self):
        return (
            f"<APIKey Key_ID={self.Key_ID} "
            f"Agency='{self.Agency_ID}' "
            f"Sector='{self.Sector_Name}' "
            f"Status='{self.Status}'>"
        )