import io

import pandas as pd
import streamlit as st

import core.database as db
from core.ui.page_init import bootstrap_page, finish_page

bootstrap_page(__file__, "exp_details", "Experiment Details")

st.title("Experiment Details")

experiment_ids = db.get_all_experiment_ids(user_id=st.session_state.get("user_id"))

if len(experiment_ids) == 0:
    st.warning("No experiments found.")
    st.stop()

selected_id = st.selectbox("Select Experiment", experiment_ids)
experiment_df = db.get_experiment_by_id(selected_id)

if experiment_df.empty:
    st.error("Experiment not found.")
    st.stop()

row = experiment_df.iloc[0]

st.subheader("Experiment Parameters")
parameters = pd.DataFrame({
    "Parameter": ["NH4", "NO2", "pH", "Temperature", "DO", "Biomass", "SRT"],
    "Value": [
        row["nh4"], row["no2"], row["ph"], row["temperature"],
        row["do"], row["biomass"], row["srt"],
    ],
})
st.dataframe(parameters, use_container_width=True)

st.subheader("Final Results")
results = pd.DataFrame({
    "Metric": ["Final NH4", "Final NO2", "Final NO3", "Final Biomass", "Stability"],
    "Value": [
        row["final_nh4"], row["final_no2"], row["final_no3"],
        row["final_biomass"], row["stability"],
    ],
})
st.dataframe(results, use_container_width=True)

timeseries = db.get_experiment_timeseries(selected_id)

if timeseries.empty:
    st.warning("No timeseries data found.")
    st.stop()

st.subheader("Nitrogen Dynamics")
st.line_chart(timeseries.set_index("day")[["nh4", "no2", "no3"]])
st.subheader("Biomass")
st.line_chart(timeseries.set_index("day")["biomass"])
st.subheader("Stability")
st.line_chart(timeseries.set_index("day")["stability"])
st.subheader("Raw Timeseries Data")
st.dataframe(timeseries, use_container_width=True)

csv_data = timeseries.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name=f"experiment_{selected_id}.csv",
    mime="text/csv",
)

excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    timeseries.to_excel(writer, sheet_name="Timeseries", index=False)

st.download_button(
    label="Download Excel",
    data=excel_buffer.getvalue(),
    file_name=f"experiment_{selected_id}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

finish_page()
