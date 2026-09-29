"""Saved experiments and lab readings."""

import streamlit as st

from core.ui.page_init import bootstrap_page, finish_page

bootstrap_page(__file__, "history", "History")

import core.database as db  # noqa: E402

st.title("History")
st.caption("Experiments and lab readings saved from Performance Analysis. "
           "Note: on Streamlit Community Cloud the SQLite file is reset when the app restarts — "
           "export important data regularly (CSV below).")

user_id = st.session_state["user_id"]
exps = db.get_user_experiments(user_id)
readings = db.get_lab_readings(user_id, limit=500)

tab1, tab2 = st.tabs(["Experiments", "Lab readings"])
with tab1:
    if exps.empty:
        st.info("No experiments saved yet.")
    else:
        cols = [c for c in ("id", "created_at", "stage", "nh4", "no2", "no3", "ph", "temperature", "do", "srt",
                            "final_nh4", "final_no2", "final_no3", "stability", "notes") if c in exps.columns]
        view = exps[cols].rename(columns={"stability": "performance/NAR index"})
        st.dataframe(view, use_container_width=True, hide_index=True)
        st.download_button("Export experiments (CSV)", exps.to_csv(index=False).encode(), "experiments.csv", "text/csv")
        exp_id = st.selectbox("Show time series of experiment", exps["id"].tolist())
        ts = db.get_experiment_timeseries(int(exp_id))
        if not ts.empty:
            st.line_chart(ts.set_index("day")[["nh4", "no2", "no3"]])
with tab2:
    if readings.empty:
        st.info("No lab readings saved yet.")
    else:
        st.dataframe(readings, use_container_width=True, hide_index=True)
        st.download_button("Export readings (CSV)", readings.to_csv(index=False).encode(), "lab_readings.csv", "text/csv")

finish_page()
