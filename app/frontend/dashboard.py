import streamlit as st

from app.frontend.api import (
    get_all_resumes,
    show_api_error,
)


def show_dashboard():

    st.title("Dashboard")

    st.write(
        f"Welcome, {st.session_state.username}"
    )

    response = get_all_resumes()

    if response is None:
        st.error("Unable to connect to API.")
        return

    if response.status_code != 200:
        show_api_error(response)
        return

    resumes = response.json()


    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Resumes",
        len(resumes),
    )

    col2.metric(
        "Authentication",
        "JWT",
    )

    col3.metric(
        "Backend",
        "FastAPI",
    )


    st.divider()

    st.subheader(
        "Recent Resumes"
    )

    if not resumes:
        st.info(
            "No resumes found."
        )
        return


    for resume in resumes[:5]:

        with st.container(
            border=True
        ):

            st.write(
                f"**{resume['candidate_name']}**"
            )

            st.write(
                resume["email"]
            )

            st.write(
                f"Resume ID: {resume['id']}"
            )