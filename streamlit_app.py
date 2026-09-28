"""Streamlit Community Cloud entry (main file: streamlit_app.py).

Login runs from app/Home.py; multipage routes use repo-root pages/ shims
(see scripts/sync_root_pages.py). Local dev: streamlit run app/Home.py
"""

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

runpy.run_path(str(ROOT / "app" / "Home.py"), run_name="__main__")
