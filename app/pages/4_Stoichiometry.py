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

from core.constants import LOTTI_2014, STROUS_1998, pna_max_tn_removal, pna_no3_per_nh4_removed
from core.stoichiometry import check_anammox_feed, intrinsic_no3_note

render_app_chrome("stoich")

st.title("⚖️ Stoichiometry — anammox & one-stage PN/A")
eq = st.radio("Stoichiometry", ["strous_1998", "lotti_2014"], horizontal=True,
              format_func=lambda k: "Strous et al. 1998" if k == "strous_1998" else "Lotti et al. 2014")
S = STROUS_1998 if eq == "strous_1998" else LOTTI_2014
if eq == "strous_1998":
    st.markdown("`NH₄⁺ + 1.32 NO₂⁻ + 0.066 HCO₃⁻ + 0.13 H⁺ → 1.02 N₂ + 0.26 NO₃⁻ + 0.066 CH₂O₀.₅N₀.₁₅ + 2.03 H₂O`")
else:
    st.markdown("`NH₄⁺ + 1.146 NO₂⁻ + 0.071 HCO₃⁻ + 0.057 H⁺ → 0.986 N₂ + 0.161 NO₃⁻ + 0.071 CH₁.₇₄O₀.₃₁N₀.₂₀ + 2.002 H₂O`")
    st.caption("Lotti et al. (2014) Water Res. 60:1–14 — verify coefficients against the paper before citing.")
st.caption("H⁺ is CONSUMED → anammox raises pH (alkalinity is produced, not buffered). "
           "1.32 is a molar ratio (mol NO₂ per mol NH₄), not a rate.")

col1, col2 = st.columns(2)

with col1:
    nh4 = st.number_input("NH₄-N (mg/L)", value=50.0, min_value=0.0)
    no2 = st.number_input("NO₂-N (mg/L)", value=66.0, min_value=0.0)
    no3 = st.number_input("NO₃-N (mg/L)", value=0.0, min_value=0.0)

with col2:
    hco3 = st.number_input("HCO₃⁻ (mg/L)", value=120.0, min_value=0.0)
    tolerance = st.slider("Ratio tolerance (%)", 5, 30, 15)

if st.button("Check feed", type="primary"):
    result = check_anammox_feed(nh4, no2, no3, hco3, ratio_tolerance_pct=tolerance, stoichiometry=eq)

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
st.subheader("One-stage PN/A — derived ratios")
r = pna_no3_per_nh4_removed(S)
c1, c2, c3 = st.columns(3)
c1.metric("NH₄ removed per NH₄ used by anammox", f"{1 + S['no2_per_nh4']:.3f}")
c2.metric("ΔNO₃/ΔNH₄ (theory)", f"{r:.3f}")
c3.metric("Max TIN removal (autotrophic)", f"{pna_max_tn_removal(S):.1%}")
st.caption("ΔNO₃/ΔNH₄ well above this value → NOB activity; well below → heterotrophic denitrification.")

st.subheader("Reference coefficients")
st.table({
    "Component": ["NO₂⁻ / NH₄⁺", "NO₃⁻ / NH₄⁺ (anammox)", "HCO₃⁻ / NH₄⁺ (mol)", "HCO₃⁻ / NH₄-N (mg/mg)"],
    "Value": [f"{S['no2_per_nh4']}", f"{S['no3_per_nh4']}", f"{S['hco3_per_nh4']}", f"{S['hco3_per_nh4'] * 61 / 14:.3f}"],
})

render_sidebar_footer()
