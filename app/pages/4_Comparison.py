import pandas as pd
import streamlit as st

import core.database as db
from core.ui.page_init import bootstrap_page, finish_page

bootstrap_page(__file__, "comparison", "Experiment Comparison")

st.title("Experiment Comparison")

experiment_ids = db.get_all_experiment_ids(user_id=st.session_state.get("user_id"))

if len(experiment_ids) < 2:
    st.warning("At least 2 experiments are required.")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    exp1 = st.selectbox("Experiment A", experiment_ids, key="exp1")
with col2:
    exp2 = st.selectbox(
        "Experiment B",
        experiment_ids,
        index=min(1, len(experiment_ids) - 1),
        key="exp2",
    )

df1 = db.get_experiment_by_id(exp1)
df2 = db.get_experiment_by_id(exp2)

if df1.empty or df2.empty:
    st.error("Experiment data not found.")
    st.stop()

row1 = df1.iloc[0]
row2 = df2.iloc[0]

comparison = pd.DataFrame({
    "Metric": ["Final NH4", "Final NO2", "Final NO3", "Final Biomass", "Stability"],
    f"Experiment {exp1}": [
        row1["final_nh4"],
        row1["final_no2"],
        row1["final_no3"],
        row1["final_biomass"],
        row1["stability"],
    ],
    f"Experiment {exp2}": [
        row2["final_nh4"],
        row2["final_no2"],
        row2["final_no3"],
        row2["final_biomass"],
        row2["stability"],
    ],
})

st.dataframe(comparison, use_container_width=True)

finish_page()
