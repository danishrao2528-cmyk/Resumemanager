import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")


def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def show_api_error(response):
    if response is None:
        st.error("Unable to connect to the API.")
        return
    try:
        detail = response.json().get("detail", "Something went wrong.")
    except Exception:
        detail = "Unable to communicate with API."
    st.error(f"Error {response.status_code}: {detail}")


def _request(method, path, **kwargs):
    try:
        return requests.request(method, f"{API_URL}{path}", timeout=kwargs.pop("timeout", 15), **kwargs)
    except requests.exceptions.RequestException:
        return None


def register_candidate(payload):
    return _request("POST", "/auth/register", json=payload)


def login_user(email, password):
    return _request(
        "POST",
        "/auth/login",
        data={"username": email, "password": password},
    )


def get_my_resume():
    return _request("GET", "/resume/me", headers=get_headers())


def create_my_resume(resume_text):
    return _request("POST", "/resume/me", json={"resume_text": resume_text}, headers=get_headers())


def update_my_resume(resume_text):
    return _request("PATCH", "/resume/me", json={"resume_text": resume_text}, headers=get_headers())


def get_admin_stats():
    return _request("GET", "/admin/stats", headers=get_headers())


def get_candidates():
    return _request("GET", "/admin/candidates", headers=get_headers())


def get_candidate(user_id):
    return _request("GET", f"/admin/candidates/{user_id}", headers=get_headers())


def delete_candidate(user_id):
    return _request("DELETE", f"/admin/candidates/{user_id}", headers=get_headers())


def get_all_resumes():
    return _request("GET", "/admin/resumes", headers=get_headers())


def ai_candidate_search(requirement):
    return _request(
        "POST",
        "/admin/ai-search",
        json={"requirement": requirement},
        headers=get_headers(),
        timeout=90,
    )
def get_current_user_profile():
    return _request(
        "GET",
        "/auth/me",
        headers=get_headers(),
    )