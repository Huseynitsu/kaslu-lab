import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd

from core.ui.layout import render_app_chrome, render_sidebar_footer, setup_page_config
from core.ui.navigation import switch_to

setup_page_config("Experiment Analysis")

if st.session_state.get("user_id") is None:
    switch_to("Home.py")
    st.stop()

import core.database as db
from core.experiment_analysis import analyze_experiment
from core.experiment_selector import select_user_experiment
from core.lab_table import table_from_json, table_to_dataframe

render_app_chrome("analytics")

st.title("Experiment Analysis")
st.markdown("Detailed analysis for **one selected experiment** — not aggregated across all runs.")

exp_id, row = select_user_experiment("analytics_experiment")

if exp_id is None:
    st.stop()

timeseries = db.get_experiment_timeseries(exp_id)
analysis = analyze_experiment(row, timeseries if not timeseries.empty else None)

st.subheader("Experiment #%d" % exp_id)

params = pd.DataFrame({
    "Parameter": ["Stage", "NH4", "NO2", "NO3 (initial)", "pH", "DO", "SRT", "Biomass"],
    "Value": [
        str(row.get("stage", "anammox")),
        row["nh4"], row["no2"], row.get("initial_no3", 0),
        row["ph"], row["do"], row["srt"], row["biomass"],
    ],
})
st.dataframe(params, use_container_width=True)

st.subheader("Notebook data")
st.dataframe(table_to_dataframe(table_from_json(row.get("lab_table_json"))), use_container_width=True)

if not timeseries.empty:
    st.subheader("Nitrogen dynamics")
    st.line_chart(timeseries.set_index("day")[["nh4", "no2", "no3"]])
    st.subheader("Biomass / stability index")
    st.line_chart(timeseries.set_index("day")[["biomass", "stability"]])

    results = pd.DataFrame({
        "Metric": ["Final NH4", "Final NO2", "Final NO3", "Final biomass", "Stability"],
        "Value": [
            row["final_nh4"], row["final_no2"], row["final_no3"],
            row["final_biomass"], row["stability"],
        ],
    })
    st.dataframe(results, use_container_width=True)

st.subheader("Scientific findings")
for item in analysis.findings:
    st.write("-", item)

render_sidebar_footer()
