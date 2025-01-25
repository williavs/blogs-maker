import streamlit as st
import os
from supabase import create_client

# Configure page
st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered"
)

# Initialize Supabase client
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# Add custom CSS
st.markdown("""
<style>
    .auth-form {
        max-width: 400px;
        margin: auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .auth-title {
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None

def authenticate(email: str, password: str) -> bool:
    """Authenticate user with Supabase"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.session_state.user = response.user
        st.session_state.authenticated = True
        return True
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
        return False

def main():
    init_session_state()
    
    if st.session_state.authenticated:
        st.success("You are logged in!")
        st.markdown(f"Welcome back, {st.session_state.user.email}")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    else:
        st.markdown("<h1 class='auth-title'>🔐 Login</h1>", unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=True):
            email = st.text_input("Email", key="email")
            password = st.text_input("Password", type="password", key="password")
            
            if st.form_submit_button("Login"):
                if email and password:
                    if authenticate(email, password):
                        st.success("Login successful!")
                        st.rerun()
                else:
                    st.warning("Please enter both email and password.")

if __name__ == "__main__":
    main() 