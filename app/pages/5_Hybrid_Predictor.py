"""PN/A digital twin: mechanistic model + closed-loop controller test."""

from dataclasses import replace

import pandas as pd
import streamlit as st

from core.ui.page_init import bootstrap_page, finish_page

bootstrap_page(__file__, "twin", "PN/A Digital Twin")

from core.constants import PNA_MAX_TN_REMOVAL, PNA_NO3_PER_NH4_REMOVED  # noqa: E402
from core.pna_model import KineticParameters, ReactorConfig, simulate  # noqa: E402
from core.self_control import closed_loop_test  # noqa: E402

st.title("PN/A Digital Twin — one-stage reactor model")
st.warning(
    "Mechanistic model with **literature default parameters** (Hao et al. 2002; Strous et al. 1998; "
    "Anthonisen et al. 1976). It is not calibrated to your reactor — use it for scenario and controller "
    "testing, and calibrate μmax, K_O and SRT with your own data before drawing quantitative conclusions."
)

with st.sidebar:
    st.markdown("**Influent & hydraulics**")
    nh4_in = st.number_input("Influent NH₄-N (mg/L)", 10.0, 2000.0, 200.0, 10.0)
    hrt_h = st.number_input("HRT (h)", 1.0, 240.0, 24.0, 1.0)
    st.markdown("**Environment**")
    temperature = st.slider("Temperature (°C)", 10.0, 40.0, 30.0, 0.5)
    ph = st.slider("pH", 6.5, 8.8, 7.6, 0.1)
    do = st.slider("DO set-point (mg/L)", 0.0, 2.0, 0.3, 0.05)
    af = st.slider("Aerobic fraction (intermittent aeration)", 0.1, 1.0, 1.0, 0.05)
    st.markdown("**Biomass & retention**")
    x_amx = st.number_input("Anammox (mg VSS/L)", 1.0, 10000.0, 1500.0, 50.0)
    x_aob = st.number_input("AOB (mg VSS/L)", 1.0, 5000.0, 300.0, 10.0)
    x_nob = st.number_input("NOB (mg VSS/L)", 0.1, 5000.0, 50.0, 5.0)
    srt_floc = st.number_input("Floc SRT — AOB/NOB (d)", 1.0, 200.0, 10.0, 1.0)
    srt_amx = st.number_input("Granule SRT — anammox (d)", 5.0, 500.0, 60.0, 5.0)
    st.markdown("**Model**")
    stoich = st.selectbox("Anammox stoichiometry", ["strous_1998", "lotti_2014"],
                          format_func=lambda s: "Strous 1998 (1.32 / 0.26)" if s == "strous_1998" else "Lotti 2014 (1.146 / 0.161)")
    ko_amx = st.number_input("Apparent anammox K_O (mg O₂/L)", 0.005, 2.0, 0.2, 0.01,
                             help="Lumps O₂ protection inside granules/biofilm. Intrinsic value ≈ 0.01 mg/L.")
    days = st.slider("Simulation days", 10, 200, 60, 5)

params = KineticParameters(stoichiometry=stoich, ko_amx=ko_amx)
cfg = ReactorConfig(
    nh4=nh4_in * 0.1, no2=0.0, no3=0.0,
    nh4_in=nh4_in, hrt_d=hrt_h / 24.0,
    ph=ph, temperature=temperature, do=do, aeration_fraction=af,
    x_aob=x_aob, x_nob=x_nob, x_amx=x_amx, srt_floc=srt_floc, srt_amx=srt_amx,
    days=days, dt_min=10.0, params=params,
)

tab1, tab2 = st.tabs(["Scenario simulation", "Controller test (closed loop)"])

with tab1:
    if st.button("Run simulation", type="primary"):
        with st.spinner("Integrating…"):
            df = simulate(cfg)
        last = df.iloc[-1]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TIN removal", f"{last['TIN_removal_pct']:.1f} %", help=f"Autotrophic max ≈ {PNA_MAX_TN_REMOVAL:.0%}")
        c2.metric("ΔNO₃/ΔNH₄", f"{last['dNO3_dNH4']:.3f}", help=f"Theory ≈ {PNA_NO3_PER_NH4_REMOVED:.3f}")
        c3.metric("NRR", f"{last['NRR']:.3f} kg N/m³/d")
        c4.metric("Effluent NO₂", f"{last['NO2']:.1f} mg N/L")
        st.subheader("Effluent nitrogen (mg N/L)")
        st.line_chart(df.set_index("Day")[["NH4", "NO2", "NO3"]])
        st.subheader("Biomass (mg VSS/L)")
        st.line_chart(df.set_index("Day")[["AOB", "NOB", "AMX"]])
        st.subheader("Indicators")
        st.line_chart(df.set_index("Day")[["TIN_removal_pct"]])
        st.line_chart(df.set_index("Day")[["dNO3_dNH4"]])
        st.dataframe(df.round(4), use_container_width=True)

with tab2:
    st.markdown(
        "Compares **fixed DO** (open loop) with the **expert-rule** and **PI** supervisory controllers from the "
        "Early Warning page. The controller acts once per day on noisy (3 %) effluent measurements."
    )
    if st.button("Compare strategies", type="primary"):
        results = {}
        with st.spinner("Running three closed-loop simulations…"):
            for strat in ("fixed", "rules", "pi"):
                results[strat] = closed_loop_test(replace(cfg, dt_min=15.0), strat)
        summary = []
        for strat, df in results.items():
            tail = df[df["Day"] >= df["Day"].max() - 10]
            summary.append({
                "Strategy": strat,
                "Mean TIN removal, last 10 d (%)": tail["TIN_removal_pct"].mean(),
                "Mean ΔNO3/ΔNH4, last 10 d": tail["dNO3_dNH4"].mean(),
                "Max effluent NO2 (mg N/L)": df["NO2"].max(),
                "Final NOB (mg VSS/L)": df["NOB"].iloc[-1],
                "Final DO set-point": df["DO"].iloc[-1],
            })
        st.dataframe(pd.DataFrame(summary).round(3), use_container_width=True, hide_index=True)
        tin = pd.DataFrame({k: v.set_index("Day")["TIN_removal_pct"] for k, v in results.items()})
        st.subheader("TIN removal (%)")
        st.line_chart(tin)
        dos = pd.DataFrame({k: v.set_index("Day")["DO"] for k, v in results.items()})
        st.subheader("DO set-point (mg/L)")
        st.line_chart(dos)
        st.caption("Thesis tip: repeat with different disturbances (temperature drop, load step, higher initial NOB) "
                   "and report TIN removal, NOB suppression and control effort for each strategy.")

finish_page()
