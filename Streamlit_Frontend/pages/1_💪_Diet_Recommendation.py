"""
TARG - Diet Recommendation Page
Premium Healthcare UI with ML Integration
"""
import streamlit as st
import requests
import time
from pathlib import Path
from api import APIClient, BASE_URL
from ui.polish import inject_ui_polish
from ui.safe import escape_html
from ui.ux import handle_auth_expired, require_login

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Diet Recommendation - TARG",
    page_icon="💪",
    layout="wide"
)

LOGO_PATH = Path(__file__).parent.parent / "logo.png"

require_login("pages/1_💪_Diet_Recommendation.py")

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
    .bmi-normal, .bmi-underweight, .bmi-overweight, .bmi-obese {
        color: white !important;
    }
    .calorie-card.active, .calorie-card.active * {
        color: white !important;
    }
    .stButton > button, .stButton > button * {
        color: white !important;
    }
    
    /* Form Card */
    .form-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid rgba(76, 175, 80, 0.1);
    }
    
    .form-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #333333 !important;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Results Section */
    .results-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid rgba(76, 175, 80, 0.1);
        margin-bottom: 20px;
    }
    
    .results-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2E7D32 !important;
        margin-bottom: 16px;
    }
    
    /* Health Metric Cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin: 20px 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #A5D6A7 0%, #C8E6C9 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2E7D32 !important;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #333333 !important;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* BMI Badge */
    .bmi-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .bmi-normal { background: #4CAF50; color: white; }
    .bmi-underweight { background: #FFA726; color: white; }
    .bmi-overweight { background: #FF7043; color: white; }
    .bmi-obese { background: #EF5350; color: white; }
    
    /* Recipe Cards */
    .recipe-card {
        background: #FFFFFF;
        border: 1px solid rgba(76, 175, 80, 0.15);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    
    .recipe-card:hover {
        transform: translateX(8px);
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.12);
        border-color: #4CAF50;
    }
    
    .recipe-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #333333 !important;
        margin-bottom: 12px;
    }
    
    .recipe-nutrients {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
    }
    
    .nutrient-item {
        background: #F1F8E9;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #2E7D32 !important;
        font-weight: 500;
    }
    
    /* Calorie Cards */
    .calorie-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 20px 0;
    }
    
    .calorie-card {
        text-align: center;
        padding: 16px;
        border-radius: 12px;
        background: #F5F5F5;
    }
    
    .calorie-card.active {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
    }
    
    .calorie-value {
        font-size: 1.4rem;
        font-weight: 700;
    }
    
    .calorie-label {
        font-size: 0.75rem;
        margin-top: 4px;
        opacity: 0.85;
    }
    
    /* Streamlit overrides */
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 14px 30px;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
    }
</style>
""", unsafe_allow_html=True)
inject_ui_polish()

recipe_count_label = "50K+"
try:
    api_health = APIClient.check_health()
    if api_health.get("connected") and api_health.get("dataset_size", 0) > 0:
        dataset_size = api_health["dataset_size"]
        recipe_count_label = f"{dataset_size:,}" if dataset_size < 10000 else f"{dataset_size // 1000}K+"
except Exception:
    pass

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=160)
    st.markdown("---")
    st.markdown("### 💪 Diet Recommendation")
    st.caption("Get personalized meal suggestions based on your health profile.")
    st.markdown("---")
    st.info("📊 Enter your details and click **Analyze** to see results.")

# ═══════════════════════════════════════════════════════════════
# PAGE HEADER
# ═══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="page-header">
    <h1 class="page-title">💪 Personalized Diet Recommendation</h1>
    <p class="page-subtitle">AI-powered nutrition matching from {recipe_count_label} recipes</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
if 'health_data' not in st.session_state:
    st.session_state.health_data = None
if 'diet_recommendations' not in st.session_state:
    st.session_state.diet_recommendations = None

# ═══════════════════════════════════════════════════════════════
# LAYOUT: INPUT + RESULTS
# ═══════════════════════════════════════════════════════════════
input_col, results_col = st.columns([1, 2])

# ═══════════════════════════════════════════════════════════════
# INPUT FORM
# ═══════════════════════════════════════════════════════════════
with input_col:
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">📋 Your Health Profile</div>', unsafe_allow_html=True)
    
    with st.form("health_form", clear_on_submit=False):
        age = st.number_input("Age (years)", min_value=10, max_value=100, value=25, step=1)
        height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170, step=1)
        weight = st.number_input("Weight (kg)", min_value=30, max_value=250, value=70, step=1)
        
        gender = st.selectbox("Gender", ["male", "female"], format_func=lambda x: x.capitalize())
        
        activity = st.select_slider(
            "Activity Level",
            options=["sedentary", "light", "moderate", "active", "extra_active"],
            value="moderate",
            format_func=lambda x: x.replace("_", " ").title()
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.form_submit_button("🔍 Analyze & Recommend", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# PROCESS HEALTH ANALYSIS
# ═══════════════════════════════════════════════════════════════
if analyze_btn:
    with st.spinner("🔬 Analyzing your health profile..."):
        time.sleep(0.5)
        
        auth_token = st.session_state.get('auth_token')
        result = APIClient.health_analysis(age, height, weight, gender, activity, auth_token)
        
        if result["success"]:
            st.session_state.health_data = result["data"]
        else:
            # Fallback: local calculation via shared HealthCalculator
            from api import HealthCalculator
            bmi = HealthCalculator.calculate_bmi(weight, height)
            category = HealthCalculator.get_bmi_category(bmi)
            bmr = HealthCalculator.calculate_bmr(weight, height, age, gender)
            calories = HealthCalculator.calculate_tdee(bmr, activity)
            workout = HealthCalculator.get_workout_plan(category["category"])
            
            st.session_state.health_data = {
                "bmi": bmi, "bmi_category": category, "bmr": bmr,
                "daily_calories": calories, "workout_plan": workout
            }
        
        st.success("✅ Health analysis completed!")
        st.rerun()

# ═══════════════════════════════════════════════════════════════
# RESULTS DISPLAY
# ═══════════════════════════════════════════════════════════════
with results_col:
    if st.session_state.health_data:
        data = st.session_state.health_data
        
        # ─── HEALTH SUMMARY ───
        st.markdown('<div class="results-card">', unsafe_allow_html=True)
        st.markdown('<div class="results-title">📊 Health Summary</div>', unsafe_allow_html=True)
        
        # BMI Category Badge
        category = data["bmi_category"]["category"]
        bmi_class = f"bmi-{category.lower()}"
        
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <span class="bmi-badge {bmi_class}">{category}</span>
            <p style="margin-top: 8px; color: #666;">{data["bmi_category"]["status"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics Grid
        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">{data["bmi"]}</div>
                <div class="metric-label">BMI</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{int(data["bmr"])}</div>
                <div class="metric-label">BMR (kcal)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{data["daily_calories"]["maintenance"]}</div>
                <div class="metric-label">Daily Need</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ─── CALORIE TARGETS ───
        st.markdown('<div class="results-card">', unsafe_allow_html=True)
        st.markdown('<div class="results-title">🎯 Calorie Targets</div>', unsafe_allow_html=True)
        
        cals = data["daily_calories"]
        st.markdown(f"""
        <div class="calorie-grid">
            <div class="calorie-card">
                <div class="calorie-value">{cals["weight_loss"]}</div>
                <div class="calorie-label">Weight Loss<br>-0.5 kg/week</div>
            </div>
            <div class="calorie-card">
                <div class="calorie-value">{cals["mild_loss"]}</div>
                <div class="calorie-label">Mild Loss<br>-0.25 kg/week</div>
            </div>
            <div class="calorie-card active">
                <div class="calorie-value">{cals["maintenance"]}</div>
                <div class="calorie-label">Maintain<br>Current weight</div>
            </div>
            <div class="calorie-card">
                <div class="calorie-value">{cals["weight_gain"]}</div>
                <div class="calorie-label">Weight Gain<br>+0.5 kg/week</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ─── DIET RECOMMENDATIONS (ML-POWERED) ───
        st.markdown('<div class="results-card">', unsafe_allow_html=True)
        st.markdown('<div class="results-title">🥗 ML-Powered Diet Recommendations</div>', unsafe_allow_html=True)
        
        cals_per_meal = data["daily_calories"]["maintenance"] // 3
        
        st.markdown(f"""
        <div style="background: #E8F5E9; padding: 14px 18px; border-radius: 10px; margin-bottom: 16px; border-left: 4px solid #4CAF50;">
            <strong style="color: #2E7D32 !important;">💡 How it works:</strong>
            <span style="color: #333 !important;">Finding recipes matching ~{cals_per_meal} kcal/meal from {recipe_count_label} options using KNN + Cosine Similarity</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Try real ML recommendations
        recipes_fetched = False
        try:
            nutrition_input = [
                float(cals_per_meal),  # Calories per meal
                15.0, 5.0, 50.0, 500.0,  # Fat, SatFat, Cholesterol, Sodium
                50.0, 5.0, 10.0, 30.0    # Carbs, Fiber, Sugar, Protein
            ]
            
            result = APIClient.diet_recommendation(nutrition_input, ingredients=[], k=5)
            
            if result["success"]:
                ml_recipes = result["data"].get("output", [])
                
                if ml_recipes:
                    recipes_fetched = True
                    for idx, recipe in enumerate(ml_recipes):
                        name = recipe.get("Name", "Recipe")
                        name_html = escape_html(name, 120)
                        cal = int(recipe.get("Calories", 0))
                        pro = round(recipe.get("ProteinContent", 0), 1)
                        carb = round(recipe.get("CarbohydrateContent", 0), 1)
                        fat_val = round(recipe.get("FatContent", 0), 1)
                        fiber = round(recipe.get("FiberContent", 0), 1)
                        ingredients = recipe.get("RecipeIngredientParts", [])[:5]
                        
                        st.markdown(f"""
                        <div class="recipe-card">
                            <div class="recipe-name">🍽️ {name_html}</div>
                            <div class="recipe-nutrients">
                                <span class="nutrient-item">🔥 {cal} kcal</span>
                                <span class="nutrient-item">💪 {pro}g protein</span>
                                <span class="nutrient-item">🌾 {carb}g carbs</span>
                                <span class="nutrient-item">🥑 {fat_val}g fat</span>
                                <span class="nutrient-item">🌿 {fiber}g fiber</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Save + Expand row
                        btn_col, exp_col = st.columns([1, 2])
                        with btn_col:
                            auth_token = st.session_state.get('auth_token')
                            if auth_token:
                                if st.button(f"⭐ Save", key=f"save_diet_{idx}"):
                                    result = APIClient.save_meal(
                                        meal_name=name, calories=float(cal),
                                        protein=float(pro), carbs=float(carb), fat=float(fat_val),
                                        meal_type="saved", auth_token=auth_token
                                    )
                                    handle_auth_expired(result)
                                    if result["success"]:
                                        st.success(f"⭐ Saved: {name[:30]}")
                                    else:
                                        st.error(result.get("error", "Failed to save"))
                        with exp_col:
                            if ingredients:
                                with st.expander(f"📜 Ingredients"):
                                    for ing in ingredients:
                                        st.markdown(f"• {ing}")
        except:
            pass
        
        # Fallback if API unavailable
        if not recipes_fetched:
            st.info("⚡ Backend offline — showing curated example meals. Start the Docker backend for real ML recommendations.")
            
            meal_tabs = st.tabs(["🍳 Breakfast", "🍛 Lunch", "🍽️ Dinner"])
            
            sample_meals = {
                "Breakfast": [
                    {"name": "Greek Yogurt Parfait with Berries", "calories": 350, "protein": 20, "carbs": 45, "fat": 12},
                    {"name": "Avocado Toast with Poached Eggs", "calories": 420, "protein": 18, "carbs": 32, "fat": 24},
                    {"name": "Oatmeal with Banana & Almonds", "calories": 380, "protein": 12, "carbs": 55, "fat": 14}
                ],
                "Lunch": [
                    {"name": "Grilled Chicken Quinoa Bowl", "calories": 520, "protein": 38, "carbs": 48, "fat": 18},
                    {"name": "Mediterranean Salad with Feta", "calories": 450, "protein": 22, "carbs": 35, "fat": 22},
                    {"name": "Turkey Avocado Wrap", "calories": 480, "protein": 30, "carbs": 42, "fat": 19}
                ],
                "Dinner": [
                    {"name": "Baked Salmon with Vegetables", "calories": 550, "protein": 42, "carbs": 28, "fat": 26},
                    {"name": "Chicken Stir Fry with Brown Rice", "calories": 520, "protein": 35, "carbs": 52, "fat": 16},
                    {"name": "Grilled Tofu with Quinoa", "calories": 420, "protein": 28, "carbs": 45, "fat": 14}
                ]
            }
            
            for i, (meal_type, meals) in enumerate(sample_meals.items()):
                with meal_tabs[i]:
                    for meal in meals:
                        st.markdown(f"""
                        <div class="recipe-card">
                            <div class="recipe-name">🍽️ {meal["name"]}</div>
                            <div class="recipe-nutrients">
                                <span class="nutrient-item">🔥 {meal["calories"]} kcal</span>
                                <span class="nutrient-item">💪 {meal["protein"]}g protein</span>
                                <span class="nutrient-item">🌾 {meal["carbs"]}g carbs</span>
                                <span class="nutrient-item">🥑 {meal["fat"]}g fat</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ─── WORKOUT PREVIEW ───
        st.markdown('<div class="results-card">', unsafe_allow_html=True)
        st.markdown('<div class="results-title">🏋️ Workout Preview</div>', unsafe_allow_html=True)
        
        workout = data["workout_plan"]
        st.success(f"**Focus:** {workout['focus']}")
        
        for exercise in workout["exercises"][:4]:
            st.markdown(f"✅ {exercise}")
        
        st.info(f"💡 **Tip:** {workout['tips']}")
        
        if st.button("🏋️ View Full Workout Plan", use_container_width=True):
            st.switch_page("pages/3_🏋️_Workout_Recommendation.py")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        # Empty state
        st.markdown("""
        <div class="results-card" style="text-align: center; padding: 60px 40px;">
            <div style="font-size: 4rem; margin-bottom: 20px;">📊</div>
            <h3 style="color: #333;">Ready to analyze your health?</h3>
            <p style="color: #666;">Enter your details in the form and click <strong>Analyze & Recommend</strong> to get personalized diet recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info(f"💡 **How it works:** Our ML algorithm analyzes your health profile and matches you with nutritionally optimal recipes from {recipe_count_label} options.")
