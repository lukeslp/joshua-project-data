# Joshua Project Dataset Architecture

## Design Philosophy

**Normalized datasets as source of truth** + **Enriched datasets for consumption**

This hybrid architecture provides the best of both worlds:
- ✅ Clean, updatable source data (normalized)
- ✅ Easy-to-use visualizations (enriched JSON)
- ✅ High-performance analysis (enriched Parquet)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    JOSHUA PROJECT API                       │
│              https://api.joshuaproject.net/v1/              │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ fetch_all_datasets.py
                              │ (quarterly updates)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              NORMALIZED DATASETS (Source of Truth)          │
├─────────────────────────────────────────────────────────────┤
│  📄 joshua_project_full_dump.json      130 MB   16,382     │
│  📄 joshua_project_countries.json      286 KB   238        │
│  📄 joshua_project_languages.json      4.9 MB   7,134      │
│  📄 joshua_project_totals.json         3.1 KB   38         │
│  📄 dataset_metadata.json              < 1 KB   (tracking) │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ create_enriched_datasets.py
                              │ (run after API updates)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              ENRICHED DATASETS (For Consumption)            │
├─────────────────────────────────────────────────────────────┤
│  FULL DATASET (all people groups with embedded data)       │
│  📄 joshua_project_enriched.json       139 MB   16,382     │
│  📦 joshua_project_enriched.parquet    6.2 MB   16,382     │
│                                                              │
│  UNREACHED SUBSET (43.5% of data)                          │
│  📄 joshua_project_unreached.json      72 MB    7,124      │
│  📦 joshua_project_unreached.parquet   3.8 MB   7,124      │
│                                                              │
│  METADATA                                                    │
│  📄 enriched_metadata.json             < 1 KB   (stats)    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├───────────────┬───────────────┐
                              ▼               ▼               ▼
                    ┌──────────────┐  ┌──────────────┐  ┌─────────────┐
                    │ D3.js / Web  │  │   Python     │  │ Hugging Face│
                    │ Visualizations│  │  Analysis    │  │   Upload    │
                    │              │  │              │  │             │
                    │  .json files │  │ .parquet files│  │ .parquet    │
                    └──────────────┘  └──────────────┘  └─────────────┘
```

---

## File Inventory

### Source of Truth (Normalized - 135 MB total)
```
joshua_project_full_dump.json       130 MB    People groups (PGIC)
joshua_project_countries.json       286 KB    Country statistics
joshua_project_languages.json       4.9 MB    Language details
joshua_project_totals.json          3.1 KB    Global summaries
dataset_metadata.json               < 1 KB    Fetch tracking
```

**Update workflow**: `python3 fetch_all_datasets.py` (quarterly)

---

### Enriched for Consumption (222 MB JSON, 10 MB Parquet)
```
joshua_project_enriched.json        139 MB    Full dataset (browser viz)
joshua_project_enriched.parquet     6.2 MB    Full dataset (analysis)
joshua_project_unreached.json       72 MB     Unreached subset (browser)
joshua_project_unreached.parquet    3.8 MB    Unreached subset (analysis)
enriched_metadata.json              < 1 KB    Enrichment stats
```

**Regenerate workflow**: `python3 create_enriched_datasets.py` (after API updates)

---

### Scripts & Utilities
```
fetch_all_datasets.py               6.8 KB    Fetch from API
create_enriched_datasets.py         11 KB     Generate enriched versions
data_utilities.py                   7.4 KB    Loading helpers
```

---

### Documentation
```
README.md                           Updated    Complete inventory
USAGE_GUIDE.md                      9.9 KB     How to use datasets
DATA_INTEGRATION_STRATEGY.md        7.4 KB     Technical architecture
DATASET_CARD.md                     6.4 KB     Hugging Face ready
ARCHITECTURE.md                     This file  System overview
```

---

## Data Flow

### 1. Initial Setup (One-time)
```bash
# Fetch all normalized datasets from API
python3 fetch_all_datasets.py

# Generate enriched versions
python3 create_enriched_datasets.py
```

**Result**: 9 dataset files ready for use

---

### 2. Quarterly Updates
```bash
# Step 1: Update source of truth
python3 fetch_all_datasets.py
# Downloads: countries, languages, totals (< 5 seconds)

# Step 2: Regenerate enriched datasets
python3 create_enriched_datasets.py
# Creates: enriched JSON + Parquet (~ 30 seconds)

# Step 3: Update Hugging Face (optional)
cp joshua_project_enriched.parquet huggingface_dataset/
cd huggingface_dataset && git push
```

---

### 3. Usage Patterns

**For D3.js/Observable Visualization**:
```javascript
// Load enriched JSON - everything embedded, no joins
d3.json('joshua_project_enriched.json').then(data => {
  // Country and language data already embedded
  const viz = data.filter(d => d.LeastReached === 'Y')
    .map(d => ({
      name: d.PeopNameInCountry,
      country: d.country_data.name,
      language: d.language_data.name,
      population: d.Population
    }));
});
```

**For Python/pandas Analysis**:
```python
# Load Parquet - 95.5% smaller, 20x faster
import pandas as pd
df = pd.read_parquet('joshua_project_enriched.parquet')

# Query with embedded data
result = df[df['LeastReached'] == 'Y'].groupby('ROG3').agg({
    'Population': 'sum',
    'PeopleID3': 'count'
})
```

**For Simple Queries**:
```python
# Use helper functions
from data_utilities import *

india = get_by_country('IN')        # All groups in India
unreached = load_unreached()        # Just unreached groups
hindi = get_by_language('hin')      # Hindi speakers
```

---

## Key Design Decisions

### Why Keep Normalized Datasets?

✅ **Source of Truth**: Match API structure exactly
✅ **Clean Updates**: Refresh individual datasets without rebuilding everything
✅ **Storage Efficient**: No data duplication in source files
✅ **API Parity**: Easy to validate against source

### Why Create Enriched Datasets?

✅ **No Joins Needed**: Single file loading for visualizations
✅ **Browser Friendly**: JSON works directly in browsers
✅ **Performance**: Parquet is 95.5% smaller and 10-100x faster
✅ **Simplicity**: Beginners don't need to understand relational joins

### Why Both JSON and Parquet?

**JSON** (for visualizations):
- ✅ Works in browsers
- ✅ Human readable
- ✅ No dependencies
- ✅ D3.js native format

**Parquet** (for analysis):
- ✅ 95.5% smaller (6.2 MB vs 139 MB)
- ✅ Columnar = efficient filtering
- ✅ Strongly typed
- ✅ Industry standard (Hugging Face, Databricks, Snowflake)

---

## Storage Efficiency

| Format | Files | Total Size | Compression |
|--------|-------|------------|-------------|
| **Normalized (source)** | 4 | 135 MB | Baseline |
| **Enriched JSON** | 2 | 211 MB | +56% (embedded data) |
| **Enriched Parquet** | 2 | 10 MB | **-93% vs source!** |

**Parquet magic**: Columnar format + compression = 93% space savings

---

## Maintenance Schedule

### Quarterly (Recommended)
1. Run `fetch_all_datasets.py` to update source data
2. Run `create_enriched_datasets.py` to regenerate enriched versions
3. Update Hugging Face repo (if applicable)

### As Needed
- When Joshua Project announces major updates
- When adding new enriched dataset variants (e.g., by region)
- When updating documentation

### Version Tracking
- Use `dataset_metadata.json` fetch dates as version identifiers
- Example: "2025-12-23" = December 23, 2025 snapshot

---

## Future Enhancements

### Potential Additions
- Regional subsets (by continent/region)
- Religion-focused datasets
- Language family aggregations
- Time-series data (if historical snapshots saved)

### When to Add
- **Regional subsets**: If visualizations focus on specific regions
- **Specialized views**: Based on actual usage patterns
- **Historical data**: If tracking changes over time becomes valuable

---

## Success Metrics

✅ **All 4 API datasets** fetched (people_groups, countries, languages, totals)
✅ **16,382 people groups** with 99.99% country/language coverage
✅ **Enriched datasets** created in both JSON and Parquet
✅ **95.5% compression** achieved with Parquet
✅ **Complete documentation** for all use cases
✅ **Python utilities** for easy data access
✅ **Ready for Hugging Face** upload

**Total dataset package**: 357 MB (JSON) or 145 MB (with Parquet replacing JSON)

---

## Questions & Answers

**Q: Which format should I use?**
- Visualization → Enriched JSON
- Analysis → Enriched Parquet
- Database → Normalized JSON

**Q: How do I update the data?**
- Run `fetch_all_datasets.py` then `create_enriched_datasets.py`

**Q: Can I delete the JSON enriched files?**
- Yes, if you only need Parquet for analysis (saves 211 MB)
- Keep them if you need browser-based visualizations

**Q: Should I commit large files to git?**
- **Commit**: Scripts, docs, metadata
- **Don't commit**: Large dataset files (use Git LFS or .gitignore)
- **Alternative**: Upload to Hugging Face, reference in README

**Q: How do I share this dataset?**
- Upload Parquet files to Hugging Face
- Share documentation and data_utilities.py
- Reference source API for attribution
