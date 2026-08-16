import streamlit as st
from streamlit_cookies_controller import CookieController


COOKIE_STATE_KEY = "resume_manager_browser_cookies"


def _current_browser_cookies() -> dict:
    """
    Read cookies sent by the current browser session.

    st.context.cookies is read-only and belongs to the current Streamlit
    browser session, so it is safe to use for restoring login state.
    """
    try:
        return dict(st.context.cookies)
    except Exception:
        return {}


def get_cookie(name: str):
    """
    Read a cookie for the current browser/session.

    Prefer Streamlit's built-in browser context. Fall back to the
    per-session cache for a cookie that was just set during this session.
    """
    browser_cookies = _current_browser_cookies()

    if name in browser_cookies:
        return browser_cookies[name]

    cached = st.session_state.get(COOKIE_STATE_KEY)
    if isinstance(cached, dict):
        return cached.get(name)

    return None


def get_cookie_controller() -> CookieController:
    """
    Return a CookieController whose internal cookie cache is always a dict.

    The third-party controller can return None while its frontend component
    is still initializing. Seeding its session-state key from st.context
    prevents `TypeError: argument of type 'NoneType' is not iterable`.

    The state is still per Streamlit session, so separate browsers do not
    share authentication state.
    """
    cached = st.session_state.get(COOKIE_STATE_KEY)

    if not isinstance(cached, dict):
        st.session_state[COOKIE_STATE_KEY] = _current_browser_cookies()

    return CookieController(key=COOKIE_STATE_KEY)
