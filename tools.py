import os
from apify_client import ApifyClient
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
apify_token = st.secrets.get("APIFY_API_TOKEN") or os.getenv("APIFY_API_TOKEN")
client = ApifyClient(apify_token)

def search_influencers(niche):
    if not os.getenv("APIFY_API_TOKEN"):
        return [{"username": "test_user", "followers": 5000}]
    run_input = {"search": niche, "resultsLimit": 5}
    run = client.actor("apify/instagram-scraper").call(run_input=run_input)
    return [item for item in client.dataset(run["defaultDatasetId"]).iterate_items()]
