import streamlit as st
import pandas as pd
from main import app # Your LangGraph workflow

# 1. Page Configuration
st.set_page_config(page_title="AI Agency - Secure Portal", page_icon="🔐", layout="wide")

# 2. Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 3. Simple Authentication Function
def check_login():
    """Validates user credentials."""
    # Replace these with your desired credentials
    VALID_USER = "admin"
    VALID_PASS = "hypefy123"

    if st.session_state["username"] == VALID_USER and st.session_state["password"] == VALID_PASS:
        st.session_state.logged_in = True
        # Clear sensitive inputs from session state
        del st.session_state["password"]
    else:
        st.error("❌ Invalid username or password")

# 4. Login Screen UI
if not st.session_state.logged_in:
    # Centering the login form using columns
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.title("🔐 AI Agency Login")
        with st.form("login_form"):
            st.text_input("Username", key="username", placeholder="Enter your username")
            st.text_input("Password", key="password", type="password", placeholder="Enter your password")
            st.form_submit_button("Login", on_click=check_login)
    st.stop() # Prevents any code below from running until logged in

# 5. Main Dashboard Content (Only visible after login)
st.sidebar.title("Settings")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🚀 AI Influencer Agency Dashboard")
query = st.text_input("What are you looking for?", placeholder="e.g., Denver Fitness Influencers")

if st.button("Start AI Scout") and query:
    with st.spinner("Agents are working..."):
        inputs = {"user_request": query}
        col1, col2 = st.columns(2)

        # Stream the results
        for output in app.stream(inputs):
            for key, value in output.items():
                if key == "scout":
                    with col1:
                        st.subheader("🕵️ Talent Scout Results")
                        st.write(value["influencer_list"])
                        # Store for CSV export
                        st.session_state["last_scout"] = value["influencer_list"]
                elif key == "manager":
                    with col2:
                        st.subheader("✉️ Campaign Manager Brief")
                        st.write(value["outreach_emails"])

    # 6. Professional CSV Export Feature
    if "last_scout" in st.session_state:
        df = pd.DataFrame({"Research Results": [st.session_state["last_scout"]]})
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name='influencer_research.csv',
            mime='text/csv',
        )