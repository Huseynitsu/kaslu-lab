import streamlit as st

from core.optimization import optimize_reactor
from core.ui.page_init import bootstrap_page, finish_page

bootstrap_page(__file__, "optimization", "Reactor Optimization")

st.title("Reactor Optimization")
st.caption("Grid search demo — not a production optimizer.")

st.markdown("Search for optimal reactor conditions based on the mechanistic Anammox model.")

if st.button("Run Optimization", type="primary"):
    with st.spinner("Searching best conditions..."):
        result = optimize_reactor()

    st.success("Optimization completed.")
    st.subheader("Optimal Parameters")
    st.json(result)

finish_page()
