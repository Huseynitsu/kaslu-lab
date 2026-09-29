"""Scientific validation — literature benchmarks and equation verification."""

import pytest

from core import scientific_validation as sv


@pytest.mark.parametrize("fn", [
    sv.validate_chemistry,
    sv.validate_stoichiometry,
    sv.validate_anammox_kinetics,
    sv.validate_pn_sharon,
    sv.validate_pna,
    sv.validate_lab_tools,
    sv.validate_early_warning,
])
def test_domain_passes(fn):
    report = fn()
    failed = [c for c in report.checks if not c.passed]
    assert not failed, sv.format_audit_summary([report])
