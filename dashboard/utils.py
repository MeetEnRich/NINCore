"""
NINCore Dashboard — Shared Utilities
=======================================
API helper functions and shared state used across all pages.
"""

import streamlit as st
import requests
from typing import Optional

API_TIMEOUT = 8  # seconds

def setup_page(page_title: str) -> Optional[str]:
    """
    Sets up the global page config, global styles, sidebar branding, 
    and returns the configured API key. This should be called at the 
    top of EVERY page script.
    """
    st.set_page_config(
        page_title=f"NINCore — {page_title}",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Global CSS
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

    with st.sidebar:
        # Branding
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

        # API Key Input
        st.markdown(
            "<div style='font-size:0.72rem; color:#607d8b; "
            "text-transform:uppercase; letter-spacing:0.08em; "
            "margin-bottom:0.3rem;'>API Authentication</div>",
            unsafe_allow_html=True,
        )
        
        if "saved_api_key" not in st.session_state:
            st.session_state.saved_api_key = ""

        def update_key():
            st.session_state.saved_api_key = st.session_state.global_api_key_widget

        api_key = st.text_input(
            "X-API-Key",
            value=st.session_state.saved_api_key,
            type="password",
            placeholder="Paste sector API key...",
            key="global_api_key_widget",
            on_change=update_key,
            label_visibility="collapsed",
        )
        
        if api_key:
            st.markdown(
                "<div style='font-size:0.7rem; color:#1e8449;'>"
                "Key configured</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div style='font-size:0.7rem; color:#c0392b;'>"
                "No key set</div>",
                unsafe_allow_html=True,
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

    return api_key or None


def api_get(url: str, api_key: str) -> Optional[dict]:
    """GET request to the NINCore API. Returns parsed JSON or None."""
    try:
        resp = requests.get(
            url,
            headers={"X-API-Key": api_key},
            timeout=API_TIMEOUT,
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None


def api_post(url: str, api_key: str, payload: dict) -> Optional[dict]:
    """POST request to the NINCore API. Returns parsed JSON or None."""
    try:
        resp = requests.post(
            url,
            json=payload,
            headers={"X-API-Key": api_key},
            timeout=API_TIMEOUT,
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None


def format_number(value: int) -> str:
    """Format large integers with comma separators."""
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    return str(value)