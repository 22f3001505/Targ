"""Shared Streamlit UX helpers for auth and session flow."""
from html import escape

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

FLOW_HINTS = {
    "Hello.py": "Start or jump back into today's health work.",
    "pages/0_🔐_Account.py": "Sync progress, saved meals, water, plans, and workout logs.",
    "pages/1_💪_Diet_Recommendation.py": "Set your BMI, calories, and nutrition targets.",
    "pages/2_🔍_Custom_Food_Recommendation.py": "Find and save foods that match your target macros.",
    "pages/3_🏋️_Workout_Recommendation.py": "Use your health profile for a safe workout plan.",
    "pages/4_📊_Macro_Tracker.py": "Log meals, water, and daily macro progress.",
    "pages/5_📅_Meal_Planner.py": "Build a weekly plan and grocery list.",
}

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


def _step_index(path: str) -> int:
    return next((idx for idx, step in enumerate(FLOW_STEPS) if step[1] == path), 0)


def _link_to_page(path: str, label: str, *, key: str) -> None:
    """Render a page link with a button fallback for older Streamlit versions."""
    if hasattr(st, "page_link"):
        st.page_link(path, label=label)
    elif st.button(label, key=key, use_container_width=True):
        st.switch_page(path)


def _coerce_int(value: object, default: int = 0) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def _session_flow_state() -> dict:
    """Collect page-completion state without making extra API calls."""
    user_data = st.session_state.get("user_data") or {}
    meals_logged = st.session_state.get("meals_logged") or []
    if not isinstance(meals_logged, list):
        meals_logged = []

    planner_slots = (
        "Monday_breakfast", "Monday_lunch", "Monday_snack", "Monday_dinner",
        "Tuesday_breakfast", "Tuesday_lunch", "Tuesday_snack", "Tuesday_dinner",
        "Wednesday_breakfast", "Wednesday_lunch", "Wednesday_snack", "Wednesday_dinner",
        "Thursday_breakfast", "Thursday_lunch", "Thursday_snack", "Thursday_dinner",
        "Friday_breakfast", "Friday_lunch", "Friday_snack", "Friday_dinner",
        "Saturday_breakfast", "Saturday_lunch", "Saturday_snack", "Saturday_dinner",
        "Sunday_breakfast", "Sunday_lunch", "Sunday_snack", "Sunday_dinner",
    )
    planned_meals = sum(1 for key in planner_slots if st.session_state.get(key))

    has_health = bool(st.session_state.get("health_data"))
    has_workout = bool(st.session_state.get("workout_data") or has_health)
    tracked_meals = len(meals_logged)
    water_glasses = _coerce_int(st.session_state.get("water_glasses"))

    return {
        "has_auth": bool(st.session_state.get("auth_token")),
        "username": user_data.get("username") or "account",
        "has_health": has_health,
        "has_workout": has_workout,
        "tracked_meals": tracked_meals,
        "water_glasses": water_glasses,
        "has_macro_activity": tracked_meals > 0 or water_glasses > 0,
        "planned_meals": planned_meals,
        "has_plan": bool(st.session_state.get("meal_plan_loaded_at")) or planned_meals > 0,
    }


def _step_complete(path: str, state: dict) -> bool:
    if path == "Hello.py":
        return True
    if path == "pages/0_🔐_Account.py":
        return state["has_auth"]
    if path == "pages/1_💪_Diet_Recommendation.py":
        return state["has_health"]
    if path == "pages/2_🔍_Custom_Food_Recommendation.py":
        return state["has_health"]
    if path == "pages/3_🏋️_Workout_Recommendation.py":
        return state["has_workout"]
    if path == "pages/4_📊_Macro_Tracker.py":
        return state["has_macro_activity"]
    if path == "pages/5_📅_Meal_Planner.py":
        return state["has_plan"]
    return False


def _recommended_step(active_page: str, state: dict) -> tuple[str | None, str]:
    """Choose the most useful next destination for the user's current state."""
    if not state["has_auth"]:
        if active_page == AUTH_PAGE:
            return None, "Create an account or sign in to unlock saved progress across web and app."
        return AUTH_PAGE, "Sign in once so your meals, water, workouts, and plans stay synced."
    if not state["has_health"]:
        return "pages/1_💪_Diet_Recommendation.py", "Run health analysis first so every later page uses the right targets."
    if active_page == "pages/1_💪_Diet_Recommendation.py":
        return "pages/2_🔍_Custom_Food_Recommendation.py", "Use your calorie target to find recipes that fit."
    if not state["has_macro_activity"]:
        return "pages/4_📊_Macro_Tracker.py", "Log a meal or water so today's dashboard has real progress."
    if not state["has_plan"]:
        return "pages/5_📅_Meal_Planner.py", "Turn your targets into a weekly plan and grocery list."
    return NEXT_STEP.get(active_page), "Your core flow is ready. Keep moving through the next health task."


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
    """Render a clear end-to-end workflow strip shared by every page."""
    state = _session_flow_state()
    current_label, _ = _find_step(active_page)
    active_idx = _step_index(active_page)
    completed_steps = sum(1 for _, path in FLOW_STEPS[1:] if _step_complete(path, state))
    progress_pct = round(completed_steps / max(len(FLOW_STEPS) - 1, 1) * 100)
    sync_label = escape(f"@{state['username']}" if state["has_auth"] else "offline")
    next_path, next_reason = _recommended_step(active_page, state)
    next_label = _find_step(next_path)[0] if next_path else current_label
    safe_current = escape(current_label)
    safe_next_label = escape(next_label)
    safe_reason = escape(next_reason)
    safe_hint = escape(FLOW_HINTS.get(active_page, "Keep moving through your health workflow."))

    st.markdown(
        f"""
        <div class="flow-panel">
            <div class="flow-topline">
                <div>
                    <div class="flow-eyebrow">End-to-end web flow</div>
                    <div class="flow-heading">Current Step: <strong>{safe_current}</strong></div>
                    <div class="flow-copy">{safe_hint}</div>
                </div>
                <div class="flow-score">
                    <strong>{progress_pct}%</strong>
                    <span>ready</span>
                </div>
            </div>
            <div class="flow-progress" aria-label="Workflow completion">
                <div class="flow-progress-fill" style="width: {progress_pct}%;"></div>
            </div>
            <div class="flow-badges">
                <span>☁️ Sync: {sync_label}</span>
                <span>💪 Health: {'ready' if state['has_health'] else 'needed'}</span>
                <span>🍽️ Meals: {state['tracked_meals']}</span>
                <span>💧 Water: {state['water_glasses']}</span>
                <span>📅 Plan: {'ready' if state['has_plan'] else 'open'}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    step_cards = []
    for idx, (label, path) in enumerate(FLOW_STEPS):
        complete = _step_complete(path, state)
        classes = ["flow-step-card"]
        if path == active_page:
            classes.append("active")
        elif complete or idx < active_idx:
            classes.append("done")
        status = "Current" if path == active_page else ("Ready" if complete else "Next")
        step_cards.append(
            f'<div class="{" ".join(classes)}">'
            f"<span>{idx + 1}</span>"
            f"<strong>{escape(label)}</strong>"
            f"<small>{status}</small>"
            "</div>"
        )
    st.markdown(f"<div class=\"flow-step-grid\">{''.join(step_cards)}</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="flow-next-card">
            <div>
                <div class="flow-next-title">Recommended Next: {safe_next_label}</div>
                <div class="flow-copy">{safe_reason}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if next_path and next_path != active_page:
        _link_to_page(next_path, f"Continue to {next_label}", key=f"next_{active_page}")

    nav_rows = (FLOW_STEPS[:4], FLOW_STEPS[4:])
    for row_idx, row in enumerate(nav_rows):
        cols = st.columns(len(row))
        for col, (label, path) in zip(cols, row):
            with col:
                display = f"✓ {label}" if _step_complete(path, state) and path != active_page else label
                if path == active_page:
                    st.markdown(f"<div class=\"flow-current-link\">{escape(display)}</div>", unsafe_allow_html=True)
                else:
                    _link_to_page(path, display, key=f"flow_{active_page}_{row_idx}_{path}")
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
