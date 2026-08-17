import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

API_URL = os.getenv(
    "API_URL",
    "https://resumemanager-production-e17d.up.railway.app",
).rstrip("/")

AUTH_STATE_KEYS = [
    "token",
    "user_id",
    "full_name",
    "username",
    "email",
    "role",
    "candidate_detail",
    "ai_results",
    "show_all_ai",
]

COOKIE_REMOVE_REQUEST_KEY = "remove_auth_cookie_requested"


def get_headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"}


def clear_local_auth(
    message: str | None = None,
    *,
    remove_persistent_cookie: bool = True,
):
    """
    Clear only this Streamlit user's authentication state.

    Cookie deletion is not performed in this module. Instead we set a
    session-state flag. streamlit_app.py owns the browser cookie manager and
    removes the cookie on the next rerun. This keeps the cookie component in
    the main Streamlit script and avoids cross-user/shared controller state.
    """
    for key in AUTH_STATE_KEYS:
        st.session_state[key] = None

    if remove_persistent_cookie:
        st.session_state[COOKIE_REMOVE_REQUEST_KEY] = True

    if message:
        st.session_state["auth_notice"] = message


def show_api_error(response):
    if response is None:
        st.error("Unable to connect to the API.")
        return

    try:
        body = response.json()
        detail = body.get("detail", "Something went wrong.")
    except Exception:
        detail = "Unable to communicate with API."

    st.error(f"Error {response.status_code}: {detail}")


def _request(method, path, **kwargs):
    had_login = bool(st.session_state.get("token"))

    try:
        response = requests.request(
            method,
            f"{API_URL}{path}",
            timeout=kwargs.pop("timeout", 15),
            **kwargs,
        )
    except requests.exceptions.RequestException:
        return None

    non_auto_logout_paths = {"/auth/login", "/auth/register", "/auth/logout"}

    # Only an authenticated request receiving 401 means that the current
    # login is no longer valid. Failed login attempts should simply display
    # their own error instead of clearing another session.
    if (
        response.status_code == 401
        and had_login
        and path not in non_auto_logout_paths
    ):
        try:
            detail = response.json().get(
                "detail",
                "Your session has expired",
            )
        except Exception:
            detail = "Your session has expired"

        clear_local_auth(
            f"{detail}. Please sign in again.",
            remove_persistent_cookie=True,
        )
        st.rerun()

    return response


# ============================================================
# AUTHENTICATION
# ============================================================


def register_candidate(payload):
    return _request("POST", "/auth/register", json=payload)


def login_user(email, password):
    return _request(
        "POST",
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )


def logout_user():
    return _request(
        "POST",
        "/auth/logout",
        headers=get_headers(),
    )


def check_session():
    return _request(
        "GET",
        "/auth/session-status",
        headers=get_headers(),
    )


def get_current_user_profile():
    return _request(
        "GET",
        "/auth/me",
        headers=get_headers(),
    )


# ============================================================
# CANDIDATE RESUME
# ============================================================


def get_my_resume():
    return _request(
        "GET",
        "/resume/me",
        headers=get_headers(),
    )


def create_my_resume(resume_text):
    return _request(
        "POST",
        "/resume/me",
        json={"resume_text": resume_text},
        headers=get_headers(),
    )


def update_my_resume(resume_text):
    return _request(
        "PATCH",
        "/resume/me",
        json={"resume_text": resume_text},
        headers=get_headers(),
    )


# ============================================================
# ADMIN
# ============================================================


def get_admin_stats():
    return _request(
        "GET",
        "/admin/stats",
        headers=get_headers(),
    )


def get_candidates():
    return _request(
        "GET",
        "/admin/candidates",
        headers=get_headers(),
    )


def get_candidate(user_id):
    return _request(
        "GET",
        f"/admin/candidates/{user_id}",
        headers=get_headers(),
    )


def delete_candidate(user_id):
    return _request(
        "DELETE",
        f"/admin/candidates/{user_id}",
        headers=get_headers(),
    )


def get_all_resumes():
    return _request(
        "GET",
        "/admin/resumes",
        headers=get_headers(),
    )


# ============================================================
# SUPER ADMIN
# ============================================================


def get_admin_accounts():
    return _request(
        "GET",
        "/admin/admins",
        headers=get_headers(),
    )


def create_admin_account(payload):
    return _request(
        "POST",
        "/admin/admins",
        json=payload,
        headers=get_headers(),
    )


# ============================================================
# AI CANDIDATE SEARCH
# ============================================================


def ai_candidate_search(requirement):
    return _request(
        "POST",
        "/admin/ai-search",
        json={"requirement": requirement},
        headers=get_headers(),
        timeout=90,
    )
