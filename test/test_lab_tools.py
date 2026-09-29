import pytest

from core.diagnostics import interpret_daily_reading
from core.dilution import calculate_dilution, fit_calibration, suggest_dilution_factor
from core.lab_table import default_table
from core.multi_column_analysis import analyze_multi_column
from core.pn_control import assess_pn_operation


def test_dilution_back_calculation():
    r = calculate_dilution(0.45, 0.30, dilution_factor=50, blank_absorbance=0.0)
    assert r.true_concentration_mg_l == pytest.approx(75.0)
    assert r.in_linear_range


def test_suggested_factor():
    assert suggest_dilution_factor(1.6) == 5.0
    assert suggest_dilution_factor(0.5) == 1.0


def test_calibration_quality_flags():
    bad = fit_calibration([0, 1, 2], [0, 0.3, 0.61])
    assert not bad.acceptable  # fewer than 5 standards


def test_blank_is_not_a_sample_point():
    t = default_table()
    t["nh4"]["distilled"] = 2.0
    res = analyze_multi_column(t, stage="pna")
    assert any("blank" in a.message.lower() for a in res.alerts)
    assert "Entrance − Distilled" not in set(res.differences_df.get("Comparison", []))


def test_pna_diagnostics_nob_alarm():
    d = interpret_daily_reading(20, 1, 60, 200, 0, 0, stage="pna")  # ΔNO3/ΔNH4 = 0.33
    assert d.status == "danger"


def test_anammox_diagnostics_consistent():
    d = interpret_daily_reading(10, 13.2, 10.4, 50, 66, 0, stage="anammox")  # 40 NH4, 52.8 NO2, 10.4 NO3
    assert d.status == "ok"
    assert d.metrics["ΔNO2/ΔNH4"] == pytest.approx(1.32)


def test_pna_assessment_flags_short_srt():
    a = assess_pn_operation(0.3, 30, 7.6, 3, 20, 2, mode="pna")
    assert a.overall_status == "danger"
