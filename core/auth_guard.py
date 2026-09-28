import streamlit as st

from core.ui.navigation import switch_to


def require_login():
    if "user_id" not in st.session_state or st.session_state["user_id"] is None:
        st.warning("Please login first")
        switch_to("Home.py")
        st.stop()