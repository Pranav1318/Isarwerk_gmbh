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
