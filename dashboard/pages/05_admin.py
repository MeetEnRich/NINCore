"""
NINCore Dashboard — Page 5: Administration
============================================
API key management, sector revocation,
citizen profile lookup, system health check.
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.utils import setup_page, api_get, api_post

API_BASE = "http://localhost:8000/api/v1"

SECTORS = ["Banking", "Health", "Education", "Transport", "Telecoms"]


st.markdown(
    "<h2 style='color:#e8f4fd; font-weight:700; "
    "margin-bottom:0.2rem;'>Administration</h2>"
    "<p style='color:#607d8b; font-size:0.85rem; "
    "margin-bottom:1.5rem;'>System health, API key registry, "
    "citizen lookup, and sector revocation controls.</p>",
    unsafe_allow_html=True,
)

api_key = setup_page("Admin")
if not api_key:
    st.warning("Configure your API key in the sidebar.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "System Health",
    "API Key Registry",
    "Citizen Lookup",
    "Sector Revocation",
])

# ── Tab 1: System Health ──────────────────────────────────────────
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-header'>System Health Check</div>",
        unsafe_allow_html=True,
    )

    if st.button("Run Health Check", type="primary"):
        try:
            resp = requests.get(
                "http://localhost:8000/health", timeout=5
            )
            health = resp.json()
        except Exception:
            health = None

        if health:
            h1, h2, h3 = st.columns(3)
            status_color = (
                "#1e8449" if health["status"] == "healthy"
                else "#c0392b"
            )
            for col, label, val in [
                (h1, "API Status",  health["status"].upper()),
                (h2, "Database",    health["database"].upper()),
                (h3, "Risk Engine", health["model"].upper()),
            ]:
                color = "#1e8449" if val in ("HEALTHY","CONNECTED","LOADED") \
                        else "#c0392b"
                with col:
                    st.markdown(f"""
                    <div class='kpi-card'>
                        <div class='kpi-label'>{label}</div>
                        <div class='kpi-value'
                             style='color:{color}; font-size:1.3rem;'>
                            {val}
                        </div>
                        <div class='kpi-sub'>v{health.get("version","1.0.0")}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='background:#1a2332; border:1px solid #2d4057;
                        border-radius:8px; padding:1rem 1.5rem;
                        font-size:0.82rem; color:#aabbcc;'>
                <b style='color:#4fc3f7;'>Health check completed</b>
                &nbsp;|&nbsp;
                {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("API is unreachable. Ensure run_api.py is running.")

# ── Tab 2: API Keys ───────────────────────────────────────────────
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-header'>Registered Sector API Keys</div>",
        unsafe_allow_html=True,
    )

    keys = api_get(f"{API_BASE}/admin/api-keys", api_key)
    if keys:
        df = pd.DataFrame(keys)

        # Mask API key — show first 8 + last 4 chars only
        if "API_Key" not in df.columns:
            pass
        
        display = df[[
            "Key_ID", "Agency_ID", "Sector_Name", "Status",
            "Created_At", "Last_Used"
        ]].copy()

        display["Created_At"] = pd.to_datetime(
            display["Created_At"]
        ).dt.strftime("%Y-%m-%d %H:%M")
        display["Last_Used"]  = pd.to_datetime(
            display["Last_Used"], errors="coerce"
        ).dt.strftime("%Y-%m-%d %H:%M").fillna("Never")

        display.columns = [
            "Key ID", "Agency ID", "Sector", "Status",
            "Created", "Last Used"
        ]
        st.dataframe(display, use_container_width=True, hide_index=True)

        active  = (df["Status"] == "Active").sum()
        revoked = (df["Status"] == "Revoked").sum()
        st.markdown(
            f"<p style='color:#607d8b; font-size:0.78rem; "
            f"margin-top:0.5rem;'>"
            f"Active keys: <b style='color:#1e8449'>{active}</b>"
            f"&nbsp;&nbsp;Revoked keys: "
            f"<b style='color:#c0392b'>{revoked}</b></p>",
            unsafe_allow_html=True,
        )
    else:
        st.info("No API keys found.")

# ── Tab 3: Citizen Lookup ─────────────────────────────────────────
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-header'>Citizen Profile Lookup</div>",
        unsafe_allow_html=True,
    )

    lookup_nin = st.text_input(
        "Enter NIN to look up",
        placeholder="11-digit NIN",
        max_chars=11,
        key="lookup_nin",
    )
    lookup_btn = st.button("Look Up Citizen", type="primary",
                           key="lookup_btn")

    if lookup_btn and lookup_nin:
        if len(lookup_nin) != 11 or not lookup_nin.isdigit():
            st.error("Enter a valid 11-digit NIN.")
        else:
            citizen = api_get(
                f"{API_BASE}/admin/citizen/{lookup_nin}", api_key
            )
            sectors = api_get(
                f"{API_BASE}/admin/sectors/{lookup_nin}", api_key
            )

            if citizen:
                c_col, s_col = st.columns([1, 1])

                with c_col:
                    st.markdown(
                        "<div class='section-header'>"
                        "Identity Profile</div>",
                        unsafe_allow_html=True,
                    )
                    for k, v in citizen.items():
                        if k == "NIN":
                            continue
                        st.markdown(
                            f"<div style='display:flex; "
                            f"justify-content:space-between;"
                            f"padding:0.35rem 0; "
                            f"border-bottom:1px solid #1a2332;'>"
                            f"<span style='color:#7f8c8d; "
                            f"font-size:0.82rem;'>{k}</span>"
                            f"<span style='color:#e8f4fd; "
                            f"font-size:0.82rem; "
                            f"font-weight:600;'>{v}</span></div>",
                            unsafe_allow_html=True,
                        )

                with s_col:
                    st.markdown(
                        "<div class='section-header'>"
                        "Active Sector Links</div>",
                        unsafe_allow_html=True,
                    )
                    if sectors:
                        df_s = pd.DataFrame(sectors)[[
                            "Sector_Name", "Sector_ID",
                            "Linkage_Date", "Linkage_Status"
                        ]]
                        df_s.columns = [
                            "Sector", "Sector ID",
                            "Linked Since", "Status"
                        ]
                        st.dataframe(
                            df_s, use_container_width=True,
                            hide_index=True,
                        )
                    else:
                        st.info("No active sector links.")
            else:
                st.error(f"NIN {lookup_nin} not found in registry.")

# ── Tab 4: Sector Revocation ──────────────────────────────────────
with tab4:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-header'>Revoke Sector Linkage</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#c0392b; font-size:0.82rem; "
        "margin-bottom:1rem;'>This action is irreversible. "
        "The revocation will be permanently logged to the "
        "governance audit trail.</p>",
        unsafe_allow_html=True,
    )

    r1, r2 = st.columns([1, 1])
    with r1:
        rev_nin     = st.text_input("NIN", placeholder="11-digit NIN",
                                    max_chars=11, key="rev_nin")
        rev_sector  = st.selectbox("Sector to Revoke", SECTORS,
                                   key="rev_sector")
    with r2:
        rev_reason  = st.text_area(
            "Justification (required, min 10 characters)",
            placeholder="Provide a clear reason for this revocation...",
            height=120,
            key="rev_reason",
        )

    rev_btn = st.button(
        "Confirm Revocation",
        type="primary",
        key="rev_btn",
    )

    if rev_btn:
        if not rev_nin or len(rev_nin) != 11 or not rev_nin.isdigit():
            st.error("Enter a valid 11-digit NIN.")
        elif len(rev_reason.strip()) < 10:
            st.error("Justification must be at least 10 characters.")
        else:
            result = api_post(
                f"{API_BASE}/admin/revoke-sector",
                api_key,
                {
                    "NIN":          int(rev_nin),
                    "Sector_Name":  rev_sector,
                    "Justification":rev_reason.strip(),
                },
            )
            if result and result.get("status") == "success":
                st.success(result["message"])
            else:
                st.error(
                    "Revocation failed. Check NIN and sector link exist."
                )