"""Daily interpretation of NH4 / NO2 / NO3 readings."""

import streamlit as st

from core.ui.page_init import bootstrap_page, finish_page

bootstrap_page(__file__, "diagnostics", "Daily Diagnostics")

from core.constants import PNA_NO3_PER_NH4_REMOVED  # noqa: E402
from core.diagnostics import interpret_daily_reading  # noqa: E402

st.title("Daily Diagnostics")

stage = st.radio(
    "Reactor type",
    ["pna", "pn", "anammox"],
    format_func=lambda s: {"pna": "One-stage PN/A", "pn": "PN (two-stage, stage 1)", "anammox": "Anammox (stage 2)"}[s],
    horizontal=True,
)
mode = st.radio(
    "Comparison basis",
    ["inout", "daytoday"],
    format_func=lambda m: "Influent vs effluent (continuous reactor)" if m == "inout" else "Today vs yesterday (batch / SBR cycle)",
    horizontal=True,
)
ref_label = "Influent" if mode == "inout" else "Yesterday"
cur_label = "Effluent" if mode == "inout" else "Today"

c1, c2 = st.columns(2)
with c1:
    st.markdown(f"**{ref_label}** (mg N/L)")
    nh4_r = st.number_input(f"NH₄ — {ref_label}", 0.0, 5000.0, 200.0 if mode == "inout" else 60.0)
    no2_r = st.number_input(f"NO₂ — {ref_label}", 0.0, 5000.0, 0.0)
    no3_r = st.number_input(f"NO₃ — {ref_label}", 0.0, 5000.0, 0.0)
with c2:
    st.markdown(f"**{cur_label}** (mg N/L)")
    nh4_c = st.number_input(f"NH₄ — {cur_label}", 0.0, 5000.0, 20.0 if mode == "inout" else 50.0)
    no2_c = st.number_input(f"NO₂ — {cur_label}", 0.0, 5000.0, 2.0)
    no3_c = st.number_input(f"NO₃ — {cur_label}", 0.0, 5000.0, 20.0)

if st.button("Interpret", type="primary"):
    diag = interpret_daily_reading(nh4_c, no2_c, no3_c, nh4_r, no2_r, no3_r, stage=stage)
    {"ok": st.success, "warning": st.warning, "danger": st.error}[diag.status](f"Status: {diag.status.upper()}")
    if diag.metrics:
        cols = st.columns(len(diag.metrics))
        for col, (k, v) in zip(cols, diag.metrics.items()):
            col.metric(k, f"{v:.3f}")
    st.subheader("Findings")
    for f in diag.findings:
        st.write("•", f)
    st.subheader("Actions")
    for a in diag.actions:
        st.write("→", a)
    if stage == "pna":
        st.caption(f"Reference: one-stage PN/A theoretical ΔNO₃/ΔNH₄ ≈ {PNA_NO3_PER_NH4_REMOVED:.3f} (Strous 1998: 0.26/2.32).")

finish_page()
