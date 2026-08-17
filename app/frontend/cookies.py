import streamlit as st
from streamlit_cookies_controller import CookieController


COOKIE_STATE_KEY = "resume_manager_browser_cookies"


def _current_browser_cookies() -> dict:
    """
    Return the cookies that the browser sent to the current Streamlit session.

    On a normal browser refresh, st.context.cookies contains the persistent
    resume_manager_token cookie if it was successfully written earlier.
    """
    try:
        return dict(st.context.cookies)
    except Exception:
        return {}


def _ensure_cookie_cache() -> dict:
    """
    Ensure the CookieController always receives a dictionary as its state.

    streamlit-cookies-controller can briefly initialize with None. Keeping a
    dictionary in session_state prevents NoneType errors and also gives us a
    local copy of cookies written during the current Streamlit run.
    """
    cached = st.session_state.get(COOKIE_STATE_KEY)

    if not isinstance(cached, dict):
        cached = _current_browser_cookies()
        st.session_state[COOKIE_STATE_KEY] = cached

    return cached


def get_cookie_controller() -> CookieController:
    """Return the cookie controller for this Streamlit browser session."""
    _ensure_cookie_cache()

    return CookieController(
        key=COOKIE_STATE_KEY
    )


def get_cookie(name: str):
    """
    Read a cookie.

    First check the browser cookies from st.context. If the cookie was just
    written during this Streamlit session and st.context has not updated yet,
    fall back to the local controller cache.
    """
    browser_cookies = _current_browser_cookies()

    if name in browser_cookies:
        cached = _ensure_cookie_cache()

        cached[name] = browser_cookies[name]

        st.session_state[COOKIE_STATE_KEY] = cached

        return browser_cookies[name]

    return _ensure_cookie_cache().get(name)


def set_cookie(name: str, value: str) -> None:
    """
    Persist a cookie in the browser and mirror it into Streamlit session_state.

    same_site='lax' is suitable for a normal Streamlit login cookie and path='/'
    makes it available throughout the application.
    """
    controller = get_cookie_controller()

    controller.set(
        name,
        value,
        path="/",
        same_site="lax",
    )

    cached = _ensure_cookie_cache()

    cached[name] = value

    st.session_state[COOKIE_STATE_KEY] = cached


def remove_cookie(name: str) -> None:
    """
    Remove a cookie from both the browser and the local Streamlit cache.
    """
    controller = get_cookie_controller()

    try:
        controller.remove(
            name,
            path="/",
            same_site="lax",
        )

    except KeyError:
        # CookieController.remove() can raise KeyError when its local cache
        # no longer contains the cookie even though the browser remove
        # command was already sent.
        pass

    cached = _ensure_cookie_cache()

    cached.pop(
        name,
        None,
    )

    st.session_state[COOKIE_STATE_KEY] = cached