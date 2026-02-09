# Joshua Project Data Integration Strategy

## Current State

**4 normalized datasets** (database-style structure):
- `joshua_project_full_dump.json` - 16,382 people groups (130 MB)
- `joshua_project_countries.json` - 238 countries (286 KB)
- `joshua_project_languages.json` - 7,134 languages (4.9 MB)
- `joshua_project_totals.json` - 38 global stats (3.1 KB)

**Relationships**: Near-perfect referential integrity
- All 238 countries in people groups → covered in countries dataset ✅
- 6,164 languages in people groups → 7,133/7,134 covered (99.99%) ✅

## Recommended Approach: Hybrid Architecture

### 1. Keep Normalized (Current) ✅
**Use for**: API-style queries, updates, storage efficiency

**Advantages**:
- Matches source API structure
- Easy to update individual datasets
- No data redundancy
- Clean separation of concerns

**Keep as-is**: All 4 JSON files + metadata tracker

---

### 2. Create Enriched/Denormalized Versions

#### A. Full Enriched Dataset
**File**: `joshua_project_enriched.json` / `.parquet`
**Purpose**: Complete data for complex visualizations

**Structure**: People groups with embedded country + language data
```json
{
  "PeopleID3": 10208,
  "PeopNameInCountry": "Tuareg, Air",
  "Population": 517000,
  "LeastReached": "Y",
  "JPScale": 1,

  // Embedded country data
  "country": {
    "ROG3": "NG",
    "Ctry": "Niger",
    "PercentChristianity": 1.2,
    "CntPeoples": 45,
    "CntPeoplesLR": 38
  },

  // Embedded language data
  "language": {
    "ROL3": "thz",
    "Language": "Tamajeq, Tayart",
    "BibleStatus": 4,
    "NTYear": "1990-2003",
    "HasJesusFilm": "N"
  }
}
```

**Size estimate**: ~150-180 MB (adds ~20-50 MB overhead)

**Use cases**:
- D3.js visualizations (maps, networks, charts)
- Single-file data loading
- Exploratory analysis
- Quick prototyping

---

#### B. Specialized Exports

**1. Unreached Peoples Focus**
- **File**: `joshua_project_unreached.json` / `.parquet`
- **Filter**: `LeastReached == "Y"` only
- **Records**: ~7,000 (43% of total)
- **Use**: Focused visualizations, mission analytics

**2. Geographic Clusters**
- **Files**: `joshua_project_by_region/[region].json`
- **Split by**: `RegionName` (14 regions)
- **Use**: Regional dashboards, continent-specific analysis

**3. Religion-Focused**
- **File**: `joshua_project_by_religion.json`
- **Group by**: `PrimaryReligion`
- **Use**: Religious demographics, comparative analysis

**4. Language Families**
- **File**: `joshua_project_language_families.json`
- **Aggregate**: By language with people group arrays
- **Use**: Bible translation gap analysis

---

### 3. Hugging Face Dataset Package

**Repository structure**:
```
joshua-project-dataset/
├── data/
│   ├── people_groups.parquet
│   ├── countries.parquet
│   ├── languages.parquet
│   ├── totals.parquet
│   └── enriched/
│       ├── full_enriched.parquet
│       ├── unreached_only.parquet
│       └── by_region/
│           ├── africa.parquet
│           ├── asia.parquet
│           └── ...
├── README.md (dataset card)
├── joshua_project.py (loading script)
└── metadata.json
```

**Format choice**: **Parquet** (not JSON)
- ✅ Columnar format: Efficient for analytics
- ✅ Compressed: 50-70% smaller than JSON
- ✅ Typed schemas: Better data integrity
- ✅ Native support: pandas, DuckDB, Polars, Arrow
- ✅ Hugging Face standard: `datasets` library compatible

**Example loading**:
```python
from datasets import load_dataset

# Load normalized datasets
ds = load_dataset("your-username/joshua-project")
people = ds["people_groups"]
countries = ds["countries"]

# Or load enriched version
enriched = load_dataset("your-username/joshua-project", "enriched")
```

---

## Implementation Plan

### Phase 1: Build Enrichment Pipeline ✅
**Script**: `create_enriched_datasets.py`

Features:
- Join people groups + countries + languages
- Create full enriched version
- Create specialized subsets (unreached, by region, etc.)
- Export as both JSON and Parquet
- Validate data integrity
- Generate summary statistics

### Phase 2: Hugging Face Preparation
**Script**: `prepare_huggingface_dataset.py`

Tasks:
- Convert all datasets to Parquet
- Create dataset card (README.md)
- Generate metadata.json
- Create loading script
- Add data fields documentation
- Include license and citation info

### Phase 3: Visualization Utilities
**Script**: `data_utilities.py`

Functions:
- `load_normalized()` - Load separate datasets
- `load_enriched()` - Load denormalized version
- `filter_unreached()` - Get unreached peoples
- `get_by_country(country_code)` - Country-specific data
- `get_by_language(language_code)` - Language-specific data
- `get_by_region(region_name)` - Regional data

---

## File Size Estimates

| Dataset | JSON | Parquet | Use Case |
|---------|------|---------|----------|
| People Groups | 130 MB | ~50 MB | Base data |
| Countries | 286 KB | ~100 KB | Lookups |
| Languages | 4.9 MB | ~2 MB | Lookups |
| Totals | 3 KB | ~1 KB | Stats |
| **Full Enriched** | ~180 MB | ~70 MB | Viz, analysis |
| **Unreached Only** | ~80 MB | ~30 MB | Focused viz |
| **By Region (14 files)** | ~10-15 MB each | ~4-6 MB each | Regional dash |

---

## Recommendations by Use Case

### For Visualizations (D3.js, Observable, etc.)
✅ **Use enriched JSON** - Single file, easy browser loading
- `joshua_project_enriched.json` for full dataset
- `joshua_project_unreached.json` for focused view
- Regional splits for continent-specific maps

### For Analysis (Python/R/Julia)
✅ **Use Parquet files** - Fast loading, efficient storage
- Load with pandas/polars/DuckDB
- Columnar operations are 10-100x faster
- Can load subsets without reading entire file

### For Hugging Face Upload
✅ **Use Parquet** - Platform standard
- Include both normalized and enriched versions
- Multiple dataset configs (default, enriched, unreached)
- Comprehensive dataset card

### For Web Apps (Flask/Express APIs)
✅ **Use normalized JSON** - Easy querying
- Keep current structure
- Load into SQLite/Postgres for complex queries
- Or use DuckDB for zero-setup SQL on Parquet

### For Mobile/Embedded
✅ **Use compressed subsets** - Minimize bandwidth
- Regional splits
- Unreached only
- Pre-filtered by criteria

---

## Next Steps

1. **Run**: `python3 create_enriched_datasets.py`
   - Generates all enriched versions
   - Exports JSON and Parquet formats
   - Creates validation reports

2. **Run**: `python3 prepare_huggingface_dataset.py`
   - Prepares complete HF-ready package
   - Generates dataset card
   - Creates upload structure

3. **Upload to Hugging Face**:
   ```bash
   huggingface-cli login
   huggingface-cli repo create joshua-project --type dataset
   cd huggingface_dataset/
   git add . && git commit -m "Initial commit"
   git push
   ```

4. **Update visualizations**:
   - Use enriched JSON for browser-based viz
   - Reference HF dataset in documentation
   - Add loading examples to README

---

## Maintenance Strategy

**When to update**:
- Quarterly: Refresh from API to get latest population estimates
- On-demand: When Joshua Project announces major updates

**Update workflow**:
```bash
# 1. Fetch latest normalized data
python3 fetch_all_datasets.py

# 2. Regenerate enriched versions
python3 create_enriched_datasets.py

# 3. Update Hugging Face
python3 prepare_huggingface_dataset.py
cd huggingface_dataset && git push
```

**Version tracking**: Use `dataset_metadata.json` fetch dates as version identifiers
