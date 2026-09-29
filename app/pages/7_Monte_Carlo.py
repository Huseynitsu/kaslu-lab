import numpy as np
import pandas as pd
import streamlit as st

from core.ui.page_init import bootstrap_page, finish_page

bootstrap_page(__file__, "monte_carlo", "Monte Carlo Analysis")

from core.pna_model import ReactorConfig, simulate  # noqa: E402

st.title("Monte Carlo risk analysis — one-stage PN/A")
st.caption("Propagates uncertainty in operating conditions through the uncalibrated mechanistic model.")

c1, c2, c3 = st.columns(3)
n_runs = c1.slider("Number of simulations", 50, 500, 200, 50)
days = c2.slider("Horizon (d)", 20, 120, 60, 10)
seed = c3.number_input("Random seed", 0, 10_000, 42)
c1, c2, c3 = st.columns(3)
do_mu = c1.number_input("DO mean (mg/L)", 0.05, 2.0, 0.3, 0.05)
do_sd = c1.number_input("DO std", 0.0, 1.0, 0.1, 0.01)
t_mu = c2.number_input("T mean (°C)", 10.0, 40.0, 30.0, 0.5)
t_sd = c2.number_input("T std", 0.0, 10.0, 2.0, 0.5)
nh4_mu = c3.number_input("Influent NH₄ mean (mg/L)", 10.0, 2000.0, 200.0, 10.0)
nh4_sd = c3.number_input("Influent NH₄ std", 0.0, 500.0, 20.0, 5.0)
ph_mu, ph_sd = 7.6, 0.2

if st.button("Run Monte Carlo", type="primary"):
    rng = np.random.default_rng(int(seed))
    samples = {
        "do": np.clip(rng.normal(do_mu, do_sd, n_runs), 0.0, None),          # DO cannot be negative
        "temperature": np.clip(rng.normal(t_mu, t_sd, n_runs), 5.0, 45.0),
        "nh4_in": np.clip(rng.normal(nh4_mu, nh4_sd, n_runs), 1.0, None),
        "ph": np.clip(rng.normal(ph_mu, ph_sd, n_runs), 6.0, 9.0),
    }
    with st.spinner("Simulating…"):
        runs = simulate(ReactorConfig(days=days, dt_min=15.0), overrides=samples, record_every_d=5.0)
    rows = []
    for i, df in enumerate(runs):
        last = df.iloc[-1]
        rows.append({
            "DO": samples["do"][i], "T": samples["temperature"][i], "NH4_in": samples["nh4_in"][i], "pH": samples["ph"][i],
            "TIN removal (%)": last["TIN_removal_pct"], "ΔNO3/ΔNH4": last["dNO3_dNH4"], "NO2 out": last["NO2"],
        })
    res = pd.DataFrame(rows)
    res["Success"] = (res["TIN removal (%)"] >= 75) & (res["NO2 out"] < 20) & (res["ΔNO3/ΔNH4"] < 0.15)
    c1, c2, c3 = st.columns(3)
    c1.metric("Success rate", f"{res['Success'].mean():.0%}", help="TIN ≥ 75 %, NO₂ < 20 mg N/L, ΔNO₃/ΔNH₄ < 0.15")
    c2.metric("Median TIN removal", f"{res['TIN removal (%)'].median():.1f} %")
    c3.metric("P10 TIN removal", f"{res['TIN removal (%)'].quantile(0.1):.1f} %")
    st.subheader("Which input drives failure? (Spearman correlation with TIN removal)")
    corr = res[["DO", "T", "NH4_in", "pH", "TIN removal (%)"]].corr(method="spearman")["TIN removal (%)"].drop("TIN removal (%)")
    st.bar_chart(corr)
    st.subheader("TIN removal vs DO")
    st.scatter_chart(res, x="DO", y="TIN removal (%)", color="Success")
    st.dataframe(res.round(3), use_container_width=True, hide_index=True)

finish_page()
