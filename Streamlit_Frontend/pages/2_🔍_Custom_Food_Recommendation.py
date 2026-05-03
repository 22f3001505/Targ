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
from ui.ux import add_tracked_meal_to_session, handle_auth_expired, render_flow_status, require_login

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
    nutrition_mode = st.button("📊 Search by Nutrition", width="stretch", type="primary")
    st.caption("Specify exact nutritional targets")

with mode_col2:
    ingredient_mode = st.button("🥗 Search by Ingredients", width="stretch")
    st.caption("Find recipes with specific ingredients")

st.markdown('</div>', unsafe_allow_html=True)

# Session state for mode
if 'search_mode' not in st.session_state:
    st.session_state.search_mode = "nutrition"
if 'custom_search_results' not in st.session_state:
    st.session_state.custom_search_results = []
if 'custom_search_title' not in st.session_state:
    st.session_state.custom_search_title = ""
if 'custom_search_key' not in st.session_state:
    st.session_state.custom_search_key = "nutrition"

if nutrition_mode:
    if st.session_state.search_mode != "nutrition":
        st.session_state.custom_search_results = []
        st.session_state.custom_search_title = ""
    st.session_state.search_mode = "nutrition"
    st.session_state.custom_search_key = "nutrition"
if ingredient_mode:
    if st.session_state.search_mode != "ingredients":
        st.session_state.custom_search_results = []
        st.session_state.custom_search_title = ""
    st.session_state.search_mode = "ingredients"
    st.session_state.custom_search_key = "ingredients"

health_meal_calories = 400
if 'health_data' in st.session_state and st.session_state.health_data:
    maintenance = int(st.session_state.health_data.get('daily_calories', {}).get('maintenance', 0) or 0)
    if maintenance > 0:
        health_meal_calories = min(1000, max(100, round((maintenance / 3) / 10) * 10))


def _recipe_number(recipe: dict, key: str, default: float = 0) -> float:
    try:
        return float(recipe.get(key, default) or default)
    except (TypeError, ValueError):
        return default


def _recipe_ingredients(recipe: dict) -> list:
    ingredients = recipe.get("RecipeIngredientParts", [])
    if isinstance(ingredients, str):
        return [ingredients]
    if isinstance(ingredients, list):
        return ingredients
    return []


def _store_recipe_results(results: list, title: str, key_prefix: str) -> None:
    st.session_state.custom_search_results = results
    st.session_state.custom_search_title = title
    st.session_state.custom_search_key = key_prefix


def render_recipe_results(results: list, title: str, key_prefix: str) -> None:
    if not results:
        return

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">{escape_html(title, 220)}</div>', unsafe_allow_html=True)

    auth_token = st.session_state.get('auth_token')
    for idx, recipe in enumerate(results):
        if not isinstance(recipe, dict):
            continue
        name = recipe.get("Name", "Recipe")
        name_html = escape_html(name, 120)
        cal = int(_recipe_number(recipe, "Calories"))
        pro = round(_recipe_number(recipe, "ProteinContent"), 1)
        carb = round(_recipe_number(recipe, "CarbohydrateContent"), 1)
        fat_val = round(_recipe_number(recipe, "FatContent"), 1)

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

        recipe_ings = _recipe_ingredients(recipe)[:5]
        if recipe_ings:
            with st.expander(f"📜 Ingredients for {str(name)[:25]}..."):
                for ing in recipe_ings:
                    st.markdown(f"• {escape_html(ing, 120)}")

        if auth_token:
            save_col, track_col = st.columns(2)
            with save_col:
                if st.button("⭐ Save", key=f"save_{key_prefix}_{idx}", width="stretch"):
                    result_save = APIClient.save_meal(
                        meal_name=str(name), calories=float(cal),
                        protein=float(pro), carbs=float(carb), fat=float(fat_val),
                        meal_type="saved", auth_token=auth_token,
                        recipe_data=recipe,
                    )
                    handle_auth_expired(result_save)
                    if result_save["success"]:
                        st.success(f"⭐ Saved: {str(name)[:30]}")
                    else:
                        st.error(result_save.get("error", "Failed to save"))
            with track_col:
                if st.button("➕ Track", key=f"track_{key_prefix}_{idx}", width="stretch"):
                    track_result = add_tracked_meal_to_session(str(name), cal, pro, carb, fat_val)
                    if track_result.get("success"):
                        st.success(f"Added to Macro Tracker: {str(name)[:30]}")
                        if not track_result.get("cloud_synced") and auth_token:
                            st.info("Backend is unavailable, so this meal is tracked locally for this session.")
                        if hasattr(st, "page_link"):
                            st.page_link("pages/4_📊_Macro_Tracker.py", label="Open Macro Tracker")
                    else:
                        st.error(track_result.get("error", "Could not add to tracker"))

    st.markdown('</div>', unsafe_allow_html=True)

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
        
        search_btn = st.form_submit_button("🔍 Find Recipes", width="stretch")
    
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
                        _store_recipe_results(
                            results,
                            f"✅ Found {len(results)} Matching Recipes",
                            "nutrition",
                        )
                    else:
                        _store_recipe_results([], "", "nutrition")
                        st.warning("No recipes found. Try adjusting your targets.")
                else:
                    _store_recipe_results([], "", "nutrition")
                    st.error("⚠️ **Backend unavailable.** Start the API server for ML-powered recommendations.")
                    st.info("💡 Run `uvicorn main:app --port 8080` in the FastAPI_Backend folder.")
                    
            except Exception as e:
                _store_recipe_results([], "", "nutrition")
                st.error("⚠️ **Backend unavailable.** Start the API server for ML-powered recommendations.")
                st.caption(f"Detail: {str(e)[:100]}")

    render_recipe_results(
        st.session_state.get("custom_search_results", []),
        st.session_state.get("custom_search_title", ""),
        st.session_state.get("custom_search_key", "nutrition"),
    )

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
    
    if st.button("🔍 Search Recipes", width="stretch"):
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
                        _store_recipe_results(
                            results,
                            f"✅ {len(results)} ML-Matched Recipes for: {', '.join(ingredients_list)}",
                            "ingredients",
                        )
                    else:
                        _store_recipe_results([], "", "ingredients")
                        st.warning("No recipes found matching those ingredients. Try different combinations.")
                else:
                    _store_recipe_results([], "", "ingredients")
                    st.error("⚠️ **Backend unavailable.** Start the API server for ingredient-based search.")
                    st.info("💡 Run `uvicorn main:app --port 8080` in the FastAPI_Backend folder.")
        else:
            _store_recipe_results([], "", "ingredients")
            st.warning("Please enter some ingredients to search.")
    
    st.markdown('</div>', unsafe_allow_html=True)

    render_recipe_results(
        st.session_state.get("custom_search_results", []),
        st.session_state.get("custom_search_title", ""),
        st.session_state.get("custom_search_key", "ingredients"),
    )
