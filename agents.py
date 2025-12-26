from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
import os
import streamlit as st

# For local development, use .env; for Streamlit Cloud, use st.secrets
openai_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
apify_token = st.secrets.get("APIFY_API_TOKEN") or os.getenv("APIFY_API_TOKEN")

llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=openai_key)

def scout_agent(state):
    prompt = f"Find influencer archetypes for: {state['user_request']}"
    res = llm.invoke([SystemMessage(content='You are a Scout.'), prompt])
    return {"influencer_list": res.content}

def manager_agent(state):
    prompt = f"Create a brief for: {state['influencer_list']}"
    res = llm.invoke([SystemMessage(content='You are a Manager.'), prompt])
    return {"outreach_emails": res.content}
