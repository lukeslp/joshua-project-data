"""
File Purpose: Fetch all available Joshua Project datasets from the API.
Primary Functions:
- Fetches countries, languages, and totals datasets
- Saves each dataset to separate JSON files
- Generates metadata file with fetch timestamps and record counts
- Provides progress indicators and error handling

Inputs:
- API Key (via JOSHUA_PROJECT_API_KEY env var)

Outputs:
- joshua_project_countries.json
- joshua_project_languages.json
- joshua_project_totals.json
- dataset_metadata.json (metadata tracker)
"""

import requests
import json
import os
import time
from datetime import datetime

API_KEY = os.environ.get("JOSHUA_PROJECT_API_KEY", "YOUR_API_KEY_HERE")
BASE_URL = "https://api.joshuaproject.net/v1"

# Dataset definitions
DATASETS = {
    "countries": {
        "endpoint": "countries.json",
        "output_file": "joshua_project_countries.json",
        "expected_records": 238,
        "description": "Country-level statistics and demographics"
    },
    "languages": {
        "endpoint": "languages.json",
        "output_file": "joshua_project_languages.json",
        "expected_records": 7134,
        "description": "Language details and translation status"
    },
    "totals": {
        "endpoint": "totals.json",
        "output_file": "joshua_project_totals.json",
        "expected_records": 38,
        "description": "Global summary statistics"
    }
}

def fetch_dataset(dataset_name, endpoint, expected_records):
    """Fetch a dataset from the API with progress indicators."""
    # Use high limit to ensure we get all records
    limit = 20000
    url = f"{BASE_URL}/{endpoint}?api_key={API_KEY}&limit={limit}"

    print(f"\n{'='*60}")
    print(f"Fetching {dataset_name}...")
    print(f"Endpoint: {endpoint}")
    print(f"Expected records: ~{expected_records}")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        # Parse JSON
        data = response.json()
        duration = time.time() - start_time

        count = len(data)
        print(f"✅ Success! Downloaded {count} records in {duration:.2f} seconds.")

        # Warn if record count differs significantly from expected
        if abs(count - expected_records) > 10:
            print(f"⚠️  Warning: Expected ~{expected_records} records, got {count}")

        return data

    except requests.exceptions.Timeout:
        print(f"❌ Error: Request timed out after 30 seconds")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def save_dataset(data, filepath, dataset_name):
    """Save dataset to JSON file with progress indicator."""
    print(f"Saving {dataset_name} to {filepath}...")

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"✅ Saved {size_mb:.2f} MB to {filepath}")
        return True

    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return False

def create_metadata(results):
    """Create metadata file tracking all datasets."""
    metadata = {}

    # Add existing people_groups data
    if os.path.exists("joshua_project_full_dump.json"):
        try:
            with open("joshua_project_full_dump.json", 'r') as f:
                people_data = json.load(f)
            metadata["people_groups"] = {
                "file": "joshua_project_full_dump.json",
                "records": len(people_data),
                "fetched": "2025-12-21",
                "endpoint": "/v1/people_groups.json",
                "description": "People groups in countries (PGIC)"
            }
        except:
            pass

    # Add newly fetched datasets
    for dataset_name, info in results.items():
        if info["success"]:
            metadata[dataset_name] = {
                "file": DATASETS[dataset_name]["output_file"],
                "records": info["records"],
                "fetched": info["timestamp"],
                "endpoint": f"/v1/{DATASETS[dataset_name]['endpoint']}",
                "description": DATASETS[dataset_name]["description"]
            }

    # Save metadata
    metadata_file = "dataset_metadata.json"
    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Metadata saved to {metadata_file}")
        return True
    except Exception as e:
        print(f"\n❌ Error saving metadata: {e}")
        return False

def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("Joshua Project Complete Dataset Fetcher")
    print("="*60)
    print(f"Fetching {len(DATASETS)} datasets from API...")

    results = {}
    total_start = time.time()

    # Fetch each dataset
    for dataset_name, config in DATASETS.items():
        data = fetch_dataset(
            dataset_name,
            config["endpoint"],
            config["expected_records"]
        )

        if data:
            success = save_dataset(data, config["output_file"], dataset_name)
            results[dataset_name] = {
                "success": success,
                "records": len(data),
                "timestamp": datetime.now().strftime("%Y-%m-%d")
            }
        else:
            results[dataset_name] = {
                "success": False,
                "records": 0,
                "timestamp": None
            }

        # Brief pause between requests to be polite to the API
        time.sleep(0.5)

    total_duration = time.time() - total_start

    # Print summary
    print("\n" + "="*60)
    print("FETCH SUMMARY")
    print("="*60)

    success_count = sum(1 for r in results.values() if r["success"])
    total_records = sum(r["records"] for r in results.values() if r["success"])

    print(f"Datasets fetched: {success_count}/{len(DATASETS)}")
    print(f"Total records: {total_records:,}")
    print(f"Total time: {total_duration:.2f} seconds")

    for dataset_name, result in results.items():
        status = "✅" if result["success"] else "❌"
        records = f"{result['records']:,} records" if result["success"] else "FAILED"
        print(f"  {status} {dataset_name}: {records}")

    # Create metadata file
    if success_count > 0:
        create_metadata(results)

    print("\n" + "="*60)
    if success_count == len(DATASETS):
        print("🎉 All datasets fetched successfully!")
    else:
        print(f"⚠️  {len(DATASETS) - success_count} dataset(s) failed to fetch")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
