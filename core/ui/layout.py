"""Shared Streamlit layout — compact sidebar nav, top toolbar, modern styling."""

from __future__ import annotations

import html

import streamlit as st

from core.auth_session import clear_login
from core.i18n import init_lang, t
from core.ui.brand import inject_seo, logo_path, render_logo_html
from core.ui.navigation import navigate_to, render_page_transition_overlay, switch_to
from core.ui.theme import inject_theme_css, init_theme, render_topbar_theme_segment

DASHBOARD_PATH = "pages/1_Lab_Dashboard.py"
HOME_PATH = "Home.py"
BRAND_NAME = "KASLU LAB"

NAV_GROUPS: dict[str, list[tuple[str, str, str]]] = {
    "Workflow": [
        ("dashboard", "Dashboard", DASHBOARD_PATH),
        ("operation_log", "Reactor Operation Log", "pages/2_Reactor_Operation_Log.py"),
        ("sample", "Sample Analysis", "pages/2_Sample_Analysis.py"),
        ("simulation", "Performance Analysis", "pages/1_Simulation.py"),
        ("history", "History", "pages/6_Simulation_History.py"),
        ("advisor", "AI Advisor", "pages/7_AI_Advisor.py"),
    ],
    "Lab tools": [
        ("pn", "PN Monitor", "pages/3_PN_Monitor.py"),
        ("stoich", "Stoichiometry", "pages/4_Stoichiometry.py"),
        ("diagnostics", "Daily Diagnostics", "pages/5_Daily_Diagnostics.py"),
        ("analytics", "Experiment Analysis", "pages/6_Analytics.py"),
        ("sensitivity", "Sensitivity", "pages/6_Sensitivity_Analysis.py"),
        ("exp_details", "Experiment Details", "pages/5_Experiment_Details.py"),
    ],
    "Research": [
        ("prediction", "Hybrid / ML Prediction", "pages/4_Prediction.py"),
        ("optimization", "Optimization", "pages/9_Optimization.py"),
        ("monte_carlo", "Monte Carlo", "pages/7_Monte_Carlo.py"),
        ("comparison", "Comparison", "pages/4_Comparison.py"),
        ("pdf_report", "PDF Report", "pages/8_PDF_Report.py"),
    ],
    "Administration": [
        ("admin", "Admin Panel", "pages/0_Admin.py"),
    ],
}

PAGE_I18N_KEYS: dict[str, str] = {
    "dashboard": "nav.dashboard",
    "operation_log": "nav.operation_log",
    "sample": "nav.sample",
    "simulation": "nav.simulation",
    "history": "nav.history",
    "advisor": "nav.advisor",
    "pn": "nav.pn",
    "stoich": "nav.stoich",
    "diagnostics": "nav.diagnostics",
    "analytics": "nav.analytics",
    "sensitivity": "nav.sensitivity",
    "exp_details": "nav.exp_details",
    "prediction": "nav.prediction",
    "optimization": "nav.optimization",
    "monte_carlo": "nav.monte_carlo",
    "comparison": "nav.comparison",
    "pdf_report": "nav.pdf_report",
    "admin": "nav.admin_panel",
}

GROUP_I18N_KEYS: dict[str, str] = {
    "Workflow": "nav.workflow",
    "Lab tools": "nav.lab_tools",
    "Research": "nav.research",
    "Administration": "nav.admin",
}


def setup_page_config(title: str | None = None, *, wide: bool = True) -> None:
    from core.auth_session import restore_session

    init_theme()
    init_lang()
    restore_session()
    layout = "wide" if wide else "centered"
    page_title = title or BRAND_NAME
    if BRAND_NAME not in page_title.upper():
        page_title = f"{page_title} · {BRAND_NAME}"
    icon = str(logo_path()) if logo_path().is_file() else "🧪"
    st.set_page_config(
        page_title=page_title,
        page_icon=icon,
        layout=layout,
        initial_sidebar_state="expanded",
    )


def _render_sidebar_brand() -> None:
    logo = render_logo_html(size="48px", css_class="brand-logo")
    st.markdown(
        f"""
        <div class="app-brand">
            <div class="brand-logo-row">
                <span class="brand-logo-emblem">{logo}</span>
                <p class="brand-title">{t("brand.title")}</p>
            </div>
            <p class="brand-sub">{t("brand.sub")}</p>
            <div class="brand-accent"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_sidebar_navigation(current_page: str) -> None:
    """Page navigation — call after page-specific sidebar controls when present."""
    with st.sidebar:
        for group_name, items in NAV_GROUPS.items():
            expanded = any(page_id == current_page for page_id, _label, _path in items)
            group_label = t(GROUP_I18N_KEYS.get(group_name, group_name))
            with st.expander(group_label, expanded=expanded):
                for idx, (page_id, _label, path) in enumerate(items):
                    if idx > 0:
                        st.markdown('<div class="sidebar-nav-divider"></div>', unsafe_allow_html=True)
                    label = t(PAGE_I18N_KEYS.get(page_id, page_id))
                    if page_id == current_page:
                        st.markdown(
                            f'<div class="nav-current">{label}</div>',
                            unsafe_allow_html=True,
                        )
                    elif st.button(label, key=f"sidebar_nav_{page_id}", use_container_width=True):
                        navigate_to(path)


def _render_top_toolbar(current_page: str) -> None:
    page_label = t(PAGE_I18N_KEYS.get(current_page, current_page))
    username = st.session_state.get("username") or "User"

    st.markdown('<div class="kaslu-topbar-marker"></div>', unsafe_allow_html=True)
    with st.container(border=True, key="app_top_bar"):
        title_col, actions_col = st.columns([5, 5], vertical_alignment="center")

        with title_col:
            if current_page != "dashboard":
                nav_block, label_col = st.columns(
                    [0.95, 4.05], gap="small", vertical_alignment="center"
                )
                with nav_block:
                    home_col, back_col = st.columns(2, gap="small")
                    with home_col:
                        if st.button(
                            "\u200b",
                            key="top_home",
                            icon=":material/home:",
                            type="secondary",
                            help=t("ui.home"),
                            width="content",
                        ):
                            navigate_to(DASHBOARD_PATH)
                    with back_col:
                        if st.button(
                            "\u200b",
                            key="top_back",
                            icon=":material/arrow_back:",
                            type="secondary",
                            help=t("ui.back"),
                            width="content",
                        ):
                            navigate_to(DASHBOARD_PATH)
                with label_col:
                    st.markdown(
                        f'<p class="topbar-page-title"><span class="lab-status-dot"></span>{page_label}</p>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    f'<p class="topbar-page-title"><span class="lab-status-dot"></span>{page_label}</p>',
                    unsafe_allow_html=True,
                )

        with actions_col:
            user_col, theme_col, logout_col = st.columns(
                [1.85, 1.35, 1.2], gap="small", vertical_alignment="center"
            )
            with user_col:
                initial = (username.strip()[:1] or "U").upper()
                safe_user = html.escape(username)
                safe_initial = html.escape(initial)
                account_label = html.escape(t("ui.account"))
                st.markdown(
                    f"""
                    <div class="topbar-account">
                        <span class="topbar-account-avatar" aria-hidden="true">{safe_initial}</span>
                        <span class="topbar-account-text">
                            <span class="topbar-account-label">{account_label}</span>
                            <span class="topbar-account-name">{safe_user}</span>
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with theme_col:
                render_topbar_theme_segment()
            with logout_col:
                if st.button(t("ui.logout_short"), key="top_logout", use_container_width=True):
                    clear_login()
                    switch_to(HOME_PATH)


def render_app_chrome(current_page: str, *, defer_nav: bool = False) -> None:
    """Call once at the top of each authenticated page (after login check)."""
    inject_seo(page_title=t(PAGE_I18N_KEYS.get(current_page, current_page)))
    inject_theme_css()
    render_page_transition_overlay()
    with st.sidebar:
        _render_sidebar_brand()
    if not defer_nav:
        render_sidebar_navigation(current_page)
    _render_top_toolbar(current_page)


def render_sidebar_footer() -> None:
    """Reserved for page-specific sidebar widgets (logout lives in the top bar)."""
    return


def render_login_chrome() -> None:
    """Theme + toggle for the public login page."""
    from core.ui.login_page import inject_login_page_css

    inject_seo(page_title=t("home.title"))
    inject_theme_css()
    inject_login_page_css()
