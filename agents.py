from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
import os
from tools import search_influencers

openai_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=openai_key) if openai_key else None

def scout_agent(state):
    """Triggers the real-time search tool instead of mock text."""
    niche = state['user_request']

    # This now calls the LIVE function we updated above
    live_data = search_influencers(niche)

    # Format the live data into a string for the next AI agent to read
    formatted_list = "\n".join([f"- {i['username']} ({i['followers']} followers): {i['bio']}" for i in live_data])

    return {"influencer_list": formatted_list}

def manager_agent(state):
    if llm is None:
        return {"outreach_emails": "Mock: outreach emails generated"}
    prompt = f"Create a brief for: {state['influencer_list']}"
    res = llm.invoke([SystemMessage(content='You are a Manager.'), prompt])
    return {"outreach_emails": res.content}
