"""
TARG - Custom Food Recommendation
Premium Search by Nutrition or Ingredients
"""
import streamlit as st
import requests
from pathlib import Path
from api import APIClient, BASE_URL
from ui.polish import inject_ui_polish
from ui.safe import escape_html
from ui.ux import handle_auth_expired, render_flow_status, require_login

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Custom Food Search - TARG",
    page_icon="🔍",
    layout="wide"
)

LOGO_PATH = Path(__file__).parent.parent / "logo.png"

require_login("pages/2_🔍_Custom_Food_Recommendation.py")

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
    
    .stMarkdown, .stText, .stSelectbox label, .stSlider label, .stTextArea label {
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
    .nutrient-badge.calories { color: white !important; }
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
    
    /* Search Modes */
    .mode-selector {
        display: flex;
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .mode-card {
        flex: 1;
        padding: 24px;
        border-radius: 14px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .mode-card.nutrition {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
    }
    
    .mode-card.ingredients {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
    }
    
    .mode-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .mode-card.active {
        border-color: #4CAF50;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.2);
    }
    
    .mode-icon {
        font-size: 2.5rem;
        margin-bottom: 12px;
    }
    
    .mode-title {
        font-weight: 600;
        color: #333;
        font-size: 1.1rem;
    }
    
    /* Recipe Cards */
    .recipe-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }
    
    .recipe-card {
        background: #FFFFFF;
        border: 1px solid rgba(76, 175, 80, 0.15);
        border-radius: 16px;
        padding: 24px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .recipe-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #4CAF50, #81C784);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .recipe-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(76, 175, 80, 0.15);
        border-color: #4CAF50;
    }
    
    .recipe-card:hover::before {
        transform: scaleX(1);
    }
    
    .recipe-name {
        font-size: 1.15rem;
        font-weight: 600;
        color: #333333 !important;
        margin-bottom: 12px;
    }
    
    .recipe-nutrients {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 16px;
    }
    
    .nutrient-badge {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #2E7D32;
        font-weight: 500;
    }
    
    .nutrient-badge.calories {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
    }
    
    /* Nutrition Sliders */
    .nutrition-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin: 20px 0;
    }
    
    .nutrition-item {
        background: #F8FFF8;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    
    .nutrition-label {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 8px;
    }
    
    .nutrition-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2E7D32;
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
        st.caption("🔐 Login to save favorite recipes")
    
    st.markdown("---")
    st.markdown("### 🔍 Custom Search")
    st.caption("Find recipes by nutritional values or ingredients.")
    st.markdown("---")
    st.info("💡 Use nutrition search for precise macro targets, or ingredient search for what you have on hand.")

# ═══════════════════════════════════════════════════════════════
# PAGE HEADER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-header">
    <h1 class="page-title">🔍 Custom Food Search</h1>
    <p class="page-subtitle">Find recipes that match your nutritional needs</p>
</div>
""", unsafe_allow_html=True)

render_flow_status("pages/2_🔍_Custom_Food_Recommendation.py")

# ═══════════════════════════════════════════════════════════════
# SEARCH MODE SELECTION
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">🎯 Choose Search Method</div>', unsafe_allow_html=True)

mode_col1, mode_col2 = st.columns(2)

with mode_col1:
    nutrition_mode = st.button("📊 Search by Nutrition", use_container_width=True, type="primary")
    st.caption("Specify exact nutritional targets")

with mode_col2:
    ingredient_mode = st.button("🥗 Search by Ingredients", use_container_width=True)
    st.caption("Find recipes with specific ingredients")

st.markdown('</div>', unsafe_allow_html=True)

# Session state for mode
if 'search_mode' not in st.session_state:
    st.session_state.search_mode = "nutrition"

if nutrition_mode:
    st.session_state.search_mode = "nutrition"
if ingredient_mode:
    st.session_state.search_mode = "ingredients"

health_meal_calories = 400
if 'health_data' in st.session_state and st.session_state.health_data:
    maintenance = int(st.session_state.health_data.get('daily_calories', {}).get('maintenance', 0) or 0)
    if maintenance > 0:
        health_meal_calories = min(1000, max(100, round((maintenance / 3) / 10) * 10))

# ═══════════════════════════════════════════════════════════════
# NUTRITION SEARCH
# ═══════════════════════════════════════════════════════════════
if st.session_state.search_mode == "nutrition":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Set Nutritional Targets</div>', unsafe_allow_html=True)
    
    with st.form("nutrition_search"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            calories = st.slider("🔥 Calories", 100, 1000, health_meal_calories, 10)
            fat = st.slider("🥑 Fat (g)", 0, 50, 15, 1)
            saturated = st.slider("🧈 Saturated Fat (g)", 0, 20, 5, 1)
        
        with col2:
            protein = st.slider("💪 Protein (g)", 0, 100, 30, 1)
            sodium = st.slider("🧂 Sodium (mg)", 0, 2000, 500, 50)
            carbs = st.slider("🌾 Carbs (g)", 0, 150, 50, 5)
        
        with col3:
            fiber = st.slider("🌿 Fiber (g)", 0, 30, 5, 1)
            cholesterol = st.slider("❤️ Cholesterol (mg)", 0, 300, 50, 10)
            sugar = st.slider("🍬 Sugar (g)", 0, 50, 10, 1)
        
        num_results = st.slider("Number of results", 3, 10, 5)
        
        search_btn = st.form_submit_button("🔍 Find Recipes", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if search_btn:
        with st.spinner("🔬 Searching through recipes..."):
            try:
                result = APIClient.diet_recommendation(
                    [calories, fat, saturated, cholesterol, sodium, carbs, fiber, sugar, protein],
                    ingredients=[], k=num_results
                )
                
                if result["success"]:
                    results = result["data"].get("output", [])
                    
                    if results:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown(f'<div class="card-title">✅ Found {len(results)} Matching Recipes</div>', unsafe_allow_html=True)
                        
                        for idx, recipe in enumerate(results):
                            r_name = recipe.get('Name', 'Recipe')
                            r_name_html = escape_html(r_name, 120)
                            r_cal = int(recipe.get('Calories', 0))
                            r_pro = int(recipe.get('ProteinContent', 0))
                            r_carb = int(recipe.get('CarbohydrateContent', 0))
                            r_fat = int(recipe.get('FatContent', 0))
                            
                            st.markdown(f"""
                            <div class="recipe-card">
                                <div class="recipe-name">🍽️ {r_name_html}</div>
                                <div class="recipe-nutrients">
                                    <span class="nutrient-badge calories">🔥 {r_cal} kcal</span>
                                    <span class="nutrient-badge">💪 {r_pro}g protein</span>
                                    <span class="nutrient-badge">🌾 {r_carb}g carbs</span>
                                    <span class="nutrient-badge">🥑 {r_fat}g fat</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            auth_token = st.session_state.get('auth_token')
                            if auth_token:
                                if st.button(f"⭐ Save", key=f"save_custom_{idx}"):
                                    result_save = APIClient.save_meal(
                                        meal_name=r_name, calories=float(r_cal),
                                        protein=float(r_pro), carbs=float(r_carb), fat=float(r_fat),
                                        meal_type="saved", auth_token=auth_token
                                    )
                                    handle_auth_expired(result_save)
                                    if result_save["success"]:
                                        st.success(f"⭐ Saved: {r_name[:30]}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.warning("No recipes found. Try adjusting your targets.")
                else:
                    st.error("⚠️ **Backend unavailable.** Start the API server for ML-powered recommendations.")
                    st.info("💡 Run `uvicorn main:app --port 8080` in the FastAPI_Backend folder.")
                    
            except Exception as e:
                st.error("⚠️ **Backend unavailable.** Start the API server for ML-powered recommendations.")
                st.caption(f"Detail: {str(e)[:100]}")

# ═══════════════════════════════════════════════════════════════
# INGREDIENT SEARCH
# ═══════════════════════════════════════════════════════════════
else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🥗 Search by Ingredients</div>', unsafe_allow_html=True)
    
    ingredients_input = st.text_area(
        "Enter ingredients (comma-separated)",
        placeholder="chicken, broccoli, garlic, olive oil...",
        height=100
    )
    
    col1, col2 = st.columns(2)
    with col1:
        ingredient_calorie_default = min(1000, max(200, round((health_meal_calories + 150) / 50) * 50))
        max_calories = st.slider("Max Calories", 200, 1000, ingredient_calorie_default, 50)
    with col2:
        num_results = st.slider("Results to show", 3, 10, 5)
    
    if st.button("🔍 Search Recipes", use_container_width=True):
        if ingredients_input:
            ingredients_list = [i.strip() for i in ingredients_input.split(",") if i.strip()]
            
            with st.spinner("🔬 Searching for matching recipes..."):
                result = APIClient.diet_recommendation(
                    [float(max_calories), 15.0, 5.0, 50.0, 500.0, 50.0, 5.0, 10.0, 30.0],
                    ingredients=ingredients_list, k=num_results
                )
                
                if result["success"]:
                    results = result["data"].get("output", [])
                    if results:
                        ingredients_title = escape_html(", ".join(ingredients_list), 180)
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown(f'<div class="card-title">✅ {len(results)} ML-Matched Recipes for: {ingredients_title}</div>', unsafe_allow_html=True)
                        
                        for idx, recipe in enumerate(results):
                            name = recipe.get("Name", "Recipe")
                            name_html = escape_html(name, 120)
                            cal = int(recipe.get("Calories", 0))
                            pro = round(recipe.get("ProteinContent", 0), 1)
                            carb = round(recipe.get("CarbohydrateContent", 0), 1)
                            fat_val = round(recipe.get("FatContent", 0), 1)
                            
                            st.markdown(f"""
                            <div class="recipe-card">
                                <div class="recipe-name">🍽️ {name_html}</div>
                                <div class="recipe-nutrients">
                                    <span class="nutrient-badge calories">🔥 {cal} kcal</span>
                                    <span class="nutrient-badge">💪 {pro}g protein</span>
                                    <span class="nutrient-badge">🌾 {carb}g carbs</span>
                                    <span class="nutrient-badge">🥑 {fat_val}g fat</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show ingredients
                            recipe_ings = recipe.get("RecipeIngredientParts", [])[:5]
                            if recipe_ings:
                                with st.expander(f"📜 Ingredients for {name[:25]}..."):
                                    for ing in recipe_ings:
                                        st.markdown(f"• {ing}")
                            
                            # Save button
                            auth_token = st.session_state.get('auth_token')
                            if auth_token:
                                if st.button(f"⭐ Save", key=f"save_ing_{idx}"):
                                    result_save = APIClient.save_meal(
                                        meal_name=name, calories=float(cal),
                                        protein=float(pro), carbs=float(carb), fat=float(fat_val),
                                        meal_type="saved", auth_token=auth_token
                                    )
                                    handle_auth_expired(result_save)
                                    if result_save["success"]:
                                        st.success(f"⭐ Saved: {name[:30]}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.warning("No recipes found matching those ingredients. Try different combinations.")
                else:
                    st.error("⚠️ **Backend unavailable.** Start the API server for ingredient-based search.")
                    st.info("💡 Run `uvicorn main:app --port 8080` in the FastAPI_Backend folder.")
        else:
            st.warning("Please enter some ingredients to search.")
    
    st.markdown('</div>', unsafe_allow_html=True)
