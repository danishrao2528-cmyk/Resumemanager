import streamlit as st

from api import clear_local_auth, logout_user


COOKIE_NAME = "resume_manager_token"


def logout(cookies):
    """
    Log out this browser completely.

    1. Ask FastAPI to revoke the server-side AuthSession.
    2. Overwrite the encrypted JWT cookie with an empty value and save it.
    3. Clear this Streamlit session's authentication state.
    4. Rerun so the login page is rendered.

    We intentionally overwrite instead of deleting because the cookie-manager
    package's deletion path is unreliable, while its write/save path is already
    proven to work in this app for persistent login.
    """

    response = logout_user()

    try:
        cookies[COOKIE_NAME] = ""
        cookies.save()
    except Exception as error:
        st.error(f"Logout cookie could not be cleared: {error}")
        return

    clear_local_auth(remove_persistent_cookie=False)

    if response is None:
        st.session_state["auth_notice"] = (
            "You have been logged out from this browser. The API could not be "
            "reached to revoke the server session."
        )
    elif response.status_code in {204, 401}:
        st.session_state["auth_notice"] = "You have been logged out."
    else:
        st.session_state["auth_notice"] = (
            "You have been logged out from this browser, but the server "
            f"returned HTTP {response.status_code} while revoking the session."
        )

    st.rerun()


def show_sidebar(cookies):
    with st.sidebar:
        st.title("📄 Resume Manager")
        st.caption("AI Recruitment Workspace")
        st.divider()

        role = st.session_state.role

        with st.container(border=True):
            if role == "super_admin":
                st.markdown(f"### 👑 {st.session_state.full_name}")
            elif role == "admin":
                st.markdown(f"### 🛡️ {st.session_state.full_name}")
            else:
                st.markdown(f"### 👤 {st.session_state.full_name}")

            st.caption(f"@{st.session_state.username}")

            if role == "super_admin":
                st.caption("👑 Super Administrator")
            elif role == "admin":
                st.caption("🛡️ Administrator")
            else:
                st.caption("🎓 Candidate")

        st.write("")

        if role in {"admin", "super_admin"}:
            page_map = {
                "🏠 Dashboard": "Dashboard",
                "👥 Candidates": "Candidates",
                "📄 All Resumes": "All Resumes",
                "✨ AI Candidate Search": "AI Candidate Search",
            }
            if role == "super_admin":
                page_map["👑 Admin Management"] = "Admin Management"
        else:
            page_map = {
                "🏠 Dashboard": "Dashboard",
                "📄 My Resume": "My Resume",
            }

        selected = st.radio(
            "Navigation",
            list(page_map.keys()),
            label_visibility="collapsed",
        )

        st.divider()
        st.caption("🔐 Signed in securely with JWT")

        if st.button("🚪 Logout", use_container_width=True):
            logout(cookies)

    return page_map[selected]
