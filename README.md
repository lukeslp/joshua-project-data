# Joshua Project Data

## Overview
This directory contains **complete datasets** from the Joshua Project, fetched directly from their API v1. The Joshua Project is a research initiative providing demographic and religious information about people groups worldwide, serving as the primary source of truth for visualizations regarding global access to the Gospel, language groups, and missiological statistics.

## Complete Dataset Inventory

This repository now contains **all 4 available datasets** from the Joshua Project API:

### 1. People Groups (PGIC - People Groups in Countries)
- **File**: `joshua_project_full_dump.json`
- **Records**: 16,382
- **Size**: 129 MB
- **Fetched**: Dec 21, 2025
- **Endpoint**: `/v1/people_groups.json`
- **Description**: Detailed demographic and religious data for people groups within specific countries
- **Key ID**: `PeopleID3` (unique identifier for a people group within a country)

### 2. Countries
- **File**: `joshua_project_countries.json`
- **Records**: 238
- **Size**: 0.28 MB
- **Fetched**: Dec 23, 2025
- **Endpoint**: `/v1/countries.json`
- **Description**: Country-level statistics including religious composition, people group counts, and least-reached status
- **Key ID**: `ROG3` (three-letter country code)

### 3. Languages
- **File**: `joshua_project_languages.json`
- **Records**: 7,134
- **Size**: 4.81 MB
- **Fetched**: Dec 23, 2025
- **Endpoint**: `/v1/languages.json`
- **Description**: Language details including Bible translation status, audio recordings, and Jesus Film availability
- **Key ID**: `ROL3` (three-letter language code)

### 4. Summary Statistics
- **File**: `joshua_project_totals.json`
- **Records**: 38
- **Size**: < 0.01 MB
- **Fetched**: Dec 23, 2025
- **Endpoint**: `/v1/totals.json`
- **Description**: Global aggregate statistics (e.g., count of Buddhist people groups, total unreached populations, etc.)

## Metadata Tracker
- **`dataset_metadata.json`**: Tracks fetch dates, record counts, and file locations for all datasets

## Scripts

### Fetch All Datasets (Recommended)
- **`fetch_all_datasets.py`**: Unified script to fetch **all 3 missing datasets** (countries, languages, totals)
  - Usage: `python3 fetch_all_datasets.py`
  - Features: Progress indicators, error handling, automatic metadata generation
  - Duration: ~3-5 seconds for all datasets

### Fetch People Groups Only
- **`fetch_full_data.py`**: Legacy script to fetch only the people groups dataset
  - Usage: `python3 fetch_full_data.py`
  - Note: Use `fetch_all_datasets.py` for a complete refresh of all data

## Dataset Relationships

The four datasets are interconnected through shared identifiers:

- **People Groups** reference **Countries** via `ROG3` and **Languages** via `ROL3`
- **Countries** aggregate data from all people groups within their borders
- **Languages** show which people groups speak each language
- **Totals** provide global summary statistics derived from the people groups dataset

**Example**: A person searching for unreached people groups speaking Hindi (`ROL3: hin`) in India (`ROG3: IN`) would:
1. Query `languages.json` for Hindi language details
2. Query `countries.json` for India's overall statistics
3. Filter `people_groups.json` where `ROG3 = "IN"` AND `ROL3 = "hin"`
4. Reference `totals.json` for global context

## Archive

The `archive/` directory preserves legacy data for reference:

- **CSV Extracts** (circa 2016): Outdated snapshots, replaced by current JSON datasets
  - `AllPeoplesInCountry.csv` - Old people groups listing
  - `AllCountriesListing.csv` - Old countries data
  - `AllLanguageListing.csv` - Old languages data
  - `UnreachedPeoplesByCountry.csv` - Subset of unreached peoples
- **CPPI Data** (`jp-cppi-cross-reference-csv.zip`): Church Planting Progress Indicators
- **Harvest Field Data** (`jpharvfielddataonly.zip`): Microsoft Access databases (.accdb, .mdb)
- **Analysis Reports**: Preliminary data summaries (`joshua_data_summary.md`)

**Note**: The JSON datasets from the API are the current source of truth. CSV files are retained for historical reference only.

## Data Notes

### Important Concepts
- **People Group Definition**: A "People Group" is defined primarily by socio-linguistic barriers to the spread of the Gospel, not necessarily by political or strict genetic boundaries.
- **Population Data**: All population figures are estimates and should be treated as approximations. The API data is more current than archived CSVs.
- **Least Reached**: People groups with less than 2% evangelical Christian population and less than 5% Christian adherents.
- **Joshua Project Scale (JPScale)**: 1-5 scale measuring gospel access and church establishment (1 = least reached, 5 = most reached)

### Data Freshness
- **Current API Data**: Dec 21-23, 2025
- **Archive CSV Data**: Circa 2016 (outdated)
- **Update Frequency**: Run `fetch_all_datasets.py` to refresh all datasets with latest API data

### API Access
- **Base URL**: `https://api.joshuaproject.net/v1/`
- **API Key**: Required for all requests (currently hardcoded in scripts)
- **Documentation**: https://api.joshuaproject.net/
- **Rate Limiting**: Be respectful; add delays between bulk requests

## Enriched Datasets (For Visualization & Analysis)

In addition to the normalized datasets, **enriched versions** are available that combine people groups with country and language data:

### Full Enriched Dataset
- **`joshua_project_enriched.json`** (139 MB) - All people groups with embedded country/language data
- **`joshua_project_enriched.parquet`** (6.2 MB) - Same data, **95.5% smaller** in columnar format

### Unreached Subset
- **`joshua_project_unreached.json`** (72 MB) - Only unreached peoples (7,124 records)
- **`joshua_project_unreached.parquet`** (3.8 MB) - Compressed columnar format

**Why use enriched datasets?**
- ✅ No joins needed - all data in one record
- ✅ Perfect for D3.js, Observable, and visualization tools
- ✅ Faster analysis in Python/R with Parquet format
- ✅ Ready for Hugging Face upload

### Creating Enriched Datasets
```bash
python3 create_enriched_datasets.py
```

This generates:
- Full enriched dataset (JSON + Parquet)
- Unreached subset (JSON + Parquet)
- Metadata with statistics

## Data Utilities

Use `data_utilities.py` for easy data loading and querying:

```python
from data_utilities import *

# Load enriched data
data = load_enriched()

# Get people groups by country
india = get_by_country('IN')

# Get unreached only
unreached = load_unreached()

# Use Parquet for fast analysis
import pandas as pd
df = pd.read_parquet(load_parquet('enriched'))
```

See `USAGE_GUIDE.md` for complete examples.

## Documentation

| File | Purpose |
|------|---------|
| **`USAGE_GUIDE.md`** | Complete guide to using the datasets (visualizations, analysis, Hugging Face) |
| **`DATA_INTEGRATION_STRATEGY.md`** | Technical architecture and integration strategy |
| **`DATASET_CARD.md`** | Hugging Face dataset card (ready for upload) |
| **`data_utilities.py`** | Python utilities for easy data loading |
| **`dataset_metadata.json`** | Fetch dates and record counts |
| **`enriched_metadata.json`** | Enrichment process statistics |
