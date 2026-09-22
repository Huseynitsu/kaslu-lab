import streamlit as st

from core.prediction_service import predict_anammox
from core.ui.page_init import bootstrap_page, finish_page

bootstrap_page(__file__, "prediction", "Hybrid / ML Prediction")

st.title("Hybrid Anammox Prediction")
st.caption("Research prototype — trained on synthetic data, not validated for publication.")

nh4 = st.number_input("NH4-N (mg/L)", value=50.0, min_value=0.0)
no2 = st.number_input("NO2-N (mg/L)", value=66.0, min_value=0.0)
hco3 = st.number_input("HCO3- (mg/L)", value=120.0, min_value=0.0)
ph = st.number_input("pH", value=7.8, min_value=5.0, max_value=10.0)
temperature = st.number_input("Temperature (°C)", value=35.0)
do = st.number_input("DO (mg/L)", value=0.2)
srt = st.number_input("SRT (days)", value=30.0)
biomass = st.number_input("Anammox Biomass (mg VSS/L)", value=800.0)

if st.button("Predict", type="primary"):
    result = predict_anammox(
        nh4=nh4,
        no2=no2,
        hco3=hco3,
        ph=ph,
        temperature=temperature,
        do=do,
        srt=srt,
        biomass=biomass,
    )

    st.success("Prediction completed")

    col1, col2 = st.columns(2)
    col1.metric("Mechanistic NO3", round(result["mechanistic_no3"], 2))
    col2.metric("ML NO3", round(result["ml_no3"], 2))
    st.metric("Prediction Gap", round(result["prediction_gap"], 2))

    if result["stability"] == 1:
        st.success("Reactor predicted as STABLE")
    else:
        st.error("Reactor predicted as UNSTABLE")

finish_page()
