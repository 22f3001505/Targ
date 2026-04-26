"""
TARG - Macro Tracker Page
Premium Interactive Nutrition Tracking
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import requests
from pathlib import Path
from datetime import datetime
from api import APIClient, BASE_URL

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Macro Tracker - TARG",
    page_icon="📊",
    layout="wide"
)

LOGO_PATH = Path(__file__).parent.parent / "logo.png"

if not st.session_state.get("auth_token"):
    st.switch_page("pages/0_🔐_Account.py")

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
    
    .stMarkdown, .stText, .stSelectbox label, .stNumberInput label, .stSlider label {
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
    .summary-card, .summary-card * { color: white !important; }
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
    }
    
    /* Goal Cards */
    .goal-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin: 20px 0;
    }
    
    .goal-card {
        background: linear-gradient(135deg, #A5D6A7 0%, #C8E6C9 100%);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
    }
    
    .goal-icon {
        font-size: 2rem;
        margin-bottom: 8px;
    }
    
    .goal-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2E7D32 !important;
    }
    
    .goal-label {
        font-size: 0.85rem;
        color: #333333 !important;
        margin-top: 4px;
    }
    
    /* Progress Bars */
    .progress-container {
        margin: 16px 0;
    }
    
    .progress-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    
    .progress-label {
        font-weight: 600;
        color: #333;
    }
    
    .progress-value {
        color: #4CAF50;
        font-weight: 600;
    }
    
    .progress-bar {
        height: 12px;
        background: #E8F5E9;
        border-radius: 6px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease;
    }
    
    /* Meal Log */
    .meal-item {
        background: #FFFFFF;
        border: 1px solid rgba(76, 175, 80, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.3s ease;
    }
    
    .meal-item:hover {
        transform: translateX(8px);
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.1);
        border-color: #4CAF50;
    }
    
    .meal-name {
        font-weight: 600;
        color: #333;
    }
    
    .meal-macros {
        display: flex;
        gap: 16px;
    }
    
    .macro-tag {
        background: #E8F5E9;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #2E7D32;
        font-weight: 500;
    }
    
    /* Summary Stats */
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
    }
    
    .summary-card {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        border-radius: 14px;
        padding: 24px;
        color: white;
        text-align: center;
    }
    
    .summary-value {
        font-size: 2.5rem;
        font-weight: 800;
    }
    
    .summary-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-top: 4px;
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
        st.caption("🔐 Login to save meal logs")
    
    st.markdown("---")
    st.markdown("### 📊 Macro Tracker")
    st.caption("Track your daily nutrition with interactive visualizations.")
    st.markdown("---")
    
    # Health status link
    if "health_data" in st.session_state and st.session_state.health_data:
        data = st.session_state.health_data
        st.success(f"📊 BMI: **{data.get('bmi', 'N/A')}** | Cal: **{data.get('daily_calories', {}).get('maintenance', 'N/A')}**")
        st.caption("Goals auto-filled from your health analysis ✨")
    else:
        st.info("💡 Complete Health Analysis first to auto-fill your daily goals.")

# ═══════════════════════════════════════════════════════════════
# PAGE HEADER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-header">
    <h1 class="page-title">📊 Macro Tracker</h1>
    <p class="page-subtitle">Track your daily nutrition with interactive visualizations</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
if 'daily_goals' not in st.session_state:
    # Auto-populate from health analysis if available
    if 'health_data' in st.session_state and st.session_state.health_data:
        cal = st.session_state.health_data.get('daily_calories', {}).get('maintenance', 2000)
        st.session_state.daily_goals = {
            "calories": int(cal),
            "protein": round(cal * 0.30 / 4),   # 30% from protein (4 kcal/g)
            "carbs": round(cal * 0.45 / 4),      # 45% from carbs (4 kcal/g)
            "fat": round(cal * 0.25 / 9)          # 25% from fat (9 kcal/g)
        }
    else:
        st.session_state.daily_goals = {"calories": 2000, "protein": 150, "carbs": 250, "fat": 65}

if 'meals_logged' not in st.session_state:
    st.session_state.meals_logged = []
    # Load from backend if authenticated
    auth_token = st.session_state.get('auth_token')
    if auth_token:
        saved = APIClient.get_saved_meals(auth_token, meal_type="tracked", limit=50)
        if saved["success"] and saved["data"]:
            for m in saved["data"]:
                st.session_state.meals_logged.append({
                    "name": m.get("meal_name", "Meal"),
                    "calories": int(m.get("calories", 0)),
                    "protein": int(m.get("protein", 0)),
                    "carbs": int(m.get("carbs", 0)),
                    "fat": int(m.get("fat", 0)),
                    "time": m.get("saved_at", "")[-8:-3] if m.get("saved_at") else "--:--"
                })

if 'totals' not in st.session_state:
    # Calculate from loaded meals
    st.session_state.totals = {
        "calories": sum(m["calories"] for m in st.session_state.meals_logged),
        "protein": sum(m["protein"] for m in st.session_state.meals_logged),
        "carbs": sum(m["carbs"] for m in st.session_state.meals_logged),
        "fat": sum(m["fat"] for m in st.session_state.meals_logged)
    }

# ═══════════════════════════════════════════════════════════════
# LAYOUT
# ═══════════════════════════════════════════════════════════════
left_col, right_col = st.columns([1, 2])

# ═══════════════════════════════════════════════════════════════
# LEFT: GOALS & LOGGING
# ═══════════════════════════════════════════════════════════════
with left_col:
    # Daily Goals
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🎯 Set Daily Goals</div>', unsafe_allow_html=True)
    
    with st.form("goals_form"):
        cal_goal = st.number_input("Calories (kcal)", 1000, 5000, st.session_state.daily_goals["calories"], step=50)
        protein_goal = st.number_input("Protein (g)", 50, 300, st.session_state.daily_goals["protein"], step=5)
        carbs_goal = st.number_input("Carbs (g)", 100, 500, st.session_state.daily_goals["carbs"], step=10)
        fat_goal = st.number_input("Fat (g)", 30, 200, st.session_state.daily_goals["fat"], step=5)
        
        if st.form_submit_button("💾 Save Goals", use_container_width=True):
            st.session_state.daily_goals = {"calories": cal_goal, "protein": protein_goal, "carbs": carbs_goal, "fat": fat_goal}
            st.success("✅ Goals saved!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Log Meal
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🍽️ Log a Meal</div>', unsafe_allow_html=True)
    
    with st.form("meal_form"):
        meal_name = st.text_input("Meal Name", placeholder="e.g., Chicken Salad")
        
        mc1, mc2 = st.columns(2)
        with mc1:
            meal_cal = st.number_input("Calories", 0, 2000, 400, step=10)
            meal_protein = st.number_input("Protein (g)", 0, 100, 30, step=1)
        with mc2:
            meal_carbs = st.number_input("Carbs (g)", 0, 150, 40, step=1)
            meal_fat = st.number_input("Fat (g)", 0, 80, 15, step=1)
        
        if st.form_submit_button("➕ Add Meal", use_container_width=True):
            if meal_name:
                meal = {
                    "name": meal_name,
                    "calories": meal_cal,
                    "protein": meal_protein,
                    "carbs": meal_carbs,
                    "fat": meal_fat,
                    "time": datetime.now().strftime("%H:%M")
                }
                st.session_state.meals_logged.append(meal)
                
                # Update totals
                st.session_state.totals["calories"] += meal_cal
                st.session_state.totals["protein"] += meal_protein
                st.session_state.totals["carbs"] += meal_carbs
                st.session_state.totals["fat"] += meal_fat
                
                # Save to backend if authenticated
                auth_token = st.session_state.get('auth_token')
                if auth_token:
                    APIClient.save_meal(
                        meal_name=meal_name, calories=float(meal_cal),
                        protein=float(meal_protein), carbs=float(meal_carbs),
                        fat=float(meal_fat), meal_type="tracked", auth_token=auth_token
                    )
                
                st.success(f"✅ Added: {meal_name}")
                st.rerun()
            else:
                st.warning("Please enter a meal name")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# RIGHT: VISUALIZATIONS
# ═══════════════════════════════════════════════════════════════
with right_col:
    goals = st.session_state.daily_goals
    totals = st.session_state.totals
    
    # Goal Cards
    st.markdown(f"""
    <div class="goal-grid">
        <div class="goal-card">
            <div class="goal-icon">🔥</div>
            <div class="goal-value">{goals["calories"]}</div>
            <div class="goal-label">Calorie Goal</div>
        </div>
        <div class="goal-card">
            <div class="goal-icon">💪</div>
            <div class="goal-value">{goals["protein"]}g</div>
            <div class="goal-label">Protein Goal</div>
        </div>
        <div class="goal-card">
            <div class="goal-icon">🌾</div>
            <div class="goal-value">{goals["carbs"]}g</div>
            <div class="goal-label">Carbs Goal</div>
        </div>
        <div class="goal-card">
            <div class="goal-icon">🥑</div>
            <div class="goal-value">{goals["fat"]}g</div>
            <div class="goal-label">Fat Goal</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Charts Section
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🥧 Macro Distribution</div>', unsafe_allow_html=True)
        
        # Donut chart
        macro_data = {
            "Macro": ["Protein", "Carbs", "Fat"],
            "Value": [totals["protein"] or 1, totals["carbs"] or 1, totals["fat"] or 1]
        }
        
        fig_donut = go.Figure(data=[go.Pie(
            labels=macro_data["Macro"],
            values=macro_data["Value"],
            hole=0.65,
            marker_colors=["#4CAF50", "#81C784", "#A5D6A7"],
            textinfo='label+percent',
            textfont_size=12,
            textfont_family="Inter"
        )])
        
        fig_donut.update_layout(
            height=280,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            annotations=[{
                'text': f'{totals["calories"]}<br>kcal',
                'x': 0.5, 'y': 0.5,
                'font_size': 20,
                'font_family': 'Inter',
                'font_color': '#2E7D32',
                'showarrow': False
            }]
        )
        
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📈 Progress to Goals</div>', unsafe_allow_html=True)
        
        # Progress bars
        macros = [
            ("Calories", totals["calories"], goals["calories"], "🔥"),
            ("Protein", totals["protein"], goals["protein"], "💪"),
            ("Carbs", totals["carbs"], goals["carbs"], "🌾"),
            ("Fat", totals["fat"], goals["fat"], "🥑")
        ]
        
        colors = ["#4CAF50", "#2E7D32", "#81C784", "#A5D6A7"]
        
        for i, (name, current, goal, icon) in enumerate(macros):
            pct = min((current / goal * 100) if goal > 0 else 0, 100)
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-header">
                    <span class="progress-label">{icon} {name}</span>
                    <span class="progress-value">{current} / {goal}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {pct}%; background: {colors[i]};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Today's Meals
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🍽️ Today\'s Meals</div>', unsafe_allow_html=True)
    
    if st.session_state.meals_logged:
        for meal in st.session_state.meals_logged:
            st.markdown(f"""
            <div class="meal-item">
                <div>
                    <span class="meal-name">{meal["name"]}</span>
                    <span style="color: #999; font-size: 0.85rem; margin-left: 10px;">{meal["time"]}</span>
                </div>
                <div class="meal-macros">
                    <span class="macro-tag">🔥 {meal["calories"]} kcal</span>
                    <span class="macro-tag">💪 {meal["protein"]}g</span>
                    <span class="macro-tag">🌾 {meal["carbs"]}g</span>
                    <span class="macro-tag">🥑 {meal["fat"]}g</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Clear button
        if st.button("🗑️ Clear All Meals", use_container_width=True):
            st.session_state.meals_logged = []
            st.session_state.totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
            st.rerun()
    else:
        st.markdown("""
        <div style="text-align: center; padding: 30px; color: #666;">
            <div style="font-size: 2rem; margin-bottom: 10px;">🍽️</div>
            <p>No meals logged yet. Add your first meal to start tracking!</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Summary
    st.markdown(f"""
    <div class="summary-grid">
        <div class="summary-card">
            <div class="summary-value">{totals["calories"]}</div>
            <div class="summary-label">Calories Consumed</div>
        </div>
        <div class="summary-card">
            <div class="summary-value">{max(goals["calories"] - totals["calories"], 0)}</div>
            <div class="summary-label">Calories Remaining</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# FOOD NUTRITION SEARCH (v7.0)
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div class="card">
    <div class="card-title">🔍 Food Nutrition Search</div>
</div>
""", unsafe_allow_html=True)

search_col, result_col = st.columns([1, 2])

with search_col:
    food_query = st.text_input("🔍 Search food", placeholder="e.g., chicken, rice, salad...")
    if food_query and len(food_query) >= 2:
        result = APIClient.search_foods(food_query, limit=8)
        if result["success"] and result["data"].get("foods"):
            foods = result["data"]["foods"]
            st.caption(f"Found {result['data'].get('total', len(foods))} results")
            for i, food in enumerate(foods):
                with st.expander(f"🍽️ {food['name']}", expanded=(i == 0)):
                    st.markdown(f"""
                    - **Calories**: {food['calories']} kcal
                    - **Protein**: {food['protein']}g
                    - **Carbs**: {food['carbs']}g
                    - **Fat**: {food['fat']}g
                    - **Fiber**: {food.get('fiber', 0)}g
                    """)
                    if st.button(f"➕ Add to log", key=f"add_food_{i}"):
                        meal = {
                            "name": food["name"],
                            "calories": int(food["calories"]),
                            "protein": int(food["protein"]),
                            "carbs": int(food["carbs"]),
                            "fat": int(food["fat"]),
                            "time": datetime.now().strftime("%H:%M")
                        }
                        st.session_state.meals_logged.append(meal)
                        st.session_state.totals["calories"] += meal["calories"]
                        st.session_state.totals["protein"] += meal["protein"]
                        st.session_state.totals["carbs"] += meal["carbs"]
                        st.session_state.totals["fat"] += meal["fat"]
                        auth_token = st.session_state.get('auth_token')
                        if auth_token:
                            APIClient.save_meal(food["name"], food["calories"], food["protein"], food["carbs"], food["fat"], "tracked", auth_token)
                        st.success(f"✅ Added {food['name']}")
                        st.rerun()
        elif food_query:
            st.info("No foods found. Try a different search term.")

with result_col:
    st.markdown("""
    <div class="card" style="text-align: center; padding: 24px;">
        <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 12px; color: #333;">💡 Quick Tips</div>
        <div style="color: #666; line-height: 1.8;">
            Search any food from our database of 375K+ recipes.<br/>
            Click <strong>"Add to log"</strong> to auto-fill your macro tracker.<br/>
            Nutrition values are from real recipe data.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# WATER INTAKE TRACKER (v7.0)
# ═══════════════════════════════════════════════════════════════
st.markdown("---")

auth_token = st.session_state.get('auth_token')
if 'water_glasses' not in st.session_state:
    st.session_state.water_glasses = 0
    if auth_token:
        water_data = APIClient.get_water(auth_token)
        if water_data["success"]:
            st.session_state.water_glasses = water_data["data"].get("glasses", 0)

water_goal = 10  # glasses (2.5L)
water_pct = min(100, round(st.session_state.water_glasses / water_goal * 100))

w1, w2, w3 = st.columns([2, 1, 1])
with w1:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">💧 Water Intake</div>
        <div style="font-size: 2.5rem; font-weight: 800; color: #1976D2; text-align: center;">
            {st.session_state.water_glasses} / {water_goal}
        </div>
        <div style="text-align: center; color: #666; margin-bottom: 16px;">glasses today ({st.session_state.water_glasses * 250}ml / {water_goal * 250}ml)</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {water_pct}%; background: linear-gradient(90deg, #42A5F5, #1976D2);"></div>
        </div>
        <div style="text-align: center; margin-top: 8px; color: #1976D2; font-weight: 600;">{water_pct}%</div>
    </div>
    """, unsafe_allow_html=True)

with w2:
    if st.button("💧 +1 Glass", use_container_width=True):
        st.session_state.water_glasses += 1
        if auth_token:
            APIClient.log_water(glasses=1, auth_token=auth_token)
        st.rerun()

with w3:
    if st.button("💧 +2 Glasses", use_container_width=True):
        st.session_state.water_glasses += 2
        if auth_token:
            APIClient.log_water(glasses=2, auth_token=auth_token)
        st.rerun()
