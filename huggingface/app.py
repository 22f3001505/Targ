"""
🥗 TARG — AI-Powered Health & Nutrition Platform
Hugging Face Spaces Deployment (Self-Contained)

Features:
  - ML Recipe Recommendations (KNN + Cosine Similarity)
  - BMI / BMR / TDEE Health Analysis
  - Exercise Calorie Calculator (198 MET-based exercises)
  - Macro Tracker
  - Meal Planner
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
import os

# ═══════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════

st.set_page_config(
    page_title="TARG — AI Health & Nutrition",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════
# CUSTOM CSS
# ═══════════════════════════════════════════════════

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, #4CAF50, #2E7D32);
        color: white; padding: 2.5rem; border-radius: 20px;
        text-align: center; margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(76,175,80,0.3);
    }
    .main-header h1 { font-size: 2.5rem; margin: 0; font-weight: 800; }
    .main-header p { font-size: 1rem; opacity: 0.9; margin-top: 0.5rem; }
    
    .metric-card {
        background: white; border-radius: 16px; padding: 1.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06); text-align: center;
        border-left: 4px solid #4CAF50;
    }
    .metric-card h3 { color: #2E7D32; font-size: 2rem; margin: 0; }
    .metric-card p { color: #666; font-size: 0.85rem; margin: 0; }
    
    .recipe-card {
        background: white; border-radius: 14px; padding: 1.2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05); margin-bottom: 1rem;
        border-left: 4px solid #4CAF50;
    }
    .recipe-card h4 { color: #333; margin: 0 0 0.5rem 0; }
    
    .bmi-badge {
        display: inline-block; padding: 6px 18px; border-radius: 50px;
        color: white; font-weight: 600; font-size: 0.9rem;
    }
    
    .exercise-chip {
        display: inline-block; background: #E8F5E9; color: #2E7D32;
        padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;
        margin: 2px; font-weight: 500;
    }
    
    .section-title {
        font-size: 1.3rem; font-weight: 700; color: #2E7D32;
        margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem;
        border-bottom: 2px solid #E8F5E9;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px; padding: 10px 20px; font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# ML ENGINE (embedded)
# ═══════════════════════════════════════════════════

@st.cache_data
def load_dataset():
    """Load the recipe dataset."""
    data_paths = [
        "Data/dataset.csv",
        "../Data/dataset.csv",
        "dataset.csv",
    ]
    for path in data_paths:
        if os.path.exists(path):
            try:
                return pd.read_csv(path, compression='gzip')
            except Exception:
                try:
                    return pd.read_csv(path)
                except Exception:
                    continue
    return None


def recommend_recipes(dataframe, nutrition_input, ingredients=[], n_neighbors=5):
    """ML recipe recommendation using KNN + Cosine Similarity."""
    if dataframe is None or dataframe.empty:
        return None
    
    data = dataframe.copy()
    
    # Filter by ingredients if provided
    if ingredients:
        regex = ''.join(f'(?=.*{ing})' for ing in ingredients)
        data = data[data['RecipeIngredientParts'].str.contains(regex, regex=True, flags=re.IGNORECASE)]
    
    if len(data) < n_neighbors:
        return None
    
    # Scale features (nutrition columns 6-15)
    scaler = StandardScaler()
    prep_data = scaler.fit_transform(data.iloc[:, 6:15].to_numpy())
    
    # KNN with cosine similarity
    neigh = NearestNeighbors(metric='cosine', algorithm='brute')
    neigh.fit(prep_data)
    
    # Build pipeline
    transformer = FunctionTransformer(
        neigh.kneighbors,
        kw_args={'n_neighbors': n_neighbors, 'return_distance': False}
    )
    pipeline = Pipeline([('std_scaler', scaler), ('NN', transformer)])
    
    # Get recommendations
    input_array = np.array(nutrition_input).reshape(1, -1)
    result = data.iloc[pipeline.transform(input_array)[0]]
    
    output = result.to_dict("records")
    for recipe in output:
        recipe['RecipeIngredientParts'] = re.findall(r'"([^"]*)"', str(recipe.get('RecipeIngredientParts', '')))
        recipe['RecipeInstructions'] = re.findall(r'"([^"]*)"', str(recipe.get('RecipeInstructions', '')))
    
    return output


# ═══════════════════════════════════════════════════
# HEALTH CALCULATIONS
# ═══════════════════════════════════════════════════

def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    return round(weight / (height_m ** 2), 2)

def bmi_category(bmi):
    if bmi < 18.5: return {"category": "Underweight", "color": "#FFA726", "status": "Below healthy range"}
    elif bmi < 25: return {"category": "Normal", "color": "#4CAF50", "status": "Healthy weight"}
    elif bmi < 30: return {"category": "Overweight", "color": "#FF7043", "status": "Above healthy range"}
    else: return {"category": "Obese", "color": "#EF5350", "status": "High health risk"}

def calculate_bmr(weight, height_cm, age, gender):
    if gender.lower() == "male":
        return round(10 * weight + 6.25 * height_cm - 5 * age + 5, 2)
    else:
        return round(10 * weight + 6.25 * height_cm - 5 * age - 161, 2)

def calculate_daily_calories(bmr, activity_level):
    multipliers = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "extra_active": 1.9}
    mult = multipliers.get(activity_level.lower(), 1.55)
    maintenance = round(bmr * mult)
    return {
        "maintenance": maintenance, "mild_loss": round(maintenance * 0.9),
        "weight_loss": round(maintenance * 0.8), "extreme_loss": round(maintenance * 0.6),
        "mild_gain": round(maintenance * 1.1), "weight_gain": round(maintenance * 1.2)
    }

def workout_plan(category):
    plans = {
        "Underweight": {"focus": "Strength & Muscle Building", "exercises": ["Weight training (3-4 days/week)", "Resistance exercises", "Compound movements", "Progressive overload", "Limited cardio"], "tips": "Focus on caloric surplus with protein-rich diet."},
        "Normal": {"focus": "Balanced Fitness", "exercises": ["Cardio + Strength mix", "HIIT (2x/week)", "Flexibility exercises", "Sports activities", "Core strengthening"], "tips": "Maintain with balanced nutrition."},
        "Overweight": {"focus": "Cardio & Fat Burning", "exercises": ["Brisk walking (30-45 min)", "Swimming/cycling", "Light strength training", "Interval training", "Moderate cardio"], "tips": "Create caloric deficit gradually."},
        "Obese": {"focus": "Low-Impact Cardio", "exercises": ["Walking (15-20 min)", "Water aerobics", "Stationary cycling", "Chair exercises", "Gentle stretching"], "tips": "Consult healthcare provider. Stay consistent."}
    }
    return plans.get(category, plans["Normal"])


# ═══════════════════════════════════════════════════
# EXERCISE DATABASE (198 MET-based)
# ═══════════════════════════════════════════════════

EXERCISES = [
    {"name": "Walking (slow, 2 mph)", "category": "Cardio", "met": 2.5, "difficulty": "Easy"},
    {"name": "Walking (brisk, 4 mph)", "category": "Cardio", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Jogging (5 mph)", "category": "Cardio", "met": 7.0, "difficulty": "Moderate"},
    {"name": "Running (6 mph)", "category": "Cardio", "met": 9.8, "difficulty": "Hard"},
    {"name": "Running (8 mph)", "category": "Cardio", "met": 11.8, "difficulty": "Very Hard"},
    {"name": "Sprint intervals", "category": "Cardio", "met": 14.0, "difficulty": "Very Hard"},
    {"name": "Cycling (leisure)", "category": "Cardio", "met": 4.0, "difficulty": "Easy"},
    {"name": "Cycling (moderate)", "category": "Cardio", "met": 8.0, "difficulty": "Moderate"},
    {"name": "Cycling (vigorous)", "category": "Cardio", "met": 10.0, "difficulty": "Hard"},
    {"name": "Swimming (moderate)", "category": "Cardio", "met": 6.0, "difficulty": "Moderate"},
    {"name": "Swimming (laps)", "category": "Cardio", "met": 8.0, "difficulty": "Hard"},
    {"name": "Jump rope (moderate)", "category": "Cardio", "met": 11.8, "difficulty": "Very Hard"},
    {"name": "Rowing machine", "category": "Cardio", "met": 7.0, "difficulty": "Moderate"},
    {"name": "Elliptical trainer", "category": "Cardio", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Stair climber", "category": "Cardio", "met": 9.0, "difficulty": "Hard"},
    {"name": "Jumping jacks", "category": "Cardio", "met": 8.0, "difficulty": "Moderate"},
    {"name": "Burpees", "category": "Cardio", "met": 10.0, "difficulty": "Very Hard"},
    {"name": "Mountain climbers", "category": "Cardio", "met": 8.0, "difficulty": "Hard"},
    {"name": "Kickboxing", "category": "Cardio", "met": 10.0, "difficulty": "Hard"},
    {"name": "Weight training (light)", "category": "Strength", "met": 3.5, "difficulty": "Easy"},
    {"name": "Weight training (moderate)", "category": "Strength", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Weight training (vigorous)", "category": "Strength", "met": 6.0, "difficulty": "Hard"},
    {"name": "Circuit training", "category": "Strength", "met": 8.0, "difficulty": "Hard"},
    {"name": "Push-ups", "category": "Strength", "met": 8.0, "difficulty": "Moderate"},
    {"name": "Pull-ups", "category": "Strength", "met": 8.0, "difficulty": "Hard"},
    {"name": "Squats (bodyweight)", "category": "Strength", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Deadlifts", "category": "Strength", "met": 6.0, "difficulty": "Hard"},
    {"name": "Bench press", "category": "Strength", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Kettlebell swings", "category": "Strength", "met": 9.8, "difficulty": "Hard"},
    {"name": "Battle ropes", "category": "Strength", "met": 10.3, "difficulty": "Very Hard"},
    {"name": "Plank hold", "category": "Strength", "met": 3.8, "difficulty": "Moderate"},
    {"name": "HIIT (general)", "category": "HIIT", "met": 10.0, "difficulty": "Hard"},
    {"name": "Tabata training", "category": "HIIT", "met": 12.0, "difficulty": "Very Hard"},
    {"name": "CrossFit WOD", "category": "HIIT", "met": 12.0, "difficulty": "Very Hard"},
    {"name": "Boxing HIIT", "category": "HIIT", "met": 10.0, "difficulty": "Hard"},
    {"name": "Yoga (hatha)", "category": "Flexibility", "met": 2.5, "difficulty": "Easy"},
    {"name": "Yoga (vinyasa)", "category": "Flexibility", "met": 4.0, "difficulty": "Moderate"},
    {"name": "Yoga (power)", "category": "Flexibility", "met": 5.5, "difficulty": "Moderate"},
    {"name": "Pilates (mat)", "category": "Flexibility", "met": 3.0, "difficulty": "Moderate"},
    {"name": "Stretching", "category": "Flexibility", "met": 2.3, "difficulty": "Easy"},
    {"name": "Tai Chi", "category": "Flexibility", "met": 3.0, "difficulty": "Easy"},
    {"name": "Basketball", "category": "Sports", "met": 8.0, "difficulty": "Hard"},
    {"name": "Soccer", "category": "Sports", "met": 10.0, "difficulty": "Hard"},
    {"name": "Tennis (singles)", "category": "Sports", "met": 8.0, "difficulty": "Hard"},
    {"name": "Badminton", "category": "Sports", "met": 7.0, "difficulty": "Moderate"},
    {"name": "Volleyball", "category": "Sports", "met": 6.0, "difficulty": "Moderate"},
    {"name": "Cricket", "category": "Sports", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Rock climbing", "category": "Sports", "met": 8.0, "difficulty": "Hard"},
    {"name": "Hiking (moderate)", "category": "Outdoor", "met": 6.0, "difficulty": "Moderate"},
    {"name": "Hiking (steep)", "category": "Outdoor", "met": 8.0, "difficulty": "Hard"},
    {"name": "Trail running", "category": "Outdoor", "met": 10.0, "difficulty": "Hard"},
    {"name": "Mountain biking", "category": "Outdoor", "met": 8.5, "difficulty": "Hard"},
    {"name": "Zumba", "category": "Dance", "met": 6.5, "difficulty": "Moderate"},
    {"name": "Hip hop dance", "category": "Dance", "met": 7.5, "difficulty": "Hard"},
    {"name": "Salsa dancing", "category": "Dance", "met": 5.5, "difficulty": "Moderate"},
]

EXERCISE_CATEGORIES = sorted(set(e["category"] for e in EXERCISES))


# ═══════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 🥗 TARG v7.0")
    st.markdown("*AI Health & Nutrition*")
    st.divider()
    
    page = st.radio(
        "Navigate",
        ["🏠 Home", "💪 Health Analysis", "🍽 Recipe Search", "🏋️ Exercise Calculator", "📊 Macro Tracker", "📅 Meal Planner"],
        index=0
    )
    
    st.divider()
    
    # Load dataset status
    df = load_dataset()
    if df is not None:
        st.success(f"✅ {len(df):,} recipes loaded")
    else:
        st.warning("⚠️ Dataset not found — upload below")
        uploaded = st.file_uploader("Upload dataset.csv", type="csv")
        if uploaded:
            try:
                df = pd.read_csv(uploaded, compression='gzip')
            except Exception:
                df = pd.read_csv(uploaded)
            st.success(f"✅ {len(df):,} recipes loaded")
    
    st.markdown(f"**Exercises:** {len(EXERCISES)}")
    st.markdown(f"**Categories:** {len(EXERCISE_CATEGORIES)}")
    st.divider()
    st.caption("Built with Scikit-learn, Pandas & Streamlit")


# ═══════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════

if page == "🏠 Home":
    st.markdown("""
    <div class="main-header">
        <h1>🥗 TARG</h1>
        <p>AI-Powered Health & Nutrition Intelligence Platform</p>
        <p style="font-size:0.85rem; opacity:0.7;">v7.0.0 • Hugging Face Spaces Edition</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        recipe_count = f"{len(df):,}" if df is not None else "N/A"
        st.markdown(f"""<div class="metric-card"><h3>{recipe_count}</h3><p>Real Recipes</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><h3>9</h3><p>Nutrition Dimensions</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><h3>{len(EXERCISES)}</h3><p>MET Exercises</p></div>""", unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown('<div class="section-title">🚀 Features</div>', unsafe_allow_html=True)
    
    cols = st.columns(2)
    features = [
        ("🤖 ML Recipe Engine", "K-Nearest Neighbors + Cosine Similarity matching across 9 nutritional dimensions"),
        ("💪 Health Analysis", "BMI, BMR, TDEE calculations using Mifflin-St Jeor equation with workout plans"),
        ("🏋️ Exercise Calculator", "MET-based calorie estimation from Compendium of Physical Activities"),
        ("📊 Macro Tracking", "Daily protein, carbs, fat goal tracking with visual progress"),
    ]
    for i, (title, desc) in enumerate(features):
        with cols[i % 2]:
            st.info(f"**{title}**\n\n{desc}")
    
    st.markdown('<div class="section-title">💡 How It Works</div>', unsafe_allow_html=True)
    st.markdown("""
    ```
    Input: [Calories, Fat, SatFat, Cholesterol, Sodium, Carbs, Fiber, Sugar, Protein]
                                    │
                                    ▼
                        ┌───────────────────┐
                        │  StandardScaler   │  ← Z-score normalization
                        └─────────┬─────────┘
                                  │
                                  ▼
                   ┌──────────────────────────┐
                   │   NearestNeighbors        │  ← cosine similarity
                   │   algorithm='brute'       │
                   └──────────────┬────────────┘
                                  │
                                  ▼
                    Top-K Matching Recipes
    ```
    """)


# ═══════════════════════════════════════════════════
# PAGE: HEALTH ANALYSIS
# ═══════════════════════════════════════════════════

elif page == "💪 Health Analysis":
    st.markdown("""<div class="main-header"><h1>💪 Health & Diet Analysis</h1>
    <p>BMI, BMR, TDEE & personalized workout recommendations</p></div>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-title">📋 Your Details</div>', unsafe_allow_html=True)
        age = st.number_input("Age", 1, 120, 25)
        height = st.number_input("Height (cm)", 50, 300, 170)
        weight = st.number_input("Weight (kg)", 10, 500, 70)
        gender = st.selectbox("Gender", ["male", "female"])
        activity = st.selectbox("Activity Level", ["sedentary", "light", "moderate", "active", "extra_active"])
        
        analyze = st.button("🔬 Analyze Health", use_container_width=True, type="primary")
    
    with col2:
        if analyze or st.session_state.get("health_analyzed"):
            st.session_state["health_analyzed"] = True
            
            bmi = calculate_bmi(weight, height)
            cat = bmi_category(bmi)
            bmr = calculate_bmr(weight, height, age, gender)
            calories = calculate_daily_calories(bmr, activity)
            plan = workout_plan(cat["category"])
            
            # Store for other pages
            st.session_state["health_data"] = {
                "bmi": bmi, "category": cat, "bmr": bmr,
                "calories": calories, "plan": plan
            }
            
            # BMI Display
            st.markdown(f"""<div class="metric-card">
                <p>Body Mass Index</p>
                <h3>{bmi}</h3>
                <span class="bmi-badge" style="background:{cat['color']}">{cat['category']}</span>
                <p style="margin-top:8px">{cat['status']}</p>
            </div>""", unsafe_allow_html=True)
            
            st.markdown("")
            
            # BMR & Calories
            c1, c2 = st.columns(2)
            with c1:
                st.metric("⚡ BMR", f"{bmr} kcal")
            with c2:
                st.metric("🔥 Maintenance", f"{calories['maintenance']} kcal")
            
            # Calorie targets
            st.markdown('<div class="section-title">🎯 Daily Calorie Targets</div>', unsafe_allow_html=True)
            cols = st.columns(3)
            targets = [
                ("📉 Mild Loss", calories["mild_loss"]),
                ("📉 Weight Loss", calories["weight_loss"]),
                ("📈 Mild Gain", calories["mild_gain"]),
            ]
            for i, (label, val) in enumerate(targets):
                with cols[i]:
                    st.metric(label, f"{val} kcal")
            
            # Workout Plan
            st.markdown(f'<div class="section-title">🏋️ {plan["focus"]}</div>', unsafe_allow_html=True)
            for ex in plan["exercises"]:
                st.markdown(f"✅ {ex}")
            st.info(f"💡 **Tip:** {plan['tips']}")
    
    # BMI Gauge Chart
    if st.session_state.get("health_data"):
        data = st.session_state["health_data"]
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=data["bmi"],
            title={'text': "BMI Scale"},
            gauge={
                'axis': {'range': [10, 45]},
                'bar': {'color': data["category"]["color"]},
                'steps': [
                    {'range': [10, 18.5], 'color': '#FFF3E0'},
                    {'range': [18.5, 25], 'color': '#E8F5E9'},
                    {'range': [25, 30], 'color': '#FBE9E7'},
                    {'range': [30, 45], 'color': '#FFEBEE'},
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': data["bmi"]}
            }
        ))
        fig.update_layout(height=300, margin=dict(t=50, b=0))
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════
# PAGE: RECIPE SEARCH
# ═══════════════════════════════════════════════════

elif page == "🍽 Recipe Search":
    st.markdown("""<div class="main-header"><h1>🍽 ML Recipe Search</h1>
    <p>KNN + Cosine Similarity across 9 nutritional dimensions</p></div>""", unsafe_allow_html=True)
    
    if df is None:
        st.error("❌ Dataset not loaded. Upload dataset.csv in the sidebar.")
    else:
        st.markdown(f"**Dataset:** {len(df):,} recipes • **Algorithm:** KNN (Cosine) • **Features:** 9 Nutrients")
        
        st.markdown('<div class="section-title">📊 Set Nutritional Targets</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            calories = st.slider("🔥 Calories (kcal)", 50, 2000, 400)
            fat = st.slider("🥑 Fat (g)", 0, 100, 15)
            sat_fat = st.slider("🧈 Saturated Fat (g)", 0, 50, 5)
        with col2:
            cholesterol = st.slider("💊 Cholesterol (mg)", 0, 500, 50)
            sodium = st.slider("🧂 Sodium (mg)", 0, 3000, 500)
            carbs = st.slider("🌾 Carbohydrates (g)", 0, 300, 50)
        with col3:
            fiber = st.slider("🥦 Fiber (g)", 0, 50, 5)
            sugar = st.slider("🍬 Sugar (g)", 0, 100, 10)
            protein = st.slider("💪 Protein (g)", 0, 200, 30)
        
        n_results = st.slider("Number of results", 3, 20, 5)
        
        if st.button("🔍 Find Matching Recipes", use_container_width=True, type="primary"):
            with st.spinner("Running ML pipeline..."):
                nutrition = [calories, fat, sat_fat, cholesterol, sodium, carbs, fiber, sugar, protein]
                results = recommend_recipes(df, nutrition, n_neighbors=n_results)
            
            if results:
                st.success(f"✅ Found {len(results)} matching recipes!")
                
                for i, recipe in enumerate(results):
                    with st.expander(f"🍽 {recipe.get('Name', f'Recipe {i+1}')}", expanded=(i < 3)):
                        cols = st.columns(4)
                        cols[0].metric("🔥 Calories", f"{recipe.get('Calories', 0):.0f} kcal")
                        cols[1].metric("💪 Protein", f"{recipe.get('ProteinContent', 0):.1f}g")
                        cols[2].metric("🌾 Carbs", f"{recipe.get('CarbohydrateContent', 0):.1f}g")
                        cols[3].metric("🥑 Fat", f"{recipe.get('FatContent', 0):.1f}g")
                        
                        if recipe.get('RecipeIngredientParts'):
                            st.markdown("**🧾 Ingredients:**")
                            for ing in recipe['RecipeIngredientParts'][:15]:
                                st.markdown(f"  • {ing}")
                        
                        if recipe.get('RecipeInstructions'):
                            st.markdown("**📝 Instructions:**")
                            for j, step in enumerate(recipe['RecipeInstructions'][:10]):
                                st.markdown(f"  {j+1}. {step}")
            else:
                st.warning("No matching recipes found. Try adjusting your inputs.")


# ═══════════════════════════════════════════════════
# PAGE: EXERCISE CALCULATOR
# ═══════════════════════════════════════════════════

elif page == "🏋️ Exercise Calculator":
    st.markdown("""<div class="main-header"><h1>🏋️ Exercise Calorie Calculator</h1>
    <p>MET-based estimation from Compendium of Physical Activities</p></div>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="section-title">🏷️ Filter by Category</div>', unsafe_allow_html=True)
        selected_cat = st.selectbox("Category", ["All"] + EXERCISE_CATEGORIES)
        
        filtered = EXERCISES if selected_cat == "All" else [e for e in EXERCISES if e["category"] == selected_cat]
        
        exercise_names = [e["name"] for e in filtered]
        selected_exercise = st.selectbox("Exercise", exercise_names)
        
        weight_kg = st.number_input("Your Weight (kg)", 30, 300, 70)
        duration = st.number_input("Duration (minutes)", 1, 300, 30)
        
        if st.button("🔥 Calculate Calories", use_container_width=True, type="primary"):
            exercise = next((e for e in EXERCISES if e["name"] == selected_exercise), None)
            if exercise:
                cal = round(exercise["met"] * weight_kg * (duration / 60) * 1.05)
                st.session_state["calorie_result"] = {
                    "exercise": selected_exercise, "met": exercise["met"],
                    "calories": cal, "duration": duration, "weight": weight_kg,
                    "category": exercise["category"], "difficulty": exercise["difficulty"]
                }
    
    with col2:
        if st.session_state.get("calorie_result"):
            r = st.session_state["calorie_result"]
            st.markdown(f"""<div class="metric-card">
                <p>{r['exercise']}</p>
                <h3>🔥 {r['calories']} kcal</h3>
                <p>in {r['duration']} minutes</p>
            </div>""", unsafe_allow_html=True)
            
            st.markdown("")
            c1, c2, c3 = st.columns(3)
            c1.metric("MET Value", r["met"])
            c2.metric("Category", r["category"])
            c3.metric("Difficulty", r["difficulty"])
            
            st.info(f"💡 **Formula:** MET ({r['met']}) × Weight ({r['weight']}kg) × Duration ({r['duration']/60:.2f}h) × 1.05 = **{r['calories']} kcal**")
    
    # Exercise Table
    st.markdown('<div class="section-title">📋 Exercise Database</div>', unsafe_allow_html=True)
    ex_df = pd.DataFrame(filtered)
    st.dataframe(
        ex_df[["name", "category", "met", "difficulty"]],
        use_container_width=True,
        column_config={
            "name": "Exercise",
            "category": "Category",
            "met": st.column_config.NumberColumn("MET", format="%.1f"),
            "difficulty": "Difficulty"
        },
        hide_index=True
    )


# ═══════════════════════════════════════════════════
# PAGE: MACRO TRACKER
# ═══════════════════════════════════════════════════

elif page == "📊 Macro Tracker":
    st.markdown("""<div class="main-header"><h1>📊 Macro Tracker</h1>
    <p>Track your daily nutrition goals</p></div>""", unsafe_allow_html=True)
    
    # Initialize state
    if "meals_log" not in st.session_state:
        st.session_state["meals_log"] = []
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-title">🎯 Daily Goals</div>', unsafe_allow_html=True)
        cal_goal = st.number_input("Calorie Goal", 1000, 5000, 2000)
        protein_goal = st.number_input("Protein Goal (g)", 20, 300, 150)
        carbs_goal = st.number_input("Carbs Goal (g)", 50, 500, 250)
        fat_goal = st.number_input("Fat Goal (g)", 10, 200, 65)
    
    with col2:
        st.markdown('<div class="section-title">🍽️ Log a Meal</div>', unsafe_allow_html=True)
        meal_name = st.text_input("Meal Name", placeholder="e.g., Grilled Chicken")
        mc1, mc2 = st.columns(2)
        m_cal = mc1.number_input("Calories", 0, 3000, 400)
        m_protein = mc2.number_input("Protein (g)", 0, 200, 30)
        m_carbs = mc1.number_input("Carbs (g)", 0, 300, 40)
        m_fat = mc2.number_input("Fat (g)", 0, 100, 15)
        
        if st.button("➕ Add Meal", use_container_width=True, type="primary"):
            if meal_name:
                st.session_state["meals_log"].append({
                    "name": meal_name, "calories": m_cal,
                    "protein": m_protein, "carbs": m_carbs, "fat": m_fat
                })
                st.success(f"Added {meal_name}!")
    
    # Progress
    meals = st.session_state["meals_log"]
    total_cal = sum(m["calories"] for m in meals)
    total_pro = sum(m["protein"] for m in meals)
    total_carb = sum(m["carbs"] for m in meals)
    total_fat = sum(m["fat"] for m in meals)
    
    st.markdown('<div class="section-title">📈 Progress</div>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    cols[0].progress(min(total_cal / cal_goal, 1.0), text=f"🔥 {total_cal}/{cal_goal} kcal")
    cols[1].progress(min(total_pro / protein_goal, 1.0), text=f"💪 {total_pro}/{protein_goal}g protein")
    cols[2].progress(min(total_carb / carbs_goal, 1.0), text=f"🌾 {total_carb}/{carbs_goal}g carbs")
    cols[3].progress(min(total_fat / fat_goal, 1.0), text=f"🥑 {total_fat}/{fat_goal}g fat")
    
    if meals:
        st.markdown('<div class="section-title">🍽️ Today\'s Meals</div>', unsafe_allow_html=True)
        meals_df = pd.DataFrame(meals)
        st.dataframe(meals_df, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ Clear All Meals"):
            st.session_state["meals_log"] = []
            st.rerun()
    
    # Macro donut chart
    if total_cal > 0:
        fig = go.Figure(data=[go.Pie(
            labels=['Protein', 'Carbs', 'Fat'],
            values=[total_pro * 4, total_carb * 4, total_fat * 9],
            hole=0.6, marker_colors=['#4CAF50', '#FFA726', '#EF5350']
        )])
        fig.update_layout(height=300, margin=dict(t=30, b=0), showlegend=True,
                         annotations=[dict(text=f'{total_cal}<br>kcal', x=0.5, y=0.5, font_size=18, showarrow=False)])
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════
# PAGE: MEAL PLANNER
# ═══════════════════════════════════════════════════

elif page == "📅 Meal Planner":
    st.markdown("""<div class="main-header"><h1>📅 Weekly Meal Planner</h1>
    <p>Plan balanced meals for the whole week</p></div>""", unsafe_allow_html=True)
    
    breakfasts = ["Greek Yogurt Parfait (350 kcal)", "Avocado Toast + Eggs (420 kcal)", "Oatmeal Bowl (380 kcal)", "Smoothie Bowl (340 kcal)", "Egg White Omelette (280 kcal)"]
    lunches = ["Grilled Chicken Salad (480 kcal)", "Quinoa Buddha Bowl (520 kcal)", "Turkey Wrap (450 kcal)", "Mediterranean Plate (510 kcal)", "Salmon Poke Bowl (540 kcal)"]
    dinners = ["Baked Salmon & Veggies (550 kcal)", "Chicken Stir Fry (480 kcal)", "Lean Beef Tacos (520 kcal)", "Vegetable Curry (460 kcal)", "Grilled Tofu Bowl (420 kcal)"]
    
    breakfast_cals = [350, 420, 380, 340, 280]
    lunch_cals = [480, 520, 450, 510, 540]
    dinner_cals = [550, 480, 520, 460, 420]
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    total_week = 0
    
    for day in days:
        with st.expander(f"📆 {day}", expanded=(day == "Monday")):
            c1, c2, c3 = st.columns(3)
            with c1:
                bi = st.selectbox(f"🌅 Breakfast", breakfasts, key=f"b_{day}")
                b_idx = breakfasts.index(bi)
            with c2:
                li = st.selectbox(f"☀️ Lunch", lunches, key=f"l_{day}")
                l_idx = lunches.index(li)
            with c3:
                di = st.selectbox(f"🌙 Dinner", dinners, key=f"d_{day}")
                d_idx = dinners.index(di)
            
            day_total = breakfast_cals[b_idx] + lunch_cals[l_idx] + dinner_cals[d_idx]
            total_week += day_total
            st.metric(f"🔥 {day} Total", f"{day_total} kcal")
    
    st.markdown('<div class="section-title">📊 Weekly Summary</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 Week Total", f"{total_week:,} kcal")
    c2.metric("📈 Daily Average", f"{total_week // 7:,} kcal")
    c3.metric("🍽️ Total Meals", "21")
