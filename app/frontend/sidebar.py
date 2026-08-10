import streamlit as st

from cookies import cookie_controller


COOKIE_NAME = "resume_manager_token"


def logout():

    # ==========================================
    # REMOVE LOGIN COOKIE
    # ==========================================

    try:
        cookie_controller.remove(
            COOKIE_NAME
        )

    except Exception:
        pass

    # ==========================================
    # CLEAR STREAMLIT SESSION
    # ==========================================

    for key in [
        "token",
        "user_id",
        "full_name",
        "username",
        "email",
        "role",
        "candidate_detail",
        "ai_results",
        "show_all_ai",
    ]:
        st.session_state[key] = None

    st.rerun()


def show_sidebar():

    with st.sidebar:

        # ======================================
        # APPLICATION TITLE
        # ======================================

        st.title(
            "📄 Resume Manager"
        )

        st.caption(
            "AI Recruitment Workspace"
        )

        st.divider()

        # ======================================
        # CURRENT USER
        # ======================================

        role = st.session_state.role

        with st.container(
            border=True
        ):

            if role == "admin":
                st.markdown(
                    f"### 🛡️ "
                    f"{st.session_state.full_name}"
                )

            else:
                st.markdown(
                    f"### 👤 "
                    f"{st.session_state.full_name}"
                )

            st.caption(
                f"@{st.session_state.username}"
            )

            if role == "admin":
                st.caption(
                    "🛡️ Administrator"
                )

            else:
                st.caption(
                    "🎓 Candidate"
                )

        st.write("")

        # ======================================
        # NAVIGATION
        # ======================================

        if role == "admin":

            page_map = {
                "🏠 Dashboard":
                    "Dashboard",

                "👥 Candidates":
                    "Candidates",

                "📄 All Resumes":
                    "All Resumes",

                "✨ AI Candidate Search":
                    "AI Candidate Search",
            }

        else:

            page_map = {
                "🏠 Dashboard":
                    "Dashboard",

                "📄 My Resume":
                    "My Resume",
            }

        selected = st.radio(
            "Navigation",
            list(
                page_map.keys()
            ),
            label_visibility="collapsed",
        )

        # ======================================
        # LOGIN STATUS
        # ======================================

        st.divider()

        st.caption(
            "🔐 Signed in securely with JWT"
        )

        # ======================================
        # LOGOUT
        # ======================================

        if st.button(
            "🚪 Logout",
            use_container_width=True,
        ):
            logout()

    # ==========================================
    # RETURN ORIGINAL PAGE NAME
    # ==========================================

    return page_map[selected]