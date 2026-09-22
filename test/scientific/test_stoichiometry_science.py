"""Scientific validation — Strous stoichiometry and feed readiness."""

from core.scientific_validation import validate_stoichiometry_feed, validate_strous_constants


class TestStrousConstants:
    def test_all_critical_pass(self):
        report = validate_strous_constants()
        assert report.all_critical_passed
        assert report.score_pct == 100.0


class TestAnammoxFeedStoichiometry:
    def test_ideal_effluent_ready(self):
        report = validate_stoichiometry_feed()
        ready = next(c for c in report.checks if "Ideal PN effluent" in c.name)
        assert ready.passed

    def test_mechanistic_no3_matches_strous(self):
        report = validate_stoichiometry_feed()
        mech = next(c for c in report.checks if "Mechanistic NO3" in c.name)
        assert mech.passed

    def test_low_no2_not_ready(self):
        report = validate_stoichiometry_feed()
        low = next(c for c in report.checks if "Low NO2" in c.name)
        assert low.passed
