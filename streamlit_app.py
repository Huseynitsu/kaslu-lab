"""Streamlit Community Cloud entry (main file can point here or to app/Home.py)."""

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / "app" / "Home.py"), run_name="__main__")
