import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import importlib

import streamlit as st

import core.i18n as i18n

importlib.reload(i18n)
from core.i18n import t

from core.auth import login_user, register_user
from core.auth_session import persist_login
from core.database import create_tables
import core.ui.login_page as login_page

importlib.reload(login_page)

from core.ui.layout import render_login_chrome, setup_page_config

setup_page_config(t("home.title"), wide=True)
render_login_chrome()

create_tables()

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

if st.session_state["user_id"] is not None:
    from core.ui.navigation import switch_to

    switch_to("pages/1_Lab_Dashboard.py")
    st.stop()

st.markdown('<div id="kaslu-login"></div>', unsafe_allow_html=True)
login_page.render_login_ambience()

brand_col, form_col = st.columns(2, gap="large", vertical_alignment="top")

with brand_col:
    login_page.render_login_brand_panel()

with form_col:
    st.markdown('<div id="kaslu-form-shell"></div>', unsafe_allow_html=True)
    login_page.render_login_theme_toggle()
    mode = st.radio(
        t("home.mode"),
        options=["login", "register"],
        format_func=lambda x: t("home.login") if x == "login" else t("home.register"),
        horizontal=True,
        label_visibility="collapsed",
        key="login_mode",
    )
    login_page.render_login_form_header(mode=mode)

    username = st.text_input(t("home.username"), placeholder="Enter username")
    password = st.text_input(t("home.password"), type="password", placeholder="Enter password")

    if mode == "register":
        if st.button(t("home.create_account"), type="primary", use_container_width=True, key="auth_submit"):
            if register_user(username, password):
                st.success(t("home.account_created"))
            else:
                st.error(t("home.username_exists"))
    else:
        if st.button(t("home.sign_in"), type="primary", use_container_width=True, key="auth_submit"):
            user_id = login_user(username, password)
            if user_id:
                persist_login(user_id, username)
                from core.ui.navigation import navigate_to

                navigate_to("pages/1_Lab_Dashboard.py")
            else:
                st.error(t("home.invalid_login"))

    login_page.render_login_secure_note()
