import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Legacy debug scripts (run top-level code against a local anammox.db, contain no test functions).
# Kept for reference, excluded from collection so the real test-suite can run on a clean checkout.
collect_ignore = [
    name for name in os.listdir(os.path.dirname(__file__))
    if name.startswith("test_") and name.endswith(".py")
    and "def test" not in open(os.path.join(os.path.dirname(__file__), name), encoding="utf-8").read()
]
