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
from api import check_session, clear_local_auth, get_current_user_profile
from auth_page import show_auth_page
from candidate_pages import candidate_dashboard, my_resume_page
from cookies import get_cookie
from sidebar import show_sidebar
from styles import apply_styles
from super_admin_page import admin_management_page


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


def _restore_login():
    if st.session_state.token:
        return

    # Read from this browser's cookies without depending on the third-party
    # component being ready during the first Streamlit run.
    saved_token = get_cookie(COOKIE_NAME)

    if not saved_token:
        return

    # Never trust the cookie by itself. FastAPI validates JWT + server session.
    st.session_state.token = saved_token
    response = get_current_user_profile()

    if response is not None and response.status_code == 200:
        user = response.json()
        st.session_state.user_id = user["id"]
        st.session_state.full_name = user["full_name"]
        st.session_state.username = user["username"]
        st.session_state.email = user["email"]
        st.session_state.role = user["role"]
        return

    clear_local_auth()


@st.fragment(run_every="30s")
def _session_watchdog():
    """
    Check whether an open page has become idle/expired even when the user
    does nothing. /auth/session-status does not refresh last_activity.
    """
    if not st.session_state.get("token"):
        return

    check_session()


_restore_login()

if not st.session_state.token:
    show_auth_page()
else:
    _session_watchdog()
    page = show_sidebar()
    role = st.session_state.role

    if role in {"admin", "super_admin"}:
        if page == "Dashboard":
            admin_dashboard()
        elif page == "Candidates":
            candidates_page()
        elif page == "All Resumes":
            all_resumes_page()
        elif page == "AI Candidate Search":
            ai_search_page()
        elif page == "Admin Management" and role == "super_admin":
            admin_management_page()
        else:
            st.error("You do not have permission to open this page.")

    elif role == "candidate":
        if page == "Dashboard":
            candidate_dashboard()
        elif page == "My Resume":
            my_resume_page()

    else:
        clear_local_auth("Unknown account role. Please sign in again.")
        st.rerun()
