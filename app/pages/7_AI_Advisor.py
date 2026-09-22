import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd

from core.ui.layout import render_app_chrome, render_sidebar_footer, setup_page_config

setup_page_config("AI Advisor")

if st.session_state.get("user_id") is None:
    st.switch_page("Home.py")
    st.stop()

import core.database as db
from core.experiment_analysis import analyze_experiment
from core.experiment_selector import select_user_experiment
from core.lab_table import table_from_json, table_to_dataframe

render_app_chrome("advisor")

st.title("AI Reactor Advisor")
st.markdown(
    "Select **one saved experiment** and receive scientific advice for that run only."
)

exp_id, row = select_user_experiment("advisor_experiment")

if exp_id is None:
    st.stop()

st.divider()

timeseries = db.get_experiment_timeseries(exp_id)
analysis = analyze_experiment(row, timeseries if not timeseries.empty else None)

if analysis.status == "ok":
    st.success(analysis.summary)
elif analysis.status == "warning":
    st.warning(analysis.summary)
else:
    st.error(analysis.summary)

st.subheader("Saved notebook table")
lab_table = table_from_json(row.get("lab_table_json"))
st.dataframe(
    table_to_dataframe(lab_table)[["Parameter", "Distilled water", "Entrance water", "Reactor"]],
    use_container_width=True,
)

c1, c2, c3 = st.columns(3)
c1.metric("Initial NH4", "%.2f mg/L" % analysis.metrics["initial_nh4"])
c2.metric("Initial NO2", "%.2f mg/L" % analysis.metrics["initial_no2"])
c3.metric("Initial NO3", "%.2f mg/L" % analysis.metrics["initial_no3"])

st.subheader("Findings")
for item in analysis.findings:
    st.write("-", item)

st.subheader("Recommendations")
for rec in analysis.recommendations:
    st.write(">", rec)

if not timeseries.empty:
    st.subheader("Simulation trend (this experiment only)")
    st.line_chart(timeseries.set_index("day")[["nh4", "no2", "no3"]])

render_sidebar_footer()
    