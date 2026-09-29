import numpy as np
import streamlit as st

from core.ui.page_init import bootstrap_page, finish_page

bootstrap_page(__file__, "optimization", "Reactor Optimization")

from core.optimization import optimize_reactor  # noqa: E402
from core.pna_model import ReactorConfig  # noqa: E402

st.title("Operating-point search — one-stage PN/A")
st.caption("Grid search on the UNCALIBRATED mechanistic model. Use it to explore trade-offs, not as a set-point to apply directly.")

c1, c2, c3 = st.columns(3)
nh4_in = c1.number_input("Influent NH₄-N (mg/L)", 10.0, 2000.0, 200.0, 10.0)
temperature = c2.slider("Temperature (°C)", 10.0, 40.0, 30.0, 0.5)
ph = c3.slider("pH", 6.5, 8.8, 7.6, 0.1)
c1, c2, c3 = st.columns(3)
x_amx = c1.number_input("Anammox biomass (mg VSS/L)", 50.0, 10000.0, 1500.0, 50.0)
srt_floc = c2.number_input("Floc SRT (d)", 1.0, 100.0, 10.0, 1.0)
days = c3.slider("Horizon (d)", 20, 150, 60, 10)
no2_limit = c1.number_input("Max effluent NO₂ (mg N/L)", 1.0, 100.0, 20.0, 1.0)
ratio_limit = c2.number_input("Max ΔNO₃/ΔNH₄", 0.08, 1.0, 0.15, 0.01)
min_tin = c3.number_input("Min TIN removal (%)", 10.0, 89.0, 80.0, 1.0)
st.caption("Objective: highest nitrogen removal rate (NRR) meeting all constraints; ties → lowest DO (aeration energy).")

if st.button("Run grid search", type="primary"):
    base = ReactorConfig(nh4=nh4_in * 0.1, nh4_in=nh4_in, temperature=temperature, ph=ph,
                         x_amx=x_amx, srt_floc=srt_floc)
    with st.spinner("Simulating 35 operating points…"):
        res = optimize_reactor(base, days=days, no2_limit=no2_limit, ratio_limit=ratio_limit,
                              min_tin_removal=min_tin)
    if res["feasible"]:
        st.success("Best feasible operating point")
    else:
        st.warning("No grid point met all constraints — showing the best TIN removal.")
    st.json({k: (round(v, 3) if isinstance(v, (float, np.floating)) else v) for k, v in res["best"].items()})
    grid = res["grid"]
    st.subheader("TIN removal (%) — DO × HRT")
    st.dataframe(grid.pivot_table(index="DO (mg/L)", columns="HRT (h)", values="TIN removal (%)").round(1),
                 use_container_width=True)
    st.subheader("All grid points")
    st.dataframe(grid.round(3), use_container_width=True, hide_index=True)

finish_page()
