#!/usr/bin/env python
"""Run the full scientific validation audit and print results."""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from core.scientific_validation import format_audit_summary, run_full_scientific_audit

if __name__ == "__main__":
    reports = run_full_scientific_audit()
    print(format_audit_summary(reports))
    critical_fail = any(
        not c.passed for r in reports for c in r.checks if c.severity == "critical"
    )
    sys.exit(1 if critical_fail else 0)
