# Joshua Project Dataset Usage Guide

## 🎯 Quick Start

You now have **9 dataset files** ready for visualization and analysis:

### Normalized Datasets (For relational queries)
```
joshua_project_full_dump.json      130 MB   16,382 people groups
joshua_project_countries.json      286 KB   238 countries
joshua_project_languages.json      4.9 MB   7,134 languages
joshua_project_totals.json         3.1 KB   38 global stats
```

### Enriched Datasets (For visualization - **recommended**)
```
joshua_project_enriched.json       139 MB   16,382 people groups (with embedded country/language data)
joshua_project_enriched.parquet    6.2 MB   ↑ Same data, 95.5% smaller ↑
joshua_project_unreached.json      72 MB    7,124 unreached peoples only
joshua_project_unreached.parquet   3.8 MB   ↑ Same data, compressed ↑
```

---

## 📊 Which Format Should I Use?

### For D3.js / Observable / Browser Visualizations
✅ **Use JSON enriched datasets**

```javascript
// Load full enriched data
d3.json('joshua_project_enriched.json').then(data => {
  // All country and language info embedded - no joins needed!
  const unreached = data.filter(d => d.LeastReached === 'Y');

  // Create visualization
  svg.selectAll('circle')
    .data(unreached)
    .enter().append('circle')
    .attr('cx', d => projection([d.Longitude, d.Latitude])[0])
    .attr('r', d => Math.sqrt(d.Population) / 100)
    .attr('fill', d => d.country_data.continent === 'Asia' ? 'red' : 'blue');
});
```

**Why?**
- ✅ Single file load - no joins needed
- ✅ All related data embedded (country info, language info)
- ✅ Works directly in browsers
- ✅ No dependencies

**Size optimization**: Use `joshua_project_unreached.json` (72 MB) if focusing on unreached peoples only.

---

### For Python Analysis (pandas, polars, etc.)
✅ **Use Parquet files**

```python
import pandas as pd

# Load enriched data (6.2 MB - much faster than 139 MB JSON!)
df = pd.read_parquet('joshua_project_enriched.parquet')

# Query unreached Hindi speakers in India
unreached_hindi = df[
    (df['ROG3'] == 'IN') &
    (df['ROL3'] == 'hin') &
    (df['LeastReached'] == 'Y')
]

print(f"Found {len(unreached_hindi)} unreached Hindi-speaking groups")
print(f"Total population: {unreached_hindi['Population'].sum():,}")
```

**Why?**
- ✅ 95.5% smaller than JSON (6.2 MB vs 139 MB)
- ✅ 10-100x faster to load
- ✅ Columnar format = efficient filtering
- ✅ Strongly typed - no parsing errors

---

### For Data Utilities (Easy Queries)
✅ **Use `data_utilities.py`**

```python
from data_utilities import *

# Get all people groups in a country
india = get_by_country('IN')
print(f"India has {len(india):,} people groups")

# Get Hindi speakers
hindi_speakers = get_by_language('hin')

# Get unreached only
unreached = load_unreached()

# Get country details
india_info = get_country_info('IN')
print(f"India: {india_info['PercentEvangelical']:.2f}% evangelical")
```

**Why?**
- ✅ Simple functions for common queries
- ✅ No need to remember file names
- ✅ Automatic loading and caching
- ✅ Works with both JSON and Parquet

---

## 🗺️ Visualization Examples

### Example 1: World Map of Unreached Peoples
```javascript
// Load enriched unreached data
d3.json('joshua_project_unreached.json').then(peoples => {
  // Group by country
  const byCountry = d3.rollup(
    peoples,
    v => ({
      count: v.length,
      population: d3.sum(v, d => d.Population)
    }),
    d => d.ROG3
  );

  // Color countries by unreached population
  svg.selectAll('.country')
    .data(countries)
    .attr('fill', d => {
      const data = byCountry.get(d.properties.iso_a3);
      return data ? populationScale(data.population) : '#eee';
    });
});
```

### Example 2: Language Family Tree
```python
import pandas as pd
import plotly.express as px

# Load enriched data
df = pd.read_parquet('joshua_project_enriched.parquet')

# Group by language, sum populations
lang_pop = df.groupby('PrimaryLanguageName')['Population'].sum().reset_index()
lang_pop = lang_pop.sort_values('Population', ascending=False).head(20)

# Create treemap
fig = px.treemap(
    lang_pop,
    path=['PrimaryLanguageName'],
    values='Population',
    title='Top 20 Languages by People Group Population'
)
fig.show()
```

### Example 3: Religion Distribution by Continent
```python
import pandas as pd
import plotly.express as px

df = pd.read_parquet('joshua_project_enriched.parquet')

# Extract continent from embedded country_data
df['continent'] = df['country_data'].apply(lambda x: x.get('continent', 'Unknown') if x else 'Unknown')

# Count people groups by religion and continent
religion_by_continent = df.groupby(['continent', 'PrimaryReligion']).size().reset_index(name='count')

# Sunburst chart
fig = px.sunburst(
    religion_by_continent,
    path=['continent', 'PrimaryReligion'],
    values='count',
    title='People Groups by Continent and Religion'
)
fig.show()
```

---

## 📦 Uploading to Hugging Face

### Step 1: Install Hugging Face CLI
```bash
pip install huggingface_hub
huggingface-cli login
```

### Step 2: Create Dataset Repository
```bash
huggingface-cli repo create joshua-project --type dataset
```

### Step 3: Prepare Files
```bash
mkdir huggingface_dataset
cd huggingface_dataset

# Copy Parquet files (recommended format for HF)
cp ../joshua_project_enriched.parquet ./data.parquet
cp ../joshua_project_unreached.parquet ./unreached.parquet
cp ../joshua_project_countries.json ./countries.json
cp ../joshua_project_languages.json ./languages.json

# Copy dataset card
cp ../DATASET_CARD.md ./README.md

# Create loading script (optional but recommended)
cat > joshua_project.py << 'EOF'
import datasets

_DESCRIPTION = "Joshua Project global peoples dataset"
_URLS = {
    "enriched": "data.parquet",
    "unreached": "unreached.parquet",
}

class JoshuaProject(datasets.GeneratorBasedBuilder):
    def _info(self):
        return datasets.DatasetInfo(description=_DESCRIPTION)

    def _split_generators(self, dl_manager):
        urls = _URLS
        data_dir = dl_manager.download_and_extract(urls)
        return [
            datasets.SplitGenerator(
                name="enriched",
                gen_kwargs={"filepath": data_dir["enriched"]},
            ),
        ]
EOF
```

### Step 4: Upload
```bash
git add .
git commit -m "Initial commit: Joshua Project dataset"
git push
```

### Step 5: Use from Hugging Face
```python
from datasets import load_dataset

# Load from your HF repo
ds = load_dataset("your-username/joshua-project", "enriched")

# Convert to pandas
import pandas as pd
df = ds['enriched'].to_pandas()
```

---

## 🔄 Updating the Data

### Refresh All Datasets (Quarterly Recommended)
```bash
# 1. Fetch latest from API
python3 fetch_all_datasets.py

# 2. Regenerate enriched versions
python3 create_enriched_datasets.py

# 3. Push to Hugging Face (if applicable)
cd huggingface_dataset
cp ../joshua_project_enriched.parquet ./data.parquet
git add . && git commit -m "Update: $(date +%Y-%m-%d)" && git push
```

---

## 📚 Data Structure Reference

### Enriched Record Structure
```json
{
  // Original people group fields (107 fields)
  "PeopleID3": 10208,
  "PeopNameInCountry": "Tuareg, Air",
  "Population": 517000,
  "LeastReached": "Y",
  "JPScale": 1,
  "PrimaryReligion": "Islam",
  "ROG3": "NG",
  "ROL3": "thz",

  // Embedded country data (9 fields)
  "country_data": {
    "name": "Niger",
    "continent": null,
    "region": "Africa, West and Central",
    "percent_christianity": 1.62,
    "percent_evangelical": 1.02,
    "total_peoples": 36,
    "unreached_peoples": 30,
    "jp_scale": 1
  },

  // Embedded language data (9 fields)
  "language_data": {
    "name": "Tamajeq, Tayart",
    "hub_country": "Niger",
    "bible_status": 4,
    "bible_year": null,
    "nt_year": "1990-2003",
    "portions_year": "1934-1998",
    "has_jesus_film": "N",
    "has_audio_recordings": "Y",
    "status": "L"
  }
}
```

### Key Fields Explained

| Field | Description | Values |
|-------|-------------|--------|
| `LeastReached` | Unreached status | "Y" or "N" |
| `JPScale` | Gospel access scale | 1 (least) to 5 (most) |
| `BibleStatus` | Bible translation | 0 (none) to 5 (complete) |
| `PrimaryReligion` | Predominant religion | "Islam", "Buddhism", "Hinduism", etc. |
| `Population` | Estimated population | Integer |
| `PercentEvangelical` | % evangelical Christian | 0.0 to 100.0 |

---

## 🎨 Recommended Visualizations

1. **Choropleth Map**: Countries colored by % unreached peoples
2. **Bubble Map**: Unreached populations as circles on world map
3. **Treemap**: Languages by population, colored by Bible translation status
4. **Sankey Diagram**: Flow from continent → religion → reached status
5. **Bar Chart**: Top 20 unreached people groups by population
6. **Network Graph**: Language families and their people groups
7. **Timeline**: Bible translation progress over time
8. **Heatmap**: JP Scale by country and religion

---

## 💡 Tips & Best Practices

### Performance
- ✅ Use Parquet for analysis (95.5% smaller, 10-100x faster)
- ✅ Use unreached subset when possible (43.5% of data)
- ✅ Filter by region/continent to reduce data for regional visualizations

### Data Quality
- ⚠️ Population figures are estimates, not exact
- ⚠️ Some people groups have incomplete language/country data
- ⚠️ Religious percentages are approximations based on research

### Refreshing Data
- 🔄 Update quarterly to get latest population estimates
- 🔄 Check Joshua Project announcements for major data updates
- 🔄 Version your datasets using fetch dates from `dataset_metadata.json`

---

## 📖 Further Reading

- **Strategy Document**: `DATA_INTEGRATION_STRATEGY.md` - Detailed integration architecture
- **Dataset Card**: `DATASET_CARD.md` - Hugging Face-ready documentation
- **Main README**: `README.md` - Complete dataset inventory
- **Metadata**: `dataset_metadata.json` - Fetch dates and record counts
- **Joshua Project API**: https://api.joshuaproject.net/
- **Joshua Project Website**: https://joshuaproject.net/
