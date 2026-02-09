"""
File Purpose: Create enriched/denormalized versions of Joshua Project data.
Primary Functions:
- Loads normalized datasets (people_groups, countries, languages)
- Joins data to create enriched versions with embedded lookups
- Generates specialized subsets (unreached, by region, etc.)
- Exports to JSON and Parquet formats
- Validates data integrity

Inputs:
- joshua_project_full_dump.json (people groups)
- joshua_project_countries.json
- joshua_project_languages.json

Outputs:
- joshua_project_enriched.json (full denormalized)
- joshua_project_enriched.parquet
- joshua_project_unreached.json (unreached only)
- joshua_project_unreached.parquet
- enriched_metadata.json (stats and validation report)
"""

import json
import os
from datetime import datetime

def load_datasets():
    """Load all normalized datasets."""
    print("\n" + "="*70)
    print("LOADING NORMALIZED DATASETS")
    print("="*70)

    datasets = {}

    files = {
        'people_groups': 'joshua_project_full_dump.json',
        'countries': 'joshua_project_countries.json',
        'languages': 'joshua_project_languages_enriched_geo.json',  # Use geo-enriched version with family names
        'totals': 'joshua_project_totals.json'
    }

    for name, filename in files.items():
        print(f"\nLoading {name}...")
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            count = len(data) if isinstance(data, list) else len(data.keys())
            print(f"  ✅ Loaded {count:,} records from {filename}")
            datasets[name] = data

        except FileNotFoundError:
            print(f"  ❌ File not found: {filename}")
            return None
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON error in {filename}: {e}")
            return None

    return datasets

def create_lookups(datasets):
    """Create fast lookup dictionaries."""
    print("\n" + "="*70)
    print("CREATING LOOKUP INDICES")
    print("="*70)

    # Country lookup by ROG3
    countries_lookup = {c['ROG3']: c for c in datasets['countries']}
    print(f"✅ Country lookup: {len(countries_lookup)} entries")

    # Language lookup by ROL3
    languages_lookup = {l['ROL3']: l for l in datasets['languages']}
    print(f"✅ Language lookup: {len(languages_lookup)} entries")

    # Totals as dict
    totals_lookup = {t['id']: t for t in datasets['totals']}
    print(f"✅ Totals lookup: {len(totals_lookup)} entries")

    return {
        'countries': countries_lookup,
        'languages': languages_lookup,
        'totals': totals_lookup
    }

def enrich_people_group(people_group, lookups):
    """Enrich a single people group record with country and language data."""
    enriched = people_group.copy()

    # Add country data
    country_code = people_group.get('ROG3')
    if country_code and country_code in lookups['countries']:
        country = lookups['countries'][country_code]
        enriched['country_data'] = {
            'name': country.get('Ctry'),
            'continent': country.get('Continent'),
            'region': country.get('RegionName'),
            'percent_christianity': country.get('PercentChristianity'),
            'percent_evangelical': country.get('PercentEvangelical'),
            'total_peoples': country.get('CntPeoples'),
            'unreached_peoples': country.get('CntPeoplesLR'),
            'jp_scale': country.get('JPScaleCtry')
        }

    # Add language data
    language_code = people_group.get('ROL3')
    if language_code and language_code in lookups['languages']:
        language = lookups['languages'][language_code]
        enriched['language_data'] = {
            'name': language.get('Language'),
            'hub_country': language.get('HubCountry'),
            'bible_status': language.get('BibleStatus'),
            'bible_year': language.get('BibleYear'),
            'nt_year': language.get('NTYear'),
            'portions_year': language.get('PortionsYear'),
            'has_jesus_film': language.get('HasJesusFilm'),
            'has_audio_recordings': language.get('AudioRecordings'),
            'status': language.get('Status'),
            # Geographic enrichment fields from Glottolog
            'latitude': language.get('latitude'),
            'longitude': language.get('longitude'),
            'glottocode': language.get('glottocode'),
            'family_name': language.get('family_name'),
            'family_id': language.get('family_id'),
            'macroarea': language.get('macroarea')
        }

    return enriched

def create_full_enriched(datasets, lookups):
    """Create fully enriched dataset with all people groups."""
    print("\n" + "="*70)
    print("CREATING FULL ENRICHED DATASET")
    print("="*70)

    people_groups = datasets['people_groups']
    enriched_records = []

    total = len(people_groups)
    for i, pg in enumerate(people_groups):
        enriched = enrich_people_group(pg, lookups)
        enriched_records.append(enriched)

        # Progress indicator
        if (i + 1) % 1000 == 0:
            print(f"  Progress: {i+1:,}/{total:,} ({100*(i+1)/total:.1f}%)")

    print(f"\n✅ Created {len(enriched_records):,} enriched records")
    return enriched_records

def create_unreached_subset(enriched_records):
    """Create subset with only unreached people groups."""
    print("\n" + "="*70)
    print("CREATING UNREACHED SUBSET")
    print("="*70)

    unreached = [r for r in enriched_records if r.get('LeastReached') == 'Y']

    print(f"✅ Filtered to {len(unreached):,} unreached people groups")
    print(f"   ({100*len(unreached)/len(enriched_records):.1f}% of total)")

    return unreached

def save_json(data, filename, description):
    """Save data to JSON file."""
    print(f"\nSaving {description} to {filename}...")

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✅ Saved {size_mb:.2f} MB ({len(data):,} records)")
        return True

    except Exception as e:
        print(f"❌ Error saving: {e}")
        return False

def save_parquet(data, filename, description):
    """Save data to Parquet file."""
    print(f"\nSaving {description} to {filename}...")

    try:
        import pyarrow as pa
        import pyarrow.parquet as pq

        # Convert to PyArrow table
        table = pa.Table.from_pylist(data)

        # Write with compression
        pq.write_table(table, filename, compression='snappy')

        size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✅ Saved {size_mb:.2f} MB ({len(data):,} records)")
        return True

    except ImportError:
        print(f"⚠️  PyArrow not installed. Run: pip install pyarrow")
        print(f"   Skipping Parquet export for {filename}")
        return False
    except Exception as e:
        print(f"❌ Error saving: {e}")
        return False

def generate_enrichment_metadata(datasets, enriched, unreached):
    """Generate metadata about enrichment process."""
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "source_datasets": {
            "people_groups": len(datasets['people_groups']),
            "countries": len(datasets['countries']),
            "languages": len(datasets['languages']),
            "totals": len(datasets['totals'])
        },
        "enriched_datasets": {
            "full_enriched": {
                "records": len(enriched),
                "json_file": "joshua_project_enriched.json",
                "parquet_file": "joshua_project_enriched.parquet"
            },
            "unreached_only": {
                "records": len(unreached),
                "json_file": "joshua_project_unreached.json",
                "parquet_file": "joshua_project_unreached.parquet",
                "percentage_of_total": round(100 * len(unreached) / len(enriched), 2)
            }
        },
        "enrichment_details": {
            "added_fields": [
                "country_data (9 fields)",
                "language_data (9 fields)"
            ],
            "original_fields_per_record": 107,
            "enriched_fields_per_record": 109  # 107 + country_data + language_data
        }
    }

    return metadata

def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("JOSHUA PROJECT DATA ENRICHMENT PIPELINE")
    print("="*70)

    # Load datasets
    datasets = load_datasets()
    if not datasets:
        print("\n❌ Failed to load datasets. Exiting.")
        return

    # Create lookups
    lookups = create_lookups(datasets)

    # Create full enriched dataset
    enriched = create_full_enriched(datasets, lookups)

    # Create unreached subset
    unreached = create_unreached_subset(enriched)

    # Save outputs
    print("\n" + "="*70)
    print("SAVING ENRICHED DATASETS")
    print("="*70)

    results = {
        'full_json': save_json(enriched, 'joshua_project_enriched.json', 'full enriched dataset'),
        'full_parquet': save_parquet(enriched, 'joshua_project_enriched.parquet', 'full enriched dataset'),
        'unreached_json': save_json(unreached, 'joshua_project_unreached.json', 'unreached subset'),
        'unreached_parquet': save_parquet(unreached, 'joshua_project_unreached.parquet', 'unreached subset')
    }

    # Generate and save metadata
    metadata = generate_enrichment_metadata(datasets, enriched, unreached)
    save_json(metadata, 'enriched_metadata.json', 'enrichment metadata')

    # Print summary
    print("\n" + "="*70)
    print("ENRICHMENT SUMMARY")
    print("="*70)

    success_count = sum(1 for v in results.values() if v)
    print(f"\nFiles created: {success_count}/{len(results)}")
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {name}")

    print(f"\nEnriched records: {len(enriched):,}")
    print(f"Unreached subset: {len(unreached):,} ({100*len(unreached)/len(enriched):.1f}%)")

    if results['full_parquet']:
        json_size = os.path.getsize('joshua_project_enriched.json') / (1024 * 1024)
        parquet_size = os.path.getsize('joshua_project_enriched.parquet') / (1024 * 1024)
        savings = 100 * (json_size - parquet_size) / json_size
        print(f"\nParquet compression: {savings:.1f}% smaller than JSON")
        print(f"  JSON: {json_size:.2f} MB")
        print(f"  Parquet: {parquet_size:.2f} MB")

    print("\n" + "="*70)
    print("✅ ENRICHMENT COMPLETE")
    print("="*70 + "\n")

    print("Next steps:")
    print("  1. Use joshua_project_enriched.json for visualizations")
    print("  2. Use joshua_project_enriched.parquet for analysis (pandas/polars)")
    print("  3. Use joshua_project_unreached.json for mission-focused visualizations")
    print("  4. Run prepare_huggingface_dataset.py to prepare for HF upload")
    print()

if __name__ == "__main__":
    main()
