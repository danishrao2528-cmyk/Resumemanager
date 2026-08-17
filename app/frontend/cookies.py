"""
Deprecated compatibility file.

The previous version used streamlit-cookies-controller from this module. That
component has known synchronization/cloud issues and should not be used for
Resume Manager authentication.

Authentication cookies are now created only in streamlit_app.py with
EncryptedCookieManager and passed to auth_page.py as a per-browser manager.
Do not instantiate a cookie controller in this module.
"""
