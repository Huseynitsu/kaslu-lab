"""In-app navigation with optional K-branded page transition overlay."""

from __future__ import annotations

import html

import streamlit as st

from core.ui.brand import logo_data_uri

NAV_LOADING_KEY = "_kaslu_page_transition"


def _main_script_basename() -> str:
    try:
        from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx

        ctx = get_script_run_ctx()
        if ctx and ctx.main_script_path:
            from pathlib import Path

            return Path(ctx.main_script_path).name
    except Exception:
        pass
    return "Home.py"


def resolve_page_path(page: str) -> str:
    """Map paths for repo-root entry (streamlit_app.py) vs app/Home.py entry."""
    if _main_script_basename() == "streamlit_app.py" and page == "Home.py":
        return "streamlit_app.py"
    return page


def switch_to(page_path: str) -> None:
    st.switch_page(resolve_page_path(page_path))


def navigate_to(page_path: str) -> None:
    """Set transition flag and switch Streamlit page (authenticated nav)."""
    st.session_state[NAV_LOADING_KEY] = True
    switch_to(page_path)


def render_page_transition_overlay() -> None:
    """Show a brief K logo overlay when arriving after navigate_to."""
    if not st.session_state.get(NAV_LOADING_KEY):
        return

    st.session_state[NAV_LOADING_KEY] = False
    logo_src = html.escape(logo_data_uri())
    st.markdown(
        f"""
        <div id="kaslu-page-transition" class="kaslu-page-transition" aria-hidden="true">
            <div class="kaslu-page-transition-inner">
                <div class="kaslu-page-transition-ring"></div>
                <img class="kaslu-page-transition-logo" src="{logo_src}" alt="" />
            </div>
        </div>
        <script>
        (function () {{
            var el = document.getElementById("kaslu-page-transition");
            if (!el) return;
            requestAnimationFrame(function () {{
                el.classList.add("kaslu-page-transition--active");
            }});
            window.setTimeout(function () {{
                el.classList.add("kaslu-page-transition--done");
                window.setTimeout(function () {{ el.remove(); }}, 420);
            }}, 520);
        }})();
        </script>
        """,
        unsafe_allow_html=True,
    )
