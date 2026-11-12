"""Isarwerk | CFO-facing BLP AP value demo.

Deploy with Streamlit Community Cloud. Uses value_model.py unchanged.
All figures are illustrative, not a BLP quote or a customer-specific forecast.
"""
from html import escape

import streamlit as st

from value_model import COMPANY, SCENARIOS, ValueInputs, calculate

st.set_page_config(
    page_title="Isarwerk | AP business case",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# STYLE | premium, compact, and designed for a four-minute live demo
# ------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --ink:#182239; --muted:#6f7890; --line:#e8eaf2; --accent:#5b57d6; --green:#0e987b; }
.stApp { background:#f6f7fb; color:var(--ink); font-family:'DM Sans',sans-serif; }
[data-testid="stAppViewContainer"] { background:#f6f7fb; }
.block-container { max-width:1220px; padding:1.45rem 1.9rem 2.5rem; }
#MainMenu, footer { visibility:hidden; }
header[data-testid="stHeader"] { background:transparent; }
[data-testid="stVerticalBlockBorderWrapper"] {
 background:#fff; border:1px solid #e6e8f0 !important;
 border-radius:19px !important; box-shadow:0 6px 28px rgba(29,37,75,.035);
}
[data-testid="stNumberInput"] label p,
[data-testid="stRadio"] label p { color:#68748b !important; font-size:12px !important; font-weight:650 !important; }
[data-testid="stNumberInput"] input { font-family:Manrope,sans-serif; font-size:19px; font-weight:750; }
[data-testid="stRadio"] [role="radiogroup"] { gap:.5rem; }
[data-testid="stRadio"] [role="radiogroup"] label {
 border:1px solid #e6e9f1; background:#f7f8fc; border-radius:11px;
 padding:.4rem .66rem; font-weight:700; flex:1; justify-content:center;
}
[data-testid="stRadio"] [role="radiogroup"] label p { font-size:12px !important; }
[data-testid="stExpander"] { border:0 !important; background:#f8f9fc !important; border-radius:10px !important; }
[data-testid="stExpander"] summary { font-size:12px; }
.hero-top { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; margin:0 0 22px; }
.brand {display:flex;align-items:center;gap:10px;font-family:Manrope,sans-serif;font-size:14px;font-weight:850;letter-spacing:.7px;color:#222c45;}
.brand-badge {width:29px;height:29px;border-radius:10px;display:inline-flex;align-items:center;justify-content:center;background:#5b57d6;color:white;font-size:20px;font-weight:500;}
.top-right { font-size:10px;letter-spacing:1.6px;font-weight:800;color:#727f97;text-transform:uppercase; }
.eyebrow {font-size:10px;line-height:1.4;letter-spacing:1.7px;font-weight:900;text-transform:uppercase;color:#5b57d6;margin-bottom:6px;}
.page-title { font-family:Manrope,sans-serif;font-weight:850;font-size:clamp(25px,2.9vw,35px);letter-spacing:-1.45px;line-height:1.16;margin:0 0 9px;color:#15243d; }
.subtitle {color:#68758b;font-size:13px;line-height:1.6;margin:0 0 17px;}
.crumbs {display:flex;gap:7px;flex-wrap:wrap;margin:0 0 19px;}
.crumbs span {font-size:11px;font-weight:600;color:#627089;background:#edf0f7;border-radius:6px;padding:5px 9px;}
.card-kicker {color:#777fa0;font-size:10px;letter-spacing:1.5px;font-weight:900;text-transform:uppercase;margin:1px 0 6px;}
.card-title {font-family:Manrope,sans-serif;color:#1a2540;font-size:19px;font-weight:850;letter-spacing:-.5px;margin-bottom:4px;}
.card-desc {font-size:12px;color:#7d879b;line-height:1.6;margin-bottom:16px;}
.note {font-size:11px;color:#79849a;line-height:1.5;}
.value-card {background:linear-gradient(124deg,#1b2540 0%,#222c51 67%,#343a79 100%);color:white;border-radius:20px;padding:25px 27px 23px;min-height:325px;box-shadow:0 13px 28px rgba(24,35,71,.11);position:relative;overflow:hidden;}
.value-card:after {position:absolute;content:'';width:245px;height:245px;border-radius:100%;border:1px solid #ffffff1b;right:-115px;top:-145px;box-shadow:0 0 0 40px #ffffff08,0 0 0 80px #ffffff04;pointer-events:none;}
.value-tag {font-weight:800;font-size:11px;letter-spacing:1.5px;color:#a9b7f1;text-transform:uppercase;}
.value-number {font-family:Manrope,sans-serif;font-size:clamp(43px,4.5vw,65px);font-weight:850;line-height:1.22;letter-spacing:-3px;margin:10px 0 4px;color:#fff;}
.value-explain {font-size:12px;line-height:1.6;color:#bfc9de;}
.value-mini-wrap {display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:22px;}
.value-mini {background:#ffffff13;border:1px solid #ffffff16;border-radius:13px;padding:11px 13px;}
.value-mini span {font-size:11px;color:#c6cde1;display:block;margin-bottom:4px;}
.value-mini strong {font-family:Manrope,sans-serif;color:white;font-size:21px;letter-spacing:-.4px;}
.value-mini small {font-size:10px;color:#acbbd1;display:block;margin-top:2px;}
.bridge {background:#eef2fa;border:1px solid #e4e8f3;border-radius:12px;margin-top:12px;padding:13px 17px;}
.bridge-title {font-size:10px;letter-spacing:1.2px;font-weight:850;color:#71819c;text-transform:uppercase;margin-bottom:8px;}
.bridge-line {font-family:Manrope,sans-serif;color:#34425a;font-size:15px;font-weight:800;line-height:1.65;letter-spacing:-.3px;}
.bridge-line .minus {color:#b35b5b;}
.bridge-line .equals {color:#15977e;}
.section-row {display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin:22px 0 12px;flex-wrap:wrap;}
.section-title {font-family:Manrope,sans-serif;font-size:20px;font-weight:850;letter-spacing:-.6px;color:#1b2940;}
.section-note {font-size:11px;color:#8590a0;}
.proof-card {background:#fff;border:1px solid #e5e9f3;border-radius:17px;padding:16px 19px;min-height:163px;display:grid;grid-template-columns:132px 1fr;gap:17px;align-items:center;box-shadow:0 4px 15px rgba(25,44,81,.025);}
.proof-number {font-family:Manrope,sans-serif;font-size:32px;font-weight:850;line-height:1.12;letter-spacing:-1.4px;color:#574fca;}
.proof-unit {font-size:10px;color:#6d7891;line-height:1.55;margin-top:5px;}
.proof-kicker {font-size:10px;letter-spacing:1px;font-weight:850;color:#178e79;text-transform:uppercase;}
.proof-title {font-family:Manrope,sans-serif;font-size:14px;line-height:1.45;color:#25314d;font-weight:850;margin:6px 0;}
.proof-desc {font-size:11px;line-height:1.55;color:#6d7890;margin-bottom:4px;}
.proof-source {font-size:10px;color:#5b57d6;text-decoration:none;font-weight:750;}
.bottom-strip {margin-top:18px;padding:13px 16px;border:1px solid #e2e7ee;background:white;border-radius:13px;display:flex;align-items:center;justify-content:space-between;gap:15px;flex-wrap:wrap;}
.bottom-strip strong {font-size:12px;color:#283754;}
.bottom-strip span {font-size:11px;line-height:1.7;color:#69778c;}
.footer-note {font-size:10px;line-height:1.65;color:#909aab;margin-top:12px;}
a {color:#5b57d6;}
@media(max-width:700px){.block-container{padding:.9rem .8rem 2rem}.value-card{padding:22px}.value-number{font-size:47px}.proof-card{grid-template-columns:105px 1fr;padding:13px;gap:10px}.proof-number{font-size:27px}.bottom-strip{display:block}.page-title{font-size:27px}}
</style>
""", unsafe_allow_html=True)


def money(value: float, compact: bool = False) -> str:
    """EUR with a consistent minus sign; suppress false precision on big KPIs."""
    sign = "−" if value < 0 else ""
    magnitude = abs(value)
    if compact and magnitude >= 1000:
        return f"{sign}€{magnitude / 1000:,.1f}k"
    return f"{sign}€{magnitude:,.0f}"


# ------------------------------------------------------------------
# HEADER | one sentence + one compact company snapshot
# ------------------------------------------------------------------
st.markdown("""
<div class="hero-top">
  <div class="brand"><span class="brand-badge">◈</span> BLP <span style="font-weight:500;color:#a8afbe">/</span> VALUE ENGINEERING</div>
  <div class="top-right">CFO DECISION TOOL &nbsp; · &nbsp; LIVE DEMO</div>
</div>
<div class="eyebrow">THE BUSINESS QUESTION</div>
<div class="page-title">What is AP automation worth to Isarwerk?</div>
<div class="subtitle">A first-pass business case, built to answer the CFO in four minutes.</div>
<div class="crumbs">
  <span>Isarwerk Präzision GmbH · fictional</span>
  <span>€320m revenue</span>
  <span>60,600 estimated invoices / year</span>
  <span>Manufacturing · SAP S/4HANA</span>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# THE DEMO | three interactions and one CFO-ready answer
# ------------------------------------------------------------------
left, right = st.columns([0.86, 1.14], gap="medium", vertical_alignment="top")
with left:
    with st.container(border=True):
        st.markdown('<div class="card-kicker">01 / Your inputs</div><div class="card-title">Shape the opportunity</div><div class="card-desc">Change the workload or risk outlook. Results update instantly.</div>', unsafe_allow_html=True)
        invoices = st.number_input(
            "Supplier invoices / year", min_value=1_000, max_value=1_500_000,
            value=60_600, step=1_000,
            help="Estimated from the Isarwerk Excel case, not observed transactions.",
        )
        hourly_cost = st.number_input(
            "Fully loaded employer cost / hour (€)", min_value=5.0,
            max_value=250.0, value=45.0, step=1.0,
            help="Public Germany-wide labour-cost anchor, not an Isarwerk payroll extract.",
        )
        scenario = st.radio(
            "Value scenario", options=list(SCENARIOS), index=1, horizontal=True,
            help="Conservative / Base / Optimistic combine different manual-time reduction and cash realization assumptions.",
        )
        st.markdown('<div class="note">Scenarios are illustrative, not measured BLP performance.</div>', unsafe_allow_html=True)
        with st.expander("Adjust costs & model assumptions"):
            unit_price = st.number_input(
                "Assumed software fee (€ / invoice)", min_value=0.0,
                max_value=20.0, value=0.38, step=0.01, format="%.2f",
                help="Competitor-informed placeholder; BLP has not quoted this price.",
            )
            implementation = st.number_input(
                "One-off implementation (€)", min_value=0, max_value=1_000_000,
                value=50_000, step=5_000,
                help="Estimated project budget; obtain a BLP-specific proposal.",
            )
            st.caption(
                "Fixed invoice mix & manual handling minutes come from the supplied "
                "Excel model. Volume is scaled proportionally. Scenario presets: "
                "50%/40%, 65%/60%, 75%/80% (touch-time reduction / cash realization)."
            )

reduction, cash_realization = SCENARIOS[scenario]
model_inputs = ValueInputs(
    invoices_per_year=int(invoices),
    employer_hourly_cost_eur=hourly_cost,
    software_fee_per_invoice_eur=unit_price,
    implementation_cost_eur=implementation,
)
r = calculate(model_inputs, reduction, cash_realization)

value = r["year_one_net_eur"]
headline = "POTENTIAL YEAR-ONE NET BENEFIT" if value >= 0 else "ESTIMATED YEAR-ONE NET COST"
payback = f'{r["payback_months"]:.1f} months' if r["payback_months"] is not None else "No payback"

with right:
    st.markdown(f"""
    <div class="value-card">
      <div class="value-tag">02 / THE CFO ANSWER</div>
      <div class="value-number">{escape(money(value, compact=True))}</div>
      <div style="font-size:12px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:#dce2f8">{headline}</div>
      <div class="value-explain" style="margin-top:8px">After estimated software fees and a one-off rollout.<br>Screening estimate, not a guaranteed saving.</div>
      <div class="value-mini-wrap">
        <div class="value-mini"><span>Simple payback</span><strong>{escape(payback)}</strong><small>Assumes full run-rate</small></div>
        <div class="value-mini"><span>Capacity potentially freed</span><strong>{r['fte_released']:.2f} FTE</strong><small>Not an assumed staff cut</small></div>
      </div>
    </div>
    <div class="bridge">
      <div class="bridge-title">First-year value explained</div>
      <div class="bridge-line">{money(r['cash_benefit_eur'], True)} benefit
      <span class="minus"> − {money(r['annual_software_eur'], True)} software
      − {money(model_inputs.implementation_cost_eur, True)} setup</span>
      <span class="equals"> = {money(value, True)} net</span></div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------
# EVIDENCE | above the fold: actual published BLP customer impact
# ------------------------------------------------------------------
st.markdown("""
<div class="section-row">
  <div class="section-title">03 / Real-world impact: BLP has delivered before</div>
  <div class="section-note">Published BLP customer outcomes · not Isarwerk forecasts</div>
</div>
""", unsafe_allow_html=True)
proof1, proof2 = st.columns(2, gap="medium")
with proof1:
    st.markdown("""
    <div class="proof-card">
      <div><div class="proof-number">1.5 FTE</div><div class="proof-unit">running accounts payable<br>at Evatec today</div></div>
      <div>
        <div class="proof-kicker">EVATEC · MANUFACTURING</div>
        <div class="proof-title">1,000+ invoice backlog cleared within days of BLP go-live</div>
        <div class="proof-desc">BLP reports ~57,000 mixed documents / year and 1.5 AP FTE. The documents are not all invoices.</div>
        <a class="proof-source" href="https://blp.digital/resources/our-customers/evatec" target="_blank">Source: BLP customer story ↗</a>
      </div>
    </div>""", unsafe_allow_html=True)
with proof2:
    st.markdown("""
    <div class="proof-card">
      <div><div class="proof-number">30–40%</div><div class="proof-unit">lower resource needs<br>in Migros AP project</div></div>
      <div>
        <div class="proof-kicker">MIGROS · RETAIL</div>
        <div class="proof-title">12 fragmented AP processes consolidated into one</div>
        <div class="proof-desc">BLP reports this reduction as part of Migros's group-wide AP transformation.</div>
        <a class="proof-source" href="https://blp.digital/resources/our-customers/migros" target="_blank">Source: BLP customer story ↗</a>
      </div>
    </div>""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# CFO CLOSE | only the business-level process and next decision
# ------------------------------------------------------------------
st.markdown("""
<div class="bottom-strip">
  <div><strong>How BLP helps</strong><span> &nbsp; Invoices arrive → routine checks & matching → exceptions go to the right approver</span></div>
  <div><strong>CFO next decision</strong><span> &nbsp; Validate AP data, realizable savings & a BLP quote before approval</span></div>
</div>
<div class="footer-note">Illustrative German manufacturing case. Isarwerk is fictional. Annual invoice volume, automation assumptions, software pricing and setup cost are estimates. Capacity freed is not automatically cash saved. Simple payback assumes immediate steady-state savings; no rollout ramp or discounting is modelled.</div>
""", unsafe_allow_html=True)
