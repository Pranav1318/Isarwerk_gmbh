# Isarwerk | CFO AP Value Calculator

**Working Streamlit prototype** using the fictional Isarwerk Präzision GmbH scenario and the financial logic in `Isarwerk_AP_Value_Model_Final_Simplified(2).xlsx`.

## Two-minute CFO demo

1. Start on the hero section: fictional manufacturer (revenue €320m, employees 1,100, 3 plants, SAP S/4HANA).
2. Change **annual supplier invoices** and **employer cost per hour** or select Conservative / Base / Optimistic.
3. Read **annual net cash value**, **year-one value**, **simple payback** and **capacity freed**. The bridge distinguishes capacity from cash.
4. Scroll to the three-step process explanation and **Evatec / Migros** real BLP customer evidence.
5. Finish with the recommended **short validation**, not an instant purchase approval.

## Deploy publicly with Streamlit Community Cloud

1. Extract the ZIP and create a new **public GitHub repository** (e.g. `isarwerk-cfo-value-demo`).
2. Upload **`app.py`, `value_model.py`, `requirements.txt`, and the `.streamlit/config.toml` folder** to the repository root. You do not need to upload the original Excel or PowerPoint.
3. Visit <https://share.streamlit.io/> and choose **Create app** / **Deploy an app**.
4. Select the repository, its main branch, and set **Main file path** to `app.py`.
5. Deploy. Copy the new `https://...streamlit.app/` public link into your presentation's live demo slide. Test in an incognito window to ensure outsiders can open it.

**Important**: An app that redirects an unauthenticated visitor to `share.streamlit.io/-/auth/app` is not public. Verify Community Cloud app visibility and app-sharing settings before the interview.

### Run locally (optional)

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Workbook alignment (Base scenario)

- Annual incoming invoices: 60,600 (24,600 direct / 16,000 indirect / 12,000 freight / 8,000 non-PO)
- Manual minutes: 10 / 11 / 8 / 15
- Baseline manual hours: 10,633.33, workload equivalent ≈ 6.90 FTE using 1,540 productive hrs/FTE
- Time reduction: 65%; monetized portion of released time: 60%; employer cost: €45/hour
- Gross capacity value: €311,025/year; cash-relevant benefit: €186,615/year
- Estimated software spend: €0.38 x 60,600 = €23,028/year (NOT a BLP quote)
- Net recurring value: €163,587/year
- Assumed one-time rollout: €50,000
- Year-one value: €113,587; simple payback: 3.67 months; capacity: 4.49 FTE equivalent

**Scenarios are hypotheses, not BLP claims.** The software price is a low-confidence placeholder and BLP publicly states its prices are customized. The original workbook has inconsistent wording about its Klippa uplift (20% input vs a “×1.6” text explanation). The app retains the workbook's explicit €0.38 default and labels it as unquoted.

## Source transparency

Real customer evidence (not assumptions about Isarwerk):
- Evatec: <https://blp.digital/resources/our-customers/evatec> — 57,000 **mixed documents**/year, not just invoices; 1.5 FTE to handle AP; backlog cleared after go-live.
- Migros: <https://blp.digital/resources/our-customers/migros> — 12 AP workflows unified, 30–40% reduced resources reported in the transformation context.
- BLP Finance: <https://blp.digital/solutions/finance>
- BLP pricing FAQ: <https://blp.digital/resources/faqs>

Indicative model inputs (revalidation needed):
- Labour €45/hour, German average, 2025: <https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/04/PD26_148_624.html>
- Klippa pricing: <https://www.klippa.com/en/invoice-processing/prices/> (at 60,600 invoices the higher-volume tier is custom/quote-only)
- ISR standard implementation list fee: <https://isr.de/en/technologies/isr/accounts-payable-flow/offer/> (€19,500, uplift to €50,000 is an assumption)

## Limitations

This prototype does not include phased deployment, depreciation, tax, discounting, AP process variation by entity, vendor validation, actual savings attribution, or a vendor contract. Payback is calculated with a full steady-state run-rate. Freed capacity is **not** the same as cash savings. Approval would require a real invoice export, manual-time measurements, realized personnel-cost plan, BLP pilot outcomes and quote.
