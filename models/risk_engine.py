"""
NINCore Risk Engine
=====================
Loads the trained Random Forest model from disk and exposes
a clean predict() interface for the API layer.

The model is loaded once at module import time — not on every
request — so the API stays fast under load.

Usage:
    from models.risk_engine import RiskEngine

    engine = RiskEngine()
    risk_score, prediction = engine.predict(feature_vector_dict)
"""

import logging
import os
from pathlib import Path
from typing import Tuple

import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ── Path resolution ───────────────────────────────────────────────────
_THIS_DIR  = Path(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = _THIS_DIR / "saved" / "risk_engine.pkl"

# ── Feature order must exactly match training (notebook 02, Cell 2) ──
FEATURE_COLUMNS = [
    "Age",
    "State_of_Origin",
    "Gender",
    "NIN_Linkage_Count",
    "Login_Frequency",
    "Geographic_Velocity",
    "Device_Reputation_Score",
    "Sector_Conflict_Flag",
    "Failed_Auth_Attempts",
    "Access_Hour",
    "BVN_Status",
    "NHIA_Status",
    "JAMB_Status",
    "FRSC_Status",
    "Voter_ID_Status",
    "Age_Consistency_Score",
    "Name_Mismatch_Flag",
    "Sector_Access_Frequency",
]

HIGH_RISK_THRESHOLD = 0.7


class RiskEngine:
    """
    Wrapper around the trained Random Forest Classifier.

    Responsibilities:
      - Load and validate the .pkl model file on init
      - Accept a feature dictionary from the API layer
      - Return a (risk_score, prediction_label) tuple
    """

    def __init__(self, model_path: Path = MODEL_PATH):
        self.model_path = model_path
        self.model      = None
        self._load()

    def _load(self) -> None:
        """Load the model from disk. Raises clearly if file is missing."""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Risk engine model not found at {self.model_path}\n"
                "Run notebooks/02_model_training.ipynb first."
            )
        self.model = joblib.load(self.model_path)
        logger.info("Risk engine loaded from %s", self.model_path)

    def _build_vector(self, features: dict) -> pd.DataFrame:
        """
        Convert a feature dictionary into a single-row DataFrame
        with columns in the exact order the model was trained on.

        Raises KeyError if any required feature is missing.
        """
        missing = [f for f in FEATURE_COLUMNS if f not in features]
        if missing:
            raise KeyError(
                f"Feature vector is missing required fields: {missing}"
            )

        row = {col: [features[col]] for col in FEATURE_COLUMNS}
        return pd.DataFrame(row)

    def predict(self, features: dict) -> Tuple[float, str]:
        """
        Run inference on a single feature vector.

        Args:
            features: dict mapping feature name → value.
                      Must contain all 18 keys in FEATURE_COLUMNS.

        Returns:
            (risk_score, prediction)
              risk_score  : float between 0.0 and 1.0
              prediction  : "High_Risk" or "Low_Risk"
        """
        X = self._build_vector(features)

        # Probability of class 1 (Fraudulent) is the risk score
        risk_score = float(self.model.predict_proba(X)[0][1])

        prediction = (
            "High_Risk" if risk_score >= HIGH_RISK_THRESHOLD else "Low_Risk"
        )

        logger.debug(
            "Inference complete — score=%.4f prediction=%s",
            risk_score, prediction,
        )
        return risk_score, prediction

    def batch_predict(self, feature_list: list) -> list:
        """
        Run inference on a list of feature dicts.
        Returns a list of (risk_score, prediction) tuples.
        Used by notebooks for bulk evaluation.
        """
        results = []
        for features in feature_list:
            results.append(self.predict(features))
        return results

    @property
    def is_loaded(self) -> bool:
        """True if the model is loaded and ready."""
        return self.model is not None

    def __repr__(self):
        status = "loaded" if self.is_loaded else "NOT loaded"
        return f"<RiskEngine model={self.model_path.name} status={status}>"