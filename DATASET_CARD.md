---
license: mit
task_categories:
  - tabular-classification
  - text-classification
language:
  - en
tags:
  - demographics
  - linguistics
  - religion
  - geospatial
  - people-groups
  - languages
  - missions
pretty_name: Joshua Project Global Peoples
size_categories:
  - 10K<n<100K
---

# Joshua Project Global Peoples Dataset

## Dataset Description

- **Homepage:** [joshuaproject.net](https://joshuaproject.net)
- **Repository:** [github.com/lukeslp/joshua-project-data](https://github.com/lukeslp/joshua-project-data)
- **Point of Contact:** [Luke Steuber](https://lukesteuber.com)
- **Part of:** [Data Trove](https://dr.eamer.dev/datavis/data_trove/)

### Dataset Summary

Demographic, linguistic, and religious data for people groups worldwide, sourced from the Joshua Project API v1.

- **16,382 people groups** across 238 countries
- **7,134 languages** with Bible translation status
- **Enriched Parquet files** for fast analysis (95% smaller than JSON)
- Updated December 2025

### Supported Tasks

- Geospatial visualization and mapping
- Demographic analysis and clustering
- Linguistic diversity research
- Bible translation gap analysis
- Cross-cultural studies

### Languages

Data covers 7,134 languages identified by ISO 639-3 codes.

## Dataset Structure

### Data Instances

Each record in the enriched dataset looks like:

```json
{
  "PeopleID3": 10208,
  "PeopNameInCountry": "Tuareg, Air",
  "Population": 517000,
  "LeastReached": "Y",
  "JPScale": 1,
  "PrimaryReligion": "Islam",
  "country_data": {
    "name": "Niger",
    "percent_christianity": 1.62,
    "total_peoples": 36
  },
  "language_data": {
    "name": "Tamajeq, Tayart",
    "bible_status": 4,
    "has_jesus_film": "N"
  }
}
```

### Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `PeopleID3` | int | Unique people-group identifier |
| `PeopNameInCountry` | str | Name within country context |
| `ROG3` | str | 3-letter country code |
| `ROL3` | str | 3-letter language code (ISO 639-3) |
| `Population` | int | Estimated population |
| `LeastReached` | str | `Y` / `N` --under 2% evangelical |
| `JPScale` | int | 1-5 gospel access scale |
| `PrimaryReligion` | str | Predominant religion |
| `PercentEvangelical` | float | Evangelical Christian % |
| `BibleStatus` | int | Translation completeness (0-5) |

107 total fields per record. See [FieldDefinitions.csv](https://github.com/lukeslp/joshua-project-data/blob/main/archive/FieldDefinitions.csv) for the complete schema.

### Data Splits

| Split | Records | Description |
|-------|---------|-------------|
| Full (enriched) | 16,382 | All people groups with embedded country/language data |
| Unreached | 7,124 | Least-reached subset (< 2% evangelical) |

## Dataset Creation

### Source Data

- **Provider:** [Joshua Project](https://joshuaproject.net) via [API v1](https://api.joshuaproject.net/)
- **API maintainer:** [Missional Digerati](https://missionaldigerati.org)
- **Collection date:** December 21-23, 2025
- **Method:** Full API dump via Python fetcher scripts (included in repo)
- **Recommended refresh:** Quarterly

### Considerations for Using the Data

**Known biases:**
- Data is collected with a Christian missions focus --religious categorizations reflect that lens
- Population figures are estimates, not census data
- Coverage is more detailed for regions with active missions research

**Limitations:**
- Snapshot from December 2025; populations and percentages change over time
- Religious categories are simplified; doesn't capture pluralism
- Some remote groups have sparse information

**Ethical use:**
- Not intended for political targeting or discrimination
- Population estimates should be cited as approximations

## Additional Information

### Licensing

This packaging is MIT-licensed. The underlying data is provided by Joshua Project for research purposes --see [joshuaproject.net](https://joshuaproject.net) for their terms.

### Citation

```bibtex
@dataset{joshua_project_2025,
  title   = {Joshua Project Global Peoples Dataset},
  author  = {Joshua Project},
  year    = {2025},
  url     = {https://joshuaproject.net},
  note    = {Packaged by Luke Steuber, fetched December 2025 via API v1}
}
```

### Dataset Card Author

[Luke Steuber](https://lukesteuber.com) --[dr.eamer.dev](https://dr.eamer.dev)
