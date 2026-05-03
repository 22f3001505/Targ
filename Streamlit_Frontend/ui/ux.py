"""Shared Streamlit UX helpers for auth and session flow."""
import streamlit as st
from api import APIClient


AUTH_PAGE = "pages/0_🔐_Account.py"
DEFAULT_AFTER_LOGIN = "Hello.py"

FLOW_STEPS = (
    ("🏠 Home", "Hello.py"),
    ("🔐 Account", "pages/0_🔐_Account.py"),
    ("💪 Health", "pages/1_💪_Diet_Recommendation.py"),
    ("🔍 Recipes", "pages/2_🔍_Custom_Food_Recommendation.py"),
    ("🏋️ Workouts", "pages/3_🏋️_Workout_Recommendation.py"),
    ("📊 Macros", "pages/4_📊_Macro_Tracker.py"),
    ("📅 Planner", "pages/5_📅_Meal_Planner.py"),
)

NEXT_STEP = {
    "Hello.py": "pages/1_💪_Diet_Recommendation.py",
    "pages/0_🔐_Account.py": "pages/1_💪_Diet_Recommendation.py",
    "pages/1_💪_Diet_Recommendation.py": "pages/2_🔍_Custom_Food_Recommendation.py",
    "pages/2_🔍_Custom_Food_Recommendation.py": "pages/4_📊_Macro_Tracker.py",
    "pages/3_🏋️_Workout_Recommendation.py": "pages/4_📊_Macro_Tracker.py",
    "pages/4_📊_Macro_Tracker.py": "pages/5_📅_Meal_Planner.py",
    "pages/5_📅_Meal_Planner.py": "pages/0_🔐_Account.py",
}


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


def _find_step(path: str) -> tuple[str, str]:
    return next((step for step in FLOW_STEPS if step[1] == path), FLOW_STEPS[0])


def _link_to_page(path: str, label: str, *, key: str) -> None:
    """Render a page link with a button fallback for older Streamlit versions."""
    if hasattr(st, "page_link"):
        st.page_link(path, label=label)
    elif st.button(label, key=key, use_container_width=True):
        st.switch_page(path)


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


def render_flow_status(active_page: str) -> None:
    """Render a compact end-to-end workflow strip shared by every page."""
    current_label, _ = _find_step(active_page)
    has_health = bool(st.session_state.get("health_data"))
    tracked_meals = len(st.session_state.get("meals_logged", []) or [])
    water_glasses = st.session_state.get("water_glasses")
    user_data = st.session_state.get("user_data") or {}
    sync_label = f"@{user_data.get('username', 'account')}" if st.session_state.get("auth_token") else "offline"

    st.markdown(
        f"""
        <div class="flow-panel">
            <div class="flow-heading">Current Step: <strong>{current_label}</strong></div>
            <div class="flow-badges">
                <span>☁️ Sync: {sync_label}</span>
                <span>💪 Health: {'ready' if has_health else 'needed'}</span>
                <span>🍽️ Meals: {tracked_meals}</span>
                <span>💧 Water: {water_glasses if water_glasses is not None else 0}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(len(FLOW_STEPS))
    for idx, (label, path) in enumerate(FLOW_STEPS):
        with cols[idx]:
            if path == active_page:
                st.markdown(f"**{label}**")
            else:
                _link_to_page(path, label, key=f"flow_{active_page}_{idx}")

    next_path = "pages/1_💪_Diet_Recommendation.py" if not has_health else NEXT_STEP.get(active_page)
    if next_path and next_path != active_page:
        next_label, _ = _find_step(next_path)
        st.caption("Recommended next")
        _link_to_page(next_path, f"Continue to {next_label}", key=f"next_{active_page}")
    st.markdown("---")


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
