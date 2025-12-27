import os
import time
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

# Initialize the client with your token
# You found this in Settings > API & Integrations on Apify
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

def search_influencers(niche: str, max_retries=3, retry_delay=5):
    """Replaces mock data with a live Instagram search with retry logic."""
    for attempt in range(max_retries):
        try:
            # 1. Prepare the search parameters
            run_input = {
                "search": niche,
                "searchType": "user",
                "resultsLimit": 3  # Reduced to minimize timeouts
            }

            # 2. Run the Actor and wait for it to finish
            # 'apify/instagram-scraper' is a popular Choice
            run = client.actor("apify/instagram-scraper").call(run_input=run_input)

            # 3. Fetch results from the run's dataset
            results = []
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append({
                    "username": item.get("username"),
                    "followers": item.get("followersCount"),
                    "bio": item.get("biography")
                })

            return results
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"API call failed after {max_retries} attempts: {e}. Falling back to mock data.")
                # Fallback to mock data if API fails
                return [{"username": "test_user", "followers": 5000, "bio": "Mock bio"}]
