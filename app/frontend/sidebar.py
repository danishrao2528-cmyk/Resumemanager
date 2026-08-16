import streamlit as st

from api import clear_local_auth, logout_user


def logout():
    # Revoke the server-side session first. Even if the API is unavailable,
    # local logout still continues below.
    logout_user()
    clear_local_auth()
    st.rerun()


def show_sidebar():
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
            logout()

    return page_map[selected]
