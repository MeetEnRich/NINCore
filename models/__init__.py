"""
NINCore models package
=======================
Exposes the RiskEngine for import anywhere in the project:

    from models.risk_engine import RiskEngine
"""

from models.risk_engine import RiskEngine, FEATURE_COLUMNS, HIGH_RISK_THRESHOLD

__all__ = ["RiskEngine", "FEATURE_COLUMNS", "HIGH_RISK_THRESHOLD"]