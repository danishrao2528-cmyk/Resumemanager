import streamlit as st

from app.frontend.auth_page import (
    show_auth_page,
)
from app.frontend.dashboard import (
    show_dashboard,
)
from app.frontend.resume_pages import (
    ai_analysis_page,
    create_resume_page,
    delete_resume_page,
    search_resume_page,
    show_all_resumes,
    update_resume_page,
)
from app.frontend.sidebar import (
    show_sidebar,
)


st.set_page_config(
    page_title="Resume Manager",
    layout="wide",
)


if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None

if "update_resume" not in st.session_state:
    st.session_state.update_resume = None


if st.session_state.token is None:

    show_auth_page()

else:

    page = show_sidebar()


    if page == "Dashboard":

        show_dashboard()

    elif page == "All Resumes":

        show_all_resumes()

    elif page == "Add Resume":

        create_resume_page()

    elif page == "Find Resume":

        search_resume_page()

    elif page == "Update Resume":

        update_resume_page()

    elif page == "Delete Resume":

        delete_resume_page()

    elif page == "AI Analysis":

        ai_analysis_page()