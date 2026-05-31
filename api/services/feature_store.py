"""
NINCore - Feature Store Service
===============================
Abstracts the complex logic for assembling the 18-feature vector used by the ML model.
"""

import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from database import crud
from database.models import CitizenRegistry

class FeatureStore:
    NIGERIAN_STATES = [
        "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa",
        "Benue", "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti",
        "Enugu", "FCT", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina",
        "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo",
        "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara",
    ]
    STATE_INDEX = {s: i for i, s in enumerate(sorted(NIGERIAN_STATES))}

    @classmethod
    def _hash_device(cls, device_id: str) -> str:
        return hashlib.sha256(device_id.encode()).hexdigest()

    @classmethod
    def _encode_state(cls, state: str) -> int:
        return cls.STATE_INDEX.get(state, 0)

    @classmethod
    def build_feature_vector(
        cls, 
        db: Session, 
        nin: int, 
        citizen: CitizenRegistry,
        request_location: str, 
        request_device: str,
        access_hour: int,
    ) -> tuple[dict, str, int, float]:
        """
        Extracts and engineers behavioral features for ML inference.
        Returns:
            feature_vector (dict): The 18 features expected by the Random Forest
            device_hash (str): The hashed device ID
            login_freq_24h (int): Number of logins in 24h (needed for logging)
            geo_velocity (float): The geographical velocity (needed for logging)
        """
        now = datetime.utcnow()
        
        # Real-time behavioral features from DB
        login_freq_24h = crud.telemetry.get_login_frequency_24h(db, nin=nin)
        active_links   = crud.sector.count_active_links(db, nin=nin)
        last_event     = crud.telemetry.get_last_event(db, nin=nin)

        # Geographic velocity
        geo_velocity = 0.0
        if last_event and last_event.Location_State:
            if last_event.Location_State != request_location:
                geo_velocity = 500.0
            else:
                geo_velocity = 10.0
        
        # Sector conflict
        sector_conflict = 1 if geo_velocity >= 500.0 and login_freq_24h > 3 else 0

        # Sector flags
        sector_flags = {s: 0 for s in ["Banking", "Health", "Education", "Transport", "Telecoms"]}
        for link in crud.sector.get_by_nin(db, nin=nin):
            if link.Sector_Name in sector_flags:
                sector_flags[link.Sector_Name] = 1

        # Failed auth attempts
        recent_logs = crud.telemetry.get_history(db, nin=nin, limit=10)
        failed_attempts = sum(1 for log in recent_logs if log.ML_Prediction == "High_Risk")

        # Age consistency
        try:
            birth_year = int(citizen.DOB[:4])
            computed_age = now.year - birth_year
            age_consistency = min(1.0, max(0.0, 1.0 - abs(computed_age - 40) / 80))
        except Exception:
            age_consistency = 0.75

        # Name mismatch
        name_mismatch = 1 if sector_conflict == 1 and failed_attempts > 2 else 0

        # Device reputation
        device_hash = cls._hash_device(request_device)
        known_device = any(log.Device_ID_Hash == device_hash for log in recent_logs)
        device_reputation = 0.85 if known_device else 0.45

        # Assemble the 18-feature vector
        feature_vector = {
            "Age":                     now.year - int(citizen.DOB[:4]),
            "State_of_Origin":         cls._encode_state(citizen.State_of_Origin or "FCT"),
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

        return feature_vector, device_hash, login_freq_24h, geo_velocity
