"""Reusable lab-themed UI building blocks (presentation only)."""

from __future__ import annotations

import streamlit as st

from core.i18n import t
from core.ui.navigation import navigate_to


def render_page_header(title: str, caption: str | None = None, *, badge: str | None = None) -> None:
    badge_html = f'<span class="lab-badge">{badge}</span>' if badge else ""
    caption_html = f'<p class="lab-page-caption">{caption}</p>' if caption else ""
    st.markdown(
        f"""
        <div class="lab-page-header">
            <div class="lab-page-header-text">
                <h1 class="lab-page-title">{title}{badge_html}</h1>
                {caption_html}
            </div>
            <div class="lab-page-header-accent"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section(title: str, subtitle: str | None = None) -> None:
    subtitle_html = f'<p class="lab-section-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div class="lab-section">
            <h2 class="lab-section-title">{title}</h2>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_workflow_strip(steps: list[str]) -> None:
    cols = st.columns(len(steps), gap="small")
    for col, (idx, label) in zip(cols, enumerate(steps, start=1)):
        with col:
            with st.container(border=True, key=f"wf_step_{idx}"):
                st.markdown(f"**{idx:02d}**")
                st.caption(label)


def render_module_card(title: str, description: str, path: str, button_key: str) -> None:
    with st.container(border=True, key=button_key):
        st.markdown(f"**{title}**")
        st.caption(description)
        if st.button(t("dash.open"), key=f"{button_key}_open", type="primary", use_container_width=True):
            navigate_to(path)


def render_data_panel(title: str) -> None:
    st.markdown(
        f'<div class="lab-data-panel"><p class="lab-data-panel-title">{title}</p></div>',
        unsafe_allow_html=True,
    )
