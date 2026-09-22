"""Scientific validation — Partial nitritation (PN) model."""

from core.scientific_validation import validate_pn_30day_batch, validate_pn_single_step


class TestPNSingleStep:
    def test_nh4_to_no2_direction(self):
        report = validate_pn_single_step()
        nh4 = next(c for c in report.checks if "NH4 down" in c.name)
        no2 = next(c for c in report.checks if "NO2 accumulates" in c.name)
        assert nh4.passed
        assert no2.passed

    def test_nob_suppression_low_no3(self):
        report = validate_pn_single_step()
        no3 = next(c for c in report.checks if "NOB suppressed" in c.name)
        nar = next(c for c in report.checks if "High NAR" in c.name)
        assert no3.passed
        assert nar.passed

    def test_all_critical_pass(self):
        report = validate_pn_single_step()
        assert report.all_critical_passed


class TestPN30DayBatch:
    def test_nob_suppression_and_nar(self):
        report = validate_pn_30day_batch()
        no3 = next(c for c in report.checks if "NO3 stays low" in c.name)
        nar = next(c for c in report.checks if "Final NAR high" in c.name)
        assert no3.passed
        assert nar.passed

    def test_directional_trends(self):
        report = validate_pn_30day_batch()
        nh4 = next(c for c in report.checks if "NH4 decreases" in c.name)
        no2 = next(c for c in report.checks if "NO2 increases" in c.name)
        assert nh4.passed
        assert no2.passed

    def test_calibration_info_flag(self):
        """PN batch removes little NH4 in 30 d — documented as calibration gap."""
        report = validate_pn_30day_batch()
        cal = next(c for c in report.checks if "calibration" in c.name.lower())
        assert cal.severity == "info"
