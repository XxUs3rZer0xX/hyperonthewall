import os
import zipfile

# CONFIGURATION
PROJECT_NAME = "hypefy_agent_agency"

files = {
    "requirements.txt": "langchain\nlanggraph\nlangchain-openai\npython-dotenv\napify-client\npydantic",
    ".env": "OPENAI_API_KEY=your_openai_key_here\nAPIFY_API_TOKEN=your_apify_token_here",
    "tools.py": """import os
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

def search_influencers(niche):
    if not os.getenv("APIFY_API_TOKEN"):
        return [{"username": "test_user", "followers": 5000}]
    run_input = {"search": niche, "resultsLimit": 5}
    run = client.actor("apify/instagram-scraper").call(run_input=run_input)
    return [item for item in client.dataset(run["defaultDatasetId"]).iterate_items()]
""",
    "agents.py": """from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage

llm = ChatOpenAI(model="gpt-4o", temperature=0)

def scout_agent(state):
    prompt = f"Find influencer archetypes for: {state['user_request']}"
    res = llm.invoke([SystemMessage(content='You are a Scout.'), prompt])
    return {"influencer_list": res.content}

def manager_agent(state):
    prompt = f"Create a brief for: {state['influencer_list']}"
    res = llm.invoke([SystemMessage(content='You are a Manager.'), prompt])
    return {"outreach_emails": res.content}
""",
    "main.py": """import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from agents import scout_agent, manager_agent
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    user_request: str
    influencer_list: str
    outreach_emails: str

builder = StateGraph(AgentState)
builder.add_node("scout", scout_agent)
builder.add_node("manager", manager_agent)
builder.set_entry_point("scout")
builder.add_edge("scout", "manager")
builder.add_edge("manager", END)
graph = builder.compile()

if __name__ == "__main__":
    print("AI Agency Bot Started...")
    query = input("Niche: ")
    inputs = {"user_request": query}
    for output in graph.stream(inputs):
        print(output)
"""
}

# FILE CREATION
if not os.path.exists(PROJECT_NAME):
    os.makedirs(PROJECT_NAME)

for filename, content in files.items():
    with open(os.path.join(PROJECT_NAME, filename), "w", encoding="utf-8") as f:
        f.write(content)

# ZIP CREATION
with zipfile.ZipFile(f"{PROJECT_NAME}.zip", "w") as zipf:
    for root, dirs, project_files in os.walk(PROJECT_NAME):
        for file in project_files:
            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), PROJECT_NAME))

print(f"DONE! Folder '{PROJECT_NAME}' and '{PROJECT_NAME}.zip' created.")