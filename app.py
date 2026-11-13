"""BLP Digital | Business Value Studio.

A standalone, CFO-friendly Streamlit demo for a fictional German manufacturer.
No dependencies on the old value_model.py. Replace app.py in your existing
Streamlit/GitHub app and set requirements.txt from this package.

All savings and prices are illustrative assumptions, not a BLP quotation.
The core calculation matches Isarwerk's final Excel workbook.
"""

from __future__ import annotations

from html import escape
import math

import pandas as pd
import streamlit as st


# ── Transparent inputs: final Excel baseline ─────────────────────────────────
COMPANY_NAME = "Isarwerk Präzision"
ANNUAL_REVENUE_EUR = 320_000_000     # Fixed fictional company revenue
EMPLOYEES = 1_100
AP_STAFF_FTE = 7
ERP_SYSTEM = "SAP S/4HANA"
BASE_ANNUAL_DOCUMENTS = 60_600
PRODUCTIVE_HOURS_PER_FTE = 1_650

# Annual invoice split + manual minutes/invoice, from user's final Excel.
DOCUMENT_TYPES = (
    ("Direct materials / components", 24_600, 10.0),
    ("Indirect goods / services", 16_000, 11.0),
    ("Freight / logistics", 12_000, 11.0),
    ("Other / non-PO", 8_000, 15.0),
)

SCENARIOS = {
    "Conservative": (50, 40),
    "Base case": (60, 50),
    "Optimistic": (70, 60),
}

# Public references; source metrics are NOT used to "verify" scenario outcomes.
SOURCES = {
    "blp_faq": "https://blp.digital/resources/faqs",
    "evatec": "https://blp.digital/resources/our-customers/evatec",
    "migros": "https://blp.digital/resources/our-customers/migros",
    "klippa": "https://www.klippa.com/en/invoice-processing/prices/",
    "isr": "https://isr.de/en/technologies/isr/accounts-payable-flow/offer/",
    "destatis": "https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/04/PD26_148_624.html",
}


def calculate_value(
    volume: int,
    hourly_cost: float,
    effort_pct: int,
    cash_pct: int,
    monthly_platform: float,
    price_per_document: float,
    implementation: float,
    hours_per_fte: int = PRODUCTIVE_HOURS_PER_FTE,
) -> dict[str, float | None]:
    """One-year scenario. Cost savings are distinct from revenue growth.

    Simple setup payback = setup / ((gross cash savings - annual SaaS) / 12),
    and only exists if recurring net savings are positive.
    """
    if volume <= 0 or hours_per_fte <= 0:
        raise ValueError("Volume and productive hours per FTE must be positive")

    weighted_minutes = sum(n * minutes for _, n, minutes in DOCUMENT_TYPES) / BASE_ANNUAL_DOCUMENTS
    manual_before = volume * weighted_minutes / 60.0
    saved_hours = manual_before * effort_pct / 100.0
    manual_after = manual_before - saved_hours
    capacity_eur = saved_hours * hourly_cost
    cash_benefit = capacity_eur * cash_pct / 100.0

    platform_year = monthly_platform * 12
    processing_year = volume * price_per_document
    annual_software = platform_year + processing_year
    recurring_net = cash_benefit - annual_software
    first_year_cost = annual_software + implementation
    first_year_net = cash_benefit - first_year_cost
    roi = first_year_net / first_year_cost * 100 if first_year_cost > 0 else None
    payback = implementation / (recurring_net / 12) if recurring_net > 0 else None

    return {
        "manual_before": manual_before,
        "manual_after": manual_after,
        "saved_hours": saved_hours,
        "baseline_fte": manual_before / hours_per_fte,
        "remaining_fte": manual_after / hours_per_fte,
        "released_fte": saved_hours / hours_per_fte,
        "capacity_eur": capacity_eur,
        "cash_benefit": cash_benefit,
        "platform_year": platform_year,
        "processing_year": processing_year,
        "annual_software": annual_software,
        "implementation": implementation,
        "first_year_cost": first_year_cost,
        "recurring_net": recurring_net,
        "first_year_net": first_year_net,
        "roi_percent": roi,
        "payback_months": payback,
        "margin_basis_points": recurring_net / ANNUAL_REVENUE_EUR * 10_000,
        "minutes_per_document": weighted_minutes,
    }


def annual_outlook(
    *, years: int, starting_revenue: float, base_growth_pct: float,
    annual_runrate_net: float, setup_cost: float,
    sales_uplift_enabled: bool, sales_uplift_pct: float,
    contribution_margin_pct: float,
) -> list[dict]:
    """Years 1–5. Unverified sales uplift begins in Year 2, separately.

    Workflow volumes, effort, labor cost and SaaS tariffs are held constant.
    Revenue forecast does NOT feed the core annual operational ROI.
    """
    rows = []
    running_process = 0.0
    running_sales_profit = 0.0
    for year in range(1, years + 1):
        baseline = starting_revenue * (1 + base_growth_pct / 100) ** year
        incremental_sales = (baseline * sales_uplift_pct / 100
                             if sales_uplift_enabled and year >= 2 else 0.0)
        contribution = incremental_sales * contribution_margin_pct / 100
        process_net = annual_runrate_net - (setup_cost if year == 1 else 0)
        running_process += process_net
        running_sales_profit += contribution
        rows.append({
            "year": year,
            "baseline_revenue": baseline,
            "with_sales_uplift": baseline + incremental_sales,
            "incremental_sales": incremental_sales,
            "sales_contribution": contribution,
            "operational_net": process_net,
            "cumulative_operational_net": running_process,
            "cumulative_optional_sales_profit": running_sales_profit,
        })
    return rows


def euro(n: float, short: bool = True) -> str:
    sign = "−" if n < 0 else ""
    a = abs(n)
    if short and a >= 1_000_000:
        return f"{sign}€{a / 1_000_000:,.2f}m"
    if short and a >= 1_000:
        return f"{sign}€{a / 1_000:,.1f}k"
    return f"{sign}€{a:,.0f}"


def num(n: float, decimals: int = 0) -> str:
    return f"{n:,.{decimals}f}"


def apply_scenario() -> None:
    st.session_state.effort_pct, st.session_state.cash_pct = SCENARIOS[st.session_state.scenario]


def restore_case() -> None:
    st.session_state.scenario = "Base case"
    st.session_state.effort_pct = 60
    st.session_state.cash_pct = 50
    st.session_state.doc_volume = BASE_ANNUAL_DOCUMENTS
    st.session_state.hourly_cost = 45.0
    st.session_state.platform_month = 300.0
    st.session_state.usage_price = 0.32
    st.session_state.rollout_cost = 12_100.0


st.set_page_config(
    page_title="Business Value Studio | BLP Digital",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Preserve Streamlit widget state. A preset selection refreshes both sliders.
DEFAULTS = {
    "scenario": "Base case", "effort_pct": 60, "cash_pct": 50,
    "doc_volume": BASE_ANNUAL_DOCUMENTS, "hourly_cost": 45.0,
    "platform_month": 300.0, "usage_price": 0.32,
    "rollout_cost": 12_100.0,
    "forecast_years": 5, "forecast_growth": 3.0,
    "revenue_uplift": False, "uplift_pct": 0.25,
    "contribution_margin": 25.0,
}
for state_key, default_value in DEFAULTS.items():
    if state_key not in st.session_state:
        st.session_state[state_key] = default_value

# Every earlier section responds instantly, even though inputs are positioned later.
r = calculate_value(
    volume=int(st.session_state.doc_volume),
    hourly_cost=float(st.session_state.hourly_cost),
    effort_pct=int(st.session_state.effort_pct),
    cash_pct=int(st.session_state.cash_pct),
    monthly_platform=float(st.session_state.platform_month),
    price_per_document=float(st.session_state.usage_price),
    implementation=float(st.session_state.rollout_cost),
)

# ── Style: neutral consulting palette, sharp hierarchy, restrained mint accent ─
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--navy:#142d43;--ink:#1b3548;--grey:#677986;--line:#dfe8ec;--bg:#f7f9fa;--teal:#068d7a;--mint:#e8f7f1;}
html,body,[class*="css"],.stApp{font-family:'DM Sans',sans-serif;}
.stApp,[data-testid="stAppViewContainer"]{background:var(--bg);color:var(--ink);}
.block-container{max-width:1190px;padding:1.4rem 2rem 3.5rem;}
header[data-testid="stHeader"]{background:transparent;height:22px;}
#MainMenu,footer,[data-testid="stToolbar"]{visibility:hidden;}
[data-testid="stVerticalBlock"]{gap:.7rem;}
[data-testid="stExpander"]{background:white;border:1px solid var(--line);border-radius:13px;}
[data-testid="stExpander"] summary p{font-weight:700;color:#24465b;}
[data-testid="stVerticalBlockBorderWrapper"]{border:1px solid var(--line)!important;background:white;border-radius:14px!important;}
[data-testid="stSlider"] label p,[data-testid="stNumberInput"] label p{color:#385367;font-size:13px;font-weight:700;}
[data-testid="stNumberInput"] input{font-size:16px;color:#223d50;font-weight:700;}
[data-testid="stRadio"] [role="radiogroup"]{gap:.6rem;}
[data-testid="stRadio"] [role="radiogroup"] label{background:#f4f8f9;border:1px solid #dee8ec;border-radius:10px;padding:.36rem .8rem;}
[data-testid="stButton"] button{background:#e7f4ef;border:1px solid #a9d8c8;color:#0e6759;font-weight:750;border-radius:9px;min-height:41px;}
[data-testid="stButton"] button:hover{background:#c6efe2;border-color:#0d9b81;color:#0e6759;}
.stMarkdown a{color:#078674!important;}
.bar-top{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:1px 0 17px;}
.brand{font-size:11px;letter-spacing:1.7px;font-weight:850;color:#19354a;}
.brand span{display:inline-block;background:#183348;color:white;border-radius:7px;padding:5px 9px;margin-right:8px;}
.live{font-size:10px;letter-spacing:1px;background:#e6f5ef;border:1px solid #c0e5d7;color:#157563;border-radius:20px;padding:6px 11px;font-weight:850;}
.top-eyebrow{font-size:10px;letter-spacing:1.8px;font-weight:850;color:#0b8676;margin-bottom:4px;}
.main-title{font-family:Manrope,sans-serif;font-size:clamp(31px,3.4vw,44px);letter-spacing:-1.6px;line-height:1.18;font-weight:850;color:#142d43;margin:0 0 7px;}
.main-sub{color:#5b7081;font-size:14px;line-height:1.55;margin-bottom:14px;}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;}
.chips span{background:#eaf0f3;border-radius:6px;color:#536879;font-size:11px;font-weight:750;padding:6px 10px;}
.section{display:flex;align-items:center;gap:10px;margin:23px 0 10px;}
.numeral{font-size:11px;letter-spacing:.7px;background:#18374e;color:#e3f5f2;border-radius:7px;padding:6px 9px;font-weight:850;}
.section h3{font-family:Manrope,sans-serif;color:#18354a;font-weight:850;font-size:19px;line-height:1.25;letter-spacing:-.5px;margin:0;}
.section small{font-size:11px;color:#8192a0;margin-left:auto;}
.big-kpis{display:grid;grid-template-columns:1.3fr repeat(3,1fr);gap:11px;}
.primary{background:linear-gradient(112deg,#153247,#174952);border-radius:15px;padding:18px 20px;color:white;min-height:141px;}
.primary .over{font-size:10px;letter-spacing:1px;color:#a2d7cd;font-weight:850;}
.primary .value{font-family:Manrope,sans-serif;font-size:clamp(27px,2.7vw,35px);letter-spacing:-1px;line-height:1.18;font-weight:850;color:white;margin:12px 0 3px;}
.primary .under{font-size:11px;color:#c4d8d9;line-height:1.35;}
.mini{background:white;border:1px solid var(--line);border-radius:14px;padding:17px 16px;min-height:141px;}
.mini .over{font-size:11px;line-height:1.45;color:#657b89;font-weight:750;}
.mini .value{font-family:Manrope,sans-serif;font-size:clamp(23px,2.2vw,31px);font-weight:850;letter-spacing:-.9px;color:#1b3b4d;margin:10px 0 3px;}
.mini .under{font-size:10px;color:#96a4ac;line-height:1.4;}
.fins{display:grid;grid-template-columns:1fr 1fr;gap:11px;margin-top:11px;}
.fin-panel{background:white;border:1px solid var(--line);border-radius:14px;padding:14px 19px;}
.fin-panel .cap{font-size:10px;letter-spacing:.7px;font-weight:850;color:#6a8090;}
.fin-panel .fig{font-family:Manrope,sans-serif;font-size:26px;letter-spacing:-.7px;font-weight:850;color:#19384b;margin:4px 0;}
.fin-panel .detail{font-size:11px;line-height:1.55;color:#778b98;}
.fin-panel.emphasis{background:#ebf7f3;border-color:#cae9df;}
.fin-panel.emphasis .fig{color:#077b69;}
.note{background:#f0f4f6;border-radius:10px;border:1px solid #e0e8ec;color:#526a7b;font-size:11px;line-height:1.6;padding:10px 13px;margin-top:10px;}
.compare{display:grid;grid-template-columns:1fr 66px 1fr;align-items:stretch;gap:8px;}
.side{background:white;border-radius:14px;border:1px solid var(--line);padding:18px 20px;}
.side.after{background:#edf9f4;border-color:#bbe5d4;}
.side .top{font-size:10px;letter-spacing:1px;font-weight:850;color:#718694;}
.side.after .top{color:#128473;}
.side .hours{font-family:Manrope,sans-serif;font-size:clamp(28px,3.2vw,39px);font-weight:850;letter-spacing:-1.1px;color:#214255;margin:8px 0 3px;}
.side.after .hours{color:#087d6a;}
.side .minor{font-size:11px;color:#8799a4;margin-bottom:12px;}
.side .line{display:flex;justify-content:space-between;gap:8px;padding-top:9px;margin-top:9px;border-top:1px solid #e2eaeb;font-size:11px;color:#627787;}
.side .line b{color:#294b5e;font-size:13px;}
.center-arrow{display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;gap:8px;}
.center-arrow .arrow{background:#ddefe8;color:#068d7a;width:43px;height:43px;border-radius:50%;font-size:27px;display:flex;align-items:center;justify-content:center;}
.center-arrow .percent{font-size:14px;font-weight:850;color:#0e836f;}
.capacity{background:#e9f5f1;border:1px solid #d1e6df;color:#236255;font-size:12px;padding:12px 15px;border-radius:11px;margin-top:10px;line-height:1.6;}
.casegrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;}
.case{background:white;border:1px solid var(--line);border-radius:13px;padding:15px 15px 13px;min-height:148px;}
.case .tag{font-size:10px;font-weight:850;letter-spacing:.7px;color:#128473;}
.case .tag.optional{color:#8797a2;}
.case .name{font-size:15px;color:#244457;font-weight:850;margin:8px 0 5px;}
.case .desc{font-size:11px;line-height:1.58;color:#718594;}
.proof{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;}
.proof .item{padding:12px 16px;border-radius:12px;background:#edf2f4;color:#526c7d;font-size:11px;line-height:1.7;}
.proof b{color:#1a4d4f;}
.subhead{font-size:12px;color:#4d6778;font-weight:800;margin:9px 0 3px;}
.costgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;}
.cost{background:#f3f7f8;border:1px solid #e3ebee;border-radius:11px;padding:13px;}
.cost .small{font-size:11px;color:#697e8b;}.cost strong{font-family:Manrope,sans-serif;font-size:21px;color:#1e4051;}
.helptext{font-size:11px;color:#7b8d9a;line-height:1.65;}
.summaryline{font-size:12px;background:#eaf7f2;color:#265b51;border:1px solid #cce8de;padding:12px 15px;border-radius:11px;line-height:1.6;margin-top:11px;}
.explain-card{background:#f2f6f7;border:1px solid #dbe7e9;border-radius:10px;padding:10px 13px;font-size:11px;line-height:1.65;color:#5e7785;}
@media(max-width:1050px){.big-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.casegrid{grid-template-columns:repeat(2,minmax(0,1fr))}.section small{display:none}}
@media(max-width:680px){.block-container{padding:1rem .9rem 2rem}.main-title{font-size:29px}.big-kpis{grid-template-columns:1fr 1fr}.fins{grid-template-columns:1fr}.compare{grid-template-columns:1fr}.center-arrow{flex-direction:row;padding:3px}.casegrid{grid-template-columns:1fr 1fr}.proof{grid-template-columns:1fr}.costgrid{grid-template-columns:1fr}.mini,.primary{padding:12px}.mini .value{font-size:22px}}
</style>
""", unsafe_allow_html=True)


# ── 00 / Opening ───────────────────────────────────────────────────────────────
st.markdown(
    '<div class="bar-top"><div class="brand"><span>◈</span> BLP DIGITAL / VALUE STUDIO</div>'
    '<div class="live">● INTERACTIVE CFO DEMO</div></div>'
    '<div class="top-eyebrow">FROM OPERATIONAL EFFICIENCY TO MEASURABLE IMPACT</div>'
    '<div class="main-title">What could smarter ERP workflows be worth?</div>'
    '<div class="main-sub">A practical, live business case. Explore profitability, capacity, and the next five years—without assuming new revenue.</div>'
    f'<div class="chips"><span>{escape(COMPANY_NAME)} · fictional</span>'
    f'<span>{euro(ANNUAL_REVENUE_EUR)} annual revenue</span>'
    f'<span>{EMPLOYEES:,} employees</span>'
    f'<span>{int(st.session_state.doc_volume):,} supplier documents/year</span>'
    f'<span>{escape(ERP_SYSTEM)}</span></div>',
    unsafe_allow_html=True,
)


# ── 01 / Finance & revenue: cost efficiency ≠ new revenue ──────────────────────
st.markdown('<div class="section"><span class="numeral">01</span><h3>Financial impact — what changes for the CFO?</h3><small>Year 1 · live inputs</small></div>', unsafe_allow_html=True)
roi_caption = f"{r['roi_percent']:,.0f}%" if r["roi_percent"] is not None else "n/a"
payback_caption = f"{r['payback_months']:.1f} months" if r["payback_months"] is not None else "No payback"
st.markdown(f"""
<div class="big-kpis">
  <div class="primary"><div class="over">YEAR 1 · NET FINANCIAL VALUE</div><div class="value">{euro(r['first_year_net'])}</div><div class="under">Cashable savings after annual software and one-time rollout</div></div>
  <div class="mini"><div class="over">Year-one return on investment</div><div class="value">{escape(roi_caption)}</div><div class="under">Net benefit ÷ first-year vendor costs</div></div>
  <div class="mini"><div class="over">Simple implementation payback</div><div class="value">{escape(payback_caption)}</div><div class="under">Assumes full run rate immediately</div></div>
  <div class="mini"><div class="over">Recurring annual net value</div><div class="value">{euro(r['recurring_net'])}</div><div class="under">From Year 2 onward, at constant volume</div></div>
</div>
<div class="fins">
  <div class="fin-panel"><div class="cap">REVENUE PERSPECTIVE</div><div class="fig">{euro(ANNUAL_REVENUE_EUR)} → {euro(ANNUAL_REVENUE_EUR)}</div><div class="detail">Revenue stays unchanged in the core business case. Efficiency does not create sales by itself.</div></div>
  <div class="fin-panel emphasis"><div class="cap">PROFITABILITY PERSPECTIVE · YEAR 2+</div><div class="fig">+{r['margin_basis_points']:.2f} basis points</div><div class="detail">Potential operating-margin improvement from {euro(r['recurring_net'])} annual net cost savings, if Finance confirms they are cashable.</div></div>
</div>
<div class="note"><strong>Important distinction:</strong> a business may gain employee capacity without reducing cash expenditure. Only the cash-conversion share enters this financial result. Revenue opportunities can be explored separately in the optional five-year model.</div>
""", unsafe_allow_html=True)


# ── 02 / Operations ────────────────────────────────────────────────────────────
st.markdown('<div class="section"><span class="numeral">02</span><h3>Operational impact — before vs. after</h3><small>Modeled document-processing workload</small></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="compare">
  <div class="side">
    <div class="top">BEFORE · MANUAL WORKLOAD</div>
    <div class="hours">{num(r['manual_before'])} <span style="font-size:14px;font-weight:650;color:#879aa3">hrs / year</span></div>
    <div class="minor">Handling, matching, approvals and exceptions</div>
    <div class="line"><span>Workload equivalent</span><b>{r['baseline_fte']:.2f} FTE</b></div>
    <div class="line"><span>Time per document</span><b>{r['minutes_per_document']:.1f} min</b></div>
  </div>
  <div class="center-arrow"><div class="arrow">→</div><div class="percent">−{int(st.session_state.effort_pct)}% effort</div></div>
  <div class="side after">
    <div class="top">AFTER · MODELED WORKLOAD</div>
    <div class="hours">{num(r['manual_after'])} <span style="font-size:14px;font-weight:650;color:#7ba99b">hrs / year</span></div>
    <div class="minor">People focus on exceptions and higher-value work</div>
    <div class="line"><span>Remaining workload equivalent</span><b>{r['remaining_fte']:.2f} FTE</b></div>
    <div class="line"><span>Time per document</span><b>{r['minutes_per_document']*(1-st.session_state.effort_pct/100):.1f} min</b></div>
  </div>
</div>
<div class="capacity"><strong>{num(r['saved_hours'])} hours · {r['released_fte']:.2f} FTE capacity released per year.</strong> This is additional operational capacity, <strong>not</strong> a prediction of job cuts. The model converts only {int(st.session_state.cash_pct)}% of released hours into cash savings.</div>
""", unsafe_allow_html=True)


# ── 03 / Use cases & actual customer proof ────────────────────────────────────
st.markdown('<div class="section"><span class="numeral">03</span><h3>Use cases — where automation can help</h3><small>Only supplier-invoice workflow is quantified in this model</small></div>', unsafe_allow_html=True)
st.markdown("""
<div class="casegrid">
  <div class="case"><div class="tag">● INCLUDED IN THIS ROI</div><div class="name">Finance workflows</div><div class="desc">Capture supplier documents, match purchase orders, route approvals and review discrepancies.</div></div>
  <div class="case"><div class="tag optional">○ EXPANSION OPPORTUNITY</div><div class="name">Procurement</div><div class="desc">Read supplier order confirmations and compare price, quantities and dates to orders.</div></div>
  <div class="case"><div class="tag optional">○ EXPANSION OPPORTUNITY</div><div class="name">Logistics</div><div class="desc">Process delivery notes and align incoming-goods records with ERP transactions.</div></div>
  <div class="case"><div class="tag optional">○ EXPANSION OPPORTUNITY</div><div class="name">Sales operations</div><div class="desc">Translate incoming customer orders into structured ERP transactions with exception checks.</div></div>
</div>
<div class="proof">
  <div class="item"><b>Evatec · 1.5 FTE</b> now run its AP operation; BLP reports around 57,000 annual automated documents across multiple document types. <a href="https://blp.digital/resources/our-customers/evatec" target="_blank">Customer case ↗</a></div>
  <div class="item"><b>Migros · 30–40%</b> lower resource requirements in its documented rollout. This is different from the manual touch-time reduction tested here. <a href="https://blp.digital/resources/our-customers/migros" target="_blank">Customer case ↗</a></div>
</div>
""", unsafe_allow_html=True)


# ── 04 / Interactive parameters (after the presentation narrative) ───────────
st.markdown('<div class="section"><span class="numeral">04</span><h3>Your assumptions — challenge the business case</h3><small>Everything above recalculates instantly</small></div>', unsafe_allow_html=True)
with st.container(border=True):
    st.radio("Choose a scenario", list(SCENARIOS), horizontal=True,
             on_change=apply_scenario, key="scenario")
    slider_a, slider_b = st.columns(2, gap="large")
    with slider_a:
        st.slider("Reduction in manual processing effort", 0, 90, step=5,
                  key="effort_pct", format="%d%%",
                  help="50% / 60% / 70% are scenario assumptions; not verified BLP outcomes.")
    with slider_b:
        st.slider("Freed hours converted to actual cash savings", 0, 100, step=5,
                  key="cash_pct", format="%d%%",
                  help="Model cashable avoided hiring, overtime or services—not the whole capacity value.")

    inputs_a, inputs_b, inputs_c = st.columns([1, 1, 1], gap="medium")
    with inputs_a:
        st.number_input("Documents processed per year", min_value=1_000, max_value=2_000_000,
                        step=1_000, key="doc_volume")
    with inputs_b:
        st.number_input("Employer cost (€ / hour)", min_value=5.0, max_value=250.0,
                        step=1.0, format="%.2f", key="hourly_cost")
    with inputs_c:
        st.markdown('<div style="padding-top:26px"></div>', unsafe_allow_html=True)
        st.button("↺ Restore Excel base case", on_click=restore_case,
                  use_container_width=True)

    st.markdown(f'<div class="summaryline"><b>In this scenario:</b> {euro(r["cash_benefit"])} potential annual cash savings − {euro(r["annual_software"])} recurring platform + usage − {euro(r["implementation"])} one-time implementation = <b>{euro(r["first_year_net"])} Year-1 net value</b>.</div>', unsafe_allow_html=True)

with st.expander("More assumptions · platform pricing, implementation and invoice mix", expanded=False):
    st.markdown('#### Simple BLP pricing model (illustrative, not quoted)')
    aa, bb, cc = st.columns(3)
    with aa:
        st.number_input("All-inclusive platform (€ / month)",
                        min_value=0.0, max_value=50_000.0, step=50.0,
                        key="platform_month", format="%.2f")
    with bb:
        st.number_input("Pay as you go (€ / document)", min_value=0.0,
                        max_value=10.0, step=0.01, format="%.2f", key="usage_price")
    with cc:
        st.number_input("One-time rollout + consulting (€)", min_value=0.0,
                        max_value=500_000.0, step=500.0, key="rollout_cost", format="%.2f")

    st.markdown(f"""
    <div class="costgrid">
       <div class="cost"><div class="small">Annual platform subscription</div><strong>{euro(r['platform_year'])}</strong></div>
       <div class="cost"><div class="small">Annual usage-based processing</div><strong>{euro(r['processing_year'])}</strong></div>
       <div class="cost"><div class="small">Year-1 total vendor cost</div><strong>{euro(r['first_year_cost'])}</strong></div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Reference: Doxis/Klippa publicly offers Premium at €275/month, with additional invoices from €0.28. The BLP €300 + €0.32 model and €12,100 one-time estimate are fictional scenario inputs, not BLP list prices.")
    st.markdown(f"[Doxis/Klippa published pricing]({SOURCES['klippa']})  ·  [ISR implementation reference]({SOURCES['isr']})")
    st.markdown("**Estimated workload mix · quantities scale with the documents/year input**")
    mix = []
    for name, count, minutes in DOCUMENT_TYPES:
        scaled = round(count * st.session_state.doc_volume / BASE_ANNUAL_DOCUMENTS)
        mix.append({"Workflow": name, "Documents / year (approx.)": scaled,
                    "Minutes / document": int(minutes), "Confidence": "Low · assumed"})
    st.dataframe(pd.DataFrame(mix), use_container_width=True, hide_index=True)


# ── 05 / Optional five-year view. Revenue not smuggled into cash ROI. ─────────
st.markdown('<div class="section"><span class="numeral">05</span><h3>Five-year revenue & value outlook</h3><small>Optional CFO exploration</small></div>', unsafe_allow_html=True)
with st.expander("Open interactive 1–5 year forecast · revenue, savings & optional upside", expanded=False):
    st.markdown('''<div class="explain-card">Base revenue growth and operating savings are modeled separately. A sales uplift is <strong>off by default</strong>; if enabled, it is an unverified sensitivity and <strong>never changes the core ROI above</strong>.</div>''', unsafe_allow_html=True)
    ya, yb = st.columns(2)
    with ya:
        st.slider("Forecast horizon", 1, 5, step=1, key="forecast_years", format="%d years")
    with yb:
        st.slider("Assumed annual company revenue growth", -5.0, 15.0, step=0.5,
                  key="forecast_growth", format="%.1f%%")

    st.checkbox("Explore additional sales enabled by faster business workflows (hypothetical)",
                key="revenue_uplift")
    if st.session_state.revenue_uplift:
        ua, ub = st.columns(2)
        with ua:
            st.slider("Incremental revenue uplift from Year 2 onward", 0.0, 3.0,
                      step=0.05, key="uplift_pct", format="%.2f%%")
        with ub:
            st.slider("Contribution margin on those extra sales", 0.0, 60.0,
                      step=5.0, key="contribution_margin", format="%.0f%%")

    projection = annual_outlook(
        years=int(st.session_state.forecast_years),
        starting_revenue=ANNUAL_REVENUE_EUR,
        base_growth_pct=float(st.session_state.forecast_growth),
        annual_runrate_net=float(r["recurring_net"]),
        setup_cost=float(r["implementation"]),
        sales_uplift_enabled=bool(st.session_state.revenue_uplift),
        sales_uplift_pct=float(st.session_state.uplift_pct),
        contribution_margin_pct=float(st.session_state.contribution_margin),
    )

    final = projection[-1]
    series = pd.DataFrame({
        "Year": [f"Year {x['year']}" for x in projection],
        "Baseline revenue (€m)": [round(x["baseline_revenue"] / 1e6, 2) for x in projection],
        **({"With optional sales uplift (€m)": [round(x["with_sales_uplift"] / 1e6, 2)
            for x in projection]} if st.session_state.revenue_uplift else {}),
    }).set_index("Year")

    fa, fb, fc = st.columns(3)
    with fa:
        st.metric(f"Revenue · Year {st.session_state.forecast_years}",
                  euro(final["with_sales_uplift"]),
                  help="Base forecast plus optional unvalidated sales uplift (if enabled).")
    with fb:
        st.metric("Cumulative operational net value", euro(final["cumulative_operational_net"]),
                  help="Recurring cashable savings minus SaaS each year, less setup only in Year 1.")
    with fc:
        st.metric("Optional extra sales profit", euro(final["cumulative_optional_sales_profit"]),
                  help="Hypothetical incremental sales × contribution margin, never included in core ROI.")

    st.line_chart(series, height=290, color=["#9BAEB9", "#068D7A"] if st.session_state.revenue_uplift else ["#068D7A"])
    st.caption("Annual revenue projection (€m). The first projected year applies the chosen YoY growth to the fictional current €320m turnover.")
    display_rows = []
    for item in projection:
        display_rows.append({
            "Year": f"Y{item['year']}",
            "Revenue forecast": euro(item["baseline_revenue"]),
            "Optional extra sales": euro(item["incremental_sales"]),
            "Operational net value": euro(item["operational_net"]),
            "Optional extra sales profit": euro(item["sales_contribution"]),
        })
    st.dataframe(pd.DataFrame(display_rows), use_container_width=True, hide_index=True)
    st.caption("Assumptions: fixed workflow volume, unit pricing, employer cost and effort reduction for all projected years; setup charged only in Y1; no inflation, discounting, tax or rollout ramp. Optional sales uplift starts in Y2 and is not an evidence-based BLP outcome.")


# ── Source appendix, intentionally collapsed to fit a four-minute demo ─────────
with st.expander("Evidence, confidence & how the ROI works", expanded=False):
    st.markdown("""
    | Input / claim | Confidence | Interpretation |
    |:--|:--|:--|
    | BLP Evatec and Migros published outcomes | **High** | Real customer cases; different organizations and measures |
    | Klippa €275/month & extra invoices from €0.28 | **High** | Competitor tariff, not BLP's price |
    | Fictional Isarwerk revenue, team and invoice mix | **Low** | Planning baseline, not actual company data |
    | €45 employer cost / hour | **Medium** | German broad labor-cost proxy, not actual AP payroll |
    | 50–70% manual effort reduction | **Low** | Scenario; validate through pilot before forecasting |
    | 40–60% cash conversion | **Low** | Requires an avoidable-cost plan approved by Finance |
    | €300 + €0.32 usage + €12,100 rollout | **Low** | Proposed fee structure, not a BLP quotation |

    **Core math**: annual manual hours = volume × weighted manual minutes ÷ 60. Saved hours = manual hours × effort reduction. Annual cash savings = saved hours × € / hour × cash conversion. Recurring cost = 12 × monthly platform + volume × fee/document. Year-one net = annual cash savings − recurring cost − one-time rollout. ROI = year-one net ÷ total year-one cost. Simple payback = rollout ÷ monthly recurring net savings, only if recurring net savings are positive.
    """)
    st.markdown(f"[BLP customer FAQ]({SOURCES['blp_faq']}) · [Evatec]({SOURCES['evatec']}) · [Migros]({SOURCES['migros']}) · [Doxis/Klippa prices]({SOURCES['klippa']}) · [ISR rollout reference]({SOURCES['isr']}) · [Destatis labor cost]({SOURCES['destatis']})")

st.markdown('''<div class="note"><strong>Next CFO decision:</strong> validate workflow volumes and handling time with Operations, realizable cash savings with Finance, and scope/pricing in a vendor-led pilot. <em>This demo is illustrative and is neither a BLP Digital quotation nor a measured Isarwerk forecast.</em></div>''', unsafe_allow_html=True)
