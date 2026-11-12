"""Transparent, dependency-free financial model for the Isarwerk CFO demo.

Defaults are transcribed from the user-supplied Isarwerk_AP_Value_Model_Final_Simplified workbook.
Illustrative customer case only; no BLP-specific outcome or quote is represented here.
"""
from dataclasses import dataclass
from typing import Optional


COMPANY = {
    "name": "Isarwerk Präzision GmbH",
    "sector": "Precision components manufacturing",
    "annual_revenue_eur": 320_000_000,
    "employees": 1_100,
    "plants": "3 plants · Bavaria, Saxony and Czechia",
    "erp": "SAP S/4HANA",
    "fictional": True,
}

# Fixed category counts sum to 60,600; used only to allocate a changed volume.
INVOICE_CATEGORIES = (
    ("Direct materials · PO", 24_600, 10.0),
    ("Indirect spend · PO", 16_000, 11.0),
    ("Freight & logistics", 12_000, 8.0),
    ("Non-PO & other", 8_000, 15.0),
)
BASE_VOLUME = sum(cat[1] for cat in INVOICE_CATEGORIES)

# Each scenario changes only the effort reduction and cash realization fractions.
SCENARIOS = {
    "Conservative": (0.50, 0.40),
    "Base": (0.65, 0.60),
    "Optimistic": (0.75, 0.80),
}


@dataclass(frozen=True)
class ValueInputs:
    invoices_per_year: int = 60_600
    ap_team_fte: float = 7.0
    annual_hours_per_fte: float = 1_540.0
    employer_hourly_cost_eur: float = 45.0
    software_fee_per_invoice_eur: float = 0.38
    implementation_cost_eur: float = 50_000.0
    minutes_by_category: tuple[float, float, float, float] = (10.0, 11.0, 8.0, 15.0)


def calculate(inputs: ValueInputs, reduction_fraction: float, monetised_fraction: float) -> dict:
    """Return a screening estimate. Cash conversion and capacity are separate on purpose."""
    if inputs.invoices_per_year < 0:
        raise ValueError("Invoice count must be non-negative")
    if not 0 <= reduction_fraction <= 1 or not 0 <= monetised_fraction <= 1:
        raise ValueError("Fractions must be between 0 and 1")
    if inputs.annual_hours_per_fte <= 0:
        raise ValueError("Annual productive hours per FTE must be positive")
    if any(v < 0 for v in inputs.minutes_by_category):
        raise ValueError("Invoice minutes cannot be negative")

    mix = []
    for (label, base_count, _), minutes in zip(INVOICE_CATEGORIES, inputs.minutes_by_category):
        annual_count = inputs.invoices_per_year * base_count / BASE_VOLUME
        mix.append({"name": label, "invoices": annual_count, "minutes": minutes,
                    "annual_hours": annual_count * minutes / 60})

    manual_hours = sum(d["annual_hours"] for d in mix)
    saved_hours = manual_hours * reduction_fraction
    remaining_hours = manual_hours - saved_hours
    capacity_fte = saved_hours / inputs.annual_hours_per_fte
    baseline_fte = manual_hours / inputs.annual_hours_per_fte
    gross_capacity_eur = saved_hours * inputs.employer_hourly_cost_eur
    cash_benefit_eur = gross_capacity_eur * monetised_fraction
    noncash_capacity_eur = gross_capacity_eur - cash_benefit_eur
    annual_software_eur = inputs.invoices_per_year * inputs.software_fee_per_invoice_eur
    annual_net_eur = cash_benefit_eur - annual_software_eur
    year_one_net_eur = annual_net_eur - inputs.implementation_cost_eur
    total_year_one_costs_eur = annual_software_eur + inputs.implementation_cost_eur

    if annual_net_eur > 0:
        payback_months: Optional[float] = inputs.implementation_cost_eur / annual_net_eur * 12
    else:
        payback_months = None

    roi_year_one = (year_one_net_eur / total_year_one_costs_eur
                    if total_year_one_costs_eur > 0 else None)

    return {
        "category_mix": mix,
        "baseline_manual_hours": manual_hours,
        "baseline_manual_fte": baseline_fte,
        "remaining_manual_hours": remaining_hours,
        "hours_released": saved_hours,
        "fte_released": capacity_fte,
        "reduction_fraction": reduction_fraction,
        "monetised_fraction": monetised_fraction,
        "gross_capacity_eur": gross_capacity_eur,
        "noncash_capacity_eur": noncash_capacity_eur,
        "cash_benefit_eur": cash_benefit_eur,
        "annual_software_eur": annual_software_eur,
        "annual_net_eur": annual_net_eur,
        "year_one_net_eur": year_one_net_eur,
        "payback_months": payback_months,
        "year_one_roi": roi_year_one,
        "team_utilisation": (baseline_fte / inputs.ap_team_fte if inputs.ap_team_fte > 0 else None),
        "annual_cost_break_even_fee_per_invoice": (
            cash_benefit_eur / inputs.invoices_per_year if inputs.invoices_per_year else None
        ),
    }
