"""
TARG - Workout Recommendation Page
Premium Healthcare UI with BMI Visualization
"""
import streamlit as st
import plotly.graph_objects as go
import requests
import time
from pathlib import Path
from api import APIClient, BASE_URL
from ui.polish import inject_ui_polish
from ui.ux import handle_auth_expired, require_login

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Workout Recommendation - TARG",
    page_icon="🏋️",
    layout="wide"
)

LOGO_PATH = Path(__file__).parent.parent / "logo.png"

require_login("pages/3_🏋️_Workout_Recommendation.py")

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
    
    /* Fix text visibility */
    p, span, div, label {
        color: #333333 !important;
    }
    
    .stMarkdown, .stText, .stSelectbox label, .stNumberInput label {
        color: #333333 !important;
    }
    
    /* Page Header */
    .page-header {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 15px 40px rgba(76, 175, 80, 0.25);
    }
    
    .page-header *, .page-header .page-title, .page-header .page-subtitle {
        color: #FFFFFF !important;
    }
    
    .page-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FFFFFF !important;
        margin: 0;
    }
    
    .page-subtitle {
        color: rgba(255,255,255,0.9) !important;
        margin-top: 8px;
        font-size: 1.1rem;
    }
    
    /* White text inside green elements */
    .bmi-normal, .bmi-underweight, .bmi-overweight, .bmi-obese { color: white !important; }
    .workout-card, .workout-card * { color: white !important; }
    .exercise-item, .exercise-item * { color: white !important; }
    .exercise-number { color: white !important; }
    .schedule-day.active, .schedule-day.active * { color: white !important; }
    .calorie-card.primary, .calorie-card.primary * { color: white !important; }
    .tips-box, .tips-box * { color: #333333 !important; }
    .stButton > button, .stButton > button * { color: white !important; }
    
    /* Cards */
    .card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid rgba(76, 175, 80, 0.1);
        margin-bottom: 20px;
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2E7D32 !important;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* BMI Category Badges */
    .bmi-badge {
        display: inline-block;
        padding: 10px 24px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1rem;
        margin: 10px 0;
    }
    
    .bmi-normal { background: linear-gradient(135deg, #4CAF50, #2E7D32); color: white; }
    .bmi-underweight { background: linear-gradient(135deg, #FFA726, #F57C00); color: white; }
    .bmi-overweight { background: linear-gradient(135deg, #FF7043, #E64A19); color: white; }
    .bmi-obese { background: linear-gradient(135deg, #EF5350, #C62828); color: white; }
    
    /* Workout Card */
    .workout-card {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        border-radius: 16px;
        padding: 30px;
        color: white;
        margin: 20px 0;
    }
    
    .workout-focus {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 20px;
    }
    
    .exercise-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .exercise-item {
        background: rgba(255,255,255,0.15);
        border-radius: 10px;
        padding: 14px 18px;
        margin: 10px 0;
        display: flex;
        align-items: center;
        gap: 12px;
        backdrop-filter: blur(10px);
    }
    
    .exercise-number {
        background: rgba(255,255,255,0.25);
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
    }
    
    /* Schedule Grid */
    .schedule-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 8px;
        margin: 20px 0;
    }
    
    .schedule-day {
        text-align: center;
        padding: 16px 8px;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    .schedule-day.active {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    
    .schedule-day.rest {
        background: #F5F5F5;
        color: #666;
    }
    
    .day-name {
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 8px;
    }
    
    .day-activity {
        font-size: 0.75rem;
        opacity: 0.9;
    }
    
    /* Calorie Cards */
    .calorie-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 16px 0;
    }
    
    .calorie-card {
        background: #F5F5F5;
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .calorie-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }
    
    .calorie-card.primary {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
    }
    
    .calorie-value {
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .calorie-label {
        font-size: 0.75rem;
        margin-top: 4px;
        opacity: 0.85;
    }
    
    /* Tips Box */
    .tips-box {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-left: 4px solid #4CAF50;
        border-radius: 0 12px 12px 0;
        padding: 20px;
        margin: 20px 0;
    }
    
    /* Button overrides */
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
</style>
""", unsafe_allow_html=True)
inject_ui_polish()

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=160)
    st.markdown("---")
    
    # Auth status
    if 'auth_token' in st.session_state and st.session_state.auth_token:
        user = st.session_state.get('user_data', {})
        st.success(f"✅ **{user.get('username', 'User')}**")
    else:
        st.caption("🔐 Login to save workout logs")
    
    st.markdown("---")
    st.markdown("### 🏋️ Workout Plans")
    st.caption("Personalized exercise recommendations based on your BMI and health goals.")
    st.markdown("---")
    
    if 'health_data' in st.session_state and st.session_state.health_data:
        data = st.session_state.health_data
        st.success(f"✅ Health data loaded (BMI: {data.get('bmi', 'N/A')})")
    else:
        st.info("💡 Your workout plan adapts to your BMI category for safe, effective results.")

# ═══════════════════════════════════════════════════════════════
# PAGE HEADER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-header">
    <h1 class="page-title">🏋️ Personalized Workout Plan</h1>
    <p class="page-subtitle">Exercise recommendations tailored to your body metrics</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
if 'workout_data' not in st.session_state:
    # Auto-load from health analysis if it's already done
    if 'health_data' in st.session_state and st.session_state.health_data:
        st.session_state.workout_data = st.session_state.health_data
    else:
        st.session_state.workout_data = None

# ═══════════════════════════════════════════════════════════════
# LAYOUT
# ═══════════════════════════════════════════════════════════════
input_col, results_col = st.columns([1, 2])

# ═══════════════════════════════════════════════════════════════
# INPUT FORM
# ═══════════════════════════════════════════════════════════════
with input_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📋 Your Details</div>', unsafe_allow_html=True)
    
    with st.form("workout_form"):
        age = st.number_input("Age", 10, 100, 25)
        height = st.number_input("Height (cm)", 100, 250, 170)
        weight = st.number_input("Weight (kg)", 30, 250, 70)
        gender = st.selectbox("Gender", ["male", "female"], format_func=str.capitalize)
        activity = st.select_slider(
            "Activity Level",
            options=["sedentary", "light", "moderate", "active", "extra_active"],
            value="moderate",
            format_func=lambda x: x.replace("_", " ").title()
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.form_submit_button("🔍 Analyze & Get Plan", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# PROCESS
# ═══════════════════════════════════════════════════════════════
if analyze_btn:
    with st.spinner("🔬 Analyzing your health metrics..."):
        time.sleep(0.5)
        
        auth_token = st.session_state.get('auth_token')
        result = APIClient.health_analysis(age, height, weight, gender, activity, auth_token)
        
        if result["success"]:
            st.session_state.workout_data = result["data"]
            st.session_state.health_data = result["data"]  # Sync across pages
        else:
            from api import HealthCalculator
            bmi = HealthCalculator.calculate_bmi(weight, height)
            category = HealthCalculator.get_bmi_category(bmi)
            bmr = HealthCalculator.calculate_bmr(weight, height, age, gender)
            calories = HealthCalculator.calculate_tdee(bmr, activity)
            workout = HealthCalculator.get_workout_plan(category["category"])
            
            st.session_state.workout_data = {
                "bmi": bmi, "bmi_category": category, "bmr": bmr,
                "daily_calories": calories, "workout_plan": workout
            }
            st.session_state.health_data = st.session_state.workout_data
        
        st.success("✅ Analysis complete!")
        st.rerun()

# ═══════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════
with results_col:
    if st.session_state.workout_data:
        data = st.session_state.workout_data
        category = data["bmi_category"]["category"]
        
        # ─── BMI GAUGE ───
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 Your BMI Analysis</div>', unsafe_allow_html=True)
        
        # Plotly Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=data["bmi"],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Body Mass Index", 'font': {'size': 18, 'family': 'Inter', 'color': '#333'}},
            number={'font': {'size': 48, 'color': '#2E7D32', 'family': 'Inter'}},
            gauge={
                'axis': {'range': [10, 40], 'tickwidth': 1, 'tickcolor': '#666', 'tickfont': {'size': 12}},
                'bar': {'color': "#4CAF50", 'thickness': 0.3},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#E0E0E0",
                'steps': [
                    {'range': [10, 18.5], 'color': "#FFF3E0"},
                    {'range': [18.5, 25], 'color': "#E8F5E9"},
                    {'range': [25, 30], 'color': "#FBE9E7"},
                    {'range': [30, 40], 'color': "#FFEBEE"}
                ],
                'threshold': {'line': {'color': "#2E7D32", 'width': 4}, 'thickness': 0.8, 'value': data["bmi"]}
            }
        ))
        fig.update_layout(
            height=280,
            font_family="Inter",
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Category badge
        bmi_class = f"bmi-{category.lower()}"
        st.markdown(f"""
        <div style="text-align: center;">
            <span class="bmi-badge {bmi_class}">{category}</span>
            <p style="color: #666; margin-top: 8px;">{data["bmi_category"]["status"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ─── CALORIE TARGETS ───
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🎯 Daily Calorie Targets</div>', unsafe_allow_html=True)
        
        cals = data["daily_calories"]
        st.markdown(f"""
        <div class="calorie-grid">
            <div class="calorie-card">
                <div class="calorie-value">{cals["weight_loss"]}</div>
                <div class="calorie-label">Weight Loss</div>
            </div>
            <div class="calorie-card">
                <div class="calorie-value">{cals["mild_loss"]}</div>
                <div class="calorie-label">Mild Loss</div>
            </div>
            <div class="calorie-card primary">
                <div class="calorie-value">{cals["maintenance"]}</div>
                <div class="calorie-label">Maintain</div>
            </div>
            <div class="calorie-card">
                <div class="calorie-value">{cals["weight_gain"]}</div>
                <div class="calorie-label">Weight Gain</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ─── WORKOUT PLAN ───
        workout = data["workout_plan"]
        
        st.markdown(f"""
        <div class="workout-card">
            <div class="workout-focus">🎯 {workout["focus"]}</div>
        """, unsafe_allow_html=True)
        
        for i, ex in enumerate(workout["exercises"], 1):
            st.markdown(f"""
            <div class="exercise-item">
                <div class="exercise-number">{i}</div>
                <div>{ex}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tips
        st.markdown(f"""
        <div class="tips-box">
            <strong>💡 Pro Tip:</strong> {workout["tips"]}
        </div>
        """, unsafe_allow_html=True)
        
        # ─── WEEKLY SCHEDULE ───
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📅 Sample Weekly Schedule</div>', unsafe_allow_html=True)
        
        schedules = {
            "Normal": {"Mon": "Strength", "Tue": "Cardio", "Wed": "HIIT", "Thu": "Rest", "Fri": "Strength", "Sat": "Yoga", "Sun": "Rest"},
            "Underweight": {"Mon": "Weights", "Tue": "Rest", "Wed": "Weights", "Thu": "Rest", "Fri": "Weights", "Sat": "Walk", "Sun": "Rest"},
            "Overweight": {"Mon": "Cardio", "Tue": "Walk", "Wed": "Cardio", "Thu": "Weights", "Fri": "Cardio", "Sat": "Active", "Sun": "Rest"},
            "Obese": {"Mon": "Walk", "Tue": "Rest", "Wed": "Water", "Thu": "Rest", "Fri": "Walk", "Sat": "Stretch", "Sun": "Rest"}
        }
        
        schedule = schedules.get(category, schedules["Normal"])
        
        schedule_html = '<div class="schedule-grid">'
        for day, activity_name in schedule.items():
            is_rest = activity_name == "Rest"
            day_class = "rest" if is_rest else "active"
            schedule_html += f"""
            <div class="schedule-day {day_class}">
                <div class="day-name">{day}</div>
                <div class="day-activity">{activity_name}</div>
            </div>
            """
        schedule_html += '</div>'
        
        st.markdown(schedule_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ─── EXERCISE CALORIE CALCULATOR ───
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🔥 Exercise Calorie Calculator</div>', unsafe_allow_html=True)
        st.caption("Select an exercise and get a science-based calorie estimate using MET values.")
        
        ex_data = APIClient.get_exercises()
        if ex_data["success"] and ex_data["data"].get("exercises"):
            exercises = ex_data["data"]["exercises"]
            categories = ex_data["data"].get("categories", [])
            
            ex_cat = st.selectbox("Category", ["All"] + categories, key="ex_cat_sel")
            if ex_cat != "All":
                exercises = [e for e in exercises if e["category"] == ex_cat]
            
            ex_names = [e["name"] for e in exercises]
            selected_exercise = st.selectbox("Exercise", ex_names, key="ex_name_sel")
            
            ec1, ec2 = st.columns(2)
            with ec1:
                ex_weight = st.number_input("Your Weight (kg)", 30, 200, int(weight) if 'weight' in dir() else 70, key="ex_weight")
            with ec2:
                ex_duration = st.number_input("Duration (min)", 5, 180, 30, step=5, key="ex_dur")
            
            if st.button("🔥 Calculate Calories", use_container_width=True, key="calc_cal_btn"):
                cal_result = APIClient.estimate_exercise_calories(selected_exercise, float(ex_weight), ex_duration)
                if cal_result["success"] and cal_result["data"]:
                    d = cal_result["data"]
                    st.session_state["_est_calories"] = d["calories_burned"]
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%); border-radius: 14px; padding: 24px; text-align: center; margin: 12px 0;">
                        <div style="color: white !important; font-size: 2.5rem; font-weight: 800;">{d['calories_burned']} kcal</div>
                        <div style="color: rgba(255,255,255,0.9) !important; margin-top: 4px;">{d['exercise']} · {d['duration_minutes']} min · MET {d['met']}</div>
                        <div style="color: rgba(255,255,255,0.7) !important; font-size: 0.8rem; margin-top: 8px;">Source: {d['source']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Could not calculate. Try again.")
        else:
            st.info("Exercise database unavailable. Start the backend to access the exercise library.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ─── LOG WORKOUT ───
        auth_token = st.session_state.get('auth_token')
        if auth_token:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">✅ Log a Workout</div>', unsafe_allow_html=True)
            
            est_cals = st.session_state.get("_est_calories", 200)
            with st.form("log_workout_form"):
                wc1, wc2 = st.columns(2)
                with wc1:
                    wo_duration = st.number_input("Duration (minutes)", 5, 180, 30, step=5)
                with wc2:
                    wo_calories = st.number_input("Calories Burned", 50, 2000, int(est_cals), step=25)
                wo_notes = st.text_input("Notes (optional)", placeholder="e.g., Felt good, increased weight")
                
                if st.form_submit_button("✅ Log This Workout", use_container_width=True):
                    result = APIClient.log_workout(
                        workout_focus=workout["focus"],
                        exercises=workout["exercises"],
                        duration=wo_duration,
                        calories_burned=wo_calories,
                        notes=wo_notes,
                        auth_token=auth_token
                    )
                    handle_auth_expired(result)
                    if result["success"]:
                        st.success("✅ Workout logged successfully!")
                        st.balloons()
                    else:
                        st.error(result.get("error", "Failed to log workout"))
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # ─── WORKOUT HISTORY ───
            history = APIClient.get_workout_history(auth_token, limit=5)
            handle_auth_expired(history)
            if history["success"] and history["data"]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title">📋 Recent Workouts</div>', unsafe_allow_html=True)
                
                for log in history["data"]:
                    log_date = log.get("logged_at", "")[:10]
                    st.markdown(f"""
                    <div style="padding: 12px; background: #F8FFF8; border-radius: 10px; margin-bottom: 8px; border-left: 3px solid #4CAF50;">
                        <strong style="color: #2E7D32 !important;">{log.get('workout_focus', '')}</strong>
                        <span style="color: #666; float: right;">{log_date}</span><br>
                        <span style="color: #666;">⏱ {log.get('duration_minutes', 0)} min · 🔥 {log.get('calories_burned', 0)} kcal</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Disclaimer
        st.warning("⚠️ **Medical Disclaimer:** Consult a healthcare professional before starting any exercise program.")
        
    else:
        # Empty state
        st.markdown("""
        <div class="card" style="text-align: center; padding: 60px;">
            <div style="font-size: 4rem; margin-bottom: 20px;">🏋️</div>
            <h3 style="color: #333;">Ready for your workout plan?</h3>
            <p style="color: #666;">Enter your details and click <strong>Analyze & Get Plan</strong> to receive personalized exercise recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
