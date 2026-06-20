import os
from supabase import create_client, Client
import streamlit as st

def get_supabase_url() -> str:
    try:
        return st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL") or ""
    except Exception:
        return os.environ.get("SUPABASE_URL") or ""

AUTH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── GLOBAL ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.stApp {
    background: linear-gradient(180deg, #fafafa 0%, #f9f8f8 36%, #f4f1ee 45%, #f4f1ee 51%, #e2ecf6 73%, #a7cbf2 125%) fixed !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* ── HIDE ALL STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

/* ── CENTER EVERYTHING (Liquid Glass Card) ── */
.block-container {
    max-width: 440px !important;
    margin: 80px auto !important;
    padding: 40px 36px !important;
    background: rgba(255, 255, 255, 0.4) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    
    /* Rim Light Thickness */
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.45) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 20px !important;
    
    /* Soft Depth & Shine */
    box-shadow: 
      0 12px 40px rgba(26, 22, 21, 0.06),
      inset 0 0 0 1px rgba(255, 255, 255, 0.15) !important;
}

/* ── INPUTS ── */
.stTextInput > div,
.stTextInput div[data-baseweb="input"],
.stTextInput div[data-testid="stTextInputRootElement"] {
    border: none !important;
    box-shadow: none !important;
    background-color: transparent !important;
}

.stTextInput div[data-testid="stTextInputRootElement"],
.stTextInput div[data-baseweb="input"] {
    border: 1px solid #E5E7EB !important;
    background-color: #F8FAFC !important;
    border-radius: 10px !important;
    height: 48px !important;
    display: flex !important;
    align-items: center !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease !important;
}

.stTextInput div[data-testid="stTextInputRootElement"] div,
.stTextInput div[data-baseweb="input"] div {
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.stTextInput div[data-testid="stTextInputRootElement"]:focus-within,
.stTextInput div[data-baseweb="input"]:focus-within {
    border-color: #84b9ef !important;
    box-shadow: 0 0 0 3px rgba(132, 185, 239, 0.3) !important;
    background-color: #FFFFFF !important;
}

.stTextInput input {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    color: #1a1615 !important;
    width: 100% !important;
    height: 100% !important;
    padding: 0 16px !important;
}

.stTextInput input:focus {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}

.stTextInput input::placeholder {
    color: #9CA3AF !important;
    font-weight: 400 !important;
}

/* Style password visibility eye toggle button to be completely transparent with no background or border */
.stTextInput button[title="Show password text"],
.stTextInput button[title="Hide password text"],
.stTextInput div[data-baseweb="input"] button {
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #9CA3AF !important;
    padding: 0 12px !important;
    height: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
.stTextInput button[title="Show password text"]:hover,
.stTextInput button[title="Hide password text"]:hover,
.stTextInput div[data-baseweb="input"] button:hover {
    background-color: transparent !important;
    color: #4A90FF !important;
}

/* ── INPUT LABELS ── */
.stTextInput label {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #374151 !important;
    margin-bottom: 6px !important;
    letter-spacing: -0.01em !important;
}

/* ── BUTTONS ── */
/* Primary Buttons */
div.stButton > button[kind="primary"] {
    background: #0A0A0A !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    height: 48px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    letter-spacing: -0.01em !important;
    cursor: pointer !important;
}
div.stButton > button[kind="primary"]:hover {
    background: #1A1A1A !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.18) !important;
}
div.stButton > button[kind="primary"]:active {
    transform: translateY(0) !important;
    box-shadow: none !important;
}

/* Secondary/Link Buttons */
div.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #4A90FF !important;
    border: none !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    width: 100% !important;
    height: auto !important;
    padding: 0 !important;
    box-shadow: none !important;
    cursor: pointer !important;
    transition: color 0.15s !important;
}
div.stButton > button[kind="secondary"]:hover {
    color: #2563EB !important;
    text-decoration: underline !important;
    background: transparent !important;
}

/* ── TOP LEFT LOGO ── */
.top-left-logo {
    position: fixed;
    top: 24px;
    left: 24px;
    display: flex;
    align-items: center;
    z-index: 100;
    font-family: 'Inter', sans-serif !important;
}


/* ── ALERTS ── */
.stSuccess {
    background: rgba(0,212,170,0.06) !important;
    border: 1px solid rgba(0,212,170,0.25) !important;
    border-radius: 10px !important;
    color: #065f46 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}
.stError {
    background: rgba(239,68,68,0.06) !important;
    border: 1px solid rgba(239,68,68,0.25) !important;
    border-radius: 10px !important;
    color: #991b1b !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}
.stWarning {
    background: rgba(245,158,11,0.06) !important;
    border: 1px solid rgba(245,158,11,0.25) !important;
    border-radius: 10px !important;
}
.stInfo {
    background: rgba(74,144,255,0.06) !important;
    border: 1px solid rgba(74,144,255,0.25) !important;
    border-radius: 10px !important;
    color: #1e40af !important;
}

/* ── SPINNER ── */
.stSpinner > div {
    border-top-color: #4A90FF !important;
}

/* ── DIVIDER ── */
hr {
    border: none !important;
    border-top: 1px solid #F3F4F6 !important;
    margin: 24px 0 !important;
}

/* ── AUTH CARD ── */
.auth-card {
    background: rgba(255,255,255,0.90);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid #E5E7EB;
    border-radius: 20px;
    padding: 40px 36px;
    box-shadow:
        0 0 0 1px rgba(0,0,0,0.02),
        0 4px 40px rgba(0,0,0,0.08),
        0 1px 0 rgba(255,255,255,0.9) inset;
    position: relative;
    overflow: hidden;
}

/* Shimmer on card */
.auth-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg,
        transparent,
        rgba(255,255,255,0.8),
        transparent
    );
}

/* ── LOGO ── */
.auth-logo {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 28px;
}
.auth-logo-mark {
    width: 52px;
    height: 52px;
    background: #0A0A0A;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    font-weight: 900;
    color: #FFFFFF;
    font-family: 'Inter', sans-serif;
    letter-spacing: -0.06em;
    margin-bottom: 12px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}
.auth-logo-name {
    font-size: 22px;
    font-weight: 800;
    color: #0A0A0A;
    letter-spacing: -0.04em;
    font-family: 'Inter', sans-serif;
}
.auth-logo-tagline {
    font-size: 13px;
    color: #9CA3AF;
    font-family: 'Inter', sans-serif;
    margin-top: 4px;
    text-align: center;
}

/* ── HEADING ── */
.auth-heading {
    font-size: 24px;
    font-weight: 800;
    color: #0A0A0A;
    letter-spacing: -0.03em;
    font-family: 'Inter', sans-serif;
    text-align: center;
    margin-bottom: 6px;
}
.auth-subheading {
    font-size: 14px;
    color: #6B7280;
    font-family: 'Inter', sans-serif;
    text-align: center;
    margin-bottom: 28px;
    line-height: 1.5;
}

/* ── GOOGLE BUTTON ── */
.google-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    height: 48px;
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 600;
    color: #374151;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}
.google-btn:hover {
    background: #F8FAFC;
    border-color: #D1D5DB;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* ── DIVIDER WITH TEXT ── */
.or-divider {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 24px 0;
}
.or-divider::before, .or-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #E5E7EB;
}
.or-divider span {
    font-size: 12px;
    font-weight: 600;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-family: 'Inter', sans-serif;
    white-space: nowrap;
}

/* ── LINKS ── */
.auth-link {
    color: #4A90FF;
    font-weight: 600;
    text-decoration: none;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    cursor: pointer;
    transition: color 0.15s;
}
.auth-link:hover {
    color: #2563EB;
    text-decoration: underline;
}

/* ── FORM HELPER TEXT ── */
.helper-text {
    font-size: 12px;
    color: #9CA3AF;
    font-family: 'Inter', sans-serif;
    margin-top: 6px;
    line-height: 1.5;
}

/* ── SWITCH ROW (Sign in / Sign up toggle) ── */
.switch-row {
    text-align: center;
    margin-top: 24px;
    font-size: 14px;
    color: #6B7280;
    font-family: 'Inter', sans-serif;
}

/* ── FORGOT PASSWORD ROW ── */
.forgot-row {
    display: flex;
    justify-content: flex-end;
    margin-top: 4px;
    margin-bottom: 20px;
}

/* ── BACKGROUND BLOBS (cloud ambient) ── */
.auth-bg {
    position: fixed;
    inset: 0;
    overflow: hidden;
    pointer-events: none;
    z-index: 0;
}
.auth-blob {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.35;
}
.blob-1 { width:500px;height:500px;background:rgba(219,234,254,0.5);
           top:-100px;left:-100px; }
.blob-2 { width:400px;height:400px;background:rgba(241,245,249,0.6);
           top:100px;right:-80px; }
.blob-3 { width:600px;height:400px;background:rgba(248,250,252,0.5);
           bottom:0;left:30%; }

/* ── TERMS TEXT ── */
.terms-text {
    font-size: 11px;
    color: #9CA3AF;
    text-align: center;
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
    margin-top: 20px;
}
.terms-text a {
    color: #6B7280;
    text-decoration: underline;
    cursor: pointer;
}

/* ── PASSWORD STRENGTH INDICATOR ── */
.pwd-strength {
    display: flex;
    gap: 4px;
    margin-top: 8px;
}
.pwd-bar {
    flex: 1;
    height: 3px;
    border-radius: 100px;
    background: #F3F4F6;
    transition: background 0.3s;
}
.pwd-bar.weak   { background: #EF4444; }
.pwd-bar.medium { background: #F59E0B; }
.pwd-bar.strong { background: #00D4AA; }

/* ── CHECKBOX STYLING ── */
/* Checkbox Text Color under all states (including checked) */
[data-testid="stCheckbox"] [data-testid="stMarkdownContainer"] p,
[data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p,
[data-testid="stCheckbox"] label p,
[data-testid="stCheckbox"] p,
[data-testid="stCheckbox"] input:checked ~ div p,
[data-testid="stCheckbox"] input:checked ~ span,
[data-testid="stCheckbox"] input:checked ~ div,
[data-testid="stCheckbox"] [aria-checked="true"] p,
[data-testid="stCheckbox"] [aria-checked="true"] span {
    color: #374151 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
}

/* Checkbox Square Border & Background (Unchecked) */
[data-testid="stCheckbox"] label > span:first-child,
[data-testid="stCheckbox"] label > div:first-of-type,
[data-testid="stCheckbox"] div[role="checkbox"] {
    border: 1px solid #D1D5DB !important;
    border-radius: 6px !important;
    background-color: #FFFFFF !important;
    transition: all 0.2s ease !important;
}

/* Checkbox Hover */
[data-testid="stCheckbox"]:hover label > span:first-child,
[data-testid="stCheckbox"]:hover label > div:first-of-type,
[data-testid="stCheckbox"]:hover div[role="checkbox"] {
    border-color: #4A90FF !important;
    box-shadow: 0 0 0 3px rgba(74, 144, 255, 0.15) !important;
}

/* Checked Checkbox state - Target only the checkbox square (both div and span) */
[data-testid="stCheckbox"] input:checked ~ span:first-of-type,
[data-testid="stCheckbox"] input:checked ~ span:first-of-type span,
[data-testid="stCheckbox"] input:checked ~ div:first-of-type,
[data-testid="stCheckbox"] input:checked ~ div:first-of-type div,
[data-testid="stCheckbox"] input:checked + span,
[data-testid="stCheckbox"] input:checked + span span,
[data-testid="stCheckbox"] input:checked + div,
[data-testid="stCheckbox"] input:checked + div div,
[data-testid="stCheckbox"] div[role="checkbox"][aria-checked="true"],
[data-testid="stCheckbox"] div[role="checkbox"][aria-checked="true"] > div {
    background-color: #4A90FF !important;
    border-color: #4A90FF !important;
}

/* Checkmark color (make it white) and handle stroke/fill correctly for visibility */
[data-testid="stCheckbox"] svg,
[data-testid="stCheckbox"] [role="checkbox"] svg {
    color: #FFFFFF !important;
    stroke: #FFFFFF !important;
    fill: none !important;
    display: block !important;
    visibility: visible !important;
}
[data-testid="stCheckbox"] svg *,
[data-testid="stCheckbox"] [role="checkbox"] svg * {
    stroke: #FFFFFF !important;
    fill: none !important;
    stroke-width: 3px !important; /* slightly thicker for readability */
}
</style>
<script>
    if (window.location.hash && window.location.hash.indexOf('access_token=') !== -1) {
        var hash = window.location.hash.substring(1);
        var params = new URLSearchParams(hash);
        var token = params.get('access_token');
        if (token) {
            window.location.href = window.location.origin + window.location.pathname + '?access_token=' + token;
        }
    }
</script>
"""

def get_supabase_client() -> Client:
    url  = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key  = st.secrets.get("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")
    if not url or not key:
        st.error("Supabase credentials not found. Add SUPABASE_URL and SUPABASE_ANON_KEY to secrets or environment.")
        st.stop()
    return create_client(url, key)

def sign_in(email: str, password: str) -> dict:
    """Sign in with email and password. Returns user dict or raises."""
    client = get_supabase_client()
    response = client.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    return response

def sign_up(email: str, password: str, full_name: str = "") -> dict:
    """Register new user. Returns user dict or raises."""
    client = get_supabase_client()
    response = client.auth.sign_up({
        "email": email,
        "password": password,
        "options": {
            "data": {"full_name": full_name}
        }
    })
    return response

def sign_out():
    """Sign out current user and clear session."""
    try:
        client = get_supabase_client()
        client.auth.sign_out()
    except:
        pass
    for key in ["user", "access_token", "user_email", "user_name"]:
        st.session_state.pop(key, None)

def get_current_user():
    """Return current user from session_state or None."""
    return st.session_state.get("user", None)

def is_authenticated() -> bool:
    return "user" in st.session_state and st.session_state.user is not None

def reset_password(email: str):
    """Send password reset email."""
    client = get_supabase_client()
    client.auth.reset_password_email(email)

def check_oauth_callback():
    """Check query parameters for access_token from Google OAuth callback."""
    params = {}
    try:
        params = st.query_params
    except AttributeError:
        try:
            params = st.experimental_get_query_params()
        except:
            pass

    if "access_token" in params:
        access_token = params["access_token"]
        if isinstance(access_token, list):
            access_token = access_token[0]
            
        try:
            client = get_supabase_client()
            res = client.auth.get_user(access_token)
            user = res.user
            if user:
                st.session_state.user         = user
                st.session_state.access_token = access_token
                st.session_state.user_email   = user.email
                st.session_state.user_name    = user.user_metadata.get("full_name") or user.email.split("@")[0]
                
                # Clear query parameters
                try:
                    st.query_params.clear()
                except AttributeError:
                    try:
                        st.experimental_set_query_params()
                    except:
                        pass
                st.rerun()
        except Exception as e:
            st.error(f"Failed to authenticate with Google: {e}")
