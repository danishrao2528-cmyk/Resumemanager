import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from streamlit_cookies_manager_ext import EncryptedCookieManager


st.set_page_config(
    page_title="Resume Manager AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# COOKIE MANAGER MUST LIVE IN THE MAIN STREAMLIT SCRIPT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

# Use a separate cookie password when available. For local compatibility with
# your current project, SECRET_KEY is accepted as a fallback. In deployment,
# set COOKIE_PASSWORD as a root-level Streamlit secret/environment variable.
COOKIE_PASSWORD = os.getenv("COOKIE_PASSWORD") or os.getenv("SECRET_KEY")

if not COOKIE_PASSWORD:
    st.error(
        "COOKIE_PASSWORD is missing. Add COOKIE_PASSWORD to .env locally and "
        "to your Streamlit deployment secrets, then restart the app."
    )
    st.stop()

cookies = EncryptedCookieManager(
    prefix="resume_manager/",
    password=COOKIE_PASSWORD,
)

# The component needs one browser round trip to load this browser's cookies.
# Do not render the login page before it is ready, otherwise refresh can look
# like a logout simply because the cookie has not loaded yet.
if not cookies.ready():
    st.stop()


# Import the rest only after the cookie component has been initialized in the
# main Streamlit script.
from admin_pages import (
    admin_dashboard,
    ai_search_page,
    all_resumes_page,
    candidates_page,
)
from api import (
    COOKIE_REMOVE_REQUEST_KEY,
    check_session,
    clear_local_auth,
    get_current_user_profile,
)
from auth_page import show_auth_page
from candidate_pages import candidate_dashboard, my_resume_page
from sidebar import show_sidebar
from styles import apply_styles
from super_admin_page import admin_management_page


COOKIE_NAME = "resume_manager_token"

apply_styles()


# ============================================================
# INITIAL SESSION STATE
# ============================================================

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


# ============================================================
# PERSISTENT COOKIE REMOVAL REQUESTS
# ============================================================


def _apply_cookie_removal_request():
    if not st.session_state.pop(COOKIE_REMOVE_REQUEST_KEY, False):
        return

    try:
        # Do not delete the cookie. The cookie-manager family has a long-standing
        # deletion issue. Overwriting with an empty value uses the same write/save
        # path that already works for login persistence.
        cookies[COOKIE_NAME] = ""
        cookies.save()
    except Exception as error:
        # Do not restore an old cookie after logout if deletion fails. Keep a
        # visible message so the problem is diagnosable instead of silent.
        st.session_state["auth_notice"] = (
            "The local session was cleared, but the browser cookie could not "
            f"be removed: {error}"
        )


_apply_cookie_removal_request()


# ============================================================
# RESTORE LOGIN AFTER BROWSER REFRESH
# ============================================================


def _restore_login():
    if st.session_state.get("token"):
        return

    saved_token = cookies.get(COOKIE_NAME)

    if not saved_token:
        return

    # Put the JWT in session_state only long enough for api.py to build the
    # Authorization header. FastAPI remains the source of truth.
    st.session_state.token = saved_token
    response = get_current_user_profile()

    if response is None:
        # Railway/network failure is not the same thing as an invalid login.
        # Keep the encrypted browser cookie so a later refresh can retry.
        clear_local_auth(
            "Unable to verify your saved login because the API is temporarily "
            "unavailable. Refresh again when the API is available.",
            remove_persistent_cookie=False,
        )
        return

    if response.status_code == 200:
        user = response.json()
        st.session_state.user_id = user["id"]
        st.session_state.full_name = user["full_name"]
        st.session_state.username = user["username"]
        st.session_state.email = user["email"]
        st.session_state.role = user["role"]
        return

    if response.status_code >= 500:
        clear_local_auth(
            "The API could not verify your saved login right now. "
            "Please refresh again in a moment.",
            remove_persistent_cookie=False,
        )
        return

    # 401 is normally handled inside api.py, but keep this as a safe fallback.
    clear_local_auth(
        "Your saved login is no longer valid. Please sign in again.",
        remove_persistent_cookie=True,
    )
    st.rerun()


# ============================================================
# IDLE-TIMEOUT WATCHDOG
# ============================================================


@st.fragment(run_every="30s")
def _session_watchdog():
    """
    Ask FastAPI whether the server-side AuthSession is still valid.

    /auth/session-status uses get_current_user_no_touch, so this check does not
    count as user activity and therefore does not defeat the 15-minute idle
    timeout.
    """
    if not st.session_state.get("token"):
        return

    check_session()


_restore_login()


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.get("token"):
    show_auth_page(cookies)


# ============================================================
# AUTHENTICATED APP
# ============================================================

else:
    _session_watchdog()
    page = show_sidebar(cookies)
    role = st.session_state.get("role")

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
            st.error("You do not have permission to open this page.")

    else:
        clear_local_auth(
            "Unknown account role. Please sign in again.",
            remove_persistent_cookie=True,
        )
        st.rerun()
