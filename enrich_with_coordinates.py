#!/usr/bin/env python3
"""
Joshua Project Geographic Enrichment
Enriches Joshua Project datasets with geographic coordinates.

Merges:
1. People groups with country centroids (via ISO country codes)
2. Languages with Glottolog coordinates (via ISO 639-3 codes)

Creates valuable IP: Comprehensive people group + language data with full geographic coverage.

Usage:
    python3 enrich_with_coordinates.py

Output:
    - joshua_project_enriched_geo.json
    - joshua_project_languages_enriched_geo.json
    - enrichment_metadata.json
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Configuration
BASE_DIR = Path(__file__).parent.parent
JOSHUA_DIR = Path(__file__).parent
GEOGRAPHIC_DIR = BASE_DIR / 'data' / 'geographic'
LINGUISTIC_DIR = BASE_DIR / 'data' / 'linguistic'

def load_data():
    """Load all required datasets."""
    print("=" * 70)
    print("JOSHUA PROJECT GEOGRAPHIC ENRICHMENT")
    print("=" * 70)
    print("\n📂 Loading datasets...")

    # Load Joshua Project data
    with open(JOSHUA_DIR / 'joshua_project_full_dump.json') as f:
        people_groups = json.load(f)
    print(f"   ✓ Loaded {len(people_groups):,} people groups")

    with open(JOSHUA_DIR / 'joshua_project_languages.json') as f:
        languages = json.load(f)
    print(f"   ✓ Loaded {len(languages):,} languages")

    with open(JOSHUA_DIR / 'joshua_project_countries.json') as f:
        countries_jp = json.load(f)
    print(f"   ✓ Loaded {len(countries_jp):,} countries (Joshua Project)")

    # Load geographic data
    with open(GEOGRAPHIC_DIR / 'country_centroids.json') as f:
        centroids = json.load(f)
    print(f"   ✓ Loaded {len(centroids):,} country centroids (Natural Earth)")

    # Load Glottolog coordinates
    with open(LINGUISTIC_DIR / 'glottolog_coordinates.json') as f:
        glottolog = json.load(f)
    print(f"   ✓ Loaded {len(glottolog):,} language coordinates (Glottolog)")

    # Load Glottolog languoid data for family lookup
    glottolog_languoid_path = LINGUISTIC_DIR / 'glottolog_languoid.csv'
    glottolog_languoid = pd.read_csv(glottolog_languoid_path)
    print(f"   ✓ Loaded {len(glottolog_languoid):,} Glottolog languoid entries")

    # Load ISO 639-3 codes for reference
    with open(LINGUISTIC_DIR / 'iso_639_3.json') as f:
        iso_codes = json.load(f)
    print(f"   ✓ Loaded {len(iso_codes):,} ISO 639-3 language codes")

    return people_groups, languages, countries_jp, centroids, glottolog, glottolog_languoid, iso_codes

def build_lookup_tables(centroids, glottolog, glottolog_languoid):
    """Build fast lookup dictionaries for matching."""
    print("\n🔍 Building lookup tables...")

    # Country centroids by ISO code
    centroid_lookup = {}
    for country in centroids:
        iso_a2 = country.get('iso_a2')
        iso_a3 = country.get('iso_a3')
        if iso_a2:
            centroid_lookup[iso_a2] = country
        if iso_a3:
            centroid_lookup[iso_a3] = country

    print(f"   ✓ Indexed {len(centroid_lookup)} country codes")

    # Glottolog by ISO code (one-to-many - language can have multiple dialects)
    glottolog_lookup = {}
    for lang in glottolog:
        iso_codes = str(lang.get('isocodes', '')).strip()
        if iso_codes and iso_codes != 'nan':
            # Handle comma-separated codes
            for code in iso_codes.split(','):
                code = code.strip()
                if code:
                    if code not in glottolog_lookup:
                        glottolog_lookup[code] = []
                    glottolog_lookup[code].append(lang)

    print(f"   ✓ Indexed {len(glottolog_lookup)} ISO language codes")

    # Build family lookup dictionaries from glottolog_languoid
    family_lookup = {}  # family_id → family_name
    glottocode_to_family = {}  # glottocode → family_id

    for _, row in glottolog_languoid.iterrows():
        if row['level'] == 'family':
            family_lookup[row['id']] = row['name']
        if pd.notna(row['family_id']):
            glottocode_to_family[row['id']] = row['family_id']

    print(f"   ✓ Indexed {len(family_lookup)} language families")
    print(f"   ✓ Mapped {len(glottocode_to_family)} glottocodes to families")

    return centroid_lookup, glottolog_lookup, family_lookup, glottocode_to_family

def enrich_people_groups(people_groups, centroid_lookup):
    """Enrich people groups with country centroids."""
    print("\n🌍 Enriching people groups with coordinates...")

    enriched = []
    matched = 0
    unmatched_countries = set()

    for pg in people_groups:
        pg_enriched = pg.copy()

        # Get country code (ROG3 is 3-letter ISO code)
        country_code = pg.get('ROG3', '')

        if country_code in centroid_lookup:
            centroid = centroid_lookup[country_code]
            pg_enriched['country_latitude'] = centroid['latitude']
            pg_enriched['country_longitude'] = centroid['longitude']
            pg_enriched['continent'] = centroid.get('continent', '')
            pg_enriched['region_un'] = centroid.get('region_un', '')
            pg_enriched['coordinate_source'] = 'Natural Earth (country centroid)'
            matched += 1
        else:
            pg_enriched['country_latitude'] = None
            pg_enriched['country_longitude'] = None
            pg_enriched['continent'] = None
            pg_enriched['region_un'] = None
            pg_enriched['coordinate_source'] = None
            if country_code:
                unmatched_countries.add(country_code)

        enriched.append(pg_enriched)

    match_rate = 100 * matched / len(people_groups)
    print(f"   ✓ Matched {matched:,} / {len(people_groups):,} ({match_rate:.1f}%)")

    if unmatched_countries:
        print(f"   ⚠ {len(unmatched_countries)} unmatched country codes: {sorted(unmatched_countries)[:10]}")

    return enriched

def enrich_languages(languages, glottolog_lookup, family_lookup, glottocode_to_family):
    """Enrich Joshua Project languages with Glottolog coordinates."""
    print("\n🗣️ Enriching languages with coordinates...")

    enriched = []
    matched = 0
    unmatched_iso_codes = set()

    for lang in languages:
        lang_enriched = lang.copy()

        # Get ISO 639-3 code (ROL3)
        iso_code = lang.get('ROL3', '')

        if iso_code and iso_code in glottolog_lookup:
            # Get first Glottolog entry (usually the main language)
            glotto_entries = glottolog_lookup[iso_code]
            glotto = glotto_entries[0]  # Take first match

            # Convert NaN to None for proper JSON null
            lat = glotto.get('latitude')
            lng = glotto.get('longitude')
            lang_enriched['latitude'] = None if pd.isna(lat) else lat
            lang_enriched['longitude'] = None if pd.isna(lng) else lng

            glottocode = glotto.get('glottocode', '')
            lang_enriched['glottocode'] = glottocode

            # Get family name via 2-step lookup: glottocode → family_id → family_name
            if glottocode and glottocode in glottocode_to_family:
                family_id = glottocode_to_family[glottocode]
                family_name = family_lookup.get(family_id, '')
                lang_enriched['family_name'] = family_name
                lang_enriched['family_id'] = family_id
            else:
                # Fallback: check if this IS a family-level entry
                if glottocode and glottocode in family_lookup:
                    lang_enriched['family_name'] = family_lookup[glottocode]
                    lang_enriched['family_id'] = glottocode
                else:
                    lang_enriched['family_name'] = 'Isolate' if glottocode else ''
                    lang_enriched['family_id'] = ''

            lang_enriched['macroarea'] = glotto.get('macroarea', '')
            lang_enriched['coordinate_source'] = 'Glottolog'
            lang_enriched['glottolog_match_count'] = len(glotto_entries)
            matched += 1
        else:
            lang_enriched['latitude'] = None
            lang_enriched['longitude'] = None
            lang_enriched['glottocode'] = None
            lang_enriched['family_name'] = None
            lang_enriched['family_id'] = None
            lang_enriched['macroarea'] = None
            lang_enriched['coordinate_source'] = None
            lang_enriched['glottolog_match_count'] = 0
            if iso_code:
                unmatched_iso_codes.add(iso_code)

        enriched.append(lang_enriched)

    match_rate = 100 * matched / len(languages)
    print(f"   ✓ Matched {matched:,} / {len(languages):,} ({match_rate:.1f}%)")

    if unmatched_iso_codes:
        print(f"   ⚠ {len(unmatched_iso_codes)} unmatched ISO codes (sample): {sorted(unmatched_iso_codes)[:10]}")

    return enriched

def save_enriched_data(people_groups_enriched, languages_enriched):
    """Save enriched datasets."""
    print("\n💾 Saving enriched datasets...")

    # Save people groups
    pg_file = JOSHUA_DIR / 'joshua_project_enriched_geo.json'
    with open(pg_file, 'w', encoding='utf-8') as f:
        json.dump(people_groups_enriched, f, indent=2, ensure_ascii=False)

    file_size_mb = pg_file.stat().st_size / (1024 * 1024)
    print(f"   ✓ People groups: {pg_file}")
    print(f"     Size: {file_size_mb:.1f} MB")

    # Save languages
    lang_file = JOSHUA_DIR / 'joshua_project_languages_enriched_geo.json'
    with open(lang_file, 'w', encoding='utf-8') as f:
        json.dump(languages_enriched, f, indent=2, ensure_ascii=False)

    file_size_mb = lang_file.stat().st_size / (1024 * 1024)
    print(f"   ✓ Languages: {lang_file}")
    print(f"     Size: {file_size_mb:.1f} MB")

    # Count coordinates
    pg_with_coords = sum(1 for pg in people_groups_enriched if pg.get('country_latitude'))
    lang_with_coords = sum(1 for lang in languages_enriched if lang.get('latitude'))

    # Create metadata
    metadata = {
        'enrichment_date': datetime.now().isoformat(),
        'source_datasets': {
            'joshua_project': 'Joshua Project API v1',
            'natural_earth': 'Natural Earth 1:10m Admin 0 Label Points',
            'glottolog': 'Glottolog languages_and_dialects_geo.csv'
        },
        'people_groups': {
            'total': len(people_groups_enriched),
            'with_coordinates': pg_with_coords,
            'coverage': f'{100 * pg_with_coords / len(people_groups_enriched):.1f}%'
        },
        'languages': {
            'total': len(languages_enriched),
            'with_coordinates': lang_with_coords,
            'coverage': f'{100 * lang_with_coords / len(languages_enriched):.1f}%'
        },
        'new_fields': {
            'people_groups': ['country_latitude', 'country_longitude', 'continent', 'region_un', 'coordinate_source'],
            'languages': ['latitude', 'longitude', 'glottocode', 'family_name', 'family_id', 'macroarea', 'coordinate_source', 'glottolog_match_count']
        },
        'license': 'Compiled dataset - see individual source licenses',
        'description': 'Joshua Project data enriched with geographic coordinates from Natural Earth and Glottolog'
    }

    meta_file = JOSHUA_DIR / 'enrichment_metadata.json'
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"   ✓ Metadata: {meta_file}")

    return metadata

def print_summary(metadata):
    """Print summary statistics."""
    print("\n" + "=" * 70)
    print("ENRICHMENT SUMMARY")
    print("=" * 70)

    print(f"\n📊 People Groups:")
    print(f"   Total: {metadata['people_groups']['total']:,}")
    print(f"   With coordinates: {metadata['people_groups']['with_coordinates']:,}")
    print(f"   Coverage: {metadata['people_groups']['coverage']}")

    print(f"\n🗣️ Languages:")
    print(f"   Total: {metadata['languages']['total']:,}")
    print(f"   With coordinates: {metadata['languages']['with_coordinates']:,}")
    print(f"   Coverage: {metadata['languages']['coverage']}")

    print("\n✨ New Fields Added:")
    print(f"   People groups: {', '.join(metadata['new_fields']['people_groups'])}")
    print(f"   Languages: {', '.join(metadata['new_fields']['languages'])}")

    print("\n" + "=" * 70)
    print("✅ Geographic enrichment complete!")
    print("=" * 70)

def main():
    """Main execution function."""
    try:
        # Load all data
        people_groups, languages, countries_jp, centroids, glottolog, glottolog_languoid, iso_codes = load_data()

        # Build lookup tables
        centroid_lookup, glottolog_lookup, family_lookup, glottocode_to_family = build_lookup_tables(centroids, glottolog, glottolog_languoid)

        # Enrich datasets
        people_groups_enriched = enrich_people_groups(people_groups, centroid_lookup)
        languages_enriched = enrich_languages(languages, glottolog_lookup, family_lookup, glottocode_to_family)

        # Save results
        metadata = save_enriched_data(people_groups_enriched, languages_enriched)

        # Print summary
        print_summary(metadata)

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
