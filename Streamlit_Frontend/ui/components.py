"""
TARG - Shared UI Components
Reusable components for consistent UI across all pages.
Import this in every page for identical look & feel.
"""
import streamlit as st
from pathlib import Path
import time
import sys
import os

# Add parent directory to path for api imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import APIClient

LOGO_PATH = Path(__file__).parent / "logo.png"

# ═══════════════════════════════════════════════════════════════
# GLOBAL CSS (inject once per page)
# ═══════════════════════════════════════════════════════════════
def inject_global_css():
    """Inject the global design system CSS. Call at the top of every page."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        .stApp {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FFF8 100%);
            color: #333333;
        }
        
        #MainMenu, footer, header {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* Fix text visibility globally */
        p, span, div, label, h1, h2, h3, h4, h5, h6 {
            color: #333333 !important;
        }
        .stMarkdown, .stText, .stSelectbox label,
        .stNumberInput label, .stSlider label, .stTextArea label {
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
        .page-header * {
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
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
            color: white !important;
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.35);
        }
        
        /* Explanation Box */
        .explanation-box {
            background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
            border-left: 4px solid #4CAF50;
            border-radius: 0 12px 12px 0;
            padding: 16px 20px;
            margin: 16px 0;
            font-size: 0.9rem;
            color: #333333 !important;
        }
        .explanation-box * {
            color: #333333 !important;
        }
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
def render_sidebar(active_page="Home"):
    """Render the consistent sidebar with logo and navigation."""
    with st.sidebar:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=160)
        st.markdown("---")
        
        # Auth status
        if 'auth_token' in st.session_state and st.session_state.auth_token:
            user = st.session_state.get('user_data', {})
            st.success(f"✅ **{user.get('username', 'User')}**")
        else:
            st.caption("🔐 Login to save your data")
        
        st.markdown("---")
        st.markdown(f"### {active_page}")
        st.caption("AI-powered health & nutrition system")
        st.markdown("---")
        
        # Show health status if available
        if "health_data" in st.session_state and st.session_state.health_data:
            data = st.session_state.health_data
            st.success(f"✅ Health analyzed (BMI: {data.get('bmi', 'N/A')})")
        else:
            st.info("💡 Start with Health Analysis to unlock all features.")
        
        # Backend status indicator
        st.markdown("---")
        status = APIClient.check_health()
        if status["connected"]:
            st.markdown(f"""
            <div style="background: #E8F5E9; padding: 8px 12px; border-radius: 8px; border-left: 3px solid #4CAF50; font-size: 0.8rem;">
                <strong style="color: #2E7D32 !important;">⚡ API Connected</strong><br>
                <span style="color: #666 !important;">v{status['version']} · {status['dataset_size']:,} recipes</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #FFF3E0; padding: 8px 12px; border-radius: 8px; border-left: 3px solid #FF9800; font-size: 0.8rem;">
                <strong style="color: #E65100 !important;">⚠️ Backend Offline</strong><br>
                <span style="color: #666 !important;">Using local fallbacks</span>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE HEADER
# ═══════════════════════════════════════════════════════════════
def page_header(title, subtitle):
    """Render the gradient page header."""
    st.markdown(f"""
    <div class="page-header">
        <h1 class="page-title">{title}</h1>
        <p class="page-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# CARD
# ═══════════════════════════════════════════════════════════════
def card_start(title=None):
    """Open a styled card. Must be followed by card_end()."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if title:
        st.markdown(f'<div class="card-title">{title}</div>', unsafe_allow_html=True)

def card_end():
    """Close a styled card."""
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# EXPLANATION BOX (ML Explainability)
# ═══════════════════════════════════════════════════════════════
def explanation_box(text):
    """Show an ML explanation with a styled info box."""
    st.markdown(f"""
    <div class="explanation-box">
        <strong>💡 How it works:</strong> {text}
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# FLOW GATE (Lock system for guided UX)
# ═══════════════════════════════════════════════════════════════
def require_health_analysis():
    """
    Gate function: blocks the page if health analysis hasn't been done.
    Returns True if analysis exists, False if blocked.
    """
    if "health_data" not in st.session_state or not st.session_state.health_data:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 60px;">
            <div style="font-size: 4rem; margin-bottom: 20px;">🔒</div>
            <h3 style="color: #333333 !important;">Step 1 Required</h3>
            <p style="color: #666666 !important;">
                Please complete your <strong>Health Analysis</strong> on the 
                <strong>Diet Recommendation</strong> page first to unlock this feature.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return False
    return True


# ═══════════════════════════════════════════════════════════════
# SMART LOADING
# ═══════════════════════════════════════════════════════════════
def smart_spinner(message="Generating your personalized plan..."):
    """Returns a context manager for a branded spinner."""
    return st.spinner(f"🔬 {message}")
