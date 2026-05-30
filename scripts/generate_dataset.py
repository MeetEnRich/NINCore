"""
NINCore Synthetic Dataset Generator
=====================================
Generates 50,000 synthetic NIN identity records for model training.

Class Distribution (pre-SMOTE):
  - Legitimate (0): 47,500  ->  95%
  - Fraudulent  (1):  2,500  ->   5%

Features: 20 (as specified in Table 3.1)
Output:   data/raw/nincore_dataset.csv

Run:
    python scripts/generate_dataset.py
"""

import os
import random
import numpy as np
import pandas as pd
from faker import Faker

# -- Reproducibility --------------------------------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
fake = Faker("en_NG")
fake.seed_instance(SEED)

# -- Constants --------------------------------------------------------
TOTAL_RECORDS = 50_000
FRAUD_RATIO   = 0.05
N_FRAUD       = int(TOTAL_RECORDS * FRAUD_RATIO)   # 2,500
N_LEGIT       = TOTAL_RECORDS - N_FRAUD             # 47,500

NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa",
    "Benue", "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti",
    "Enugu", "FCT", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina",
    "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo",
    "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara",
]

OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "nincore_dataset.csv")


# -- NIN Generator ----------------------------------------------------
def generate_nin(existing: set) -> int:
    """Generate a unique 11-digit NIN."""
    while True:
        nin = random.randint(10_000_000_000, 99_999_999_999)
        if nin not in existing:
            existing.add(nin)
            return nin


# -- Sectoral flag logic ----------------------------------------------
def generate_sectoral_flags(age: int) -> dict:
    """
    Sector linkage probabilities loosely tied to realistic age ranges:
      BVN        -- likely if age >= 18 (bank account)
      NHIA       -- moderate across all ages
      JAMB       -- likely if age 16-35 (student / graduate)
      FRSC       -- likely if age >= 20 (driver licence)
      Voter_ID   -- likely if age >= 18 (registered voter)
    """
    return {
        "BVN_Status":      int(random.random() < (0.85 if age >= 18 else 0.10)),
        "NHIA_Status":     int(random.random() < 0.60),
        "JAMB_Status":     int(random.random() < (0.75 if 16 <= age <= 35 else 0.15)),
        "FRSC_Status":     int(random.random() < (0.65 if age >= 20 else 0.05)),
        "Voter_ID_Status": int(random.random() < (0.78 if age >= 18 else 0.00)),
    }


# -- Legitimate record generator --------------------------------------
def generate_legitimate(nin: int) -> dict:
    age   = random.randint(18, 80)
    state = random.choice(NIGERIAN_STATES)
    flags = generate_sectoral_flags(age)

    linkage_count = max(1, sum(flags.values()))

    return {
        "NIN":                     nin,
        "Age":                     age,
        "State_of_Origin":         state,
        "Gender":                  random.choice(["M", "F"]),
        "NIN_Linkage_Count":       linkage_count,
        "Login_Frequency":         random.randint(1, 5),
        "Geographic_Velocity":     round(random.uniform(0.0, 80.0), 4),
        "Device_Reputation_Score": round(random.uniform(0.55, 1.0), 4),
        "Sector_Conflict_Flag":    0,
        "Failed_Auth_Attempts":    random.randint(0, 2),
        "Access_Hour":             random.randint(6, 22),
        **flags,
        "Age_Consistency_Score":   round(random.uniform(0.75, 1.0), 4),
        "Name_Mismatch_Flag":      0,
        "Sector_Access_Frequency": random.randint(1, 15),
        "Anomaly_Flag":            0,
    }


# -- Fraudulent record generator --------------------------------------
# Six distinct fraud patterns so the model learns varied signals,
# not a single obvious combination.
FRAUD_PATTERNS = [
    "impossible_travel",
    "credential_stuffing",
    "identity_conflict",
    "device_compromise",
    "after_hours_access",
    "mixed",
]

def generate_fraudulent(nin: int) -> dict:
    age     = random.randint(18, 80)
    state   = random.choice(NIGERIAN_STATES)
    flags   = generate_sectoral_flags(age)
    pattern = random.choice(FRAUD_PATTERNS)

    # Baseline suspicious record
    record = {
        "NIN":                     nin,
        "Age":                     age,
        "State_of_Origin":         state,
        "Gender":                  random.choice(["M", "F"]),
        "NIN_Linkage_Count":       max(1, sum(flags.values())),
        "Login_Frequency":         random.randint(1, 8),
        "Geographic_Velocity":     round(random.uniform(0.0, 100.0), 4),
        "Device_Reputation_Score": round(random.uniform(0.3, 0.9), 4),
        "Sector_Conflict_Flag":    0,
        "Failed_Auth_Attempts":    random.randint(0, 3),
        "Access_Hour":             random.randint(0, 23),
        **flags,
        "Age_Consistency_Score":   round(random.uniform(0.4, 0.9), 4),
        "Name_Mismatch_Flag":      0,
        "Sector_Access_Frequency": random.randint(1, 25),
        "Anomaly_Flag":            1,
    }

    # Pattern-specific anomalies
    if pattern == "impossible_travel":
        record["Geographic_Velocity"]     = round(random.uniform(800.0, 3000.0), 4)
        record["Sector_Conflict_Flag"]    = 1
        record["Login_Frequency"]         = random.randint(6, 20)

    elif pattern == "credential_stuffing":
        record["Failed_Auth_Attempts"]    = random.randint(8, 25)
        record["Device_Reputation_Score"] = round(random.uniform(0.0, 0.30), 4)
        record["Login_Frequency"]         = random.randint(10, 30)

    elif pattern == "identity_conflict":
        record["Sector_Conflict_Flag"]    = 1
        record["Name_Mismatch_Flag"]      = 1
        record["Age_Consistency_Score"]   = round(random.uniform(0.0, 0.40), 4)

    elif pattern == "device_compromise":
        record["Device_Reputation_Score"] = round(random.uniform(0.0, 0.20), 4)
        record["Failed_Auth_Attempts"]    = random.randint(3, 10)
        record["Name_Mismatch_Flag"]      = random.choice([0, 1])

    elif pattern == "after_hours_access":
        record["Access_Hour"]             = random.choice(list(range(0, 5)) + [23])
        record["Login_Frequency"]         = random.randint(8, 25)
        record["Sector_Access_Frequency"] = random.randint(20, 60)

    elif pattern == "mixed":
        record["Geographic_Velocity"]     = round(random.uniform(300.0, 1500.0), 4)
        record["Failed_Auth_Attempts"]    = random.randint(4, 15)
        record["Device_Reputation_Score"] = round(random.uniform(0.0, 0.35), 4)
        record["Sector_Conflict_Flag"]    = random.choice([0, 1])
        record["Name_Mismatch_Flag"]      = random.choice([0, 1])
        record["Age_Consistency_Score"]   = round(random.uniform(0.1, 0.50), 4)
        record["Access_Hour"]             = random.choice(
            list(range(0, 5)) + list(range(6, 23))
        )

    return record


# -- Main generator ---------------------------------------------------
def generate_dataset() -> pd.DataFrame:
    print(f"Generating {TOTAL_RECORDS:,} records "
          f"({N_LEGIT:,} legitimate | {N_FRAUD:,} fraudulent)...")

    existing_nins: set = set()
    records = []

    for i in range(N_LEGIT):
        records.append(generate_legitimate(generate_nin(existing_nins)))
        if (i + 1) % 10_000 == 0:
            print(f"  Legitimate: {i + 1:,} / {N_LEGIT:,}")

    for i in range(N_FRAUD):
        records.append(generate_fraudulent(generate_nin(existing_nins)))
        if (i + 1) % 500 == 0:
            print(f"  Fraudulent: {i + 1:,} / {N_FRAUD:,}")

    random.shuffle(records)

    df = pd.DataFrame(records)

    # Enforce column order matching Table 3.1
    column_order = [
        "NIN", "Age", "State_of_Origin", "Gender",
        "NIN_Linkage_Count", "Login_Frequency", "Geographic_Velocity",
        "Device_Reputation_Score", "Sector_Conflict_Flag",
        "Failed_Auth_Attempts", "Access_Hour",
        "BVN_Status", "NHIA_Status", "JAMB_Status",
        "FRSC_Status", "Voter_ID_Status",
        "Age_Consistency_Score", "Name_Mismatch_Flag",
        "Sector_Access_Frequency",
        "Anomaly_Flag",
    ]
    return df[column_order]


# -- Validation -------------------------------------------------------
def validate_dataset(df: pd.DataFrame) -> None:
    print("\nRunning validation checks...")

    assert df.shape == (TOTAL_RECORDS, 20), \
        f"Expected (50000, 20), got {df.shape}"
    assert df.isnull().sum().sum() == 0, \
        "Null values found"
    assert df["NIN"].duplicated().sum() == 0, \
        "Duplicate NINs found"

    fraud_pct = df["Anomaly_Flag"].sum() / len(df) * 100
    assert 4.0 <= fraud_pct <= 6.0, \
        f"Fraud ratio out of range: {fraud_pct:.2f}%"

    assert df["Age"].between(18, 80).all()
    assert df["Access_Hour"].between(0, 23).all()
    assert df["Device_Reputation_Score"].between(0, 1).all()
    assert df["Age_Consistency_Score"].between(0, 1).all()
    assert df["NIN_Linkage_Count"].between(1, 5).all()
    assert df["NIN"].between(10_000_000_000, 99_999_999_999).all()
    assert df["Gender"].isin(["M", "F"]).all()

    for col in ["Sector_Conflict_Flag", "Name_Mismatch_Flag", "Anomaly_Flag",
                "BVN_Status", "NHIA_Status", "JAMB_Status",
                "FRSC_Status", "Voter_ID_Status"]:
        assert df[col].isin([0, 1]).all(), f"{col} has non-binary values"

    print("  All validation checks passed.")


# -- Summary ----------------------------------------------------------
def print_summary(df: pd.DataFrame) -> None:
    fraud = df[df["Anomaly_Flag"] == 1]
    legit = df[df["Anomaly_Flag"] == 0]

    print("\n" + "=" * 55)
    print("  DATASET SUMMARY")
    print("=" * 55)
    print(f"  Total records        : {len(df):,}")
    print(f"  Legitimate (0)       : {len(legit):,}  ({len(legit)/len(df)*100:.1f}%)")
    print(f"  Fraudulent (1)       : {len(fraud):,}   ({len(fraud)/len(df)*100:.1f}%)")
    print(f"  Features             : {df.shape[1]}")
    print(f"  Duplicate NINs       : {df['NIN'].duplicated().sum()}")
    print(f"  Null values          : {df.isnull().sum().sum()}")
    print("-" * 55)
    print("  Fraud pattern indicators (fraud records only):")
    print(f"    Sector_Conflict_Flag  = 1 : {fraud['Sector_Conflict_Flag'].sum():,}")
    print(f"    Name_Mismatch_Flag    = 1 : {fraud['Name_Mismatch_Flag'].sum():,}")
    print(f"    Avg Geographic_Velocity   : {fraud['Geographic_Velocity'].mean():.1f} km/h")
    print(f"    Avg Failed_Auth_Attempts  : {fraud['Failed_Auth_Attempts'].mean():.2f}")
    print(f"    Avg Device_Reputation     : {fraud['Device_Reputation_Score'].mean():.3f}")
    print("-" * 55)
    print("  Legitimate record baselines:")
    print(f"    Avg Geographic_Velocity   : {legit['Geographic_Velocity'].mean():.1f} km/h")
    print(f"    Avg Failed_Auth_Attempts  : {legit['Failed_Auth_Attempts'].mean():.2f}")
    print(f"    Avg Device_Reputation     : {legit['Device_Reputation_Score'].mean():.3f}")
    print("=" * 55)


# -- Entry point ------------------------------------------------------
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = generate_dataset()
    validate_dataset(df)
    print_summary(df)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n  Saved  -> {OUTPUT_FILE}")
    print(f"  Size   -> {os.path.getsize(OUTPUT_FILE) / 1024 / 1024:.2f} MB")