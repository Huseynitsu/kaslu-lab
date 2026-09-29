import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from core.ui.layout import render_app_chrome, render_sidebar_footer, setup_page_config
from core.ui.navigation import switch_to

setup_page_config("Sample Analysis")

if st.session_state.get("user_id") is None:
    switch_to("Home.py")
    st.stop()

import pandas as pd

from core.constants import ABSORBANCE_LINEAR_MAX
from core.dilution import calculate_dilution, fit_calibration
from core.lab_state import LAB_TABLE, init_lab_state
from core.lab_table import dataframe_to_table, notebook_editor_column_config, table_to_dataframe

init_lab_state()
render_app_chrome("sample")

st.title("Sample Analysis — calibration & dilution")
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
st.subheader("1. Calibration curve")
st.caption("A = k·C + b. Use ≥ 5 standards including zero; accept only R² ≥ 0.999 (Standard Methods QC / HJ 535).")

PARAM_MAP = {"NH4-N (Nessler, 420 nm)": "nh4", "NO2-N (NED/Griess, 540 nm)": "no2", "NO3-N (UV, A220 − 2·A275)": "no3"}
COL_MAP = {"Reactor": "reactor", "Entrance water": "entrance", "Distilled water (blank)": "distilled"}

param_label = st.selectbox("Analyte", list(PARAM_MAP.keys()))
key = PARAM_MAP[param_label]
std_key = f"calib_{key}"
if std_key not in st.session_state:
    st.session_state[std_key] = pd.DataFrame({"C (mg N/L)": [0.0, 0.2, 0.4, 0.8, 1.2, 1.6],
                                              "Absorbance": [None] * 6})
std_df = st.data_editor(st.session_state[std_key], num_rows="dynamic", use_container_width=True, key=f"ed_{std_key}")
st.session_state[std_key] = std_df
cal = fit_calibration(std_df["C (mg N/L)"], std_df["Absorbance"])
if cal.n_points >= 2 and cal.slope == cal.slope:
    c1, c2, c3 = st.columns(3)
    c1.metric("Slope k (A per mg/L)", f"{cal.slope:.4f}")
    c2.metric("Intercept b", f"{cal.intercept:.4f}")
    c3.metric("R²", f"{cal.r2:.5f}")
for m in cal.messages:
    (st.success if cal.acceptable else st.warning)(m)

st.subheader("2. Sample")
c1, c2 = st.columns(2)
with c1:
    if key == "no3":
        a220 = st.number_input("A220 (measured solution)", 0.0, 3.0, 0.45, 0.001, format="%.3f")
        a275 = st.number_input("A275 (organic-matter correction)", 0.0, 3.0, 0.02, 0.001, format="%.3f")
        absorbance = a220 - 2.0 * a275
        st.caption(f"Corrected A = A220 − 2·A275 = {absorbance:.3f}")
    else:
        absorbance = st.number_input("Absorbance of the measured (diluted) solution", 0.0, 3.0, 0.45, 0.001, format="%.3f")
    blank = st.number_input("Reagent blank absorbance", 0.0, 1.0, 0.0, 0.001, format="%.3f")
with c2:
    dilution_factor = st.number_input("Dilution factor applied BEFORE measuring (e.g. 1 mL + 49 mL = 50)", min_value=1.0, value=50.0)
    manual = st.checkbox("Enter slope manually (no standards)", value=not cal.acceptable)
    k = st.number_input("k (A per mg/L)", min_value=0.0001, value=float(cal.slope) if cal.acceptable else 0.30,
                        step=0.001, format="%.4f", disabled=not manual)
    b0 = st.number_input("b (intercept)", value=float(cal.intercept) if cal.acceptable else 0.0,
                         step=0.001, format="%.4f", disabled=not manual)
    if not manual:
        k, b0 = cal.slope, cal.intercept
    target_col = st.selectbox("Write result to column", list(COL_MAP.keys()))

result = calculate_dilution(absorbance, k, dilution_factor=dilution_factor, intercept=b0, blank_absorbance=blank)
m1, m2 = st.columns(2)
m1.metric("In cuvette", f"{result.measured_concentration_mg_l:.3f} mg N/L")
m2.metric("Original sample", f"{result.true_concentration_mg_l:.2f} mg N/L")
if result.in_linear_range:
    st.success(result.recommendation)
else:
    st.warning(result.recommendation)

if st.button("Write to notebook", type="primary", disabled=absorbance > ABSORBANCE_LINEAR_MAX):
    col = COL_MAP[target_col]
    st.session_state[LAB_TABLE][key][col] = result.true_concentration_mg_l
    st.success("Wrote %.2f mg/L to %s / %s" % (result.true_concentration_mg_l, param_label, target_col))
    st.rerun()

st.caption("Methods: NH₄-N HJ 535-2009 (Nessler) or SM 4500-NH₃ F (phenate); NO₂-N GB 7493-87 / SM 4500-NO₂⁻ B; "
           "NO₃-N HJ/T 346-2007 / SM 4500-NO₃⁻ B (UV screening). Filter 0.45 µm, analyse promptly at 4 °C.")

render_sidebar_footer()
