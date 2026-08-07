import streamlit as st


def show_sidebar():

    with st.sidebar:

        st.title(
            "Resume Manager"
        )

        st.write(
            f"Logged in as "
            f"**{st.session_state.username}**"
        )

        st.divider()

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "All Resumes",
                "Add Resume",
                "Find Resume",
                "Update Resume",
                "Delete Resume",
                "AI Analysis",
            ],
        )

        st.divider()

        if st.button(
            "Logout",
            use_container_width=True,
        ):

            st.session_state.token = None
            st.session_state.username = None
            st.session_state.update_resume = None

            st.rerun()

    return page