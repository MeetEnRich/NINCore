"""
NINCore Dashboard — Page 4: Governance Trail
=============================================
Tamper-evident audit log viewer.
Recent system events, per-NIN audit history.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.utils import get_api_key, api_get

API_BASE = "http://localhost:8000/api/v1"

ACTION_COLORS = {
    "VERIFY_REQUEST":    "#1565c0",
    "AUDIT_VIEW":        "#00695c",
    "TELEMETRY_VIEW":    "#4a148c",
    "ADMIN_VIEW":        "#e65100",
    "SECTOR_VIEW":       "#880e4f",
    "REVOKE_SECTOR_LINK":"#c0392b",
}


def render():
    st.markdown(
        "<h2 style='color:#e8f4fd; font-weight:700; "
        "margin-bottom:0.2rem;'>Governance Trail</h2>"
        "<p style='color:#607d8b; font-size:0.85rem; "
        "margin-bottom:1.5rem;'>Tamper-evident audit log of all "
        "system actions, agency access events, and administrative "
        "operations. Append-only in compliance with NDPA 2023.</p>",
        unsafe_allow_html=True,
    )

    api_key = get_api_key()
    if not api_key:
        st.warning("Configure your API key in the sidebar.")
        return

    # ── Controls ──────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Audit Log Query</div>",
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        nin_filter = st.text_input(
            "Filter by NIN (optional)",
            placeholder="11-digit NIN",
            max_chars=11,
        )
    with c2:
        limit = st.selectbox("Records to load", [50, 100, 200, 500],
                             index=0)
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        load_btn = st.button("Load Audit Log", type="primary",
                             use_container_width=True)

    if not load_btn and "audit_data" not in st.session_state:
        st.info("Click 'Load Audit Log' to fetch the governance trail.")
        return

    # ── Fetch data ────────────────────────────────────────────────────
    if load_btn:
        if nin_filter and len(nin_filter) == 11 and nin_filter.isdigit():
            data = api_get(
                f"{API_BASE}/audit/{nin_filter}?limit={limit}", api_key
            )
        else:
            data = api_get(
                f"{API_BASE}/audit/recent/all?limit={limit}", api_key
            )

        if not data:
            st.warning("No audit records found.")
            return

        st.session_state["audit_data"] = data

    data = st.session_state.get("audit_data", [])
    if not data:
        return

    df = pd.DataFrame(data)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # ── Summary KPIs ──────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Log Summary</div>",
                unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>Records Loaded</div>
            <div class='kpi-value'>{len(df):,}</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        unique_nins = df["NIN"].nunique()
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>Unique NINs</div>
            <div class='kpi-value'>{unique_nins:,}</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        unique_agencies = df["Agency_ID"].nunique() if "Agency_ID" in df else 0
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>Agencies Active</div>
            <div class='kpi-value'>{unique_agencies}</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        revoke_count = (df["Action_Taken"] == "REVOKE_SECTOR_LINK").sum() \
            if "Action_Taken" in df else 0
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>Revocations</div>
            <div class='kpi-value'
                 style='color:{"#c0392b" if revoke_count > 0 else "#e8f4fd"}'>
                {revoke_count}
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Action breakdown chart ────────────────────────────────────────
    if "Action_Taken" in df:
        col_chart, col_table = st.columns([1, 2])

        with col_chart:
            st.markdown(
                "<div class='section-header'>Actions Breakdown</div>",
                unsafe_allow_html=True,
            )
            action_counts = df["Action_Taken"].value_counts()
            colors = [
                ACTION_COLORS.get(a, "#455a64")
                for a in action_counts.index
            ]
            fig = go.Figure(go.Bar(
                x           = action_counts.values,
                y           = action_counts.index,
                orientation = "h",
                marker      = dict(color=colors,
                                   line=dict(color="#0f1923", width=1)),
                text        = action_counts.values,
                textposition= "outside",
                textfont    = dict(color="#aabbcc", size=10),
            ))
            fig.update_layout(
                paper_bgcolor = "rgba(0,0,0,0)",
                plot_bgcolor  = "rgba(0,0,0,0)",
                font          = dict(color="#aabbcc"),
                margin        = dict(t=5, b=5, l=5, r=40),
                height        = 280,
                xaxis = dict(showgrid=True, gridcolor="#1a2332",
                             tickfont=dict(color="#aabbcc")),
                yaxis = dict(showgrid=False,
                             tickfont=dict(color="#aabbcc", size=10)),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_table:
            st.markdown(
                "<div class='section-header'>Audit Log Entries</div>",
                unsafe_allow_html=True,
            )
            display_cols = ["Audit_ID", "NIN", "Agency_ID",
                            "Action_Taken", "Timestamp"]
            display_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(
                df[display_cols].head(100),
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)