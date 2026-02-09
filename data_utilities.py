"""
Joshua Project Data Utilities
Easy loading functions for different use cases.

Usage examples:

    # For visualizations (enriched data)
    >>> from data_utilities import load_enriched
    >>> data = load_enriched()
    >>> unreached = [p for p in data if p['LeastReached'] == 'Y']

    # For analysis (pandas)
    >>> from data_utilities import load_parquet
    >>> import pandas as pd
    >>> df = pd.read_parquet(load_parquet('enriched'))

    # For specific queries
    >>> from data_utilities import get_by_country
    >>> india_peoples = get_by_country('IN')
"""

import json
import os
from pathlib import Path

# Dataset file paths
DATASET_DIR = Path(__file__).parent

FILES = {
    'people_groups': DATASET_DIR / 'joshua_project_full_dump.json',
    'countries': DATASET_DIR / 'joshua_project_countries.json',
    'languages': DATASET_DIR / 'joshua_project_languages.json',
    'totals': DATASET_DIR / 'joshua_project_totals.json',
    'enriched': DATASET_DIR / 'joshua_project_enriched.json',
    'unreached': DATASET_DIR / 'joshua_project_unreached.json',
    'enriched_parquet': DATASET_DIR / 'joshua_project_enriched.parquet',
    'unreached_parquet': DATASET_DIR / 'joshua_project_unreached.parquet',
}

def load_json(dataset_name):
    """
    Load a JSON dataset by name.

    Args:
        dataset_name: One of 'people_groups', 'countries', 'languages',
                     'totals', 'enriched', 'unreached'

    Returns:
        Parsed JSON data (list or dict)
    """
    if dataset_name not in FILES:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    filepath = FILES[dataset_name]

    if not filepath.exists():
        raise FileNotFoundError(f"Dataset not found: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_normalized():
    """
    Load all normalized datasets.

    Returns:
        dict with keys: people_groups, countries, languages, totals
    """
    return {
        'people_groups': load_json('people_groups'),
        'countries': load_json('countries'),
        'languages': load_json('languages'),
        'totals': load_json('totals')
    }

def load_enriched():
    """
    Load the enriched dataset (people groups with embedded country/language data).

    Returns:
        list of enriched people group records
    """
    return load_json('enriched')

def load_unreached():
    """
    Load only unreached people groups (LeastReached == 'Y').

    Returns:
        list of unreached people group records (enriched format)
    """
    return load_json('unreached')

def load_parquet(dataset_name='enriched'):
    """
    Get the path to a Parquet file for loading with pandas/polars.

    Args:
        dataset_name: 'enriched' or 'unreached'

    Returns:
        Path object to the Parquet file

    Example:
        >>> import pandas as pd
        >>> df = pd.read_parquet(load_parquet('enriched'))
    """
    parquet_key = f'{dataset_name}_parquet'

    if parquet_key not in FILES:
        raise ValueError(f"Unknown parquet dataset: {dataset_name}")

    filepath = FILES[parquet_key]

    if not filepath.exists():
        raise FileNotFoundError(f"Parquet file not found: {filepath}")

    return filepath

def get_by_country(country_code, enriched=True):
    """
    Get all people groups in a specific country.

    Args:
        country_code: 3-letter country code (ROG3), e.g., 'IN' for India
        enriched: If True, use enriched dataset; if False, use normalized

    Returns:
        list of people group records for that country
    """
    dataset = load_enriched() if enriched else load_json('people_groups')
    return [p for p in dataset if p.get('ROG3') == country_code]

def get_by_language(language_code, enriched=True):
    """
    Get all people groups speaking a specific language.

    Args:
        language_code: 3-letter language code (ROL3), e.g., 'hin' for Hindi
        enriched: If True, use enriched dataset; if False, use normalized

    Returns:
        list of people group records speaking that language
    """
    dataset = load_enriched() if enriched else load_json('people_groups')
    return [p for p in dataset if p.get('ROL3') == language_code]

def get_by_religion(religion, enriched=True):
    """
    Get all people groups with a specific primary religion.

    Args:
        religion: Religion name, e.g., 'Islam', 'Buddhism', 'Hinduism'
        enriched: If True, use enriched dataset; if False, use normalized

    Returns:
        list of people group records with that primary religion
    """
    dataset = load_enriched() if enriched else load_json('people_groups')
    return [p for p in dataset if p.get('PrimaryReligion') == religion]

def filter_unreached(data=None):
    """
    Filter dataset to only unreached people groups.

    Args:
        data: Dataset to filter (if None, loads enriched dataset)

    Returns:
        list of unreached people group records
    """
    if data is None:
        data = load_enriched()

    return [p for p in data if p.get('LeastReached') == 'Y']

def get_totals():
    """
    Get global summary statistics.

    Returns:
        dict mapping statistic ID to value
    """
    totals = load_json('totals')
    return {t['id']: t['Value'] for t in totals}

def get_country_info(country_code):
    """
    Get detailed information about a specific country.

    Args:
        country_code: 3-letter country code (ROG3)

    Returns:
        dict with country data, or None if not found
    """
    countries = load_json('countries')
    for country in countries:
        if country['ROG3'] == country_code:
            return country
    return None

def get_language_info(language_code):
    """
    Get detailed information about a specific language.

    Args:
        language_code: 3-letter language code (ROL3)

    Returns:
        dict with language data, or None if not found
    """
    languages = load_json('languages')
    for language in languages:
        if language['ROL3'] == language_code:
            return language
    return None

# Example usage and tests
if __name__ == "__main__":
    print("Joshua Project Data Utilities - Examples")
    print("=" * 60)

    # Example 1: Load enriched data
    print("\n1. Loading enriched dataset...")
    data = load_enriched()
    print(f"   Loaded {len(data):,} people groups")

    # Example 2: Get unreached peoples
    print("\n2. Filtering unreached peoples...")
    unreached = filter_unreached(data)
    print(f"   Found {len(unreached):,} unreached people groups")

    # Example 3: Get by country
    print("\n3. Getting people groups in India (ROG3='IN')...")
    india = get_by_country('IN')
    print(f"   Found {len(india):,} people groups in India")

    # Example 4: Get by language
    print("\n4. Getting Hindi-speaking people groups (ROL3='hin')...")
    hindi = get_by_language('hin')
    print(f"   Found {len(hindi):,} Hindi-speaking people groups")

    # Example 5: Get by religion
    print("\n5. Getting Buddhist people groups...")
    buddhist = get_by_religion('Buddhism')
    print(f"   Found {len(buddhist):,} Buddhist people groups")

    # Example 6: Global statistics
    print("\n6. Global statistics...")
    totals = get_totals()
    print(f"   Total countries: {totals.get('CntCountries', 'N/A')}")
    print(f"   Buddhist people groups: {totals.get('CntBuddhistPeopGroups', 'N/A')}")

    print("\n" + "=" * 60)
    print("All examples completed successfully!")
