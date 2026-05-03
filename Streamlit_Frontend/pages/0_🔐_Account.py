"""
TARG - Login & Signup Page
Premium Authentication Flow
"""
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path
from api import APIClient
from ui.polish import inject_ui_polish
from ui.safe import escape_html
from ui.ux import (
    add_tracked_meal_to_session,
    clear_user_session,
    consume_auth_redirect,
    ensure_session_fresh,
    handle_auth_expired,
    render_auth_redirect_notice,
    render_flow_status,
    sync_tracked_meals_from_api,
    sync_water_from_api,
    sync_workout_history_from_api,
)

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Account - TARG",
    page_icon="🔐",
    layout="wide"
)

LOGO_PATH = Path(__file__).parent.parent / "logo.png"

# ═══════════════════════════════════════════════════════════════
# PREMIUM CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FFF8 100%);
        color: #333333;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    p, span, div, label { color: #333333 !important; }
    .stMarkdown, .stText { color: #333333 !important; }
    
    .auth-header {
        text-align: center;
        padding: 40px 30px;
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        border-radius: 24px;
        margin-bottom: 30px;
        box-shadow: 0 15px 40px rgba(76, 175, 80, 0.25);
    }
    
    .auth-header *, .auth-header h1, .auth-header p {
        color: #FFFFFF !important;
    }
    
    .auth-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: white !important;
        margin: 0;
    }
    
    .auth-subtitle {
        color: rgba(255,255,255,0.9) !important;
        margin-top: 8px;
        font-size: 1rem;
    }
    
    .auth-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid rgba(76, 175, 80, 0.1);
    }
    
    .success-banner {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .success-banner * { color: white !important; }
    
    .user-badge {
        display: inline-block;
        background: rgba(76, 175, 80, 0.1);
        border: 1px solid rgba(76, 175, 80, 0.3);
        border-radius: 10px;
        padding: 12px 20px;
        margin: 5px 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    .stButton > button * { color: white !important; }
</style>
""", unsafe_allow_html=True)
inject_ui_polish()

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

if st.session_state.auth_token:
    ensure_session_fresh()

account_water_result = None
account_tracked_result = None
account_workouts_result = None
if st.session_state.auth_token:
    account_water_result = APIClient.get_water(st.session_state.auth_token)
    handle_auth_expired(account_water_result)
    if account_water_result.get("success"):
        sync_water_from_api(account_water_result.get("data"))

    account_tracked_result = APIClient.get_saved_meals(st.session_state.auth_token, meal_type="tracked", limit=50)
    handle_auth_expired(account_tracked_result)
    if account_tracked_result.get("success"):
        sync_tracked_meals_from_api(account_tracked_result.get("data"))

    account_workouts_result = APIClient.get_workout_history(st.session_state.auth_token, limit=5)
    handle_auth_expired(account_workouts_result)
    if account_workouts_result.get("success"):
        sync_workout_history_from_api(account_workouts_result.get("data"))

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=160)
    st.markdown("---")
    st.markdown("### 🔐 Authentication")
    
    if st.session_state.auth_token:
        user = st.session_state.user_data
        st.success(f"✅ Logged in as **{user.get('username', '')}**")
        if st.button("🚪 Logout", width="stretch"):
            clear_user_session()
            st.rerun()
    else:
        st.caption("Login or create an account to save your data.")

# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="auth-header">
    <div class="auth-title">🔐 Welcome to TARG</div>
    <div class="auth-subtitle">Login or create an account to save your health data</div>
</div>
""", unsafe_allow_html=True)

render_flow_status("pages/0_🔐_Account.py")

# ═══════════════════════════════════════════════════════════════
# LOGGED IN VIEW
# ═══════════════════════════════════════════════════════════════
if st.session_state.auth_token:
    user = st.session_state.user_data
    pending_target = st.session_state.get("auth_redirect_target")
    display_name = escape_html(user.get('full_name') or user.get('username') or 'User', 120)
    
    st.markdown(f"""
    <div class="success-banner">
        <div style="font-size: 2rem;">✅</div>
        <div style="font-size: 1.3rem; font-weight: 700; margin-top: 8px;">Welcome, {display_name}!</div>
        <div style="margin-top: 6px; opacity: 0.9;">Your data is being saved automatically.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown("#### 👤 Your Profile")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Username:** {user.get('username', '')}")
        st.markdown(f"**Email:** {user.get('email', '')}")
    with col2:
        st.markdown(f"**Full Name:** {user.get('full_name', '-')}")
    
    st.markdown('</div>', unsafe_allow_html=True)

    if pending_target:
        if st.button("Continue where you left off", width="stretch", type="primary"):
            st.switch_page(consume_auth_redirect())
    
    # User stats via APIClient
    stats_result = APIClient.get_user_stats(st.session_state.auth_token)
    handle_auth_expired(stats_result)
    if stats_result["success"]:
        stats = stats_result["data"]
        st.markdown("---")
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("🔬 Health Analyses", stats.get("total_health_analyses", 0))
        sc2.metric("🍽️ Saved Meals", stats.get("total_saved_meals", 0))
        sc3.metric("🏋️ Workouts", stats.get("total_workouts", 0))

    # Synced daily water and tracked meals, matching the Android account overview.
    st.markdown("---")
    st.markdown("### 💧 Today’s Water")
    water = account_water_result or APIClient.get_water(st.session_state.auth_token)
    handle_auth_expired(water)
    if water["success"]:
        wd = water["data"]
        glasses = int(wd.get("glasses", 0))
        goal_ml = int(wd.get("goal_ml", 2500) or 2500)
        pct = int(wd.get("percent", 0) or 0)
        st.progress(min(max(pct, 0), 100) / 100)
        st.caption(f"{glasses} glasses · {glasses * 250}ml / {goal_ml}ml")
    else:
        st.info("Water tracking will appear here after you log it from Macro Tracker.")

    st.markdown("### 🍽️ Recent Tracked Meals")
    tracked = account_tracked_result or APIClient.get_saved_meals(st.session_state.auth_token, meal_type="tracked", limit=50)
    handle_auth_expired(tracked)
    if tracked["success"] and tracked["data"]:
        for meal in tracked["data"][:5]:
            m_name = escape_html(meal.get('meal_name', 'Meal'), 80)
            m_date = escape_html(str(meal.get('saved_at') or meal.get('created_at', ''))[:16])
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid rgba(76,175,80,0.15); border-radius: 12px; padding: 14px; margin-bottom: 8px; border-left: 4px solid #D9F0DF;">
                <strong style="color: #000000 !important;">{m_name}</strong>
                <span style="color: #647067; float: right;">{m_date}</span><br>
                <span style="color: #647067;">🔥 {int(meal.get('calories', 0))} kcal · 💪 {round(meal.get('protein', 0), 1)}g · 🌾 {round(meal.get('carbs', 0), 1)}g · 🥑 {round(meal.get('fat', 0), 1)}g</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No tracked meals yet. Add meals from the Macro Tracker.")
    
    # Quick actions
    st.markdown("---")
    quick_actions = [
        ("💪 Health Analysis", "pages/1_💪_Diet_Recommendation.py", "primary"),
        ("🔍 Search Recipes", "pages/2_🔍_Custom_Food_Recommendation.py", "secondary"),
        ("🏋️ Workouts", "pages/3_🏋️_Workout_Recommendation.py", "secondary"),
        ("📊 Track Macros", "pages/4_📊_Macro_Tracker.py", "secondary"),
        ("📅 Meal Planner", "pages/5_📅_Meal_Planner.py", "secondary"),
    ]
    for row_start in range(0, len(quick_actions), 3):
        cols = st.columns(3)
        for col, (label, target, button_type) in zip(cols, quick_actions[row_start:row_start + 3]):
            with col:
                if st.button(label, width="stretch", type=button_type):
                    st.switch_page(target)
    
    # ═══════════════════════════════════════════════════════════════
    # HEALTH HISTORY CHART
    # ═══════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### 📈 Health Progress")
    
    trend = APIClient.get_health_trend(st.session_state.auth_token)
    handle_auth_expired(trend)
    if trend["success"] and trend["data"]:
        trend_data = trend["data"]
        dates = [d["date"] for d in trend_data]
        bmis = [d["bmi"] for d in trend_data]
        weights = [d["weight"] for d in trend_data]
        calories = [d["calories"] for d in trend_data]
        
        tab_bmi, tab_weight, tab_cal = st.tabs(["📊 BMI Trend", "⚖️ Weight", "🔥 Calories"])
        
        with tab_bmi:
            fig_bmi = go.Figure()
            fig_bmi.add_trace(go.Scatter(x=dates, y=bmis, mode='lines+markers',
                line=dict(color='#4CAF50', width=3), marker=dict(size=8, color='#2E7D32'),
                name='BMI', fill='tozeroy', fillcolor='rgba(76,175,80,0.1)'))
            # Add healthy range band
            fig_bmi.add_hrect(y0=18.5, y1=25, fillcolor='rgba(76,175,80,0.08)', line_width=0,
                annotation_text='Healthy Range', annotation_position='top left')
            fig_bmi.update_layout(height=300, margin=dict(l=20,r=20,t=30,b=20),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False), yaxis=dict(title='BMI', gridcolor='rgba(0,0,0,0.05)'),
                font_family='Inter')
            st.plotly_chart(fig_bmi, width="stretch")
        
        with tab_weight:
            fig_w = go.Figure()
            fig_w.add_trace(go.Scatter(x=dates, y=weights, mode='lines+markers',
                line=dict(color='#2196F3', width=3), marker=dict(size=8, color='#1565C0'),
                name='Weight (kg)', fill='tozeroy', fillcolor='rgba(33,150,243,0.1)'))
            fig_w.update_layout(height=300, margin=dict(l=20,r=20,t=30,b=20),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False), yaxis=dict(title='Weight (kg)', gridcolor='rgba(0,0,0,0.05)'),
                font_family='Inter')
            st.plotly_chart(fig_w, width="stretch")
        
        with tab_cal:
            fig_c = go.Figure()
            fig_c.add_trace(go.Bar(x=dates, y=calories,
                marker_color='#FF9800', name='Maintenance Calories'))
            fig_c.update_layout(height=300, margin=dict(l=20,r=20,t=30,b=20),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False), yaxis=dict(title='kcal/day', gridcolor='rgba(0,0,0,0.05)'),
                font_family='Inter')
            st.plotly_chart(fig_c, width="stretch")
    else:
        st.info("📊 Run a **Health Analysis** from the Diet page to start tracking your progress over time.")
    
    # ═══════════════════════════════════════════════════════════════
    # SAVED RECIPES GALLERY
    # ═══════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### ⭐ Saved Recipes")
    
    saved = APIClient.get_saved_meals(st.session_state.auth_token, meal_type="saved", limit=50)
    handle_auth_expired(saved)
    if saved["success"] and saved["data"]:
        for idx, meal in enumerate(saved["data"]):
            m_name = escape_html(meal.get('meal_name', 'Recipe'), 50)
            m_cal = int(meal.get('calories', 0))
            m_pro = round(meal.get('protein', 0), 1)
            m_carb = round(meal.get('carbs', 0), 1)
            m_fat = round(meal.get('fat', 0), 1)
            m_date = escape_html(str(meal.get('saved_at') or meal.get('created_at', ''))[:10])
            
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid rgba(76,175,80,0.15); border-radius: 12px; padding: 16px; margin-bottom: 10px; border-left: 4px solid #4CAF50;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: #2E7D32 !important; font-size: 1.05rem;">⭐ {m_name}</strong><br>
                        <span style="color: #666;">🔥 {m_cal} kcal · 💪 {m_pro}g protein · 🌾 {m_carb}g carbs · 🥑 {m_fat}g fat</span>
                    </div>
                    <span style="color: #999; font-size: 0.8rem;">{m_date}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("➕ Add saved recipe to Macro Tracker", key=f"track_saved_recipe_{meal.get('id') or idx}", width="stretch"):
                track_result = add_tracked_meal_to_session(meal.get('meal_name', 'Recipe'), m_cal, m_pro, m_carb, m_fat)
                if track_result.get("success"):
                    st.success(f"Added to Macro Tracker: {m_name}")
                    if hasattr(st, "page_link"):
                        st.page_link("pages/4_📊_Macro_Tracker.py", label="Open Macro Tracker")
                else:
                    st.error(track_result.get("error", "Could not add to tracker"))
    else:
        st.info("⭐ No saved recipes yet. Search for recipes and click **Save** to bookmark them here.")
    
    # ═══════════════════════════════════════════════════════════════
    # RECENT WORKOUTS
    # ═══════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### 🏋️ Recent Workouts")
    
    workouts = account_workouts_result or APIClient.get_workout_history(st.session_state.auth_token, limit=5)
    handle_auth_expired(workouts)
    recent_workouts = st.session_state.get("workout_history") if workouts.get("success") else None
    if recent_workouts:
        for log in recent_workouts[:5]:
            log_focus = escape_html(log.get('workout_focus', ''), 80)
            log_date = escape_html(str(log.get('logged_at', ''))[:10])
            st.markdown(f"""
            <div style="background: #F8FFF8; border-radius: 10px; padding: 14px; margin-bottom: 8px; border-left: 3px solid #4CAF50;">
                <strong style="color: #2E7D32 !important;">{log_focus}</strong>
                <span style="color: #666; float: right;">{log_date}</span><br>
                <span style="color: #666;">⏱ {log.get('duration_minutes', 0)} min · 🔥 {log.get('calories_burned', 0)} kcal</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🏋️ No workouts logged yet. Head to the **Workout** page to log your first session.")

# ═══════════════════════════════════════════════════════════════
# LOGIN / SIGNUP FORMS
# ═══════════════════════════════════════════════════════════════
else:
    render_auth_redirect_notice()
    tab_login, tab_signup = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    # ─── LOGIN ───
    with tab_login:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        
        with st.form("login_form"):
            login_username = st.text_input("Username or email", placeholder="Enter your username or email")
            login_password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            if st.form_submit_button("🔑 Login", width="stretch"):
                if login_username and login_password:
                    result = APIClient.login(login_username, login_password)
                    if result["success"]:
                        data = result["data"]
                        st.session_state.auth_token = data["access_token"]
                        st.session_state.user_data = data["user"]
                        st.session_state.auth_session_checked = True
                        st.success("✅ Login successful!")
                        st.switch_page(consume_auth_redirect())
                    else:
                        st.error(f"❌ {result['error']}")
                else:
                    st.warning("Please fill in all fields")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ─── SIGNUP ───
    with tab_signup:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        
        with st.form("signup_form"):
            signup_fullname = st.text_input("Full Name", placeholder="Your full name")
            signup_email = st.text_input("Email", placeholder="you@example.com")
            signup_username = st.text_input("Choose Username", placeholder="3-32 letters, numbers, _, . or -")
            signup_password = st.text_input("Choose Password", type="password", placeholder="Min 8 characters, include a number")
            signup_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
            
            if st.form_submit_button("📝 Create Account", width="stretch"):
                if not all([signup_fullname, signup_email, signup_username, signup_password]):
                    st.warning("Please fill in all fields")
                elif len(signup_password) < 8:
                    st.warning("Password must be at least 8 characters")
                elif not any(ch.isalpha() for ch in signup_password) or not any(ch.isdigit() for ch in signup_password):
                    st.warning("Password must include at least one letter and one number")
                elif signup_password != signup_confirm:
                    st.error("Passwords don't match")
                else:
                    result = APIClient.signup(signup_email, signup_username, signup_password, signup_fullname)
                    if result["success"]:
                        data = result["data"]
                        st.session_state.auth_token = data["access_token"]
                        st.session_state.user_data = data["user"]
                        st.session_state.auth_session_checked = True
                        st.success("✅ Account created!")
                        st.balloons()
                        st.switch_page(consume_auth_redirect())
                    else:
                        st.error(f"Error: {result['error']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Benefits callout
    st.markdown("---")
    st.markdown("#### ✨ Why create an account?")
    bc1, bc2, bc3 = st.columns(3)
    bc1.markdown("💾 **Save Data**\nYour health analyses are saved automatically")
    bc2.markdown("📊 **Track Progress**\nView your BMI and calorie history over time")
    bc3.markdown("🍽️ **Bookmark Meals**\nSave your favorite recipes for later")
