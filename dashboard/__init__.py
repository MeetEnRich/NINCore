"""
NINCore Streamlit Dashboard package
=====================================
Entry point : dashboard/app.py
Start with  : python run_dashboard.py

Pages:
  01_overview.py        -- System KPIs and activity overview
  02_risk_assessment.py -- Live NIN risk lookup
  03_sector_analysis.py -- Sector linkage distribution
  04_governance.py      -- Audit trail viewer
  05_admin.py           -- Administration and system controls
"""

from dashboard import utils

__all__ = ["utils"]