"""Full scientific audit — summary report for Anammox research validation."""

from core.scientific_validation import format_audit_summary, run_full_scientific_audit


class TestFullScientificAudit:
    def test_audit_runs_all_domains(self):
        reports = run_full_scientific_audit()
        domains = {r.domain for r in reports}
        assert "Strous stoichiometry constants" in domains
        assert "Anammox 30-day simulation" in domains
        assert "PN single-step kinetics" in domains
        assert "Multi-column lab analysis" in domains

    def test_overall_critical_pass_rate(self):
        reports = run_full_scientific_audit()
        critical_total = 0
        critical_pass = 0
        for rep in reports:
            for check in rep.checks:
                if check.severity == "critical":
                    critical_total += 1
                    if check.passed:
                        critical_pass += 1
        rate = 100.0 * critical_pass / critical_total
        assert rate >= 90.0, format_audit_summary(reports)

    def test_anammox_domain_strong(self):
        reports = run_full_scientific_audit()
        anammox_reports = [
            r for r in reports
            if "Anammox" in r.domain or "Strous" in r.domain or "feed stoichiometry" in r.domain
        ]
        for rep in anammox_reports:
            assert rep.score_pct >= 85.0, f"{rep.domain} score {rep.score_pct}"

    def test_summary_text_generated(self):
        reports = run_full_scientific_audit()
        summary = format_audit_summary(reports)
        assert "Overall:" in summary
        assert "PASS" in summary or "FAIL" in summary
