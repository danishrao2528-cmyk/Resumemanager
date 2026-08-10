import streamlit as st

st.set_page_config(
    page_title="Resume Manager AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

from admin_pages import (
    admin_dashboard,
    ai_search_page,
    all_resumes_page,
    candidates_page,
)
from api import get_current_user_profile
from auth_page import show_auth_page
from candidate_pages import (
    candidate_dashboard,
    my_resume_page,
)
from cookies import cookie_controller
from sidebar import show_sidebar
from styles import apply_styles


COOKIE_NAME = "resume_manager_token"

apply_styles()


for key, default in {
    "token": None,
    "user_id": None,
    "full_name": None,
    "username": None,
    "email": None,
    "role": None,
    "candidate_detail": None,
    "ai_results": None,
    "show_all_ai": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def _clear_login_state():
    st.session_state.token = None
    st.session_state.user_id = None
    st.session_state.full_name = None
    st.session_state.username = None
    st.session_state.email = None
    st.session_state.role = None


def _restore_login():
    # Already logged in during this Streamlit session
    if st.session_state.token:
        return

    # Try to recover JWT from browser cookie
    saved_token = cookie_controller.get(
        COOKIE_NAME
    )

    # No cookie = normal logged-out state
    if not saved_token:
        return

    # api.py uses st.session_state.token
    # to build the Authorization header
    st.session_state.token = saved_token

    response = get_current_user_profile()

    # JWT is valid
    if (
        response is not None
        and response.status_code == 200
    ):
        user = response.json()

        st.session_state.user_id = user["id"]
        st.session_state.full_name = user["full_name"]
        st.session_state.username = user["username"]
        st.session_state.email = user["email"]
        st.session_state.role = user["role"]

        return

    # JWT expired / invalid / user no longer exists
    _clear_login_state()

    try:
        cookie_controller.remove(
            COOKIE_NAME
        )
    except Exception:
        pass


_restore_login()


# -----------------------------------
# NOT LOGGED IN
# -----------------------------------

if not st.session_state.token:
    show_auth_page()


# -----------------------------------
# LOGGED IN
# -----------------------------------

else:
    page = show_sidebar()

    # ADMIN
    if st.session_state.role == "admin":

        if page == "Dashboard":
            admin_dashboard()

        elif page == "Candidates":
            candidates_page()

        elif page == "All Resumes":
            all_resumes_page()

        elif page == "AI Candidate Search":
            ai_search_page()

    # CANDIDATE
    elif st.session_state.role == "candidate":

        if page == "Dashboard":
            candidate_dashboard()

        elif page == "My Resume":
            my_resume_page()

    else:
        st.error(
            "Unknown account role. "
            "Please log out and sign in again."
        )