import re

import streamlit as st

from api import login_user, register_candidate, show_api_error
from cookies import get_cookie_controller


COOKIE_NAME = "resume_manager_token"


def _password_valid(password: str) -> bool:
    return (
        len(password) >= 8
        and bool(re.search(r"[A-Z]", password))
        and bool(re.search(r"[a-z]", password))
        and bool(re.search(r"\d", password))
    )


def _save_login(data):
    token = data["access_token"]
    st.session_state.token = token
    st.session_state.user_id = data["user_id"]
    st.session_state.full_name = data["full_name"]
    st.session_state.username = data["username"]
    st.session_state.email = data["email"]
    st.session_state.role = data["role"]

    try:
        get_cookie_controller().set(COOKIE_NAME, token)
    except Exception:
        # Login should still work even if the browser blocks the persistence cookie.
        pass


def _login_panel(expected_role: str):
    role_name = "Administrator" if expected_role == "admin" else "Candidate"
    role_icon = "🛡️" if expected_role == "admin" else "👤"

    with st.container(border=True):
        st.subheader(f"{role_icon} {role_name} Login")
        st.caption(
            "Manage candidates, resumes, and AI search."
            if expected_role == "admin"
            else "Access your profile and manage your resume."
        )

        email = st.text_input(
            "Email",
            key=f"{expected_role}_email",
            placeholder="you@example.com",
        )
        password = st.text_input(
            "Password",
            type="password",
            key=f"{expected_role}_password",
        )

        button_text = "Enter Admin Workspace" if expected_role == "admin" else "Sign In"
        clicked = st.button(
            button_text,
            type="primary",
            use_container_width=True,
            key=f"{expected_role}_login_button",
        )

    if not clicked:
        return
    if not email or not password:
        st.warning("Enter your email and password.")
        return

    response = login_user(email, password)
    if response is None:
        st.error("Unable to connect to the API.")
        return
    if response.status_code != 200:
        show_api_error(response)
        return

    data = response.json()
    actual_role = data.get("role")

    if expected_role == "admin":
        if actual_role not in {"admin", "super_admin"}:
            st.error("This account does not have administrator access.")
            return
    elif actual_role != "candidate":
        st.error("This is an administrator account. Please use Admin Login.")
        return

    _save_login(data)
    st.rerun()


def _signup_panel():
    with st.container(border=True):
        st.subheader("📝 Create Candidate Account")
        st.caption("Create your account and maintain one professional resume.")

        with st.form("candidate_signup", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full name", placeholder="Danish Ali")
            with col2:
                username = st.text_input("Username", placeholder="danish")

            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm password", type="password")

            st.caption("🔐 Use 8+ characters with uppercase, lowercase, and a number.")
            submitted = st.form_submit_button(
                "Create Candidate Account",
                type="primary",
                use_container_width=True,
            )

    if not submitted:
        return
    if not all([full_name, username, email, password, confirm_password]):
        st.warning("Complete all fields.")
        return
    if not _password_valid(password):
        st.warning("Password needs at least 8 characters, including uppercase, lowercase, and a number.")
        return
    if password != confirm_password:
        st.warning("Passwords do not match.")
        return

    response = register_candidate(
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
        return
    if response.status_code == 201:
        st.session_state.next_auth_mode = "Candidate Login"
        st.session_state.signup_success = True
        st.rerun()
    show_api_error(response)


def _show_left_panel():
    st.caption("✨ RESUME MANAGER AI")
    st.title("Find stronger candidates.\nManage resumes simply.")
    st.write(
        "A role-based recruitment workspace powered by FastAPI and Streamlit. "
        "Candidates maintain one professional resume while administrators review "
        "profiles and use AI-assisted matching."
    )

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### 🔐 JWT Security")
            st.caption("Secure token-based authentication with persistent login.")
    with c2:
        with st.container(border=True):
            st.markdown("### 👥 Role Access")
            st.caption("Candidate, administrator, and Super Admin workspaces.")

    with st.container(border=True):
        c1, c2 = st.columns([1, 5], vertical_alignment="center")
        with c1:
            st.markdown("# ✨")
        with c2:
            st.markdown("### AI Candidate Matching")
            st.caption("Describe who you need and rank matching resumes automatically.")

    st.caption("⚡ FastAPI  •  Streamlit  •  SQLAlchemy  •  JWT  •  AI")


def show_auth_page():
    notice = st.session_state.pop("auth_notice", None)
    if notice:
        st.warning(notice)

    if "next_auth_mode" in st.session_state:
        st.session_state.auth_mode = st.session_state.pop("next_auth_mode")
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "Candidate Login"

    left, right = st.columns([1.05, 0.95], gap="large", vertical_alignment="center")

    with left:
        _show_left_panel()

    with right:
        st.title("Welcome 👋")
        st.caption("Choose how you want to access Resume Manager.")

        mode = st.radio(
            "Account access",
            ["Candidate Login", "Admin Login", "Candidate Sign Up"],
            horizontal=True,
            key="auth_mode",
            label_visibility="collapsed",
        )
        st.write("")

        if mode == "Candidate Login":
            _login_panel("candidate")
        elif mode == "Admin Login":
            _login_panel("admin")
        else:
            _signup_panel()

        if st.session_state.pop("signup_success", False):
            st.success("✅ Account created successfully. Sign in with Candidate Login.")
