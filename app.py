import streamlit as st
import pandas as pd
from main import graph  # Import the LangGraph workflow you built

# Page Config
st.set_page_config(page_title="AI Influencer Scout", page_icon="🤖", layout="wide")

# Sidebar for API Status
with st.sidebar:
    st.title("Settings")
    st.info("Ensure your .env file has valid OpenAI and Apify keys.")
    if st.button("Reset Session"):
        st.rerun()

# Main UI
st.title("🚀 AI Influencer Agency Dashboard")
st.markdown("Use the power of autonomous agents to find and pitch creators in seconds.")

# User Input
query = st.text_input("What are you looking for?", placeholder="e.g., Denver Fitness Influencers")

if st.button("Start AI Scout") and query:
    with st.spinner("Agents are working..."):
        # Run the LangGraph workflow
        inputs = {"user_request": query}

        # Create columns for the output
        col1, col2 = st.columns(2)

        influencer_list = ""
        outreach_emails = ""

        # Stream the results
        for output in graph.stream(inputs):
            for key, value in output.items():
                if key == "scout":
                    influencer_list = value["influencer_list"]
                    with col1:
                        st.subheader("🕵️ Talent Scout Results")
                        st.write(influencer_list)
                elif key == "manager":
                    outreach_emails = value["outreach_emails"]
                    with col2:
                        st.subheader("✉️ Campaign Manager Brief")
                        st.write(outreach_emails)

        # After the agents finish, convert the results into a DataFrame
        # Note: This assumes your agent output is a list or can be parsed into one
        data = {"Influencer": [influencer_list]}
        df = pd.DataFrame(data)

        # Add a download button for the CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Influencer List as CSV",
            data=csv,
            file_name='influencer_results.csv',
            mime='text/csv',
        )

    st.success("Campaign generation complete!")