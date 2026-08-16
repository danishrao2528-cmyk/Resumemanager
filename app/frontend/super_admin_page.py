import re

import streamlit as st

from api import create_admin_account, get_admin_accounts, show_api_error


def _password_valid(password: str) -> bool:
    return (
        len(password) >= 8
        and bool(re.search(r"[A-Z]", password))
        and bool(re.search(r"[a-z]", password))
        and bool(re.search(r"\d", password))
    )


def admin_management_page():
    if st.session_state.get("role") != "super_admin":
        st.error("Super Admin access required.")
        return

    st.title("👑 Admin Management")
    st.caption("Only the Super Admin can create administrator accounts.")

    with st.container(border=True):
        st.subheader("Create Administrator")

        with st.form("create_admin_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full name")
                username = st.text_input("Username")
            with col2:
                email = st.text_input("Email")
                password = st.text_input("Initial password", type="password")

            confirm_password = st.text_input("Confirm initial password", type="password")
            st.caption("Use at least 8 characters with uppercase, lowercase, and a number.")
            submitted = st.form_submit_button(
                "Create Administrator",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not all([full_name, username, email, password, confirm_password]):
                st.warning("Complete all fields.")
            elif not _password_valid(password):
                st.warning("Password needs at least 8 characters, uppercase, lowercase, and a number.")
            elif password != confirm_password:
                st.warning("Passwords do not match.")
            else:
                response = create_admin_account(
                    {
                        "full_name": full_name,
                        "username": username,
                        "email": email,
                        "password": password,
                        "confirm_password": confirm_password,
                    }
                )

                if response is None:
                    st.error("Unable to connect to the API.")
                elif response.status_code == 201:
                    created = response.json()
                    st.success(f"Administrator {created['email']} created successfully.")
                else:
                    show_api_error(response)

    st.subheader("Administrator Accounts")
    response = get_admin_accounts()

    if response is None:
        st.error("Unable to connect to the API.")
        return
    if response.status_code != 200:
        show_api_error(response)
        return

    admins = response.json()
    if not admins:
        st.info("No administrator accounts found.")
        return

    rows = [
        {
            "ID": admin["id"],
            "Name": admin["full_name"],
            "Username": admin["username"],
            "Email": admin["email"],
            "Role": "Super Admin" if admin["role"] == "super_admin" else "Admin",
        }
        for admin in admins
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
