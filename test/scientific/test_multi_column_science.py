"""Scientific validation — multi-column lab notebook analysis."""

from core.scientific_validation import validate_multi_column_analysis


class TestMultiColumnScience:
    def test_all_checks_pass(self):
        report = validate_multi_column_analysis()
        assert report.all_critical_passed
        assert report.score_pct == 100.0

    def test_nh4_efficiency_formula(self):
        report = validate_multi_column_analysis()
        eff = next(c for c in report.checks if "efficiency formula" in c.name.lower())
        assert eff.passed
        assert eff.actual == "50.0%"

    def test_reactor_no2_nh4_ratio(self):
        report = validate_multi_column_analysis()
        ratio = next(c for c in report.checks if "Reactor NO2/NH4" in c.name)
        assert ratio.passed
