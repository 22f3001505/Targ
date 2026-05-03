"""
TARG - Weekly Meal Planner
Premium 7-Day Meal Planning with Grocery List
"""
import streamlit as st
import random
from pathlib import Path
from api import APIClient, BASE_URL
from ui.safe import escape_html
from ui.polish import inject_ui_polish
from ui.ux import handle_auth_expired, require_login

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Meal Planner - TARG",
    page_icon="📅",
    layout="wide"
)

LOGO_PATH = Path(__file__).parent.parent / "logo.png"

require_login("pages/5_📅_Meal_Planner.py")

# ═══════════════════════════════════════════════════════════════
# MEAL OPTIONS
# ═══════════════════════════════════════════════════════════════
MEALS = {
    "breakfast": [
        {"name": "Greek Yogurt Parfait", "calories": 350, "ingredients": ["Greek yogurt", "Granola", "Mixed berries", "Honey"]},
        {"name": "Avocado Toast + Eggs", "calories": 420, "ingredients": ["Whole grain bread", "Avocado", "Eggs", "Cherry tomatoes"]},
        {"name": "Oatmeal Bowl", "calories": 380, "ingredients": ["Oats", "Banana", "Almonds", "Almond milk", "Cinnamon"]},
        {"name": "Smoothie Bowl", "calories": 340, "ingredients": ["Frozen berries", "Banana", "Spinach", "Almond butter", "Chia seeds"]},
        {"name": "Egg White Omelette", "calories": 280, "ingredients": ["Egg whites", "Spinach", "Mushrooms", "Feta cheese"]},
        {"name": "Protein Pancakes", "calories": 390, "ingredients": ["Protein powder", "Oats", "Eggs", "Banana", "Maple syrup"]},
    ],
    "lunch": [
        {"name": "Grilled Chicken Salad", "calories": 480, "ingredients": ["Chicken breast", "Mixed greens", "Tomatoes", "Cucumber", "Olive oil"]},
        {"name": "Quinoa Buddha Bowl", "calories": 520, "ingredients": ["Quinoa", "Chickpeas", "Roasted vegetables", "Tahini", "Lemon"]},
        {"name": "Turkey Wrap", "calories": 450, "ingredients": ["Whole wheat tortilla", "Turkey breast", "Lettuce", "Tomato", "Hummus"]},
        {"name": "Mediterranean Plate", "calories": 510, "ingredients": ["Falafel", "Hummus", "Tabbouleh", "Pita bread", "Olives"]},
        {"name": "Salmon Poke Bowl", "calories": 540, "ingredients": ["Sushi rice", "Salmon", "Edamame", "Avocado", "Soy sauce"]},
        {"name": "Paneer Tikka Wrap", "calories": 490, "ingredients": ["Whole wheat tortilla", "Paneer", "Bell peppers", "Greek yogurt", "Mint chutney"]},
    ],
    "snack": [
        {"name": "🍌 Banana + Almonds", "calories": 180, "ingredients": ["Banana", "Almonds"]},
        {"name": "🥜 Protein Bar", "calories": 220, "ingredients": ["Protein bar"]},
        {"name": "🍎 Apple + PB", "calories": 250, "ingredients": ["Apple", "Peanut butter"]},
        {"name": "🥛 Greek Yogurt", "calories": 150, "ingredients": ["Greek yogurt"]},
        {"name": "None", "calories": 0, "ingredients": []},
    ],
    "dinner": [
        {"name": "Baked Salmon & Veggies", "calories": 550, "ingredients": ["Salmon fillet", "Asparagus", "Broccoli", "Lemon", "Olive oil"]},
        {"name": "Chicken Stir Fry", "calories": 480, "ingredients": ["Chicken breast", "Bell peppers", "Broccoli", "Brown rice", "Soy sauce"]},
        {"name": "Lean Beef Tacos", "calories": 520, "ingredients": ["Ground beef (lean)", "Corn tortillas", "Lettuce", "Salsa", "Greek yogurt"]},
        {"name": "Vegetable Curry + Rice", "calories": 460, "ingredients": ["Mixed vegetables", "Coconut milk", "Curry paste", "Basmati rice", "Cilantro"]},
        {"name": "Grilled Tofu Bowl", "calories": 420, "ingredients": ["Firm tofu", "Quinoa", "Roasted vegetables", "Teriyaki sauce"]},
        {"name": "Dal + Roti + Salad", "calories": 440, "ingredients": ["Dal", "Roti", "Mixed greens", "Cucumber", "Tomatoes"]},
    ]
}

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MEAL_SLOTS = [
    ("breakfast", "🌅 Breakfast", "Select breakfast"),
    ("lunch", "☀️ Lunch", "Select lunch"),
    ("snack", "🍫 Snack", "Select snack"),
    ("dinner", "🌙 Dinner", "Select dinner"),
]
MEAL_ALIASES = {
    "breakfast": {
        "Avocado Toast with Eggs": "Avocado Toast + Eggs",
    },
    "snack": {
        "Banana + Almonds": "🍌 Banana + Almonds",
        "Protein Bar": "🥜 Protein Bar",
        "Apple + Peanut Butter": "🍎 Apple + PB",
        "Greek Yogurt": "🥛 Greek Yogurt",
    },
    "dinner": {
        "Grilled Chicken Stir Fry": "Chicken Stir Fry",
        "Vegetable Curry": "Vegetable Curry + Rice",
    },
}


def meal_options(slot: str) -> list[str]:
    return [meal["name"] for meal in MEALS[slot]]


def resolve_meal_name(slot: str, value: object) -> str:
    options = meal_options(slot)
    default = "None" if slot == "snack" else options[0]
    meal_name = "" if value is None else str(value).strip()
    meal_name = MEAL_ALIASES.get(slot, {}).get(meal_name, meal_name)
    return meal_name if meal_name in options else default


def selected_meal(slot: str, value: object) -> dict:
    meal_name = resolve_meal_name(slot, value)
    return next(meal for meal in MEALS[slot] if meal["name"] == meal_name)

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
    
    .stMarkdown, .stText, .stSelectbox label {
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
    .day-header, .day-header * { color: white !important; }
    .grocery-header, .grocery-header * { color: white !important; }
    .meal-type { color: #4CAF50 !important; }
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
    
    /* Day Plans */
    .day-header {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .day-name {
        font-weight: 700;
        font-size: 1.2rem;
    }
    
    .day-calories {
        background: rgba(255,255,255,0.2);
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
    }
    
    /* Meal Cards */
    .meal-card {
        background: #F8FFF8;
        border: 1px solid rgba(76, 175, 80, 0.15);
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .meal-card:hover {
        transform: translateX(6px);
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.1);
        border-color: #4CAF50;
    }
    
    .meal-type {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #4CAF50;
        font-weight: 600;
        margin-bottom: 6px;
    }
    
    .meal-name {
        font-weight: 600;
        color: #333333 !important;
        font-size: 1.05rem;
    }
    
    .meal-calories {
        color: #666666 !important;
        font-size: 0.9rem;
        margin-top: 4px;
    }
    
    /* Summary Stats */
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin: 20px 0;
    }
    
    .summary-card {
        background: linear-gradient(135deg, #A5D6A7 0%, #C8E6C9 100%);
        border-radius: 14px;
        padding: 24px;
        text-align: center;
    }
    
    .summary-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2E7D32;
    }
    
    .summary-label {
        font-size: 0.85rem;
        color: #333;
        margin-top: 4px;
    }
    
    /* Grocery List */
    .grocery-header {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        padding: 16px 24px;
        border-radius: 12px 12px 0 0;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .grocery-list {
        background: #FFFFFF;
        border: 1px solid rgba(76, 175, 80, 0.1);
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 20px;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .grocery-category {
        font-weight: 600;
        color: #2E7D32;
        margin: 16px 0 8px 0;
        font-size: 0.95rem;
    }
    
    .grocery-item {
        padding: 8px 0;
        border-bottom: 1px solid #F0F0F0;
        display: flex;
        align-items: center;
        gap: 10px;
        color: #333;
    }
    
    .grocery-item:last-child {
        border-bottom: none;
    }
    
    /* Weekly Overview */
    .week-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 8px;
        margin: 20px 0;
    }
    
    .week-day {
        text-align: center;
        padding: 12px 8px;
        border-radius: 10px;
        background: #F5F5F5;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .week-day:hover {
        background: linear-gradient(135deg, #81C784 0%, #4CAF50 100%);
        color: white;
        transform: translateY(-4px);
        box-shadow: 0 6px 15px rgba(76, 175, 80, 0.2);
    }
    
    .week-day.active {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
    }
    
    .week-day-name {
        font-weight: 600;
        font-size: 0.8rem;
    }
    
    .week-day-cal {
        font-size: 0.75rem;
        margin-top: 4px;
        opacity: 0.85;
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

# Match Android: load the saved cloud plan automatically on first visit.
auth_token = st.session_state.get('auth_token')
if auth_token and not st.session_state.get("meal_plan_autoloaded"):
    saved_plan = APIClient.get_meal_plan(auth_token)
    handle_auth_expired(saved_plan)
    if saved_plan.get("success") and saved_plan.get("data") and saved_plan["data"].get("plan_data"):
        plan = saved_plan["data"]["plan_data"]
        for day in DAYS:
            if day in plan:
                for slot, _, _ in MEAL_SLOTS:
                    if plan[day].get(slot) is not None:
                        st.session_state[f"{day}_{slot}"] = resolve_meal_name(slot, plan[day][slot])
        st.session_state.meal_plan_loaded_at = saved_plan["data"].get("created_at")
    st.session_state.meal_plan_autoloaded = True

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
        st.caption("🔐 Login to save your meal plans")
    
    st.markdown("---")
    st.markdown("### 📅 Meal Planner")
    st.caption("Plan your week with balanced, nutritious meals.")
    st.markdown("---")
    
    if st.button("🎲 Randomize Week", use_container_width=True):
        for day in DAYS:
            for slot, _, _ in MEAL_SLOTS:
                st.session_state[f"{day}_{slot}"] = random.choice(meal_options(slot))
        st.success("✅ Plan randomized!")
        st.rerun()

# ═══════════════════════════════════════════════════════════════
# PAGE HEADER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-header">
    <h1 class="page-title">📅 Weekly Meal Planner</h1>
    <p class="page-subtitle">Plan your week with balanced, nutritious meals</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# WEEKLY TABS
# ═══════════════════════════════════════════════════════════════
day_tabs = st.tabs([f"📆 {day[:3]}" for day in DAYS])

weekly_totals = {"calories": 0, "ingredients": set(), "planned_items": 0}

for i, day in enumerate(DAYS):
    with day_tabs[i]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Day Header
            day_cal = 0
            
            st.markdown(f'<div class="card">', unsafe_allow_html=True)
            
            day_meals = {}
            for slot_index, (slot, slot_title, select_label) in enumerate(MEAL_SLOTS):
                st.markdown(f"#### {slot_title}")
                state_key = f"{day}_{slot}"
                st.session_state[state_key] = resolve_meal_name(slot, st.session_state.get(state_key))
                selected = st.selectbox(
                    select_label,
                    meal_options(slot),
                    key=state_key,
                    label_visibility="collapsed"
                )
                meal = selected_meal(slot, selected)
                day_meals[slot] = {"label": slot_title, "selected": resolve_meal_name(slot, selected), "meal": meal}
                day_cal += meal["calories"]
                if meal["calories"] > 0:
                    weekly_totals["planned_items"] += 1
                    weekly_totals["ingredients"].update(meal["ingredients"])

                st.markdown(f"<p style='color: #666;'>🔥 {meal['calories']} kcal</p>", unsafe_allow_html=True)

                if slot_index < len(MEAL_SLOTS) - 1:
                    st.markdown("---")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            weekly_totals["calories"] += day_cal
        
        with col2:
            # Day Summary
            # Show calorie target comparison if health data exists
            calorie_target = None
            if 'health_data' in st.session_state and st.session_state.health_data:
                calorie_target = st.session_state.health_data.get('daily_calories', {}).get('maintenance', None)
            
            target_badge = ""
            if calorie_target:
                diff = day_cal - calorie_target
                if abs(diff) <= 100:
                    target_badge = f'<span class="target-badge" style="background:#D9F0DF;color:#000000;padding:3px 8px;border-radius:8px;font-size:0.75rem;">✅ On Target</span>'
                elif diff > 100:
                    target_badge = f'<span class="target-badge" style="background:#FFE2D8;color:#000000;padding:3px 8px;border-radius:8px;font-size:0.75rem;">⬆️ +{diff} kcal</span>'
                else:
                    target_badge = f'<span class="target-badge" style="background:#FFF3D6;color:#000000;padding:3px 8px;border-radius:8px;font-size:0.75rem;">⬇️ {diff} kcal</span>'
            
            st.markdown(f"""
            <div class="day-header">
                <span class="day-name">{escape_html(day)}</span>
                <span class="day-calories">🔥 {day_cal} kcal {target_badge}</span>
            </div>
            """, unsafe_allow_html=True)

            meal_cards = []
            for slot, _, _ in MEAL_SLOTS:
                entry = day_meals[slot]
                meal_cards.append(f"""
                <div class="meal-card">
                    <div class="meal-type">{escape_html(entry["label"])}</div>
                    <div class="meal-name">{escape_html(entry["selected"])}</div>
                    <div class="meal-calories">{entry["meal"]["calories"]} kcal</div>
                </div>
                """)
            st.markdown("\n".join(meal_cards), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# WEEKLY SUMMARY & GROCERY LIST
# ═══════════════════════════════════════════════════════════════
st.markdown("---")

summary_col, grocery_col = st.columns([1, 1])

with summary_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Weekly Summary</div>', unsafe_allow_html=True)
    
    avg_daily = weekly_totals["calories"] // 7 if weekly_totals["calories"] > 0 else 0
    
    # Target comparison for weekly view
    target_html = ""
    if 'health_data' in st.session_state and st.session_state.health_data:
        calorie_target = st.session_state.health_data.get('daily_calories', {}).get('maintenance', 0)
        if calorie_target > 0:
            weekly_target = calorie_target * 7
            diff_pct = round(((weekly_totals["calories"] - weekly_target) / weekly_target) * 100) if weekly_target > 0 else 0
            if abs(diff_pct) <= 5:
                target_html = f'<div class="summary-card"><div class="summary-value" style="color:#4CAF50;">✅</div><div class="summary-label">Within 5% of target ({calorie_target}/day)</div></div>'
            elif diff_pct > 5:
                target_html = f'<div class="summary-card"><div class="summary-value" style="color:#FF7043;">+{diff_pct}%</div><div class="summary-label">Above target ({calorie_target}/day)</div></div>'
            else:
                target_html = f'<div class="summary-card"><div class="summary-value" style="color:#FFA726;">{diff_pct}%</div><div class="summary-label">Below target ({calorie_target}/day)</div></div>'
    
    st.markdown(f"""
    <div class="summary-grid">
        <div class="summary-card">
            <div class="summary-value">{weekly_totals["calories"]}</div>
            <div class="summary-label">Total Calories</div>
        </div>
        <div class="summary-card">
            <div class="summary-value">{avg_daily}</div>
            <div class="summary-label">Daily Average</div>
        </div>
        <div class="summary-card">
            <div class="summary-value">{weekly_totals["planned_items"]}</div>
            <div class="summary-label">Meals & Snacks</div>
        </div>
        {target_html}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with grocery_col:
    st.markdown('<div class="grocery-header">🛒 Grocery List</div>', unsafe_allow_html=True)
    st.markdown('<div class="grocery-list">', unsafe_allow_html=True)
    
    # Categorize ingredients
    categories = {
        "Proteins": ["Chicken breast", "Salmon fillet", "Turkey breast", "Eggs", "Egg whites", "Ground beef (lean)", "Firm tofu", "Salmon", "Falafel"],
        "Dairy": ["Greek yogurt", "Feta cheese", "Almond milk", "Coconut milk", "Paneer"],
        "Grains": ["Oats", "Quinoa", "Brown rice", "Basmati rice", "Sushi rice", "Whole grain bread", "Whole wheat tortilla", "Pita bread", "Corn tortillas", "Granola", "Roti"],
        "Vegetables": ["Spinach", "Mushrooms", "Mixed greens", "Tomatoes", "Cucumber", "Bell peppers", "Broccoli", "Asparagus", "Roasted vegetables", "Mixed vegetables", "Cherry tomatoes", "Lettuce", "Edamame"],
        "Fruits": ["Banana", "Mixed berries", "Frozen berries", "Lemon", "Avocado", "Apple"],
        "Pantry": ["Olive oil", "Honey", "Almonds", "Almond butter", "Chia seeds", "Tahini", "Hummus", "Cinnamon", "Soy sauce", "Teriyaki sauce", "Salsa", "Curry paste", "Cilantro", "Chickpeas", "Olives", "Tabbouleh", "Protein powder", "Maple syrup", "Protein bar", "Peanut butter", "Mint chutney", "Dal"]
    }
    
    ingredients = weekly_totals["ingredients"]
    categorized = set()
    
    for category, items in categories.items():
        matching = [item for item in items if item in ingredients]
        if matching:
            categorized.update(matching)
            st.markdown(f'<div class="grocery-category">{escape_html(category)}</div>', unsafe_allow_html=True)
            for item in matching:
                st.markdown(f'<div class="grocery-item">☐ {escape_html(item)}</div>', unsafe_allow_html=True)

    uncategorized = sorted(item for item in ingredients if item not in categorized)
    if uncategorized:
        st.markdown('<div class="grocery-category">Other</div>', unsafe_allow_html=True)
        for item in uncategorized:
            st.markdown(f'<div class="grocery-item">☐ {escape_html(item)}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Print button
if st.button("🖨️ Print Grocery List", use_container_width=True):
    grocery_text = "\n".join([f"☐ {item}" for item in sorted(weekly_totals["ingredients"])])
    st.text_area("Copy this list:", grocery_text, height=200)
    st.success("✅ Grocery list ready to print!")

# ═══════════════════════════════════════════════════════════════
# SAVE / LOAD MEAL PLAN (Backend Persistence)
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
auth_token = st.session_state.get('auth_token')
if auth_token:
    save_col, load_col = st.columns(2)
    with save_col:
        if st.button("💾 Save Plan to Account", use_container_width=True, type="primary"):
            plan_data = {}
            for day in DAYS:
                plan_data[day] = {}
                for slot, _, _ in MEAL_SLOTS:
                    plan_data[day][slot] = resolve_meal_name(slot, st.session_state.get(f"{day}_{slot}", ""))
            result = APIClient.save_meal_plan(plan_data, auth_token)
            handle_auth_expired(result)
            if result["success"]:
                st.success("✅ Meal plan saved! It will be restored next time you visit.")
            else:
                st.error(result.get("error", "Failed to save plan"))
    
    with load_col:
        if st.button("📥 Load Saved Plan", use_container_width=True):
            result = APIClient.get_meal_plan(auth_token)
            handle_auth_expired(result)
            if result["success"] and result["data"] and result["data"].get("plan_data"):
                plan = result["data"]["plan_data"]
                for day in DAYS:
                    if day in plan:
                        for slot, _, _ in MEAL_SLOTS:
                            if plan[day].get(slot) is not None:
                                st.session_state[f"{day}_{slot}"] = resolve_meal_name(slot, plan[day][slot])
                st.success("✅ Plan loaded!")
                st.rerun()
            else:
                st.info("No saved plan found. Build one and save it!")
else:
    st.info("🔐 **Login** to save your meal plans and access them anywhere.")
