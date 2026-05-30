"""
NINCore Dashboard — Page 2: Risk Assessment
=============================================
Live NIN risk lookup form. Submits to POST /api/v1/verify-risk
and renders the full risk verdict with score gauge.
"""

import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.utils import get_api_key, api_post, api_get

API_BASE = "http://localhost:8000/api/v1"

NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa",
    "Benue", "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti",
    "Enugu", "FCT", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina",
    "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo",
    "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara",
]

SECTORS = ["Banking", "Health", "Education", "Transport", "Telecoms"]


def render_gauge(risk_score: float) -> go.Figure:
    """Render a risk score gauge chart."""
    color = "#c0392b" if risk_score >= 0.7 else (
        "#f39c12" if risk_score >= 0.4 else "#1e8449"
    )
    fig = go.Figure(go.Indicator(
        mode  = "gauge+number",
        value = round(risk_score * 100, 2),
        title = dict(text="Risk Score (%)", font=dict(color="#aabbcc", size=13)),
        number= dict(font=dict(color=color, size=36), suffix="%"),
        gauge = dict(
            axis=dict(
                range=[0, 100],
                tickcolor="#aabbcc",
                tickfont=dict(color="#aabbcc"),
            ),
            bar=dict(color=color, thickness=0.25),
            bgcolor="#1a2332",
            bordercolor="#2d4057",
            steps=[
                dict(range=[0,  40],  color="#0d2218"),
                dict(range=[40, 70],  color="#2d1f00"),
                dict(range=[70, 100], color="#2d0a0a"),
            ],
            threshold=dict(
                line=dict(color="white", width=2),
                thickness=0.8,
                value=70,
            ),
        ),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#aabbcc"),
        margin=dict(t=30, b=10, l=30, r=30),
        height=260,
    )
    return fig


def render():
    st.markdown(
        "<h2 style='color:#e8f4fd; font-weight:700; "
        "margin-bottom:0.2rem;'>Risk Assessment</h2>"
        "<p style='color:#607d8b; font-size:0.85rem; "
        "margin-bottom:1.5rem;'>Submit a NIN for real-time "
        "ML-powered identity risk evaluation.</p>",
        unsafe_allow_html=True,
    )

    api_key = get_api_key()
    if not api_key:
        st.warning("Configure your API key in the sidebar to submit assessments.")
        return

    # ── Input form ────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Verification Request</div>",
                unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        nin = st.text_input(
            "National Identification Number (NIN)",
            placeholder="Enter 11-digit NIN",
            max_chars=11,
        )
        sector = st.selectbox("Requesting Sector", SECTORS)
        state  = st.selectbox("Access Location (State)", NIGERIAN_STATES,
                               index=NIGERIAN_STATES.index("FCT"))

    with col2:
        device_id = st.text_input(
            "Device Identifier",
            placeholder="e.g. device-abc-xyz-001",
            value="device-dashboard-001",
        )
        activity  = st.selectbox(
            "Activity Type",
            ["VERIFICATION", "LOGIN", "TRANSACTION", "DATA_ACCESS"],
        )
        submitted = st.button(
            "Run Risk Assessment",
            type="primary",
            use_container_width=True,
        )

    # ── Submission ────────────────────────────────────────────────────
    if submitted:
        if not nin or len(nin) != 11 or not nin.isdigit():
            st.error("Please enter a valid 11-digit NIN.")
            return

        payload = {
            "NIN":           int(nin),
            "Sector_Name":   sector,
            "Location_State":state,
            "Device_ID":     device_id,
            "Activity_Type": activity,
        }

        with st.spinner("Running ML inference..."):
            result = api_post(
                f"{API_BASE}/verify-risk", api_key, payload
            )

        if not result:
            st.error("Assessment failed. Check that the NIN exists in the registry.")
            return

        # ── Results ───────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Assessment Result</div>",
                    unsafe_allow_html=True)

        is_high = result["ML_Prediction"] == "High_Risk"
        verdict_color  = "#c0392b" if is_high else "#1e8449"
        verdict_label  = "HIGH RISK — FLAGGED" if is_high else "LOW RISK — CLEARED"
        verdict_border = "#c0392b" if is_high else "#1e8449"

        # Verdict banner
        st.markdown(f"""
        <div style='background: linear-gradient(135deg,
                    {"#2d0a0a" if is_high else "#0d2218"} 0%,
                    {"#1a0505" if is_high else "#071510"} 100%);
                    border: 1px solid {verdict_border};
                    border-left: 5px solid {verdict_border};
                    border-radius: 8px;
                    padding: 1.2rem 1.5rem;
                    margin-bottom: 1rem;'>
            <div style='font-size:1.2rem; font-weight:700;
                        color:{verdict_color};'>
                {verdict_label}
            </div>
            <div style='font-size:0.85rem; color:#aabbcc;
                        margin-top:0.4rem;'>
                {result["Message"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Gauge + details
        g_col, d_col = st.columns([1, 1])

        with g_col:
            st.plotly_chart(
                render_gauge(result["Risk_Score"]),
                use_container_width=True,
            )

        with d_col:
            st.markdown("<br>", unsafe_allow_html=True)
            details = {
                "NIN":              result["NIN"],
                "Risk Score":       f"{result['Risk_Score']:.4f}",
                "Confidence":       f"{result['Confidence_Pct']:.2f}%",
                "Prediction":       result["ML_Prediction"],
                "Sector":           result["Sector_Requested"],
                "Location":         result["Location_State"],
                "Timestamp (UTC)":  result["Timestamp"][:19].replace("T", " "),
                "Action":           result["Action"],
            }
            for k, v in details.items():
                st.markdown(
                    f"<div style='display:flex; justify-content:space-between;"
                    f"padding:0.35rem 0; border-bottom:1px solid #1a2332;'>"
                    f"<span style='color:#7f8c8d; font-size:0.82rem;'>{k}</span>"
                    f"<span style='color:#e8f4fd; font-size:0.82rem;"
                    f"font-weight:600;'>{v}</span></div>",
                    unsafe_allow_html=True,
                )

        # ── Telemetry history ─────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Telemetry History for this NIN</div>",
                    unsafe_allow_html=True)

        history = api_get(
            f"{API_BASE}/audit/telemetry/{nin}?limit=10", api_key
        )
        if history:
            import pandas as pd
            df = pd.DataFrame(history)[[
                "Log_ID", "Sector_Requesting",
                "Risk_Score", "ML_Prediction", "Timestamp"
            ]]
            df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.strftime(
                "%Y-%m-%d %H:%M"
            )
            df.columns = ["Log ID", "Sector", "Risk Score",
                          "Prediction", "Timestamp"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No prior telemetry for this NIN.")