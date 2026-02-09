"""
File Purpose: Fetch and analyze Joshua Project API data.
Primary Functions:
- Fetch data from API.
- Analyze structure and quality indicators.
- Compare with local CSV data.
Inputs:
- API Key (hardcoded for this script)
- joshua-project/AllPeoplesInCountry.csv
Outputs:
- api_data_sample.json
- Console output with analysis
"""

import requests
import pandas as pd
import json
import os

API_KEY = "143a3df23d27"
BASE_URL = "https://api.joshuaproject.net/v1/people_groups.json"
# Use absolute path or relative to script execution
CSV_PATH = "AllPeoplesInCountry.csv"
OUTPUT_JSON = "api_data_sample.json"

def fetch_data(limit=50):
    url = f"{BASE_URL}?api_key={API_KEY}&limit={limit}"
    print(f"Fetching data from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def analyze_structure(data):
    if not data or not isinstance(data, list):
        print("Invalid data format.")
        return

    print(f"\nFetched {len(data)} records.")
    first_record = data[0]
    print("\nKeys in first record:")
    print(list(first_record.keys()))

    # Check for quality indicators
    quality_keywords = ['source', 'date', 'updated', 'precision', 'status']
    print("\nPotential Quality Indicators found in keys:")
    found_quality = [k for k in first_record.keys() if any(q in k.lower() for q in quality_keywords)]
    for k in found_quality:
        print(f"  - {k}: {first_record[k]}")

def compare_with_csv(api_data, csv_path):
    if not os.path.exists(csv_path):
        print(f"\nCSV file {csv_path} not found. Skipping comparison.")
        return

    print(f"\nLoading CSV from {csv_path}...")
    try:
        # Skip first 2 lines as per previous analysis script
        df = pd.read_csv(csv_path, skiprows=2)
        print(f"Loaded {len(df)} rows from CSV.")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Clean columns just in case
    df.columns = df.columns.str.strip()

    print("\nComparing API sample with CSV data (matching on PeopleID3)...")
    
    matches = 0
    mismatches = 0
    
    # Prepare CSV data for matching
    if 'PeopleID3' not in df.columns:
        print("PeopleID3 column missing in CSV.")
        return
        
    # Create a string column for PeopleID3 to handle float/int discrepancies
    # Handle NaN values and convert float (e.g. 10208.0) to int (10208) then string
    df_clean = df.dropna(subset=['PeopleID3']).copy()
    df_clean['PeopleID3_str'] = df_clean['PeopleID3'].astype(int).astype(str).str.strip()

    for record in api_data:
        # API PeopleID3 might be int or str
        pid_api = record.get("PeopleID3")
        pid_api_str = str(pid_api).strip()
        
        # Find in DF
        match = df_clean[df_clean['PeopleID3_str'] == pid_api_str]
        
        if not match.empty:
            matches += 1
            csv_row = match.iloc[0]
            # Compare a few fields
            api_name = record.get("PeopNameInCountry")
            csv_name = csv_row.get("PeopNameInCountry")
            
            api_pop = record.get("Population")
            csv_pop = csv_row.get("Population")
            
            if matches <= 5: # Print first 5 matches details
                print(f"Match found for PeopleID3 {pid_api}:")
                print(f"  Name - API: {api_name}, CSV: {csv_name}")
                print(f"  Pop  - API: {api_pop}, CSV: {csv_pop}")
        else:
            mismatches += 1
            if mismatches <= 5:
                 print(f"No match in CSV for PeopleID3 {pid_api} (Name: {record.get('PeopNameInCountry')})")

    print(f"\nTotal Matches: {matches}")
    print(f"Total Mismatches (in sample): {mismatches}")

def main():
    data = fetch_data(limit=50)
    if data:
        analyze_structure(data)
        compare_with_csv(data, CSV_PATH)
        
        print(f"\nSaving fetched data to {OUTPUT_JSON}...")
        with open(OUTPUT_JSON, 'w') as f:
            json.dump(data, f, indent=2)
        print("Done.")

if __name__ == "__main__":
    main()
