"""Shared Streamlit UI polish layer."""
import streamlit as st


def inject_ui_polish() -> None:
    """Apply final visual-system overrides consistently across pages."""
    st.markdown(
        """
        <style>
            :root {
                --targ-bg: #F6F8F4;
                --targ-surface: #FFFFFF;
                --targ-border: #D8E3D6;
                --targ-text: #000000;
                --targ-muted: #647067;
                --targ-green: #2F7D48;
                --targ-green-dark: #1F5F39;
                --targ-mint: #D9F0DF;
                --targ-pale: #EFF8F0;
                --targ-teal: #0F766E;
                --targ-blue: #2563EB;
                --targ-amber: #D97706;
                --targ-rose: #E11D48;
                --targ-radius: 8px;
                --targ-shadow: 0 1px 2px rgba(20, 33, 24, 0.07), 0 10px 28px rgba(20, 33, 24, 0.06);
            }

            * {
                letter-spacing: 0 !important;
            }

            .stApp {
                background: var(--targ-bg) !important;
                color: var(--targ-text) !important;
            }

            .block-container {
                max-width: 1180px;
                padding-top: 1.25rem;
                padding-bottom: 3rem;
            }

            section[data-testid="stSidebar"] {
                background: #FFFFFF !important;
                border-right: 1px solid var(--targ-border);
            }

            section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
            section[data-testid="stSidebar"] li {
                color: var(--targ-muted) !important;
                line-height: 1.45;
            }

            .page-header,
            .auth-header,
            .hero-section,
            .footer-section {
                background: linear-gradient(135deg, var(--targ-mint) 0%, var(--targ-pale) 64%, #FFFFFF 100%) !important;
                border-radius: 10px !important;
                box-shadow: var(--targ-shadow) !important;
                padding: 28px 30px !important;
                margin-bottom: 24px !important;
                border: 1px solid var(--targ-border) !important;
            }

            .hero-section::before,
            .feature-card::before {
                display: none !important;
            }

            .hero-title,
            .page-title,
            .auth-title {
                font-size: clamp(2rem, 2.2rem, 2.4rem) !important;
                line-height: 1.08 !important;
                color: var(--targ-text) !important;
            }

            .hero-subtitle,
            .page-subtitle,
            .auth-subtitle {
                max-width: 760px;
                margin-left: auto !important;
                margin-right: auto !important;
                color: var(--targ-muted) !important;
            }

            .page-header *,
            .auth-header *,
            .hero-section *,
            .footer-section *,
            .success-banner *,
            .workout-card,
            .workout-card *,
            .exercise-item,
            .exercise-item *,
            .exercise-number,
            .schedule-day.active,
            .schedule-day.active *,
            .summary-card,
            .summary-card *,
            .day-header,
            .day-header *,
            .grocery-header,
            .grocery-header *,
            .calorie-card.active,
            .calorie-card.active *,
            .calorie-card.primary,
            .calorie-card.primary *,
            .nutrient-badge.calories,
            .target-badge,
            .target-badge *,
            .step-number,
            .cta-primary,
            .cta-primary *,
            .footer-title,
            .footer-subtitle,
            .footer-tagline {
                color: var(--targ-text) !important;
            }

            .flow-panel {
                background: var(--targ-surface);
                border: 1px solid var(--targ-border);
                border-radius: var(--targ-radius);
                box-shadow: 0 1px 2px rgba(20, 33, 24, 0.05);
                padding: 14px 16px;
                margin: 12px 0 10px 0;
            }

            .flow-heading {
                color: var(--targ-text) !important;
                font-size: 0.95rem;
                margin-bottom: 10px;
            }

            .flow-badges {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }

            .flow-badges span {
                background: var(--targ-pale);
                border: 1px solid var(--targ-border);
                border-radius: 8px;
                color: var(--targ-text) !important;
                font-size: 0.8rem;
                padding: 4px 8px;
            }

            .card,
            .auth-card,
            .form-card,
            .results-card,
            .feature-card,
            .meal-card,
            .recipe-card,
            .grocery-list,
            .tech-container,
            .tips-box {
                background: var(--targ-surface) !important;
                border: 1px solid var(--targ-border) !important;
                border-radius: var(--targ-radius) !important;
                box-shadow: var(--targ-shadow) !important;
            }

            .card,
            .auth-card,
            .form-card,
            .results-card,
            .feature-card {
                padding: 20px !important;
            }

            .feature-grid {
                gap: 16px !important;
            }

            .feature-card {
                border-top: 3px solid var(--targ-green) !important;
            }

            .feature-card:nth-child(4n+2) {
                border-top-color: var(--targ-blue) !important;
            }

            .feature-card:nth-child(4n+3) {
                border-top-color: var(--targ-amber) !important;
            }

            .feature-card:nth-child(4n+4) {
                border-top-color: var(--targ-rose) !important;
            }

            .section-header {
                text-align: left !important;
                margin: 34px 0 16px 0 !important;
            }

            .section-title,
            .card-title,
            .results-title {
                color: var(--targ-green-dark) !important;
                line-height: 1.2 !important;
            }

            .section-subtitle,
            .feature-desc,
            .step-desc {
                color: var(--targ-muted) !important;
            }

            div[data-testid="stMetric"] {
                background: var(--targ-surface);
                border: 1px solid var(--targ-border);
                border-radius: var(--targ-radius);
                padding: 14px 16px;
                box-shadow: 0 1px 2px rgba(20, 33, 24, 0.05);
            }

            div[data-testid="stMetric"] label,
            div[data-testid="stMetric"] p {
                color: var(--targ-muted) !important;
            }

            div[data-testid="stMetricValue"] {
                color: var(--targ-text) !important;
            }

            .stButton > button {
                min-height: 44px;
                border-radius: var(--targ-radius) !important;
                background: var(--targ-mint) !important;
                border: 1px solid rgba(47, 125, 72, 0.45) !important;
                box-shadow: 0 1px 2px rgba(20, 33, 24, 0.08) !important;
                color: var(--targ-text) !important;
                white-space: normal;
                transition: background 160ms ease, border-color 160ms ease, transform 160ms ease;
            }

            .stButton > button * {
                color: var(--targ-text) !important;
            }

            .stButton > button:hover {
                background: var(--targ-pale) !important;
                border-color: var(--targ-green) !important;
                transform: translateY(-1px);
            }

            input,
            textarea,
            div[data-baseweb="select"] > div {
                border-radius: var(--targ-radius) !important;
            }

            div[data-testid="stAlert"] {
                border-radius: var(--targ-radius) !important;
                border: 1px solid var(--targ-border);
            }

            .tech-badge,
            .nutrient-badge,
            .target-badge,
            .user-badge {
                border-radius: var(--targ-radius) !important;
            }

            .steps-container {
                justify-content: flex-start !important;
                gap: 18px !important;
            }

            .step-item {
                background: var(--targ-surface);
                border: 1px solid var(--targ-border);
                border-radius: var(--targ-radius);
                padding: 18px;
                max-width: 245px !important;
                box-shadow: 0 1px 2px rgba(20, 33, 24, 0.05);
            }

            .step-number {
                background: var(--targ-mint) !important;
                color: var(--targ-text) !important;
                box-shadow: none !important;
            }

            .success-banner,
            .workout-card,
            .summary-card,
            .day-header,
            .grocery-header,
            .calorie-card.active,
            .calorie-card.primary,
            .schedule-day.active,
            .nutrient-badge.calories,
            .target-badge,
            .cta-primary {
                background: var(--targ-mint) !important;
                border: 1px solid rgba(47, 125, 72, 0.28) !important;
                box-shadow: 0 1px 2px rgba(20, 33, 24, 0.06) !important;
            }

            .cta-secondary:hover,
            .cta-secondary:hover * {
                background: var(--targ-pale) !important;
                color: var(--targ-text) !important;
            }

            .bmi-badge,
            .bmi-badge *,
            .bmi-normal,
            .bmi-underweight,
            .bmi-overweight,
            .bmi-obese {
                color: var(--targ-text) !important;
            }

            .bmi-normal {
                background: #D9F0DF !important;
            }

            .bmi-underweight {
                background: #FFF3D6 !important;
            }

            .bmi-overweight {
                background: #FFE2D8 !important;
            }

            .bmi-obese {
                background: #FDE2E7 !important;
            }

            .exercise-number,
            .day-calories,
            .stat-item {
                background: rgba(255,255,255,0.72) !important;
                border: 1px solid rgba(47, 125, 72, 0.18) !important;
            }

            @media (max-width: 768px) {
                .block-container {
                    padding-left: 1rem;
                    padding-right: 1rem;
                }

                .page-header,
                .auth-header,
                .hero-section {
                    padding: 22px 18px !important;
                }

                .hero-title,
                .page-title,
                .auth-title {
                    font-size: 1.75rem !important;
                }

                .card,
                .auth-card,
                .form-card,
                .results-card,
                .feature-card {
                    padding: 16px !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
