"""Session-state keys for the shared laboratory notebook."""

import streamlit as st

from core.lab_table import SAMPLE_COLUMNS, default_table

LAB_TABLE = "lab_table"
LAB_SELECTED_COLUMNS = "lab_selected_columns"


def init_lab_state() -> None:
    if LAB_TABLE not in st.session_state:
        st.session_state[LAB_TABLE] = default_table()
    if LAB_SELECTED_COLUMNS not in st.session_state:
        st.session_state[LAB_SELECTED_COLUMNS] = [c for c in SAMPLE_COLUMNS if c != "distilled"]
