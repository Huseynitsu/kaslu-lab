"""Generate repo-root pages/*.py shims for Streamlit Cloud (main file: streamlit_app.py)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PAGES = ROOT / "app" / "pages"
OUT = ROOT / "pages"

SHIM = '''"""Streamlit Cloud shim (main file: streamlit_app.py at repo root)."""
import runpy
from pathlib import Path

runpy.run_path(
    str(Path(__file__).resolve().parent.parent / "app" / "pages" / Path(__file__).name),
    run_name="__main__",
)
'''

def main() -> None:
    OUT.mkdir(exist_ok=True)
    for src in sorted(APP_PAGES.glob("*.py")):
        dest = OUT / src.name
        dest.write_text(SHIM, encoding="utf-8")
        print("wrote", dest.relative_to(ROOT))


if __name__ == "__main__":
    main()
