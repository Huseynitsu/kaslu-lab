"""Streamlit Cloud shim (main file: streamlit_app.py at repo root)."""
import runpy
from pathlib import Path

runpy.run_path(
    str(Path(__file__).resolve().parent.parent / "app" / "pages" / Path(__file__).name),
    run_name="__main__",
)
