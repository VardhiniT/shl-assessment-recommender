import requests
import json
import os

# SHL catalog JSON endpoint
CATALOG_URL = "https://tcp-us-prod-rnd.shl.com/voiceRater/shl-ai-hiring/shl_product_catalog.json"


def fetch_shl_catalog():

    print("Fetching SHL catalog...")

    # Send GET request
    response = requests.get(CATALOG_URL)

    # Check request success
    if response.status_code != 200:
        print("Failed to fetch catalog")
        return

    # Convert response to Python object
    data = json.loads(response.text, strict=False)

    print(f"Fetched {len(data)} assessments")

    # Create data folder if not exists
    os.makedirs("data", exist_ok=True)

    # Save catalog locally
    with open("data/assessments.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Catalog saved successfully!")


if __name__ == "__main__":
    fetch_shl_catalog()
