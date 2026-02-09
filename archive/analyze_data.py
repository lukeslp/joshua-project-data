"""
File Purpose: Analyze and compare Joshua Project data files.
Primary Functions:
- Load CSV data into pandas DataFrames.
- Compare 'master' dataset (AllPeoplesInCountry.csv) with CPPI cross-reference dataset.
- Identify duplicates, unique records, and data discrepancies.
- Generate a summary report.
Inputs:
- /home/coolhand/html/datavis/joshua-project/AllPeoplesInCountry.csv
- /home/coolhand/html/datavis/joshua-project/extracted_cppi/jp-cppi-cross-reference.csv
Outputs:
- Printed summary of analysis.
- joshua_data_summary.md (Report file)
"""

import pandas as pd
import os

# Paths
BASE_DIR = "/home/coolhand/html/datavis/joshua-project"
MASTER_CSV = os.path.join(BASE_DIR, "AllPeoplesInCountry.csv")
CPPI_CSV = os.path.join(BASE_DIR, "extracted_cppi", "jp-cppi-cross-reference.csv")
OUTPUT_REPORT = os.path.join(BASE_DIR, "joshua_data_summary.md")

def load_data():
    """Load the CSV files into DataFrames."""
    print("Loading data...")
    try:
        # Load Master - Skip first 2 lines (Title + Blank)
        master_df = pd.read_csv(MASTER_CSV, encoding='utf-8', on_bad_lines='skip', skiprows=2)
        print(f"Loaded Master CSV: {len(master_df)} rows")
        
        # Load CPPI
        # CPPI might have encoding issues or whitespace in headers
        cppi_df = pd.read_csv(CPPI_CSV, encoding='latin1', on_bad_lines='skip') # Fallback encoding often needed
        print(f"Loaded CPPI CSV: {len(cppi_df)} rows")
        
        return master_df, cppi_df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

def clean_columns(df):
    """Strip whitespace from column names."""
    df.columns = df.columns.str.strip()
    return df

def analyze(master_df, cppi_df):
    """Compare the two DataFrames."""
    print("\nAnalyzing data...")
    
    # Clean headers
    master_df = clean_columns(master_df)
    cppi_df = clean_columns(cppi_df)
    
    # Check for keys
    join_keys = ['ROG3', 'PeopleID3']
    for key in join_keys:
        if key not in master_df.columns:
            print(f"Error: '{key}' not in Master.")
            return
        if key not in cppi_df.columns:
            print(f"Error: '{key}' not in CPPI.")
            return

    # Convert keys to string
    for key in join_keys:
        master_df[key] = master_df[key].astype(str).str.strip()
        cppi_df[key] = cppi_df[key].astype(str).str.strip()

    # Create a composite key for easier set operations
    master_df['KEY'] = master_df['ROG3'] + "_" + master_df['PeopleID3']
    cppi_df['KEY'] = cppi_df['ROG3'] + "_" + cppi_df['PeopleID3']

    # Sets of Keys
    master_keys = set(master_df['KEY'])
    cppi_keys = set(cppi_df['KEY'])
    
    # Intersections and differences
    common_keys = master_keys.intersection(cppi_keys)
    only_master_keys = master_keys - cppi_keys
    only_cppi_keys = cppi_keys - master_keys
    
    # Summarize findings
    summary = []
    summary.append("# Joshua Project Data Analysis Summary\n")
    summary.append(f"## Dataset Overview")
    summary.append(f"- **Master Dataset** (`AllPeoplesInCountry.csv`): {len(master_df)} records")
    summary.append(f"- **CPPI Cross-Ref** (`jp-cppi-cross-reference.csv`): {len(cppi_df)} records")
    
    summary.append(f"\n## Comparison by ROG3 + PeopleID3")
    summary.append(f"- **Common Records**: {len(common_keys)}")
    summary.append(f"- **Only in Master**: {len(only_master_keys)}")
    summary.append(f"- **Only in CPPI**: {len(only_cppi_keys)}")
    
    # Data Consistency Check (Population)
    summary.append(f"\n## Data Consistency (Common Records)")
    
    if 'Population' in master_df.columns and 'JPPopulation' in cppi_df.columns:
        # Merge on Keys
        merged = pd.merge(master_df, cppi_df, on=join_keys, suffixes=('_master', '_cppi'))
        
        def clean_pop(val):
            if isinstance(val, str):
                val = val.replace(',', '').strip()
                if val == '': return 0.0
                return float(val)
            return float(val)

        merged['Population_master'] = merged['Population'].apply(clean_pop)
        merged['JPPopulation_cppi'] = merged['JPPopulation'].apply(clean_pop)
        
        merged['diff'] = merged['Population_master'] - merged['JPPopulation_cppi']
        # Consider a match if difference is small (e.g. < 10) just in case
        exact_matches = merged[merged['diff'].abs() < 1]
        discrepancies = merged[merged['diff'].abs() >= 1]
        
        summary.append(f"- **Population Exact Matches**: {len(exact_matches)} / {len(merged)}")
        summary.append(f"- **Population Discrepancies**: {len(discrepancies)}")
        
        if not discrepancies.empty:
             summary.append(f"\n### Top 10 Population Discrepancies")
             name_col_master = 'PeopNameInCountry' if 'PeopNameInCountry' in master_df.columns else 'JPPeopleGroup_master'
             name_col_cppi = 'JPPeopleGroup' if 'JPPeopleGroup' in cppi_df.columns else 'JPPeopleGroup_cppi'
             
             summary.append(f"| ROG3 | PeopleID3 | Name | Pop (Master) | Pop (CPPI) | Diff |")
             summary.append("|---|---|---|---|---|---|")
             for _, row in discrepancies.sort_values('diff', key=abs, ascending=False).head(10).iterrows():
                 name = row.get(name_col_master, 'N/A')
                 summary.append(f"| {row['ROG3']} | {row['PeopleID3']} | {name} | {row['Population_master']:.0f} | {row['JPPopulation_cppi']:.0f} | {row['diff']:.0f} |")

    else:
        summary.append("- Could not compare population (missing columns).")

    # Write report
    with open(OUTPUT_REPORT, 'w') as f:
        f.write('\n'.join(summary))
    
    print('\n'.join(summary))
    print(f"\nReport saved to: {OUTPUT_REPORT}")

if __name__ == "__main__":
    m_df, c_df = load_data()
    if m_df is not None and c_df is not None:
        analyze(m_df, c_df)
