"""Reactor operation log — flexible Excel import, i18n, detailed AI recommendations."""

import sys
import os
from datetime import datetime, timezone

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from core.ai_recommendations import ProviderId, get_detailed_recommendations
from core.env_loader import load_env
from core.i18n import t
from core.operation_log import OperationLogResult, parse_default_sample, parse_operation_log
from core.operation_log_charts import build_display_table, build_line_chart_df, resolve_x_axis
from core.oplog_inhibition_charts import build_fa_chart_df, build_fna_chart_df
from core.operation_log_ui import render_oplog_data_quality, render_section_advice
from core.ui.layout import render_app_chrome, render_sidebar_footer, render_sidebar_navigation, setup_page_config
from core.ui.operation_log_empty import render_oplog_empty_state

load_env()
setup_page_config(t("oplog.title"))

if st.session_state.get("user_id") is None:
    st.switch_page("Home.py")
    st.stop()

render_app_chrome("operation_log", defer_nav=True)

if "operation_log_result" not in st.session_state:
    st.session_state["operation_log_result"] = None
if "operation_log_ai_sections" not in st.session_state:
    st.session_state["operation_log_ai_sections"] = None
if "operation_log_ai_error" not in st.session_state:
    st.session_state["operation_log_ai_error"] = None
if "operation_log_upload_id" not in st.session_state:
    st.session_state["operation_log_upload_id"] = None
if "operation_log_fa_params" not in st.session_state:
    st.session_state["operation_log_fa_params"] = None
if "operation_log_last_meta" not in st.session_state:
    st.session_state["operation_log_last_meta"] = None
if "operation_log_banner_dismissed_for" not in st.session_state:
    st.session_state["operation_log_banner_dismissed_for"] = None


def _set_loaded_result(result: OperationLogResult, upload_id: str) -> None:
    st.session_state["operation_log_result"] = result
    st.session_state["operation_log_upload_id"] = upload_id
    st.session_state["operation_log_ai_sections"] = None
    st.session_state["operation_log_ai_error"] = None
    st.session_state["operation_log_banner_dismissed_for"] = None
    st.session_state["operation_log_last_meta"] = {
        "name": result.source_name,
        "count": result.summary.row_count,
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }


def _load_sample_from_desktop() -> None:
    sample = parse_default_sample()
    if sample is None:
        st.error(t("oplog.sample_missing"))
        return
    _set_loaded_result(sample, "sample:desktop")
    st.rerun()


with st.sidebar:
    st.markdown(f"**{t('oplog.load_data')}**")
    uploaded = st.file_uploader(t("oplog.upload"), type=["xlsx", "xls"])
    if st.button(t("oplog.load_sample"), use_container_width=True, key="oplog_sidebar_sample"):
        _load_sample_from_desktop()

    meta = st.session_state.get("operation_log_last_meta")
    if meta:
        st.markdown(t("oplog.file_ready", name=meta["name"], count=meta["count"]))
        st.caption(meta.get("ts", ""))

    st.divider()
    st.caption(t("oplog.inhibition_shared_ph"))
    fa_ph = st.number_input("pH", min_value=6.0, max_value=9.5, value=7.5, step=0.1, key="oplog_inhib_ph")
    fa_temp = st.number_input("T (°C)", min_value=15.0, max_value=45.0, value=35.0, step=0.5, key="oplog_inhib_temp")
    with st.expander(t("oplog.fa_optional"), expanded=False):
        st.caption(t("oplog.fa_hint"))
    with st.expander(t("oplog.fna_optional"), expanded=False):
        st.caption(t("oplog.fna_hint"))

    with st.expander(t("oplog.ai.api_keys"), expanded=False):
        st.caption(t("oplog.ai.api_hint"))
        st.caption(t("oplog.ai.no_key"))
        st.text_input("OpenAI", type="password", key="api_key_openai", placeholder="sk-...")
        st.text_input("Anthropic", type="password", key="api_key_claude", placeholder="sk-ant-...")
        st.text_input("DeepSeek", type="password", key="api_key_deepseek", placeholder="sk-...")
        st.text_input("Perplexity", type="password", key="api_key_perplexity", placeholder="pplx-...")

render_sidebar_navigation("operation_log")

if uploaded is not None:
    upload_id = f"{uploaded.name}:{uploaded.size}"
    if st.session_state.get("operation_log_upload_id") != upload_id:
        try:
            with st.spinner(t("oplog.parsing")):
                parsed = parse_operation_log(uploaded, source_name=uploaded.name)
            _set_loaded_result(parsed, upload_id)
            st.rerun()
        except Exception as exc:
            st.session_state["operation_log_last_meta"] = None
            st.error(str(exc))


def _refresh_builtin_advice():
    used, sections, err = get_detailed_recommendations(
        "rule_based",
        st.session_state["operation_log_result"],
        fa_ph=fa_ph,
        fa_temp=fa_temp,
    )
    st.session_state["operation_log_ai_sections"] = sections
    st.session_state["operation_log_ai_error"] = err
    st.session_state["operation_log_ai_used"] = used


result = st.session_state.get("operation_log_result")

with st.container(key="oplog_page_intro"):
    st.markdown(t("oplog.intro"))

if result is None:
    render_oplog_empty_state(on_load_sample=_load_sample_from_desktop)
    render_sidebar_footer()
    st.stop()

fa_params = (fa_ph, fa_temp)
if st.session_state.get("operation_log_fa_params") != fa_params:
    st.session_state["operation_log_fa_params"] = fa_params
    st.session_state["operation_log_ai_sections"] = None

if st.session_state.get("operation_log_ai_sections") is None:
    _refresh_builtin_advice()

df = result.df
summary = result.summary
schema = result.schema
x_col, x_label = resolve_x_axis(df, schema)

banner_key = st.session_state.get("operation_log_upload_id") or result.source_name
if st.session_state.get("operation_log_banner_dismissed_for") != banner_key:
    with st.container(key="oplog_loaded_banner"):
        b_col, d_col = st.columns([6, 1], vertical_alignment="center")
        with b_col:
            st.markdown(t("oplog.loaded", name=result.source_name, count=summary.row_count))
        with d_col:
            if st.button(t("ui.dismiss"), key="oplog_dismiss_loaded", use_container_width=True):
                st.session_state["operation_log_banner_dismissed_for"] = banner_key
                st.rerun()

r1_mean = summary.nh4_removal_r1_mean
r2_mean = summary.nh4_removal_r2_mean
r2_value = f"{r2_mean:.1f}%" if r2_mean else "—"
r2_delta: str | None = None
if r1_mean is not None and r2_mean is not None:
    r2_delta = f"{r2_mean - r1_mean:+.1f}%"

with st.container(border=False, key="oplog_summary_metrics"):
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(
        t("oplog.date_range"),
        f"{summary.date_start:%Y-%m-%d}" if summary.date_start else "—",
        help=t("oplog.help.date_range"),
    )
    m2.metric(
        t("oplog.to"),
        f"{summary.date_end:%Y-%m-%d}" if summary.date_end else "—",
        help=t("oplog.help.to"),
    )
    m3.metric(
        t("oplog.duration"),
        f"{summary.duration_min:.0f}–{summary.duration_max:.0f}" if summary.duration_min else "—",
        help=t("oplog.help.duration"),
    )
    m4.metric(
        t("oplog.mean_r1"),
        f"{r1_mean:.1f}%" if r1_mean else "—",
        help=t("oplog.help.mean_r1"),
    )
    m5.metric(
        t("oplog.mean_r2"),
        r2_value,
        delta=r2_delta,
        help=t("oplog.help.mean_r2"),
    )

if summary.removal_formula_max_error_pct is not None and summary.removal_formula_max_error_pct <= 0.01:
    st.caption(t("oplog.formula_ok", err=summary.removal_formula_max_error_pct))

render_oplog_data_quality(schema, summary.alerts)

# --- Charts ---
st.divider()
tab_labels = [
    t("oplog.tab.nh4"),
    t("oplog.tab.removal"),
    t("oplog.tab.tn"),
    t("oplog.tab.ops"),
    t("oplog.tab.compare"),
    t("oplog.tab.fa"),
    t("oplog.tab.fna"),
    t("oplog.tab.data"),
]
with st.container(key="oplog_chart_tabs"):
    tabs = st.tabs(tab_labels)

with tabs[0]:
    cols = [c for c in ("nh4_influent_mg_l", "reactor1_effluent_mg_l", "reactor2_effluent_mg_l") if c in schema.detected_fields]
    if not cols:
        st.info("—")
    else:
        st.line_chart(build_line_chart_df(df, schema, cols))

with tabs[1]:
    rem_cols = [c for c in ("removal_rate_r1_pct", "removal_rate_r2_pct") if c in df.columns and df[c].notna().any()]
    if rem_cols:
        st.line_chart(build_line_chart_df(df, schema, rem_cols))
    else:
        st.info("—")

with tabs[2]:
    tn_cols = [c for c in ("tn_influent_mg_l", "tn_effluent_r1_mg_l", "tn_effluent_r2_mg_l") if c in schema.detected_fields]
    if tn_cols:
        st.line_chart(build_line_chart_df(df, schema, tn_cols))
    else:
        st.info("—")

with tabs[3]:
    ops_cols = [c for c in ("anr_r1_g_n_l_d", "anr_r2_g_n_l_d", "loading_influent_g_n_l_d") if c in schema.detected_fields]
    if ops_cols:
        st.line_chart(build_line_chart_df(df, schema, ops_cols))
    else:
        st.info("—")

with tabs[4]:
    if "reactor1_effluent_mg_l" in schema.detected_fields and "reactor2_effluent_mg_l" in schema.detected_fields:
        last = df.iloc[-1]
        c1, c2, c3 = st.columns(3)
        c1.metric(t("oplog.compare.r1"), f"{last['reactor1_effluent_mg_l']:.1f} mg/L")
        c2.metric(t("oplog.compare.r2"), f"{last['reactor2_effluent_mg_l']:.1f} mg/L")
        c3.metric(t("oplog.compare.diff"), f"{last['reactor2_effluent_mg_l'] - last['reactor1_effluent_mg_l']:+.1f} mg/L")
    else:
        st.info("—")

with tabs[5]:
    st.caption(t("oplog.fa_formula"))
    fa_chart = build_fa_chart_df(df, x_col=x_col, x_label=x_label, ph=fa_ph, temperature_c=fa_temp)
    if fa_chart is None:
        st.info(t("oplog.fa_missing_nh4"))
    else:
        st.line_chart(fa_chart)

with tabs[6]:
    st.caption(t("oplog.fna_formula"))
    fna_chart = build_fna_chart_df(df, x_col=x_col, x_label=x_label, ph=fa_ph, temperature_c=fa_temp)
    if fna_chart is None:
        st.info(t("oplog.fna_missing_no2"))
    else:
        st.line_chart(fna_chart)

with tabs[7]:
    st.dataframe(build_display_table(df), use_container_width=True, hide_index=True)
    st.download_button(t("oplog.download_csv"), df.to_csv(index=False).encode("utf-8"), "operation_log.csv", "text/csv")

# --- AI recommendations BELOW charts ---
st.divider()
st.subheader(t("oplog.ai.title"))

provider_options: list[tuple[str, ProviderId]] = [
    (t("oplog.ai.rule_based"), "rule_based"),
    (t("oplog.ai.providers.gpt"), "gpt"),
    (t("oplog.ai.providers.claude"), "claude"),
    (t("oplog.ai.providers.deepseek"), "deepseek"),
    (t("oplog.ai.providers.perplexity"), "perplexity"),
]
provider_labels = [p[0] for p in provider_options]
provider_ids = [p[1] for p in provider_options]

ai_col1, ai_col2 = st.columns([2, 1])
with ai_col1:
    selected_label = st.selectbox(t("oplog.ai.provider"), provider_labels, key="oplog_ai_provider")
    selected_provider: ProviderId = provider_ids[provider_labels.index(selected_label)]
with ai_col2:
    st.write("")
    st.write("")
    run_ai = st.button(t("oplog.ai.get"), type="primary", use_container_width=True)

if run_ai:
    with st.spinner("…"):
        used, sections, err = get_detailed_recommendations(
            selected_provider,
            result,
            fa_ph=fa_ph,
            fa_temp=fa_temp,
        )
        st.session_state["operation_log_ai_sections"] = sections
        st.session_state["operation_log_ai_error"] = err
        st.session_state["operation_log_ai_used"] = used

sections = st.session_state.get("operation_log_ai_sections")
ai_error = st.session_state.get("operation_log_ai_error")

if ai_error:
    st.error(ai_error)

if sections:
    render_section_advice(sections)

render_sidebar_footer()
