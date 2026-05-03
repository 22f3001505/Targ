"""Shared Streamlit UX helpers for auth and session flow."""
import streamlit as st
from api import APIClient


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
    "daily_goals",
    "water_glasses",
    "confirm_clear_meals",
    "meal_plan_autoloaded",
    "auth_session_checked",
    "auth_redirect_target",
    "auth_redirect_message",
)


def ensure_session_fresh() -> bool:
    """Refresh the saved web token once per Streamlit session, keeping temporary offline sessions usable."""
    token = st.session_state.get("auth_token")
    if not token:
        return False
    if st.session_state.get("auth_session_checked"):
        return True

    result = APIClient.refresh_token(token)
    if result.get("success"):
        data = result["data"]
        st.session_state.auth_token = data.get("access_token", token)
        st.session_state.user_data = data.get("user", st.session_state.get("user_data"))
        st.session_state.auth_session_checked = True
        return True

    if result.get("auth_expired"):
        clear_user_session()
        st.session_state.auth_redirect_message = "Your session expired. Please sign in again to continue."
        st.switch_page(AUTH_PAGE)

    if result.get("connection_error"):
        st.session_state.auth_session_checked = True
        return True

    return True


def require_login(target_page: str, message: str | None = None) -> None:
    """Redirect unauthenticated users to Account while remembering their target."""
    if st.session_state.get("auth_token"):
        ensure_session_fresh()
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
