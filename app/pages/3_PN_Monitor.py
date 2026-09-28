import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from core.ui.layout import render_app_chrome, render_sidebar_footer, render_sidebar_navigation, setup_page_config
from core.ui.navigation import switch_to

setup_page_config("PN Monitor")

if st.session_state.get("user_id") is None:
    switch_to("Home.py")
    st.stop()

from core.pn_control import assess_pn_operation
from core.pn_config import PNConfig
from core.pn_simulation import simulate_pn_30_days

render_app_chrome("pn", defer_nav=True)

with st.sidebar:
    st.markdown("**Reactor parameters**")
    do = st.slider("DO (mg/L)", 0.0, 3.0, 0.8, 0.1)
    temperature = st.slider("Temperature (°C)", 15.0, 45.0, 35.0, 0.5)
    ph = st.slider("pH", 6.5, 9.0, 7.8, 0.1)
    srt = st.slider("SRT (days)", 1.0, 15.0, 4.0, 0.5)
    continuous = st.checkbox("Continuous flow (CSTR)", value=False)
    influent_nh4 = (
        st.slider("Daily influent NH₄ (mg/L)", 0.0, 200.0, 100.0, 5.0)
        if continuous else 0.0
    )
    hrt = st.slider("HRT (days)", 0.5, 5.0, 2.0, 0.5) if continuous else 0.0
    st.markdown("**Current concentrations**")
    nh4 = st.number_input("NH₄ (mg/L)", value=50.0, min_value=0.0)
    no2 = st.number_input("NO₂ (mg/L)", value=30.0, min_value=0.0)

render_sidebar_navigation("pn")

render_sidebar_footer()

st.title("Partial Nitritation (PN) Monitor")
st.caption("Stage 1: enrich AOB, suppress NOB — article Table 1")

if st.button("Assess NOB risk", type="primary"):
    assessment = assess_pn_operation(
        do_mg_l=do,
        temperature_c=temperature,
        ph=ph,
        srt_days=srt,
        nh4_mg_l=nh4,
        no2_mg_l=no2,
    )

    c1, c2, c3 = st.columns(3)
    risk_color = {"low": "🟢", "medium": "🟡", "high": "🔴"}
    c1.metric("NOB risk", f"{risk_color.get(assessment.nob_risk, '')} {assessment.nob_risk.upper()}")
    c2.metric("AOB advantage", assessment.aob_favorability.upper())
    c3.metric("Overall status", assessment.overall_status.upper())

    st.subheader("Parameter checks")
    for check in assessment.checks:
        icon = {"ok": "✅", "warning": "⚠️", "danger": "❌"}.get(check.status, "•")
        st.write(f"{icon} **{check.name}:** {check.value:.3f} {check.unit} — {check.message}")
        st.caption(f"Optimal: {check.optimal_range}")

    st.subheader("Recommendations")
    for rec in assessment.recommendations:
        st.write("•", rec)

st.divider()
st.subheader("30-day PN simulation")

if st.button("Run simulation"):
    config = PNConfig(
        nh4=50.0,
        ph=ph,
        temperature=temperature,
        do=do,
        srt=srt,
        influent_nh4=influent_nh4 if continuous else 0.0,
        hrt_days=hrt if continuous else 0.0,
    )

    df = simulate_pn_30_days(config)

    st.line_chart(df.set_index("Day")[["NH4", "NO2", "NO3"]])
    st.line_chart(df.set_index("Day")[["AOB", "NOB"]])

    final = df.iloc[-1]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Final NH₄", f"{final['NH4']:.1f}")
    m2.metric("Final NO₂", f"{final['NO2']:.1f}")
    m3.metric("Final NO₃", f"{final['NO3']:.1f}")
    m4.metric("NAR", f"{final['NAR']:.2f}")

    st.dataframe(df.tail(10))
