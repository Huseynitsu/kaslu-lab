"""Reusable experiment selector for single-experiment analysis pages."""

import streamlit as st

import core.database as db


def select_user_experiment(key: str = "selected_experiment_id") -> tuple[int | None, object]:
    """
    Show dropdown of current user's experiments.
    Returns (experiment_id, row) or (None, None).
    """
    if st.session_state.get("user_id") is None:
        return None, None

    experiments = db.get_user_experiments(st.session_state["user_id"])

    if experiments.empty:
        st.warning("No saved experiments. Run a simulation first.")
        return None, None

    def label(row):
        stage = str(row.get("stage", "anammox") or "anammox").upper()
        created = str(row.get("created_at", ""))[:16]
        return (
            f"#{int(row['id'])} — {stage} — "
            f"NH₄={row['nh4']:.1f}, NO₂={row['no2']:.1f} — {created}"
        )

    options = experiments["id"].tolist()
    labels = {exp_id: label(experiments[experiments["id"] == exp_id].iloc[0]) for exp_id in options}

    selected_id = st.selectbox(
        "Select experiment",
        options,
        format_func=lambda x: labels[x],
        key=key,
    )

    row = experiments[experiments["id"] == selected_id].iloc[0]
    return int(selected_id), row
