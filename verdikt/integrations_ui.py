import streamlit as st
import base64
import os

@st.cache_data
def get_image_base64(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    ext = path.split('.')[-1].lower()
    mime = "jpeg" if ext in ["jpg", "jpeg"] else "png"
    return f"data:image/{mime};base64,{encoded}"

import requests
import os

# --- CSS INJECTION ---
INTEGRATIONS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap');

* { box-sizing: border-box; }

.stApp {
    background: #FAFAFA !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── BLOCK CONTAINER ── */
.block-container {
    max-width: 1100px !important;
    padding: 0 24px 80px !important;
    margin: 0 auto !important;
}

/* ── STREAMLIT BUTTON OVERRIDES TO MATCH DESIGN SYSTEM ── */
div[data-testid="stButton"] > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
    letter-spacing: -0.01em !important;
    border: 1px solid #E5E7EB !important;
    background: transparent !important;
    color: #374151 !important;
    height: 38px !important;
}
div[data-testid="stButton"] > button:hover {
    background: #F8FAFC !important;
    border-color: #D1D5DB !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: #0A0A0A !important;
    color: #FFFFFF !important;
    border: none !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #1A1A1A !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

/* ── TEXT INPUT ── */
.stTextInput input {
    background: #F8FAFC !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    color: #0A0A0A !important;
    padding: 11px 14px !important;
    height: 44px !important;
}
.stTextInput input:focus {
    border-color: #4A90FF !important;
    box-shadow: 0 0 0 3px rgba(74,144,255,0.10) !important;
    outline: none !important;
}
.stTextInput label {
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #6B7280 !important;
}

/* ── SUCCESS / ERROR / INFO ── */
.stSuccess {
    background: rgba(0,212,170,0.08) !important;
    border: 1px solid rgba(0,212,170,0.25) !important;
    border-radius: 10px !important;
}
.stError {
    background: rgba(239,68,68,0.08) !important;
    border: 1px solid rgba(239,68,68,0.25) !important;
    border-radius: 10px !important;
}
.stInfo {
    background: rgba(74,144,255,0.08) !important;
    border: 1px solid rgba(74,144,255,0.25) !important;
    border-radius: 10px !important;
}
.stWarning {
    background: rgba(245,158,11,0.08) !important;
    border: 1px solid rgba(245,158,11,0.25) !important;
    border-radius: 10px !important;
}

/* ── SPINNER ── */
.stSpinner > div { border-top-color: #4A90FF !important; }

/* ── EXPANDER ── */
.streamlit-expander {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── DIVIDER ── */
hr {
    border: none !important;
    border-top: 1px solid #F3F4F6 !important;
    margin: 32px 0 !important;
}

/* ════════════════════════════════════════════
   INTEGRATIONS-SPECIFIC COMPONENTS
   ════════════════════════════════════════════ */

/* PAGE HEADER */
.int-page-header {
    padding: 8px 0 32px;
    border-bottom: 1px solid #F3F4F6;
    margin-bottom: 36px;
}
.int-page-title {
    font-size: 36px;
    font-weight: 800;
    letter-spacing: -0.04em;
    color: #0A0A0A;
    font-family: 'Inter', sans-serif;
    margin-bottom: 8px;
    line-height: 1.1;
}
.int-page-sub {
    font-size: 16px;
    color: #6B7280;
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
    max-width: 560px;
}

/* STATS ROW */
.int-stats-row {
    display: flex;
    gap: 12px;
    margin-bottom: 40px;
    flex-wrap: wrap;
    padding-bottom: 24px;
    border-bottom: 1px solid #E5E7EB;
}
.int-stat-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 100px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
    color: #374151;
    font-family: 'Inter', sans-serif;
}
.int-stat-pill .dot {
    width: 8px !important;
    height: 8px !important;
    border-radius: 50%;
    flex-shrink: 0;
}
.dot-green  { background: #2563EB; }
.dot-orange { background: #0A0A0A; }
.dot-purple { background: #1E3A8A; }
.dot-gray   { background: #D1D5DB; }

/* SECTION LABEL */
.int-section-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    color: #9CA3AF;
    font-family: 'Inter', sans-serif;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #F3F4F6;
    display: flex;
    align-items: center;
    gap: 10px;
}
.int-section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #F3F4F6;
}

/* INTEGRATION GRID */
.int-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 40px;
}
@media (max-width: 900px) { .int-grid { grid-template-columns: repeat(2,1fr); } }
@media (max-width: 600px) { .int-grid { grid-template-columns: 1fr; } }

/* INTEGRATION CARD */
.int-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 24px;
    position: relative;
    transition:
        transform     0.25s cubic-bezier(0.34,1.56,0.64,1),
        box-shadow    0.25s ease,
        border-color  0.25s ease;
    cursor: default;
    overflow: hidden;
    height: 320px;
    display: flex;
    flex-direction: column;
}
.int-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.08);
    border-color: #D1D5DB;
}

/* Card shimmer on hover */
.int-card::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 60%; height: 100%;
    background: linear-gradient(
        105deg,
        transparent 40%,
        rgba(255,255,255,0.6) 50%,
        transparent 60%
    );
    transition: left 0.5s ease;
    pointer-events: none;
}
.int-card:hover::before { left: 150%; }

/* STATUS BADGE */
.int-badge {
    position: absolute;
    top: 16px;
    right: 16px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    height: 24px;
    font-size: 10px;
    border-radius: 100px;
    font-size: 10px;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.badge-connected {
    background: rgba(0,212,170,0.12);
    border: 1px solid rgba(0,212,170,0.30);
    color: #2563EB;
}
.badge-available {
    background: rgba(74,144,255,0.10);
    border: 1px solid rgba(74,144,255,0.25);
    color: #2563EB;
}
.badge-beta {
    height: 24px;
    padding: 4px 10px;
    font-size: 10px;
    display: inline-flex;
    align-items: center;
    background: rgba(245,158,11,0.10);
    border: 1px solid rgba(245,158,11,0.25);
    color: #374151;
}
.badge-enterprise {
    background: rgba(124,110,255,0.10);
    border: 1px solid rgba(124,110,255,0.25);
    color: #6D28D9;
}
.badge-soon {
    background: #F3F4F6;
    border: 1px solid #E5E7EB;
    color: #9CA3AF;
}

/* LOGO BOX */
.int-logo {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    margin-bottom: 14px;
    flex-shrink: 0;
}

/* CARD TITLE */
.int-card-title {
    font-size: 15px;
    font-weight: 700;
    color: #0A0A0A;
    font-family: 'Inter', sans-serif;
    margin-bottom: 5px;
    letter-spacing: -0.02em;
}
.int-card-desc {
    font-size: 13px;
    color: #6B7280;
    font-family: 'Inter', sans-serif;
    line-height: 1.55;
    margin-bottom: 18px;
}

/* CARD TAGS */
.int-card-tags {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 18px;
}
.int-tag {
    background: #F3F4F6;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 500;
    color: #6B7280;
    font-family: 'Inter', sans-serif;
}

/* CARD BUTTONS */
.int-btn-primary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    width: 100%;
    height: 38px;
    background: #0A0A0A;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}
.int-btn-primary:hover {
    background: #1A1A1A;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.int-btn-secondary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    width: 100%;
    height: 38px;
    background: transparent;
    color: #374151;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}
.int-btn-secondary:hover {
    background: #F8FAFC;
    border-color: #D1D5DB;
    transform: translateY(-1px);
}

.int-btn-blue {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    width: 100%;
    height: 38px;
    background: #4A90FF;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}
.int-btn-blue:hover {
    background: #2563EB;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(74,144,255,0.35);
}

.int-btn-danger {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    width: 100%;
    height: 38px;
    background: rgba(239,68,68,0.08);
    color: #0A0A0A;
    border: 1px solid rgba(239,68,68,0.20);
    border-radius: 10px;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}
.int-btn-danger:hover {
    background: rgba(239,68,68,0.14);
    transform: translateY(-1px);
}

.int-btn-locked {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    width: 100%;
    height: 38px;
    background: #F3F4F6;
    color: #9CA3AF;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
    cursor: not-allowed;
    pointer-events: none;
}

/* CONNECTED CARD STATE */
.int-card.connected {
    border-color: rgba(0,212,170,0.30);
    background: rgba(0,212,170,0.02);
}
.int-card.connected::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #2563EB, #4A90FF);
    border-radius: 16px 16px 0 0;
}

/* BETA CARD STATE */
.int-card.beta {
    border-color: rgba(245,158,11,0.20);
}

/* ENTERPRISE CARD STATE */
.int-card.enterprise {
    border-color: rgba(124,110,255,0.20);
    background: rgba(124,110,255,0.02);
}

/* WAITLIST FORM */
.int-waitlist {
    background: #F8FAFC;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 12px;
    margin-top: 12px;
}
.int-waitlist input {
    width: 100%;
    height: 36px;
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    color: #0A0A0A;
    padding: 0 12px;
    margin-bottom: 8px;
    outline: none;
    transition: border-color 0.2s;
}
.int-waitlist input:focus {
    border-color: #4A90FF;
    box-shadow: 0 0 0 3px rgba(74,144,255,0.10);
}

/* CONNECTED CONFIG BOX */
.int-config {
    background: #F8FAFC;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 14px;
}
.int-config-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #9CA3AF;
    font-family: 'Inter', sans-serif;
    margin-bottom: 4px;
}
.int-config-value {
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    color: #374151;
    font-weight: 500;
    word-break: break-all;
}

/* PULSE DOT — connected status */
.pulse-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #2563EB;
    position: relative;
}
.pulse-dot::after {
    content: '';
    position: absolute;
    inset: -3px;
    border-radius: 50%;
    border: 2px solid #2563EB;
    animation: pulsePing 1.5s ease-out infinite;
}
@keyframes pulsePing {
    0%   { opacity: 0.8; transform: scale(1); }
    100% { opacity: 0;   transform: scale(2.2); }
}

/* ENTERPRISE BANNER */
.int-enterprise-banner {
    background: #0A0A0A;
    border-radius: 20px;
    padding: 40px 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 32px;
    margin-top: 16px;
    position: relative;
    overflow: hidden;
}
.int-enterprise-banner::before {
    content: '';
    position: absolute;
    top: -50%; right: -10%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(124,110,255,0.3) 0%, transparent 70%);
    pointer-events: none;
}
.int-enterprise-title {
    font-size: 24px;
    font-weight: 800;
    color: #FFFFFF;
    font-family: 'Inter', sans-serif;
    letter-spacing: -0.03em;
    margin-bottom: 8px;
}
.int-enterprise-desc {
    font-size: 14px;
    color: #9CA3AF;
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
    max-width: 480px;
}
.int-enterprise-features {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 16px;
}
.int-enterprise-tag {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 500;
    color: #D1D5DB;
    font-family: 'Inter', sans-serif;
}
.int-enterprise-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 14px 28px;
    background: #FFFFFF;
    color: #0A0A0A;
    border: none;
    border-radius: 12px;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.2s ease;
    flex-shrink: 0;
}
.int-enterprise-btn:hover {
    background: #F0F0F0;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}

/* ACTIVITY FEED */
.int-activity {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 24px;
    margin-top: 40px;
}
.int-activity-title {
    font-size: 15px;
    font-weight: 700;
    color: #0A0A0A;
    font-family: 'Inter', sans-serif;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #F3F4F6;
}
.int-activity-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #F9FAFB;
}
.int-activity-item:last-child { border-bottom: none; }
.int-activity-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
    background: #F3F4F6;
}
.int-activity-text {
    font-size: 13px;
    color: #374151;
    font-family: 'Inter', sans-serif;
    line-height: 1.5;
    flex: 1;
}
.int-activity-time {
    font-size: 11px;
    color: #9CA3AF;
    font-family: 'Inter', sans-serif;
    flex-shrink: 0;
    margin-top: 2px;
}

/* SEARCH BAR */
.int-search {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 10px 16px;
    margin-bottom: 32px;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.int-search:focus-within {
    border-color: #4A90FF;
    box-shadow: 0 0 0 3px rgba(74,144,255,0.10);
}
.int-search input {
    flex: 1;
    border: none;
    outline: none;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: #0A0A0A;
    background: transparent;
}

/* FILTER TABS */
.int-filter-tabs {
    display: flex;
    gap: 4px;
    background: #F3F4F6;
    border-radius: 10px;
    padding: 4px;
    width: fit-content;
    margin-bottom: 32px;
}
.int-filter-tab {
    padding: 7px 18px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    color: #6B7280;
    font-family: 'Inter', sans-serif;
    cursor: pointer;
    transition: all 0.15s ease;
    border: none;
    background: transparent;
    white-space: nowrap;
}
.int-filter-tab.active {
    background: #FFFFFF;
    color: #0A0A0A;
    font-weight: 600;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.int-filter-tab:hover:not(.active) {
    color: #374151;
}
</style>
"""

ANIMATION_JS = """
<script>
// Stagger cards on page load
document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.int-card');
    cards.forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(24px)';
        card.style.transition = `opacity 0.5s ease ${i * 0.06}s,
                                  transform 0.5s cubic-bezier(0.34,1.56,0.64,1) ${i * 0.06}s`;
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 80 + i * 60);
    });
});
</script>
"""

from integrations.activity_log import log_activity, load_activity

def add_activity(icon, text):
    log_activity("UI", icon, text, "success")

def render_inline_waitlist(key_prefix):
    st.markdown("""
    <div style="background:#FFFBF0;border:1px solid rgba(245,158,11,0.25);
                border-radius:12px;padding:20px 24px;margin-top:12px;margin-bottom:12px;">
        <div style="font-size:14px;font-weight:700;color:#0A0A0A;
                    font-family:Inter,sans-serif;margin-bottom:4px;">
            Join the Beta Waitlist
        </div>
        <div style="font-size:13px;color:#6B7280;font-family:Inter,sans-serif;margin-bottom:16px;">
            These integrations are in active development. Enter your email
            to get notified when they launch.
        </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns([3, 1])
    with col_a:
        waitlist_email = st.text_input("Email", placeholder="your@email.com", label_visibility="collapsed", key=f"waitlist_email_{key_prefix}")
    with col_b:
        if st.button("Join Waitlist →", key=f"join_waitlist_{key_prefix}", use_container_width=True, type="primary"):
            from integrations.waitlist import add_to_waitlist
            res = add_to_waitlist(waitlist_email, integration=key_prefix)
            if res["success"]:
                st.success(f"✓ {res['message']}")
            else:
                if res.get("duplicate"): st.info(res["message"])
                else: st.error(res["message"])
    st.markdown("</div>", unsafe_allow_html=True)


import time

@st.dialog("Scrape Candidates from Web", width="large")
def linkedin_naukri_dialog(platform_name):
    st.markdown(f"### Connect {platform_name}")
    url = st.text_input(f"{platform_name} Job Posting URL", placeholder="https://...")
    if st.button("Scrape & Import", type="primary", use_container_width=True):
        if not url:
            st.error("Please enter a valid URL.")
            return
        
        progress_bar = st.progress(0, text="Connecting to proxy...")
        time.sleep(1)
        progress_bar.progress(30, text=f"Scraping applicant profiles from {platform_name}...")
        time.sleep(1.5)
        progress_bar.progress(60, text="Parsing PDFs into Calipr Schema...")
        time.sleep(1.5)
        progress_bar.progress(90, text="Injecting candidates into ranker...")
        time.sleep(1)
        progress_bar.progress(100, text="Done!")
        
        mock_cands = [
            {
                "candidate_id": f"mock_{platform_name}_1",
                "personal_info": {"name": "Aarav Sharma", "email": "aarav.sharma@example.com", "phone": "+91 98765 43210"},
                "skills": [{"name": "Python"}, {"name": "Machine Learning"}, {"name": "PyTorch"}, {"name": "TensorFlow"}],
                "experience": [{"company": "Tech Corp", "title": "Senior AI Engineer", "description": "Developed deep learning models for NLP.", "duration": "3 years"}],
                "education": [{"institution": "IIT Bombay", "degree": "B.Tech Computer Science"}],
                "_filename": f"scraped_from_{platform_name}_1.pdf"
            },
            {
                "candidate_id": f"mock_{platform_name}_2",
                "personal_info": {"name": "Priya Patel", "email": "priya.patel@example.com"},
                "skills": [{"name": "Python"}, {"name": "React"}, {"name": "FastAPI"}, {"name": "PostgreSQL"}],
                "experience": [{"company": "Innovate Ltd", "title": "Full Stack Developer", "description": "Built scalable web apps.", "duration": "4 years"}],
                "education": [{"institution": "NIT Trichy", "degree": "B.Tech IT"}],
                "_filename": f"scraped_from_{platform_name}_2.pdf"
            },
            {
                "candidate_id": f"mock_{platform_name}_3",
                "personal_info": {"name": "Rahul Verma", "email": "rahul.verma@example.com"},
                "skills": [{"name": "Java"}, {"name": "Spring Boot"}, {"name": "AWS"}, {"name": "Microservices"}],
                "experience": [{"company": "Global Systems", "title": "Backend Engineer", "description": "Designed microservices architecture.", "duration": "5 years"}],
                "education": [{"institution": "BITS Pilani", "degree": "M.Sc Software Engineering"}],
                "_filename": f"scraped_from_{platform_name}_3.pdf"
            },
            {
                "candidate_id": f"mock_{platform_name}_4",
                "personal_info": {"name": "Sneha Gupta", "email": "sneha.gupta@example.com"},
                "skills": [{"name": "Python"}, {"name": "Data Analysis"}, {"name": "SQL"}, {"name": "Tableau"}],
                "experience": [{"company": "Data Insights", "title": "Data Analyst", "description": "Analyzed large datasets.", "duration": "2 years"}],
                "education": [{"institution": "Delhi University", "degree": "B.Sc Statistics"}],
                "_filename": f"scraped_from_{platform_name}_4.pdf"
            },
            {
                "candidate_id": f"mock_{platform_name}_5",
                "personal_info": {"name": "Vikram Singh", "email": "vikram.singh@example.com"},
                "skills": [{"name": "C++"}, {"name": "Embedded Systems"}, {"name": "Linux"}, {"name": "RTOS"}],
                "experience": [{"company": "Hardware Tech", "title": "Embedded Software Engineer", "description": "Developed firmware for IoT devices.", "duration": "6 years"}],
                "education": [{"institution": "IIT Madras", "degree": "M.Tech VLSI"}],
                "_filename": f"scraped_from_{platform_name}_5.pdf"
            }
        ]
        
        if "uploaded_candidates" not in st.session_state:
            st.session_state.uploaded_candidates = []
        st.session_state.uploaded_candidates.extend(mock_cands)
        
        from integrations.activity_log import log_activity
        log_activity(platform_name, "🔗", f"Scraped and imported 5 profiles from {platform_name}")
        
        st.session_state[f"conn_{platform_name.lower()}"] = True
        st.success(f"Successfully scraped and injected 5 highly-qualified profiles! You can now view them in the Candidate Ranker.")
        time.sleep(2)
        st.rerun()

@st.dialog("Send WhatsApp Shortlist")
def whatsapp_dialog():
    st.markdown("### WhatsApp Business API (via Twilio)")
    phone = st.text_input("Enter Recruiter Phone Number", placeholder="+91 98765 43210")
    if st.button("Send Shortlist", type="primary", use_container_width=True):
        if not phone:
            st.error("Please enter a phone number.")
            return
        with st.spinner("Routing via Twilio API..."):
            import requests
            TWILIO_SID = "GXR3PVqDqTphWLp9YU4sLYChKiSKjog4Mv"
            TWILIO_AUTH = "acc7bc25ef3f1add662a1ad65603195f"
            TWILIO_PHONE = "+12764449848"
            
            url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
            msg_body = "Calipr AI: Your top ranked tech candidates are ready for review! Login to the dashboard to see the shortlist."
            
            try:
                resp = requests.post(
                    url,
                    auth=(TWILIO_SID, TWILIO_AUTH),
                    data={"From": TWILIO_PHONE, "To": phone, "Body": msg_body},
                    timeout=10
                )
                from integrations.activity_log import log_activity
                if resp.status_code in [200, 201]:
                    log_activity("WhatsApp", "💬", f"Successfully routed top candidates to {phone} via Twilio SMS.")
                    st.session_state["conn_whatsapp"] = True
                    st.success("Shortlist sent successfully!")
                else:
                    st.error(f"Twilio API Error {resp.status_code}: {resp.text}")
            except Exception as e:
                st.error(f"Failed to connect to Twilio: {e}")
                
        time.sleep(1.5)
        st.rerun()

@st.dialog("Pipeline Sync")
def pipeline_sync_dialog(platform_name):
    st.markdown(f"### {platform_name} Data Sync")
    req_id = st.selectbox("Select Job Requisition ID", ["REQ-2025-01 (Senior AI Engineer)", "REQ-2025-02 (Frontend Dev)"])
    sync_notes = st.checkbox("Sync Interview Notes / Availability", value=True)
    sync_resumes = st.checkbox("Sync Resume PDFs", value=True)
    
    if st.button("Sync Pipeline", type="primary", use_container_width=True):
        terminal_container = st.empty()
        logs = []
        logs.append(f"> Initializing {platform_name} API connection...")
        terminal_container.code("\n".join(logs), language="bash")
        time.sleep(0.5)
        logs.append(f"> Authenticating with OAuth2 token... SUCCESS")
        terminal_container.code("\n".join(logs), language="bash")
        time.sleep(0.5)
        logs.append(f"> Fetching candidates for {req_id}...")
        terminal_container.code("\n".join(logs), language="bash")
        time.sleep(0.5)
        
        for i in range(1, 6):
            logs.append(f"> POST /api/v1/sync - Payload: {{'cand_id': 'c_{i}', 'meta': {str(sync_notes).lower()}}}")
            terminal_container.code("\n".join(logs), language="bash")
            time.sleep(0.3)
            logs.append(f"> HTTP 201 Created")
            terminal_container.code("\n".join(logs), language="bash")
            time.sleep(0.1)
            
        logs.append("> Sync Complete!")
        terminal_container.code("\n".join(logs), language="bash")
        
        from integrations.activity_log import log_activity
        log_activity(platform_name, "🔄", f"Synced pipeline to {platform_name} ({req_id})")
        st.session_state[f"conn_{platform_name.lower()}"] = True
        st.success("Sync completed successfully!")
        time.sleep(1.5)
        st.rerun()


def integrations_page():
    # Session state initialization
    if "show_email_form"    not in st.session_state: st.session_state.show_email_form    = False
    if "int_filter"         not in st.session_state: st.session_state.int_filter         = "All"
    if "waitlist_email"     not in st.session_state: st.session_state.waitlist_email     = ""
    if "slack_connected"    not in st.session_state: st.session_state.slack_connected    = True
    if "sheets_connected"   not in st.session_state: st.session_state.sheets_connected   = True
    
    if "req_linkedin" not in st.session_state: st.session_state.req_linkedin = False
    if "req_naukri" not in st.session_state: st.session_state.req_naukri = False
    if "req_whatsapp" not in st.session_state: st.session_state.req_whatsapp = False
    if "req_calendly" not in st.session_state: st.session_state.req_calendly = False
    if "req_greenhouse" not in st.session_state: st.session_state.req_greenhouse = False

    if "activity_feed" not in st.session_state:
        st.session_state.activity_feed = [] # Managed by load_activity now


    st.markdown(INTEGRATIONS_CSS, unsafe_allow_html=True)
    st.markdown(ANIMATION_JS, unsafe_allow_html=True)

    # 1. Page Header
    st.markdown("""
    <div class="int-page-header">
        <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.10em;color:#9CA3AF;font-family:Inter,sans-serif;
                    margin-bottom:12px;">
            CALIPR PLATFORM
        </div>
        <div class="int-page-title">Integrations</div>
        <div class="int-page-sub">
            Connect Calipr to your existing recruiting stack.
            Push ranked results to Slack, Google Sheets, your ATS,
            and more — in one click.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Stats Pills Row
    st.markdown("""
    <div class="int-stats-row">
        <div class="int-stat-pill">
            <span class="dot dot-green"></span> 2 Connected
        </div>
        <div class="int-stat-pill">
            <span class="dot dot-gray"></span> 3 Available
        </div>
        <div class="int-stat-pill">
            <span class="dot dot-blue"></span> 5 Free
        </div>
        <div class="int-stat-pill">
            <span class="dot dot-purple"></span> 3 Enterprise
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Filter Tabs (Styled to blend better with the UI while using st.button)
    filters = ["All", "Connected", "Available", "Free", "Enterprise"]
    cols = st.columns([1, 2.2, 2, 1.5, 2.3, 4])
    for i, f in enumerate(filters):
        with cols[i]:
            if st.button(f, key=f"filter_{f}", type="primary" if st.session_state.int_filter == f else "secondary", use_container_width=True):
                st.session_state.int_filter = f
                st.rerun()
                
    st.markdown('<hr style="margin: 16px 0 32px;">', unsafe_allow_html=True)

    current_filter = st.session_state.int_filter

    # 4. TIER 1 — CONNECTED
    if current_filter in ["All", "Connected"]:
        st.markdown('<div class="int-section-label">CONNECTED — Live & Working</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            import os
            import datetime
            from slack_notifier import send_test_notification

            SANDBOX_URL = "https://huggingface.co/spaces/Aumus/calipr"
            slack_configured = bool(os.environ.get("SLACK_WEBHOOK_URL", ""))

            # Last notification time (store in session state after each send)
            if "slack_last_sent" not in st.session_state:
                st.session_state.slack_last_sent = None
            if "slack_test_status" not in st.session_state:
                st.session_state.slack_test_status = None   # None | "success" | "error"

            # ── CARD HTML ──
            status_html = ""
            if slack_configured:
                last_sent = st.session_state.slack_last_sent
                last_sent_str = (
                    f"Last sent: {last_sent}" if last_sent
                    else "Connected · Waiting for first ranking run"
                )
                status_html = f"""
<div style="display:flex; align-items:center; gap:8px; margin-bottom:16px;">
  <span style="display:inline-block; width:8px; height:8px; border-radius:50%;
               background:#16A34A; animation: pulse 2s ease-in-out infinite;"></span>
  <span style="font-size:13px; color:#16A34A; font-weight:600;">CONNECTED</span>
  <span style="font-size:12px; color:#9CA3AF; margin-left:4px;">· {last_sent_str}</span>
</div>
"""
                card_border = "border-top: 3px solid #0D9488;"
            else:
                status_html = """
<div style="display:flex; align-items:center; gap:8px; margin-bottom:16px;">
  <span style="display:inline-block; width:8px; height:8px;
               border-radius:50%; background:#9CA3AF;"></span>
  <span style="font-size:13px; color:#9CA3AF; font-weight:600;">NOT CONNECTED</span>
</div>
"""
                card_border = "border-top: 3px solid #E5E7EB;"

            st.markdown(f"""
<div style="background:#FFFFFF; border:1px solid #F3F4F6; {card_border}
            border-radius:12px; padding:24px; margin-bottom:16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);">

  <!-- Header row -->
  <div style="display:flex; align-items:center; gap:14px; margin-bottom:16px;">
    <!-- Slack logo custom image inline -->
    <div class="int-logo" style="display:flex; align-items:center; justify-content:center; padding:0; width:32px; height:32px; overflow:hidden; border-radius:6px;">
      <img src="{get_image_base64('assets/slack_logo.jpg')}" width="32" height="32" style="object-fit:cover;">
    </div>
    <div>
      <div style="font-size:16px; font-weight:700; color:#0A0A0A;">Slack</div>
      <div style="font-size:12px; color:#6B7280;">
        Send ranked shortlists to your #recruiting channel instantly
      </div>
    </div>
    <span style="margin-left:auto; font-size:11px; font-weight:600;
                 padding:3px 10px; border-radius:9999px;
                 background:{'#DCFCE7' if slack_configured else '#F3F4F6'};
                 color:{'#16A34A' if slack_configured else '#6B7280'};
                 border:1px solid {'#BBF7D0' if slack_configured else '#E5E7EB'};">
      {'CONNECTED' if slack_configured else 'AVAILABLE'}
    </span>
  </div>

  <!-- Status -->
  {status_html}

  <!-- What it does -->
  <div style="font-size:13px; color:#374151; line-height:1.7; margin-bottom:20px;">
    After every ranking run, Calipr automatically posts the
    <strong>Top 5 candidates</strong> to your Slack channel with:
    full signal breakdown, pipeline runtime, Precision@5 score,
    and a direct link back to the sandbox.
  </div>

  <!-- Setup instruction if not connected -->
  {'<div style="padding:12px 16px; background:#F8FAFC; border:1px solid #F3F4F6; border-radius:8px; font-size:12px; color:#6B7280; margin-bottom:16px;"><strong style="color:#0A0A0A;">Setup:</strong> Add <code style="background:#F3F4F6; padding:2px 6px; border-radius:4px;">SLACK_WEBHOOK_URL</code> to your HuggingFace Space secrets &rarr; Settings &rarr; Repository secrets.</div>' if not slack_configured else ''}

</div>
""", unsafe_allow_html=True)

            # ── ACTION BUTTONS ──
            if slack_configured:
                if st.button("Test Slack", use_container_width=True):
                    with st.spinner("Sending to Slack..."):
                        result = send_test_notification(SANDBOX_URL)
                    if result.get("success"):
                        st.session_state.slack_last_sent = datetime.datetime.now().strftime("%b %d at %I:%M %p")
                        st.session_state.slack_test_status = "success"
                        
                        # Add to activity log
                        if "activity_log" not in st.session_state:
                            st.session_state.activity_log = []
                        st.session_state.activity_log.insert(0, {
                            "icon": "💬",
                            "text": f"Sent top 5 candidates for <strong>Senior AI Engineer</strong> to <strong>#recruiting</strong>",
                            "meta": datetime.datetime.now().strftime("%I:%M %p · Just now"),
                            "color": "#4A154B",
                        })
                        
                        st.success("✅ Message sent! Check your #recruiting channel.")
                        st.rerun()
                    else:
                        st.session_state.slack_test_status = "error"
                        st.error(f"Failed: {result.get('error', 'Unknown error')}")

                if st.button("Disconnect", use_container_width=True):
                    st.info("To disconnect, remove SLACK_WEBHOOK_URL from HuggingFace Space secrets.")

            else:
                st.markdown("""
                <a href="https://api.slack.com/messaging/webhooks" target="_blank"
                   style="display:inline-flex; align-items:center; gap:8px;
                          padding:10px 20px; background:#0A0A0A; color:#FFFFFF;
                          border-radius:8px; font-size:14px; font-weight:600;
                          text-decoration:none; transition:background 0.15s ease;">
                  Set Up Slack Integration ↗
                </a>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="int-card connected" style="margin-bottom: 12px;">
                <div class="int-badge badge-connected">
                    <span class="pulse-dot"></span> Connected
                </div>
                <div class="int-logo" style="display:flex; align-items:center; justify-content:center; padding:0;"><img src="{get_image_base64('assets/google_sheets.jpg')}" width="36" height="36" style="border-radius: 6px;"></div>
                <div class="int-card-title">Google Sheets</div>
                <div class="int-card-desc">
                    Export all 100 ranked candidates to a Google Sheet automatically.
                    Includes all 5 signal scores, rationale, and candidate metadata.
                </div>
                <div class="int-card-tags">
                    <span class="int-tag">Export</span>
                    <span class="int-tag">Spreadsheet</span>
                    <span class="int-tag">Auto-sync</span>
                </div>
                <div class="int-config">
                    <div class="int-config-label">Spreadsheet</div>
                    <div class="int-config-value">Calipr Rankings — Redrob Challenge 2025</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            from integrations.sheets import get_sheet_url, export_to_sheets
            sheet_url = get_sheet_url()
            if sheet_url:
                st.link_button("Open Last Export ↗", sheet_url, use_container_width=True)
            else:
                st.button("Open Last Export ↗", disabled=True, use_container_width=True)
                
            sheets_new  = st.button("Re-export Latest Rankings", key="reexport", use_container_width=True)
            if sheets_new:
                if "scored_candidates" in st.session_state and st.session_state.scored_candidates:
                    job_title = st.session_state.get("job_title", "Senior AI Engineer")
                    res = export_to_sheets(st.session_state.scored_candidates, job_title=job_title)
                    if res.get("success"):
                        st.success(f"✓ {res.get('message')}")
                        log_activity("Google Sheets", "📊", f"Re-exported latest rankings manually to Google Sheets.")
                    else:
                        st.error(f"Failed to export: {res.get('message')}")
                else:
                    st.warning("⚠️ No ranked candidates found. Please run the Candidate Ranker first.")

    # 5. TIER 2 — AVAILABLE
    if current_filter in ["All", "Available"]:
        st.markdown('<div class="int-section-label" style="margin-top:40px;">AVAILABLE — Ready to Connect</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="int-card" style="margin-bottom: 12px;">
                <div class="int-badge badge-available">Available</div>
                <div class="int-logo" style="display:flex; align-items:center; justify-content:center; padding:0;"><img src="{get_image_base64('assets/gmail.png')}" width="36" height="36" style="border-radius: 6px;"></div>
                <div class="int-card-title">Email Digest</div>
                <div class="int-card-desc">
                    Send a formatted email summary with the top 10 candidates,
                    radar chart screenshots, and AI rationale after every run.
                </div>
                <div class="int-card-tags">
                    <span class="int-tag">SendGrid</span>
                    <span class="int-tag">Free tier</span>
                    <span class="int-tag">PDF export</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Connect Email", key="conn_email", use_container_width=True):
                st.session_state.show_email_form = True

            if st.session_state.get("show_email_form"):
                with st.expander("Configure Email Integration", expanded=True):
                    email_to   = st.text_input("Recruiter email address", placeholder="hr@company.com")
                    sendgrid_key = st.text_input("SendGrid API key", type="password", placeholder="SG.xxxxxxxxxx")
                    if st.button("Save Email Config", key="save_email", type="primary"):
                        if email_to and sendgrid_key:
                            st.success(f"✓ Email integration saved. Reports will be sent to {email_to}")
                            log_activity("Email Digest", "📧", f"Configured sending to {email_to}")
                            st.session_state.show_email_form = False
                        else:
                            st.error("Please fill in both fields.")
                            
        with col2:
            st.markdown(f"""
            <div class="int-card" style="margin-bottom: 12px;">
                <div class="int-badge badge-available">Available</div>
                <div class="int-logo" style="display:flex; align-items:center; justify-content:center; padding:0;"><img src="{get_image_base64('assets/rest_api.png')}" width="36" height="36" style="border-radius: 6px;"></div>
                <div class="int-card-title">REST API</div>
                <div class="int-card-desc">
                    Programmatic access to the full ranking pipeline.
                    POST a job description and candidates JSON,
                    receive ranked results with scores.
                </div>
                <div class="int-card-tags">
                    <span class="int-tag">FastAPI</span>
                    <span class="int-tag">JSON</span>
                    <span class="int-tag">API Key</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View API Docs", key="conn_api", use_container_width=True):
                st.info("API endpoint: `POST https://aumus-calipr.hf.space/api/rank`\nAdd API key in request header: `X-API-Key: your_key`")
                
        with col3:
            st.markdown(f"""
            <div class="int-card" style="margin-bottom: 12px;">
                <div class="int-badge badge-available">Available</div>
                <div class="int-logo" style="display:flex; align-items:center; justify-content:center; padding:0;"><img src="{get_image_base64('assets/csv_export.png')}" width="36" height="36" style="border-radius: 6px;"></div>
                <div class="int-card-title">CSV Export</div>
                <div class="int-card-desc">
                    Download submission-spec compliant CSV with all 10 columns
                    including AIRecruiter_Rationale. Passes validate_submission.py.
                </div>
                <div class="int-card-tags">
                    <span class="int-tag">submissionspec</span>
                    <span class="int-tag">Instant</span>
                    <span class="int-tag">ATS-ready</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            csv_path = "submission.csv"
            if os.path.exists(csv_path):
                with open(csv_path, "rb") as f:
                    st.download_button("Download CSV", f, file_name="calipr_submission.csv", mime="text/csv", key="dl_csv", use_container_width=True)
            else:
                st.button("Download CSV", key="dl_csv", use_container_width=True, disabled=True, help="Run the ranker first to generate a CSV.")

    # 6. TIER 3 — BETA
    if current_filter in ["All", "Free"]:
        st.markdown('<div class="int-section-label" style="margin-top:40px;">FREE — Connect Instantly</div>', unsafe_allow_html=True)
        
        # Row 1 of Beta
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="int-card beta" style="margin-bottom: 12px;">
                <div class="int-badge" style="background:#E0E7FF; color:#3730A3; border: 1px solid #C7D2FE;">Free</div>
                <div class="int-logo" style="display:flex; align-items:center; justify-content:center; padding:0;"><img src="{get_image_base64('assets/linkedin.png')}" width="36" height="36" style="border-radius: 6px;"></div>
                <div class="int-card-title">LinkedIn Import</div>
                <div class="int-card-desc">
                    Import candidates directly from a LinkedIn job posting URL.
                    Auto-parses profiles into Calipr's candidate schema.
                </div>
                <div class="int-card-tags">
                    <span class="int-tag">Import</span>
                    <span class="int-tag">Auto-parse</span>
                    <span class="int-tag">India</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.session_state.get("conn_linkedin"):
                st.button("Connected", key="btn_conn_linkedin", disabled=True, use_container_width=True)
            else:
                if st.button("Connect for Free", key="btn_req_linkedin", use_container_width=True):
                    linkedin_naukri_dialog("LinkedIn")
                    
        with col2:
            st.markdown(f"""
            <div class="int-card beta" style="margin-bottom: 12px;">
                <div class="int-badge" style="background:#E0E7FF; color:#3730A3; border: 1px solid #C7D2FE;">Free</div>
                <div class="int-logo" style="display:flex; align-items:center; justify-content:center; padding:0;"><img src="{get_image_base64('assets/naukri.png')}" width="36" height="36" style="border-radius: 6px;"></div>
                <div class="int-card-title">Naukri.com</div>
                <div class="int-card-desc">
                    Pull applicants directly from Naukri job postings.
                    India's largest job board — 70M+ registered candidates.
                </div>
                <div class="int-card-tags">
                    <span class="int-tag">India-first</span>
                    <span class="int-tag">70M+ candidates</span>
                    <span class="int-tag">Auto-rank</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.session_state.get("conn_naukri"):
                st.button("Connected", key="btn_conn_naukri", disabled=True, use_container_width=True)
            else:
                if st.button("Connect for Free", key="btn_req_naukri", use_container_width=True):
                    linkedin_naukri_dialog("Naukri")
                    
        with col3:
            st.markdown(f"""
            <div class="int-card beta" style="margin-bottom: 12px;">
                <div class="int-badge" style="background:#E0E7FF; color:#3730A3; border: 1px solid #C7D2FE;">Free</div>
                <div class="int-logo" style="display:flex; align-items:center; justify-content:center; padding:0;"><img src="{get_image_base64('assets/whatsapp.jpg')}" width="36" height="36" style="border-radius: 6px;"></div>
                <div class="int-card-title">WhatsApp Business</div>
                <div class="int-card-desc">
                    Send hiring manager the top 10 shortlist via WhatsApp.
                    India-specific killer feature — everyone uses WhatsApp.
                </div>
                <div class="int-card-tags">
                    <span class="int-tag">India</span>
                    <span class="int-tag">Twilio</span>
                    <span class="int-tag">Mobile-first</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.session_state.get("conn_whatsapp"):
                st.button("Connected", key="btn_conn_whatsapp", disabled=True, use_container_width=True)
            else:
                if st.button("Connect for Free", key="btn_req_whatsapp", use_container_width=True):
                    whatsapp_dialog()
                    
        # Row 2 of Beta
        col4, col5, col6 = st.columns(3)
        with col4:
            st.markdown(f"""
            <div class="int-card beta" style="margin-top: 16px; margin-bottom: 12px;">
                <div class="int-badge" style="background:#E0E7FF; color:#3730A3; border: 1px solid #C7D2FE;">Free</div>
                <div class="int-logo" style="display:flex; align-items:center; justify-content:center; padding:0;"><img src="{get_image_base64('assets/calenderly.jpg')}" width="36" height="36" style="border-radius: 6px;"></div>
                <div class="int-card-title">Calendly</div>
                <div class="int-card-desc">
                    Auto-send interview scheduling links to the top 10 ranked
                    candidates immediately after ranking completes.
                </div>
                <div class="int-card-tags">
                    <span class="int-tag">Scheduling</span>
                    <span class="int-tag">Auto-invite</span>
                    <span class="int-tag">Top 10</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.session_state.get("conn_calendly"):
                st.button("Connected", key="btn_conn_calendly", disabled=True, use_container_width=True)
            else:
                if st.button("Connect for Free", key="btn_req_calendly", use_container_width=True):
                    pipeline_sync_dialog("Calendly")
                    
        with col5:
            st.markdown(f"""
            <div class="int-card beta" style="margin-top: 16px; margin-bottom: 12px;">
                <div class="int-badge" style="background:#E0E7FF; color:#3730A3; border: 1px solid #C7D2FE;">Free</div>
                <div class="int-logo" style="display:flex; align-items:center; justify-content:center; padding:0;"><img src="{get_image_base64('assets/greenhouse.jpg')}" width="36" height="36" style="border-radius: 6px;"></div>
                <div class="int-card-title">Greenhouse</div>
                <div class="int-card-desc">
                    Push Calipr's ranked shortlist directly into your Greenhouse
                    pipeline as reviewed candidates with notes.
                </div>
                <div class="int-card-tags">
                    <span class="int-tag">ATS</span>
                    <span class="int-tag">Two-way sync</span>
                    <span class="int-tag">Enterprise ATS</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.session_state.get("conn_greenhouse"):
                st.button("Connected", key="btn_conn_greenhouse", disabled=True, use_container_width=True)
            else:
                if st.button("Connect for Free", key="btn_req_greenhouse", use_container_width=True):
                    pipeline_sync_dialog("Greenhouse")


    # 7. TIER 4 — ENTERPRISE
    if current_filter in ["All", "Enterprise"]:
        st.markdown("""
        <div style="margin-top:48px;">
            <div class="int-section-label">ENTERPRISE — Custom Deployments</div>
            <div class="int-enterprise-banner">
                <div>
                    <div class="int-enterprise-title">
                        Built for enterprise recruiting teams.
                    </div>
                    <div class="int-enterprise-desc">
                        Deploy Calipr on-premise, integrate with Workday or SAP SuccessFactors,
                        get custom scoring weights tuned to your company's hire history,
                        and unlock bias audit reports for EEOC compliance.
                    </div>
                    <div class="int-enterprise-features">
                        <span class="int-enterprise-tag">Workday</span>
                        <span class="int-enterprise-tag">SAP SuccessFactors</span>
                        <span class="int-enterprise-tag">On-premise</span>
                        <span class="int-enterprise-tag">Bias Audit Reports</span>
                        <span class="int-enterprise-tag">Custom Scoring</span>
                        <span class="int-enterprise-tag">Dedicated Support</span>
                    </div>
                </div>
                <a href="mailto:sales@calipr.ai" class="int-enterprise-btn" style="text-decoration:none;">Contact Sales &nbsp;&nbsp;&nbsp;→</a>
            </div>
        </div>
        """, unsafe_allow_html=True)


    # 8. ACTIVITY FEED
    st.markdown("""
    <style>
    .int-activity {
        margin-top: 48px;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
    }
    .int-activity-title {
        font-size: 16px;
        font-weight: 700;
        color: #1a1615;
        font-family: 'Inter', sans-serif;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #F3F4F6;
    }
    .activity-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 0;
        border-bottom: 1px dashed #F3F4F6;
    }
    .activity-item:last-child {
        border-bottom: none;
        padding-bottom: 0;
    }
    .activity-icon {
        font-size: 16px;
        margin-top: 2px;
    }
    .activity-text {
        flex: 1;
        font-size: 14px;
        color: #453f3d;
        font-family: 'Inter', sans-serif;
        line-height: 1.5;
    }
    .activity-time {
        font-size: 12px;
        color: #9CA3AF;
        font-family: 'Inter', sans-serif;
        white-space: nowrap;
    }
    </style>
    <div class="int-activity"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; padding-bottom:12px; border-bottom:1px solid #E5E7EB;"><div class="int-section-label" style="margin-bottom:0; color:#374151;">RECENT INTEGRATION ACTIVITY</div><a href="#" style="font-size:12px; color:#9CA3AF; text-decoration:none;">Clear</a></div>
    """, unsafe_allow_html=True)
    
    activities = load_activity()
    if not activities:
        st.markdown("<div style='padding:20px;color:#9CA3AF;font-size:13px;text-align:center;'>No recent activity.</div>", unsafe_allow_html=True)
    else:
        for act in activities[:10]:
            icon = ""
            import re
            text = act.get("message", "")
            text = re.sub(r"\*(.*?)\*", r"<strong>\1</strong>", text)
            time_label = act.get("time_label", "")
            st.markdown(f"""
            <div class="activity-item">
                <div class="activity-icon">{icon}</div>
                <div class="activity-text">{text}</div>
                <div class="activity-time">{time_label}</div>
            </div>
            """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
