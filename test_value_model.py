from value_model import ValueInputs, calculate, SCENARIOS


def test_excel_base():
    x = calculate(ValueInputs(), *SCENARIOS["Base"])
    assert abs(x["baseline_manual_hours"] - 10633.33333333) < 1e-5
    assert abs(x["baseline_manual_fte"] - 6.90476190476) < 1e-5
    assert abs(x["hours_released"] - 6911.6666667) < 1e-5
    assert abs(x["gross_capacity_eur"] - 311025) < 1e-6
    assert abs(x["cash_benefit_eur"] - 186615) < 1e-6
    assert abs(x["annual_software_eur"] - 23028) < 1e-6
    assert abs(x["annual_net_eur"] - 163587) < 1e-6
    assert abs(x["year_one_net_eur"] - 113587) < 1e-6
    assert abs(x["payback_months"] - 3.66777311) < 1e-6


def test_scenarios_match_excel():
    expected = {"Conservative": (72672, 22672),
                "Base": (163587, 113587),
                "Optimistic": (264072, 214072)}
    for scenario, (annual, year1) in expected.items():
        data = calculate(ValueInputs(), *SCENARIOS[scenario])
        assert abs(data["annual_net_eur"] - annual) < 1e-6
        assert abs(data["year_one_net_eur"] - year1) < 1e-6


def test_no_illusory_cash_saving_when_not_realized():
    x = calculate(ValueInputs(), .65, 0)
    assert x["cash_benefit_eur"] == 0
    assert x["annual_net_eur"] < 0
    assert x["payback_months"] is None
    assert x["fte_released"] > 0


def test_scaling_changes_invoices_without_using_revenue():
    base = calculate(ValueInputs(), *SCENARIOS["Base"])
    half = calculate(ValueInputs(invoices_per_year=30_300), *SCENARIOS["Base"])
    assert abs(half["baseline_manual_hours"] - base["baseline_manual_hours"] / 2) < 1e-6
    assert abs(half["annual_software_eur"] - base["annual_software_eur"] / 2) < 1e-6


if __name__ == "__main__":
    test_excel_base()
    test_scenarios_match_excel()
    test_no_illusory_cash_saving_when_not_realized()
    test_scaling_changes_invoices_without_using_revenue()
    print("4 model tests passed; Base and all 3 scenarios align with the Excel workbook.")
