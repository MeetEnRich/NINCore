"""
NINCore Database Setup
========================
Creates the SQLite database and all 4 tables as defined in the ERD (Section 3.6).

Tables:
  1. Citizen_Registry   -- Master NIN identity records
  2. Sector_Mapping     -- NIN-to-sector linkage bridge
  3. Risk_Telemetry     -- Behavioral event log (feeds ML model)
  4. System_Audit       -- Tamper-evident governance trail

Run:
    python scripts/setup_database.py
"""

import os
import sqlite3

# -- Path config ------------------------------------------------------
BASE_DIR  = os.path.join(os.path.dirname(__file__), "..")
DB_DIR    = os.path.join(BASE_DIR, "database")
DB_PATH   = os.path.join(DB_DIR, "nincore.db")


# -- Table definitions ------------------------------------------------
TABLES = {

    "Citizen_Registry": """
        CREATE TABLE IF NOT EXISTS Citizen_Registry (
            NIN              BIGINT       PRIMARY KEY,
            Full_Name        VARCHAR(100) NOT NULL,
            DOB              DATE         NOT NULL,
            Gender           CHAR(1)      NOT NULL CHECK (Gender IN ('M', 'F')),
            State_of_Origin  VARCHAR(50),
            Biometric_Hash   VARCHAR(255) NOT NULL,
            Created_At       DATETIME     DEFAULT CURRENT_TIMESTAMP
        );
    """,

    "Sector_Mapping": """
        CREATE TABLE IF NOT EXISTS Sector_Mapping (
            Link_ID         INTEGER      PRIMARY KEY AUTOINCREMENT,
            NIN             BIGINT       NOT NULL,
            Sector_Name     VARCHAR(50)  NOT NULL
                                CHECK (Sector_Name IN (
                                    'Banking', 'Health',
                                    'Education', 'Transport', 'Telecoms'
                                )),
            Sector_ID       VARCHAR(50)  NOT NULL,
            Linkage_Date    DATE,
            Linkage_Status  VARCHAR(20)  DEFAULT 'Active'
                                CHECK (Linkage_Status IN ('Active', 'Revoked')),
            FOREIGN KEY (NIN) REFERENCES Citizen_Registry(NIN)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
    """,

    "Risk_Telemetry": """
        CREATE TABLE IF NOT EXISTS Risk_Telemetry (
            Log_ID                INTEGER      PRIMARY KEY AUTOINCREMENT,
            NIN                   BIGINT       NOT NULL,
            Sector_Requesting     VARCHAR(50),
            Timestamp             DATETIME     DEFAULT CURRENT_TIMESTAMP,
            Location_State        VARCHAR(50),
            Geographic_Velocity   FLOAT,
            Login_Frequency_24h   INTEGER,
            Device_ID_Hash        VARCHAR(255),
            Access_Hour           INTEGER      CHECK (Access_Hour BETWEEN 0 AND 23),
            Risk_Score            FLOAT        CHECK (Risk_Score BETWEEN 0.0 AND 1.0),
            ML_Prediction         VARCHAR(10)
                                CHECK (ML_Prediction IN ('Low_Risk', 'High_Risk')),
            FOREIGN KEY (NIN) REFERENCES Citizen_Registry(NIN)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
    """,

    "System_Audit": """
        CREATE TABLE IF NOT EXISTS System_Audit (
            Audit_ID      INTEGER      PRIMARY KEY AUTOINCREMENT,
            NIN           BIGINT       NOT NULL,
            Agency_ID     VARCHAR(50),
            Admin_UserID  VARCHAR(50),
            Action_Taken  VARCHAR(100),
            Justification TEXT,
            Timestamp     DATETIME     DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (NIN) REFERENCES Citizen_Registry(NIN)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
    """,

    # API key management table (supports the dashboard admin page)
    "API_Keys": """
        CREATE TABLE IF NOT EXISTS API_Keys (
            Key_ID        INTEGER      PRIMARY KEY AUTOINCREMENT,
            Agency_ID     VARCHAR(50)  NOT NULL UNIQUE,
            Sector_Name   VARCHAR(50)  NOT NULL,
            API_Key       VARCHAR(64)  NOT NULL UNIQUE,
            Status        VARCHAR(10)  DEFAULT 'Active'
                              CHECK (Status IN ('Active', 'Revoked')),
            Created_At    DATETIME     DEFAULT CURRENT_TIMESTAMP,
            Last_Used     DATETIME
        );
    """,
}

# -- Indexes (for query performance) ----------------------------------
INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_sector_mapping_nin  ON Sector_Mapping(NIN);",
    "CREATE INDEX IF NOT EXISTS idx_telemetry_nin       ON Risk_Telemetry(NIN);",
    "CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON Risk_Telemetry(Timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_audit_nin           ON System_Audit(NIN);",
    "CREATE INDEX IF NOT EXISTS idx_audit_timestamp     ON System_Audit(Timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_apikeys_agency      ON API_Keys(Agency_ID);",
]


# -- Setup function ----------------------------------------------------
def setup_database() -> None:
    os.makedirs(DB_DIR, exist_ok=True)

    print(f"Setting up database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable foreign key enforcement (SQLite requires this explicitly)
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create tables
    print("\nCreating tables...")
    for name, ddl in TABLES.items():
        cursor.execute(ddl)
        print(f"  [OK] {name}")

    # Create indexes
    print("\nCreating indexes...")
    for idx_sql in INDEXES:
        cursor.execute(idx_sql)
        idx_name = idx_sql.split("IF NOT EXISTS ")[1].split(" ON")[0]
        print(f"  [OK] {idx_name}")

    conn.commit()

    # -- Verify --
    print("\nVerifying schema...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"  Tables found: {tables}")

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        cols = cursor.fetchall()
        print(f"  {table}: {len(cols)} columns")

    conn.close()

    size_kb = os.path.getsize(DB_PATH) / 1024
    print(f"\nDatabase created successfully.")
    print(f"  Path : {DB_PATH}")
    print(f"  Size : {size_kb:.1f} KB")


# -- Entry point ------------------------------------------------------
if __name__ == "__main__":
    # Safety check — warn if DB already exists
    if os.path.exists(DB_PATH):
        confirm = input(
            f"\nDatabase already exists at {DB_PATH}.\n"
            "Re-running will not drop existing data (CREATE IF NOT EXISTS).\n"
            "Continue? [y/N]: "
        ).strip().lower()
        if confirm != "y":
            print("Aborted.")
            exit(0)

    setup_database()