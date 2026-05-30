"""
NINCore Database Seeder
=========================
Reads the generated synthetic dataset and seeds the SQLite database.

Populates:
  1. Citizen_Registry   -- one row per NIN (core identity record)
  2. Sector_Mapping     -- sector linkages derived from binary status flags
  3. API_Keys           -- one key per sector agency (for API auth)

Note:
  Risk_Telemetry and System_Audit are NOT seeded here.
  They are populated at runtime as the API processes requests.

Run:
    python scripts/seed_database.py
"""

import os
import sqlite3
import hashlib
import secrets
import random
from datetime import date, timedelta

import pandas as pd
from faker import Faker

# -- Config -----------------------------------------------------------
SEED     = 42
random.seed(SEED)
fake     = Faker("en_NG")
fake.seed_instance(SEED)

BASE_DIR  = os.path.join(os.path.dirname(__file__), "..")
DB_PATH   = os.path.join(BASE_DIR, "database", "nincore.db")
CSV_PATH  = os.path.join(BASE_DIR, "data", "raw", "nincore_dataset.csv")

BATCH_SIZE = 1_000   # records per DB commit


# -- Sector config ----------------------------------------------------
# Maps dataset column -> (Sector_Name, Agency, ID prefix)
SECTOR_MAP = {
    "BVN_Status":      ("Banking",    "CBN",   "BVN"),
    "NHIA_Status":     ("Health",     "NHIA",  "NHIA"),
    "JAMB_Status":     ("Education",  "JAMB",  "JAMB"),
    "FRSC_Status":     ("Transport",  "FRSC",  "FRSC"),
    "Voter_ID_Status": ("Telecoms",   "INEC",  "VIN"),
}

# Sector agencies that will receive API keys
SECTOR_AGENCIES = [
    {"Agency_ID": "CBN_BANKING_001",   "Sector_Name": "Banking"},
    {"Agency_ID": "NHIA_HEALTH_001",   "Sector_Name": "Health"},
    {"Agency_ID": "JAMB_EDU_001",      "Sector_Name": "Education"},
    {"Agency_ID": "FRSC_TRANSPORT_001","Sector_Name": "Transport"},
    {"Agency_ID": "INEC_TELECOMS_001", "Sector_Name": "Telecoms"},
]


# -- Helpers ----------------------------------------------------------
def hash_biometric(nin: int) -> str:
    """Simulate a biometric hash from the NIN."""
    return hashlib.sha256(f"NINCORE_BIO_{nin}".encode()).hexdigest()


def generate_sector_id(prefix: str, nin: int) -> str:
    """Generate a realistic-looking sector identifier."""
    suffix = str(abs(hash(f"{prefix}{nin}{SEED}")) % 10**10).zfill(10)
    return f"{prefix}{suffix}"


def random_linkage_date() -> str:
    """Random date within the last 8 years."""
    days_ago = random.randint(30, 8 * 365)
    return (date.today() - timedelta(days=days_ago)).isoformat()


def generate_api_key() -> str:
    """Generate a secure 32-byte hex API key."""
    return secrets.token_hex(32)


# -- Seeders ----------------------------------------------------------
def seed_citizen_registry(cursor, df: pd.DataFrame) -> None:
    print("\nSeeding Citizen_Registry...")

    records = []
    for _, row in df.iterrows():
        nin        = int(row["NIN"])
        full_name  = fake.name()
        age        = int(row["Age"])
        gender     = row["Gender"]

        # Derive DOB from age (approximate)
        birth_year = date.today().year - age
        dob        = date(birth_year, random.randint(1, 12), random.randint(1, 28))

        records.append((
            nin,
            full_name,
            dob.isoformat(),
            gender,
            row["State_of_Origin"],
            hash_biometric(nin),
        ))

        if len(records) % BATCH_SIZE == 0:
            cursor.executemany(
                """INSERT OR IGNORE INTO Citizen_Registry
                   (NIN, Full_Name, DOB, Gender, State_of_Origin, Biometric_Hash)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                records,
            )
            records.clear()
            print(f"  Inserted {cursor.rowcount} rows in batch...")

    # Final batch
    if records:
        cursor.executemany(
            """INSERT OR IGNORE INTO Citizen_Registry
               (NIN, Full_Name, DOB, Gender, State_of_Origin, Biometric_Hash)
               VALUES (?, ?, ?, ?, ?, ?)""",
            records,
        )

    print(f"  Citizen_Registry seeded.")


def seed_sector_mapping(cursor, df: pd.DataFrame) -> None:
    print("\nSeeding Sector_Mapping...")

    records = []
    for _, row in df.iterrows():
        nin = int(row["NIN"])
        for col, (sector_name, agency, prefix) in SECTOR_MAP.items():
            if int(row[col]) == 1:
                records.append((
                    nin,
                    sector_name,
                    generate_sector_id(prefix, nin),
                    random_linkage_date(),
                    "Active",
                ))

        if len(records) >= BATCH_SIZE:
            cursor.executemany(
                """INSERT OR IGNORE INTO Sector_Mapping
                   (NIN, Sector_Name, Sector_ID, Linkage_Date, Linkage_Status)
                   VALUES (?, ?, ?, ?, ?)""",
                records,
            )
            records.clear()

    # Final batch
    if records:
        cursor.executemany(
            """INSERT OR IGNORE INTO Sector_Mapping
               (NIN, Sector_Name, Sector_ID, Linkage_Date, Linkage_Status)
               VALUES (?, ?, ?, ?, ?)""",
            records,
        )

    print(f"  Sector_Mapping seeded.")


def seed_api_keys(cursor) -> None:
    print("\nSeeding API_Keys...")

    for agency in SECTOR_AGENCIES:
        api_key = generate_api_key()
        cursor.execute(
            """INSERT OR IGNORE INTO API_Keys
               (Agency_ID, Sector_Name, API_Key, Status)
               VALUES (?, ?, ?, 'Active')""",
            (agency["Agency_ID"], agency["Sector_Name"], api_key),
        )
        print(f"  [{agency['Sector_Name']:12}]  {agency['Agency_ID']}  ->  {api_key}")

    print(f"  API_Keys seeded.")


# -- Summary ----------------------------------------------------------
def print_summary(cursor) -> None:
    print("\n" + "=" * 55)
    print("  SEED SUMMARY")
    print("=" * 55)

    tables = ["Citizen_Registry", "Sector_Mapping", "API_Keys",
              "Risk_Telemetry", "System_Audit"]
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"  {table:<25}: {count:,} rows")

    # Sector distribution
    print("-" * 55)
    print("  Sector_Mapping breakdown:")
    cursor.execute("""
        SELECT Sector_Name, COUNT(*) as cnt
        FROM Sector_Mapping
        GROUP BY Sector_Name
        ORDER BY cnt DESC;
    """)
    for sector, cnt in cursor.fetchall():
        print(f"    {sector:<15}: {cnt:,} links")

    print("=" * 55)


# -- Entry point ------------------------------------------------------
def main() -> None:
    # Pre-flight checks
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        print("Run setup_database.py first.")
        exit(1)

    if not os.path.exists(CSV_PATH):
        print(f"ERROR: Dataset not found at {CSV_PATH}")
        print("Run generate_dataset.py first.")
        exit(1)

    print(f"Loading dataset from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    print(f"  Loaded {len(df):,} records.")

    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    seed_citizen_registry(cursor, df)
    conn.commit()

    seed_sector_mapping(cursor, df)
    conn.commit()

    seed_api_keys(cursor)
    conn.commit()

    print_summary(cursor)
    conn.close()

    print(f"\nDatabase seeded successfully.")
    print(f"  Path : {DB_PATH}")
    db_mb = os.path.getsize(DB_PATH) / 1024 / 1024
    print(f"  Size : {db_mb:.2f} MB")


if __name__ == "__main__":
    main()