from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
import os

openai_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=openai_key) if openai_key else None

def scout_agent(state):
    if llm is None:
        return {"influencer_list": "Mock: fitness_guru, health_coach"}
    prompt = f"Find influencer archetypes for: {state['user_request']}"
    res = llm.invoke([SystemMessage(content='You are a Scout.'), prompt])
    return {"influencer_list": res.content}

def manager_agent(state):
    if llm is None:
        return {"outreach_emails": "Mock: outreach emails generated"}
    prompt = f"Create a brief for: {state['influencer_list']}"
    res = llm.invoke([SystemMessage(content='You are a Manager.'), prompt])
    return {"outreach_emails": res.content}
