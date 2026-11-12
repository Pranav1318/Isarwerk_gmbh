"""Isarwerk | Four-minute CFO value demo for BLP Digital.

Replace app.py in the EXISTING GitHub repo; retain the original value_model.py.
Numbers are transparent illustrative estimates, not a BLP quote or customer forecast.
"""
from html import escape

import streamlit as st

from value_model import (
    BASE_VOLUME,
    COMPANY,
    INVOICE_CATEGORIES,
    SCENARIOS,
    ValueInputs,
    calculate,
)

st.set_page_config(
    page_title="Isarwerk | CFO value story",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# DESIGN: executive typography, deliberate whitespace and immediately visible proof.
# -----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {--navy:#10283b;--navy2:#1a3a4d;--ink:#193245;--muted:#728195;
--accent:#0e9f8a;--mint:#d7f8ed;--line:#e0e8ed;--paper:#f5f8fa;}
html,body,[class*="css"],.stApp{font-family:'DM Sans',sans-serif;}
.stApp,[data-testid="stAppViewContainer"]{background:var(--paper);color:var(--ink);}
.block-container{max-width:1300px;padding:1.18rem 1.55rem 2.2rem;}
#MainMenu,footer,[data-testid="stToolbar"]{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;height:32px;}
[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border:1px solid #e0e8ed!important;border-radius:17px!important;box-shadow:0 6px 22px rgba(15,49,67,.04);}
[data-testid="stVerticalBlock"]{gap:.7rem;}
[data-testid="stNumberInput"] label p,[data-testid="stSlider"] label p,[data-testid="stRadio"] label p{font-size:12px!important;font-weight:700!important;color:#55677a!important;}
[data-testid="stNumberInput"] input{font-weight:750;font-size:16px!important;color:var(--ink);border-radius:9px;}
[data-testid="stRadio"] [role="radiogroup"]{gap:.4rem;flex-wrap:wrap;}
[data-testid="stRadio"] [role="radiogroup"] label{background:#f3f7f8;border:1px solid #dfe7ea;border-radius:10px;padding:.35rem .5rem;flex:1;justify-content:center;font-size:12px;}
[data-testid="stRadio"] [role="radiogroup"] label p{font-size:11px!important;}
[data-testid="stSlider"]{padding-bottom:0!important;}
[data-testid="stSlider"] [data-baseweb="slider"]{margin-top:-5px;}
div.stButton>button{border:1px solid #dce7e7;border-radius:11px;padding:.42rem .52rem;font-size:11px;font-weight:800;background:#f3f9f8;color:#17665e;width:100%;min-height:38px;transition:all .18s;}
div.stButton>button:hover{border-color:#0e9f8a;background:#e0f8f0;color:#0d6c61;box-shadow:0 4px 10px #0e9f8a13;}
[data-testid="stExpander"]{background:#fff!important;border:1px solid #e1e9ed!important;border-radius:12px!important;}
[data-testid="stExpander"] summary{font-size:12px;font-weight:700;color:#536779;}
[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden;}
a{color:#088d7b;}
/* Compact heading */
.topline{display:flex;justify-content:space-between;align-items:center;gap:10px;margin:1px 0 13px;}
.brand{display:flex;gap:9px;align-items:center;font-family:Manrope,sans-serif;font-size:12px;font-weight:850;letter-spacing:1px;color:#1c3346;}
.brand-icon{display:inline-flex;width:29px;height:29px;align-items:center;justify-content:center;border-radius:9px;background:var(--navy);font-size:17px;color:#b6fce6;}
.brand-sub{font-weight:600;letter-spacing:.2px;color:#93a1ad;margin-left:2px;}
.livepill{font-size:10px;font-weight:800;color:#108776;letter-spacing:.9px;border:1px solid #bfe8db;border-radius:20px;background:#e8f8f1;padding:6px 10px;white-space:nowrap;}
.hero-title{font-family:Manrope,sans-serif;font-size:clamp(25px,2.55vw,35px);line-height:1.15;font-weight:850;letter-spacing:-1.1px;color:#112b3e;margin:0 0 6px;}
.hero-sub{font-size:13px;color:#607386;margin:0 0 12px;line-height:1.5;}
.chips{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:11px;}
.chips span{font-size:10.5px;font-weight:700;color:#53677a;background:#e8eff2;padding:6px 9px;border-radius:7px;}
.section-head{display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;margin:17px 0 10px;}
.section-head .name{font-family:Manrope,sans-serif;font-size:17px;font-weight:850;letter-spacing:-.5px;color:#193449;}
.section-head .hint{font-size:10.5px;color:#8392a0;font-weight:600;}
.eyebrow{font-size:10px;letter-spacing:1.5px;color:#11947f;font-weight:850;text-transform:uppercase;margin:0 0 5px;}
.input-heading{font-family:Manrope,sans-serif;font-size:17px;letter-spacing:-.45px;font-weight:850;color:#173044;margin-bottom:1px;}
.input-desc{font-size:11px;color:#8391a0;line-height:1.48;margin-bottom:4px;}
.small-info{color:#8896a2;font-size:10.5px;line-height:1.5;}
/* Main highlight */
.result-hero{position:relative;background:linear-gradient(115deg,#142e43 0%,#163e48 70%,#126b5d 135%);border-radius:19px;color:white;padding:23px 26px 21px;min-height:215px;overflow:hidden;box-shadow:0 12px 25px #142f4320;}
.result-hero:after{content:'';position:absolute;width:245px;height:245px;border:1px solid #ffffff22;border-radius:50%;right:-145px;top:-125px;box-shadow:0 0 0 46px #ffffff08,0 0 0 92px #ffffff06;pointer-events:none;}
.result-kicker{font-size:10px;letter-spacing:1.6px;font-weight:800;color:#9de5d4;text-transform:uppercase;}
.result-amount{font-family:Manrope,sans-serif;font-size:clamp(47px,4.5vw,68px);font-weight:850;letter-spacing:-3px;line-height:1.24;margin:5px 0 1px;color:#fff;}
.result-label{font-size:12px;font-weight:800;letter-spacing:.25px;color:#ebfbf5;}
.result-desc{color:#b8d4d2;font-size:11px;line-height:1.5;margin-top:7px;max-width:505px;}
.result-flag{display:inline-block;background:#ffffff13;border:1px solid #ffffff2a;border-radius:50px;padding:6px 10px;font-size:10px;color:#c9ffed;font-weight:800;margin-top:10px;}
.result-flag.negative{color:#ffe1cd;}
.kpi-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:10px;}
.kpi{background:#fff;border:1px solid #dfe9ed;border-radius:13px;min-height:100px;padding:13px 14px;}
.kpi-label{font-size:10.5px;color:#788995;font-weight:750;line-height:1.4;}
.kpi-number{font-family:Manrope,sans-serif;font-size:clamp(18px,2.05vw,26px);font-weight:850;line-height:1.35;letter-spacing:-.65px;color:#17334a;margin-top:4px;}
.kpi-note{font-size:9.5px;color:#95a1aa;line-height:1.4;margin-top:3px;}
/* Economic bridge and live bars */
.fin-bridge{display:grid;grid-template-columns:1.16fr 1fr 1fr 1.12fr;align-items:stretch;gap:8px;}
.fin-tile{background:#fff;border:1px solid #e0e9ed;border-radius:13px;padding:14px 14px 12px;position:relative;min-height:94px;}
.fin-tile.final{background:#eaf9f2;border-color:#b8e5d7;}
.fin-title{font-size:10.5px;font-weight:750;color:#697e8a;line-height:1.35;}
.fin-value{font-family:Manrope,sans-serif;font-size:clamp(18px,1.9vw,24px);font-weight:850;letter-spacing:-.75px;color:#123a47;margin-top:6px;}
.fin-tile.final .fin-value{color:#007f6b;}
.fin-tile.final.bad{background:#fff4ee;border-color:#f1d9cc}.fin-tile.final.bad .fin-value{color:#aa5740;}
.fin-sub{font-size:9.5px;color:#94a1aa;line-height:1.4;margin-top:3px;}
.math-sign{position:absolute;right:-16px;top:35px;background:#e8eff2;width:21px;height:21px;border-radius:50%;display:flex;align-items:center;justify-content:center;z-index:2;color:#697d89;font-weight:900;font-size:13px;}
.breakeven-line{margin-top:9px;border-radius:9px;background:#ecf3f4;padding:9px 12px;color:#4f6879;font-size:11px;line-height:1.55;}
.breakeven-line strong{color:#136f64;}
/* Context, workflow, customer proof */
.workload-card{background:#fff;border:1px solid #e0e8ed;border-radius:15px;padding:14px 17px 13px;min-height:160px;}
.workrow{display:flex;justify-content:space-between;align-items:baseline;gap:8px;font-size:11px;font-weight:750;color:#526b7b;margin:10px 0 5px;}
.workrow strong{font-family:Manrope,sans-serif;font-size:12px;font-weight:850;color:#223d4f;}
.track{height:13px;border-radius:6px;background:#e7edf1;overflow:hidden;display:flex;}
.track .before{background:#a2b7c0;height:100%;}
.track .after{background:#17ab90;height:100%;transition:width .4s ease;}
.track .saved{background:#d7f1e9;height:100%;transition:width .4s ease;}
.work-foot{font-size:10.5px;color:#6d8792;margin-top:8px;line-height:1.55;}
.mix-track{display:flex;height:13px;border-radius:6px;overflow:hidden;margin:13px 0 8px;background:#e9f0f2;}
.mix-track span{height:100%;}
.mix-legend{display:grid;grid-template-columns:1fr 1fr;gap:6px 12px;}
.mix-item{font-size:10px;color:#667b88;line-height:1.5;}
.mix-item b{color:#284558;}
.dot{width:8px;height:8px;display:inline-block;border-radius:2px;margin-right:5px;}
.proof-card{background:#fff;border:1px solid #e0e8ed;border-radius:15px;padding:14px 17px;min-height:143px;display:flex;align-items:center;gap:17px;}
.proof-number{font-family:Manrope,sans-serif;font-size:clamp(24px,2.35vw,34px);font-weight:850;letter-spacing:-1.4px;line-height:1.1;color:#0c9880;min-width:132px;white-space:nowrap;}
.proof-unit{font-size:10px;color:#8798a1;line-height:1.4;margin-top:5px;font-weight:650;}
.proof-title{font-family:Manrope,sans-serif;font-size:12px;font-weight:850;line-height:1.4;color:#233e4d;margin-bottom:4px;}
.proof-desc{font-size:10.5px;color:#71838f;line-height:1.5;margin-bottom:5px;}
.proof-source{font-size:10px;font-weight:750;color:#0d8b78;text-decoration:none;}
.decision{background:#eaf7f2;border:1px solid #c7e8dc;border-radius:12px;padding:12px 15px;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:center;margin-top:13px;}
.decision strong{font-size:12px;color:#1f5d50;}
.decision span{font-size:11px;color:#527468;}
.footnote{font-size:10px;color:#8495a1;line-height:1.6;margin-top:12px;}
@media(max-width:970px){.block-container{padding:1rem}.fin-bridge{grid-template-columns:repeat(2,minmax(0,1fr));}.fin-tile:nth-child(2) .math-sign{display:none;}.fin-tile{min-height:90px}.kpi-grid{gap:7px}.kpi{padding:11px}.result-hero{padding:20px}}
@media(max-width:600px){.result-amount{font-size:48px}.kpi-grid{grid-template-columns:1fr 1fr 1fr}.kpi-number{font-size:18px}.proof-card{gap:11px}.proof-number{min-width:94px;font-size:25px;min-width:98px}.mix-legend{grid-template-columns:1fr}.hero-title{font-size:26px}}
</style>
""", unsafe_allow_html=True)


def euros(value: float, compact: bool = True) -> str:
    """Signed Euro values; show more precision in exports than in visual headings."""
    negative = "−" if value < 0 else ""
    amount = abs(value)
    if compact and amount >= 1000:
        return f"{negative}€{amount / 1000:,.1f}k"
    return f"{negative}€{amount:,.0f}"


def numeric(value: float) -> str:
    return f"{value:,.0f}"


def reset_case() -> None:
    """Callback runs before widgets are re-instantiated on Streamlit rerun."""
    st.session_state.case_scenario = "Base"
    st.session_state.cash_pct = 60
    st.session_state.touch_pct = 65
    st.session_state.invoice_count = BASE_VOLUME
    st.session_state.hourly_cost = 45.0
    st.session_state.unit_fee = 0.38
    st.session_state.setup_cost = 50_000
    st.session_state.productive_hours = 1_540
    for i, (_, _, default_minutes) in enumerate(INVOICE_CATEGORIES):
        st.session_state[f"minutes_{i}"] = float(default_minutes)


def stress_case() -> None:
    # Challenge the CASH REALIZATION only: capacity reduction is unchanged.
    st.session_state.cash_pct = 30


def scenario_changed() -> None:
    reduction, cashable = SCENARIOS[st.session_state.case_scenario]
    st.session_state.touch_pct = int(round(reduction * 100))
    st.session_state.cash_pct = int(round(cashable * 100))


# Initialize before any widgets. Keeps action buttons reliable after GitHub deployment.
for key, default in {
    "case_scenario": "Base",
    "cash_pct": 60,
    "touch_pct": 65,
    "invoice_count": BASE_VOLUME,
    "hourly_cost": 45.0,
    "unit_fee": 0.38,
    "setup_cost": 50_000,
    "productive_hours": 1_540,
    **{f"minutes_{i}": float(row[2]) for i, row in enumerate(INVOICE_CATEGORIES)},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


st.markdown("""
<div class="topline">
 <div class="brand"><span class="brand-icon">◈</span> BLP DIGITAL <span class="brand-sub">/ Value Engineering</span></div>
 <div class="livepill">● LIVE CFO DEMO</div>
</div>
<div class="hero-title">What is AP automation worth to Isarwerk?</div>
<div class="hero-sub">A live financial conversation: change one assumption, see the investment case respond.</div>
<div class="chips">
 <span>ISARWERK PRÄZISION · FICTIONAL</span><span>€320m revenue</span>
 <span>1,100 employees</span><span>7 AP FTE · estimated</span><span>SAP S/4HANA</span>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([0.85, 1.35], gap="medium", vertical_alignment="top")
with left:
    with st.container(border=True):
        st.markdown('<div class="eyebrow">01 / YOUR ASSUMPTIONS</div><div class="input-heading">Run your own scenario</div><div class="input-desc">Start from Isarwerk’s fictional case. Changes are instant.</div>', unsafe_allow_html=True)
        a, b = st.columns(2, gap="small")
        with a:
            invoices = st.number_input(
                "Invoices / year", min_value=1_000, max_value=1_500_000,
                step=1_000, key="invoice_count",
                help="60,600 is estimated from the supplied Excel scenario, not observed company records.",
            )
        with b:
            hourly_cost = st.number_input(
                "Employer cost / hour (€)", min_value=5.0, max_value=250.0,
                step=1.0, key="hourly_cost",
                help="€45 is an external German employer-cost benchmark; not Isarwerk payroll data.",
            )
        st.radio(
            "Scenario preset", options=list(SCENARIOS),
            horizontal=True, key="case_scenario", on_change=scenario_changed,
            help="Presets pair manual time reduction with a share of freed time that may generate cash value.",
        )
        st.slider(
            "Reduction in manual invoice work (%)", min_value=0, max_value=95,
            step=5, key="touch_pct",
            help="Efficiency assumption. It is not a verified BLP automation rate.",
        )
        st.slider(
            "Of freed hours, how much is cashable? (%)", min_value=0, max_value=100,
            step=5, key="cash_pct",
            help="Avoided overtime or hiring, or equivalent validated cost reduction. Capacity release alone is not cash.",
        )
        button1, button2 = st.columns(2, gap="small")
        with button1:
            st.button("⚡ CFO stress test · 30%", on_click=stress_case,
                      help="Keep the time savings, but only count 30% of freed hours as cashable.")
        with button2:
            st.button("↺ Restore base case", on_click=reset_case)
        st.markdown('<div class="small-info">Low-confidence estimates until validated with Finance and the AP team.</div>', unsafe_allow_html=True)

# Keep inputs separate from published customer results; the two must never be conflated.
with left:
    with st.expander("Optional: edit software, implementation & handling assumptions", expanded=False):
        p, q, hours = st.columns(3, gap="small")
        with p:
            st.number_input("Software €/invoice (estimate)", min_value=0.0, max_value=20.0,
                            step=0.01, format="%.2f", key="unit_fee",
                            help="Competitor-informed budget placeholder, not official BLP pricing.")
        with q:
            st.number_input("One-off rollout (€)", min_value=0, max_value=1_000_000,
                            step=5_000, key="setup_cost",
                            help="Illustrative implementation allowance; not a BLP proposal.")
        with hours:
            productive_hours = st.number_input("Productive hours / FTE / yr", min_value=500,
                                               max_value=2_500, step=20, key="productive_hours")
        st.caption("Manual touch-time estimates by invoice category (minutes per invoice):")
        mins_cols = st.columns(4, gap="small")
        category_minutes = []
        for i, ((label, _, base_minutes), col) in enumerate(zip(INVOICE_CATEGORIES, mins_cols)):
            with col:
                short = ("Direct PO", "Indirect PO", "Freight", "Non-PO / other")[i]
                category_minutes.append(st.number_input(
                    short, min_value=0.0, max_value=240.0, step=1.0,
                    key=f"minutes_{i}",
                ))

inputs = ValueInputs(
    invoices_per_year=int(invoices),
    ap_team_fte=7.0,
    annual_hours_per_fte=float(productive_hours),
    employer_hourly_cost_eur=float(hourly_cost),
    software_fee_per_invoice_eur=float(st.session_state.unit_fee),
    implementation_cost_eur=float(st.session_state.setup_cost),
    minutes_by_category=tuple(category_minutes),
)
r = calculate(inputs, st.session_state.touch_pct / 100, st.session_state.cash_pct / 100)
first_year = r["year_one_net_eur"]
net_color_class = "" if first_year >= 0 else "bad"
annual_recurring = r["annual_net_eur"]
payback = f'{r["payback_months"]:.1f} mo' if r["payback_months"] is not None else "None"
gross = r["gross_capacity_eur"]
threshold = ((r["annual_software_eur"] + inputs.implementation_cost_eur) / gross * 100) if gross > 0 else None

preset_reduction, preset_cash = SCENARIOS[st.session_state.case_scenario]
scenario_status = ("preset" if st.session_state.touch_pct == round(preset_reduction * 100)
                   and st.session_state.cash_pct == round(preset_cash * 100) else "customized")

if first_year > 0:
    decision_label = "Positive first-year estimate · validate before investing"
    decision_class = ""
elif annual_recurring > 0:
    decision_label = "Recurring benefit positive · first-year costs not yet recovered"
    decision_class = "negative"
else:
    decision_label = "No recurring cash payback at these assumptions"
    decision_class = "negative"

with right:
    st.markdown(f"""
    <div class="result-hero">
      <div class="result-kicker">02 / THE CFO ANSWER · {escape(st.session_state.case_scenario.upper())} {escape(scenario_status.upper())}</div>
      <div class="result-amount">{escape(euros(first_year))}</div>
      <div class="result-label">Estimated net financial benefit in Year 1</div>
      <div class="result-desc">After estimated recurring software spend and one-time rollout cost. Based on cashable benefits—not all time saved.</div>
      <div class="result-flag {decision_class}">● {escape(decision_label)}</div>
    </div>
    <div class="kpi-grid">
      <div class="kpi"><div class="kpi-label">Annual net benefit · Year 2 onward</div><div class="kpi-number">{escape(euros(annual_recurring))}</div><div class="kpi-note">Run-rate; not extra in Year 1</div></div>
      <div class="kpi"><div class="kpi-label">Simple setup payback</div><div class="kpi-number">{escape(payback)}</div><div class="kpi-note">Assumes full run-rate from Day 1</div></div>
      <div class="kpi"><div class="kpi-label">Workload capacity freed</div><div class="kpi-number">{r['fte_released']:.2f} FTE</div><div class="kpi-note">Not automatically headcount savings</div></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-head"><div class="name">03 / Where the financial value comes from</div><div class="hint">An auditable four-number bridge · updates live</div></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="fin-bridge">
  <div class="fin-tile">
    <div class="fin-title">Annual cashable AP benefit</div>
    <div class="fin-value">{escape(euros(r['cash_benefit_eur']))}</div>
    <div class="fin-sub">{escape(euros(gross))} capacity value × {st.session_state.cash_pct}% cashable</div>
    <div class="math-sign">−</div>
  </div>
  <div class="fin-tile">
    <div class="fin-title">Annual software allowance</div>
    <div class="fin-value">{escape(euros(r['annual_software_eur']))}</div>
    <div class="fin-sub">{numeric(inputs.invoices_per_year)} invoices × €{inputs.software_fee_per_invoice_eur:.2f}</div>
    <div class="math-sign">−</div>
  </div>
  <div class="fin-tile">
    <div class="fin-title">One-time implementation</div>
    <div class="fin-value">{escape(euros(inputs.implementation_cost_eur))}</div>
    <div class="fin-sub">Illustrative first-year allowance</div>
    <div class="math-sign">=</div>
  </div>
  <div class="fin-tile final {net_color_class}">
    <div class="fin-title">Net benefit · Year 1</div>
    <div class="fin-value">{escape(euros(first_year))}</div>
    <div class="fin-sub">Benefit less both cost lines</div>
  </div>
</div>
""", unsafe_allow_html=True)

if threshold is None:
    benchmark_text = "A break-even cash-conversion threshold cannot be calculated with zero capacity value."
elif threshold > 100:
    benchmark_text = f"Year-one break-even needs {threshold:.1f}% cash realization, above the model's maximum of 100%."
else:
    benchmark_text = (f"<strong>At least {threshold:.1f}% cashable time</strong> covers first-year costs in this model. "
                      f"You are testing <strong>{st.session_state.cash_pct}%</strong>. "
                      "This is why a CFO should challenge cash conversion, not just automation speed.")
st.markdown(f'<div class="breakeven-line">↗ <strong>CFO sensitivity check:</strong> {benchmark_text}</div>', unsafe_allow_html=True)

st.markdown('<div class="section-head"><div class="name">04 / Real-world BLP impact</div><div class="hint">Public customer outcomes · not used in Isarwerk ROI assumptions</div></div>', unsafe_allow_html=True)
p1, p2 = st.columns(2, gap="medium")
with p1:
    st.markdown("""
    <div class="proof-card">
      <div><div class="proof-number">1.5 FTE</div><div class="proof-unit">Evatec · accounts payable<br>after BLP deployment</div></div>
      <div><div class="proof-title">1,000+ invoice backlog cleared within days of go-live</div>
        <div class="proof-desc">Swiss equipment manufacturer now processes AP with 1.5 FTE; its 57k annual documents include other document types, not just invoices.</div>
        <a class="proof-source" href="https://blp.digital/resources/our-customers/evatec" target="_blank">BLP customer story ↗</a>
      </div>
    </div>""", unsafe_allow_html=True)
with p2:
    st.markdown("""
    <div class="proof-card">
      <div><div class="proof-number">30–40%</div><div class="proof-unit">Migros · reduction in<br>resource needs</div></div>
      <div><div class="proof-title">12 separate AP processes became one standardized flow</div>
        <div class="proof-desc">BLP reports 30–40% lower resource requirements in Migros’s group-wide SAP transformation, with improved transparency.</div>
        <a class="proof-source" href="https://blp.digital/resources/our-customers/migros" target="_blank">BLP customer story ↗</a>
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="section-head"><div class="name">05 / What changes operationally</div><div class="hint">Fixed mix, scaled with annual volume</div></div>', unsafe_allow_html=True)
wleft, wright = st.columns(2, gap="medium")
remaining_pct = (r["remaining_manual_hours"] / r["baseline_manual_hours"] * 100) if r["baseline_manual_hours"] > 0 else 0
saved_pct = 100 - remaining_pct
with wleft:
    st.markdown(f"""
    <div class="workload-card">
      <div class="eyebrow">FROM MANUAL WORK TO CAPACITY</div>
      <div class="workrow"><span>Before automation</span><strong>{numeric(r['baseline_manual_hours'])} hrs/year · {r['baseline_manual_fte']:.1f} FTE</strong></div>
      <div class="track"><span class="before" style="width:100%"></span></div>
      <div class="workrow"><span>After proposed reduction</span><strong>{numeric(r['remaining_manual_hours'])} hrs/year</strong></div>
      <div class="track"><span class="after" style="width:{remaining_pct:.2f}%"></span><span class="saved" style="width:{saved_pct:.2f}%"></span></div>
      <div class="work-foot"><strong>{numeric(r['hours_released'])} hrs/year released</strong> · redeployable capacity; only the cashable share contributes to ROI.</div>
    </div>
    """, unsafe_allow_html=True)
with wright:
    mix_colors = ["#15465d", "#318794", "#15a78e", "#a6dacb"]
    segments, legends = [], []
    for item, color in zip(r["category_mix"], mix_colors):
        percent = (item["invoices"] / inputs.invoices_per_year * 100) if inputs.invoices_per_year else 0
        segments.append(f'<span style="width:{percent:.3f}%;background:{color}"></span>')
        short = item["name"].split(" · ")[0]
        legends.append(f'<div class="mix-item"><span class="dot" style="background:{color}"></span><b>{escape(short)}</b> · {numeric(item["invoices"])} · {item["minutes"]:g} min</div>')
    st.markdown(f"""
    <div class="workload-card">
      <div class="eyebrow">WHAT THE WORKLOAD INCLUDES</div>
      <div style="font-family:Manrope,sans-serif;font-size:18px;font-weight:850;color:#1c3c4b;margin:9px 0 -5px">{numeric(inputs.invoices_per_year)} invoices / year</div>
      <div class="mix-track">{''.join(segments)}</div>
      <div class="mix-legend">{''.join(legends)}</div>
      <div class="work-foot">Invoice counts and touch times are estimated, not measured.</div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("""
<div class="decision"><strong>THE NEXT CFO DECISION</strong><span>Validate invoice volume and time with AP · cashable savings with Finance · scope, pricing and pilot results with BLP</span></div>
<div class="footnote">Illustrative manufacturing example; Isarwerk is fictional. Software cost (€0.38/invoice), setup (€50k), time reduction and monetization rates are assumptions, <b>not BLP quotations or proven Isarwerk outcomes</b>. Payback is simple setup payback at immediate steady-state savings (no rollout ramp or discounted cash flow). Released FTE is workload capacity, not a staffing recommendation.</div>
""", unsafe_allow_html=True)

with st.expander("Assumption confidence, sources & calculations · for CFO follow-up", expanded=False):
    st.markdown("""
| Driver | Base case | Confidence | Validation owner |
|---|---:|---|---|
| Annual supplier invoices | 60,600 | Low; estimated volume and mix | AP / ERP export |
| Manual processing time | 8–15 min by type | Low; working assumption | AP time study |
| Employer cost | €45/hr | Medium-low; national benchmark | Finance payroll |
| Time reduction | 65% | Low; hypothetical scenario | BLP pilot |
| Cash conversion of freed time | 60% | Low; finance hypothesis | CFO / controlling |
| Software cost | €0.38 / invoice | Low; competitor-informed placeholder | BLP quotation |
| Setup cost | €50,000 one-off | Low; modeled budget | BLP & IT scope |
| AP team | 7 FTE | Low; fictional context | AP lead |
""")
    st.markdown("**Formula logic**: invoice count × manual handling minutes → baseline manual hours; manual hours × time reduction → saved hours; saved hours × cost/hour × cash conversion → cashable benefit; minus recurring software and one-time setup → first-year net benefit. Year 2 onward excludes the one-time setup cost.")
    st.markdown("**Public reference points**: [BLP Finance](https://blp.digital/solutions/finance) · [BLP Evatec](https://blp.digital/resources/our-customers/evatec) · [BLP Migros](https://blp.digital/resources/our-customers/migros) · [Klippa pricing](https://www.klippa.com/en/invoice-processing/prices/) · [ISR standard AP setup offer](https://isr.de/en/technologies/isr/accounts-payable-flow/offer/). BLP does not publish a fixed price for this modeled use case.")
    st.markdown("**Preset comparison on the current invoice volume, hourly cost and commercial assumptions**")
    comparison = []
    for label, (time_saved, cash_share) in SCENARIOS.items():
        x = calculate(inputs, time_saved, cash_share)
        comparison.append({
            "Scenario": label,
            "Effort reduction": f"{time_saved:.0%}",
            "Cash conversion": f"{cash_share:.0%}",
            "Year 1 net": euros(x["year_one_net_eur"]),
            "Year 2+ net / year": euros(x["annual_net_eur"]),
            "Payback": f'{x["payback_months"]:.1f} months' if x["payback_months"] is not None else "No cash payback",
        })
    st.dataframe(comparison, hide_index=True, use_container_width=True)

