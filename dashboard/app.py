"""
NINCore — Streamlit Dashboard
================================
Main entry point. Handles page routing via sidebar navigation.

Start with:
    python run_dashboard.py
or:
    streamlit run dashboard/app.py
"""

import streamlit as st

st.set_page_config(
    page_title="NINCore — Identity Governance Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global styles ─────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f1923;
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }

    /* Main background */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* KPI cards */
    .kpi-card {
        background: linear-gradient(135deg, #1a2332 0%, #243447 100%);
        border: 1px solid #2d4057;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        text-align: center;
    }
    .kpi-label {
        font-size: 0.78rem;
        color: #8899aa;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-size: 2.1rem;
        font-weight: 700;
        color: #e8f4fd;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #6688aa;
        margin-top: 0.3rem;
    }

    /* Risk badge */
    .badge-high {
        background: #c0392b;
        color: white;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-low {
        background: #1e8449;
        color: white;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* Section headers */
    .section-header {
        font-size: 0.72rem;
        font-weight: 600;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        border-bottom: 1px solid #2d4057;
        padding-bottom: 0.4rem;
        margin-bottom: 1rem;
    }

    /* Tables */
    .dataframe thead th {
        background-color: #1a2332 !important;
        color: #aabbcc !important;
        font-size: 0.78rem !important;
    }
    .dataframe tbody td {
        font-size: 0.82rem !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer    {visibility: hidden;}
    header    {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

import importlib
import sys
from pathlib import Path

# Make sure project root is on path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 1.5rem 0;'>
        <div style='font-size:1.5rem; font-weight:800;
                    color:#4fc3f7; letter-spacing:0.05em;'>
            NINCORE
        </div>
        <div style='font-size:0.7rem; color:#607d8b;
                    text-transform:uppercase; letter-spacing:0.1em;'>
            Identity Governance Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    PAGES = {
        "System Overview":     "pages.01_overview",
        "Risk Assessment":     "pages.02_risk_assessment",
        "Sector Analysis":     "pages.03_sector_analysis",
        "Governance Trail":    "pages.04_governance",
        "Administration":      "pages.05_admin",
    }

    selection = st.radio(
        "Navigation",
        list(PAGES.keys()),
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.68rem; color:#455a64; padding: 0.5rem 0;'>
        <b style='color:#546e7a;'>NINCore v1.0.0</b><br>
        Federal University of Lafia<br>
        Stefan Habila Musa &nbsp;|&nbsp; 2026<br><br>
        API: <span style='color:#4fc3f7;'>localhost:8000</span>
    </div>
    """, unsafe_allow_html=True)

# ── Load selected page ────────────────────────────────────────────────
page_module = importlib.import_module(
    f"dashboard.{PAGES[selection]}"
)
page_module.render()