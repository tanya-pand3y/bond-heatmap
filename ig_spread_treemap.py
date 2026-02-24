"""
IG Credit Spread Treemap Monitor
=================================
Run with:  streamlit run ig_spread_treemap.py

Install deps:
    pip install streamlit plotly pandas numpy
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IG Credit · Spread Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Mono', monospace !important;
    background-color: #0a0c0f !important;
    color: #c8d0da !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 1.5rem !important; max-width: 100% !important; }

[data-testid="stSidebar"] {
    background-color: #111418 !important;
    border-right: 1px solid #1e2329 !important;
}
[data-testid="stSidebar"] * { color: #c8d0da !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 11px !important; }

.metric-card {
    background: #111418;
    border: 1px solid #1e2329;
    border-radius: 3px;
    padding: 12px 16px;
}
.metric-label {
    font-size: 9px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #5a6370;
    margin-bottom: 4px;
}
.metric-value {
    font-size: 22px;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    line-height: 1.2;
}
.metric-sub { font-size: 9px; color: #5a6370; margin-top: 3px; }

.section-header {
    font-size: 9px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #5a6370;
    border-bottom: 1px solid #1e2329;
    padding-bottom: 6px;
    margin-bottom: 12px;
    margin-top: 8px;
}
.top-header {
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid #1e2329;
}
.app-title { font-size: 14px; font-weight: 600; letter-spacing: 0.1em; }
.app-title span { color: #f0b429; }
.app-subtitle { font-size: 10px; color: #5a6370; letter-spacing: 0.06em; }

.badge { display:inline-block; font-size:9px; padding:2px 8px; border-radius:2px; font-weight:600; letter-spacing:.1em; text-transform:uppercase; }
.badge-Rich  { background:rgba(0,196,140,.12); color:#00c48c; border:1px solid rgba(0,196,140,.3); }
.badge-Fair  { background:rgba(61,122,181,.1);  color:#5a9fd4; border:1px solid rgba(61,122,181,.25); }
.badge-Cheap { background:rgba(224,92,92,.12);  color:#e05c5c; border:1px solid rgba(224,92,92,.3); }
.badge-Wide  { background:rgba(224,92,92,.22);  color:#ff7070; border:1px solid rgba(224,92,92,.45); }

div[data-testid="stTabs"] button {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: .08em !important;
}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    bonds = [
        # FINANCIALS
        dict(issuer="JPMorgan Chase",   ticker="JPM",  isin="US46625HJA38", rating="A+",   sector="Financials", maturity=2029, coupon=4.25, oas=82,  lo52=68,  hi52=145, chg=+3,  notional=45, sdur=5.1),
        dict(issuer="JPMorgan Chase",   ticker="JPM",  isin="US46625HKB02", rating="A+",   sector="Financials", maturity=2034, coupon=4.85, oas=91,  lo52=75,  hi52=158, chg=+2,  notional=30, sdur=8.6),
        dict(issuer="Bank of America",  ticker="BAC",  isin="US06051GHQ38", rating="A-",   sector="Financials", maturity=2028, coupon=3.95, oas=96,  lo52=80,  hi52=162, chg=-4,  notional=38, sdur=4.4),
        dict(issuer="Goldman Sachs",    ticker="GS",   isin="US38141GXZ20", rating="BBB+", sector="Financials", maturity=2032, coupon=5.10, oas=138, lo52=98,  hi52=195, chg=+8,  notional=22, sdur=7.2),
        dict(issuer="Morgan Stanley",   ticker="MS",   isin="US6174468V21", rating="A-",   sector="Financials", maturity=2030, coupon=4.30, oas=109, lo52=88,  hi52=172, chg=-2,  notional=28, sdur=5.9),
        dict(issuer="Wells Fargo",      ticker="WFC",  isin="US94974BFX24", rating="BBB+", sector="Financials", maturity=2027, coupon=3.55, oas=122, lo52=95,  hi52=178, chg=+5,  notional=18, sdur=3.8),
        dict(issuer="Citigroup",        ticker="C",    isin="US172967NE02", rating="BBB+", sector="Financials", maturity=2031, coupon=4.65, oas=131, lo52=105, hi52=188, chg=+6,  notional=20, sdur=6.8),
        dict(issuer="Barclays",         ticker="BARC", isin="US06738EBM04", rating="BBB",  sector="Financials", maturity=2029, coupon=5.20, oas=162, lo52=118, hi52=218, chg=+12, notional=15, sdur=5.3),
        dict(issuer="HSBC",             ticker="HSBC", isin="US40434LAB09", rating="A-",   sector="Financials", maturity=2033, coupon=4.75, oas=118, lo52=94,  hi52=175, chg=-1,  notional=25, sdur=8.1),
        # TECHNOLOGY
        dict(issuer="Apple",            ticker="AAPL", isin="US037833DV97", rating="AA+",  sector="Technology", maturity=2028, coupon=3.00, oas=42,  lo52=35,  hi52=88,  chg=-1,  notional=60, sdur=4.2),
        dict(issuer="Apple",            ticker="AAPL", isin="US037833DX53", rating="AA+",  sector="Technology", maturity=2033, coupon=3.85, oas=55,  lo52=44,  hi52=102, chg=+1,  notional=40, sdur=8.0),
        dict(issuer="Microsoft",        ticker="MSFT", isin="US594918BY39", rating="AAA",  sector="Technology", maturity=2030, coupon=2.92, oas=38,  lo52=30,  hi52=79,  chg=0,   notional=55, sdur=6.1),
        dict(issuer="Alphabet",         ticker="GOOGL",isin="US02079KAC87", rating="AA+",  sector="Technology", maturity=2031, coupon=3.37, oas=48,  lo52=38,  hi52=93,  chg=+2,  notional=35, sdur=7.2),
        dict(issuer="Meta Platforms",   ticker="META", isin="US30303M7072", rating="A+",   sector="Technology", maturity=2032, coupon=4.45, oas=78,  lo52=62,  hi52=138, chg=-3,  notional=22, sdur=7.8),
        dict(issuer="Salesforce",       ticker="CRM",  isin="US79466LAG09", rating="A-",   sector="Technology", maturity=2034, coupon=4.90, oas=98,  lo52=76,  hi52=152, chg=+7,  notional=15, sdur=9.1),
        # ENERGY
        dict(issuer="ExxonMobil",       ticker="XOM",  isin="US30231GAV29", rating="AA-",  sector="Energy",     maturity=2029, coupon=3.45, oas=72,  lo52=58,  hi52=128, chg=-5,  notional=30, sdur=5.0),
        dict(issuer="Chevron",          ticker="CVX",  isin="US166764BE67", rating="AA-",  sector="Energy",     maturity=2032, coupon=3.90, oas=80,  lo52=64,  hi52=135, chg=-2,  notional=25, sdur=7.5),
        dict(issuer="Shell",            ticker="SHEL", isin="US822582BL05", rating="A+",   sector="Energy",     maturity=2030, coupon=4.10, oas=88,  lo52=72,  hi52=148, chg=+3,  notional=20, sdur=6.2),
        dict(issuer="BP Capital",       ticker="BP",   isin="US055622DB36", rating="A-",   sector="Energy",     maturity=2033, coupon=4.55, oas=112, lo52=86,  hi52=168, chg=+9,  notional=18, sdur=8.4),
        dict(issuer="ConocoPhillips",   ticker="COP",  isin="US20826FAD95", rating="A-",   sector="Energy",     maturity=2028, coupon=4.15, oas=95,  lo52=74,  hi52=155, chg=+4,  notional=15, sdur=4.3),
        # CONSUMER
        dict(issuer="Amazon",           ticker="AMZN", isin="US023135BW19", rating="AA-",  sector="Consumer",   maturity=2031, coupon=3.88, oas=62,  lo52=50,  hi52=115, chg=-2,  notional=42, sdur=7.0),
        dict(issuer="Walmart",          ticker="WMT",  isin="US931142EK06", rating="AA",   sector="Consumer",   maturity=2029, coupon=3.25, oas=45,  lo52=36,  hi52=90,  chg=+1,  notional=35, sdur=5.1),
        dict(issuer="McDonald's",       ticker="MCD",  isin="US58013MFB73", rating="BBB+", sector="Consumer",   maturity=2032, coupon=4.70, oas=128, lo52=102, hi52=185, chg=+6,  notional=18, sdur=7.7),
        dict(issuer="Coca-Cola",        ticker="KO",   isin="US191216EG85", rating="A+",   sector="Consumer",   maturity=2030, coupon=3.00, oas=58,  lo52=46,  hi52=108, chg=0,   notional=28, sdur=6.4),
        dict(issuer="Nike",             ticker="NKE",  isin="US654106AG41", rating="AA-",  sector="Consumer",   maturity=2033, coupon=3.62, oas=68,  lo52=54,  hi52=122, chg=-1,  notional=20, sdur=8.3),
        # HEALTHCARE
        dict(issuer="Johnson & Johnson",ticker="JNJ",  isin="US478160CW90", rating="AAA",  sector="Healthcare", maturity=2028, coupon=2.75, oas=36,  lo52=28,  hi52=75,  chg=0,   notional=40, sdur=4.5),
        dict(issuer="AbbVie",           ticker="ABBV", isin="US00287YBN95", rating="BBB+", sector="Healthcare", maturity=2032, coupon=4.88, oas=118, lo52=92,  hi52=178, chg=+5,  notional=22, sdur=7.4),
        dict(issuer="UnitedHealth",     ticker="UNH",  isin="US91324PEH94", rating="A+",   sector="Healthcare", maturity=2030, coupon=3.70, oas=85,  lo52=68,  hi52=142, chg=+11, notional=18, sdur=6.0),
        dict(issuer="Pfizer",           ticker="PFE",  isin="US717081ED62", rating="A-",   sector="Healthcare", maturity=2033, coupon=4.42, oas=105, lo52=82,  hi52=165, chg=+3,  notional=15, sdur=8.6),
        # UTILITIES
        dict(issuer="NextEra Energy",   ticker="NEE",  isin="US65339KBM20", rating="A-",   sector="Utilities",  maturity=2030, coupon=4.50, oas=102, lo52=80,  hi52=158, chg=+4,  notional=20, sdur=6.3),
        dict(issuer="Duke Energy",      ticker="DUK",  isin="US26441CAB89", rating="BBB+", sector="Utilities",  maturity=2033, coupon=4.30, oas=125, lo52=99,  hi52=185, chg=+7,  notional=15, sdur=8.0),
        dict(issuer="Dominion Energy",  ticker="D",    isin="US25746UBK43", rating="BBB",  sector="Utilities",  maturity=2031, coupon=3.90, oas=148, lo52=112, hi52=202, chg=+14, notional=12, sdur=7.1),
    ]
    df = pd.DataFrame(bonds)
    df["pct52w"]   = ((df["oas"] - df["lo52"]) / (df["hi52"] - df["lo52"]) * 100).round(1)
    df["range52w"] = df["hi52"] - df["lo52"]
    df["signal"]   = df["pct52w"].apply(
        lambda p: "Rich" if p < 20 else "Wide" if p > 85 else "Cheap" if p > 60 else "Fair"
    )
    df["dv01"]  = (df["notional"] * 1e6 * df["sdur"] / 10000).round(0)
    df["label"] = df["ticker"] + " " + df["maturity"].astype(str)
    df["hover"] = (
        "<b>" + df["issuer"] + "</b>  " + df["rating"] + "<br>"
        + "ISIN: " + df["isin"] + "<br>"
        + "Maturity: " + df["maturity"].astype(str)
        + "  |  Coupon: " + df["coupon"].astype(str) + "%<br>"
        + "OAS: <b>" + df["oas"].astype(str) + " bps</b>"
        + "  |  Δ Today: " + df["chg"].apply(lambda x: f"+{x}" if x > 0 else str(x)) + " bps<br>"
        + "52W Range: " + df["lo52"].astype(str) + " – " + df["hi52"].astype(str) + " bps<br>"
        + "52W Percentile: <b>" + df["pct52w"].astype(str) + "%</b>"
        + "  →  <b>" + df["signal"] + "</b><br>"
        + "Notional: $" + df["notional"].astype(str) + "mm"
        + "  |  Spread Dur: " + df["sdur"].astype(str) + "y"
    )
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-header">FILTERS</div>', unsafe_allow_html=True)
    sel_sector = st.selectbox("Sector", ["All"] + sorted(df["sector"].unique()))
    sel_rating = st.selectbox("Rating", ["All", "AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB"])

    st.markdown('<div class="section-header">COLOUR MODE</div>', unsafe_allow_html=True)
    color_mode = st.radio("", ["52W Percentile (Rich/Cheap)", "Today's Spread Δ", "OAS Level"], label_visibility="collapsed")

    st.markdown('<div class="section-header">TILE SIZE</div>', unsafe_allow_html=True)
    size_mode = st.radio("", ["Notional ($mm)", "Spread Duration", "DV01 ($)"], label_visibility="collapsed")

    st.markdown('<div class="section-header">LEGEND</div>', unsafe_allow_html=True)
    if color_mode == "52W Percentile (Rich/Cheap)":
        st.markdown("""<div style='font-size:10px;line-height:2.2'>
        <span style='color:#00c48c'>■</span> Rich — tight vs 52W range<br>
        <span style='color:#4a9fd4'>■</span> Fair — middle of range<br>
        <span style='color:#e07050'>■</span> Cheap — wide vs 52W range<br>
        <span style='color:#ff4444'>■</span> Wide — extreme cheapness</div>""", unsafe_allow_html=True)
    elif color_mode == "Today's Spread Δ":
        st.markdown("""<div style='font-size:10px;line-height:2.2'>
        <span style='color:#00c48c'>■</span> Tightening (negative Δ)<br>
        <span style='color:#555'>■</span> Unchanged<br>
        <span style='color:#e05c5c'>■</span> Widening (positive Δ)</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style='font-size:10px;line-height:2.2'>
        <span style='color:#00c48c'>■</span> Tight (low OAS)<br>
        <span style='color:#e05c5c'>■</span> Wide (high OAS)</div>""", unsafe_allow_html=True)

# ── Filter ────────────────────────────────────────────────────────────────────
fdf = df.copy()
if sel_sector != "All":
    fdf = fdf[fdf["sector"] == sel_sector]
if sel_rating != "All":
    fdf = fdf[fdf["rating"] == sel_rating]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""<div class="top-header">
  <span class="app-title"><span>IG</span> CREDIT — SPREAD TREEMAP</span>
  <span class="app-subtitle">OAS vs 52-Week Range · Investment Grade Portfolio · Mock Data</span>
</div>""", unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────────────────────────────────
avg_oas = int(fdf["oas"].mean())
avg_pct = round(fdf["pct52w"].mean(), 1)
avg_chg = round(fdf["chg"].mean(), 1)
total_n = int(fdf["notional"].sum())
n_rich  = (fdf["signal"] == "Rich").sum()
n_fair  = (fdf["signal"] == "Fair").sum()
n_cheap = fdf["signal"].isin(["Cheap", "Wide"]).sum()

pct_col = "#e05c5c" if avg_pct > 60 else "#00c48c" if avg_pct < 30 else "#5a9fd4"
chg_col = "#e05c5c" if avg_chg > 0 else "#00c48c"

c1, c2, c3, c4, c5 = st.columns(5)
for col, lbl, val, sub, color in [
    (c1, "BONDS SHOWN",    str(len(fdf)),                                   f"of {len(df)} total",  "#c8d0da"),
    (c2, "AVG OAS",        f"{avg_oas} bps",                                "notional weighted",    "#c8d0da"),
    (c3, "52W PERCENTILE", f"{avg_pct}%",                                   "0% = richest ever",    pct_col),
    (c4, "AVG Δ TODAY",    f"{'+' if avg_chg>0 else ''}{avg_chg} bps",     "spread change",        chg_col),
    (c5, "PORTFOLIO SIZE", f"${total_n:,}mm",                              f"R:{n_rich} F:{n_fair} C:{n_cheap}", "#c8d0da"),
]:
    col.markdown(f"""<div class="metric-card">
      <div class="metric-label">{lbl}</div>
      <div class="metric-value" style="color:{color}">{val}</div>
      <div class="metric-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ── Colour & size config ──────────────────────────────────────────────────────
if color_mode == "52W Percentile (Rich/Cheap)":
    color_col   = "pct52w"
    color_label = "52W %ile"
    cscale = [
        (0.00, "rgb(0,180,120)"),
        (0.20, "rgb(0,120,80)"),
        (0.50, "rgb(25,45,70)"),
        (0.75, "rgb(180,65,45)"),
        (1.00, "rgb(215,40,40)"),
    ]
    range_color = [0, 100]
elif color_mode == "Today's Spread Δ":
    color_col   = "chg"
    color_label = "Δ bps"
    cscale = [
        (0.00, "rgb(0,180,120)"),
        (0.50, "rgb(30,48,72)"),
        (1.00, "rgb(215,60,60)"),
    ]
    mx = max(abs(fdf["chg"].min()), abs(fdf["chg"].max()))
    range_color = [-mx, mx]
else:
    color_col   = "oas"
    color_label = "OAS bps"
    cscale = [
        (0.00, "rgb(0,180,120)"),
        (0.50, "rgb(25,45,70)"),
        (1.00, "rgb(215,60,60)"),
    ]
    range_color = [fdf["oas"].min(), fdf["oas"].max()]

size_col = {"Notional ($mm)": "notional", "Spread Duration": "sdur", "DV01 ($)": "dv01"}[size_mode]

# ── Treemap ───────────────────────────────────────────────────────────────────
# KEY FIX: use px.treemap with path= instead of go.Treemap with manual ids/parents.
# px.treemap handles the hierarchy automatically and avoids the blank-chart bug
# caused by None color values on parent/root nodes.

plot_df = fdf.copy()
plot_df["root"] = "Portfolio"  # invisible root node

fig = px.treemap(
    plot_df,
    path=["root", "sector", "label"],  # Portfolio > Sector > Bond
    values=size_col,
    color=color_col,
    color_continuous_scale=cscale,
    range_color=range_color,
    custom_data=["hover"],
)

fig.update_traces(
    hovertemplate="%{customdata[0]}<extra></extra>",
    # Show ticker + OAS on tiles; sector tiles show sector name
    texttemplate="<b>%{label}</b>",
    textfont=dict(family="IBM Plex Mono", size=12, color="white"),
    textposition="middle center",
    marker=dict(
        line=dict(width=1.5, color="#0a0c0f"),
        pad=dict(t=22, l=4, r=4, b=4),
    ),
    root_color="#0a0c0f",
)

fig.update_layout(
    margin=dict(t=0, l=0, r=0, b=0),
    paper_bgcolor="#0a0c0f",
    plot_bgcolor="#0a0c0f",
    font=dict(family="IBM Plex Mono", color="#c8d0da", size=11),
    height=530,
    coloraxis_colorbar=dict(
        title=dict(text=color_label, font=dict(size=9, color="#5a6370", family="IBM Plex Mono")),
        tickfont=dict(size=9, color="#5a6370", family="IBM Plex Mono"),
        bgcolor="#111418",
        bordercolor="#1e2329",
        borderwidth=1,
        thickness=10,
        len=0.55,
        x=1.005,
    ),
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── Bond detail table ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">BOND DETAIL</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Cheapest First ▼", "Richest First ▲"])

def signal_badge(sig):
    return f'<span class="badge badge-{sig}">{sig}</span>'

def fmt_chg(c):
    col = "#e05c5c" if c > 0 else "#00c48c" if c < 0 else "#5a6370"
    return f'<span style="color:{col};font-weight:500">{("+" if c>0 else "")}{c} bps</span>'

def fmt_pct(p):
    col = "#e05c5c" if p > 60 else "#00c48c" if p < 25 else "#5a9fd4"
    return f'<span style="color:{col};font-weight:600">{p}%</span>'

def fmt_oas(oas, pct):
    col = "#e05c5c" if pct > 60 else "#00c48c" if pct < 25 else "#c8d0da"
    return f'<span style="color:{col};font-weight:600">{oas}</span>'

def render_table(sdf):
    rows = "".join(f"""
    <tr style="border-top:1px solid #1a1f26">
      <td style="padding:7px 10px"><b style="color:#c8d0da">{r['issuer']}</b>
        <div style="color:#5a6370;font-size:9px;margin-top:1px">{r['isin']}</div></td>
      <td style="padding:7px 10px"><span style="background:#1e2329;padding:2px 6px;border-radius:2px;font-size:10px">{r['rating']}</span></td>
      <td style="padding:7px 10px;color:#8a95a0">{r['sector']}</td>
      <td style="padding:7px 10px;color:#8a95a0">{r['maturity']}</td>
      <td style="padding:7px 10px;text-align:right">{fmt_oas(r['oas'], r['pct52w'])}</td>
      <td style="padding:7px 10px;text-align:right">{fmt_chg(r['chg'])}</td>
      <td style="padding:7px 10px;text-align:right;color:#5a6370;font-size:10px">{r['lo52']} / {r['hi52']}</td>
      <td style="padding:7px 10px;text-align:right">{fmt_pct(r['pct52w'])}</td>
      <td style="padding:7px 10px;text-align:right;color:#8a95a0">${r['notional']}mm</td>
      <td style="padding:7px 10px;text-align:center">{signal_badge(r['signal'])}</td>
    </tr>""" for _, r in sdf.iterrows())

    th = "padding:8px 10px;font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:#5a6370;font-weight:400;border-bottom:1px solid #1e2329"
    return f"""<div style="overflow-x:auto">
    <table style="width:100%;border-collapse:collapse;font-family:'IBM Plex Mono',monospace;font-size:11px;background:#111418;border:1px solid #1e2329;border-radius:3px">
      <thead><tr>
        <th style="{th};text-align:left">Issuer</th>
        <th style="{th};text-align:left">Rtg</th>
        <th style="{th};text-align:left">Sector</th>
        <th style="{th};text-align:left">Mat</th>
        <th style="{th};text-align:right">OAS</th>
        <th style="{th};text-align:right">Δ Today</th>
        <th style="{th};text-align:right">52W Lo/Hi</th>
        <th style="{th};text-align:right">%ile</th>
        <th style="{th};text-align:right">Notional</th>
        <th style="{th};text-align:center">Signal</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table></div>"""

with tab1:
    st.markdown(render_table(fdf.sort_values("pct52w", ascending=False)), unsafe_allow_html=True)
with tab2:
    st.markdown(render_table(fdf.sort_values("pct52w", ascending=True)), unsafe_allow_html=True)

# ── Sector summary ────────────────────────────────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-header">SECTOR BREAKDOWN</div>', unsafe_allow_html=True)

sec = fdf.groupby("sector").agg(
    bonds=("issuer","count"), avg_oas=("oas","mean"),
    avg_pct=("pct52w","mean"), avg_chg=("chg","mean"), notional=("notional","sum")
).round(1).reset_index().sort_values("avg_pct", ascending=False)

cols = st.columns(len(sec))
for i, (_, r) in enumerate(sec.iterrows()):
    pc = "#e05c5c" if r["avg_pct"]>60 else "#00c48c" if r["avg_pct"]<30 else "#5a9fd4"
    cc = "#e05c5c" if r["avg_chg"]>0 else "#00c48c"
    with cols[i]:
        st.markdown(f"""<div class="metric-card" style="text-align:center">
          <div class="metric-label">{r['sector'].upper()}</div>
          <div style="font-size:20px;font-weight:700;color:{pc};margin:4px 0">{r['avg_pct']}%</div>
          <div style="font-size:9px;color:#5a6370">52W pctile</div>
          <div style="font-size:10px;color:#8a95a0;margin-top:5px">{int(r['avg_oas'])} bps avg</div>
          <div style="font-size:10px;color:{cc}">{'+' if r['avg_chg']>0 else ''}{r['avg_chg']} bps today</div>
          <div style="font-size:9px;color:#5a6370;margin-top:3px">{int(r['bonds'])} bonds · ${int(r['notional'])}mm</div>
        </div>""", unsafe_allow_html=True)
        