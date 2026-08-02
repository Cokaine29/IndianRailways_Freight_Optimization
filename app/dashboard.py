# CE 749 — dashboard.py
# Interactive Streamlit Dashboard for Indian Railways Freight Optimization
# Run with: streamlit run dashboard.py

import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IR Freight Optimizer | CE 749",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* Dark background */
  .stApp { background: #0d1117; color: #e6edf3; }
  .stSidebar { background: #161b22 !important; border-right: 1px solid #30363d; }

  /* Metric cards */
  .metric-card {
      background: linear-gradient(135deg, #1c2230 0%, #161b22 100%);
      border: 1px solid #30363d;
      border-radius: 12px;
      padding: 20px 24px;
      text-align: center;
      transition: transform 0.2s, box-shadow 0.2s;
  }
  .metric-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  }
  .metric-value {
      font-size: 2.0rem;
      font-weight: 700;
      background: linear-gradient(135deg, #58a6ff, #3fb950);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      line-height: 1.2;
  }
  .metric-label {
      font-size: 0.78rem;
      color: #8b949e;
      margin-top: 6px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
  }
  .metric-delta-good  { font-size:0.85rem; color:#3fb950; font-weight:600; margin-top:4px; }
  .metric-delta-warn  { font-size:0.85rem; color:#f78166; font-weight:600; margin-top:4px; }

  /* Hero banner */
  .hero-banner {
      background: linear-gradient(135deg, #0d1117 0%, #1c2230 50%, #0d2137 100%);
      border: 1px solid #30363d;
      border-radius: 16px;
      padding: 32px 40px;
      margin-bottom: 24px;
      position: relative;
      overflow: hidden;
  }
  .hero-banner::before {
      content: '';
      position: absolute;
      top: -50%;
      right: -10%;
      width: 300px;
      height: 300px;
      background: radial-gradient(circle, rgba(88,166,255,0.08) 0%, transparent 70%);
      border-radius: 50%;
  }
  .hero-title {
      font-size: 2.0rem;
      font-weight: 700;
      color: #e6edf3;
      line-height: 1.2;
  }
  .hero-subtitle {
      font-size: 1.0rem;
      color: #8b949e;
      margin-top: 8px;
  }
  .hero-tag {
      display: inline-block;
      background: rgba(88,166,255,0.15);
      border: 1px solid rgba(88,166,255,0.3);
      color: #58a6ff;
      border-radius: 20px;
      padding: 3px 12px;
      font-size: 0.75rem;
      font-weight: 600;
      margin-right: 8px;
      margin-top: 12px;
  }

  /* Section headers */
  .section-header {
      font-size: 1.15rem;
      font-weight: 600;
      color: #e6edf3;
      border-left: 3px solid #58a6ff;
      padding-left: 12px;
      margin: 24px 0 16px 0;
  }

  /* Insight boxes */
  .insight-box {
      background: rgba(63,185,80,0.08);
      border: 1px solid rgba(63,185,80,0.25);
      border-radius: 10px;
      padding: 14px 18px;
      margin: 10px 0;
      font-size: 0.9rem;
      color: #3fb950;
  }
  .warning-box {
      background: rgba(247,129,102,0.08);
      border: 1px solid rgba(247,129,102,0.25);
      border-radius: 10px;
      padding: 14px 18px;
      margin: 10px 0;
      font-size: 0.9rem;
      color: #f78166;
  }
  .info-box {
      background: rgba(88,166,255,0.08);
      border: 1px solid rgba(88,166,255,0.25);
      border-radius: 10px;
      padding: 14px 18px;
      margin: 10px 0;
      font-size: 0.9rem;
      color: #58a6ff;
  }

  /* Plotly chart background */
  .js-plotly-plot { border-radius: 12px; }

  /* Divider */
  hr { border-color: #30363d !important; }

  /* Sidebar radio */
  .stRadio > label { color: #8b949e; font-size: 0.85rem; }
  [data-baseweb="radio"] label { color: #e6edf3 !important; }

  /* Streamlit elements */
  .stSlider > div > div { background: #30363d; }
  div[data-testid="stMetricValue"] { color: #58a6ff; font-size: 1.6rem; }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ─────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#161b22",
    plot_bgcolor="#0d1117",
    font=dict(family="Inter", color="#e6edf3"),
    xaxis=dict(gridcolor="#21262d", linecolor="#30363d", zerolinecolor="#30363d"),
    yaxis=dict(gridcolor="#21262d", linecolor="#30363d", zerolinecolor="#30363d"),
)
DEFAULT_MARGIN = dict(l=50, r=30, t=50, b=50)

def layout(**overrides):
    """Merge PLOTLY_LAYOUT with per-chart overrides without key conflicts."""
    merged = {**PLOTLY_LAYOUT, "margin": DEFAULT_MARGIN}
    merged.update(overrides)
    return merged
COLORS = {
    "blue":   "#58a6ff",
    "green":  "#3fb950",
    "red":    "#f78166",
    "orange": "#f0883e",
    "purple": "#bc8cff",
    "teal":   "#39d353",
}

# ── Data imports ─────────────────────────────────────────────────────────────
from src.data import NODES, COMMODITIES, ARCS, ARC_TRACTION, ARC_DISTANCES, DEMAND

# ── Cached solver calls ───────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_cost_optimal():
    from src.model import build_and_solve
    return build_and_solve(objective="cost", use_mip=False)

@st.cache_data(show_spinner=False)
def get_emis_optimal():
    from src.model import build_and_solve
    return build_and_solve(objective="emission", use_mip=False)

@st.cache_data(show_spinner=False)
def get_pareto():
    from src.model import generate_pareto_frontier
    pareto, c, e = generate_pareto_frontier(n_points=12, use_mip=False)
    return pareto, c, e

@st.cache_data(show_spinner=False)
def get_heuristic(cost_opt_z1, cost_opt_z2):
    from src.heuristic import run_heuristic_comparison
    cost_opt = get_cost_optimal()
    return run_heuristic_comparison(cost_opt)

@st.cache_data(show_spinner=False)
def solve_epsilon(epsilon_val):
    from src.model import build_and_solve
    return build_and_solve(epsilon=epsilon_val * 1e9, objective="cost", use_mip=False)

@st.cache_data(show_spinner=False)
def get_sensitivity():
    import src.data as D
    from src.model import build_and_solve
    base = {arc: D.ARC_CAPACITY[arc] for arc in D.ARCS}
    results = []
    for cap in [40, 50, 60, 70, 80, 90, 100]:
        for arc in D.ARCS:
            D.ARC_CAPACITY[arc] = (200 if D.ARC_TRACTION[arc]=="electric"
                                   else (cap if D.ARC_DISTANCES[arc]>300 else max(cap-10,30)))
        r = build_and_solve(objective="cost", use_mip=False)
        results.append({"capacity": cap,
                         "Z1": r["Z1"] / 1e7 if r["Z1"] else None,
                         "Z2": r["Z2"] / 1e9 if r["Z2"] else None,
                         "status": r["status"]})
    for arc in D.ARCS:
        D.ARC_CAPACITY[arc] = base[arc]
    return results

# ── Node geographic coords (approximate lat/lon for India) ───────────────────
NODE_COORDS = {
    1:  (28.64, 77.22),   # Delhi
    2:  (19.08, 72.88),   # Mumbai
    3:  (13.08, 80.27),   # Chennai
    4:  (22.57, 88.36),   # Kolkata
    5:  (21.15, 79.08),   # Nagpur
    6:  (23.26, 77.41),   # Bhopal
    7:  (17.38, 78.49),   # Hyderabad
    8:  (18.52, 73.86),   # Pune
    9:  (23.03, 72.59),   # Ahmedabad
    10: (26.45, 80.35),   # Kanpur
    11: (20.30, 85.82),   # Bhubaneswar
    12: (16.51, 80.62),   # Vijayawada
    13: (21.25, 81.63),   # Raipur
    14: (22.80, 86.18),   # Jamshedpur
    15: (30.90, 75.85),   # Ludhiana
    16: (17.69, 83.22),   # Vizag
}

# ── Helper: build network figure ─────────────────────────────────────────────
def build_network_fig(flows_cost, flows_emis=None, selected_commodity=None):
    fig = go.Figure()

    # Draw arcs — traction color base
    drawn = set()
    for (i, j) in ARCS:
        if (j, i) in drawn or (i, j) in drawn:
            continue
        drawn.add((i, j))
        lat1, lon1 = NODE_COORDS[i]
        lat2, lon2 = NODE_COORDS[j]
        trac = ARC_TRACTION.get((i, j), "diesel")
        col = "rgba(88,166,255,0.18)" if trac == "electric" else "rgba(240,136,62,0.18)"
        fig.add_trace(go.Scattergeo(
            lat=[lat1, lat2, None], lon=[lon1, lon2, None],
            mode="lines",
            line=dict(width=1.2, color=col),
            showlegend=False, hoverinfo="skip"
        ))

    # Draw flow arcs for selected result
    comms_to_show = [selected_commodity] if selected_commodity else list(COMMODITIES.keys())
    comm_colors = {1: "#f78166", 2: "#3fb950", 3: "#58a6ff", 4: "#f0883e"}

    drawn_flows = {}
    for k in comms_to_show:
        if k not in flows_cost:
            continue
        for (i, j), flow in flows_cost[k].items():
            if flow < 0.5:
                continue
            key = (min(i,j), max(i,j))
            drawn_flows[key] = drawn_flows.get(key, 0) + flow

    max_flow = max(drawn_flows.values()) if drawn_flows else 1
    for (i, j), total_flow in drawn_flows.items():
        lat1, lon1 = NODE_COORDS[i]
        lat2, lon2 = NODE_COORDS[j]
        width = 1.5 + 6 * (total_flow / max_flow)
        fig.add_trace(go.Scattergeo(
            lat=[lat1, lat2, None], lon=[lon1, lon2, None],
            mode="lines",
            line=dict(width=width, color=COLORS["blue"]),
            showlegend=False,
            hovertemplate=f"{NODES[i]} → {NODES[j]}<br>Flow: {total_flow:.1f} MT<extra></extra>"
        ))

    # Draw nodes
    lats = [NODE_COORDS[n][0] for n in NODES]
    lons = [NODE_COORDS[n][1] for n in NODES]
    names = [NODES[n] for n in NODES]
    hubs = [1, 2, 3, 4]
    sizes = [18 if n in hubs else 12 for n in NODES]
    colors_node = [COLORS["orange"] if n in hubs else COLORS["blue"] for n in NODES]

    fig.add_trace(go.Scattergeo(
        lat=lats, lon=lons,
        mode="markers+text",
        marker=dict(size=sizes, color=colors_node,
                    line=dict(width=1.5, color="#0d1117")),
        text=names, textposition="top center",
        textfont=dict(size=9, color="#e6edf3"),
        hovertemplate="%{text}<extra></extra>",
        showlegend=False
    ))

    fig.update_layout(
        **{k: v for k, v in layout().items() if k not in ['xaxis', 'yaxis', 'margin']},
        geo=dict(
            scope="asia",
            center=dict(lat=22, lon=80),
            projection_scale=4.5,
            bgcolor="#0d1117",
            landcolor="#1c2230",
            oceancolor="#0d1117",
            showocean=True,
            coastlinecolor="#30363d",
            countrycolor="#30363d",
            showlakes=False,
            showrivers=False,
            resolution=50,
        ),
        height=500,
        margin=dict(l=0, r=0, t=10, b=0),
    )
    return fig

# ── Helper: pareto figure ────────────────────────────────────────────────────
def build_pareto_fig(pareto, cost_opt, emis_opt, heuristic, selected_pt=None):
    costs = [p["Z1"] / 1e7 for p in pareto]
    emiss = [p["Z2"] / 1e9 for p in pareto]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=emiss, y=costs, mode="lines+markers",
        line=dict(color=COLORS["blue"], width=2.5),
        marker=dict(size=10, color=COLORS["blue"],
                    line=dict(width=2, color="#0d1117")),
        name="Pareto Frontier",
        hovertemplate="Cost: Rs %{y:,.0f} Cr<br>Emissions: %{x:.4f} Mt-CO₂<extra></extra>"
    ))

    # Highlight selected point
    if selected_pt is not None:
        fig.add_trace(go.Scatter(
            x=[selected_pt["Z2"] / 1e9], y=[selected_pt["Z1"] / 1e7],
            mode="markers",
            marker=dict(size=18, color=COLORS["purple"],
                        symbol="star", line=dict(width=2, color="#0d1117")),
            name="Your Selection", showlegend=True
        ))

    # Extreme points
    fig.add_trace(go.Scatter(
        x=[cost_opt["Z2"] / 1e9], y=[cost_opt["Z1"] / 1e7],
        mode="markers", marker=dict(size=16, color=COLORS["orange"],
                                     symbol="diamond", line=dict(width=2, color="#0d1117")),
        name="Cost-Optimal",
        hovertemplate="Cost-Optimal<br>Rs %{y:,.0f} Cr | %{x:.4f} Mt-CO₂<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=[emis_opt["Z2"] / 1e9], y=[emis_opt["Z1"] / 1e7],
        mode="markers", marker=dict(size=16, color=COLORS["green"],
                                     symbol="diamond", line=dict(width=2, color="#0d1117")),
        name="Emission-Optimal",
        hovertemplate="Emission-Optimal<br>Rs %{y:,.0f} Cr | %{x:.4f} Mt-CO₂<extra></extra>"
    ))

    # Greedy heuristic
    g_cost = heuristic["greedy"]["Z1"] / 1e7
    g_emis = heuristic["greedy"]["Z2"] / 1e9
    fig.add_trace(go.Scatter(
        x=[g_emis], y=[g_cost],
        mode="markers", marker=dict(size=14, color=COLORS["red"],
                                     symbol="triangle-up", line=dict(width=2, color="#0d1117")),
        name="Greedy Heuristic",
        hovertemplate="Greedy Heuristic<br>Rs %{y:,.0f} Cr | %{x:.4f} Mt-CO₂<extra></extra>"
    ))

    fig.update_layout(**layout(
        xaxis_title="Total CO₂ Emissions (Mt-CO₂)",
        yaxis_title="Total Logistics Cost (Rs Crore)",
        legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
        height=420,
        title=dict(text="Pareto Frontier: Cost vs Emissions", font=dict(size=15), x=0.02)
    ))
    return fig

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🚂 IR Freight Optimizer")
    st.markdown("<p style='color:#8b949e;font-size:0.8rem;'>CE 749 · IIT Bombay · 25M1528</p>",
                unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio("Navigate", [
        "🏠  Overview",
        "🎛️  Interactive Solver",
        "🗺️  Network Map",
        "📈  Pareto Analysis",
        "🔧  Sensitivity Analysis",
    ])
    st.markdown("---")
    st.markdown("""
    <div style='color:#8b949e;font-size:0.75rem;line-height:1.6'>
    <b style='color:#e6edf3'>Model:</b> Bi-Objective MCF-LP<br>
    <b style='color:#e6edf3'>Network:</b> 16 nodes · 50 arcs<br>
    <b style='color:#e6edf3'>Demand:</b> 435 MT/year · 28 OD pairs<br>
    <b style='color:#e6edf3'>Solver:</b> PuLP + CBC<br>
    <b style='color:#e6edf3'>Method:</b> ε-Constraint Pareto
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  LOAD DATA (with spinner)
# ══════════════════════════════════════════════════════════════════════════════
with st.spinner("⚙️ Running LP solver — please wait (~5 sec)..."):
    cost_opt = get_cost_optimal()
    emis_opt = get_emis_optimal()
    pareto, _, _ = get_pareto()
    heuristic    = get_heuristic(cost_opt["Z1"], cost_opt["Z2"])

# Derived metrics
cp   = (emis_opt["Z1"] - cost_opt["Z1"]) / cost_opt["Z1"] * 100
es   = (cost_opt["Z2"] - emis_opt["Z2"]) / cost_opt["Z2"] * 100
cbp  = (emis_opt["Z1"] - cost_opt["Z1"]) / ((cost_opt["Z2"] - emis_opt["Z2"]) / 1000)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if "Overview" in page:
    st.markdown("""
    <div class='hero-banner'>
        <div class='hero-title'>🚂 Bi-Objective Freight Optimization<br>Indian Railways · Golden Quadrilateral</div>
        <div class='hero-subtitle'>Multi-Commodity Flow LP with Transshipment, Backhaul & Green Routing</div>
        <div style='margin-top:14px'>
            <span class='hero-tag'>CE 749</span>
            <span class='hero-tag'>IIT Bombay</span>
            <span class='hero-tag'>LP + ε-Constraint</span>
            <span class='hero-tag'>16 nodes · 50 arcs · 4 commodities</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Key metrics row 1 ────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>Rs {cost_opt['Z1']/1e7:,.0f} Cr</div>
            <div class='metric-label'>Cost-Optimal Z₁</div>
            <div class='metric-delta-good'>Minimum achievable cost</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{cost_opt['Z2']/1e9:.4f} Mt</div>
            <div class='metric-label'>Cost-Optimal CO₂ (Mt-CO₂)</div>
            <div class='metric-delta-warn'>Highest emissions</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{es:.2f}%</div>
            <div class='metric-label'>Max Emission Saving</div>
            <div class='metric-delta-good'>At +{cp:.1f}% cost premium</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>Rs {cbp/1000:.0f}k</div>
            <div class='metric-label'>Carbon Breakeven (Rs/tCO₂)</div>
            <div class='metric-delta-warn'>Carbon price threshold</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Second row ───────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>10.22%</div>
            <div class='metric-label'>Heuristic Cost Gap</div>
            <div class='metric-delta-warn'>Rs {(heuristic['greedy']['Z1']-heuristic['optimal']['Z1'])/1e7:,.0f} Cr extra</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>25.8%</div>
            <div class='metric-label'>Cost from Backhaul</div>
            <div class='metric-delta-warn'>Hidden cost — Rs {cost_opt['Z1_backhaul']/1e7:,.0f} Cr</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>435 MT</div>
            <div class='metric-label'>Total Annual Demand</div>
            <div class='metric-delta-good'>28 OD pairs · 4 commodities</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{len(pareto)} pts</div>
            <div class='metric-label'>Pareto Frontier Points</div>
            <div class='metric-delta-good'>ε-constraint method</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Insights ──────────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Key Findings</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='insight-box'>✅ <b>10.22% cost savings</b> (Rs 10,185 Cr/year) over greedy routing</div>
        <div class='insight-box'>✅ <b>9.69% fewer emissions</b> (0.99 Mt-CO₂) vs naive dispatching</div>
        <div class='insight-box'>✅ <b>8.66% emission cut</b> achievable at only 15.45% cost premium</div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='warning-box'>⚠️ <b>25.8% of total cost</b> is invisible backhaul — ignored by IR's current models</div>
        <div class='info-box'>ℹ️ <b>Raipur→Delhi:</b> shortest diesel route is 3.5× dirtier than EDFC alternative</div>
        <div class='info-box'>ℹ️ <b>70 MT diesel capacity</b> is the binding constraint for cost efficiency</div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    # ── Mini Pareto preview ───────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Pareto Frontier Preview</div>", unsafe_allow_html=True)
    fig = build_pareto_fig(pareto, cost_opt, emis_opt, heuristic)
    st.plotly_chart(fig, width='stretch')

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: INTERACTIVE SOLVER
# ══════════════════════════════════════════════════════════════════════════════
elif "Solver" in page:
    st.markdown("<div class='hero-title' style='margin-bottom:8px'>🎛️ Interactive Solver</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e'>Set an emission budget using the slider. The LP will find the cheapest routing that stays within that budget.</p>", unsafe_allow_html=True)

    z2_min = emis_opt["Z2"] / 1e9
    z2_max = cost_opt["Z2"] / 1e9

    col_ctrl, col_res = st.columns([1, 2])
    with col_ctrl:
        st.markdown("<div class='section-header'>Emission Budget (ε)</div>", unsafe_allow_html=True)
        eps_val = st.slider(
            "Max CO₂ allowed (Mt-CO₂)",
            min_value=float(round(z2_min, 3)),
            max_value=float(round(z2_max, 3)),
            value=float(round(z2_max, 3)),
            step=0.01,
            format="%.3f Mt"
        )

        pct_of_max = (eps_val - z2_min) / (z2_max - z2_min) * 100
        if pct_of_max > 95:
            st.markdown("<div class='info-box'>📌 <b>Near cost-optimal</b> — minimal green premium</div>", unsafe_allow_html=True)
        elif pct_of_max > 50:
            st.markdown("<div class='info-box'>⚖️ <b>Balanced zone</b> — moderate cost increase, significant emission cut</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='insight-box'>🌿 <b>Near emission-optimal</b> — maximum green routing</div>", unsafe_allow_html=True)

    with st.spinner("Solving LP..."):
        if eps_val >= z2_max - 0.005:
            result = cost_opt
        elif eps_val <= z2_min + 0.005:
            result = emis_opt
        else:
            result = solve_epsilon(eps_val)

    with col_res:
        if result["Z1"]:
            cost_pct  = (result["Z1"] - cost_opt["Z1"]) / cost_opt["Z1"] * 100
            emis_save = (cost_opt["Z2"] - result["Z2"]) / cost_opt["Z2"] * 100

            r1, r2, r3 = st.columns(3)
            with r1:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>Rs {result['Z1']/1e7:,.0f}</div>
                    <div class='metric-label'>Total Cost (Crore)</div>
                    <div class='metric-delta-warn'>+{cost_pct:.2f}% vs cost-optimal</div>
                </div>""", unsafe_allow_html=True)
            with r2:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{result['Z2']/1e9:.4f}</div>
                    <div class='metric-label'>Emissions (Mt-CO₂)</div>
                    <div class='metric-delta-good'>-{emis_save:.2f}% saved</div>
                </div>""", unsafe_allow_html=True)
            with r3:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>+{cost_pct:.1f}%</div>
                    <div class='metric-label'>Green Premium</div>
                    <div class='metric-delta-good'>For -{emis_save:.1f}% emissions</div>
                </div>""", unsafe_allow_html=True)

            # Cost breakdown bar
            st.markdown("<div class='section-header'>Cost Breakdown</div>", unsafe_allow_html=True)
            bd = {
                "Component": ["Arc Flow (Tariff)", "Backhaul (Empty Wagons)", "Transshipment (Yards)"],
                "Value (Rs Crore)": [
                    result["Z1_flow"] / 1e7,
                    result["Z1_backhaul"] / 1e7,
                    result["Z1_transship"] / 1e7,
                ],
            }
            bd_df = pd.DataFrame(bd)
            fig_bd = go.Figure(go.Bar(
                x=bd_df["Value (Rs Crore)"],
                y=bd_df["Component"],
                orientation="h",
                marker=dict(color=[COLORS["blue"], COLORS["red"], COLORS["orange"]],
                            line=dict(width=0)),
                text=[f"Rs {v:,.0f} Cr ({v/sum(bd['Value (Rs Crore)'])*100:.1f}%)"
                      for v in bd_df["Value (Rs Crore)"]],
                textposition="outside", textfont=dict(color="#e6edf3", size=11),
            ))
            fig_bd.update_layout(**layout(
                height=200, xaxis_title="Rs Crore",
                margin=dict(l=180, r=80, t=20, b=30)
            ))
            st.plotly_chart(fig_bd, width='stretch')

            # Pareto with selected point highlighted
            st.markdown("<div class='section-header'>Position on Pareto Frontier</div>", unsafe_allow_html=True)
            fig_p = build_pareto_fig(pareto, cost_opt, emis_opt, heuristic, selected_pt=result)
            st.plotly_chart(fig_p, width='stretch')
        else:
            st.error(f"❌ Infeasible — emission budget of {eps_val:.3f} Mt-CO₂ is too tight for this network.")

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: NETWORK MAP
# ══════════════════════════════════════════════════════════════════════════════
elif "Network" in page:
    st.markdown("<div class='hero-title' style='margin-bottom:8px'>🗺️ Network Flow Map</div>", unsafe_allow_html=True)

    col_ctrl, _ = st.columns([1, 3])
    with col_ctrl:
        view_mode = st.selectbox("Show routing for:", ["Cost-Optimal", "Emission-Optimal"])
        comm_names = {0: "All Commodities", **{k: v for k, v in COMMODITIES.items()}}
        sel_comm = st.selectbox("Filter commodity:", list(comm_names.keys()),
                                 format_func=lambda x: comm_names[x])

    flows = cost_opt["flows"] if view_mode == "Cost-Optimal" else emis_opt["flows"]
    sc = None if sel_comm == 0 else sel_comm

    fig = build_network_fig(flows, selected_commodity=sc)
    st.plotly_chart(fig, width='stretch')

    # Arc traction legend
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='info-box'>
        🔵 <b>Blue arcs</b> = Electrified corridors (0.010 kgCO₂/tonne-km)<br>
        🟠 <b>Orange arcs</b> = Diesel corridors (0.035 kgCO₂/tonne-km) — 3.5× dirtier
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='info-box'>
        🟠 <b>Orange nodes</b> = GQ hubs (Delhi, Mumbai, Chennai, Kolkata)<br>
        🔵 <b>Blue nodes</b> = Junction / origin / destination cities
        </div>""", unsafe_allow_html=True)

    # Flow table
    st.markdown("<div class='section-header'>Top 10 Flows</div>", unsafe_allow_html=True)
    rows = []
    for k, arcs in flows.items():
        if sc and k != sc:
            continue
        for (i, j), v in arcs.items():
            if v > 0.5:
                rows.append({
                    "Commodity": COMMODITIES[k],
                    "From": NODES[i], "To": NODES[j],
                    "Flow (MT)": round(v, 1),
                    "Traction": ARC_TRACTION.get((i, j), "?").capitalize(),
                    "Dist (km)": ARC_DISTANCES.get((i, j), 0),
                })
    if rows:
        df = pd.DataFrame(rows).sort_values("Flow (MT)", ascending=False).head(10)
        st.dataframe(df, width='stretch', hide_index=True,
                     column_config={"Traction": st.column_config.TextColumn(
                         "Traction", help="Electric or Diesel")})

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: PARETO ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif "Pareto" in page:
    st.markdown("<div class='hero-title' style='margin-bottom:8px'>📈 Pareto Frontier Analysis</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e'>Every point on this curve is an efficient solution — no other routing can reduce both cost and emissions simultaneously.</p>", unsafe_allow_html=True)

    fig = build_pareto_fig(pareto, cost_opt, emis_opt, heuristic)
    st.plotly_chart(fig, width='stretch')

    # Pareto table
    st.markdown("<div class='section-header'>All Pareto Points</div>", unsafe_allow_html=True)
    min_z1 = min(p["Z1"] for p in pareto)
    rows = []
    for i, p in enumerate(sorted(pareto, key=lambda x: x["Z2"])):
        cost_premium = (p["Z1"] - min_z1) / min_z1 * 100
        emis_saved   = (cost_opt["Z2"] - p["Z2"]) / cost_opt["Z2"] * 100
        rows.append({
            "Point": i + 1,
            "Cost (Rs Crore)": f"{p['Z1']/1e7:,.0f}",
            "CO₂ (Mt-CO₂)": f"{p['Z2']/1e9:.4f}",
            "Cost Premium %": f"+{cost_premium:.2f}%",
            "Emission Saving %": f"-{emis_saved:.2f}%",
        })
    st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)

    # Heuristic gap
    st.markdown("<div class='section-header'>LP Optimal vs Greedy Heuristic</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        opt_z1  = heuristic["optimal"]["Z1"] / 1e7
        grdy_z1 = heuristic["greedy"]["Z1"] / 1e7
        fig_h = go.Figure()
        fig_h.add_trace(go.Bar(
            x=["MCF-LP Optimal", "Greedy Heuristic"],
            y=[opt_z1, grdy_z1],
            marker=dict(color=[COLORS["blue"], COLORS["red"]]),
            text=[f"Rs {opt_z1:,.0f} Cr", f"Rs {grdy_z1:,.0f} Cr"],
            textposition="outside", textfont=dict(color="#e6edf3", size=11),
        ))
        fig_h.add_annotation(
            x=0.5, y=max(grdy_z1 * 1.02, opt_z1 * 1.1),
            xref="paper", text=f"Gap: +{heuristic['cost_gap_pct']:.2f}%",
            showarrow=False, font=dict(color=COLORS["red"], size=14, family="Inter"),
        )
        fig_h.update_layout(**layout(
            yaxis_title="Total Cost (Rs Crore)",
            height=320, title=dict(text="Cost Comparison", font=dict(size=13))
        ))
        st.plotly_chart(fig_h, width='stretch')

    with col2:
        opt_z2  = heuristic["optimal"]["Z2"] / 1e9
        grdy_z2 = heuristic["greedy"]["Z2"] / 1e9
        fig_he = go.Figure()
        fig_he.add_trace(go.Bar(
            x=["MCF-LP Optimal", "Greedy Heuristic"],
            y=[opt_z2, grdy_z2],
            marker=dict(color=[COLORS["green"], COLORS["red"]]),
            text=[f"{opt_z2:.4f} Mt", f"{grdy_z2:.4f} Mt"],
            textposition="outside", textfont=dict(color="#e6edf3", size=11),
        ))
        fig_he.add_annotation(
            x=0.5, y=max(grdy_z2 * 1.02, opt_z2 * 1.1),
            xref="paper", text=f"Gap: +{heuristic['emission_gap_pct']:.2f}%",
            showarrow=False, font=dict(color=COLORS["red"], size=14, family="Inter"),
        )
        fig_he.update_layout(**layout(
            yaxis_title="Total CO₂ (Mt-CO₂)",
            height=320, title=dict(text="Emissions Comparison", font=dict(size=13))
        ))
        st.plotly_chart(fig_he, width='stretch')

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: SENSITIVITY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif "Sensitivity" in page:
    st.markdown("<div class='hero-title' style='margin-bottom:8px'>🔧 Sensitivity Analysis</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e'>How do cost and emissions change as diesel corridor capacity varies from 40 to 100 MT/year?</p>", unsafe_allow_html=True)

    with st.spinner("Running sensitivity analysis..."):
        sens = get_sensitivity()

    valid = [r for r in sens if r["Z1"] is not None]
    caps  = [r["capacity"] for r in valid]
    z1s   = [r["Z1"] for r in valid]
    z2s   = [r["Z2"] for r in valid]

    fig_s = make_subplots(rows=1, cols=2, subplot_titles=["Cost vs Diesel Capacity", "Emissions vs Diesel Capacity"])

    fig_s.add_trace(go.Scatter(
        x=caps, y=z1s, mode="lines+markers",
        line=dict(color=COLORS["red"], width=2.5),
        marker=dict(size=9, color=COLORS["red"]),
        name="Cost (Rs Crore)",
    ), row=1, col=1)
    fig_s.add_vline(x=70, line_dash="dash", line_color="#8b949e", line_width=1.5,
                    annotation_text="Base: 70 MT", annotation_font_color="#8b949e",
                    row=1, col=1)

    fig_s.add_trace(go.Scatter(
        x=caps, y=z2s, mode="lines+markers",
        line=dict(color=COLORS["blue"], width=2.5),
        marker=dict(size=9, color=COLORS["blue"]),
        name="Emissions (Mt-CO₂)",
    ), row=1, col=2)
    fig_s.add_vline(x=70, line_dash="dash", line_color="#8b949e", line_width=1.5,
                    annotation_text="Base: 70 MT", annotation_font_color="#8b949e",
                    row=1, col=2)

    fig_s.update_layout(**layout(
        height=380, showlegend=False,
        margin=dict(l=50, r=30, t=70, b=50),
        xaxis=dict(title="Diesel Arc Capacity (MT)", **PLOTLY_LAYOUT["xaxis"]),
        yaxis=dict(title="Total Cost (Rs Crore)", **PLOTLY_LAYOUT["yaxis"]),
        xaxis2=dict(title="Diesel Arc Capacity (MT)", **PLOTLY_LAYOUT["xaxis"]),
        yaxis2=dict(title="Total Emissions (Mt-CO₂)", **PLOTLY_LAYOUT["yaxis"]),
    ))
    fig_s.update_annotations(font_size=12, font_color="#e6edf3")
    st.plotly_chart(fig_s, width='stretch')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='insight-box'>
        📌 <b>Below 70 MT:</b> Costs rise sharply — the network is forced onto longer, expensive electrified routes.<br><br>
        📌 <b>Above 70 MT:</b> Costs plateau — increasing diesel capacity beyond this point yields diminishing returns.
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='warning-box'>
        ⚠️ <b>Emissions peak at 70 MT</b> then decline — because beyond 70 MT capacity the model can reroute more efficiently, ironically reducing total distance traveled on diesel arcs.<br><br>
        ⚠️ <b>Policy implication:</b> Electrification of the Nagpur–Bhopal and Raipur–Nagpur corridors is the single highest-leverage infrastructure intervention.
        </div>""", unsafe_allow_html=True)

    # Sensitivity table
    st.markdown("<div class='section-header'>Sensitivity Data</div>", unsafe_allow_html=True)
    df_s = pd.DataFrame(valid)
    df_s.columns = ["Diesel Capacity (MT)", "Cost (Rs Crore)", "Emissions (Mt-CO₂)", "Status"]
    df_s["Cost (Rs Crore)"] = df_s["Cost (Rs Crore)"].map(lambda x: f"{x:,.0f}")
    df_s["Emissions (Mt-CO₂)"] = df_s["Emissions (Mt-CO₂)"].map(lambda x: f"{x:.4f}")
    st.dataframe(df_s, width='stretch', hide_index=True)
