"""Shared Streamlit UX helpers for auth and session flow."""
from datetime import datetime
from html import escape

import streamlit as st
from api import APIClient


AUTH_PAGE = "pages/0_🔐_Account.py"
DEFAULT_AFTER_LOGIN = "Hello.py"
FLOW_VISITED_KEY = "flow_visited_pages"

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
    "pages/2_🔍_Custom_Food_Recommendation.py": "pages/3_🏋️_Workout_Recommendation.py",
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
    "workout_history",
    "meals_logged",
    "totals",
    "daily_goals",
    "daily_goals_custom",
    "daily_goals_source_calories",
    "water_glasses",
    "confirm_clear_meals",
    "meal_plan_autoloaded",
    "meal_plan_loaded_at",
    "auth_session_checked",
    "auth_redirect_target",
    "auth_redirect_message",
    FLOW_VISITED_KEY,
)


def _find_step(path: str) -> tuple[str, str]:
    return next((step for step in FLOW_STEPS if step[1] == path), FLOW_STEPS[0])


def _link_to_page(path: str, label: str, *, key: str) -> None:
    """Render a page link with a button fallback for older Streamlit versions."""
    if hasattr(st, "page_link"):
        try:
            st.page_link(path, label=label)
            return
        except KeyError:
            pass
    if st.button(label, key=key, use_container_width=True):
        st.switch_page(path)


def _mark_page_visited(path: str) -> None:
    visited = list(st.session_state.get(FLOW_VISITED_KEY, []))
    if path not in visited:
        visited.append(path)
    st.session_state[FLOW_VISITED_KEY] = visited


def _coerce_int(value: object, default: int = 0) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def _ensure_meal_log_state() -> None:
    meals_logged = st.session_state.get("meals_logged")
    if not isinstance(meals_logged, list):
        st.session_state.meals_logged = []

    totals = st.session_state.get("totals")
    if not isinstance(totals, dict):
        recalculate_meal_totals()


def recalculate_meal_totals() -> dict:
    """Rebuild macro totals from the visible tracked meal session."""
    meals = [meal for meal in st.session_state.get("meals_logged", []) if isinstance(meal, dict)]
    totals = {
        "calories": sum(_coerce_int(meal.get("calories")) for meal in meals),
        "protein": sum(_coerce_int(meal.get("protein")) for meal in meals),
        "carbs": sum(_coerce_int(meal.get("carbs")) for meal in meals),
        "fat": sum(_coerce_int(meal.get("fat")) for meal in meals),
    }
    st.session_state.totals = totals
    return totals


def sync_water_from_api(water_data: dict | None) -> None:
    """Hydrate water state from the account API payload."""
    if not isinstance(water_data, dict):
        return
    st.session_state.water_glasses = _coerce_int(water_data.get("glasses"))


def _meal_from_api(meal: dict) -> dict:
    saved_at = str(meal.get("saved_at") or meal.get("created_at") or "")
    return {
        "id": meal.get("id"),
        "name": meal.get("meal_name", "Meal"),
        "calories": _coerce_int(meal.get("calories")),
        "protein": _coerce_int(meal.get("protein")),
        "carbs": _coerce_int(meal.get("carbs")),
        "fat": _coerce_int(meal.get("fat")),
        "time": saved_at[-8:-3] if saved_at else "--:--",
    }


def sync_tracked_meals_from_api(meals: list | None) -> None:
    """Hydrate tracked meals from cloud data while preserving local unsynced entries."""
    if not isinstance(meals, list):
        return
    local_meals = [meal for meal in st.session_state.get("meals_logged", []) if isinstance(meal, dict)]
    local_unsynced = [meal for meal in local_meals if not meal.get("id")]

    seen_ids = set()
    synced_meals = []
    for meal in meals:
        if not isinstance(meal, dict):
            continue
        meal_id = meal.get("id")
        if meal_id and meal_id in seen_ids:
            continue
        if meal_id:
            seen_ids.add(meal_id)
        synced_meals.append(_meal_from_api(meal))

    st.session_state.meals_logged = synced_meals + local_unsynced
    recalculate_meal_totals()


def sync_workout_history_from_api(workouts: list | None) -> None:
    """Hydrate recent workouts from cloud data while preserving local optimistic entries."""
    if not isinstance(workouts, list):
        return
    local_workouts = [item for item in st.session_state.get("workout_history", []) if isinstance(item, dict)]
    local_unsynced = [item for item in local_workouts if item.get("_local")]

    seen_keys = set()
    synced_workouts = []
    for item in workouts:
        if not isinstance(item, dict):
            continue
        key = (
            item.get("id"),
            item.get("logged_at"),
            item.get("workout_focus"),
            item.get("duration_minutes"),
        )
        if key in seen_keys:
            continue
        seen_keys.add(key)
        synced_workouts.append(item)

    st.session_state.workout_history = synced_workouts + local_unsynced


def add_workout_to_session(workout_focus: str, exercises: list, duration: int, calories_burned: int, notes: str = "") -> dict:
    """Optimistically update recent workout history after a successful log."""
    history = st.session_state.get("workout_history")
    if not isinstance(history, list):
        history = []
    history.insert(0, {
        "_local": True,
        "workout_focus": workout_focus,
        "exercises_completed": exercises,
        "duration_minutes": duration,
        "calories_burned": calories_burned,
        "notes": notes,
        "logged_at": datetime.now().isoformat(timespec="seconds"),
    })
    st.session_state.workout_history = history[:10]
    return st.session_state.workout_history[0]


def add_tracked_meal_to_session(
    name: str,
    calories: float,
    protein: float,
    carbs: float,
    fat: float,
    *,
    auth_token: str | None = None,
) -> dict:
    """Add a tracked meal from any page and keep local + cloud state in sync."""
    auth_token = auth_token if auth_token is not None else st.session_state.get("auth_token")
    meal_id = None
    cloud_synced = False
    if auth_token:
        save_result = APIClient.save_meal(
            meal_name=name,
            calories=float(calories),
            protein=float(protein),
            carbs=float(carbs),
            fat=float(fat),
            meal_type="tracked",
            auth_token=auth_token,
        )
        handle_auth_expired(save_result)
        if not save_result.get("success"):
            if save_result.get("error") != "Connection failed":
                return save_result
        else:
            cloud_synced = True
            meal_id = save_result.get("data", {}).get("meal_id")

    _ensure_meal_log_state()
    meal = {
        "id": meal_id,
        "name": str(name),
        "calories": _coerce_int(calories),
        "protein": _coerce_int(protein),
        "carbs": _coerce_int(carbs),
        "fat": _coerce_int(fat),
        "time": datetime.now().strftime("%H:%M"),
    }
    st.session_state.meals_logged.append(meal)
    st.session_state.totals["calories"] += meal["calories"]
    st.session_state.totals["protein"] += meal["protein"]
    st.session_state.totals["carbs"] += meal["carbs"]
    st.session_state.totals["fat"] += meal["fat"]
    return {"success": True, "data": meal, "cloud_synced": cloud_synced}


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
    has_workout_plan = bool(st.session_state.get("workout_data") or has_health)
    workout_history = st.session_state.get("workout_history") or []
    tracked_meals = len(meals_logged)
    water_glasses = _coerce_int(st.session_state.get("water_glasses"))
    visited_pages = set(st.session_state.get(FLOW_VISITED_KEY, []))

    return {
        "has_auth": bool(st.session_state.get("auth_token")),
        "username": user_data.get("username") or "account",
        "has_health": has_health,
        "has_workout_plan": has_workout_plan,
        "has_workout_activity": bool(workout_history),
        "tracked_meals": tracked_meals,
        "water_glasses": water_glasses,
        "has_macro_activity": tracked_meals > 0 or water_glasses > 0,
        "planned_meals": planned_meals,
        "has_plan": bool(st.session_state.get("meal_plan_loaded_at")) or planned_meals > 0,
        "visited_pages": visited_pages,
    }


def _step_complete(path: str, state: dict) -> bool:
    if path == "pages/0_🔐_Account.py":
        return state["has_auth"]
    if path == "pages/1_💪_Diet_Recommendation.py":
        return state["has_health"]
    if path == "pages/3_🏋️_Workout_Recommendation.py":
        return state["has_workout_activity"]
    if path == "pages/4_📊_Macro_Tracker.py":
        return state["has_macro_activity"]
    if path == "pages/5_📅_Meal_Planner.py":
        return state["has_plan"]
    return False


def _core_flow_checks(state: dict) -> tuple[tuple[str, bool], ...]:
    """Milestones that represent actual user progress, not just navigation."""
    return (
        ("Account", state["has_auth"]),
        ("Health", state["has_health"]),
        ("Workout", state["has_workout_activity"]),
        ("Daily log", state["has_macro_activity"]),
        ("Weekly plan", state["has_plan"]),
    )


def _step_status(path: str, state: dict, active_page: str) -> tuple[str, str]:
    """Return visual class and short status label for a flow step."""
    if path == active_page:
        return "active", "Current"
    if _step_complete(path, state):
        return "done", "Done"
    if path in state["visited_pages"]:
        return "visited", "Visited"
    if not state["has_auth"] and path != AUTH_PAGE:
        return "blocked", "Sign in first"
    if path == "pages/2_🔍_Custom_Food_Recommendation.py" and state["has_health"]:
        return "ready", "Ready"
    if path == "pages/3_🏋️_Workout_Recommendation.py" and state["has_workout_plan"]:
        return "ready", "Ready"
    if path in ("pages/4_📊_Macro_Tracker.py", "pages/5_📅_Meal_Planner.py") and state["has_health"]:
        return "ready", "Ready"
    if path in (
        "pages/2_🔍_Custom_Food_Recommendation.py",
        "pages/3_🏋️_Workout_Recommendation.py",
        "pages/4_📊_Macro_Tracker.py",
        "pages/5_📅_Meal_Planner.py",
    ):
        return "blocked", "Health first"
    return "ready", "Ready"


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
    if active_page == "pages/2_🔍_Custom_Food_Recommendation.py" and not state["has_workout_activity"]:
        return "pages/3_🏋️_Workout_Recommendation.py", "Log one workout so fitness progress joins your nutrition flow."
    if active_page == "pages/3_🏋️_Workout_Recommendation.py" and not state["has_workout_activity"]:
        return "pages/3_🏋️_Workout_Recommendation.py", "Log today's workout to complete the fitness step."
    if not state["has_workout_activity"]:
        return "pages/3_🏋️_Workout_Recommendation.py", "Log one workout so the complete health flow is covered."
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
    _mark_page_visited(active_page)
    state = _session_flow_state()
    current_label, _ = _find_step(active_page)
    checks = _core_flow_checks(state)
    completed_steps = sum(1 for _, complete in checks if complete)
    progress_pct = round(completed_steps / max(len(checks), 1) * 100)
    sync_label = escape(f"@{state['username']}" if state["has_auth"] else "offline")
    next_path, next_reason = _recommended_step(active_page, state)
    next_label = _find_step(next_path)[0] if next_path else (
        "Sign in / Sign up" if not state["has_auth"] and active_page == AUTH_PAGE else current_label
    )
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
                    <span>{completed_steps}/{len(checks)} done</span>
                </div>
            </div>
            <div class="flow-progress" aria-label="Workflow completion">
                <div class="flow-progress-fill" style="width: {progress_pct}%;"></div>
            </div>
            <div class="flow-badges">
                <span>☁️ Sync: {sync_label}</span>
                <span>💪 Health: {'ready' if state['has_health'] else 'needed'}</span>
                <span>🍽️ Meals: {state['tracked_meals']}</span>
                <span>🏋️ Workouts: {'logged' if state['has_workout_activity'] else 'open'}</span>
                <span>💧 Water: {state['water_glasses']}</span>
                <span>📅 Plan: {'ready' if state['has_plan'] else 'open'}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    step_cards = []
    for idx, (label, path) in enumerate(FLOW_STEPS):
        state_class, status = _step_status(path, state, active_page)
        classes = ["flow-step-card", state_class]
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
                state_class, _ = _step_status(path, state, active_page)
                display = f"✓ {label}" if state_class == "done" and path != active_page else label
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
