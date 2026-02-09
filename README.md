# Joshua Project Global Peoples Dataset

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Data Source](https://img.shields.io/badge/Source-Joshua%20Project%20API-orange)](https://joshuaproject.net)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97-HuggingFace-yellow)](https://huggingface.co/datasets/lukeslp/joshua-project-peoples)
[![Kaggle](https://img.shields.io/badge/Kaggle-Dataset-20BEFF)](https://www.kaggle.com/datasets/lukeslp/joshua-project-global-peoples)

Demographic, linguistic, and religious data for **16,382 people groups** across **238 countries** and **7,134 languages**, fetched from the [Joshua Project API](https://api.joshuaproject.net/).

Part of the [Data Trove](https://dr.eamer.dev/datavis/data_trove/) collection at [dr.eamer.dev](https://dr.eamer.dev).

---

## What's Inside

| File | Records | Size | Format |
|------|---------|------|--------|
| `joshua_project_full_dump.json` | 16,382 people groups | 130 MB | JSON (LFS) |
| `joshua_project_countries.json` | 238 countries | 286 KB | JSON |
| `joshua_project_languages.json` | 7,134 languages | 4.9 MB | JSON |
| `joshua_project_totals.json` | 38 global stats | 3 KB | JSON |
| `joshua_project_enriched.parquet` | 16,382 (denormalized) | 6.2 MB | Parquet (LFS) |
| `joshua_project_unreached.parquet` | 7,124 unreached | 3.8 MB | Parquet (LFS) |

**Enriched** variants embed country and language data directly into each people-group record -- no joins required.

**Parquet** variants are 95% smaller than their JSON equivalents and load 10-100x faster in pandas.

---

## Quick Start

### Python / pandas

```python
import pandas as pd

# Load the enriched dataset (recommended)
df = pd.read_parquet("joshua_project_enriched.parquet")

# Unreached people groups in South Asia
unreached_sa = df[(df["LeastReached"] == "Y") & (df["ROG3Continent"] == "Asia")]
print(f"{len(unreached_sa):,} unreached groups in Asia")
```

### D3.js / JavaScript

```javascript
const data = await d3.json("joshua_project_enriched.json");

// Top 10 unreached by population
const top = data
  .filter(d => d.LeastReached === "Y")
  .sort((a, b) => b.Population - a.Population)
  .slice(0, 10);
```

### Command Line

```bash
# Refresh all datasets from the API
export JOSHUA_PROJECT_API_KEY="your_key_here"
python3 fetch_all_datasets.py

# Regenerate enriched + parquet files
python3 create_enriched_datasets.py
```

Get an API key free at [joshuaproject.net/api](https://joshuaproject.net/api).

---

## Dataset Relationships

```
People Groups  ──┬── ROG3 ──▶  Countries
                  └── ROL3 ──▶  Languages

Totals = global aggregates across all people groups
```

- **`ROG3`** --3-letter country code (e.g., `IN` = India)
- **`ROL3`** --3-letter language code, ISO 639-3 (e.g., `hin` = Hindi)
- **`PeopleID3`** --unique people-group identifier

---

## Key Fields

| Field | Description |
|-------|-------------|
| `PeopNameInCountry` | People group name within a specific country |
| `Population` | Estimated population |
| `PrimaryReligion` | Predominant religion |
| `LeastReached` | `Y` if < 2% evangelical, < 5% Christian adherents |
| `JPScale` | 1-5 scale of gospel access (1 = least reached) |
| `BibleStatus` | Bible translation completeness (0-5) |
| `PercentEvangelical` | Evangelical Christian percentage |

Full field definitions: [`archive/FieldDefinitions.csv`](archive/FieldDefinitions.csv)

---

## Refreshing the Data

The Joshua Project updates their data regularly. To pull the latest:

```bash
# 1. Set your API key
export JOSHUA_PROJECT_API_KEY="your_key_here"

# 2. Fetch normalized datasets (~5 seconds)
python3 fetch_all_datasets.py

# 3. Fetch full people groups dump (~30 seconds)
python3 fetch_full_data.py

# 4. Regenerate enriched datasets (~30 seconds)
python3 create_enriched_datasets.py
```

I recommend refreshing quarterly.

---

## Project Structure

```
├── joshua_project_full_dump.json       # 16,382 people groups (source of truth)
├── joshua_project_countries.json       # 238 countries
├── joshua_project_languages.json       # 7,134 languages
├── joshua_project_totals.json          # 38 global summary stats
├── joshua_project_enriched.parquet     # Denormalized, analysis-ready
├── joshua_project_unreached.parquet    # Unreached subset only
│
├── fetch_all_datasets.py               # Fetch countries/languages/totals
├── fetch_full_data.py                  # Fetch full people groups dump
├── create_enriched_datasets.py         # Generate enriched + parquet
├── data_utilities.py                   # Python loading helpers
│
├── ARCHITECTURE.md                     # System design overview
├── DATASET_CARD.md                     # HuggingFace dataset card
├── USAGE_GUIDE.md                      # Detailed usage examples
├── LICENSE                             # MIT
└── archive/                            # Legacy CSVs (2016 era)
```

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Normalized vs. enriched design, data flow diagrams |
| [DATASET_CARD.md](DATASET_CARD.md) | HuggingFace-format dataset card with bias/limitations |
| [USAGE_GUIDE.md](USAGE_GUIDE.md) | Detailed Python, D3.js, and R usage examples |
| [DATA_INTEGRATION_STRATEGY.md](DATA_INTEGRATION_STRATEGY.md) | Technical integration and enrichment strategy |

---

## Data Source & Attribution

All data originates from the [Joshua Project](https://joshuaproject.net), a research initiative tracking people groups worldwide. The API is maintained by [Missional Digerati](https://missionaldigerati.org).

If you use this dataset, please cite:

```bibtex
@dataset{joshua_project_2025,
  title   = {Joshua Project Global Peoples Dataset},
  author  = {Joshua Project},
  year    = {2025},
  url     = {https://joshuaproject.net},
  note    = {Packaged by Luke Steuber, fetched December 2025 via API v1}
}
```

---

## Related

- [Data Trove](https://dr.eamer.dev/datavis/data_trove/) --full dataset catalog
- [lukesteuber.com](https://lukesteuber.com) --portfolio
- [HuggingFace Dataset](https://huggingface.co/datasets/lukeslp/joshua-project-peoples)
- [Kaggle Dataset](https://www.kaggle.com/datasets/lukeslp/joshua-project-global-peoples)

---

## License

MIT. See [LICENSE](LICENSE).

The underlying data is provided by Joshua Project for research purposes. Check [joshuaproject.net](https://joshuaproject.net) for their terms of use.
