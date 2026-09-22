"""Persist login across browser refresh via URL token + DB session."""

from __future__ import annotations

import streamlit as st

from core.database import get_username_by_id
from core.session import create_session, delete_session, get_user_by_token

SESSION_QUERY_KEY = "auth"
SESSION_STATE_KEY = "auth_token"


def _read_query_token() -> str | None:
    token = st.query_params.get(SESSION_QUERY_KEY)
    if isinstance(token, list):
        token = token[0] if token else None
    return str(token) if token else None


def _sync_query_token(token: str | None) -> None:
    if token:
        st.query_params[SESSION_QUERY_KEY] = token
    elif SESSION_QUERY_KEY in st.query_params:
        del st.query_params[SESSION_QUERY_KEY]


def restore_session() -> bool:
    """Load user_id/username from URL token if session_state is empty."""
    if st.session_state.get("user_id") is not None:
        token = st.session_state.get(SESSION_STATE_KEY)
        if token:
            _sync_query_token(str(token))
        return True

    token = st.session_state.get(SESSION_STATE_KEY) or _read_query_token()
    if not token:
        return False

    user_id = get_user_by_token(token)
    if user_id is None:
        st.session_state.pop(SESSION_STATE_KEY, None)
        _sync_query_token(None)
        return False

    username = get_username_by_id(user_id) or "User"
    st.session_state["user_id"] = user_id
    st.session_state["username"] = username
    st.session_state[SESSION_STATE_KEY] = token
    _sync_query_token(token)
    return True


def persist_login(user_id: int, username: str) -> None:
    token = create_session(user_id)
    st.session_state["user_id"] = user_id
    st.session_state["username"] = username
    st.session_state[SESSION_STATE_KEY] = token
    _sync_query_token(token)


def clear_login() -> None:
    token = st.session_state.get(SESSION_STATE_KEY) or _read_query_token()
    if token:
        delete_session(token)
    theme = st.session_state.get("ui_theme", "light")
    lang = st.session_state.get("ui_lang", "en")
    st.session_state.clear()
    st.session_state["ui_theme"] = theme
    if lang is not None:
        st.session_state["ui_lang"] = lang
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    _sync_query_token(None)
