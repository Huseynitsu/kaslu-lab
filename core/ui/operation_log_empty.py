"""Empty state for Reactor Operation Log main area."""

from __future__ import annotations

import html

import streamlit as st

from core.i18n import t


def render_oplog_empty_state(*, on_load_sample) -> None:
    """Three-step guide + primary sample CTA. on_load_sample() loads data and reruns."""
    steps = [
        t("oplog.steps.upload"),
        t("oplog.steps.preview"),
        t("oplog.steps.charts"),
    ]
    step_items = "".join(
        f'<li class="oplog-empty-step"><span class="oplog-empty-step-num">{idx}</span>'
        f'<span class="oplog-empty-step-label">{html.escape(label)}</span></li>'
        for idx, label in enumerate(steps, start=1)
    )
    heading = html.escape(t("oplog.empty_heading"))

    st.markdown(
        f"""
        <div class="oplog-empty-state">
            <p class="oplog-empty-title">{heading}</p>
            <ol class="oplog-empty-steps">{step_items}</ol>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(t("oplog.empty"))
    if st.button(t("oplog.load_sample"), type="primary", key="oplog_empty_sample", use_container_width=False):
        on_load_sample()
