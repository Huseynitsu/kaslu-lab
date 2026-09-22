import streamlit as st

import core.database as db
from core.ui.page_init import bootstrap_page, finish_page

bootstrap_page(__file__, "admin", "Admin Panel")

st.warning("Admin tools — delete actions are permanent.")
st.title("Admin Panel")

st.subheader("Users")
users_df = db.get_all_users()
st.dataframe(users_df, use_container_width=True)

if not users_df.empty:
    user_id = st.selectbox("Select user to delete", users_df["id"])
    if st.button("Delete user", type="primary"):
        db.delete_user(user_id)
        st.success("User deleted.")
        st.rerun()

st.subheader("Experiments")
exp_df = db.get_experiments()
st.dataframe(exp_df, use_container_width=True)

if not exp_df.empty:
    exp_id = st.selectbox("Select experiment to delete", exp_df["id"])
    if st.button("Delete experiment"):
        db.delete_experiment(exp_id)
        st.success("Experiment deleted.")
        st.rerun()

st.subheader("System stats")
col1, col2 = st.columns(2)
col1.metric("Total users", len(users_df))
col2.metric("Total experiments", len(exp_df))

finish_page()
