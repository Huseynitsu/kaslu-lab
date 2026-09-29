import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import matplotlib.pyplot as plt
import streamlit as st

from core.ui.layout import render_app_chrome, render_sidebar_footer, setup_page_config
from core.ui.navigation import switch_to

setup_page_config("Performance Analysis")

if st.session_state.get("user_id") is None:
    switch_to("Home.py")
    st.stop()

from core.config import ExperimentConfig
from core.constants import get_literature_default, get_literature_reference
from core.database import save_experiment, save_lab_reading, save_timeseries
from core.diagnostics import interpret_daily_reading
from core.lab_state import LAB_SELECTED_COLUMNS, LAB_TABLE, init_lab_state
from core.lab_table import (
    SAMPLE_COLUMNS,
    build_simulation_inputs,
    dataframe_to_table,
    notebook_editor_column_config,
    selected_columns_to_json,
    table_to_dataframe,
    table_to_json,
)
from core.multi_column_analysis import (
    analyze_multi_column,
    plot_comparison_bars,
    plot_efficiency_bars,
    plot_ratio_comparison,
)
from core.ui.theme import apply_matplotlib_theme
from core.pn_config import PNConfig
from core.pn_simulation import simulate_pn_30_days
from core.pna_model import ReactorConfig
from core.pna_model import simulate as simulate_pna
from core.constants import PNA_MAX_TN_REMOVAL
from core.lab_table import extract_column
import pandas as pd
from core.simulation import simulate_30_days

init_lab_state()
render_app_chrome("simulation")

st.title("Reactor Performance Analysis")
st.markdown("""
Compare **Entrance (influent)** and **Reactor (bulk/effluent)**; **Distilled water** is the reagent blank.
Indicators depend on the reactor type: PN → NO₂/NH₄ of the effluent vs 1.32 (anammox feed);
anammox → ΔNO₂/ΔNH₄ ≈ 1.32 and ΔNO₃/ΔNH₄ ≈ 0.26; one-stage PN/A → TIN removal and ΔNO₃/ΔNH₄ ≈ 0.11.
""")

stage = st.radio(
    "Reactor type",
    ["pna", "pn", "anammox"],
    format_func=lambda x: {"pna": "One-stage PN/A", "pn": "PN reactor (two-stage)", "anammox": "UASB / Anammox reactor"}[x],
    horizontal=True,
)

st.subheader("Laboratory notebook")
st.caption("Enter measured values for each sample point. Column headers are fixed.")

edited_df = st.data_editor(
    table_to_dataframe(st.session_state[LAB_TABLE]),
    column_config=notebook_editor_column_config(),
    hide_index=True,
    use_container_width=True,
    key="lab_notebook_editor",
)
st.session_state[LAB_TABLE] = dataframe_to_table(edited_df)

st.subheader("Sample points for analysis")
st.caption("Entrance + Reactor are needed for removal indicators; the blank is only checked for contamination.")

selected_columns = []
cols = st.columns(3)
for idx, (col_key, col_label) in enumerate(SAMPLE_COLUMNS.items()):
    default_on = col_key in st.session_state.get(LAB_SELECTED_COLUMNS, list(SAMPLE_COLUMNS.keys()))
    with cols[idx]:
        if st.checkbox(col_label, value=default_on, key="col_%s" % col_key):
            selected_columns.append(col_key)

if not selected_columns:
    st.error("Select at least one sample point.")
    st.stop()

st.session_state[LAB_SELECTED_COLUMNS] = selected_columns

st.subheader("Operating conditions (optional — kinetic forecast only)")
st.caption("Forecast = uncalibrated mechanistic model (Hao et al. 2002 structure). Entrance values are used as the "
           "influent and Reactor values as the initial state. Literature defaults apply when unchecked.")
hrt_h = st.number_input("HRT (h) — continuous operation (0 = batch)", min_value=0.0, value=24.0, step=1.0)

use_custom = {}
custom_values = {}
op_params = ["temperature", "do", "srt", "biomass"]  # biomass = AOB (PN) or anammox (anammox, PN/A)
if stage == "anammox":
    op_params.append("hco3")

for param in op_params:
    default_val = get_literature_default(stage, param)
    ref = get_literature_reference(stage, param)
    label = param.replace("_", " ").title()
    c1, c2 = st.columns([1, 2])
    with c1:
        use_custom[param] = st.checkbox(
            "Custom %s" % label,
            value=False,
            key="custom_%s" % param,
        )
    with c2:
        if use_custom[param]:
            if param == "do":
                custom_values[param] = st.number_input(
                    label, min_value=0.0, max_value=3.0, value=float(default_val), step=0.05, key="val_%s" % param
                )
            elif param == "srt":
                custom_values[param] = st.number_input(
                    label, min_value=1.0, value=float(default_val), step=0.5, key="val_%s" % param
                )
            else:
                custom_values[param] = st.number_input(
                    label, min_value=0.0, value=float(default_val), step=1.0, key="val_%s" % param
                )
        else:
            custom_values[param] = default_val
            st.markdown("**%s:** %.2f — *%s*" % (label, default_val, ref))

notes = st.text_area("Notes", value=st.session_state.get("lab_notes", ""))

run_analysis = st.button("Run performance analysis", type="primary")
run_save = st.button("Run analysis and save to history")

if run_analysis or run_save:
    st.session_state["lab_notes"] = notes
    table = st.session_state[LAB_TABLE]
    result = analyze_multi_column(table, selected_columns, stage=stage)

    st.subheader("Summary table")
    display_values = result.values_df.drop(columns=["param_key"], errors="ignore")
    st.dataframe(display_values, use_container_width=True, hide_index=True)

    if not result.differences_df.empty:
        st.subheader("Differences")
        st.dataframe(
            result.differences_df.pivot_table(
                index="Parameter",
                columns="Comparison",
                values="Difference",
            ).round(3),
            use_container_width=True,
        )

    if result.indicators:
        st.subheader("Process indicators (Entrance → Reactor)")
        st.dataframe(pd.DataFrame([result.indicators]).round(3), use_container_width=True, hide_index=True)

    if not result.efficiency_df.empty:
        st.subheader("Removal efficiency (Entrance → Reactor)")
        st.caption("Efficiency (%) = (Entrance − Reactor) / Entrance × 100; TIN = NH₄ + NO₂ + NO₃")
        eff_display = result.efficiency_df.drop(columns=["param_key"], errors="ignore")
        st.dataframe(eff_display, use_container_width=True, hide_index=True)

    if not result.ratio_df.empty:
        st.subheader("NO2/NH4 — anammox feed check")
        st.caption("Ideal anammox FEED ratio = 1.32 (Strous et al. 1998). Not meaningful inside a one-stage PN/A reactor.")
        ratio_display = result.ratio_df.drop(columns=["column_key"], errors="ignore")
        st.dataframe(ratio_display, use_container_width=True, hide_index=True)

    st.subheader("Alerts")
    for alert in result.alerts:
        if alert.level == "warning":
            st.warning(alert.message)
        elif alert.level == "danger":
            st.error(alert.message)
        else:
            st.success(alert.message)

    st.subheader("Charts")
    apply_matplotlib_theme()
    c1, c2 = st.columns(2)
    with c1:
        fig1 = plot_comparison_bars(result)
        st.pyplot(fig1)
        plt.close(fig1)
    with c2:
        fig2 = plot_efficiency_bars(result.efficiency_df)
        if fig2:
            st.pyplot(fig2)
            plt.close(fig2)
        else:
            st.info("Efficiency chart requires Entrance and Reactor columns.")

    fig3 = plot_ratio_comparison(result.ratio_df)
    if fig3:
        st.pyplot(fig3)
        plt.close(fig3)

    if run_save:
        if "reactor" not in selected_columns or "entrance" not in selected_columns:
            st.error("Saving to history requires the Entrance and Reactor columns (influent + initial state).")
        else:
            table_json = table_to_json(table)
            columns_json = selected_columns_to_json(selected_columns)
            reactor_inputs = build_simulation_inputs(
                table, "reactor", stage, use_custom, custom_values
            )

            entrance_vals = extract_column(table, "entrance")
            entrance_nh4 = entrance_vals["nh4"]
            if stage == "pna":
                pna_cfg = ReactorConfig(
                    nh4=reactor_inputs.nh4, no2=reactor_inputs.no2, no3=reactor_inputs.no3,
                    nh4_in=entrance_vals["nh4"], no2_in=entrance_vals["no2"], no3_in=entrance_vals["no3"],
                    hrt_d=hrt_h / 24.0 if hrt_h > 0 else None,
                    ph=reactor_inputs.ph, temperature=reactor_inputs.temperature, do=reactor_inputs.do,
                    x_amx=reactor_inputs.biomass, srt_amx=reactor_inputs.srt, days=30, dt_min=10.0,
                )
                df = simulate_pna(pna_cfg)
                df = df[df["Day"] >= 1].reset_index(drop=True)
                df["Day"] = df["Day"].round().astype(int)
                df["Biomass"] = df["AMX"]
                df["Stability"] = (df["TIN_removal_pct"] / 100.0 / PNA_MAX_TN_REMOVAL).clip(0, 1)
                final = df.iloc[-1]
                diag = interpret_daily_reading(
                    reactor_inputs.nh4, reactor_inputs.no2, reactor_inputs.no3,
                    entrance_vals["nh4"], entrance_vals["no2"], entrance_vals["no3"], stage="pna",
                )
                alert_text = " | ".join(a.message for a in result.alerts)
                save_lab_reading(
                    user_id=st.session_state["user_id"], stage="pna",
                    nh4=reactor_inputs.nh4, no2=reactor_inputs.no2, no3=reactor_inputs.no3,
                    ph=reactor_inputs.ph, temperature=reactor_inputs.temperature, do=reactor_inputs.do,
                    srt=reactor_inputs.srt, notes=notes, status=diag.status, findings=alert_text,
                )
                exp_config = ExperimentConfig(
                    nh4=reactor_inputs.nh4, no2=reactor_inputs.no2, no3=reactor_inputs.no3, hco3=0.0,
                    ph=reactor_inputs.ph, temperature=reactor_inputs.temperature, do=reactor_inputs.do,
                    x_anammox=reactor_inputs.biomass, srt=reactor_inputs.srt,
                )
                experiment_id = save_experiment(
                    user_id=st.session_state["user_id"], config=exp_config,
                    final_nh4=float(final["NH4"]), final_no2=float(final["NO2"]), final_no3=float(final["NO3"]),
                    final_biomass=float(final["AMX"]), stability=float(final["Stability"]), stage="pna",
                    initial_no3=reactor_inputs.no3, notes=notes,
                    lab_table_json=table_json, sim_sources_json=columns_json,
                )
                save_timeseries(experiment_id, df)
            elif stage == "pn":
                pn_config = PNConfig(
                    nh4=reactor_inputs.nh4,
                    no2=reactor_inputs.no2,
                    no3=reactor_inputs.no3,
                    ph=reactor_inputs.ph,
                    temperature=reactor_inputs.temperature,
                    do=reactor_inputs.do,
                    srt=reactor_inputs.srt,
                    x_aob=reactor_inputs.biomass,
                    influent_nh4=entrance_nh4 if hrt_h > 0 else 0.0,
                    hrt_days=hrt_h / 24.0,
                )
                df = simulate_pn_30_days(pn_config)
                final = df.iloc[-1]
                diag = interpret_daily_reading(
                    reactor_inputs.nh4, reactor_inputs.no2, reactor_inputs.no3, stage="pn"
                )
                alert_text = " | ".join(a.message for a in result.alerts)

                save_lab_reading(
                    user_id=st.session_state["user_id"],
                    stage="pn",
                    nh4=reactor_inputs.nh4,
                    no2=reactor_inputs.no2,
                    no3=reactor_inputs.no3,
                    ph=reactor_inputs.ph,
                    temperature=reactor_inputs.temperature,
                    do=reactor_inputs.do,
                    srt=reactor_inputs.srt,
                    notes=notes,
                    status=diag.status,
                    findings=alert_text,
                )

                exp_config = ExperimentConfig(
                    nh4=reactor_inputs.nh4,
                    no2=reactor_inputs.no2,
                    no3=reactor_inputs.no3,
                    ph=reactor_inputs.ph,
                    temperature=reactor_inputs.temperature,
                    do=reactor_inputs.do,
                    srt=reactor_inputs.srt,
                    x_anammox=reactor_inputs.biomass,
                )
                experiment_id = save_experiment(
                    user_id=st.session_state["user_id"],
                    config=exp_config,
                    final_nh4=float(final["NH4"]),
                    final_no2=float(final["NO2"]),
                    final_no3=float(final["NO3"]),
                    final_biomass=float(final["AOB"]),
                    stability=float(final["NAR"]),
                    stage="pn",
                    initial_no3=reactor_inputs.no3,
                    notes=notes,
                    lab_table_json=table_json,
                    sim_sources_json=columns_json,
                )
                save_timeseries(experiment_id, df.rename(columns={"AOB": "Biomass", "NAR": "Stability"}))
            else:
                an_config = ExperimentConfig(
                    hrt_d=hrt_h / 24.0 if hrt_h > 0 else None,
                    nh4_in=entrance_vals["nh4"],
                    no2_in=entrance_vals["no2"],
                    no3_in=entrance_vals["no3"],
                    nh4=reactor_inputs.nh4,
                    no2=reactor_inputs.no2,
                    no3=reactor_inputs.no3,
                    hco3=reactor_inputs.hco3,
                    ph=reactor_inputs.ph,
                    temperature=reactor_inputs.temperature,
                    do=reactor_inputs.do,
                    x_anammox=reactor_inputs.biomass,
                    srt=reactor_inputs.srt,
                )
                df = simulate_30_days(an_config)
                final = df.iloc[-1]
                diag = interpret_daily_reading(
                    reactor_inputs.nh4, reactor_inputs.no2, reactor_inputs.no3, stage="anammox"
                )
                alert_text = " | ".join(a.message for a in result.alerts)

                save_lab_reading(
                    user_id=st.session_state["user_id"],
                    stage="anammox",
                    nh4=reactor_inputs.nh4,
                    no2=reactor_inputs.no2,
                    no3=reactor_inputs.no3,
                    ph=reactor_inputs.ph,
                    temperature=reactor_inputs.temperature,
                    do=reactor_inputs.do,
                    srt=reactor_inputs.srt,
                    hco3=reactor_inputs.hco3,
                    notes=notes,
                    status=diag.status,
                    findings=alert_text,
                )

                experiment_id = save_experiment(
                    user_id=st.session_state["user_id"],
                    config=an_config,
                    final_nh4=float(final["NH4"]),
                    final_no2=float(final["NO2"]),
                    final_no3=float(final["NO3"]),
                    final_biomass=float(final["Biomass"]),
                    stability=float(final["Stability"]),
                    stage="anammox",
                    initial_no3=reactor_inputs.no3,
                    notes=notes,
                    lab_table_json=table_json,
                    sim_sources_json=columns_json,
                )
                save_timeseries(experiment_id, df)

            st.success("Saved as Experiment #%d" % experiment_id)

            st.subheader("30-day kinetic forecast (Reactor column)")
            apply_matplotlib_theme()
            st.line_chart(df.set_index("Day")[["NH4", "NO2", "NO3"]])
            st.caption("Uncalibrated model forecast — compare with your measurements before using it. "
                       "Stability column = TIN removal / theoretical maximum (PN/A, anammox) or NAR (PN).")

render_sidebar_footer()
