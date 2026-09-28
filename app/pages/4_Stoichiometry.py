import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from core.ui.layout import render_app_chrome, render_sidebar_footer, setup_page_config
from core.ui.navigation import switch_to

setup_page_config("Stoichiometry")

if st.session_state.get("user_id") is None:
    switch_to("Home.py")
    st.stop()

from core.constants import ANAMMOX_NO2_PER_NH4, ANAMMOX_NO3_PER_NH4
from core.stoichiometry import check_anammox_feed, intrinsic_no3_note

render_app_chrome("stoich")

st.title("⚖️ Stoichiometry — Strous Equation")
st.markdown("""
**Full Anammox equation** (Strous et al., 1998):

`NH₄⁺ + 1.32 NO₂⁻ + 0.066 HCO₃⁻ → 1.02 N₂ + 0.26 NO₃⁻ + biomass + H₂O`
""")

col1, col2 = st.columns(2)

with col1:
    nh4 = st.number_input("NH₄-N (mg/L)", value=50.0, min_value=0.0)
    no2 = st.number_input("NO₂-N (mg/L)", value=66.0, min_value=0.0)
    no3 = st.number_input("NO₃-N (mg/L)", value=0.0, min_value=0.0)

with col2:
    hco3 = st.number_input("HCO₃⁻ (mg/L)", value=120.0, min_value=0.0)
    tolerance = st.slider("Ratio tolerance (%)", 5, 30, 15)

if st.button("Check feed", type="primary"):
    result = check_anammox_feed(nh4, no2, no3, hco3, ratio_tolerance_pct=tolerance)

    if result.ready_for_anammox:
        st.success("✅ Effluent is READY for the Anammox stage")
    else:
        st.warning("⚠️ Effluent is not yet optimal")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("NO₂/NH₄ ratio", f"{result.no2_nh4_ratio:.2f}", f"ideal {result.ideal_ratio:.2f}")
    m2.metric("Deviation", f"{result.ratio_deviation_pct:.1f}%")
    m3.metric("Limiting substrate", result.limiting_substrate)
    m4.metric("Expected NO₃", f"{result.expected_no3_from_anammox:.1f} mg/L")

    st.subheader("Mass balance (full reaction)")
    st.write(f"- NO₂ consumed: **{result.expected_no2_consumed:.1f}** mg/L")
    st.write(f"- HCO₃⁻ consumed: **{result.expected_hco3_consumed:.1f}** mg/L")
    st.write(f"- Intrinsic NO₃ production: **{result.expected_no3_from_anammox:.1f}** mg/L")

    st.subheader("Interpretation")
    for msg in result.messages:
        st.write("•", msg)

    st.info(intrinsic_no3_note())

st.divider()
st.subheader("Reference coefficients")
st.table({
    "Component": ["NO₂⁻ / NH₄⁺", "NO₃⁻ / NH₄⁺ (intrinsic)", "HCO₃⁻ / NH₄⁺ (mass basis)"],
    "Strous (mol)": [f"{ANAMMOX_NO2_PER_NH4}", f"{ANAMMOX_NO3_PER_NH4}", "0.066"],
    "Code (mg/L)": [f"{ANAMMOX_NO2_PER_NH4}", f"{ANAMMOX_NO3_PER_NH4}", "0.287"],
})

render_sidebar_footer()
