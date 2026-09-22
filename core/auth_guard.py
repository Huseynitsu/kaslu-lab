import streamlit as st

def require_login():
    if "user_id" not in st.session_state or st.session_state["user_id"] is None:
        st.warning("Please login first")
        st.switch_page("Home.py")
        st.stop()