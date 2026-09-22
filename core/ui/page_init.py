"""Bootstrap authenticated Streamlit pages with shared layout and theme."""

from __future__ import annotations

import os
import sys

import streamlit as st

from core.ui.layout import render_app_chrome, render_sidebar_footer, setup_page_config

HOME_PATH = "Home.py"


def ensure_project_root(file_path: str) -> None:
    project_root = os.path.abspath(os.path.join(os.path.dirname(file_path), "..", ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def bootstrap_page(
    file_path: str,
    page_id: str,
    title: str,
    *,
    wide: bool = True,
) -> bool:
    ensure_project_root(file_path)
    setup_page_config(title, wide=wide)

    if st.session_state.get("user_id") is None:
        st.switch_page(HOME_PATH)
        st.stop()

    render_app_chrome(page_id)
    return True


def finish_page() -> None:
    render_sidebar_footer()
