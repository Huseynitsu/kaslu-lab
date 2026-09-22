"""Scientific validation — Anammox kinetics and 30-day simulation."""

import pytest

from core.constants import ANAMMOX_NO3_PER_NH4
from core.scientific_validation import validate_anammox_30day_simulation, validate_anammox_single_step


class TestAnammoxSingleStep:
    def test_critical_checks_pass(self):
        report = validate_anammox_single_step()
        critical = [c for c in report.checks if c.severity == "critical"]
        failed = [c.name for c in critical if not c.passed]
        assert not failed, f"Failed: {failed}"

    def test_strous_removal_ratios(self):
        report = validate_anammox_single_step()
        no2_ratio = next(c for c in report.checks if "NO2/NH4 removal ratio" in c.name)
        no3_ratio = next(c for c in report.checks if "NO3/NH4 production ratio" in c.name)
        assert no2_ratio.passed
        assert no3_ratio.passed

    def test_oxygen_inhibition(self):
        report = validate_anammox_single_step()
        o2 = next(c for c in report.checks if "Oxygen inhibition" in c.name)
        assert o2.passed


class TestAnammox30Day:
    def test_intrinsic_no3_strous_ratio(self):
        report = validate_anammox_30day_simulation()
        ratio_check = next(c for c in report.checks if "intrinsic NO3/NH4" in c.name)
        assert ratio_check.passed
        assert ANAMMOX_NO3_PER_NH4 == pytest.approx(0.26, abs=0.001)

    def test_nh4_and_no2_decrease(self):
        report = validate_anammox_30day_simulation()
        nh4_trend = next(c for c in report.checks if "Monotonic NH4" in c.name)
        no2_trend = next(c for c in report.checks if "Monotonic NO2" in c.name)
        assert nh4_trend.passed
        assert no2_trend.passed

    def test_low_do_outperforms_high_do(self):
        report = validate_anammox_30day_simulation()
        do_check = next(c for c in report.checks if "Low DO removes" in c.name)
        assert do_check.passed

    def test_critical_anammox_checks(self):
        report = validate_anammox_30day_simulation()
        assert report.all_critical_passed
