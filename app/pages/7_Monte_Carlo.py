import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from core.config import ExperimentConfig
from core.simulation import simulate_30_days
from core.ui.page_init import bootstrap_page, finish_page
from core.ui.theme import apply_matplotlib_theme

bootstrap_page(__file__, "monte_carlo", "Monte Carlo Analysis")

st.title("Monte Carlo Risk Analysis")
st.caption("Research module — synthetic random scenarios.")

n_runs = st.slider("Number of Simulations", 100, 1000, 300, step=100)

if st.button("Run Monte Carlo", type="primary"):
    results = []
    progress = st.progress(0)

    for i in range(n_runs):
        config = ExperimentConfig(
            nh4=np.random.normal(50, 5),
            no2=np.random.normal(66, 6),
            ph=np.random.normal(7.8, 0.3),
            temperature=np.random.normal(35, 2),
            do=np.random.normal(0.8, 0.2),
            x_anammox=np.random.normal(800, 100),
            srt=np.random.normal(20, 3),
        )
        df = simulate_30_days(config)
        final_row = df.iloc[-1]
        stability = float(final_row["Stability"])
        no3 = float(final_row["NO3"])
        biomass = float(final_row["Biomass"])
        final_nh4 = float(final_row["NH4"])
        success = stability >= 0.8 and final_nh4 < 10
        results.append({
            "Final NO3": no3,
            "Final Biomass": biomass,
            "Stability": stability,
            "Success": success,
        })
        progress.progress((i + 1) / n_runs)

    results_df = pd.DataFrame(results)
    success_rate = results_df["Success"].mean() * 100
    fail_rate = 100 - success_rate

    st.subheader("Risk Summary")
    col1, col2 = st.columns(2)
    col1.metric("Success Rate (%)", round(success_rate, 2))
    col2.metric("Failure Rate (%)", round(fail_rate, 2))

    st.subheader("Stability Distribution")
    st.bar_chart(results_df["Stability"])
    st.subheader("NO3 Distribution")
    st.bar_chart(results_df["Final NO3"])
    st.subheader("Simulation Results")
    st.dataframe(results_df, use_container_width=True)

    apply_matplotlib_theme()
    fig, ax = plt.subplots()
    ax.hist(results_df["Stability"], bins=20)
    st.pyplot(fig)
    plt.close(fig)

    st.metric("Mean Stability", round(results_df["Stability"].mean(), 3))
    st.metric("Worst Stability", round(results_df["Stability"].min(), 3))
    st.metric("Best Stability", round(results_df["Stability"].max(), 3))

finish_page()
