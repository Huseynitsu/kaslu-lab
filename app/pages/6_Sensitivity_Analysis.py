import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
import numpy as np

from core.ui.layout import render_app_chrome, render_sidebar_footer, setup_page_config
from core.ui.navigation import switch_to

setup_page_config("Sensitivity Analysis")

if st.session_state.get("user_id") is None:
    switch_to("Home.py")
    st.stop()

from core.config import ExperimentConfig
from core.experiment_selector import select_user_experiment
from core.simulation import simulate_30_days

render_app_chrome("sensitivity")

st.title("Sensitivity Analysis")
st.markdown("Vary one parameter around **one selected experiment** (base case).")

exp_id, row = select_user_experiment("sensitivity_experiment")

if exp_id is None:
    st.stop()

if str(row.get("stage", "anammox")) != "anammox":
    st.warning("Sensitivity module currently uses the Anammox model. Select an Anammox experiment.")
    st.stop()

BASE_CONFIG = {
    "nh4": float(row["nh4"]),
    "no2": float(row["no2"]),
    "no3": float(row.get("initial_no3", 0) or 0),
    "hco3": float(row.get("hco3", 120) or 120),
    "ph": float(row["ph"]),
    "temperature": float(row["temperature"]),
    "do": float(row["do"]),
    "x_anammox": float(row["biomass"]),
    "srt": float(row["srt"]),
}

st.info(
    "Base case from experiment #%d: NH4=%.1f, NO2=%.1f, DO=%.2f"
    % (exp_id, BASE_CONFIG["nh4"], BASE_CONFIG["no2"], BASE_CONFIG["do"])
)

parameter = st.selectbox("Parameter to vary", ["NH4", "NO2", "pH", "Temperature", "DO", "Biomass", "SRT"])

ranges = {
    "NH4": np.linspace(max(1, BASE_CONFIG["nh4"] * 0.5), BASE_CONFIG["nh4"] * 1.5, 15),
    "NO2": np.linspace(max(1, BASE_CONFIG["no2"] * 0.5), BASE_CONFIG["no2"] * 1.5, 15),
    "pH": np.linspace(6.5, 8.5, 15),
    "Temperature": np.linspace(25, 40, 15),
    "DO": np.linspace(0.0, 0.5, 15),
    "Biomass": np.linspace(max(100, BASE_CONFIG["x_anammox"] * 0.5), BASE_CONFIG["x_anammox"] * 1.5, 15),
    "SRT": np.linspace(max(5, BASE_CONFIG["srt"] * 0.5), BASE_CONFIG["srt"] * 1.5, 15),
}
values = ranges[parameter]

results = []
for value in values:
    cfg = dict(BASE_CONFIG)
    key_map = {
        "NH4": "nh4", "NO2": "no2", "pH": "ph", "Temperature": "temperature",
        "DO": "do", "Biomass": "x_anammox", "SRT": "srt",
    }
    cfg[key_map[parameter]] = float(value)
    config = ExperimentConfig(**cfg)
    df = simulate_30_days(config)
    final = df.iloc[-1]
    results.append({
        "Value": float(value),
        "Final NO3": float(final["NO3"]),
        "Stability": float(final["Stability"]),
    })

results_df = pd.DataFrame(results)
st.line_chart(results_df.set_index("Value")[["Final NO3", "Stability"]])
st.dataframe(results_df, use_container_width=True)

render_sidebar_footer()
