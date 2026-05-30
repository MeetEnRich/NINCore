"""
NINCore Dashboard pages package
=================================
Each module exposes a single render() function
called by dashboard/app.py via importlib.
"""

import importlib

_PAGES = [
    "01_overview",
    "02_risk_assessment",
    "03_sector_analysis",
    "04_governance",
    "05_admin",
]

pages = {
    name: importlib.import_module(f"dashboard.pages.{name}")
    for name in _PAGES
}
