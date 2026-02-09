"""
Prepare compact visualization data for souls visualizations.
Converts enriched Joshua Project data into minimal format for browser use.

Output: souls_enhanced_viz_data.json
Size target: < 3 MB (compact field names, essential data only)
"""

import json
import sys
from pathlib import Path

# Compact field mapping
COMPACT_FIELDS = {
    'name': 'n',                    # People group name
    'population': 'p',              # Population
    'jp_scale': 's',                # JP Scale (1-5)
    'percent_evangelical': 'e',     # % Evangelical
    'primary_religion': 'r',        # Religion
    'primary_language': 'l',        # Language name
    'language_code': 'lc',          # ROL3 code
    'country': 'c',                 # Country name
    'country_code': 'cc',           # ROG3 code
    'continent': 'cn',              # Continent
    'region': 'rg',                 # Region
    'affinity_bloc': 'ab',          # Affinity Bloc
    'people_cluster': 'pc',         # People Cluster
    'bible_status': 'bs',           # Bible translation status
    'has_jesus_film': 'jf',         # Jesus Film Y/N
    'lat_lon': 'll',                # [lat, lng] if available
    'least_reached': 'lr'           # Y/N
}

def load_enriched_data():
    """Load the enriched Joshua Project dataset."""
    data_file = Path(__file__).parent / 'joshua_project_enriched.json'

    if not data_file.exists():
        print(f"Error: {data_file} not found")
        print("Run create_enriched_datasets.py first!")
        sys.exit(1)

    print(f"Loading {data_file.name}...")
    with open(data_file, 'r') as f:
        data = json.load(f)

    print(f"Loaded {len(data):,} people groups")
    return data

def safe_float(value, default=0.0):
    """Safely convert value to float."""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Safely convert value to int."""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def compact_group(group):
    """Convert a people group record to compact format."""
    compact = {
        'n': group.get('PeopNameInCountry', 'Unknown'),
        'p': safe_int(group.get('Population', 0)),
        's': safe_int(group.get('JPScale', 0)),
        'e': round(safe_float(group.get('PercentEvangelical', 0)), 1),
        'r': group.get('PrimaryReligion', 'Unknown'),
        'l': group.get('PrimaryLanguageName', 'Unknown'),
        'lc': group.get('ROL3', ''),
        'c': group.get('country_data', {}).get('name', 'Unknown') if group.get('country_data') else group.get('Ctry', 'Unknown'),
        'cc': group.get('ROG3', ''),
        'cn': group.get('Continent', ''),
        'rg': group.get('RegionName', ''),
        'ab': group.get('AffinityBloc', ''),
        'pc': group.get('PeopleCluster', ''),
        'bs': safe_int(group.get('BibleStatus', 0)),
        'jf': group.get('language_data', {}).get('has_jesus_film', 'N') if group.get('language_data') else 'N',
        'lr': group.get('LeastReached', 'N')
    }

    # Add lat/lon if available (some people groups have this)
    # Check common field names
    lat = group.get('Latitude') or group.get('PrimaryLanguageLatitude')
    lon = group.get('Longitude') or group.get('PrimaryLanguageLongitude')

    if lat and lon:
        lat_val = safe_float(lat, None)
        lon_val = safe_float(lon, None)
        if lat_val is not None and lon_val is not None and lat_val != 0 and lon_val != 0:
            compact['ll'] = [lat_val, lon_val]

    return compact

def generate_stats(groups):
    """Generate summary statistics."""
    stats = {
        'total_groups': len(groups),
        'total_population': sum(g['p'] for g in groups),
        'unreached_count': sum(1 for g in groups if g['lr'] == 'Y'),
        'unreached_population': sum(g['p'] for g in groups if g['lr'] == 'Y'),

        # By religion
        'by_religion': {},

        # By continent
        'by_continent': {},

        # By affinity bloc
        'by_affinity_bloc': {},

        # By JP Scale
        'by_jp_scale': {str(i): 0 for i in range(1, 6)},

        # By Bible status
        'by_bible_status': {str(i): 0 for i in range(0, 6)}
    }

    for g in groups:
        # Religion
        if g['r'] not in stats['by_religion']:
            stats['by_religion'][g['r']] = {'count': 0, 'population': 0, 'unreached': 0}
        stats['by_religion'][g['r']]['count'] += 1
        stats['by_religion'][g['r']]['population'] += g['p']
        if g['lr'] == 'Y':
            stats['by_religion'][g['r']]['unreached'] += g['p']

        # Continent
        if g['cn']:
            if g['cn'] not in stats['by_continent']:
                stats['by_continent'][g['cn']] = {'count': 0, 'population': 0}
            stats['by_continent'][g['cn']]['count'] += 1
            stats['by_continent'][g['cn']]['population'] += g['p']

        # Affinity Bloc
        if g['ab']:
            if g['ab'] not in stats['by_affinity_bloc']:
                stats['by_affinity_bloc'][g['ab']] = {'count': 0, 'population': 0}
            stats['by_affinity_bloc'][g['ab']]['count'] += 1
            stats['by_affinity_bloc'][g['ab']]['population'] += g['p']

        # JP Scale
        if g['s']:
            stats['by_jp_scale'][str(g['s'])] += 1

        # Bible Status
        if g['bs'] is not None:
            stats['by_bible_status'][str(g['bs'])] += 1

    return stats

def main():
    print("=" * 70)
    print("PREPARING SOULS VISUALIZATION DATA")
    print("=" * 70)

    # Load enriched data
    enriched = load_enriched_data()

    # Convert to compact format
    print("\nConverting to compact format...")
    compact_groups = []

    for i, group in enumerate(enriched):
        compact_groups.append(compact_group(group))

        if (i + 1) % 1000 == 0:
            print(f"  Progress: {i+1:,}/{len(enriched):,}")

    print(f"\n✅ Converted {len(compact_groups):,} groups")

    # Generate stats
    print("\nGenerating statistics...")
    stats = generate_stats(compact_groups)

    # Create output
    output = {
        'groups': compact_groups,
        'stats': stats,
        'generated': '2025-12-23',
        'source': 'Joshua Project API via enriched dataset'
    }

    # Save to souls directory
    output_file = Path(__file__).parent.parent.parent / 'poems' / 'souls' / 'souls_enhanced_viz_data.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nSaving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, separators=(',', ':'), ensure_ascii=False)

    # File size
    size_mb = output_file.stat().st_size / (1024 * 1024)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Output file: {output_file.name}")
    print(f"File size: {size_mb:.2f} MB")
    print(f"People groups: {len(compact_groups):,}")
    print(f"Total population: {stats['total_population']:,}")
    print(f"Unreached: {stats['unreached_count']:,} groups ({stats['unreached_population']:,} people)")
    print(f"\nReligions: {len(stats['by_religion'])}")
    print(f"Continents: {len(stats['by_continent'])}")
    print(f"Affinity Blocs: {len(stats['by_affinity_bloc'])}")
    print("\n" + "=" * 70)
    print("✅ COMPLETE - Ready for visualization!")
    print("=" * 70)

if __name__ == '__main__':
    main()
