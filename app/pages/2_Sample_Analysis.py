import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from core.ui.layout import render_app_chrome, render_sidebar_footer, setup_page_config

setup_page_config("Sample Analysis")

if st.session_state.get("user_id") is None:
    st.switch_page("Home.py")
    st.stop()

from core.dilution import calculate_dilution, suggest_dilution_factor
from core.lab_state import LAB_TABLE, init_lab_state
from core.lab_table import dataframe_to_table, notebook_editor_column_config, table_to_dataframe

init_lab_state()
render_app_chrome("sample")

st.title("Sample Analysis — Dilution")
st.markdown(
    "Edit the notebook table directly, or use the calculator to write a value into one cell."
)

st.subheader("Laboratory notebook")
edited_df = st.data_editor(
    table_to_dataframe(st.session_state[LAB_TABLE]),
    column_config=notebook_editor_column_config(),
    hide_index=True,
    use_container_width=True,
)
st.session_state[LAB_TABLE] = dataframe_to_table(edited_df)

st.divider()
st.subheader("Spectrophotometer helper")

PARAM_MAP = {"NH4-N": "nh4", "NO2-N": "no2", "NO3-N": "no3"}
COL_MAP = {"Reactor": "reactor", "Entrance water": "entrance", "Distilled water": "distilled"}

c1, c2 = st.columns(2)
with c1:
    param_label = st.selectbox("Analyte", list(PARAM_MAP.keys()))
    absorbance = st.number_input("Absorbance", 0.0, 3.0, 1.2, 0.01)
    slope = st.number_input("Slope (mg/L per A)", min_value=0.01, value=10.0, step=0.1)
with c2:
    dilution_factor = st.number_input(
        "Dilution factor",
        min_value=1.0,
        value=float(suggest_dilution_factor(absorbance)),
    )
    target_col = st.selectbox("Write to column", list(COL_MAP.keys()))

if st.button("Calculate and write", type="primary"):
    result = calculate_dilution(absorbance, slope, dilution_factor=dilution_factor)
    key = PARAM_MAP[param_label]
    col = COL_MAP[target_col]
    st.session_state[LAB_TABLE][key][col] = result.true_concentration_mg_l
    st.success("Wrote %.2f mg/L to %s / %s" % (result.true_concentration_mg_l, param_label, target_col))
    if not result.in_linear_range:
        st.warning(result.recommendation)

render_sidebar_footer()
