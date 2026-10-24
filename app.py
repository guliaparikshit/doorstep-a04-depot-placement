"""
DEPOTIQ · Team 6 · A4 Geospatial Micro-Depot Placement
------------------------------------------------------
TA4 Streamlit dashboard — refined presentation and responsive layout.

Requires existing project outputs from TA2, TA3 and TA4:
  data/processed/clean_bookings.csv
  results/depots.csv
  results/*comparison*.csv
  results/plots/*.png and recommended_depots_map.html

All nine sections preserved. Measurements are loaded from project files.
Candidate depots remain provisional, and distances are straight-line estimates.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# 01 — PATHS, COLORS, PAGE CONFIGURATION
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw" / "bookings.csv"
CLEAN = ROOT / "data" / "processed" / "clean_bookings.csv"
RESULTS = ROOT / "results"
PLOTS = RESULTS / "plots"

C = {
    "bg": "#061813",
    "surface": "#0d241e",
    "surface2": "#102d25",
    "border": "#25483d",
    "text": "#f6fbf9",
    "muted": "#a7c5b9",
    "mint": "#67e8b3",
    "cyan": "#61cbee",
    "amber": "#ffd17a",
    "violet": "#9d91fa",
    "rose": "#fb8f9d",
}

st.set_page_config(
    page_title="DEPOTIQ | Micro-Depot Intelligence",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# 02 — PRESENTATION SYSTEM
# ---------------------------------------------------------------------------
# Intentional: sidebar, fonts, responsive metrics and chart panel geometry are
# governed here, so Streamlit's default container sizes don't clip content.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;650;700;750;800;900&display=swap');
:root { color-scheme:dark; --side:276px; --mint:#67e8b3; --muted:#9fbeb3; }
html,body,.stApp,[data-testid="stAppViewContainer"] {
    font-family:'Inter',system-ui,-apple-system,sans-serif !important;
    color:#f5fbf8 !important;
}
[data-testid="stAppViewContainer"] {
    background:
      radial-gradient(ellipse at 90% 1%,rgba(35,109,79,.24),transparent 37%),
      radial-gradient(ellipse at 20% 83%,rgba(19,90,72,.12),transparent 48%),
      #061813;
}
/* Make the left rail compact; prevent the large blank area from V3. */
[data-testid="stSidebar"] {
    width:var(--side) !important;
    min-width:var(--side) !important;
    background:linear-gradient(180deg,#061b16 0%,#071710 100%) !important;
    border-right:1px solid #244337;
}
[data-testid="stSidebar"] > div:first-child {
    width:var(--side)!important;
    padding-top:1.05rem!important;
}
[data-testid="stSidebarUserContent"] {
    padding:1.1rem .9rem 1.8rem !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] > label{display:none!important;}
[data-testid="stSidebar"] div[role="radiogroup"]{gap:2px;}
[data-testid="stSidebar"] div[role="radiogroup"] label{
    border-radius:10px!important;border:1px solid transparent;
    padding:8px 10px!important;min-height:38px!important;
    transition:background .15s,border-color .15s;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover{background:#14342a!important;}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){
    background:#1b3d32!important;border-color:#356955!important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label p{
    font-size:13px!important;letter-spacing:-.01em!important;
    color:#f0faf5!important;font-weight:650!important;margin:0!important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#a9c9ba;}
[data-testid="stSidebar"] hr{margin:13px 0!important;border-color:#254438!important;}
/* Keep the native Streamlit toolbar, but fix a small project title beneath it. */
header[data-testid="stHeader"] {background:#08100ffa !important;height:2.7rem!important;}
.di-topbar {
    position:fixed;top:2.7rem;left:var(--side);right:0;height:43px;
    background:rgba(7,26,20,.96);border-bottom:1px solid #234438;
    backdrop-filter:blur(14px);z-index:90;display:flex;align-items:center;
    justify-content:space-between;padding:0 29px;pointer-events:none;
}
.di-topbar .wordmark{font-size:13px;font-weight:850;letter-spacing:.035em;color:#f2fff8;}
.di-topbar .wordmark span{color:#69e9b5;}
.di-topbar .trail{font-size:11px;color:#a9c9b9;font-weight:600;}
section[data-testid="stMain"] .block-container {
    max-width:1650px !important;padding:6.15rem clamp(17px,2.3vw,39px) 3.5rem !important;
}
/* Use sensible fonts rather than oversized headings everywhere. */
h1,h2,h3,h4,.stMarkdown h1,.stMarkdown h2,.stMarkdown h3{
    font-family:'Inter',system-ui,sans-serif!important;
    color:#f3fcf7!important;letter-spacing:-.035em!important;
}
h1{font-size:clamp(25px,2.35vw,38px)!important;line-height:1.20!important;font-weight:800!important;}
h2{font-size:clamp(21px,1.65vw,27px)!important;line-height:1.30!important;font-weight:780!important;}
h3{font-size:clamp(18px,1.25vw,21px)!important;line-height:1.32!important;font-weight:760!important;}
p,li{line-height:1.65;}
[data-testid="stMarkdownContainer"] p{overflow-wrap:anywhere;}
hr{border-color:#25453a!important;}
/* Clean, compact hero; content scrolls, small header stays visible. */
.di-hero{
    position:relative;overflow:hidden;border:1px solid #315c48;
    border-radius:21px;margin:0 0 23px;
    min-height:210px;padding:31px 35px;
    background:linear-gradient(105deg,#0b2920 0%,#0b3226 58%,#164b3b 100%);
}
.di-hero:before{content:'';pointer-events:none;position:absolute;
    right:-3%;top:-100%;width:48%;aspect-ratio:1;border-radius:50%;
    background:repeating-radial-gradient(circle,transparent 0 28px,
        rgba(116,239,188,.105) 29px 30px,transparent 31px 58px);
}
.di-hero:after{content:'';pointer-events:none;position:absolute;
    right:7%;bottom:-62%;width:230px;height:230px;border-radius:50%;
    background:radial-gradient(circle,rgba(83,209,168,.18),transparent 65%);
}
.di-hero *{position:relative;z-index:1;}
.di-eyebrow {display:inline-flex;align-items:center;gap:8px;
    color:#92f4c3;font-size:10px;text-transform:uppercase;
    letter-spacing:2.2px;font-weight:800;margin-bottom:15px;}
.di-hero h1{font-size:clamp(27px,2.8vw,42px)!important;max-width:1050px;
    margin:0 0 15px!important;line-height:1.14!important;}
.di-hero p{font-size:14px!important;line-height:1.75!important;
    color:#bed6ca;max-width:800px;margin:0!important;}
.di-brand{font-weight:850;font-size:23px;letter-spacing:-1.15px;color:#f4fff9;
    padding:10px 6px 0;}
.di-brand span{color:#65e0aa;}
.di-brand-sub{font-size:11px;color:#a6c7b8;margin:4px 6px 15px;line-height:1.6;}
.di-sidebar-tag {font-size:10px!important;text-transform:uppercase;
    letter-spacing:1.2px;font-weight:800;color:#70dfa9;margin:5px 6px 7px;}
.di-sidebar-foot{background:#0e2c22;border:1px solid #275544;
    border-radius:13px;padding:14px;margin:12px 2px 8px;}
.di-sidebar-foot b{font-size:12px;color:#eafff2;}
.di-sidebar-foot p{font-size:11px!important;color:#a2c5b4!important;margin:6px 0 0!important;}
/* KPI values never escape their cards. At narrow widths use fewer columns. */
.di-kpis{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));
    gap:12px;margin:0 0 25px;width:100%;}
.di-kpi{min-width:0;overflow:hidden;background:linear-gradient(140deg,#123327,#0a241b);
    border:1px solid #285543;border-radius:16px;padding:16px 15px;min-height:127px;
    display:flex;flex-direction:column;justify-content:space-between;}
.di-kpi .label{font-size:11px!important;line-height:1.45!important;
    font-weight:670;color:#b9d0c2;overflow-wrap:break-word;}
.di-kpi .number{font-size:clamp(20px,1.75vw,29px)!important;
    font-weight:830;color:#fff;letter-spacing:-.052em;line-height:1.2;
    margin:11px 0 8px;overflow-wrap:anywhere;}
.di-kpi .caption{font-size:10px!important;color:#74dfab;
    line-height:1.5;overflow-wrap:break-word;}
/* Reusable custom panels, labels, explanatory notes. */
.di-panel-title{font-size:17px;font-weight:780;color:#f5fff9;
    letter-spacing:-.03em;margin:4px 0 5px;line-height:1.4;}
.di-panel-sub{font-size:11px;color:#a3c3b5;line-height:1.6;margin:0 0 12px;}
.di-section{font-size:10px;letter-spacing:2px;text-transform:uppercase;
    font-weight:800;color:#80ecc0;margin:10px 0 14px;}
.di-note{padding:14px 17px;border:1px solid #35674e;
    border-radius:12px;background:#103429;color:#c5e9d4;
    font-size:12px;line-height:1.8;margin:14px 0;}
.di-note.warn{border-color:#846a38;background:rgba(108,80,24,.16);color:#f4dca5;}
.di-microgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:12px 0 20px;}
.di-mini{min-width:0;border-radius:13px;background:#0f3025;
    border:1px solid #2c5845;padding:15px 17px;}
.di-mini b{display:block;color:#edfdf4;font-size:13px;margin-bottom:8px;}
.di-mini p{font-size:11px;line-height:1.7;color:#afcabc;margin:0;}
/* Give charts true panel width and consistent heights. */
[data-testid="stVerticalBlockBorderWrapper"] {background:rgba(10,36,27,.74);
    border:1px solid #315247!important;border-radius:17px!important;}
[data-testid="stVerticalBlockBorderWrapper"] > div{min-width:0;}
[data-testid="stDataFrame"]{border:1px solid #315647;border-radius:12px;overflow:hidden;}
[data-testid="stColumn"],[data-testid="stVerticalBlock"]{min-width:0;}
[data-testid="stPlotlyChart"]{width:100%!important;min-width:0;}
[data-testid="stPlotlyChart"] > div{width:100%!important;}
/* Controls must be usable on dark colors. */
[data-testid="stDownloadButton"] button,.stButton button,[data-testid="stLinkButton"] a{
    background:linear-gradient(125deg,#154e3c,#206c51)!important;
    border:1px solid #36896b!important;color:#eafff3!important;
    border-radius:11px!important;font-weight:700!important;
    min-height:40px!important;
}
[data-testid="stDownloadButton"] button:hover,.stButton button:hover,
[data-testid="stLinkButton"] a:hover{background:#267a57!important;border-color:#82efba!important;}
[data-testid="stSelectbox"] > div > div,[data-testid="stMultiSelect"] > div > div,
[data-testid="stSlider"] {color:#e8fdf2!important;}
/* Keep the charts readable at tablet / smaller laptop sizes. */
@media(max-width:1600px){
 .di-kpi{padding:13px 12px;min-height:119px;}
 .di-kpi .number{font-size:clamp(19px,1.7vw,27px)!important;}
}
@media(max-width:1250px){
 .di-kpis{grid-template-columns:repeat(3,minmax(0,1fr));}
 .di-kpi .number{font-size:27px!important;}
}
@media(max-width:820px){
 :root{--side:245px;}
 .di-kpis{grid-template-columns:repeat(2,minmax(0,1fr));}
 .di-microgrid{grid-template-columns:1fr;}
 .di-hero{padding:24px 22px;min-height:185px;}
 .di-topbar{padding:0 15px;}
}
@media(max-width:650px){
 .di-topbar{left:0;top:2.7rem;}
 .di-topbar .trail{display:none;}
 .di-kpis{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;}
 .di-kpi .number{font-size:22px!important;}
 section[data-testid="stMain"] .block-container{padding:6.05rem 12px 3rem!important;}
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 03 — DATA LOADING & DATA-BASED NUMBERS
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as exc:
        st.warning(f"Could not load {path.name}: {exc}")
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def read_dashboard_summary(path: Path) -> dict:
    """Load published aggregate counts when individual records are absent."""
    if not path.is_file():
        return {}
    try:
        with path.open(encoding="utf-8") as f:
            summary = json.load(f)
        if not isinstance(summary, dict):
            return {}
        return summary
    except (OSError, ValueError, TypeError) as exc:
        st.warning(f"Could not load dashboard summary: {exc}")
        return {}


def aggregate_counts(field: str) -> pd.Series:
    """Use full local data or the published area/zone aggregates."""
    if field in bookings.columns:
        return bookings[field].value_counts()
    key = "bookings_by_" + field
    values = dashboard_summary.get(key, {})
    if isinstance(values, dict) and values:
        return pd.Series({str(k): int(v) for k, v in values.items()}, dtype=int).sort_values(ascending=False)
    return pd.Series(dtype=int)


dashboard_summary = read_dashboard_summary(RESULTS / "dashboard_summary.json")

bookings = read_csv(CLEAN)
raw = read_csv(RAW)
depots = read_csv(RESULTS / "depots.csv")
km = read_csv(RESULTS / "kmeans_comparison.csv")
db = read_csv(RESULTS / "dbscan_comparison.csv")
cmp = read_csv(RESULTS / "model_comparison.csv")
reliability = read_csv(RESULTS / "kmeans_reliability_summary.csv")
logs = read_csv(ROOT / "experiments.csv")

# The audited TA2 total is documented; never invent model measurements.
raw_count = (len(raw) if not raw.empty else dashboard_summary.get("original_bookings", 40660))
clean_count = (len(bookings) if not bookings.empty else dashboard_summary.get("cleaned_bookings"))
zones = (bookings["zone"].nunique() if "zone" in bookings.columns else dashboard_summary.get("zones"))
areas = (bookings["area"].nunique() if "area" in bookings.columns else dashboard_summary.get("areas"))


def number(value, suffix=""):
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        return "—"
    if isinstance(value, (int, np.integer)):
        return f"{value:,}{suffix}"
    return f"{value}{suffix}"


def mean_candidate_distance() -> float | None:
    required = {"mean_distance_km", "assigned_bookings"}
    if not required.issubset(depots.columns):
        return None
    w = pd.to_numeric(depots["assigned_bookings"], errors="coerce").fillna(0)
    dist = pd.to_numeric(depots["mean_distance_km"], errors="coerce")
    valid = dist.notna() & (w > 0)
    if not valid.any():
        return None
    return float(np.average(dist[valid], weights=w[valid]))


avg_candidate = mean_candidate_distance()


# ---------------------------------------------------------------------------
# 04 — VISUAL COMPONENT HELPERS
# ---------------------------------------------------------------------------

def safe(value) -> str:
    return html.escape(str(value), quote=True)


def topbar(active: str):
    st.markdown(
        f'<div class="di-topbar"><div class="wordmark">⌖ DEPOT<span>IQ</span>'
        f' &nbsp; / &nbsp; {safe(active)}</div>'
        '<div class="trail">TEAM 6 &nbsp; • &nbsp; A4 INTELLIGENCE PLATFORM</div></div>',
        unsafe_allow_html=True,
    )


def hero(title: str, description: str, tag: str):
    st.markdown(
        f'<section class="di-hero"><div class="di-eyebrow">✦ {safe(tag)}</div>'
        f'<h1>{safe(title)}</h1><p>{safe(description)}</p></section>',
        unsafe_allow_html=True,
    )


def kpis(items):
    html_cards = []
    for title, value, hint in items:
        html_cards.append(
            '<div class="di-kpi">'
            f'<div class="label">{safe(title)}</div>'
            f'<div class="number">{safe(value)}</div>'
            f'<div class="caption">{safe(hint)}</div>'
            '</div>'
        )
    st.markdown('<div class="di-kpis">' + ''.join(html_cards) + '</div>',
                unsafe_allow_html=True)


def panel_title(title, subtitle=""):
    st.markdown(f'<div class="di-panel-title">{safe(title)}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="di-panel-sub">{safe(subtitle)}</div>', unsafe_allow_html=True)


def section_heading(title):
    st.markdown(f'<div class="di-section">{safe(title)}</div>', unsafe_allow_html=True)


def note(message, warning=False):
    st.markdown(
        f'<div class="di-note {"warn" if warning else ""}">{safe(message)}</div>',
        unsafe_allow_html=True,
    )


def micro_cards(items):
    bits = [f'<div class="di-mini"><b>{safe(a)}</b><p>{safe(b)}</p></div>'
            for a, b in items]
    st.markdown('<div class="di-microgrid">'+''.join(bits)+'</div>',
                unsafe_allow_html=True)


def base_fig(fig: go.Figure, height=390, l=30, r=22, t=28, b=38):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        autosize=True,
        margin=dict(l=l, r=r, t=t, b=b),
        font=dict(family="Inter, Arial, sans-serif", size=12, color="#e9f9ee"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="#16432f", font_size=12, font_color="#ffffff"),
        showlegend=False,
    )
    fig.update_xaxes(showline=False, zeroline=False,
                     gridcolor="rgba(166,214,185,.10)", tickfont_size=11)
    fig.update_yaxes(showline=False, zeroline=False,
                     gridcolor="rgba(166,214,185,.13)", tickfont_size=11)
    return fig


def chart(fig: go.Figure):
    st.plotly_chart(
        fig, use_container_width=True,
        config={"displaylogo": False, "responsive": True,
                "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
    )


def horizontal_bars(labels, values, color=None, height=420, name="Bookings", suffix=""):
    labels = [str(v) for v in labels]
    vals = [float(v) for v in values]
    color = color or C["mint"]
    # Plotly displays bars from bottom to top, so reverse to show largest on top.
    fig = go.Figure(go.Bar(
        x=vals[::-1], y=labels[::-1], orientation="h",
        marker=dict(color=color, line=dict(width=0)),
        width=.62, text=[f"{v:,.0f}{suffix}" for v in vals[::-1]],
        textposition="outside", cliponaxis=False,
        hovertemplate="%{y}<br>"+name+": %{x:,.0f}"+suffix+"<extra></extra>",
    ))
    base_fig(fig, height=height, l=14, r=70, b=22)
    fig.update_layout(bargap=.35)
    fig.update_xaxes(title=None, rangemode="tozero", fixedrange=True)
    fig.update_yaxes(title=None, showgrid=False, automargin=True,
                     tickfont=dict(size=12), fixedrange=True)
    chart(fig)


def donut(labels, values, total_text, height=420):
    fig = go.Figure(go.Pie(
        labels=[str(v) for v in labels], values=[int(v) for v in values],
        hole=.68, sort=False,
        marker=dict(colors=[C["cyan"], C["violet"], C["mint"], C["amber"], C["rose"]]),
        textinfo="percent", textposition="inside",
        insidetextfont=dict(size=13, color="#07170f"),
        hovertemplate="%{label}: %{value:,} bookings (%{percent})<extra></extra>",
    ))
    base_fig(fig, height=height, l=6, r=6, b=80, t=8)
    fig.update_layout(
        showlegend=True, legend=dict(orientation="h", y=-.1, x=.5,
                                   xanchor="center", font=dict(size=11)),
        annotations=[dict(text=total_text, x=.5, y=.5, showarrow=False,
                          align="center", font=dict(size=19, color=C["text"]))],
        uniformtext_minsize=10, uniformtext_mode="hide",
    )
    chart(fig)


def trend_k(kvalues, mean_values, highlighted=5, height=460):
    x = [int(v) for v in kvalues]
    y = [float(v) for v in mean_values]
    fig = go.Figure(go.Scatter(
        x=x, y=y, mode="lines+markers",
        line=dict(color=C["mint"], width=3, shape="linear"),
        marker=dict(size=10, color=C["cyan"], line=dict(width=2, color=C["bg"])),
        fill="tozeroy", fillcolor="rgba(103,232,179,.055)",
        customdata=x,
        hovertemplate="Candidate depots: %{x}<br>Mean distance: %{y:.3f} km<extra></extra>",
    ))
    if highlighted in x:
        at = x.index(highlighted)
        fig.add_trace(go.Scatter(
            x=[x[at]], y=[y[at]], mode="markers+text",
            marker=dict(size=15, color=C["amber"], line=dict(width=3,color=C["bg"])),
            text=[f"K={highlighted}: {y[at]:.3f} km"],
            textposition="top right", textfont=dict(size=12, color=C["amber"]),
            hoverinfo="skip", showlegend=False,
        ))
    base_fig(fig, height=height, l=58, r=30, b=55, t=28)
    fig.update_xaxes(title="Number of candidate depots (K)", dtick=1, tickmode="linear")
    fig.update_yaxes(title="Mean distance (km)", rangemode="tozero")
    chart(fig)


def render_map(filename, height=580):
    path = PLOTS / filename
    if not path.exists():
        st.info(f"Map not generated yet: results/plots/{filename}")
        return
    # These HTML files are generated by this project's Folium code.
    components.html(path.read_text(encoding="utf-8"), height=height,
                    scrolling=False)
    st.caption("Interactive Folium map · Online street tiles required · Provisional site markers")


def show_png(filename, caption=None):
    path = PLOTS / filename
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.info(f"Graph not generated yet: {filename}")


def display_table(frame, columns=None, height=330):
    if frame.empty:
        st.info("The saved experiment table is not available on this machine.")
        return
    use = frame[[c for c in columns if c in frame.columns]] if columns else frame
    st.dataframe(use, hide_index=True, use_container_width=True, height=height)


def download_csv(frame, filename, label):
    if frame.empty:
        st.caption(f"{filename} is not available")
        return
    st.download_button(
        label=label, data=frame.to_csv(index=False).encode("utf-8"),
        file_name=filename, mime="text/csv", use_container_width=True,
    )


def download_asset(path, label, mime):
    if path.exists():
        st.download_button(label=label, data=path.read_bytes(),
                           file_name=path.name, mime=mime,
                           use_container_width=True)
    else:
        st.caption(f"Not generated: {path.name}")


# ---------------------------------------------------------------------------
# 05 — SIDEBAR, PERSISTENT TOP BAR
# ---------------------------------------------------------------------------
PAGES = [
    "🏠 Overview",
    "🧹 Data Quality",
    "🗺️ Demand Map",
    "🧠 K-Means",
    "🔬 DBSCAN",
    "⚖️ Model Comparison",
    "📍 Final Recommendations",
    "📥 Downloads",
    "ℹ️ About Project",
]

with st.sidebar:
    st.markdown(
        '<div class="di-brand">⌖ DEPOT<span>IQ</span></div>'
        '<div class="di-brand-sub">A4 · Intelligent Micro-Depot Placement</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown('<div class="di-sidebar-tag">Navigation</div>', unsafe_allow_html=True)
    page = st.radio("DEPOTIQ navigation", PAGES, label_visibility="collapsed")
    st.markdown(
        '<div class="di-sidebar-foot"><b>TEAM 6 · TA4</b>'
        '<p>Track A — Service as a Service<br>'
        'AI &amp; ML Thematic Assessment<br>Research prototype</p></div>',
        unsafe_allow_html=True,
    )

topbar(page.split(" ", 1)[1] if " " in page else page)

# ---------------------------------------------------------------------------
# 06 — OVERVIEW
# ---------------------------------------------------------------------------
if page == PAGES[0]:
    hero(
        "DEPOTIQ — Intelligent Micro-Depot Placement",
        "A research-driven control centre for Doorstep service demand, geographical clustering, "
        "model evaluation and practical candidate-depot planning.",
        "MICRO-DEPOT INTELLIGENCE · TEAM 6",
    )

    kpis([
        ("📚 Original bookings", f"{raw_count:,}", "Faculty source dataset"),
        ("✅ Cleaned bookings", number(clean_count), "Completed bookings"),
        ("🗺️ Zones", number(zones), "Demand regions"),
        ("🏙️ Areas", number(areas), "Service areas"),
        ("📍 Candidate depots", number(len(depots)) if not depots.empty else "—", "Current K=5 scenario"),
        ("📏 Mean distance", f"{avg_candidate:.3f} km" if avg_candidate is not None else "—", "Straight-line estimate"),
    ])

    # Main overview: large map and generous, labelled distance graph.
    map_col, curve_col = st.columns([1.15, 1], gap="large")
    with map_col:
        with st.container(border=True):
            panel_title("🗺️ Demand heatmap & candidate depots",
                        "Every completed booking contributes to the map · K=5 provisional sites")
            render_map("recommended_depots_map.html", 590)
    with curve_col:
        with st.container(border=True):
            panel_title("📉 Distance vs depot count",
                        "K-Means · Full cleaned dataset · K=1 through 10")
            if {"k", "mean_km"}.issubset(km.columns):
                trend_k(km["k"], km["mean_km"], height=525)
            else:
                show_png("kmeans_distance_vs_k.png")

    # Unlike V3, the two visualisations below each have enough width to breathe.
    section_heading("Service area intelligence")
    area_col, zone_col = st.columns([1.3, 1], gap="large")
    with area_col:
        with st.container(border=True):
            panel_title("📊 Bookings by area", "Readable labels · Hover for exact booking counts")
            area_counts = aggregate_counts("area").head(10)
            if not area_counts.empty:
                horizontal_bars(area_counts.index, area_counts.values, height=455)
            else:
                show_png("bookings_by_area.png")
    with zone_col:
        with st.container(border=True):
            panel_title("◉ Demand by zone", "Distribution of completed service bookings")
            z = aggregate_counts("zone")
            if not z.empty:
                donut(z.index, z.values, f"{int(z.sum()):,}<br>bookings", height=455)
            else:
                show_png("bookings_by_zone.png")

    section_heading("Research findings & provisional planning")
    lcol, rcol = st.columns([1.1, 1], gap="large")
    with lcol:
        with st.container(border=True):
            panel_title("⚖️ Model comparison",
                        "Both methods evaluated on the same 6,000-booking sample")
            display_table(cmp.round(3) if not cmp.empty else cmp, height=255)
    with rcol:
        with st.container(border=True):
            panel_title("📍 Recommendation snapshot", "Current provisional K=5 scenario")
            st.markdown("**K-Means is a promising baseline for candidate placement.**")
            st.caption("Its tested configuration had lower nearest-candidate distance "
                       "than DBSCAN in the common-sample comparison.")
            display_table(depots, ["depot_id", "lat", "lng", "assigned_bookings"], height=190)

    micro_cards([
        ("K-Means", "Tests 1–10 candidate counts and measures nearest-centre distance."),
        ("DBSCAN", "Detects dense booking regions and labels isolated points as noise."),
        ("Reliability", "Forty model runs across 4 settings and 10 random seeds."),
    ])
    note("Research boundary: K=5 is a planning scenario, not a cost-optimal depot count. "
         "All current sites are provisional, and distances are straight-line rather than driving distances.", True)

# ---------------------------------------------------------------------------
# 07 — DATA QUALITY
# ---------------------------------------------------------------------------
elif page == PAGES[1]:
    hero("Data Quality & Preparation",
         "From the faculty dataset to a clean, reproducible geographical demand sample.",
         "TA2 · CLEANING WORKFLOW")
    statuses = raw["status"].value_counts() if "status" in raw.columns else pd.Series(dtype=int)
    complete = int(statuses.get("completed", clean_count if clean_count is not None else 39302))
    noshow = int(statuses.get("no_show", 1344))
    flagged = int(statuses.get("duplicate", 14))
    invalid = None
    if {"lat", "lng"}.issubset(raw.columns):
        lat = pd.to_numeric(raw["lat"], errors="coerce")
        lng = pd.to_numeric(raw["lng"], errors="coerce")
        invalid = int((lat.isna() | lng.isna() | ~lat.between(-90,90) |
                       ~lng.between(-180,180)).sum())
    kpis([
        ("Source bookings", f"{raw_count:,}", "Before cleaning"),
        ("Completed", f"{complete:,}", "Retained for modelling"),
        ("No-show", f"{noshow:,}", "Excluded status"),
        ("Flagged duplicate", str(flagged), "Status, not duplicate IDs"),
        ("Invalid coords", str(invalid) if invalid is not None else "—", "Raw-data check"),
        ("Clean sample", number(clean_count), "Ready for experiments"),
    ])
    micro_cards([
        ("01 · Load", "Read the source booking records without changing the original CSV."),
        ("02 · Validate", "Check missing values, booking statuses and latitude/longitude ranges."),
        ("03 · Clean", "Keep completed bookings and save a separate processed CSV."),
    ])
    lcol, rcol = st.columns([1.1, 1], gap="large")
    with lcol:
        with st.container(border=True):
            panel_title("Booking status distribution", "Shows why 1,358 records were excluded")
            horizontal_bars(["Completed", "No-show", "Flagged duplicate"],
                            [complete,noshow,flagged],height=365)
    with rcol:
        with st.container(border=True):
            panel_title("Source missing-value audit", "Calculated from the original CSV if available")
            if not raw.empty:
                miss = raw.isna().sum().sort_values(ascending=False)
                audit = pd.DataFrame({"Field": miss.index, "Missing values": miss.values})
                display_table(audit,height=340)
            else:
                st.info("Original bookings.csv is not available in this local folder. "
                        "The verified source total is 40,660 records.")
    with st.container(border=True):
        panel_title("Cleaned booking preview", "Limited fields, for demonstration only")
        fields=[c for c in ["date", "zone", "area", "lat", "lng", "status", "vehicle_size"]
                if c in bookings.columns]
        display_table(bookings[fields].head(20) if fields else pd.DataFrame(),height=340)
    note("The 14 records labelled 'duplicate' are a booking status category; "
         "they are not evidence of repeated booking IDs. Original files remain unchanged.", True)

# ---------------------------------------------------------------------------
# 08 — DEMAND MAP
# ---------------------------------------------------------------------------
elif page == PAGES[2]:
    hero("Geographical Demand Explorer",
         "Inspect where service demand concentrates across Gurugram and how provisional sites cover it.",
         "INTERACTIVE SPATIAL ANALYSIS")
    view = st.radio("Select map view", ["Booking heatmap", "Heatmap + candidate depots"],
                    horizontal=True, index=1)
    with st.container(border=True):
        panel_title("🗺️ Doorstep booking geography", "Zoom, pan and switch map layers directly")
        render_map("booking_demand_map.html" if view=="Booking heatmap"
                   else "recommended_depots_map.html", 685)
    lcol, rcol = st.columns([1.3, 1], gap="large")
    with lcol:
        with st.container(border=True):
            panel_title("Service areas ranked", "Completed booking counts by area")
            v = aggregate_counts("area")
            if not v.empty:
                horizontal_bars(v.index[:10], v.values[:10], height=465)
            else:
                show_png("bookings_by_area.png")
    with rcol:
        with st.container(border=True):
            panel_title("Demand split across zones")
            z = aggregate_counts("zone")
            if not z.empty:
                donut(z.index, z.values, f"{int(z.sum()):,}<br>bookings", height=465)
            else:
                show_png("bookings_by_zone.png")
    note("Map colours use completed booking coordinates. The five depot markers are provisional "
         "booking-coordinate anchors: road access, land permissions and operating costs remain unverified.",True)

# ---------------------------------------------------------------------------
# 09 — K-MEANS
# ---------------------------------------------------------------------------
elif page == PAGES[3]:
    hero("K-Means Experiment Lab",
         "Explore how changing the number of candidate depots affects average straight-line booking distance.",
         "TA3 · CLUSTERING & DISTANCE OPTIMISATION")
    if {"k", "mean_km", "p90_km"}.issubset(km.columns) and not km.empty:
        values=sorted(int(v) for v in km["k"].unique())
        selected=st.select_slider("Explore a saved value of K",options=values,
                                  value=5 if 5 in values else values[0])
        row=km.loc[km["k"]==selected].iloc[0]
        kpis([
            ("Selected depot count",str(selected),"Existing saved TA3 run"),
            ("Mean distance",f"{row['mean_km']:.3f} km","Nearest candidate centre"),
            ("P90 distance",f"{row['p90_km']:.3f} km","90% of bookings at or below"),
            ("Median distance",f"{row['median_km']:.3f} km" if "median_km" in row else "—","Middle booking"),
            ("Random seed",str(int(row['seed'])) if "seed" in row else "42","Reproducible"),
            ("Dataset size",number(clean_count),"Completed bookings"),
        ])
        with st.container(border=True):
            panel_title("📉 Average distance by candidate count",
                        "Interactive values for K=1–10 · Yellow marker is your selected scenario")
            trend_k(km["k"],km["mean_km"],highlighted=selected,height=490)
    else:
        show_png("kmeans_distance_vs_k.png")
    lcol,rcol=st.columns([1.15,1],gap="large")
    with lcol:
        with st.container(border=True):
            panel_title("Value gained by adding depots", "Percentage distance reduction per additional candidate")
            if {"k","improvement_pct"}.issubset(km.columns):
                data=km.loc[km["k"]>1].dropna(subset=["improvement_pct"])
                f=go.Figure(go.Bar(x=data["k"], y=data["improvement_pct"],
                                   marker_color=C["mint"],
                                   text=[f"{v:.1f}%" for v in data["improvement_pct"]],
                                   textposition="outside", cliponaxis=False))
                base_fig(f,height=390,l=55,r=22,b=50)
                f.update_xaxes(title="Candidate count (K)",dtick=1)
                f.update_yaxes(title="Improvement (%)")
                chart(f)
            else:show_png("kmeans_improvement_vs_k.png")
    with rcol:
        with st.container(border=True):
            panel_title("K=3 original prototype", "Early TA2 clustering evidence")
            show_png("initial_kmeans_clusters.png")
    with st.container(border=True):
        panel_title("Complete K-Means experimental table")
        display_table(km.round(4) if not km.empty else km,height=360)
    section_heading("Reliability testing")
    lcol,rcol=st.columns([1.2,1],gap="large")
    with lcol:
        with st.container(border=True):
            panel_title("Ten-seed reliability chart", "Very small variation in the tested configurations")
            show_png("kmeans_seed_reliability.png")
    with rcol:
        with st.container(border=True):
            panel_title("Reliability summary")
            display_table(reliability.round(5) if not reliability.empty else reliability,height=330)
    note("K=5 was selected for the current TA4 demonstration; it is not a proven economic optimum. "
         "The K-Means comparison uses mathematical centroids; provisional depot CSV points are "
         "snapped to observed booking coordinates and can have slightly different distances.",True)

# ---------------------------------------------------------------------------
# 10 — DBSCAN
# ---------------------------------------------------------------------------
elif page == PAGES[4]:
    hero("DBSCAN Density Analysis",
         "Find naturally dense booking regions, examine isolated points and compare clustering parameters.",
         "TA3 · DENSITY-BASED LEARNING")
    if {"eps_km", "n_clusters", "noise_pct"}.issubset(db.columns) and not db.empty:
        options=sorted(float(v) for v in db["eps_km"].dropna().unique())
        chosen=st.select_slider("Neighbourhood radius (km)",options=options,
                                value=.8 if .8 in options else options[0])
        r=db.loc[np.isclose(db["eps_km"],chosen)].iloc[0]
        kpis([
            ("Neighbourhood radius",f"{chosen:g} km","Parameter eps"),
            ("Clusters detected",str(int(r["n_clusters"])),"Density groups"),
            ("Noise points",f"{int(r['noise_points']):,}" if "noise_points" in r else "—","Isolated bookings"),
            ("Noise share",f"{r['noise_pct']:.2f}%","DBSCAN noise"),
            ("Silhouette",f"{r['silhouette']:.3f}" if pd.notna(r.get("silhouette")) else "—","Higher is generally better"),
            ("Sample size",f"{int(r['sample_size']):,}" if "sample_size" in r else "6,000","Common sampled bookings"),
        ])
    lcol,rcol=st.columns(2,gap="large")
    with lcol:
        with st.container(border=True):
            panel_title("Clusters vs neighbourhood radius", "As eps increases, nearby clusters can merge")
            if {"eps_km", "n_clusters"}.issubset(db.columns):
                f=go.Figure(go.Scatter(x=db["eps_km"],y=db["n_clusters"],mode="lines+markers",
                       line=dict(color=C["cyan"],width=3),marker=dict(size=11)))
                base_fig(f,410,l=55,r=25,b=54)
                f.update_xaxes(title="Radius (km)")
                f.update_yaxes(title="Detected clusters",dtick=1)
                chart(f)
            else:show_png("dbscan_clusters_vs_eps.png")
    with rcol:
        with st.container(border=True):
            panel_title("Noise percentage vs radius", "Fewer bookings are isolated at larger radii")
            if {"eps_km", "noise_pct"}.issubset(db.columns):
                f=go.Figure(go.Bar(x=db["eps_km"].map(lambda v:f"{v:g} km"),
                       y=db["noise_pct"],marker_color=C["violet"],
                       text=[f"{v:.1f}%" for v in db["noise_pct"]],textposition="outside"))
                base_fig(f,410,l=55,r=28,b=48)
                f.update_yaxes(title="Noise (%)")
                chart(f)
            else:show_png("dbscan_noise_vs_eps.png")
    with st.container(border=True):
        panel_title("Geographical DBSCAN groups", "Saved illustration for eps = 0.5 km")
        show_png("dbscan_cluster_map.png")
    with st.container(border=True):
        panel_title("DBSCAN parameter experiments", "Four radius configurations, min_samples=30")
        display_table(db.round(4) if not db.empty else db,height=310)
    note("Standalone DBSCAN used a reproducible 6,000-booking sample. Silhouette "
         "and Davies–Bouldin scores excluded noise points; compare carefully.",True)

# ---------------------------------------------------------------------------
# 11 — MODEL COMPARISON
# ---------------------------------------------------------------------------
elif page == PAGES[5]:
    hero("Model Comparison Studio",
         "Compare K-Means and DBSCAN on identical booking locations and explain the trade-offs honestly.",
         "TA3 · MATCHED 6,000-BOOKING EXPERIMENT")
    if not cmp.empty and {"algorithm","mean_km","p90_km"}.issubset(cmp.columns):
        lcol,rcol=st.columns(2,gap="large")
        with lcol:
            with st.container(border=True):
                panel_title("Mean nearest-candidate distance", "Lower is better · km")
                f=go.Figure(go.Bar(x=cmp["algorithm"],y=cmp["mean_km"],
                                  marker_color=[C["mint"],C["cyan"]][:len(cmp)],
                                  text=[f"{v:.3f} km" for v in cmp["mean_km"]],
                                  textposition="outside",cliponaxis=False))
                base_fig(f,425,l=55,r=34,b=43)
                f.update_yaxes(title="Mean distance (km)")
                chart(f)
        with rcol:
            with st.container(border=True):
                panel_title("90th-percentile distance", "Distance coverage of 90% of bookings")
                f=go.Figure(go.Bar(x=cmp["algorithm"],y=cmp["p90_km"],
                                  marker_color=[C["violet"],C["amber"]][:len(cmp)],
                                  text=[f"{v:.3f} km" for v in cmp["p90_km"]],
                                  textposition="outside",cliponaxis=False))
                base_fig(f,425,l=55,r=34,b=43)
                f.update_yaxes(title="P90 distance (km)")
                chart(f)
    else:
        lcol,rcol=st.columns(2,gap="large")
        with lcol:show_png("kmeans_vs_dbscan_distance.png")
        with rcol:show_png("kmeans_vs_dbscan_clusters.png")
    with st.container(border=True):
        panel_title("Full comparison results", "Same sampled bookings, four clusters in the tested settings")
        display_table(cmp.round(4) if not cmp.empty else cmp,height=245)
    micro_cards([
        ("K-Means", "Uses mathematical centroids and a chosen number of clusters."),
        ("DBSCAN", "Uses geographical density and can flag noise; represented by observed bookings."),
        ("Interpretation", "Comparison is exploratory. Both algorithms use the same 6,000 booking locations."),
    ])
    note("The two methods have different candidate-selection mechanics, even though both "
         "produced four clusters under these settings. A lower distance here does not prove "
         "that one algorithm always performs better.",True)

# ---------------------------------------------------------------------------
# 12 — FINAL RECOMMENDATIONS
# ---------------------------------------------------------------------------
elif page == PAGES[6]:
    hero("Provisional Depot Recommendations",
         "Inspect five model-generated geographical anchors, coverage and allocation demand.",
         "TA4 · CANDIDATE SITE PLANNING")
    represented=int(pd.to_numeric(depots["assigned_bookings"],errors="coerce").sum()) \
                if "assigned_bookings" in depots else None
    kpis([
        ("Candidate sites",number(len(depots)) if not depots.empty else "—","K=5 illustration"),
        ("Bookings covered",number(represented),"Assigned to closest anchor"),
        ("Mean distance",f"{avg_candidate:.3f} km" if avg_candidate is not None else "—","Straight-line estimate"),
        ("Site status","Provisional","Not road-verified"),
        ("Export","depots.csv","A1 handoff candidate"),
        ("Scenario seed","42","Reproducible model"),
    ])
    with st.container(border=True):
        panel_title("🗺️ Proposed coverage map", "Zoom into individual markers to inspect candidate-specific distances")
        render_map("recommended_depots_map.html",695)
    lcol,rcol=st.columns([1.15,1],gap="large")
    with lcol:
        with st.container(border=True):
            panel_title("Provisional candidate list", "Latitude, longitude and site-status information")
            display_table(depots,height=380)
    with rcol:
        with st.container(border=True):
            panel_title("Booking demand by candidate", "Assignments to nearest candidate coordinates")
            if {"depot_id","assigned_bookings"}.issubset(depots.columns):
                vals=depots.sort_values("assigned_bookings",ascending=False)
                horizontal_bars(vals["depot_id"],vals["assigned_bookings"],height=365)
    note("A booking coordinate does not establish a real depot location. Validate land use, "
         "road connectivity, commercial availability, refilling suitability and permissions "
         "before treating these points as operational sites.",True)

# ---------------------------------------------------------------------------
# 13 — DOWNLOADS
# ---------------------------------------------------------------------------
elif page == PAGES[7]:
    hero("Reports, Evidence & Downloads",
         "Download actual generated project outputs for your research documentation and A1 integration.",
         "TA4 · EXPORT CENTRE")
    a,b,c=st.columns(3,gap="large")
    with a:
        with st.container(border=True):
            panel_title("📍 Depot outputs")
            download_csv(depots,"depots.csv","Download depot candidates")
            download_csv(km,"kmeans_comparison.csv","Download K-Means experiments")
    with b:
        with st.container(border=True):
            panel_title("🔬 Model studies")
            download_csv(db,"dbscan_comparison.csv","Download DBSCAN experiments")
            download_csv(cmp,"model_comparison.csv","Download model comparison")
    with c:
        with st.container(border=True):
            panel_title("📊 Reliability & records")
            download_csv(reliability,"kmeans_reliability_summary.csv","Download reliability")
            download_csv(logs,"experiments.csv","Download experiment log")
    st.markdown("")
    with st.container(border=True):
        panel_title("Maps & documentation", "Interactive HTML maps and project reports")
        a,b,c=st.columns(3,gap="large")
        with a:
            download_asset(PLOTS/"recommended_depots_map.html","Download depot map (HTML)","text/html")
        with b:
            download_asset(PLOTS/"booking_demand_map.html","Download demand map (HTML)","text/html")
        with c:
            download_asset(RESULTS/"TA3_FINDINGS.md","Download TA3 findings (Markdown)","text/markdown")
    note("Depots are provisional planning candidates. No customer-level raw booking dataset "
         "is offered for download from the dashboard.")

# ---------------------------------------------------------------------------
# 14 — ABOUT PROJECT
# ---------------------------------------------------------------------------
elif page == PAGES[8]:
    hero("About DEPOTIQ & Team 6",
         "An understandable, reproducible research workflow for planning geographical micro-depots.",
         "A4 · SERVICE AS A SERVICE")
    section_heading("The Doorstep business problem")
    st.write("Doorstep is a hypothetical mobile car-washing service. Service vehicles "
             "need water and supply refills. Poorly located depots can create unnecessary travel. "
             "Our research uses booking locations to suggest provisional refilling-point locations.")
    section_heading("How the complete system works")
    micro_cards([
        ("1 · Prepare", "Load original bookings, validate coordinates and retain completed demand."),
        ("2 · Learn", "Apply K-Means and DBSCAN; inspect candidate counts, density and stability."),
        ("3 · Deliver", "Compare straight-line coverage and export candidate depots plus interactive maps."),
    ])
    with st.container(border=True):
        panel_title("Research data flow")
        st.code(
            "bookings.csv  →  cleaning  →  demand EDA  →  K-Means / DBSCAN\n"
            "      ↓                               ↓\n"
            "clean_bookings.csv       evaluation + reliability\n"
            "                                      ↓\n"
            "                       provisional depots.csv + HTML map\n"
            "                                      ↓\n"
            "                             A1 route-planner handoff",
            language="text",
        )
    section_heading("Team 6")
    lcol,rcol=st.columns(2,gap="large")
    with lcol:
        with st.container(border=True):
            st.markdown("**Parikshit Gulia**  \nProject Lead • Core ML Development, Dashboard & Deployment")
            st.markdown("**Mukul Punia**  \nData exploration and preprocessing")
    with rcol:
        with st.container(border=True):
            st.markdown("**Siddharth Sehwag**  \nClustering Research & Model Evaluation Support")
            st.markdown("**Nishant Chouhary**  \nEvaluation and documentation")
    section_heading("Methods and scientific limitations")
    st.write("K-Means groups booking coordinates into a selected number of clusters. "
             "DBSCAN detects dense regions and labels noise. Haversine distance estimates "
             "geographical, straight-line distances. Ten-seed experiments test stability under "
             "selected random initializations. Real route and site verification remains pending.")
    note("DEPOTIQ is a research prototype. Site legal suitability, real road distances, "
         "rental costs and operational feasibility have not yet been verified.",True)
    st.link_button("Open Team 6 GitHub",
                   "https://github.com/guliaparikshit/doorstep-a04-depot-placement")

st.divider()
st.caption("DEPOTIQ  ·  Team 6  ·  A4 — Micro-Depot Placement  ·  Academic research prototype")
