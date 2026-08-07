import requests
import streamlit as st


API_URL = "https://resumemanager-production-5d0c.up.railway.app"


def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


def show_api_error(response):
    try:
        detail = response.json().get(
            "detail",
            "Something went wrong.",
        )
    except Exception:
        detail = "Unable to communicate with API."

    st.error(
        f"Error {response.status_code}: {detail}"
    )


def register_user(username, password):
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={
                "username": username,
                "password": password,
            },
            timeout=10,
        )

    except requests.exceptions.RequestException:
        st.error("Unable to connect to API.")
        return False

    if response.status_code == 201:
        return True

    show_api_error(response)
    return False


def login_user(username, password):
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            data={
                "username": username,
                "password": password,
            },
            timeout=10,
        )

    except requests.exceptions.RequestException:
        st.error("Unable to connect to API.")
        return False

    if response.status_code == 200:
        data = response.json()

        st.session_state.token = data["access_token"]
        st.session_state.username = username

        return True

    show_api_error(response)
    return False


def get_all_resumes():
    try:
        return requests.get(
            f"{API_URL}/resume",
            headers=get_headers(),
            timeout=10,
        )

    except requests.exceptions.RequestException:
        return None


def get_resume(resume_id):
    try:
        return requests.get(
            f"{API_URL}/resume/{resume_id}",
            headers=get_headers(),
            timeout=10,
        )

    except requests.exceptions.RequestException:
        return None


def create_resume(payload):
    try:
        return requests.post(
            f"{API_URL}/resume",
            json=payload,
            headers=get_headers(),
            timeout=10,
        )

    except requests.exceptions.RequestException:
        return None


def update_resume(resume_id, payload):
    try:
        return requests.patch(
            f"{API_URL}/resume/{resume_id}",
            json=payload,
            headers=get_headers(),
            timeout=10,
        )

    except requests.exceptions.RequestException:
        return None


def delete_resume(resume_id):
    try:
        return requests.delete(
            f"{API_URL}/resume/{resume_id}",
            headers=get_headers(),
            timeout=10,
        )

    except requests.exceptions.RequestException:
        return None


def analyze_resume(resume_id):
    try:
        return requests.get(
            f"{API_URL}/resume/analysis/{resume_id}",
            headers=get_headers(),
            timeout=60,
        )

    except requests.exceptions.RequestException:
        return None