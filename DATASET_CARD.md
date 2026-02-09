# Joshua Project Global Peoples Dataset

## Dataset Description

The Joshua Project dataset provides comprehensive demographic, linguistic, and religious information about people groups worldwide. This dataset is the primary source for understanding unreached people groups and Bible translation needs globally.

### Dataset Summary

- **16,382 people groups** across 238 countries
- **7,134 languages** with translation status
- **Demographic data**: Population, geographic location, cultural affinity
- **Religious data**: Primary religion, Christian/evangelical percentages, JP Scale
- **Translation data**: Bible status, Jesus Film availability, audio resources

### Supported Tasks

- Geospatial visualization and mapping
- Demographic analysis and statistics
- Mission strategy planning and research
- Bible translation gap analysis
- Religious demographics research

### Languages

Data includes information about 7,134 languages worldwide, with ISO 639-3 language codes (ROL3).

## Dataset Structure

### Data Instances

**Enriched Format** (recommended for visualization):
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
    "total_peoples": 36,
    "unreached_peoples": 30
  },
  "language_data": {
    "name": "Tamajeq, Tayart",
    "bible_status": 4,
    "has_jesus_film": "N"
  }
}
```

**Normalized Format** (for relational queries):
- Separate people_groups, countries, languages, and totals tables
- Join via ROG3 (country code) and ROL3 (language code)

### Data Fields

#### People Groups (16,382 records)
- `PeopleID3` - Unique identifier
- `PeopNameInCountry` - People group name within country
- `ROG3` - Country code (3-letter)
- `ROL3` - Language code (3-letter)
- `Population` - Estimated population
- `LeastReached` - Y/N indicator (< 2% evangelical)
- `JPScale` - Joshua Project Scale (1-5, measuring gospel access)
- `PrimaryReligion` - Predominant religion
- `PercentEvangelical` - % evangelical Christian
- `BibleStatus` - Bible translation status code
- ... (107 total fields)

#### Countries (238 records)
- `ROG3` - Country code
- `Ctry` - Country name
- `Continent` - Continent name
- `CntPeoples` - Total people groups in country
- `CntPeoplesLR` - Count of unreached people groups
- `PercentChristianity` - % Christian adherents
- ... (statistical aggregations)

#### Languages (7,134 records)
- `ROL3` - Language code (ISO 639-3)
- `Language` - Language name
- `BibleStatus` - Translation status (0-5 scale)
- `NTYear` - New Testament publication year(s)
- `HasJesusFilm` - Y/N indicator
- ... (translation resources)

### Data Splits

| Split | Records | Description |
|-------|---------|-------------|
| `full` | 16,382 | All people groups (enriched) |
| `unreached` | 7,124 | Least-reached only (< 2% evangelical) |
| `normalized/people_groups` | 16,382 | People groups (normalized) |
| `normalized/countries` | 238 | Countries (normalized) |
| `normalized/languages` | 7,134 | Languages (normalized) |
| `normalized/totals` | 38 | Global statistics |

## Dataset Creation

### Curation Rationale

The Joshua Project tracks people groups worldwide to identify where the Christian gospel has limited presence and where Bible translation/missions work is needed. This data supports:

- Strategic mission planning
- Bible translation prioritization
- Academic research on religion and demographics
- Cultural and linguistic preservation efforts

### Source Data

**Initial Data Collection**:
- Primary source: Joshua Project Research Initiative
- API endpoint: https://api.joshuaproject.net/v1/
- Data collected: December 21-23, 2025
- Update frequency: Quarterly (recommended)

**Data Collection Process**:
1. Fetched via Joshua Project API v1
2. Normalized datasets joined and enriched
3. Exported to Parquet (columnar) and JSON (document) formats

### Annotations

Data is primarily observational (demographic/linguistic facts) with some analytical fields:
- **JP Scale**: Expert assessment of gospel access (1-5)
- **Least Reached**: Calculated from evangelical percentage
- **Bible Status**: Assessed translation completeness (0-5)

Annotations are performed by Joshua Project researchers through field research, surveys, and published sources.

## Considerations for Using the Data

### Social Impact of Dataset

**Intended Use**:
- Mission strategy and resource allocation
- Academic research on global religion
- Bible translation planning
- Geospatial visualization of cultural/linguistic diversity

**Potential Misuse**:
- Should NOT be used for political targeting or discrimination
- Population estimates are approximations, not precise census data
- Religious affiliation percentages are estimates based on available research

### Discussion of Biases

- **Christian-centric perspective**: Data is collected with Christian missions focus
- **Population estimates**: Based on regional census data and research estimates; may lag reality by years
- **Religious categorization**: Simplified into broad categories; doesn't capture religious pluralism
- **Geographic focus**: More detailed data for regions with active missions research

### Other Known Limitations

- **Updates**: Data reflects 2025 snapshot; populations and percentages change over time
- **Country boundaries**: Political changes may affect country codes (ROG3)
- **Language codes**: Follows ISO 639-3 which occasionally updates
- **Missing data**: Some remote people groups have limited information

## Additional Information

### Dataset Curators

- **Original data**: Joshua Project (joshuaproject.net)
- **Dataset packaging**: Luke Steuber
- **API provided by**: Missional Digerati

### Licensing Information

Joshua Project data is provided for research and missions purposes. Check joshuaproject.net for current terms of use.

### Citation Information

```bibtex
@dataset{joshua_project_2025,
  title={Joshua Project Global Peoples Dataset},
  author={Joshua Project},
  year={2025},
  publisher={Joshua Project},
  url={https://joshuaproject.net},
  note={Data fetched December 2025 via API v1}
}
```

### Contributions

For questions about the underlying data, contact Joshua Project via joshuaproject.net.

For issues with this dataset packaging, see the repository README.

## Dataset Card Authors

Luke Steuber

## Dataset Card Contact

See repository for contact information.
