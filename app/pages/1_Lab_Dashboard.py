import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from core.i18n import t
from core.ui.components import render_module_card, render_page_header, render_section, render_workflow_strip
from core.ui.layout import render_app_chrome, render_sidebar_footer, setup_page_config
from core.ui.navigation import switch_to

setup_page_config(t("dash.title"))

if st.session_state.get("user_id") is None:
    switch_to("Home.py")
    st.stop()

from core.database import get_user_experiments, get_lab_readings

render_app_chrome("dashboard")

render_page_header(t("dash.title"), t("dash.caption"), badge="Dashboard")

render_section(t("dash.workflow"))
render_workflow_strip(
    [
        t("nav.operation_log"),
        t("nav.sample"),
        t("nav.simulation"),
        t("nav.pn"),
    ]
)

cards = [
    (t("nav.prediction"), "ΔNO₃/ΔNH₄ · EWMA · DO control", "pages/4_Prediction.py", "go_ew"),
    (t("nav.twin"), "One-stage PN/A model & controller test", "pages/5_Hybrid_Predictor.py", "go_twin"),
    (t("nav.operation_log"), "Excel · NH₄/TN · duration charts", "pages/2_Reactor_Operation_Log.py", "go_oplog"),
    (t("nav.sample"), "Dilution helper + lab notebook", "pages/2_Sample_Analysis.py", "go_analysis"),
    (t("nav.simulation"), "Compare all sample points", "pages/1_Simulation.py", "go_sim"),
    (t("nav.pn"), "NOB risk & PN checks", "pages/3_PN_Monitor.py", "go_pn"),
    (t("nav.stoich"), "Strous / Lotti · feed & PN/A ratios", "pages/4_Stoichiometry.py", "go_stoich"),
    (t("nav.history"), "Saved simulations & charts", "pages/6_Simulation_History.py", "go_hist"),
]

grid = st.columns(3) + st.columns(3) + st.columns(3)
for col, (title, desc, path, key) in zip(grid, cards):
    with col:
        render_module_card(title, desc, path, key)

st.divider()

c1, c2 = st.columns(2)

with c1:
    render_section(t("dash.recent_sims"))
    sims = get_user_experiments(st.session_state["user_id"])
    if sims.empty:
        st.info(t("dash.no_sims"))
    else:
        cols = [c for c in ["id", "created_at", "stage", "nh4", "no2", "final_nh4", "final_no2", "final_no3"] if c in sims.columns]
        st.dataframe(sims[cols].head(5), use_container_width=True, hide_index=True)

with c2:
    render_section(t("dash.recent_readings"))
    readings = get_lab_readings(st.session_state["user_id"], limit=5)
    if readings.empty:
        st.info(t("dash.no_readings"))
    else:
        st.dataframe(
            readings[["id", "created_at", "stage", "nh4", "no2", "no3", "status"]],
            use_container_width=True,
            hide_index=True,
        )

render_sidebar_footer()
