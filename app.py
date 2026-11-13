"""Business Value Studio | an interactive, fictional workflow value model.

Standalone Streamlit app. Built around the final Isarwerk Excel assumptions.
Vendor pricing and model savings are estimates, not official BLP quotes.
"""
from __future__ import annotations
from html import escape
import pandas as pd
import streamlit as st

COMPANY = "Isarwerk Präzision"
REVENUE = 320_000_000
STAFF = 1_100
ERP = "SAP S/4HANA"
BASE_VOLUME = 60_600
HOURS_PER_FTE = 1_650
MIX = (
    ("Direct materials / components", 24_600, 10),
    ("Indirect goods / services", 16_000, 11),
    ("Freight / logistics", 12_000, 11),
    ("Non-PO / other expenses", 8_000, 15),
)
SCENARIOS = {"Conservative": (50, 40), "Base": (60, 50), "Optimistic": (70, 60)}
LINKS = {
    "evatec": "https://blp.digital/resources/our-customers/evatec",
    "migros": "https://blp.digital/resources/our-customers/migros",
    "klippa": "https://www.klippa.com/en/invoice-processing/prices/",
    "isr": "https://isr.de/en/technologies/isr/accounts-payable-flow/offer/",
}


def euros(value: float, compact: bool = True) -> str:
    minus = "−" if value < 0 else ""
    v = abs(float(value))
    if compact and v >= 1_000_000:
        return f"{minus}€{v / 1_000_000:,.2f}m"
    if compact and v >= 1_000:
        return f"{minus}€{v / 1_000:,.1f}k"
    return f"{minus}€{v:,.0f}"


def number(value: float) -> str:
    return f"{value:,.0f}"


def compute(volume: int, cost_per_hour: float, effort_pct: int, cash_pct: int,
            platform_month: float, usage_rate: float, setup: float,
            minutes: tuple[float, ...] | None = None, hours_per_fte: int = HOURS_PER_FTE) -> dict:
    minutes = minutes if minutes is not None else tuple(x[2] for x in MIX)
    avg_minutes = sum(n * mins for (_, n, _), mins in zip(MIX, minutes)) / BASE_VOLUME
    manual_hours = volume * avg_minutes / 60
    hours_freed = manual_hours * effort_pct / 100
    hours_after = manual_hours - hours_freed
    freed_capacity = hours_freed * cost_per_hour
    actual_cash = freed_capacity * cash_pct / 100
    annual_platform = 12 * platform_month
    annual_usage = volume * usage_rate
    annual_cost = annual_platform + annual_usage
    annual_net = actual_cash - annual_cost
    year1_cost = annual_cost + setup
    year1_net = actual_cash - year1_cost
    return {
        "minutes": avg_minutes,
        "before_hours": manual_hours,
        "after_hours": hours_after,
        "freed_hours": hours_freed,
        "before_fte": manual_hours / hours_per_fte,
        "after_fte": hours_after / hours_per_fte,
        "freed_fte": hours_freed / hours_per_fte,
        "capacity_eur": freed_capacity,
        "cash_eur": actual_cash,
        "annual_platform": annual_platform,
        "annual_usage": annual_usage,
        "annual_cost": annual_cost,
        "annual_net": annual_net,
        "year1_cost": year1_cost,
        "year1_net": year1_net,
        "roi": (year1_net / year1_cost * 100) if year1_cost > 0 else None,
        "payback_months": setup / (annual_net / 12) if annual_net > 0 else None,
    }


def forecast(years: int, growth_pct: float, current_revenue: float,
             annual_net: float, setup: float,
             extra_sales: bool, uplift_pct: float, profit_margin_pct: float) -> list[dict]:
    rows = []
    running_value = 0.0
    for y in range(1, years + 1):
        baseline_revenue = current_revenue * (1 + growth_pct/100)**y
        added_revenue = baseline_revenue * uplift_pct/100 if extra_sales and y >= 2 else 0.0
        extra_contribution = added_revenue * profit_margin_pct / 100
        yearly_value = annual_net - (setup if y == 1 else 0)
        running_value += yearly_value
        rows.append({"year": y, "revenue": baseline_revenue, "extra_revenue": added_revenue,
                     "with_extra": baseline_revenue + added_revenue,
                     "extra_contribution": extra_contribution,
                     "process_net": yearly_value, "total_process_net": running_value})
    return rows


def choose_preset():
    st.session_state.effort_pct, st.session_state.cash_pct = SCENARIOS[st.session_state.scenario]


def reset_inputs():
    st.session_state.update({
        "scenario": "Base", "effort_pct": 60, "cash_pct": 50,
        "volume": BASE_VOLUME, "hourly_cost": 45.0,
        "platform_month": 300.0, "usage_rate": 0.32,
        "setup_cost": 12_100.0, "hours_per_fte": HOURS_PER_FTE,
        **{f"mins_{i}": float(x[2]) for i, x in enumerate(MIX)},
    })


def stress_test():
    st.session_state.cash_pct = 30


st.set_page_config(page_title="BLP Digital | Business Value Studio", page_icon="◈",
                   layout="wide", initial_sidebar_state="collapsed")
for k, v in {
    "scenario": "Base", "effort_pct": 60, "cash_pct": 50,
    "volume": BASE_VOLUME, "hourly_cost": 45.0,
    "platform_month": 300.0, "usage_rate": 0.32, "setup_cost": 12_100.0,
    "hours_per_fte": HOURS_PER_FTE,
    **{f"mins_{i}": float(x[2]) for i,x in enumerate(MIX)},
    "years": 5, "growth": 3.0, "extra_sales": False,
    "uplift": 0.25, "margin": 25.0,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {--navy:#10283b;--navy2:#1a3a4d;--ink:#193245;--muted:#728195;
--accent:#0e9f8a;--mint:#d7f8ed;--line:#e0e8ed;--paper:#f5f8fa;}
html,body,[class*="css"],.stApp{font-family:'DM Sans',sans-serif;}
.stApp,[data-testid="stAppViewContainer"]{background:var(--paper);color:var(--ink);}
.block-container{max-width:1280px;padding:1.18rem 1.55rem 2.2rem;}
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
.section-head{display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;margin:18px 0 10px;}
.section-head .name{font-family:Manrope,sans-serif;font-size:17px;font-weight:850;letter-spacing:-.5px;color:#193449;}
.section-head .hint{font-size:10.5px;color:#8392a0;font-weight:600;}
.eyebrow{font-size:10px;letter-spacing:1.5px;color:#11947f;font-weight:850;text-transform:uppercase;margin:0 0 5px;}
.input-heading{font-family:Manrope,sans-serif;font-size:17px;letter-spacing:-.45px;font-weight:850;color:#173044;margin-bottom:1px;}
.input-desc{font-size:11px;color:#8391a0;line-height:1.48;margin-bottom:4px;}
.small-info{color:#8896a2;font-size:10.5px;line-height:1.5;}

/* Before versus after. */
.compare-flow{display:grid;grid-template-columns:minmax(0,1fr) 96px minmax(0,1fr);gap:10px;align-items:stretch;}
.compare-panel{background:#fff;border:1px solid #dfe8ed;border-radius:16px;padding:15px 18px 13px;min-width:0;box-shadow:0 4px 12px #102f4010;}
.compare-panel.after{background:linear-gradient(130deg,#ecfcf5 0%,#f9fffc 90%);border-color:#a7decf;}
.compare-tag{display:inline-block;font-size:10px;font-weight:850;letter-spacing:1.2px;color:#6a7e88;}
.compare-panel.after .compare-tag{color:#06846f;}
.compare-big{font-family:Manrope,sans-serif;font-size:clamp(27px,3vw,41px);letter-spacing:-1.8px;font-weight:850;line-height:1.15;color:#17364b;margin:7px 0 1px;}
.compare-panel.after .compare-big{color:#078773;}
.compare-big small{font-size:12px;letter-spacing:0;font-family:'DM Sans',sans-serif;color:#778b98;font-weight:700;}
.compare-primary{font-size:10px;color:#8194a0;margin-bottom:10px;}
.compare-row{display:flex;align-items:center;justify-content:space-between;gap:10px;border-top:1px solid #e8eef1;padding:8px 0;color:#526c79;font-size:11px;line-height:1.35;}
.compare-row b{font-family:Manrope,sans-serif;font-size:14px;font-weight:850;color:#234054;white-space:nowrap;}
.compare-panel.after .compare-row b{color:#117f6e;}
.compare-arrow{display:flex;align-items:center;justify-content:center;flex-direction:column;text-align:center;min-width:0;gap:5px;}
.compare-arrow .arrow-circle{width:39px;height:39px;display:flex;align-items:center;justify-content:center;border-radius:50%;background:#d7f4e9;color:#0d937d;font-size:24px;font-weight:750;}
.compare-arrow .arrow-pct{font-size:16px;font-weight:850;color:#0c8a75;font-family:Manrope,sans-serif;line-height:1.1;}
.compare-arrow .arrow-copy{font-size:9px;line-height:1.45;color:#8496a0;font-weight:700;}
.impact-strip{background:#f1f7f7;border:1px solid #d6e8e6;border-radius:12px;margin:9px 0 0;padding:9px 14px;display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap;}
.impact-strip strong{font-size:12px;color:#147763;}
.impact-strip span{font-size:10.5px;color:#647e88;}
.finance-compare{background:linear-gradient(120deg,#183247 0%,#18464e 100%);border-radius:16px;padding:17px 20px;margin-top:10px;color:#fff;}
.fin-compare-grid{display:grid;grid-template-columns:1fr 75px 1fr;align-items:center;gap:12px;}
.fin-compare-kicker{font-size:10px;font-weight:850;letter-spacing:1px;color:#a4c2c8;text-transform:uppercase;}
.fin-compare-val{font-family:Manrope,sans-serif;font-size:clamp(23px,2.7vw,35px);font-weight:850;letter-spacing:-1.5px;line-height:1.25;color:#fff;margin-top:4px;}
.fin-compare-after .fin-compare-val{color:#9effd7;}
.fin-compare-sub{font-size:10px;color:#b8d1d3;line-height:1.45;margin-top:3px;}
.fin-mid{font-family:Manrope,sans-serif;font-size:27px;font-weight:850;color:#9ee8d6;text-align:center;}
.fin-bars{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0 4px;}
.fin-bar-label{font-size:9px;color:#a6c7c7;font-weight:750;margin-bottom:4px;}
.fin-bar-track{height:9px;border-radius:20px;background:#ffffff20;overflow:hidden;}
.fin-bar-before{height:100%;background:#a9c0cb;border-radius:20px;transition:width .3s;}
.fin-bar-after{height:100%;background:#6fe0ba;border-radius:20px;transition:width .3s;}
.fin-revenue{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;border-top:1px solid #ffffff24;margin-top:12px;padding-top:10px;}
.fin-revenue span{font-size:10px;color:#c2d7d7;line-height:1.5;}
.fin-revenue b{color:#c4ffde;font-weight:850;}
.fin-gain{display:inline-block;background:#c4fce9;color:#0a6655;border-radius:8px;padding:6px 9px;font-size:11px;font-weight:850;white-space:nowrap;}
.fin-gain.negative{color:#9a431b;background:#ffe6d1;}
@media(max-width:850px){.compare-flow{grid-template-columns:1fr 65px 1fr;gap:6px}.compare-panel{padding:12px}.compare-arrow .arrow-pct{font-size:13px}.fin-compare-grid{grid-template-columns:1fr 45px 1fr;gap:5px}.finance-compare{padding:13px}}
@media(max-width:600px){.compare-flow{grid-template-columns:1fr;}.compare-arrow{flex-direction:row;}.compare-arrow .arrow-copy{max-width:125px}.compare-arrow .arrow-circle{transform:rotate(90deg);height:30px;width:30px;font-size:18px}.fin-compare-val{font-size:21px}.fin-compare-grid{grid-template-columns:1fr 24px 1fr}.fin-mid{font-size:18px}.fin-compare-sub{font-size:9px}}

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

.revenue-panel{background:#fff;border:1px solid #dfe8ed;border-radius:13px;padding:13px 17px;margin-top:10px;}
.revenue-panel .label{font-size:10px;letter-spacing:1px;font-weight:850;color:#8194a0;text-transform:uppercase;}
.revenue-panel .big{font-family:Manrope,sans-serif;font-size:22px;font-weight:850;letter-spacing:-.8px;color:#1b384d;margin:6px 0 4px;}
.revenue-panel .desc{font-size:11px;line-height:1.55;color:#687e8a;}
.case-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;}
.details-kpis{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:10px;}
.details-kpis .tile{background:#fff;border:1px solid #dfe8ed;border-radius:13px;padding:12px 13px;}
.details-kpis .lbl{font-size:10px;color:#718594;font-weight:750;line-height:1.4;}
.details-kpis .val{font-family:Manrope,sans-serif;font-size:20px;font-weight:850;margin-top:4px;color:#19394b;}
.main-section-note{font-size:11px;color:#728492;line-height:1.6;margin:7px 0;}
.simple-price{font-size:11px;line-height:1.7;color:#61798a;background:#f5f8f9;border:1px solid #e2eaed;padding:10px 12px;border-radius:10px;margin-top:6px;}
.extra-note{font-size:10px;line-height:1.65;color:#8395a1;margin:8px 0;}
@media(max-width:900px){.case-grid{grid-template-columns:repeat(2,minmax(0,1fr));}}
@media(max-width:550px){.case-grid{grid-template-columns:1fr;}}
@media(max-width:760px){.details-kpis{grid-template-columns:repeat(2,1fr)}.revenue-panel .big{font-size:19px}}
</style>
""", unsafe_allow_html=True)

# Header stays close to the original version's visual design.
st.markdown(f"""
<div class="topline">
  <div class="brand"><span class="brand-icon">◈</span> BLP DIGITAL <span class="brand-sub">/ Value Studio</span></div>
  <div class="livepill">● LIVE DEMO</div>
</div>
<div class="hero-title">What could smarter ERP workflows be worth?</div>
<div class="hero-sub">Change the assumptions. See the financial and operational impact instantly.</div>
<div class="chips">
  <span>{escape(COMPANY)} · fictional</span>
  <span>{euros(REVENUE)} annual revenue</span>
  <span>{STAFF:,} employees</span>
  <span>60,600 annual documents · estimated</span>
  <span>{escape(ERP)}</span>
</div>
""", unsafe_allow_html=True)

# The ORIGINAL left-controls / right-results design, kept for fast live editing.
left, right = st.columns([0.86, 1.34], gap="medium", vertical_alignment="top")
with left:
    with st.container(border=True):
        st.markdown('<div class="eyebrow">01 / YOUR ASSUMPTIONS</div>'
                    '<div class="input-heading">Run your scenario</div>'
                    '<div class="input-desc">Start with Isarwerk. Change any number to see its effect.</div>',
                    unsafe_allow_html=True)
        a, b = st.columns(2, gap="small")
        with a:
            st.number_input("Documents per year", min_value=1_000, max_value=2_000_000,
                            step=1_000, key="volume",
                            help="60,600 is an assumed annual supplier-document volume.")
        with b:
            st.number_input("Cost per hour (€)", min_value=5.0, max_value=250.0,
                            step=1.0, key="hourly_cost",
                            help="Employer labor-cost estimate; not actual Isarwerk payroll data.")
        st.radio("Choose a scenario", list(SCENARIOS), horizontal=True,
                 on_change=choose_preset, key="scenario")
        st.slider("Less manual work (%)", min_value=0, max_value=95,
                  step=5, key="effort_pct",
                  help="50%, 60%, 70% are planning scenarios, not guaranteed results.")
        st.slider("Freed time converted to cash savings (%)", min_value=0, max_value=100,
                  step=5, key="cash_pct",
                  help="Savings that can actually be realized through avoided costs.")
        x, y = st.columns(2, gap="small")
        with x:
            st.button("Test 30% cash savings", on_click=stress_test,
                      help="Keep time savings fixed but reduce the share converted to cash.")
        with y:
            st.button("↺ Reset", on_click=reset_inputs)
        st.markdown('<div class="small-info">These are estimates. Actual results need to be checked with the company.</div>',
                    unsafe_allow_html=True)

    with st.expander("Change pricing and setup costs", expanded=False):
        x, y = st.columns(2, gap="small")
        with x:
            st.number_input("Platform (€ / month)", min_value=0.0, max_value=50_000.0,
                            step=50.0, format="%.2f", key="platform_month")
        with y:
            st.number_input("Fee per document (€)", min_value=0.0, max_value=10.0,
                            step=0.01, format="%.2f", key="usage_rate")
        st.number_input("One-time setup + consulting (€)", min_value=0.0,
                        max_value=500_000.0, step=500.0, format="%.2f", key="setup_cost")
        st.markdown('<div class="simple-price">Illustrative model: €300/month includes the platform, plus €0.32 for every document; one-time setup €12,100. Not published BLP pricing.</div>',
                    unsafe_allow_html=True)
        st.markdown(f"[Competitor pricing: Doxis/Klippa]({LINKS['klippa']}) · "
                    f"[Implementation reference: ISR]({LINKS['isr']})")

    with st.expander("Change manual handling times", expanded=False):
        st.caption("Estimated minutes per document type")
        cols = st.columns(2, gap="small")
        for idx, name in enumerate(("Direct materials", "Indirect purchases", "Freight", "Other expenses")):
            with cols[idx % 2]:
                st.number_input(f"{name} (min)", min_value=0.0, max_value=120.0,
                                step=1.0, key=f"mins_{idx}")
        st.number_input("Working hours per person / year", min_value=500,
                        max_value=2500, step=50, key="hours_per_fte")
        st.caption("Assumed document mix is scaled to the selected annual volume.")

# Compute only AFTER controls are created; data in every panel is from same live inputs.
r = compute(int(st.session_state.volume), float(st.session_state.hourly_cost),
            int(st.session_state.effort_pct), int(st.session_state.cash_pct),
            float(st.session_state.platform_month), float(st.session_state.usage_rate),
            float(st.session_state.setup_cost),
            minutes=tuple(float(st.session_state[f"mins_{i}"]) for i in range(len(MIX))),
            hours_per_fte=int(st.session_state.hours_per_fte))
roi = f"{r['roi']:,.0f}%" if r["roi"] is not None else "n/a"
payback = f"{r['payback_months']:.1f} mo" if r["payback_months"] is not None else "No payback"
case_status = "Positive year-one estimate" if r['year1_net'] > 0 else (
    "Year-one costs not yet recovered" if r['annual_net'] > 0 else "No cash payback at these inputs")
case_class = "" if r['year1_net'] >= 0 else "negative"

with right:
    st.markdown(f"""
    <div class="result-hero">
      <div class="result-kicker">02 / YOUR RESULT · {escape(st.session_state.scenario.upper())}</div>
      <div class="result-amount">{euros(r['year1_net'])}</div>
      <div class="result-label">Estimated net savings in Year 1</div>
      <div class="result-desc">Annual cash savings minus software costs and one-time setup.</div>
      <div class="result-flag {case_class}">● {escape(case_status)}</div>
    </div>
    <div class="kpi-grid">
      <div class="kpi"><div class="kpi-label">Return on investment · Year 1</div><div class="kpi-number">{escape(roi)}</div><div class="kpi-note">Net savings ÷ first-year costs</div></div>
      <div class="kpi"><div class="kpi-label">Payback time</div><div class="kpi-number">{escape(payback)}</div><div class="kpi-note">Simple setup payback at full run rate</div></div>
      <div class="kpi"><div class="kpi-label">Net savings per year · thereafter</div><div class="kpi-number">{euros(r['annual_net'])}</div><div class="kpi-note">After ongoing software costs</div></div>
    </div>
    <div class="revenue-panel">
      <div class="label">REVENUE PERSPECTIVE</div>
      <div class="big">{euros(REVENUE)} → {euros(REVENUE)}</div>
      <div class="desc">Revenue stays unchanged in this estimate. The value comes from lower costs and more available working time—not assumed new sales.</div>
    </div>
    <div class="revenue-panel">
      <div class="label">WHERE THE SAVINGS COME FROM</div>
      <div class="big">{euros(r['cash_eur'])} <span style="font-size:12px;color:#81939b;font-weight:700">annual cash savings</span></div>
      <div class="desc">Less {euros(r['annual_cost'])} per year for the platform and processing; one-time setup is {euros(st.session_state.setup_cost)}.</div>
    </div>
    """, unsafe_allow_html=True)

# Operations follows the top-level economic answer.
st.markdown('<div class="section-head"><div class="name">03 / Operational impact · before → after</div>'
            '<div class="hint">Live estimate at the same document volume</div></div>',
            unsafe_allow_html=True)
minutes_before = r['minutes']
minutes_after = minutes_before * (1 - st.session_state.effort_pct / 100)
st.markdown(f"""
<div class="compare-flow">
  <div class="compare-panel before">
    <div class="compare-tag">BEFORE · MANUAL WORK</div>
    <div class="compare-big">{number(r['before_hours'])} <small>hours / year</small></div>
    <div class="compare-primary">Work done manually today (estimated)</div>
    <div class="compare-row"><span>Minutes per document</span><b>{minutes_before:.1f}</b></div>
    <div class="compare-row"><span>Workload equivalent</span><b>{r['before_fte']:.2f} FTE</b></div>
  </div>
  <div class="compare-arrow"><div class="arrow-circle">→</div>
    <div class="arrow-pct">−{st.session_state.effort_pct}%</div>
    <div class="arrow-copy">less manual work</div></div>
  <div class="compare-panel after">
    <div class="compare-tag">AFTER · MODELED WORK</div>
    <div class="compare-big">{number(r['after_hours'])} <small>hours / year</small></div>
    <div class="compare-primary">Manual work left for people to handle</div>
    <div class="compare-row"><span>Minutes per document</span><b>{minutes_after:.1f}</b></div>
    <div class="compare-row"><span>Workload equivalent</span><b>{r['after_fte']:.2f} FTE</b></div>
  </div>
</div>
<div class="impact-strip">
  <strong>{number(r['freed_hours'])} hours · {r['freed_fte']:.2f} FTE of time potentially freed</strong>
  <span>Available capacity, not automatic staff reduction</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-head"><div class="name">04 / Where automation could help</div>'
            '<div class="hint">Only supplier documents are counted in these savings</div></div>',
            unsafe_allow_html=True)
st.markdown("""
<div class="case-grid">
  <div class="workload-card"><div class="eyebrow">IN THIS ESTIMATE</div><div class="proof-title">Finance</div><div class="proof-desc">Supplier invoices, purchase-order checks, approvals and exceptions.</div></div>
  <div class="workload-card"><div class="eyebrow" style="color:#81939c">POSSIBLE NEXT STEP</div><div class="proof-title">Procurement</div><div class="proof-desc">Order confirmations, prices and quantity checks.</div></div>
  <div class="workload-card"><div class="eyebrow" style="color:#81939c">POSSIBLE NEXT STEP</div><div class="proof-title">Logistics</div><div class="proof-desc">Delivery notes, goods receipt and ERP updates.</div></div>
  <div class="workload-card"><div class="eyebrow" style="color:#81939c">POSSIBLE NEXT STEP</div><div class="proof-title">Sales</div><div class="proof-desc">Customer orders, data entry and order exceptions.</div></div>
</div>
""", unsafe_allow_html=True)
proof_a, proof_b = st.columns(2, gap="medium")
with proof_a:
    st.markdown(f"""<div class="proof-card"><div><div class="proof-number">1.5 FTE</div><div class="proof-unit">Evatec · after deployment</div></div>
    <div><div class="proof-title">Document handling with a smaller AP workload</div>
    <div class="proof-desc">BLP's customer story describes 57k annual documents of several types, not just invoices.</div>
    <a class="proof-source" href="{LINKS['evatec']}" target="_blank">Read customer story ↗</a></div></div>""", unsafe_allow_html=True)
with proof_b:
    st.markdown(f"""<div class="proof-card"><div><div class="proof-number">30–40%</div><div class="proof-unit">Migros · reduced resource needs</div></div>
    <div><div class="proof-title">Simpler workflows and lower workload</div>
    <div class="proof-desc">A reported customer result, not the manual-work reduction assumed for Isarwerk.</div>
    <a class="proof-source" href="{LINKS['migros']}" target="_blank">Read customer story ↗</a></div></div>""", unsafe_allow_html=True)

# Keep detailed math available, not in the presentation path.
with st.expander("Cost breakdown and sources", expanded=False):
    st.markdown(f"""
    | Item | Annual cost |
    |:--|--:|
    | Platform (€{st.session_state.platform_month:,.0f}/month) | {euros(r['annual_platform'], False)} |
    | {int(st.session_state.volume):,} documents × €{st.session_state.usage_rate:.2f} | {euros(r['annual_usage'], False)} |
    | **Annual software cost** | **{euros(r['annual_cost'], False)}** |
    | **One-time setup / consulting** | **{euros(st.session_state.setup_cost, False)}** |
    | **First-year cost** | **{euros(r['year1_cost'], False)}** |
    """)
    st.markdown(f"**Public references:** [Doxis/Klippa competitor pricing]({LINKS['klippa']}) · [ISR consulting/implementation]({LINKS['isr']}) · [BLP Evatec]({LINKS['evatec']}) · [BLP Migros]({LINKS['migros']})")
    st.caption("Pricing, document mix, 50–70% effort reduction and 40–60% cash realization are low-confidence planning inputs. This is not a quote or a customer forecast.")
    rows = [{"Type": label, "Est. yearly volume": round(n * st.session_state.volume / BASE_VOLUME),
             "Manual minutes / document": st.session_state[f"mins_{i}"]}
            for i,(label,n,_) in enumerate(MIX)]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# Keep the sources above the forecast so the forecast is the LAST element.
st.markdown('<div class="footnote">Illustrative example for a fictional manufacturer. Savings depend on the share of released time that can actually reduce costs. Volume and revenue are separate inputs; efficiency does not automatically create new sales.</div>', unsafe_allow_html=True)

# ASIDE at the very bottom. Closed by default, not competing with the four-minute demo.
st.markdown('<div class="section-head"><div class="name">Extra · Five-year outlook <span style="font-size:11px;color:#81919b;font-weight:650">(prototype)</span></div>'
            '<div class="hint">Optional · explore after the main demo</div></div>', unsafe_allow_html=True)
with st.expander("Open the 5-year revenue and savings calculator", expanded=False):
    st.markdown('<div class="explain-card">Explore how annual revenue might grow alongside workflow savings. The revenue forecast is separate from the savings model above.</div>', unsafe_allow_html=True)
    a, b = st.columns(2, gap="medium")
    with a:
        st.slider("Years", min_value=1, max_value=5, key="years", step=1)
    with b:
        st.slider("Revenue growth per year (%)", min_value=-5.0, max_value=15.0,
                  key="growth", step=0.5, format="%.1f%%")
    st.checkbox("Try an additional revenue scenario (hypothetical)", key="extra_sales")
    if st.session_state.extra_sales:
        a, b = st.columns(2, gap="medium")
        with a:
            st.slider("Extra revenue from Year 2 (%)", min_value=0.0, max_value=3.0,
                      step=0.05, key="uplift", format="%.2f%%")
        with b:
            st.slider("Profit margin on extra sales (%)", min_value=0.0, max_value=60.0,
                      step=5.0, key="margin", format="%.0f%%")
    projection = forecast(
        years=int(st.session_state.years),
        growth_pct=float(st.session_state.growth),
        current_revenue=REVENUE,
        annual_net=float(r['annual_net']),
        setup=float(st.session_state.setup_cost),
        extra_sales=bool(st.session_state.extra_sales),
        uplift_pct=float(st.session_state.uplift),
        profit_margin_pct=float(st.session_state.margin),
    )
    last = projection[-1]
    c1, c2, c3 = st.columns(3, gap="medium")
    c1.metric(f"Revenue in Year {st.session_state.years}", euros(last['with_extra']))
    c2.metric("Total net process savings", euros(last['total_process_net']))
    c3.metric("Extra yearly profit (hypothetical)", euros(last['extra_contribution']))
    chart = pd.DataFrame({
        "Year": [f"Year {x['year']}" for x in projection],
        "Revenue (€m)": [x['revenue']/1e6 for x in projection],
        **({"Optional revenue (€m)": [x['with_extra']/1e6 for x in projection]}
           if st.session_state.extra_sales else {}),
    }).set_index("Year")
    st.line_chart(chart, height=275)
    show_rows = [{"Year": f"Y{x['year']}", "Projected revenue": euros(x['revenue']),
                  "Net process savings": euros(x['process_net']),
                  **({"Optional additional sales": euros(x['extra_revenue'])} if st.session_state.extra_sales else {})}
                 for x in projection]
    st.dataframe(pd.DataFrame(show_rows), use_container_width=True, hide_index=True)
    st.caption("Revenue growth and optional sales uplift are scenarios, not results proven by BLP. The core ROI never includes extra sales. Workflow volumes, fees and labour costs are held constant across the forecast, with setup charged in Year 1 only.")
