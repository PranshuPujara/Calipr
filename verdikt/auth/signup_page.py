import streamlit as st
from auth.supabase_auth import sign_up, AUTH_CSS, get_supabase_url

def render_signup_page():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    # Background blobs
    st.markdown("""
    <div class="auth-bg">
        <div class="auth-blob blob-1"></div>
        <div class="auth-blob blob-2"></div>
        <div class="auth-blob blob-3"></div>
    </div>
    """, unsafe_allow_html=True)

    # Top-Left Logo
    st.markdown("""
    <div class="top-left-logo">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="color: #0A0A0A; vertical-align: middle; margin-right: 8px;">
            <path d="M4 2V22" stroke="currentColor" stroke-width="3.2" stroke-linecap="square"/>
            <path d="M4 14H19" stroke="currentColor" stroke-width="3.2" stroke-linecap="square"/>
            <path d="M13.5 9V22" stroke="currentColor" stroke-width="3.2" stroke-linecap="square"/>
        </svg>
        <span style="font-size: 18px; font-weight: 800; color: #0A0A0A; letter-spacing: -0.04em; font-family: 'Inter', sans-serif; vertical-align: middle;">Calipr</span>
    </div>
    """, unsafe_allow_html=True)

    # Google button (Supabase redirected)
    supabase_url = get_supabase_url()
    st.markdown(f"""
    <button class="google-btn" onclick="window.location.href='{supabase_url}/auth/v1/authorize?provider=google&redirect_to=' + encodeURIComponent(window.location.origin + window.location.pathname)">
        <svg width="18" height="18" viewBox="0 0 18 18">
            <path fill="#4285F4" d="M16.51 8H8.98v3h4.3c-.18 1-.74 1.48-1.6 2.04v2.01h2.6a7.8 7.8 0 0 0 2.38-5.88c0-.57-.05-.66-.15-1.18z"/>
            <path fill="#34A853" d="M8.98 17c2.16 0 3.97-.72 5.3-1.94l-2.6-2a4.8 4.8 0 0 1-7.18-2.54H1.83v2.07A8 8 0 0 0 8.98 17z"/>
            <path fill="#FBBC05" d="M4.5 10.52a4.8 4.8 0 0 1 0-3.04V5.41H1.83a8 8 0 0 0 0 7.18l2.67-2.07z"/>
            <path fill="#EA4335" d="M8.98 4.18c1.17 0 2.23.4 3.06 1.2l2.3-2.3A8 8 0 0 0 1.83 5.4L4.5 7.49a4.77 4.77 0 0 1 4.48-3.3z"/>
        </svg>
        Continue with Google
    </button>
    """, unsafe_allow_html=True)

    # OR divider
    st.markdown('<div class="or-divider"><span>or</span></div>', unsafe_allow_html=True)

    # Fields
    full_name = st.text_input("Full name",     placeholder="Aum Santoki",       key="signup_name")
    email     = st.text_input("Email address", placeholder="you@company.com",    key="signup_email")
    password  = st.text_input("Password",      placeholder="Min. 8 characters",
                               type="password", key="signup_password")
    confirm   = st.text_input("Confirm password", placeholder="Repeat password",
                               type="password", key="signup_confirm")

    # Password strength visual
    if password:
        length  = len(password)
        has_num = any(c.isdigit() for c in password)
        has_sym = any(c in "!@#$%^&*" for c in password)

        if length < 8:
            strength, label, bars = 1, "Weak", ["weak","","",""]
        elif length >= 8 and not (has_num or has_sym):
            strength, label, bars = 2, "Fair", ["medium","medium","",""]
        elif length >= 8 and (has_num or has_sym):
            strength, label, bars = 3, "Good", ["strong","strong","strong",""]
        else:
            strength, label, bars = 4, "Strong", ["strong","strong","strong","strong"]

        color = {"Weak":"#EF4444","Fair":"#F59E0B","Good":"#4A90FF","Strong":"#00D4AA"}[label]
        bar_html = "".join(f'<div class="pwd-bar {b}"></div>' for b in bars)
        st.markdown(f"""
        <div class="pwd-strength">{bar_html}</div>
        <div class="helper-text" style="color:{color};margin-top:4px;">{label} password</div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Terms checkbox
    agree = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="signup_terms")

    # Sign Up button
    if st.button("Create Account", key="signup_btn", use_container_width=True, type="primary"):
        if not full_name:
            st.error("Please enter your full name.")
        elif not email or "@" not in email:
            st.error("Please enter a valid email address.")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters.")
        elif password != confirm:
            st.error("Passwords do not match.")
        elif not agree:
            st.error("Please accept the Terms of Service to continue.")
        else:
            with st.spinner("Creating your account..."):
                try:
                    response = sign_up(email, password, full_name)
                    user = response.user
                    if user:
                        st.success("✓ Account created! Check your email to verify your address, then sign in.")
                        st.session_state.auth_page = "signin"
                    else:
                        st.error("Sign up failed. This email may already be registered.")
                except Exception as e:
                    err = str(e).lower()
                    if "already" in err or "exists" in err:
                        st.error("An account with this email already exists. Please sign in.")
                    else:
                        st.error(f"Sign up failed: {e}")

    # Switch to Sign In (Only one way to toggle)
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    if st.button("Already have an account? Sign in", key="goto_signin", type="secondary", use_container_width=True):
        st.session_state.auth_page = "signin"
        st.rerun()
