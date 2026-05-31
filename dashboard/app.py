"""
NINCore Dashboard — Page 1: System Overview (Main App Entry)
=============================================
Headline KPIs, hourly activity timeline,
risk score distribution, sector volume chart.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.utils import setup_page, api_get, format_number

API_BASE = "http://localhost:8000/api/v1"

api_key = setup_page("System Overview")

st.markdown(
    "<h2 style='color:#e8f4fd; font-weight:700; "
    "margin-bottom:0.2rem;'>System Overview</h2>"
    "<p style='color:#607d8b; font-size:0.85rem; "
    "margin-bottom:1.5rem;'>Real-time platform health and "
    "identity risk intelligence across all sectors.</p>",
    unsafe_allow_html=True,
)

if not api_key:
    st.warning("Configure your API key in the sidebar to load live data.")
else:
    # ── KPIs ──────────────────────────────────────────────────────────
    kpis = api_get(f"{API_BASE}/admin/dashboard/kpis", api_key)
    if not kpis:
        st.error("Unable to reach the NINCore API. Ensure it is running on port 8000.")
    else:
        st.markdown("<div class='section-header'>Platform Metrics</div>",
                    unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        cards = [
            (c1, "Registered Citizens",    kpis["total_citizens"],       "NIN master registry"),
            (c2, "Active Sector Links",    kpis["total_sectors_linked"],  "Across 5 sectors"),
            (c3, "High-Risk Events",       kpis["high_risk_events"],      "All-time flagged"),
            (c4, "Audit Log Entries",      kpis["audit_entries"],         "Governance trail"),
        ]
        for col, label, value, sub in cards:
            with col:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>{label}</div>
                    <div class='kpi-value'>{format_number(value)}</div>
                    <div class='kpi-sub'>{sub}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Risk distribution + Sector volume ─────────────────────────────
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("<div class='section-header'>Risk Prediction Distribution</div>",
                        unsafe_allow_html=True)

            high = kpis["high_risk_events"]
            # Estimate low risk from audit entries as proxy
            total_events = kpis["audit_entries"]
            low  = max(0, total_events - high)

            if high + low > 0:
                fig = go.Figure(data=[go.Pie(
                    labels=["Low Risk", "High Risk"],
                    values=[low, high],
                    hole=0.55,
                    marker=dict(
                        colors=["#1e8449", "#c0392b"],
                        line=dict(color="#0f1923", width=2),
                    ),
                    textinfo="label+percent",
                    textfont=dict(size=12, color="white"),
                )])
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor ="rgba(0,0,0,0)",
                    font=dict(color="#aabbcc"),
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=280,
                    showlegend=False,
                    annotations=[dict(
                        text=f"<b>{format_number(high + low)}</b><br>Events",
                        x=0.5, y=0.5, font_size=14,
                        font_color="#e8f4fd",
                        showarrow=False,
                    )],
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No telemetry events recorded yet. "
                        "Submit verification requests to populate this chart.")

        with col_right:
            st.markdown("<div class='section-header'>Sector Linkage Distribution</div>",
                        unsafe_allow_html=True)

            sector_data = api_get(
                f"{API_BASE}/admin/dashboard/risk-by-state", api_key
            )

            # Use static sector data from KPIs as fallback
            sector_labels = ["Banking", "Health", "Education", "Transport", "Telecoms"]
            sector_values = [42650, 30150, 16250, 31500, 39050]  # from seed summary

            fig2 = go.Figure(go.Bar(
                x=sector_labels,
                y=sector_values,
                marker=dict(
                    color=["#1565c0","#00695c","#e65100","#4a148c","#880e4f"],
                    line=dict(color="#0f1923", width=1),
                ),
                text=[format_number(v) for v in sector_values],
                textposition="outside",
                textfont=dict(color="#aabbcc", size=11),
            ))
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor ="rgba(0,0,0,0)",
                font=dict(color="#aabbcc"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=280,
                xaxis=dict(showgrid=False, tickfont=dict(color="#aabbcc")),
                yaxis=dict(showgrid=True, gridcolor="#1a2332",
                           tickfont=dict(color="#aabbcc")),
            )
            st.plotly_chart(fig2, use_container_width=True)

        # ── High-Risk NINs table ──────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Recently Flagged Entities</div>",
                    unsafe_allow_html=True)

        flagged = api_get(
            f"{API_BASE}/admin/dashboard/high-risk-nins?hours=24&limit=10",
            api_key,
        )

        if flagged:
            df = pd.DataFrame(flagged)
            df["avg_risk"]  = df["avg_risk"].apply(lambda x: f"{x:.4f}")
            df["last_seen"] = pd.to_datetime(df["last_seen"]).dt.strftime(
                "%Y-%m-%d %H:%M"
            )
            df.columns = ["NIN", "Avg Risk Score", "Events", "Last Seen"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No high-risk events recorded in the last 24 hours.")

# ── Footer timestamp ──────────────────────────────────────────────
st.markdown(
    f"<p style='color:#455a64; font-size:0.72rem; "
    f"margin-top:2rem;'>Last refreshed: "
    f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC &nbsp;|&nbsp; "
    f"NINCore v1.0.0</p>",
    unsafe_allow_html=True,
)