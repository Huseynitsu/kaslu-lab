import streamlit as st

import core.database as db
from core.report_generator import generate_pdf
from core.ui.page_init import bootstrap_page, finish_page

bootstrap_page(__file__, "pdf_report", "PDF Report")

st.title("PDF Report Generator")

experiment_ids = db.get_all_experiment_ids(user_id=st.session_state.get("user_id"))

if not experiment_ids:
    st.warning("No experiments available.")
    st.stop()

selected_id = st.selectbox("Experiment", experiment_ids)

if st.button("Generate PDF", type="primary"):
    df = db.get_experiment_by_id(selected_id)
    row = df.iloc[0]
    pdf_file = f"experiment_{selected_id}.pdf"
    generate_pdf(row, pdf_file)

    with open(pdf_file, "rb") as f:
        st.download_button(
            label="Download PDF",
            data=f,
            file_name=pdf_file,
            mime="application/pdf",
        )

    st.success("PDF generated successfully.")

finish_page()
