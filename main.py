import os
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
