"""
NINCore Dashboard — Shared Utilities
=======================================
API helper functions and shared state used across all pages.
"""

import streamlit as st
import requests
from typing import Optional


API_TIMEOUT = 8  # seconds


def get_api_key() -> Optional[str]:
    """
    Renders the API key input in the sidebar and returns the value.
    Persists in session state across page navigations.
    """
    with st.sidebar:
        st.markdown(
            "<div style='font-size:0.72rem; color:#607d8b; "
            "text-transform:uppercase; letter-spacing:0.08em; "
            "margin-bottom:0.3rem;'>API Authentication</div>",
            unsafe_allow_html=True,
        )
        api_key = st.text_input(
            "X-API-Key",
            type="password",
            placeholder="Paste sector API key...",
            key="global_api_key",
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