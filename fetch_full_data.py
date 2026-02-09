"""
File Purpose: Fetch the complete Joshua Project people groups dataset.
Primary Functions:
- Fetches all people group records (up to 20k) from the API.
- Saves the data to a local JSON file.
- Provides basic stats on the downloaded data.
Inputs:
- API Key (hardcoded: 143a3df23d27)
Outputs:
- joshua_project_full_dump.json
"""

import requests
import json
import os
import time

API_KEY = "143a3df23d27"
BASE_URL = "https://api.joshuaproject.net/v1/people_groups.json"
OUTPUT_FILE = "joshua_project_full_dump.json"

def fetch_full_dataset():
    # Based on our check, the total count is ~16k, so 20000 covers it.
    limit = 20000
    url = f"{BASE_URL}?api_key={API_KEY}&limit={limit}"
    
    print(f"Fetching full dataset from {BASE_URL}...")
    print(f"Limit set to: {limit}")
    
    start_time = time.time()
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Parse JSON
        data = response.json()
        duration = time.time() - start_time
        
        count = len(data)
        print(f"\nSuccess! Downloaded {count} records in {duration:.2f} seconds.")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return None

def save_data(data, filepath):
    print(f"Saving data to {filepath}...")
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"Saved {size_mb:.2f} MB to {filepath}")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    data = fetch_full_dataset()
    if data:
        save_data(data, OUTPUT_FILE)
