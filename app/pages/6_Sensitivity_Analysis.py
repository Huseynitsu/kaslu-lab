"""One-at-a-time sensitivity of the one-stage PN/A model."""

import numpy as np
import pandas as pd
import streamlit as st

from core.ui.page_init import bootstrap_page, finish_page

bootstrap_page(__file__, "sensitivity", "Sensitivity Analysis")

from core.pna_model import ReactorConfig, simulate  # noqa: E402

st.title("Sensitivity analysis — one-stage PN/A")
st.caption("Vary one operating variable, keep the others at the base case (uncalibrated model).")

PARAMS = {
    "DO (mg/L)": ("do", np.linspace(0.05, 1.0, 12)),
    "Temperature (°C)": ("temperature", np.linspace(12, 38, 12)),
    "pH": ("ph", np.linspace(6.8, 8.6, 12)),
    "HRT (h)": ("hrt_d", np.linspace(6, 48, 12) / 24.0),
    "Influent NH₄ (mg/L)": ("nh4_in", np.linspace(50, 800, 12)),
    "Floc SRT (d)": ("srt_floc", np.linspace(2, 40, 12)),
    "Anammox SRT (d)": ("srt_amx", np.linspace(10, 120, 12)),
    "Anammox biomass (mg VSS/L)": ("x_amx", np.linspace(200, 4000, 12)),
}
label = st.selectbox("Parameter", list(PARAMS))
days = st.slider("Horizon (d)", 20, 150, 60, 10)
field, values = PARAMS[label]

if st.button("Run", type="primary"):
    with st.spinner("Simulating 12 cases…"):
        runs = simulate(ReactorConfig(days=days, dt_min=15.0), overrides={field: values}, record_every_d=5.0)
    shown = values * 24.0 if field == "hrt_d" else values
    res = pd.DataFrame({
        label: shown,
        "TIN removal (%)": [r.iloc[-1]["TIN_removal_pct"] for r in runs],
        "ΔNO3/ΔNH4": [r.iloc[-1]["dNO3_dNH4"] for r in runs],
        "Effluent NO2 (mg N/L)": [r.iloc[-1]["NO2"] for r in runs],
        "NOB (mg VSS/L)": [r.iloc[-1]["NOB"] for r in runs],
    })
    st.line_chart(res.set_index(label)[["TIN removal (%)"]])
    st.line_chart(res.set_index(label)[["ΔNO3/ΔNH4"]])
    st.line_chart(res.set_index(label)[["Effluent NO2 (mg N/L)"]])
    st.dataframe(res.round(3), use_container_width=True, hide_index=True)

finish_page()
