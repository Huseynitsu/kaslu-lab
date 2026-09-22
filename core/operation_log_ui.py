"""Render operation log recommendation cards in Streamlit."""

from __future__ import annotations

import streamlit as st

from core.i18n import t
from core.operation_log_schema import SchemaReport
from core.operation_log_sections import SectionAdvice


def render_oplog_data_quality(schema: SchemaReport, alerts: list[str]) -> None:
    """User-facing notices only — no raw column name lists."""
    for alert in alerts:
        st.caption(alert)

    if not schema.warnings:
        return

    with st.expander(t("oplog.dq.warnings"), expanded=False):
        with st.container(key="oplog_data_quality"):
            for warning in schema.warnings:
                st.caption(warning)


def _render_metric_row(items: list) -> None:
    """Compact metric tiles using native Streamlit widgets (no raw HTML)."""
    if not items:
        return

    per_row = 3 if len(items) > 2 else len(items)
    for start in range(0, len(items), per_row):
        chunk = items[start : start + per_row]
        cols = st.columns(len(chunk), gap="small")
        for col, item in zip(cols, chunk):
            with col:
                st.metric(label=item.label, value=item.value)
                if item.caption:
                    st.caption(item.caption)


def render_section_advice(sections: list[SectionAdvice]) -> None:
    for sec in sections:
        with st.container(border=True):
            st.markdown(f"#### {sec.title}")
            if sec.summary:
                st.markdown(sec.summary)

            if sec.highlights:
                _render_metric_row(sec.highlights[:4])

            if sec.recommendations:
                st.markdown(f"**{t('oplog.ai.actions')}**")
                for rec in sec.recommendations:
                    st.markdown(f"- {rec}")
