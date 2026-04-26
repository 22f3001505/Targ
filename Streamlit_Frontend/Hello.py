"""
TARG - Landing Page
Healthcare-Grade Premium UI
"""
import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
try:
    from api import APIClient
except ImportError:
    APIClient = None
from ui.polish import inject_ui_polish
from ui.ux import require_login

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="TARG - Personalized Health & Nutrition",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logo path
LOGO_PATH = Path(__file__).parent / "logo.png"

require_login("Hello.py")

# ═══════════════════════════════════════════════════════════════
# PREMIUM CSS - HEALTHCARE GRADE DESIGN
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* ══════════ IMPORTS ══════════ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* ══════════ GLOBAL RESET ══════════ */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FFF8 100%);
        color: #333333;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Fix text visibility */
    p, span, div, label, h1, h2, h3, h4, h5, h6 {
        color: #333333 !important;
    }
    
    .stMarkdown, .stText {
        color: #333333 !important;
    }
    
    /* ══════════ HERO SECTION ══════════ */
    .hero-section {
        text-align: center;
        padding: 60px 40px;
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        border-radius: 24px;
        margin-bottom: 40px;
        box-shadow: 0 20px 60px rgba(76, 175, 80, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    }
    
    .hero-logo {
        width: 140px;
        height: 140px;
        margin: 0 auto 20px auto;
        border-radius: 24px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: rgba(255,255,255,0.9);
        margin-top: 12px;
        font-weight: 400;
    }
    
    .hero-tagline {
        font-size: 1rem;
        color: rgba(255,255,255,0.75);
        margin-top: 20px;
        font-style: italic;
    }
    
    /* ══════════ STATS SECTION ══════════ */
    .stats-container {
        display: flex;
        justify-content: center;
        gap: 40px;
        margin-top: 40px;
        flex-wrap: wrap;
    }
    
    .stat-item {
        text-align: center;
        padding: 20px 30px;
        background: rgba(255,255,255,0.15);
        border-radius: 16px;
        backdrop-filter: blur(10px);
        min-width: 140px;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: #FFFFFF !important;
        display: block;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.85) !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 4px;
    }
    
    /* ══════════ SECTION HEADERS ══════════ */
    .section-header {
        text-align: center;
        margin: 50px 0 30px 0;
    }
    
    .section-title {
        font-size: 2rem;
        font-weight: 700;
        color: #2E7D32 !important;
        margin: 0;
    }
    
    .section-subtitle {
        font-size: 1rem;
        color: #666666 !important;
        margin-top: 8px;
    }
    
    /* ══════════ FEATURE CARDS ══════════ */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 24px;
        margin: 30px 0;
    }
    
    .feature-card {
        background: #FFFFFF;
        border: 1px solid rgba(76, 175, 80, 0.1);
        border-radius: 16px;
        padding: 30px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
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
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(76, 175, 80, 0.15);
        border-color: rgba(76, 175, 80, 0.3);
    }
    
    .feature-card:hover::before {
        transform: scaleX(1);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 16px;
        display: block;
    }
    
    .feature-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #333333 !important;
        margin-bottom: 10px;
    }
    
    .feature-desc {
        font-size: 0.95rem;
        color: #666666 !important;
        line-height: 1.6;
    }
    
    /* ══════════ CTA BUTTONS ══════════ */
    .cta-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 40px 0;
        flex-wrap: wrap;
    }
    
    .cta-primary {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        padding: 16px 40px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1.1rem;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(76, 175, 80, 0.4);
    }
    
    .cta-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(76, 175, 80, 0.5);
    }
    
    .cta-secondary {
        background: #FFFFFF;
        color: #4CAF50;
        padding: 16px 40px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1.1rem;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        border: 2px solid #4CAF50;
        transition: all 0.3s ease;
    }
    
    .cta-secondary:hover {
        background: #4CAF50;
        color: white;
    }
    
    /* ══════════ HOW IT WORKS ══════════ */
    .steps-container {
        display: flex;
        justify-content: center;
        gap: 30px;
        flex-wrap: wrap;
        margin: 30px 0;
    }
    
    .step-item {
        text-align: center;
        max-width: 220px;
        position: relative;
    }
    
    .step-number {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0 auto 16px auto;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
    }
    
    .step-title {
        font-weight: 600;
        color: #333333 !important;
        margin-bottom: 8px;
        font-size: 1.1rem;
    }
    
    .step-desc {
        font-size: 0.9rem;
        color: #666666 !important;
        line-height: 1.5;
    }
    
    /* ══════════ TECH STACK ══════════ */
    .tech-container {
        display: flex;
        justify-content: center;
        gap: 16px;
        flex-wrap: wrap;
        margin: 30px 0;
        padding: 30px;
        background: linear-gradient(135deg, #A5D6A7 0%, #C8E6C9 100%);
        border-radius: 16px;
    }
    
    .tech-badge {
        background: #FFFFFF;
        padding: 12px 24px;
        border-radius: 50px;
        font-weight: 500;
        font-size: 0.9rem;
        color: #333333 !important;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* ══════════ FOOTER ══════════ */
    .footer-section {
        text-align: center;
        padding: 40px;
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        border-radius: 20px 20px 0 0;
        margin-top: 60px;
        color: white;
    }
    
    .footer-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    .footer-subtitle {
        opacity: 0.85;
        font-size: 1rem;
    }
    
    .footer-tagline {
        margin-top: 20px;
        font-size: 0.9rem;
        opacity: 0.7;
    }
    
    /* ══════════ SIDEBAR ══════════ */
    .sidebar-logo {
        text-align: center;
        padding: 20px 0;
    }
    
    /* ══════════ STREAMLIT OVERRIDES ══════════ */
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
    }
    
    /* Success/Info boxes */
    .stSuccess {
        background-color: rgba(76, 175, 80, 0.1);
        border-left-color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)
inject_ui_polish()

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=180)
    st.markdown("---")
    
    # Auth status
    if 'auth_token' in st.session_state and st.session_state.auth_token:
        user = st.session_state.get('user_data', {})
        st.success(f"✅ Logged in as **{user.get('username', 'User')}**")
    else:
        st.info("🔐 [Create an account](0_🔐_Account) to save your data")
    
    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    st.markdown("""
    - 🏠 **Home** ← You are here
    - 🔐 Account
    - 💪 Diet Recommendation
    - 🔍 Custom Food Search
    - 🏋️ Workout Plans
    - 📊 Macro Tracker
    - 📅 Meal Planner
    """)
    st.markdown("---")
    
    # Health status
    if "health_data" in st.session_state and st.session_state.health_data:
        data = st.session_state.health_data
        st.success(f"📊 BMI: **{data.get('bmi', 'N/A')}** | Cal: **{data.get('daily_calories', {}).get('maintenance', 'N/A')}**")
    else:
        st.caption("💡 Start with **Diet Recommendation** for personalized guidance!")
    
    # Backend status
    st.markdown("---")
    if APIClient:
        status = APIClient.check_health()
        if status.get("connected"):
            st.success(f"🟢 API v{status['version']} · {status['dataset_size']:,} recipes · {status.get('exercise_count', 0)} exercises")
        else:
            st.warning("🔴 API Offline")

# ═══════════════════════════════════════════════════════════════
# HERO SECTION
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-section">
    <div class="hero-title">🥗 TARG</div>
    <div class="hero-subtitle">Your AI-Powered Personal Health & Nutrition Companion</div>
    <div class="hero-tagline">"Personalized health, powered by data."</div>
</div>
""", unsafe_allow_html=True)

# Stats row — use real count if API available
recipe_count = "375K+"
exercise_count = "198"
if APIClient:
    hs = APIClient.check_health()
    if hs.get("connected") and hs.get("dataset_size", 0) > 0:
        ds = hs["dataset_size"]
        recipe_count = f"{ds:,}" if ds < 10000 else f"{ds//1000}K+"
        exercise_count = str(hs.get("exercise_count", 198))

sc1, sc2, sc3, sc4 = st.columns(4)
sc1.metric("📚 Recipes", recipe_count)
sc2.metric("🧬 Nutrients", "9")
sc3.metric("🏋️ Exercises", exercise_count)
sc4.metric("💯 Free", "100%")

# ═══════════════════════════════════════════════════════════════
# QUICK ACTIONS
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><h2 class="section-title">🚀 Get Started</h2><p class="section-subtitle">Choose your path to better health</p></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("💪 Get Diet Plan", use_container_width=True, type="primary"):
        st.switch_page("pages/1_💪_Diet_Recommendation.py")

with col2:
    if st.button("🔍 Search Foods", use_container_width=True):
        st.switch_page("pages/2_🔍_Custom_Food_Recommendation.py")

with col3:
    if st.button("🏋️ Workout Plans", use_container_width=True):
        st.switch_page("pages/3_🏋️_Workout_Recommendation.py")

with col4:
    if st.button("📊 Track Macros", use_container_width=True):
        st.switch_page("pages/4_📊_Macro_Tracker.py")

# ═══════════════════════════════════════════════════════════════
# WHY TARG SECTION
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><h2 class="section-title">✨ Why TARG?</h2><p class="section-subtitle">Healthcare-grade recommendations powered by machine learning</p></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="feature-grid">
    <div class="feature-card">
        <span class="feature-icon">🧠</span>
        <div class="feature-title">ML-Powered Intelligence</div>
        <div class="feature-desc">Our KNN algorithm with cosine similarity analyzes {recipe_count} recipes to find your closest nutritional match.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">📊</span>
        <div class="feature-title">Medical-Grade Formulas</div>
        <div class="feature-desc">BMI, BMR, and TDEE calculated using Mifflin-St Jeor and WHO-standard equations.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">🏋️</span>
        <div class="feature-title">Personalized Workouts</div>
        <div class="feature-desc">Exercise plans tailored to your BMI category with safety-first recommendations.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">🥗</span>
        <div class="feature-title">Complete Nutrition</div>
        <div class="feature-desc">Track 9 key nutrients with interactive visualizations and meal planning tools.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# HOW IT WORKS
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><h2 class="section-title">⚡ How It Works</h2><p class="section-subtitle">Simple 4-step process to better health</p></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="steps-container">
    <div class="step-item">
        <div class="step-number">1</div>
        <div class="step-title">Enter Details</div>
        <div class="step-desc">Provide basic health info: age, height, weight, activity level</div>
    </div>
    <div class="step-item">
        <div class="step-number">2</div>
        <div class="step-title">Health Analysis</div>
        <div class="step-desc">Get BMI, BMR, and daily calorie requirements</div>
    </div>
    <div class="step-item">
        <div class="step-number">3</div>
        <div class="step-title">AI Matching</div>
        <div class="step-desc">ML finds nutritionally aligned recipes from {recipe_count} options</div>
    </div>
    <div class="step-item">
        <div class="step-number">4</div>
        <div class="step-title">Get Your Plan</div>
        <div class="step-desc">Receive personalized diet and workout recommendations</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TECH STACK
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><h2 class="section-title">🛠️ Built With Modern Tech</h2></div>', unsafe_allow_html=True)

st.markdown("""
<div class="tech-container">
    <span class="tech-badge">🐍 Python 3.10+</span>
    <span class="tech-badge">🧠 Scikit-Learn</span>
    <span class="tech-badge">⚡ FastAPI</span>
    <span class="tech-badge">🎨 Streamlit</span>
    <span class="tech-badge">📊 Plotly</span>
    <span class="tech-badge">🐳 Docker</span>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# ML EXPLAINER
# ═══════════════════════════════════════════════════════════════
with st.expander("🧠 How does the ML algorithm work?", expanded=False):
    st.markdown(f"""
    ### Content-Based Filtering with K-Nearest Neighbors
    
    TARG uses a **scientifically-backed approach** to find foods that match your nutritional needs:
    
    1. **Feature Extraction**: Each active recipe is represented as a 9-dimensional vector:
       - Calories, Protein, Carbs, Fat, Fiber, Saturated Fat, Cholesterol, Sodium, Sugar
    
    2. **Normalization**: We use `StandardScaler` to normalize all features, ensuring no single nutrient dominates the similarity calculation.
    
    3. **Similarity Metric**: Cosine similarity measures the angle between two nutritional profiles:
    
    ```
    Similarity(A, B) = (A · B) / (||A|| × ||B||)
    ```
    
    4. **K-Nearest Neighbors**: Given your target nutrition, we find the K most similar recipes in our dataset.
    
    **Why this approach?**
    - ✅ Explainable recommendations
    - ✅ No cold-start problem
    - ✅ Works with any nutritional target
    - ✅ Fast inference (< 100ms)
    """)

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer-section">
    <div class="footer-title">🥗 TARG</div>
    <div class="footer-subtitle">Your Personal Health & Nutrition Companion</div>
    <div class="footer-tagline">Machine learning for healthier lives.</div>
</div>
""", unsafe_allow_html=True)
