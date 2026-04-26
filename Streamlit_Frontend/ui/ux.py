"""Shared Streamlit UX helpers for auth and session flow."""
import streamlit as st


AUTH_PAGE = "pages/0_🔐_Account.py"
DEFAULT_AFTER_LOGIN = "Hello.py"


USER_SESSION_KEYS = (
    "auth_token",
    "user_data",
    "health_data",
    "diet_recommendations",
    "workout_data",
    "meals_logged",
    "totals",
    "auth_redirect_target",
    "auth_redirect_message",
)


def require_login(target_page: str, message: str | None = None) -> None:
    """Redirect unauthenticated users to Account while remembering their target."""
    if st.session_state.get("auth_token"):
        return

    st.session_state.auth_redirect_target = target_page
    st.session_state.auth_redirect_message = (
        message or "Sign in once and I will take you right back to the page you opened."
    )
    st.switch_page(AUTH_PAGE)


def render_auth_redirect_notice() -> None:
    """Show context on the Account page when login was triggered by a protected page."""
    message = st.session_state.get("auth_redirect_message")
    if message:
        st.info(message)


def consume_auth_redirect(default_page: str = DEFAULT_AFTER_LOGIN) -> str:
    """Return and clear the post-login destination."""
    target = st.session_state.get("auth_redirect_target") or default_page
    st.session_state.pop("auth_redirect_target", None)
    st.session_state.pop("auth_redirect_message", None)
    return target


def clear_user_session() -> None:
    """Clear user-owned state on logout or expired auth."""
    for key in USER_SESSION_KEYS:
        st.session_state.pop(key, None)


def handle_auth_expired(result: dict, *, message: str | None = None) -> bool:
    """Clear session and redirect when an API response reports an expired token."""
    if not result.get("auth_expired"):
        return False

    clear_user_session()
    st.session_state.auth_redirect_message = message or "Your session expired. Please sign in again to continue."
    st.switch_page(AUTH_PAGE)
    return True
