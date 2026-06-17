import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG & CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
# Environment-aware API configurations for deployment compatibility
API_URL = os.getenv(
    "API_URL",
    "https://truthlens-api.onrender.com/api/v1/predict"
)

st.set_page_config(
    page_title="TruthLens AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# STATE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "history" not in st.session_state:
    st.session_state.history = []

# ══════════════════════════════════════════════════════════════════════════════
# CENTRALIZED THEME & STYLES (Warm Purple AI Startup Theme)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Base structure modifications */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #faf9f6 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1f2937;
}
[data-testid="stAppViewContainer"] > .main {
    background-color: #faf9f6 !important;
}
.block-container {
    padding: 1.5rem 2.5rem 3rem !important;
    max-width: 1200px;
}
[data-testid="stSidebar"] {
    background-color: #f5f3ff !important;
    border-right: 1px solid #e9d5ff !important;
}
#MainMenu, footer, header {
    visibility: hidden;
}

/* Sidebar navigation buttons custom layout */
div[data-testid="stSidebar"] .stButton > button {
    border-radius: 10px !important;
    padding: 0.6rem 1rem !important;
    font-size: 0.92rem !important;
}

/* Base Cards styling */
.card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.6rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
    margin-bottom: 1.2rem;
    border: 1px solid #ede9fe;
    transition: all 0.2s ease-in-out;
}
.card:hover {
    box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.08), 0 4px 6px -2px rgba(124, 58, 237, 0.05);
    transform: translateY(-2px);
    border-color: #ddd6fe;
}

/* Hero elements styling */
.hero-container {
    background: linear-gradient(135deg, #f5f3ff 0%, #faf5ff 50%, #faf9f6 100%);
    border-radius: 24px;
    padding: 3rem;
    margin-bottom: 2.5rem;
    border: 1px solid #e9d5ff;
    position: relative;
    overflow: hidden;
}
.hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #ede9fe;
    color: #7c3aed;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 1rem;
    letter-spacing: 0.3px;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1.15;
    color: #1f2937;
    margin-bottom: 1rem;
}
.hero-title span {
    color: #7c3aed;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #7c3aed;
    font-weight: 600;
    margin-bottom: 0.8rem;
}
.hero-desc {
    font-size: 0.95rem;
    color: #4b5563;
    line-height: 1.6;
    margin-bottom: 1.8rem;
}

/* Feature grid items styling */
.feat-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.4rem;
    border: 1px solid #ede9fe;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    text-align: left;
    height: 100%;
    transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}
.feat-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(124, 58, 237, 0.08);
    border-color: #c084fc;
}
.feat-icon {
    width: 42px;
    height: 42px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    margin-bottom: 0.9rem;
}
.feat-title {
    font-size: 1rem;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 0.3rem;
}
.feat-desc {
    font-size: 0.83rem;
    color: #6b7280;
    line-height: 1.5;
}

/* Summary stats metrics styling */
.stat-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    border: 1px solid #ede9fe;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    border-left-width: 4px;
    transition: all 0.2s ease-in-out;
}
.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(124, 58, 237, 0.05);
}
.stat-label {
    font-size: 0.75rem;
    color: #9ca3af;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 4px;
}
.stat-value {
    font-size: 1.8rem;
    font-weight: 800;
    line-height: 1.1;
}
.stat-sub {
    font-size: 0.78rem;
    color: #9ca3af;
    margin-top: 3px;
}

/* Prediction Result Alert Cards */
.result-card {
    border-radius: 16px;
    padding: 1.8rem;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    border-width: 1px;
    border-style: solid;
    margin-bottom: 1.2rem;
}
.result-real {
    background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
    border-color: #a7f3d0;
}
.result-fake {
    background: linear-gradient(135deg, #fff5f5 0%, #fff1f2 100%);
    border-color: #fecdd3;
}
.result-emoji {
    font-size: 3rem;
    margin-bottom: 0.6rem;
}
.result-label {
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    margin-bottom: 0.4rem;
}
.result-real .result-label {
    color: #065f46;
}
.result-fake .result-label {
    color: #991b1b;
}
.result-conf {
    font-size: 0.95rem;
    margin-bottom: 0.8rem;
}
.result-real .result-conf {
    color: #047857;
}
.result-fake .result-conf {
    color: #b91c1c;
}
.result-subtext {
    font-size: 0.82rem;
    color: #6b7280;
}

.conf-bar-wrap {
    background-color: #e5e7eb;
    border-radius: 99px;
    height: 8px;
    overflow: hidden;
    margin: 0.8rem auto;
    max-width: 280px;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.6s ease;
}

/* Customizing streamlit text area */
.stTextArea textarea {
    border-radius: 12px !important;
    border: 1px solid #e9d5ff !important;
    background-color: #ffffff !important;
    color: #1f2937 !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease-in-out !important;
}
.stTextArea textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15) !important;
}

/* Customizing streamlit default buttons styling */
div.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s ease-in-out !important;
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 6px -1px rgba(124, 58, 237, 0.2), 0 2px 4px -1px rgba(124, 58, 237, 0.1) !important;
}
div.stButton > button[kind="primary"]:hover {
    box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.3), 0 4px 6px -2px rgba(124, 58, 237, 0.2) !important;
    transform: translateY(-1px) !important;
}
div.stButton > button[kind="secondary"] {
    background-color: #ffffff !important;
    border: 1px solid #e9d5ff !important;
    color: #4b5563 !important;
}
div.stButton > button[kind="secondary"]:hover {
    background-color: #f5f3ff !important;
    color: #7c3aed !important;
    border-color: #c084fc !important;
}

/* About page sections styling */
.about-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.8rem;
    border: 1px solid #ede9fe;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    margin-bottom: 1.5rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.about-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.08);
    border-color: #ddd6fe;
}
.about-card h3 {
    color: #7c3aed;
    font-size: 1.15rem;
    font-weight: 700;
    margin-top: 0;
    margin-bottom: 0.8rem;
}
.about-card p {
    color: #4b5563;
    font-size: 0.88rem;
    line-height: 1.6;
    margin: 0;
}

/* Charts cards */
.chart-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid #ede9fe;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    margin-bottom: 1.5rem;
}
.chart-card h4 {
    font-size: 1rem;
    font-weight: 700;
    color: #374151;
    margin-top: 0;
    margin-bottom: 1rem;
}

/* Structure dividers */
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #e9d5ff, transparent);
    margin: 2.5rem 0;
}
.section-heading {
    font-size: 1.6rem;
    font-weight: 800;
    color: #1f2937;
    margin-bottom: 0.3rem;
}
.section-sub {
    font-size: 0.95rem;
    color: #6b7280;
    margin-bottom: 1.8rem;
}
.footer {
    text-align: center;
    padding: 1.5rem;
    border-top: 1px solid #ede9fe;
    margin-top: 4rem;
    color: #9ca3af;
    font-size: 0.85rem;
}
.footer strong {
    color: #7c3aed;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════
def render_sidebar() -> None:
    """Renders side-navigation layout containing branding logs and metrics."""
    with st.sidebar:
        st.markdown("""
        <div style='padding: 0.5rem 0.5rem 1.5rem;'>
            <div style='font-size: 1.3rem; font-weight: 800; color: #7c3aed; display: flex; align-items: center; gap: 8px; margin-bottom: 4px;'>
                🔍 TruthLens AI
            </div>
            <div style='font-size: 0.78rem; color: #6b7280;'>AI credibility scoring dashboard</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='font-size: 0.72rem; font-weight: 600; color: #a78bfa; text-transform: uppercase; letter-spacing: 0.8px; padding: 0 0.5rem; margin-bottom: 8px;'>Navigation</div>", unsafe_allow_html=True)

        nav_items = [
            ("🏠", "Home", "Landing page overview"),
            ("🔍", "Analyzer", "Scan articles"),
            ("📊", "Dashboard", "View prediction logs"),
            ("ℹ️", "About", "Project methodology"),
        ]

        for icon, label, desc in nav_items:
            button_type = "primary" if st.session_state.page == label else "secondary"
            if st.button(f"{icon}  {label}", key=f"nav_{label}", type=button_type, use_container_width=True):
                st.session_state.page = label
                st.rerun()

        st.markdown("<div class='section-divider' style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

        # Real-time session stats indicator inside the sidebar
        total = len(st.session_state.history)
        fake_c = sum(1 for h in st.session_state.history if h["label"] == "Fake")
        real_c = total - fake_c
        
        st.markdown(f"""
        <div style='background: #ffffff; border-radius: 12px; padding: 1rem; border: 1px solid #ede9fe;'>
            <div style='font-size: 0.72rem; color: #9ca3af; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 8px;'>Session Metrics</div>
            <div style='display: flex; justify-content: space-between; margin-bottom: 4px;'>
                <span style='font-size: 0.83rem; color: #4b5563;'>Total Scans</span>
                <span style='font-size: 0.83rem; font-weight: 700; color: #7c3aed;'>{total}</span>
            </div>
            <div style='display: flex; justify-content: space-between; margin-bottom: 4px;'>
                <span style='font-size: 0.83rem; color: #4b5563;'>Credible</span>
                <span style='font-size: 0.83rem; font-weight: 700; color: #10b981;'>{real_c}</span>
            </div>
            <div style='display: flex; justify-content: space-between;'>
                <span style='font-size: 0.83rem; color: #4b5563;'>Unreliable</span>
                <span style='font-size: 0.83rem; font-weight: 700; color: #ef4444;'>{fake_c}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='position: absolute; bottom: 1rem; left: 1rem; right: 1rem; font-size: 0.72rem; color: #9ca3af; text-align: center;'>TruthLens AI · Production build</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# BACKEND API CALL WRAPPER
# ══════════════════════════════════════════════════════════════════════════════
def call_predict_api(text: str) -> dict:
    """
    Submits article text to FastAPI endpoint and parses output metrics.
    
    Args:
        text: Raw news text content to classify.
        
    Returns:
        dict: Standardized prediction label ('Real' | 'Fake') and rounded confidence (0-100).
        
    Raises:
        requests.exceptions.ConnectionError: If API cannot be reached.
        requests.exceptions.Timeout: If server request times out.
        requests.exceptions.HTTPError: If server responds with failure code.
        ValueError: If parsing response returns empty/corrupted data.
    """
    if not text.strip():
        raise ValueError("Provided text is empty.")
        
    try:
        response = requests.post(
            API_URL,
            json={"text": text},
            timeout=10,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise requests.exceptions.ConnectionError("Could not establish connection to the prediction server.") from e
    except requests.exceptions.Timeout as e:
        raise requests.exceptions.Timeout("Connection timed out. Prediction server took too long to respond.") from e
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(f"HTTP classification request failed with code: {e.response.status_code}") from e
        
    data = response.json()
    if not data:
        raise ValueError("Server returned an empty classification dataset.")
        
    if "prediction" not in data or "confidence" not in data:
        raise ValueError("Response payload lacks prediction or confidence records.")
        
    label = str(data["prediction"]).strip().capitalize()
    if label not in ["Real", "Fake"]:
        label = "Real" if "real" in label.lower() else "Fake"
        
    try:
        conf = float(data["confidence"])
    except (TypeError, ValueError) as e:
        raise ValueError("Confidence value returned is not a valid floating-point number.") from e
        
    # Scale probabilities to percentage (0.0-1.0 to 0-100) if needed
    if conf <= 1.0:
        conf = conf * 100
        
    return {"label": label, "confidence": round(conf, 2)}

# Helper to generate explanation and suggestions
def get_explanation_and_recommendations(label: str, text: str, confidence: float) -> tuple[str, list[str]]:
    """Analyzes simple structural heuristics to generate explanations and recommendations."""
    is_fake = label.lower() == "fake"
    
    exclamations = text.count("!")
    caps_ratio = sum(1 for c in text if c.isupper()) / (len(text) + 1)
    has_clickbait = any(w in text.lower() for w in ["shocking", "unbelievable", "secret", "miracle", "won't believe", "exposed"])
    
    if is_fake:
        explanation = f"Our model detected linguistic signatures indicative of misinformation with a confidence of {confidence}%."
        flags = []
        if caps_ratio > 0.08:
            flags.append("Elevated uppercase letter usage commonly styled to provoke attention.")
        if exclamations > 2:
            flags.append("Frequent use of exclamation markers to heighten sensational impact.")
        if has_clickbait:
            flags.append("Stylistic trigger phrases matching standard clickbait definitions.")
        if not flags:
            flags.append("Stylistic patterns matching structural profiles of unreliable media sources.")
            
        explanation += " Key flags: " + " ".join(flags)
        
        recommendations = [
            "Check alternative media agencies (e.g., Reuters, AP) for verified primary coverages.",
            "Verify author identity and publisher registration details.",
            "Run searches on verified platforms like PolitiFact or Snopes.",
            "Avoid sharing or forwarding this content until corroborating evidence emerges."
        ]
    else:
        explanation = f"Linguistic syntax and structures align closely with factual, standard news journalism with a confidence of {confidence}%."
        signals = []
        if caps_ratio < 0.05:
            signals.append("Standard grammatical capitalization levels.")
        if exclamations == 0:
            signals.append("Neutral syntax styling omitting subjective punctuations.")
        if not has_clickbait:
            signals.append("Absence of emotional or clickbait keywords.")
            
        if signals:
            explanation += " Noted structures: " + " ".join(signals)
        else:
            explanation += " Follows general guidelines for editorial news reporting."
            
        recommendations = [
            "Support independent journalism by reading and subscribing directly to official sites.",
            "Examine the publication's date and author bio for deep editorial context.",
            "Compare reports to analyze potential framing differences between credible sources."
        ]
        
    return explanation, recommendations

# ══════════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_home() -> None:
    """Renders Landing page displaying platform overview, feature grids, and metrics."""
    # 2-column Hero Layout
    col1, col2 = st.columns([1.2, 0.8], gap="large")
    
    with col1:
        st.markdown('<div class="hero-tag">✨ AI-Powered · Natural Language Processing</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="hero-title">TruthLens AI</h1>', unsafe_allow_html=True)
        st.markdown('<div class="hero-subtitle">AI-Powered Fake News Detection and News Credibility Analysis</div>', unsafe_allow_html=True)
        st.markdown("""
        <p class="hero-desc">
            Analyze text headlines and body content in real-time. TruthLens AI leverages 
            optimized vectorization pipelines and supervised machine learning classifiers 
            to screen information and flag stylistic markers of misinformation instantly.
        </p>
        """, unsafe_allow_html=True)
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("🔍 Analyze News", type="primary", use_container_width=True, key="hero_analyze"):
                st.session_state.page = "Analyzer"
                st.rerun()
        with btn_col2:
            if st.button("📊 View Dashboard", type="secondary", use_container_width=True, key="hero_dashboard"):
                st.session_state.page = "Dashboard"
                st.rerun()
                
    with col2:
        if os.path.exists("assets/hero_image.png"):
            st.image("assets/hero_image.png", use_container_width=True)
        else:
            # Fallback graphic container
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f5f3ff, #faf5ff); border-radius: 20px; border: 1px dashed #c084fc; height: 320px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #7c3aed; padding: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                <div style="font-size: 4.5rem; margin-bottom: 1rem;">🔍</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #7c3aed;">TruthLens AI Platform</div>
                <div style="font-size: 0.85rem; color: #9ca3af; text-align: center; margin-top: 0.5rem; max-width: 200px;">Advanced Machine Learning News Credibility Verifier</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # Features Row
    st.markdown("<div class='section-heading'>Platform Capabilities</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Engineered for credibility scanning speed and accuracy</div>", unsafe_allow_html=True)

    feat_col1, feat_col2, feat_col3, feat_col4 = st.columns(4)
    features = [
        ("#f5f3ff", "🤖", "AI Detection", "Logistic Regression model trained to recognize text patterns and propaganda.", feat_col1),
        ("#ecfdf5", "⚡", "Instant Analysis", "Verifies and processes articles in under a second for real-time feedback.", feat_col2),
        ("#eff6ff", "📈", "High Accuracy", "Achieves near-perfect benchmarks on testing datasets through optimization.", feat_col3),
        ("#fffbeb", "🧠", "NLP Powered", "Uses advanced TF-IDF vectorization to capture semantic properties of text.", feat_col4),
    ]
    for bg, icon, title, desc, col in features:
        with col:
            st.markdown(f"""
            <div class="feat-card">
                <div class="feat-icon" style="background: {bg};">{icon}</div>
                <div class="feat-title">{title}</div>
                <div class="feat-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # Statistics Row
    st.markdown("<div class='section-heading'>Model Statistics</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Core metrics validated across test datasets</div>", unsafe_allow_html=True)

    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    with stat_col1:
        st.markdown("""
        <div class="stat-card" style="border-left-color: #7c3aed;">
            <div class="stat-label">Model Accuracy</div>
            <div class="stat-value" style="color: #7c3aed;">~99%</div>
            <div class="stat-sub">Validated on test datasets</div>
        </div>
        """, unsafe_allow_html=True)
    with stat_col2:
        st.markdown("""
        <div class="stat-card" style="border-left-color: #10b981;">
            <div class="stat-label">Analysis Speed</div>
            <div class="stat-value" style="color: #059669;">&lt; 1s</div>
            <div class="stat-sub">Real-time predictions</div>
        </div>
        """, unsafe_allow_html=True)
    with stat_col3:
        st.markdown("""
        <div class="stat-card" style="border-left-color: #3b82f6;">
            <div class="stat-label">Dataset Size</div>
            <div class="stat-value" style="color: #2563eb;">40k+</div>
            <div class="stat-sub">Cleaned news articles</div>
        </div>
        """, unsafe_allow_html=True)
    with stat_col4:
        st.markdown("""
        <div class="stat-card" style="border-left-color: #f59e0b;">
            <div class="stat-label">NLP Pipeline</div>
            <div class="stat-value" style="color: #d97706;">TF-IDF</div>
            <div class="stat-sub">Logistic Regression model</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="footer"><strong>TruthLens AI</strong> &nbsp;·&nbsp; Streamlit · FastAPI · Scikit-Learn · TF-IDF · Logistic Regression</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ANALYZER PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_analyzer() -> None:
    """Renders Credibility scanning inputs, prediction loading, and result panels."""
    st.markdown("<div class='section-heading'>🔍 News Article Analyzer</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Paste headline or article contents to verify classification</div>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1.3, 0.7], gap="large")

    with left_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.88rem; font-weight: 600; color: #374151; margin-bottom: 8px;'>📝 News Text Input</p>", unsafe_allow_html=True)
        
        text_input = st.text_area(
            label="Article Text Area",
            placeholder="Paste text contents or headline (minimum 20 characters recommended)...",
            height=200,
            key="analyzer_input",
            label_visibility="collapsed",
        )
        
        char_count = len(text_input.strip())
        col_c, col_b = st.columns([2, 1])
        with col_c:
            label_color = "#9ca3af" if char_count >= 20 else "#ef4444"
            st.markdown(f"<p style='font-size: 0.78rem; color: {label_color}; margin-top: 4px;'>{char_count} characters entered · Recommended: 20+</p>", unsafe_allow_html=True)
            
        analyze_btn = st.button("⚡ Run Classification", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown("""
        <div class="about-card" style="height: 100%; margin-bottom: 0;">
            <h3 style="margin-bottom: 12px; font-size: 1.05rem;">💡 Tips for Credibility Analysis</h3>
            <div style="display: flex; gap: 8px; margin-bottom: 8px; font-size: 0.83rem; color: #4b5563;">
                <span>✅</span> <span>Include headline and article body together for higher accuracy predictions.</span>
            </div>
            <div style="display: flex; gap: 8px; margin-bottom: 8px; font-size: 0.83rem; color: #4b5563;">
                <span>✅</span> <span>Avoid copy-pasting heavy HTML structures or unrelated formatting.</span>
            </div>
            <div style="display: flex; gap: 8px; margin-bottom: 8px; font-size: 0.83rem; color: #4b5563;">
                <span>⚠️</span> <span>Satire or parody news sites may trigger low credibility predictions.</span>
            </div>
            <div style="display: flex; gap: 8px; font-size: 0.83rem; color: #4b5563;">
                <span>🔍</span> <span>Cross-check flag notifications against certified facts portals.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── CLASSIFICATION RESULT OUTPUT ──
    if analyze_btn:
        cleaned_text = text_input.strip()
        if not cleaned_text:
            st.warning("⚠️ Text input is empty. Please paste article news contents to classify.")
            return
        if len(cleaned_text) < 20:
            st.warning("⚠️ Article input must contain at least 20 characters to analyze successfully.")
            return

        with st.spinner("🔄 Invoking NLP classifiers and predicting..."):
            try:
                result = call_predict_api(cleaned_text)
            except requests.exceptions.ConnectionError:
                st.error("❌ Prediction server is currently unreachable. Ensure the FastAPI backend is running.")
                return
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Prediction server took too long to analyze.")
                return
            except Exception as e:
                st.error(f"❌ Error encountered during evaluation: {e}")
                return

        label = result["label"]
        confidence = result["confidence"]
        is_fake = label.lower() == "fake"

        # Log prediction to session history
        st.session_state.history.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "preview": cleaned_text[:70] + ("..." if len(cleaned_text) > 70 else ""),
            "label": label,
            "confidence": confidence,
        })

        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        
        # Result Details Layout
        res_col1, res_col2 = st.columns([1.0, 1.0], gap="large")
        
        with res_col1:
            if not is_fake:
                st.markdown(f"""
                <div class="result-card result-real">
                    <div class="result-emoji">✅</div>
                    <div class="result-label">REAL NEWS DETECTED</div>
                    <div class="result-conf">Credibility Confidence: <strong>{confidence}%</strong></div>
                    <div class="conf-bar-wrap">
                        <div class="conf-bar-fill" style="width: {confidence}%; background-color: #10b981;"></div>
                    </div>
                    <div class="result-subtext">This article shows style patterns matching highly credible reporting.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-card result-fake">
                    <div class="result-emoji">🚨</div>
                    <div class="result-label">FAKE NEWS DETECTED</div>
                    <div class="result-conf">Misinformation Confidence: <strong>{confidence}%</strong></div>
                    <div class="conf-bar-wrap">
                        <div class="conf-bar-fill" style="width: {confidence}%; background-color: #ef4444;"></div>
                    </div>
                    <div class="result-subtext">This article shows key markers of manipulated or sensationalized news.</div>
                </div>
                """, unsafe_allow_html=True)
                
            # Gauge chart
            color = "#10b981" if not is_fake else "#ef4444"
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=confidence,
                number={"suffix": "%", "font": {"size": 24, "color": color, "family": "Inter"}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#d1d5db"},
                    "bar": {"color": color, "thickness": 0.25},
                    "bgcolor": "#f3f4f6",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 50], "color": "#f9fafb"},
                        {"range": [50, 100], "color": "#ecfdf5" if not is_fake else "#fef2f2"},
                    ],
                },
                title={"text": "Confidence Gauge", "font": {"size": 14, "color": "#6b7280", "family": "Inter"}},
            ))
            fig.update_layout(
                height=180,
                margin=dict(t=30, b=5, l=15, r=15),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with res_col2:
            explanation, recommendations = get_explanation_and_recommendations(label, cleaned_text, confidence)
            
            st.markdown(f"""
            <div class="card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 0;">
                <div>
                    <h4 style="color: #7c3aed; margin-top: 0; margin-bottom: 0.8rem; font-size: 1.1rem;">
                        🧠 AI Analysis Explanation
                    </h4>
                    <p style="font-size: 0.88rem; color: #4b5563; line-height: 1.6; margin-bottom: 1.5rem;">
                        {explanation}
                    </p>
                </div>
                <hr style="border: 0; border-top: 1px solid #f3f0ff; margin-bottom: 1.5rem;" />
                <div>
                    <h4 style="color: #7c3aed; margin-top: 0; margin-bottom: 0.8rem; font-size: 1.1rem;">
                        📋 AI Recommendations
                    </h4>
                    <ul style="padding-left: 1.2rem; margin: 0; font-size: 0.85rem; color: #4b5563; line-height: 1.6;">
                        {"".join([f'<li style="margin-bottom: 8px;">{rec}</li>' for rec in recommendations])}
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="footer"><strong>TruthLens AI</strong> &nbsp;·&nbsp; Streamlit · FastAPI · Scikit-Learn · TF-IDF · Logistic Regression</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_dashboard() -> None:
    """Renders session stats, analytical Plotly charts, and historical prediction tables."""
    st.markdown("<div class='section-heading'>📊 Analytics Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Overview of prediction outputs and patterns across this session</div>", unsafe_allow_html=True)

    history = st.session_state.history
    total = len(history)
    fake_c = sum(1 for h in history if h["label"] == "Fake")
    real_c = total - fake_c
    avg_conf = round(sum(h["confidence"] for h in history) / total, 2) if total else 0

    # Numeric KPI metrics grids
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""
        <div class="stat-card" style="border-left-color: #7c3aed;">
            <div class="stat-label">Total Analyses</div>
            <div class="stat-value" style="color: #7c3aed;">{total}</div>
            <div class="stat-sub">Predictions run in session</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="stat-card" style="border-left-color: #ef4444;">
            <div class="stat-label">Fake Detected</div>
            <div class="stat-value" style="color: #dc2626;">{fake_c}</div>
            <div class="stat-sub">{round(fake_c/total*100) if total else 0}% of analyses</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="stat-card" style="border-left-color: #10b981;">
            <div class="stat-label">Real Detected</div>
            <div class="stat-value" style="color: #16a34a;">{real_c}</div>
            <div class="stat-sub">{round(real_c/total*100) if total else 0}% of analyses</div>
        </div>
        """, unsafe_allow_html=True)
    with s4:
        st.markdown(f"""
        <div class="stat-card" style="border-left-color: #3b82f6;">
            <div class="stat-label">Avg Confidence</div>
            <div class="stat-value" style="color: #2563eb;">{avg_conf}%</div>
            <div class="stat-sub">Mean confidence score</div>
        </div>
        """, unsafe_allow_html=True)

    if total == 0:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
            <div style="font-weight: 700; font-size: 1.1rem; color: #374151;">No predictions recorded</div>
            <p style="font-size: 0.88rem; color: #9ca3af; margin-bottom: 1.5rem;">Begin by executing news checks inside the analyzer page.</p>
        </div>
        """, unsafe_allow_html=True)
        
        btn_col, _ = st.columns([1, 4])
        with btn_col:
            if st.button("🔍 Go to Analyzer", type="primary"):
                st.session_state.page = "Analyzer"
                st.rerun()
        return

    # Convert session logs into dataframe
    df = pd.DataFrame(history)
    df.index = range(1, len(df) + 1)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Grid
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="chart-card"><h4>Fake vs Real Distribution</h4>', unsafe_allow_html=True)
        pie = px.pie(
            names=["Fake", "Real"],
            values=[fake_c, real_c],
            color_discrete_sequence=["#fca5a5", "#86efac"],
            hole=0.4,
        )
        pie.update_layout(
            margin=dict(t=5, b=5, l=5, r=5),
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=11)),
            height=250,
        )
        pie.update_traces(textinfo="percent+label", textfont_size=11)
        st.plotly_chart(pie, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div class="chart-card"><h4>Confidence Scores</h4>', unsafe_allow_html=True)
        bar_colors = ["#fca5a5" if lbl == "Fake" else "#86efac" for lbl in df["label"]]
        bar = go.Figure(go.Bar(
            x=list(df.index),
            y=df["confidence"],
            marker_color=bar_colors,
            text=[f"{c}%" for c in df["confidence"]],
            textposition="outside",
            textfont=dict(size=9),
        ))
        bar.update_layout(
            xaxis=dict(title="Prediction #", showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(title="Confidence (%)", range=[0, 115], gridcolor="#f3f4f6", tickfont=dict(size=10)),
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=250,
        )
        st.plotly_chart(bar, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Line Chart: Confidence Trend
    st.markdown('<div class="chart-card"><h4>Confidence Trend Over Session</h4>', unsafe_allow_html=True)
    fig_trend = px.line(
        df,
        x=df.index,
        y="confidence",
        markers=True,
        color_discrete_sequence=["#7c3aed"]
    )
    fig_trend.update_layout(
        xaxis=dict(title="Analysis Index", showgrid=False, tickfont=dict(size=10)),
        yaxis=dict(title="Confidence (%)", range=[0, 105], gridcolor="#f3f4f6", tickfont=dict(size=10)),
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=240,
    )
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # History list logs table
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.95rem; font-weight: 700; color: #374151; margin-bottom: 0.8rem;'>📋 Session Predictions Log</p>", unsafe_allow_html=True)
    
    display_df = df[["time", "preview", "label", "confidence"]].copy()
    display_df.columns = ["Timestamp", "Text Preview", "Prediction", "Confidence (%)"]
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Confidence (%)": st.column_config.ProgressColumn(
                "Confidence (%)", min_value=0, max_value=100, format="%.2f%%"
            )
        }
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    col_c, _ = st.columns([1.5, 5])
    with col_c:
        if st.button("🗑️ Clear History", type="secondary", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    st.markdown('<div class="footer"><strong>TruthLens AI</strong> &nbsp;·&nbsp; Streamlit · FastAPI · Scikit-Learn · TF-IDF · Logistic Regression</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ABOUT PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_about() -> None:
    """Renders the detailed 9-section project portfolio as cards."""
    st.markdown("<div class='section-heading'>ℹ️ About TruthLens AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Technical overview, architecture, and machine learning components</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        # 1. Project Overview
        st.markdown("""
        <div class="about-card">
            <h3>📌 1. Project Overview</h3>
            <p>
                TruthLens AI is an advanced machine learning–based fake news classifier designed to distinguish between real and fabricated news reports. Developed as a production-grade NLP demonstration, the app serves as an interactive decision support tool for analyzing article texts and headlines to grade their credibility.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. Dataset Information
        st.markdown("""
        <div class="about-card">
            <h3>🗂️ 3. Dataset Information</h3>
            <p>
                The model was trained and validated on a balanced benchmark dataset of approximately 40,000 labeled articles containing:
                <br>• <strong>Real News:</strong> Verbatim reporting collected from primary news agencies like Reuters.
                <br>• <strong>Fake News:</strong> Propaganda, fabricated reporting, and conspiracy articles from unreliable sites.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 5. TF-IDF Vectorization
        st.markdown("""
        <div class="about-card">
            <h3>🧠 5. TF-IDF Vectorization</h3>
            <p>
                To convert text into numerical format, the pipeline utilizes **Term Frequency-Inverse Document Frequency (TF-IDF)**. TF-IDF weights words based on their unique presence within a specific document relative to the wider corpus, effectively dampening common conjunctions and amplifying highly discriminative keywords.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 7. Model Performance
        st.markdown("""
        <div class="about-card">
            <h3>📊 7. Model Performance</h3>
            <p>
                Our optimized pipeline achieves remarkable evaluation benchmarks:
                <br>• <strong>Classification Accuracy:</strong> ~99%
                <br>• <strong>Precision:</strong> ~98% (minimizes false credibility labels)
                <br>• <strong>Recall:</strong> ~98% (maximizes identification of fake reports)
                <br>• <strong>F1-Score:</strong> ~98% (balanced model performance)
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # 2. Problem Statement
        st.markdown("""
        <div class="about-card">
            <h3>🚨 2. Problem Statement</h3>
            <p>
                The uncontrolled spread of digital misinformation threatens social cohesion, financial stability, and public institutions. Automated identification of fake news at scale helps citizens parse news streams critically and supports content moderation without the latencies associated with manual fact-checking.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 4. Data Preprocessing
        st.markdown("""
        <div class="about-card">
            <h3>🛠️ 4. Data Preprocessing</h3>
            <p>
                Before modeling, raw article text undergoes an automated preprocessing pipeline:
                <br>• Tokenization and converting text to lower case.
                <br>• Removal of special characters, HTML, and punctuation.
                <br>• Stopword filtering (removing frequent but low-context words like 'is', 'the', 'and').
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 6. Logistic Regression Model
        st.markdown("""
        <div class="about-card">
            <h3>🤖 6. Logistic Regression Model</h3>
            <p>
                A <strong>Logistic Regression</strong> classifier serves as our predictive engine. Since the TF-IDF feature space is high-dimensional but linearly separable, Logistic Regression offers exceptional classification performance, robust prevention of overfitting, fast training speeds, and real-time inference support.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 8. Tech Stack
        st.markdown("""
        <div class="about-card">
            <h3>🛠️ 8. Tech Stack</h3>
            <p>
                Our modern AI architecture comprises:
                <br>• <strong>Frontend:</strong> Streamlit (Web framework) & Plotly (Analytics rendering).
                <br>• <strong>Backend:</strong> FastAPI (Asynchronous API endpoints) & Uvicorn (ASGI web server).
                <br>• <strong>ML Core:</strong> Scikit-learn (Preprocessing & Logistic Regression modeling).
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 9. Future Scope
    st.markdown("""
    <div class="about-card">
        <h3>🚀 9. Future Scope</h3>
        <p>
            Planned extensions to scale the credibility framework include:
            <br>• <strong>Web Scraping Integration:</strong> Allowing users to input a URL and scrape body contents automatically.
            <br>• <strong>Deep Learning Transformers:</strong> Integrating BERT or RoBERTa architectures for contextual text classification.
            <br>• <strong>Multilingual Frameworks:</strong> Expanding verification models to evaluate articles in Spanish, French, and German.
            <br>• <strong>Cross-Session DB:</strong> Integrating PostgreSQL or MongoDB to archive prediction histories across sessions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<div class="footer"><strong>TruthLens AI</strong> &nbsp;·&nbsp; Streamlit · FastAPI · Scikit-Learn · TF-IDF · Logistic Regression</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION ROUTER
# ══════════════════════════════════════════════════════════════════════════════
render_sidebar()

# Navigate dynamically depending on selected state page
page = st.session_state.page
if page == "Home":
    render_home()
elif page == "Analyzer":
    render_analyzer()
elif page == "Dashboard":
    render_dashboard()
elif page == "About":
    render_about()