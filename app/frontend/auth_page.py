import streamlit as st

from app.frontend.api import (
    login_user,
    register_user,
)


def show_auth_page():

    st.title("Resume Manager")

    st.write(
        "Login or create an account to manage resumes."
    )

    login_tab, register_tab = st.tabs(
        [
            "Login",
            "Register",
        ]
    )

    with login_tab:

        username = st.text_input(
            "Username",
            key="login_username",
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password",
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True,
        ):

            if not username or not password:

                st.warning(
                    "Enter username and password."
                )

            else:

                if login_user(
                    username,
                    password,
                ):

                    st.success(
                        "Login successful."
                    )

                    st.rerun()


    with register_tab:

        username = st.text_input(
            "New Username",
            key="register_username",
        )

        password = st.text_input(
            "New Password",
            type="password",
            key="register_password",
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
        )

        if st.button(
            "Create Account",
            type="primary",
            use_container_width=True,
        ):

            if len(username) < 3:

                st.warning(
                    "Username must be at least 3 characters."
                )

            elif len(password) < 6:

                st.warning(
                    "Password must be at least 6 characters."
                )

            elif password != confirm_password:

                st.warning(
                    "Passwords do not match."
                )

            else:

                if register_user(
                    username,
                    password,
                ):

                    st.success(
                        "Account created. You can now login."
                    )