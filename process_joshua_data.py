import json
import os
import math

# Paths
INPUT_FILE = "joshua_project_full_dump.json"
OUTPUT_FILE = "../../souls_viz_data.json"

def process_data():
    print(f"Loading data from {INPUT_FILE}...")
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"Loaded {len(data)} records. Processing...")

    affinity_blocs = {}
    
    # We want to group by Affinity Bloc, then Region, then Country?
    # For the visualization, we need flat lists of people groups but grouped by Affinity Bloc for the "Cells" view.
    
    processed_groups = []
    
    for record in data:
        # Extract relevant fields
        peid = record.get("PeopleID3")
        name = record.get("PeopNameInCountry")
        bloc = record.get("AffinityBloc", "Unknown")
        pop = record.get("Population", 0)
        religion = record.get("PrimaryReligion", "Unknown")
        evangelical_pct = record.get("PercentEvangelical", 0)
        # JPS cale: 1=Unreached, 2=Minimally Reached, 3=Superficially Reached, 4=Partially Reached, 5=Significantly Reached
        status_raw = record.get("JPScale", 1) 
        
        # Normalize status (some might be strings or None)
        try:
            status = int(status_raw)
        except (ValueError, TypeError):
            status = 1
            
        lat = record.get("Latitude")
        lon = record.get("Longitude")
        country = record.get("Ctry", "Unknown")
        
        # Skip records with no population (optional, but good for vis)
        if pop is None: pop = 0
        if pop < 100: continue # Skip very small groups for noise reduction? Maybe keep them.
        
        # simplify religion string
        if not religion: religion = "Unknown"
        
        group_data = {
            "n": name,
            "b": bloc,
            "p": pop,
            "r": religion,
            "s": status, # 1-5 scale. 1 is unreached (dark/red).
            "e": float(evangelical_pct) if evangelical_pct else 0.0,
            "c": country,
            "ll": [lat, lon] if lat and lon else None,
            "l": record.get("PrimaryLanguageName", "Unknown")
        }
        
        processed_groups.append(group_data)
        
        # Aggregate stats per bloc
        if bloc not in affinity_blocs:
            affinity_blocs[bloc] = {"pop": 0, "groups": 0, "unreached_pop": 0}
        
        affinity_blocs[bloc]["pop"] += pop
        affinity_blocs[bloc]["groups"] += 1
        if status <= 1: # Unreached
             affinity_blocs[bloc]["unreached_pop"] += pop

    # Combine into final structure
    # We might want to sort affinity blocs by population to help layout
    
    # Sort groups by population descending for better rendering (draw big ones first or last?)
    # Actually for Voronoi, order doesn't equate to z-index exactly, but for list views it helps.
    processed_groups.sort(key=lambda x: x['p'], reverse=True)
    
    output_data = {
        "stats": affinity_blocs,
        "groups": processed_groups
    }

    print(f"Writing {len(processed_groups)} groups to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, separators=(',', ':')) # Minified
    
    print("Done.")

if __name__ == "__main__":
    process_data()
