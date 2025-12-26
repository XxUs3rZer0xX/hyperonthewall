import os
from apify_client import ApifyClient

apify_token = os.getenv("APIFY_API_TOKEN")
client = ApifyClient(apify_token) if apify_token else None

def search_influencers(niche):
    if client is None:
        return [{"username": "test_user", "followers": 5000}]
    run_input = {"search": niche, "resultsLimit": 5}
    run = client.actor("apify/instagram-scraper").call(run_input=run_input)
    return [item for item in client.dataset(run["defaultDatasetId"]).iterate_items()]
