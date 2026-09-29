import streamlit as st
from core.config import ExperimentConfig
from core.simulation import simulate_30_days

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

st.set_page_config(
    page_title="Anammox Lab System",
    layout="wide"
)

st.title("🧪 Anammox Hybrid Reactor Dashboard")

st.markdown("""
Legacy single-page demo (anammox batch). The maintained app is app/Home.py.
""")

# Sidebar
st.sidebar.header("Reactor Parameters")

nh4 = st.sidebar.slider("NH4 (mg/L)", 0, 200, 50)
no2 = st.sidebar.slider("NO2 (mg/L)", 0, 200, 66)
ph = st.sidebar.slider("pH", 5.0, 9.0, 7.8)
temperature = st.sidebar.slider("Temperature (°C)", 10, 45, 35)
do = st.sidebar.slider("DO (mg/L)", 0.0, 1.0, 0.05)
x_anammox = st.sidebar.slider("Biomass", 100, 2000, 800)
srt = st.sidebar.slider("SRT (days)", 1, 40, 20)

# Run button
if st.button("▶ Run Simulation"):

    config = ExperimentConfig(
        nh4=nh4,
        no2=no2,
        ph=ph,
        temperature=temperature,
        do=do,
        x_anammox=x_anammox,
        srt=srt
    )

    df = simulate_30_days(config)

    # KPI CARDS
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Final NH4", f"{df['NH4'].iloc[-1]:.2f}")
    col2.metric("Final NO2", f"{df['NO2'].iloc[-1]:.2f}")
    col3.metric("NO3 Produced", f"{df['NO3'].iloc[-1]:.2f}")
    col4.metric("Biomass", f"{df['Biomass'].iloc[-1]:.2f}")

    st.divider()

    # CHARTS
    st.subheader("📈 Concentration Dynamics")

    st.line_chart(df.set_index("Day")[["NH4", "NO2", "NO3"]])

    st.subheader("🧬 Biomass Growth")

    st.line_chart(df.set_index("Day")["Biomass"])

    st.subheader("📊 Raw Data")
    st.dataframe(df)
