#!/usr/bin/env python3
"""
Energize Denver Benchmark Calculator

Calculates estimated energy usage benchmarks using CBECS 2018 data.
Takes building size and type, looks up values, averages them, and generates output table.

Usage:
    python calculate_benchmark.py --sqft 15000 --type "Office"
    python calculate_benchmark.py --sqft 15000 --type "Office" --name "Downtown Plaza" --address "123 Main St"
"""

import argparse
import pandas as pd
import sys
from pathlib import Path


def find_size_range(sqft):
    """Find the appropriate size range for the given square footage."""
    if sqft <= 5000:
        return "1,001 to 5,000"
    elif sqft <= 10000:
        return "5,001 to 10,000"
    elif sqft <= 25000:
        return "10,001 to 25,000"
    elif sqft <= 50000:
        return "25,001 to 50,000"
    elif sqft <= 100000:
        return "50,001 to 100,000"
    elif sqft <= 200000:
        return "100,001 to 200,000"
    elif sqft <= 500000:
        return "200,001 to 500,000"
    else:
        return "Over 500,000"


def load_data():
    """Load the CBECS lookup tables."""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"

    size_df = pd.read_csv(data_dir / "cbecs_by_size.csv")
    type_df = pd.read_csv(data_dir / "cbecs_by_type.csv")

    # Clean category names
    size_df['Category'] = size_df['Category'].str.strip()
    type_df['Category'] = type_df['Category'].str.strip()

    return size_df, type_df


def lookup_by_size(size_df, sqft):
    """Look up energy intensity values by building size."""
    size_range = find_size_range(sqft)
    row = size_df[size_df['Category'] == size_range]

    if row.empty:
        print(f"ERROR: Size range '{size_range}' not found in data")
        sys.exit(1)

    return row.iloc[0]


def lookup_by_type(type_df, building_type):
    """Look up energy intensity values by building type."""
    # Try exact match first
    row = type_df[type_df['Category'].str.lower() == building_type.lower()]

    if row.empty:
        # Try partial match
        row = type_df[type_df['Category'].str.lower().str.contains(building_type.lower())]

    if row.empty:
        print(f"ERROR: Building type '{building_type}' not found")
        print("\nAvailable building types:")
        for btype in type_df['Category']:
            print(f"  - {btype}")
        sys.exit(1)

    if len(row) > 1:
        print(f"WARNING: Multiple matches found for '{building_type}'. Using first match: {row.iloc[0]['Category']}")

    return row.iloc[0]


def calculate_averages(size_row, type_row):
    """Calculate averages between size-based and type-based values."""
    avg_row = {}

    # Get all numeric columns (Total and all categories)
    for col in size_row.index:
        if col == 'Category':
            avg_row[col] = "AVERAGE (AUDIT)"
            continue

        try:
            size_val = float(size_row[col])
            type_val = float(type_row[col])
            avg_row[col] = round((size_val + type_val) / 2, 2)
        except (ValueError, TypeError):
            # Handle "Q" or other non-numeric values
            avg_row[col] = "Q"

    return pd.Series(avg_row)


def calculate_percentages(row):
    """Calculate percentage of each category from total."""
    pct_row = {}
    total_value = row['Total']

    if total_value == "Q" or total_value <= 0:
        return None

    for col in row.index:
        if col == 'Category':
            continue
        if col == 'Total':
            pct_row[col] = '100%'
        else:
            try:
                val = float(row[col])
                pct = (val / total_value) * 100
                pct_row[col] = f"{pct:.0f}%"
            except (ValueError, TypeError):
                pct_row[col] = "N/A"

    return pct_row


def format_output_table(size_row, type_row, avg_row, sqft, building_name=None, building_address=None):
    """Format the output as a readable table."""
    output = []

    # Header
    if building_name:
        output.append(f"Building: {building_name}")
    if building_address:
        output.append(f"Address: {building_address}")
    output.append(f"Size: {sqft:,} sqft")
    output.append(f"Type: {type_row['Category']}")
    output.append("")
    output.append("Energy Use Intensity (kBtu/sqft):")
    output.append("")

    # Size-based row and percentage
    size_data = size_row.drop('Category')
    size_df = pd.DataFrame([size_data])
    size_df.insert(0, 'Source', [f"Size-based ({size_row['Category']})"])
    output.append(size_df.to_string(index=False))

    size_pct = calculate_percentages(size_row)
    if size_pct:
        size_pct['Source'] = 'Percentage (%)'
        pct_df = pd.DataFrame([size_pct])
        output.append(pct_df.to_string(index=False, header=False))
    output.append("")

    # Type-based row and percentage
    type_data = type_row.drop('Category')
    type_df = pd.DataFrame([type_data])
    type_df.insert(0, 'Source', [f"Type-based ({type_row['Category']})"])
    output.append(type_df.to_string(index=False, header=False))

    type_pct = calculate_percentages(type_row)
    if type_pct:
        type_pct['Source'] = 'Percentage (%)'
        pct_df = pd.DataFrame([type_pct])
        output.append(pct_df.to_string(index=False, header=False))
    output.append("")

    # Average row and percentage
    avg_data = avg_row.drop('Category')
    avg_df = pd.DataFrame([avg_data])
    avg_df.insert(0, 'Source', ['AVERAGE (AUDIT)'])
    output.append(avg_df.to_string(index=False, header=False))

    avg_pct = calculate_percentages(avg_row)
    if avg_pct:
        avg_pct['Source'] = 'Percentage (%)'
        pct_df = pd.DataFrame([avg_pct])
        output.append(pct_df.to_string(index=False, header=False))

    # Calculate total annual energy
    output.append("")
    if avg_row['Total'] != "Q":
        total_annual = avg_row['Total'] * sqft
        output.append(f"Total Annual Energy Use: {total_annual:,.0f} kBtu ({avg_row['Total']} kBtu/sqft × {sqft:,} sqft)")
    else:
        output.append("Total Annual Energy Use: Data not available (Q)")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='Calculate energy benchmarks for Energize Denver auditing')
    parser.add_argument('--sqft', type=int, required=True, help='Building square footage')
    parser.add_argument('--type', required=True, help='Building type (e.g., Office, Retail, Warehouse)')
    parser.add_argument('--name', help='Building name (optional)')
    parser.add_argument('--address', help='Building address (optional)')

    args = parser.parse_args()

    # Load data
    print("Loading CBECS data...")
    size_df, type_df = load_data()

    # Look up values
    print(f"Looking up values for {args.sqft:,} sqft {args.type}...")
    size_row = lookup_by_size(size_df, args.sqft)
    type_row = lookup_by_type(type_df, args.type)

    # Calculate averages
    avg_row = calculate_averages(size_row, type_row)

    # Format and print output
    print("\n" + "="*80)
    print(format_output_table(size_row, type_row, avg_row, args.sqft, args.name, args.address))
    print("="*80)


if __name__ == "__main__":
    main()
