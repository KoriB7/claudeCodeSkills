#!/usr/bin/env python3
"""
Energize Denver Advanced Benchmark Calculator

Multi-factor energy benchmarking using CBECS 2018 data.
Supports optional refinement by year built, region/climate, floors, and operating hours.

Usage:
    # Basic (size + type)
    python calculate_advanced.py --sqft 25000 --type "Office"

    # With year
    python calculate_advanced.py --sqft 25000 --type "Office" --year "1980 to 1989"

    # Full refinement
    python calculate_advanced.py --sqft 25000 --type "Office" --year "1980 to 1989" \
                                  --region "Mountain" --floors 3 --hours "50 to 99"
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


def find_floors_range(floors):
    """Find the appropriate floor count range."""
    if floors == 1:
        return "1"
    elif floors == 2:
        return "2"
    elif floors == 3:
        return "3"
    elif floors <= 9:
        return "4 to 9"
    else:
        return "10 or more"


def find_hours_range(hours):
    """Find the appropriate weekly hours range."""
    if hours < 5:
        return "Fewer than 5"
    elif hours <= 9:
        return "5 to 9"
    elif hours <= 19:
        return "10 to 19"
    elif hours <= 49:
        return "20 to 49"
    elif hours <= 99:
        return "50 to 99"
    elif hours <= 249:
        return "100 to 249"
    else:
        return "250 or more"


def load_data():
    """Load all CBECS lookup tables."""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"

    data = {
        'size': pd.read_csv(data_dir / "cbecs_by_size.csv"),
        'type': pd.read_csv(data_dir / "cbecs_by_type.csv"),
        'year': pd.read_csv(data_dir / "cbecs_by_year.csv"),
        'region': pd.read_csv(data_dir / "cbecs_by_region_climate.csv"),
        'floors': pd.read_csv(data_dir / "cbecs_by_floors.csv"),
        'hours': pd.read_csv(data_dir / "cbecs_by_hours.csv")
    }

    # Clean category names
    for df in data.values():
        df['Category'] = df['Category'].str.strip()

    return data


def lookup_value(df, category_value, factor_name):
    """Look up energy intensity values by category."""
    # Try exact match
    row = df[df['Category'].str.lower() == str(category_value).lower()]

    if row.empty:
        # Try partial match
        row = df[df['Category'].str.lower().str.contains(str(category_value).lower(), na=False)]

    if row.empty:
        print(f"ERROR: '{category_value}' not found in {factor_name}")
        print(f"\nAvailable values:")
        for val in df['Category']:
            print(f"  - {val}")
        return None

    if len(row) > 1:
        print(f"WARNING: Multiple matches for '{category_value}' in {factor_name}. Using: {row.iloc[0]['Category']}")

    return row.iloc[0]


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


def calculate_averages(factor_rows):
    """Calculate averages across all provided factors."""
    if not factor_rows:
        print("ERROR: No valid factors to average")
        return None

    avg_row = {'Category': 'AVERAGE (AUDIT)'}

    # Get column names from first row
    first_row = factor_rows[0]

    for col in first_row.index:
        if col == 'Category':
            continue

        values = []
        for row in factor_rows:
            try:
                val = float(row[col])
                values.append(val)
            except (ValueError, TypeError):
                # Skip Q or non-numeric values
                pass

        if values:
            avg_row[col] = round(sum(values) / len(values), 2)
        else:
            avg_row[col] = "Q"

    return pd.Series(avg_row)


def format_output_table(factor_rows, factor_names, avg_row, basic_avg, sqft, building_name=None, building_address=None):
    """Format the output as a readable table with comparison."""
    output = []

    # Header
    if building_name:
        output.append(f"Building: {building_name}")
    if building_address:
        output.append(f"Address: {building_address}")
    output.append(f"Size: {sqft:,} sqft")
    output.append(f"Type: {factor_rows[1]['Category'] if len(factor_rows) > 1 else 'N/A'}")
    output.append("")

    # Factors used
    output.append(f"Refinement Factors Used: {len(factor_rows)}")
    for i, name in enumerate(factor_names):
        if i < len(factor_rows):
            output.append(f"  - {name}: {factor_rows[i]['Category']}")
    output.append("")
    output.append("Energy Use Intensity (kBtu/sqft):")
    output.append("")

    # Add each factor row with its percentage
    for i, row in enumerate(factor_rows):
        row_data = row.drop('Category')
        row_df = pd.DataFrame([row_data])
        row_df.insert(0, 'Source', [f"{factor_names[i]} ({row['Category']})"])

        if i == 0:
            output.append(row_df.to_string(index=False))
        else:
            output.append(row_df.to_string(index=False, header=False))

        # Add percentage row
        row_pct = calculate_percentages(row)
        if row_pct:
            row_pct['Source'] = 'Percentage (%)'
            pct_df = pd.DataFrame([row_pct])
            output.append(pct_df.to_string(index=False, header=False))
        output.append("")

    # Add separator before average
    output.append("-" * 80)

    # Add average row
    avg_data = avg_row.drop('Category')
    avg_df = pd.DataFrame([avg_data])
    avg_df.insert(0, 'Source', ['AVERAGE (AUDIT)'])
    output.append(avg_df.to_string(index=False, header=False))

    # Add average percentage row
    avg_pct = calculate_percentages(avg_row)
    if avg_pct:
        avg_pct['Source'] = 'Percentage (%)'
        pct_df = pd.DataFrame([avg_pct])
        output.append(pct_df.to_string(index=False, header=False))

    # Add comparison if basic method provided
    if basic_avg is not None:
        output.append("")
        output.append("Comparison to Basic Method (Size + Type only):")
        basic_df = pd.DataFrame([basic_avg])
        basic_df = basic_df.drop(columns=['Category'])
        basic_df.insert(0, 'Source', ['Basic Method'])
        output.append(basic_df.to_string(index=False, header=False))

        # Calculate difference
        diff_row = {'Source': 'Difference'}
        for col in avg_row.index:
            if col == 'Category':
                continue
            try:
                diff = float(avg_row[col]) - float(basic_avg[col])
                diff_row[col] = f"{diff:+.2f}"
            except (ValueError, TypeError):
                diff_row[col] = "N/A"

        diff_df = pd.DataFrame([diff_row])
        output.append(diff_df.to_string(index=False, header=False))

    # Total annual energy
    output.append("")
    if avg_row['Total'] != "Q":
        total_annual = avg_row['Total'] * sqft
        output.append(f"Total Annual Energy Use: {total_annual:,.0f} kBtu ({avg_row['Total']} kBtu/sqft × {sqft:,} sqft)")
    else:
        output.append("Total Annual Energy Use: Data not available (Q)")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Advanced energy benchmarking with multi-factor refinement',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic (size + type)
  %(prog)s --sqft 25000 --type "Office"

  # With year built
  %(prog)s --sqft 25000 --type "Office" --year "1980 to 1989"

  # Full refinement
  %(prog)s --sqft 25000 --type "Office" --year "1980 to 1989" \\
           --region "Mountain" --floors 3 --hours 50
        """
    )

    # Required arguments
    parser.add_argument('--sqft', type=int, required=True, help='Building square footage')
    parser.add_argument('--type', required=True, help='Building type (e.g., Office, Retail, Warehouse)')

    # Optional refinement arguments
    parser.add_argument('--year', help='Year built range (e.g., "1980 to 1989", "Before 1920")')
    parser.add_argument('--region', help='Region or climate (e.g., "Mountain", "West", "Cool")')
    parser.add_argument('--floors', type=int, help='Number of floors (1, 2, 3, 4-9, 10+)')
    parser.add_argument('--hours', help='Weekly operating hours (number or range like "50 to 99")')

    # Building details
    parser.add_argument('--name', help='Building name (optional)')
    parser.add_argument('--address', help='Building address (optional)')

    args = parser.parse_args()

    # Load data
    print("Loading CBECS data...")
    data = load_data()

    # Build list of factors to look up
    factor_rows = []
    factor_names = []

    # 1. Size (required)
    size_range = find_size_range(args.sqft)
    size_row = lookup_value(data['size'], size_range, "Building Size")
    if size_row is None:
        sys.exit(1)
    factor_rows.append(size_row)
    factor_names.append("Building Size")

    # 2. Type (required)
    type_row = lookup_value(data['type'], args.type, "Building Type")
    if type_row is None:
        sys.exit(1)
    factor_rows.append(type_row)
    factor_names.append("Building Type")

    # Calculate basic average (size + type) for comparison
    basic_avg = calculate_averages([size_row, type_row])

    # 3. Year (optional)
    if args.year:
        year_row = lookup_value(data['year'], args.year, "Year Built")
        if year_row is not None:
            factor_rows.append(year_row)
            factor_names.append("Year Built")

    # 4. Region (optional)
    if args.region:
        region_row = lookup_value(data['region'], args.region, "Region/Climate")
        if region_row is not None:
            factor_rows.append(region_row)
            factor_names.append("Region/Climate")

    # 5. Floors (optional)
    if args.floors:
        floors_range = find_floors_range(args.floors)
        floors_row = lookup_value(data['floors'], floors_range, "Floor Count")
        if floors_row is not None:
            factor_rows.append(floors_row)
            factor_names.append("Floor Count")

    # 6. Hours (optional)
    if args.hours:
        # Check if it's a number or range string
        try:
            hours_num = int(args.hours)
            hours_range = find_hours_range(hours_num)
        except ValueError:
            hours_range = args.hours

        hours_row = lookup_value(data['hours'], hours_range, "Operating Hours")
        if hours_row is not None:
            factor_rows.append(hours_row)
            factor_names.append("Operating Hours")

    # Calculate averages
    print(f"Calculating average across {len(factor_rows)} factors...")
    avg_row = calculate_averages(factor_rows)

    if avg_row is None:
        sys.exit(1)

    # Format and print output
    print("\n" + "="*80)
    print(format_output_table(factor_rows, factor_names, avg_row, basic_avg, args.sqft, args.name, args.address))
    print("="*80)

    # Summary
    print(f"\nUsed {len(factor_rows)} factors for refined estimate")
    if len(factor_rows) > 2:
        try:
            basic_total = float(basic_avg['Total'])
            advanced_total = float(avg_row['Total'])
            diff_pct = ((advanced_total - basic_total) / basic_total) * 100
            print(f"Refinement adjusted estimate by {diff_pct:+.1f}% vs basic method")
        except (ValueError, TypeError):
            pass


if __name__ == "__main__":
    main()
