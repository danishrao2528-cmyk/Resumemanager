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

from api import (
    check_session,
    clear_local_auth,
    get_current_user_profile,
)

from auth_page import show_auth_page

from candidate_pages import (
    candidate_dashboard,
    my_resume_page,
)

from cookies import get_cookie

from sidebar import show_sidebar

from styles import apply_styles

from super_admin_page import (
    admin_management_page,
)


COOKIE_NAME = "resume_manager_token"


apply_styles()


# ==================================
# INITIALIZE SESSION STATE
# ==================================

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


# ==================================
# RESTORE LOGIN AFTER REFRESH
# ==================================


def _restore_login():
    """
    Restore a previous login after browser refresh.

    Streamlit session_state is temporary.

    Therefore after a refresh:

    1. Read JWT from browser cookie.
    2. Put JWT temporarily in session_state.
    3. Send JWT to FastAPI /auth/me.
    4. FastAPI validates JWT + AuthSession.
    5. Restore complete user information.
    """

    # Already authenticated in current
    # Streamlit session.
    if st.session_state.get("token"):

        return

    # ----------------------------------
    # GET JWT FROM BROWSER COOKIE
    # ----------------------------------

    saved_token = get_cookie(
        COOKIE_NAME
    )

    # No cookie means this browser is
    # genuinely logged out.
    if not saved_token:

        return

    # api.py creates the Authorization
    # header from session_state.token.
    st.session_state.token = saved_token

    # ----------------------------------
    # VERIFY TOKEN WITH FASTAPI
    # ----------------------------------

    response = get_current_user_profile()

    # ----------------------------------
    # API TEMPORARILY UNAVAILABLE
    # ----------------------------------

    if response is None:

        # Clear only temporary Streamlit state.
        #
        # DO NOT delete browser cookie because
        # the JWT may still be perfectly valid.
        clear_local_auth(
            (
                "Unable to verify your saved login "
                "because the API is temporarily "
                "unavailable. Refresh again when "
                "the API is available."
            ),
            remove_persistent_cookie=False,
        )

        return

    # ----------------------------------
    # TOKEN VALID
    # ----------------------------------

    if response.status_code == 200:

        user = response.json()

        st.session_state.user_id = (
            user["id"]
        )

        st.session_state.full_name = (
            user["full_name"]
        )

        st.session_state.username = (
            user["username"]
        )

        st.session_state.email = (
            user["email"]
        )

        st.session_state.role = (
            user["role"]
        )

        return

    # ----------------------------------
    # SERVER ERROR
    # ----------------------------------

    if response.status_code >= 500:

        clear_local_auth(
            (
                "The API could not verify your "
                "saved login right now. "
                "Please refresh again in a moment."
            ),
            remove_persistent_cookie=False,
        )

        return

    # ----------------------------------
    # INVALID LOGIN
    # ----------------------------------

    # Normally a 401 has already been handled
    # inside api.py.
    #
    # This handles other invalid authentication
    # responses safely.
    clear_local_auth(
        "Your saved login is no longer valid. "
        "Please sign in again."
    )


# ==================================
# IDLE SESSION WATCHDOG
# ==================================


@st.fragment(
    run_every="30s"
)
def _session_watchdog():
    """
    Check an open page every 30 seconds without
    resetting the inactivity timer.

    /auth/session-status uses the backend
    get_current_user_no_touch dependency.

    Therefore this check does NOT count as
    user activity.
    """

    if not st.session_state.get(
        "token"
    ):

        return

    check_session()


# ==================================
# FIRST TRY TO RESTORE COOKIE
# ==================================


_restore_login()


# ==================================
# NOT LOGGED IN
# ==================================


if not st.session_state.get(
    "token"
):

    show_auth_page()


# ==================================
# LOGGED IN
# ==================================

else:

    _session_watchdog()

    page = show_sidebar()

    role = st.session_state.get(
        "role"
    )

    # ==================================
    # ADMIN / SUPER ADMIN
    # ==================================

    if role in {
        "admin",
        "super_admin",
    }:

        if page == "Dashboard":

            admin_dashboard()

        elif page == "Candidates":

            candidates_page()

        elif page == "All Resumes":

            all_resumes_page()

        elif page == "AI Candidate Search":

            ai_search_page()

        elif (
            page == "Admin Management"
            and role == "super_admin"
        ):

            admin_management_page()

        else:

            st.error(
                "You do not have permission "
                "to open this page."
            )

    # ==================================
    # CANDIDATE
    # ==================================

    elif role == "candidate":

        if page == "Dashboard":

            candidate_dashboard()

        elif page == "My Resume":

            my_resume_page()

        else:

            st.error(
                "You do not have permission "
                "to open this page."
            )

    # ==================================
    # UNKNOWN ROLE
    # ==================================

    else:

        clear_local_auth(
            "Unknown account role. "
            "Please sign in again."
        )

        st.rerun()