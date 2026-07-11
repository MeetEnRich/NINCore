"""
NINCore Dashboard — Page 3: Sector Analysis
=============================================
Sector linkage distribution, per-sector risk volumes,
and cross-sector activity breakdown.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.utils import setup_page, api_get

API_BASE = "http://localhost:8000/api/v1"

SECTOR_COLORS = {
    "Banking":   "#1565c0",
    "Health":    "#00695c",
    "Education": "#e65100",
    "Transport": "#4a148c",
    "Telecoms":  "#880e4f",
}

# Seeded values from seed_database.py summary
SECTOR_LINK_COUNTS = {
    "Banking":   42650,
    "Health":    30150,
    "Education": 16250,
    "Transport": 31500,
    "Telecoms":  39050,
}


st.markdown(
    "<h2 style='font-weight:700; "
    "margin-bottom:0.2rem;'>Sector Analysis</h2>"
    "<p style='font-size:0.85rem; "
    "margin-bottom:1.5rem;'>NIN linkage distribution and "
    "cross-sector identity coverage across all five regulated sectors.</p>",
    unsafe_allow_html=True,
)

api_key = setup_page("Sector Analysis")
if not api_key:
    st.warning("Configure your API key in the sidebar.")
    st.stop()

# ── Sector KPI row ────────────────────────────────────────────────
st.markdown("<div class='section-header'>Sector Linkage Summary</div>",
            unsafe_allow_html=True)

cols = st.columns(5)
total_links = sum(SECTOR_LINK_COUNTS.values())
for col, (sector, count) in zip(cols, SECTOR_LINK_COUNTS.items()):
    pct = count / total_links * 100
    with col:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>{sector}</div>
            <div class='kpi-value'
                 style='color:{SECTOR_COLORS[sector]};
                 font-size:1.6rem;'>
                {count:,}
            </div>
            <div class='kpi-sub'>{pct:.1f}% of total links</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Horizontal bar + Treemap ──────────────────────────────────────
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("<div class='section-header'>Linkage Volume by Sector</div>",
                unsafe_allow_html=True)

    sectors = list(SECTOR_LINK_COUNTS.keys())
    counts  = list(SECTOR_LINK_COUNTS.values())
    colors  = [SECTOR_COLORS[s] for s in sectors]

    fig = go.Figure(go.Bar(
        x           = counts,
        y           = sectors,
        orientation = "h",
        marker      = dict(color=colors,
                           line=dict(color="#0f1923", width=1)),
        text        = [f"{c:,}" for c in counts],
        textposition= "outside",
        textfont    = dict(color="#aabbcc", size=11),
    ))
    fig.update_layout(
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
        font          = dict(color="#aabbcc"),
        margin        = dict(t=10, b=10, l=10, r=60),
        height        = 300,
        xaxis = dict(showgrid=True, gridcolor="#1a2332",
                     tickfont=dict(color="#aabbcc")),
        yaxis = dict(showgrid=False,
                     tickfont=dict(color="#aabbcc", size=12)),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("<div class='section-header'>Proportional Coverage</div>",
                unsafe_allow_html=True)

    fig2 = go.Figure(go.Pie(
        labels      = sectors,
        values      = counts,
        hole        = 0.45,
        marker      = dict(
            colors  = colors,
            line    = dict(color="#0f1923", width=2),
        ),
        textinfo    = "label+percent",
        textfont    = dict(size=11, color="white"),
    ))
    fig2.update_layout(
        paper_bgcolor = "rgba(0,0,0,0)",
        font          = dict(color="#aabbcc"),
        margin        = dict(t=10, b=10, l=10, r=10),
        height        = 300,
        showlegend    = False,
        annotations   = [dict(
            text       = f"<b>{total_links:,}</b><br>Total Links",
            x=0.5, y=0.5,
            font_size  = 13,
            font_color = "#e8f4fd",
            showarrow  = False,
        )],
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Sector linkage rates table ────────────────────────────────────
st.markdown("<div class='section-header'>Sector Linkage Rate Analysis</div>",
            unsafe_allow_html=True)

total_citizens = 50_000
table_data = []
for sector, count in SECTOR_LINK_COUNTS.items():
    table_data.append({
        "Sector":           sector,
        "Total Links":      f"{count:,}",
        "Citizens Linked":  f"{count:,}",
        "Linkage Rate":     f"{count/total_citizens*100:.1f}%",
        "Avg per Citizen":  f"{count/total_citizens:.2f}",
    })

df = pd.DataFrame(table_data)
st.dataframe(df, use_container_width=True, hide_index=True)

# ── NIN Linkage Count distribution ───────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-header'>"
    "NIN Linkage Count Distribution (from EDA)"
    "</div>",
    unsafe_allow_html=True,
)

linkage_counts = [1, 2, 3, 4, 5]
legit_dist     = [2088, 8909, 17905, 14894, 3704]
fraud_dist     = [114,  443,  943,   796,   204]

fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=linkage_counts, y=legit_dist,
    mode="lines+markers",
    name="Legitimate",
    line=dict(color="#1e8449", width=2),
    marker=dict(size=8),
))
fig3.add_trace(go.Scatter(
    x=linkage_counts, y=fraud_dist,
    mode="lines+markers",
    name="Fraudulent",
    line=dict(color="#c0392b", width=2),
    marker=dict(size=8),
))
fig3.update_layout(
    paper_bgcolor = "rgba(0,0,0,0)",
    plot_bgcolor  = "rgba(0,0,0,0)",
    font          = dict(color="#aabbcc"),
    margin        = dict(t=10, b=10, l=10, r=10),
    height        = 280,
    xaxis = dict(
        title      = "Number of Sector Links",
        showgrid   = False,
        tickvals   = linkage_counts,
        tickfont   = dict(color="#aabbcc"),
    ),
    yaxis = dict(
        title    = "Number of Citizens",
        showgrid = True,
        gridcolor= "#1a2332",
        tickfont = dict(color="#aabbcc"),
    ),
    legend=dict(
        bgcolor    = "rgba(0,0,0,0)",
        font       = dict(color="#aabbcc"),
    ),
)
st.plotly_chart(fig3, use_container_width=True)