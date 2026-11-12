"""Isarwerk CFO value calculator — Streamlit Community Cloud-ready demo.

This is a fictional, screening-level decision support prototype; not a BLP quote.
The isolated financial calculations are in value_model.py.
"""
import csv
import io
from html import escape

import plotly.graph_objects as go
import streamlit as st

from value_model import COMPANY, INVOICE_CATEGORIES, SCENARIOS, ValueInputs, calculate

st.set_page_config(
    page_title="Isarwerk · CFO Value Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Light consulting-style palette: navy + teal with very restrained highlight color.
NAVY = "#142840"
TEAL = "#118b80"
MUTED = "#536477"
AMBER = "#d99b5a"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
html, body, [class*='css'], .stApp {font-family:'DM Sans',sans-serif;}
.stApp {background: #f7f9fc; color: #142840;}
.block-container {max-width: 1300px; padding-top: 2rem; padding-bottom: 4rem;}
#MainMenu, footer {visibility: hidden;}
header[data-testid='stHeader'] {background: transparent;}
:root {--ink: #142840; --muted: #657487; --line:#e1e9ee; --teal:#118b80;}
.hero {
 background: linear-gradient(108deg, #142840 0%, #1b3b50 73%, #1b675f 125%);
 border-radius: 22px; padding: 34px 38px 29px; color: white;
 box-shadow: 0 10px 32px rgba(18, 46, 70, .12);
 margin-bottom: 22px; position:relative; overflow:hidden;
}
.hero:after {content:''; position:absolute; width:300px; height:300px; border:1px solid #ffffff20;
 border-radius:50%; right:-140px; top:-160px; box-shadow:0 0 0 55px #ffffff05,0 0 0 110px #ffffff04;pointer-events:none;}
.hero-kicker {font-size:11px;font-weight:700;letter-spacing:2px;color:#72dfca; text-transform:uppercase;margin-bottom:12px;}
.hero h1 {font-family:Manrope,sans-serif;font-size:clamp(28px,3.3vw,43px);font-weight:800;line-height:1.16;letter-spacing:-1.5px;color:white;margin:0 0 10px;max-width:850px;}
.hero p {color:#d5e5ed;font-size:15px;line-height:1.6; margin:0 0 17px; max-width:810px;}
.hero-meta {display:flex;flex-wrap:wrap;gap:8px;}
.hero-meta span {border:1px solid #ffffff32; background:#ffffff13;padding:6px 11px;border-radius:99px;font-size:12px;color:#edf8fb;}
.eyebrow {font-size:12px;font-weight:800;color:#138b80;letter-spacing:1.5px;text-transform:uppercase;margin:8px 0 7px;}
.section-heading {font-family:Manrope,sans-serif;font-size:23px;font-weight:800;line-height:1.3;color:#152942;margin:3px 0 8px;}
.section-sub {color:#667589;font-size:13px;margin:0 0 14px;}
[data-testid='stVerticalBlockBorderWrapper'] {background:white; border:1px solid #e2ebf0 !important;border-radius:16px !important;box-shadow:0 4px 22px rgba(21,39,58,.035);}
div[data-testid='stMetric'] {background:#fff; padding:20px 17px 16px; border:1px solid #dfe9ee; border-radius:15px; box-shadow:0 4px 18px rgba(22,49,69,.035); min-height:133px;}
[data-testid='stMetricLabel'] {font-weight:650;color:#546678;font-size:13px;}
[data-testid='stMetricValue'] {font-family:Manrope,sans-serif;font-size:clamp(23px,2.25vw,32px);font-weight:800;color:#13283e;letter-spacing:-1px;}
[data-testid='stMetricDelta'] {font-size:12px;}
div[data-testid='stPlotlyChart'] {border-radius:10px;}
div.stButton>button, div.stDownloadButton>button {background:#142840;color:#fff;border-radius:9px;border:none;font-weight:700;}
div.stButton>button:hover, div.stDownloadButton>button:hover {background:#1e5c5c;color:white;border:none;}
input {font-weight:650 !important;}
.verdict {border-left:4px solid #118b80;background:#eaf6f3;border-radius:0 12px 12px 0; padding:14px 18px;color:#1d4a48;font-size:14px;line-height:1.6;margin:9px 0 16px;}
.verdict-warn {border-left-color:#e5a66a;background:#fff4e8;color:#644220;}
.proof-card {background:#fff;border:1px solid #e0e8ee;border-radius:16px;padding:19px 21px 16px;min-height:195px;}
.proof-tag {font-size:11px;letter-spacing:1px;font-weight:800;color:#198c81;text-transform:uppercase;}
.proof-title {font-family:Manrope,sans-serif;font-size:17px;font-weight:800;color:#142840;margin:7px 0;}
.proof-large {font-family:Manrope,sans-serif;font-size:24px;font-weight:800;color:#152f43;margin:4px 0;}
.proof-body {font-size:13px;color:#53687a;line-height:1.6;margin-bottom:11px;}
.proof-card a {font-size:12px;font-weight:800;color:#0f7e73;text-decoration:none;}
.step {display:flex;align-items:flex-start;gap:13px;padding:13px 7px;}
.step-icon {min-width:39px;height:39px;border-radius:11px;background:#e5f3f2;display:flex;align-items:center;justify-content:center;font-size:20px;}
.step-name {font-size:13px;font-weight:800;color:#142840;margin-top:2px;}
.step-desc {font-size:12px;color:#657589;margin-top:4px;line-height:1.5;}
.small-note {font-size:12px;color:#738195;line-height:1.5;}
.cta {background:#eff5f8;border:1px solid #dbe8ed;border-radius:14px;padding:19px 22px;margin-top:8px;}
.cta strong {color:#132f45;}
.hr-light {border:none;border-top:1px solid #dfebef;margin:25px 0 18px;}
a {color:#168a80;}
@media (max-width: 700px) {.hero{padding:25px 22px}.hero h1{font-size:29px}.block-container{padding-top:1rem}}
</style>
""", unsafe_allow_html=True)


def money(value: float, short: bool = False) -> str:
    if short:
        if abs(value) >= 1_000_000:
            return f"€{value/1_000_000:,.2f}m"
        if abs(value) >= 1_000:
            return f"€{value/1_000:,.1f}k"
    return "€" + f"{value:,.0f}"


def days_or_months(months):
    return "Not reached" if months is None else f"{months:.1f} mo"


def section(kicker, title, subtitle=""):
    st.markdown(f'<div class="eyebrow">{escape(kicker)}</div><div class="section-heading">{escape(title)}</div>'
                + (f'<div class="section-sub">{escape(subtitle)}</div>' if subtitle else ""),
                unsafe_allow_html=True)


st.markdown(f"""
<div class="hero">
 <div class="hero-kicker">BLP DIGITAL / VALUE ENGINEERING · CFO DECISION DEMO</div>
 <h1>What could AP automation be worth to Isarwerk?</h1>
 <p>A two-minute investment screen: understand the workload, test cash value and payback, then decide what deserves validation.</p>
 <div class="hero-meta">
  <span>Isarwerk Präzision GmbH · fictional</span>
  <span>€320m annual revenue</span>
  <span>1,100 employees</span>
  <span>3 manufacturing plants</span>
  <span>SAP S/4HANA</span>
 </div>
</div>
""", unsafe_allow_html=True)

section("01 / Quick assessment", "Start with your AP reality", "Change two figures, or choose a scenario. The business case refreshes instantly.")

with st.container(border=True):
    c1, c2, c3 = st.columns([1.05, 1.05, 1.5], gap="large")
    with c1:
        invoices = st.number_input("Supplier invoices per year", min_value=1_000,
                                   max_value=1_500_000, value=60_600, step=1_000,
                                   help="Initial estimate 60,600 from the supplied Excel model; not company-observed data.")
    with c2:
        hourly_cost = st.number_input("Employer cost per AP hour (€)", min_value=5.0,
                                      max_value=250.0, value=45.0, step=1.0,
                                      help="Germany 2025 national employer labour-cost benchmark (Destatis).")
    with c3:
        scenario = st.radio("Expected improvement", list(SCENARIOS),
                            index=1, horizontal=True,
                            help="Scenarios change time saved and share converted to cash; they do not change company size or staffing.")
    with st.expander("Fine-tune the case · assumptions, software price and invoice mix", expanded=False):
        a, b, c, d = st.columns(4, gap="small")
        with a:
            ap_fte = st.number_input("AP team · FTE", min_value=0.5, max_value=500.0, value=7.0, step=0.5)
        with b:
            workhours = st.number_input("Productive hrs / FTE / yr", min_value=500, max_value=2200,
                                        value=1540, step=20)
        with c:
            unit_price = st.number_input("BLP price assumption · €/invoice", min_value=0.0,
                                         max_value=20.0, value=0.38, step=0.01, format="%.2f",
                                         help="Placeholder inferred from a competitor proxy, NOT an official BLP price.")
        with d:
            implementation = st.number_input("One-off rollout (€)", min_value=0, max_value=5_000_000,
                                             value=50_000, step=5_000,
                                             help="Modelled using a public peer standard implementation fee and an unverified integration uplift.")
        st.markdown("**Manual time by invoice type** · working minutes per invoice, not total calendar lead time")
        mix_cols = st.columns(4, gap="small")
        custom_mins = []
        for i, ((name, _, base_minutes), column) in enumerate(zip(INVOICE_CATEGORIES, mix_cols)):
            with column:
                custom_mins.append(st.number_input(name, min_value=0.0, max_value=240.0,
                                                    value=float(base_minutes), step=1.0, key=f"catmins_{i}"))
        reduction_default, monetised_default = SCENARIOS[scenario]
        st.markdown("**Scenario economics** · what we believe will change")
        s1, s2 = st.columns(2, gap="large")
        with s1:
            reduction_pct = st.slider("Reduction in manual AP touch time", min_value=0, max_value=95,
                                      value=int(reduction_default * 100), key=f"red_{scenario}",
                                      help="Assumed efficiency improvement, not BLP's certified zero-touch rate.")
        with s2:
            monetised_pct = st.slider("Freed time translated into real cash benefit", min_value=0,
                                      max_value=100, value=int(monetised_default * 100),
                                      key=f"cash_{scenario}",
                                      help="Avoided hiring, overtime or equivalent budgeted work; the rest remains capacity.")
        st.caption("All editable performance assumptions are low-confidence until verified with an AP time study and BLP pilot.")

# Defaults also exist when the accordion stays collapsed: Streamlit executes its contents.
inputs = ValueInputs(
    invoices_per_year=int(invoices), ap_team_fte=ap_fte, annual_hours_per_fte=workhours,
    employer_hourly_cost_eur=hourly_cost,
    software_fee_per_invoice_eur=unit_price,
    implementation_cost_eur=implementation,
    minutes_by_category=tuple(custom_mins),
)
result = calculate(inputs, reduction_pct / 100, monetised_pct / 100)

st.caption("Illustrative estimate · The €0.38/invoice software assumption is NOT a BLP quotation; reduction and cash conversion require validation.")

section("02 / The answer", "The business case, in four numbers",
        "Annual net value is after indicative software fees; year one also subtracts one-off rollout costs.")

metrics = st.columns(4, gap="small")
with metrics[0]:
    st.metric("Annual net cash value", money(result["annual_net_eur"], short=True),
              help="Realizable annual AP benefit less hypothetical recurring BLP software spend.")
with metrics[1]:
    st.metric("Year-one net cash value", money(result["year_one_net_eur"], short=True),
              help="Annual net value less the one-off implementation estimate.")
with metrics[2]:
    st.metric("Simple rollout payback", days_or_months(result["payback_months"]),
              help="One-time implementation cost divided by monthly net recurring benefit. Assumes a full run-rate from day one.")
with metrics[3]:
    st.metric("AP capacity released", f"{result['fte_released']:.2f} FTE",
              help="Workload equivalent of the hours freed. This does not assume layoffs or salary elimination.")

if result["annual_net_eur"] > 0 and result["year_one_net_eur"] > 0:
    headline = "A first-pass case worth validating"
    detail = (f"Under the <strong>{escape(scenario.lower())}</strong> scenario, {money(result['cash_benefit_eur'])} "
              f"could translate into annual cash-relevant benefits; after {money(result['annual_software_eur'])} in assumed "
              f"software fees, recurring net value is <strong>{money(result['annual_net_eur'])}</strong>. "
              "This is a screening estimate, not a purchasing recommendation.")
    verdict_class = "verdict"
elif result["annual_net_eur"] > 0:
    headline = "Recurring value may be positive; year-one economics need work"
    detail = ("Estimated annual net benefit is positive, but the initial setup cost would leave a "
              "negative first-year return. Validate volume, rollout scope and realizable savings before proceeding.")
    verdict_class = "verdict verdict-warn"
else:
    headline = "No positive cash payback under these inputs"
    detail = ("The assumed cash benefits do not cover annual software spend. The available capacity "
              "may still be useful, but there is no positive cash business case without changing the inputs.")
    verdict_class = "verdict verdict-warn"
st.markdown(f'<div class="{verdict_class}"><strong>{headline}.</strong> {detail}</div>', unsafe_allow_html=True)

cchart, cexplain = st.columns([1.50, 1], gap="large")
with cchart:
    with st.container(border=True):
        st.markdown("**Where the annual value comes from**")
        y = [result["gross_capacity_eur"], -result["noncash_capacity_eur"],
             -result["annual_software_eur"], 0]
        fig = go.Figure(go.Waterfall(
            x=["Gross capacity", "Not cash-realisable", "Software fees", "Net annual cash"],
            y=y,
            measure=["relative", "relative", "relative", "total"],
            text=[money(v, short=True) if i == 0 else
                  ("−" + money(abs(v), short=True) if i in (1, 2) else money(result["annual_net_eur"], short=True))
                  for i, v in enumerate(y)],
            textposition="outside",
            connector={"line": {"color": "#c8d6df", "width": 1}},
            increasing={"marker": {"color": "#31a69a"}},
            decreasing={"marker": {"color": "#dea373"}},
            totals={"marker": {"color": "#18374d"}},
            hovertemplate="%{x}<br>%{y:,.0f} €<extra></extra>",
        ))
        fig.update_layout(
            height=320, margin=dict(l=18, r=8, t=30, b=10),
            showlegend=False, paper_bgcolor="white", plot_bgcolor="white",
            font={"family": "DM Sans, sans-serif", "color": NAVY, "size": 11},
            xaxis={"fixedrange": True, "tickfont": {"size": 11}},
            yaxis={"tickprefix": "€", "tickformat": "~s", "gridcolor": "#eaf0f4",
                   "zeroline": False, "fixedrange": True},
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.caption("Capacity value is NOT the same as cash savings. Only the selected realizable share enters cash ROI.")
with cexplain:
    with st.container(border=True):
        st.markdown("**What it means operationally**")
        st.metric("Manual AP hours today", f"{result['baseline_manual_hours']:,.0f} hrs")
        st.metric("Time freed per year", f"{result['hours_released']:,.0f} hrs")
        st.metric("Annual software budget · estimate", money(result["annual_software_eur"]))
        st.markdown(f'<div class="small-note">Using <strong>{reduction_pct}% less manual touch time</strong> '
                    f'and <strong>{monetised_pct}% cash realization</strong>. Remaining hours: '
                    f'{result["remaining_manual_hours"]:,.0f} / year.</div>', unsafe_allow_html=True)

if result["team_utilisation"] is not None and result["team_utilisation"] > 1.05:
    st.warning(f"Current estimated AP workload ({result['baseline_manual_fte']:.1f} FTE equivalent) "
               f"exceeds the {inputs.ap_team_fte:g} FTE team entered. Check scope, overtime and touch-time assumptions.")

section("03 / What actually changes", "Less manual chasing. More controlled execution.",
        "An executive-level view of the workflow BLP describes for accounts payable.")
step_cols = st.columns(3, gap="small")
steps = [
    ("📨", "1. Supplier invoices arrive", "PO and non-PO invoices arrive from different suppliers and formats."),
    ("🔎", "2. BLP handles the workload", "Matches invoices, checks discrepancies and moves routine cases forward."),
    ("✅", "3. Your team stays in control", "People approve genuine exceptions; posting and the decision trail stay visible in ERP."),
]
for col, (ico, title, desc) in zip(step_cols, steps):
    with col:
        with st.container(border=True):
            st.markdown(f'<div class="step"><div class="step-icon">{ico}</div>'
                        f'<div><div class="step-name">{escape(title)}</div>'
                        f'<div class="step-desc">{escape(desc)}</div></div></div>',
                        unsafe_allow_html=True)

section("04 / Evidence, not a forecast", "BLP has addressed this kind of AP problem before",
        "Real BLP customer examples provide plausibility, not transferable ROI assumptions for Isarwerk.")
card_a, card_b = st.columns(2, gap="medium")
with card_a:
    st.markdown("""
    <div class="proof-card">
      <div class="proof-tag">Manufacturing · Evatec · SAP Cloud ERP</div>
      <div class="proof-title">Cleared a 1,000+ invoice backlog after ERP migration</div>
      <div class="proof-large">1.5 AP FTE</div>
      <div class="proof-body">BLP reports Evatec now processes AP with 1.5 FTEs and handles around 57,000 <em>mixed documents</em> a year (not 57,000 invoices). The backlog cleared shortly after go-live.</div>
      <a href="https://blp.digital/resources/our-customers/evatec" target="_blank">Read the Evatec customer story ↗</a>
    </div>""", unsafe_allow_html=True)
with card_b:
    st.markdown("""
    <div class="proof-card">
      <div class="proof-tag">Retail · Migros · SAP S/4HANA</div>
      <div class="proof-title">Unified 12 previously separate AP processes</div>
      <div class="proof-large">30–40% less resource need</div>
      <div class="proof-body">BLP reports lower AP resource needs following Migros’s consolidated AP transformation, with real-time transparency and auditability. This is a project result, not Isarwerk’s savings rate.</div>
      <a href="https://blp.digital/resources/our-customers/migros" target="_blank">Read the Migros customer story ↗</a>
    </div>""", unsafe_allow_html=True)

section("05 / The actual CFO decision", "What must be true before we invest?",
        "Turn the estimate into a credible investment case using company facts and a BLP proof of value.")
st.markdown("""
<div class="cta">
 <strong>Recommended decision:</strong> Sponsor a short validation, not a purchase approval.
 <div style="color:#5b7080;font-size:13px;line-height:1.65;margin-top:7px;">
  ① AP lead: export 12 months of invoices and sample processing time &nbsp; · &nbsp;
  ② Finance: confirm labour cost and which freed hours genuinely save cash &nbsp; · &nbsp;
  ③ BLP: test handling performance, scope and provide an actual price and implementation quote.
 </div>
 <div style="color:#607688;font-size:12px;margin-top:8px;">Suggested validation effort: 1–2 weeks to gather initial data and interview owners; pilot timing agreed with BLP. No implementation schedule is promised.</div>
</div>
""", unsafe_allow_html=True)

with st.expander("Open the evidence file · assumptions, confidence and calculation", expanded=False):
    st.markdown("**Assumption quality**")
    st.markdown("""
| Input | Starting point | Confidence | Why |
|---|---:|---|---|
| Company revenue and size | €320m · 1,100 people | Fictional | Context only, not part of invoice volume calculation |
| Annual invoice count / mix | 60,600 across four categories | Low | Estimates from the supplied Excel workbook; not real company records |
| Manual minutes / invoice | 8–15 min depending on type | Low | Working estimates, not a measured AP time study |
| Employer labour cost | €45 / hour | Medium | Destatis 2025 German cross-sector average, not AP payroll |
| Touch-time reduction | 50% / 65% / 75% | Low | Hypothetical scenario, not measured BLP performance |
| Cash realization | 40% / 60% / 80% | Low | Must be approved by Finance before calling freed time a saving |
| BLP software budget | €0.38 per invoice | Low | An unquoted placeholder, informed by competitor pricing |
| One-off implementation | €50,000 | Low | Public peer €19,500 standard setup + €30,500 estimated uplift |
""")
    st.markdown("**Invoice mix used in this calculation**")
    st.dataframe([
        {"Invoice type": item["name"], "Invoices / year": round(item["invoices"]),
         "Manual minutes / invoice": item["minutes"], "Manual hours / year": round(item["annual_hours"])}
        for item in result["category_mix"]
    ], use_container_width=True, hide_index=True)
    st.markdown("**The five-line calculation**")
    st.markdown("""
1. **Baseline workload** = sum(invoice count × manual minutes) ÷ 60.
2. **Capacity freed** = baseline hours × assumed reduction in manual touch time.
3. **Cash-relevant benefit** = hours freed × employer hourly cost × cash realization share.
4. **Net recurring value** = cash-relevant benefit − annual estimated software fee.
5. **Year-one value** = net recurring value − one-off implementation; **simple payback** = implementation ÷ monthly net recurring value (only when positive).
""")
    st.info("Simple payback assumes a full annual operating run-rate from day one and excludes tax, discounting, phased deployment, opportunity cost and change-management effort. A CFO-approved case should add those items where material.")
    st.markdown("**Public references**")
    st.markdown("""
- [BLP Finance solution — matching, exception handling, posting and approvals](https://blp.digital/solutions/finance)
- [BLP Evatec manufacturing customer story](https://blp.digital/resources/our-customers/evatec)
- [BLP Migros transformation customer story](https://blp.digital/resources/our-customers/migros)
- [BLP official pricing FAQ — no fixed public list prices](https://blp.digital/resources/faqs)
- [Klippa public invoice-processing price tiers](https://www.klippa.com/en/invoice-processing/prices/), competitor used only as a rough market anchor; at 60,600 invoices, its published Custom tier requires a quote
- [ISR published one-off standard AP implementation package (€19,500)](https://isr.de/en/technologies/isr/accounts-payable-flow/offer/)
- [Destatis German 2025 employer labour cost (€45/hour)](https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/04/PD26_148_624.html)
""")
    st.caption("The workbook contains inconsistent narrative wording in its competitor markup explanation. To avoid implying false precision, this demo treats €0.38/invoice as an editable low-confidence placeholder pending a BLP quote.")

with st.expander("Compare all three scenarios on the same company baseline", expanded=False):
    rows = []
    for label, (r, m) in SCENARIOS.items():
        temp = calculate(inputs, r, m)
        rows.append({
            "Scenario": label,
            "Manual time saved": f"{r:.0%}",
            "Cash realization": f"{m:.0%}",
            "Annual net value": money(temp["annual_net_eur"]),
            "Year-one net": money(temp["year_one_net_eur"]),
            "Payback": days_or_months(temp["payback_months"]),
            "Capacity freed": f"{temp['fte_released']:.2f} FTE",
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.caption("This comparison uses the three original Excel scenario presets. If you manually changed the active scenario levers, the main result may differ from its preset row.")

csv_io = io.StringIO()
writer = csv.writer(csv_io)
writer.writerow(["Isarwerk CFO estimate", "Illustrative - not a BLP quote"])
writer.writerow(["Scenario", scenario])
writer.writerow(["Annual invoices", inputs.invoices_per_year])
writer.writerow(["Annual AP FTE", inputs.ap_team_fte])
writer.writerow(["Employer cost/hour EUR", inputs.employer_hourly_cost_eur])
writer.writerow(["Time reduction %", reduction_pct])
writer.writerow(["Cash realization %", monetised_pct])
writer.writerow(["Manual hours/year", round(result["baseline_manual_hours"], 2)])
writer.writerow(["Hours freed/year", round(result["hours_released"], 2)])
writer.writerow(["Gross capacity EUR/year", round(result["gross_capacity_eur"], 2)])
writer.writerow(["Cash benefit EUR/year", round(result["cash_benefit_eur"], 2)])
writer.writerow(["Software fee assumption EUR/invoice", inputs.software_fee_per_invoice_eur])
writer.writerow(["Annual software cost EUR", round(result["annual_software_eur"], 2)])
writer.writerow(["One-time implementation EUR", inputs.implementation_cost_eur])
writer.writerow(["Net annual cash value EUR", round(result["annual_net_eur"], 2)])
writer.writerow(["Net year-one cash value EUR", round(result["year_one_net_eur"], 2)])
writer.writerow(["Payback months", round(result["payback_months"], 2) if result["payback_months"] is not None else "Not reached"])
st.download_button("⬇ Download this estimate · CSV", data=csv_io.getvalue().encode("utf-8-sig"),
                   file_name="Isarwerk_CFO_AP_business_case.csv", mime="text/csv")
st.markdown("<div class='small-note' style='margin-top:16px;'>VALUE ENGINEERING PROTOTYPE · ISARWERK PRÄZISION GMBH IS FICTIONAL · PUBLIC CUSTOMER RESULTS ARE NOT FORECASTS · PRICING IS NOT A BLP QUOTATION</div>", unsafe_allow_html=True)
