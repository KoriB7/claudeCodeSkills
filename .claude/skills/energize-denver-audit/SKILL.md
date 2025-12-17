---
name: energize-denver-audit
description: Calculate estimated energy usage benchmarks for Energize Denver auditing using CBECS 2018 data. Takes building size and type, looks up benchmark values from both size and type tables, averages them, and splits into usage categories (space heating, cooling, ventilation, water heating, lighting, cooking, refrigeration, office equipment, computing, other). Generates formatted output table. Use when benchmarking buildings for Energize Denver, calculating estimated energy usage, or working with CBECS data.
---

# Energize Denver Audit Benchmarking

This skill automates the process of calculating estimated energy usage for buildings using CBECS 2018 benchmarking data for Energize Denver auditing purposes.

## Quick Start

**Input required:**
- Building square footage
- Building type (e.g., Office, Retail, Warehouse, Food service, Education, etc.)

**Output:**
A 4-row table showing:
1. Total values with category breakdowns
2. Values based on building size lookup
3. Values based on building type lookup
4. **Average values (for auditing)** - average of rows 2 and 3

## Process Overview

The skill follows this workflow:

1. **Look up by size**: Find energy intensity (kBtu/sqft) in the size range table
2. **Look up by type**: Find energy intensity (kBtu/sqft) for the building type
3. **Calculate average**: `(size_value + type_value) / 2`
4. **Calculate total energy**: `average_kBtu_per_sqft × building_sqft`
5. **Split into categories**: Apply the category breakdown percentages
6. **Generate table**: Create the 4-row output table

## Energy Categories

The breakdown includes these 10 categories:
- Space Heating (kBtu/sqft)
- Cooling (kBtu/sqft)
- Ventilation (kBtu/sqft)
- Water Heating (kBtu/sqft)
- Lighting (kBtu/sqft)
- Cooking (kBtu/sqft)
- Refrigeration (kBtu/sqft)
- Office Equipment (kBtu/sqft)
- Computing (kBtu/sqft)
- Other (kBtu/sqft)

## Data Sources

All lookup tables are stored in the [data/](data/) directory:
- **cbecs_by_size.csv** - Energy intensity values by building size ranges
- **cbecs_by_type.csv** - Energy intensity values by building type
- **cbecs_full.csv** - Complete CBECS 2018 Table E2 dataset

## Manual Calculation Steps

When the user provides building information:

1. **Extract the inputs**:
   - Building square footage
   - Building type
   - Building name (optional, for labeling)
   - Address (optional, for labeling)

2. **Look up size-based values**:
   - Open [data/cbecs_by_size.csv](data/cbecs_by_size.csv)
   - Find the row matching the building size range
   - Extract all 11 values (Total + 10 categories)

3. **Look up type-based values**:
   - Open [data/cbecs_by_type.csv](data/cbecs_by_type.csv)
   - Find the row matching the building type
   - Extract all 11 values (Total + 10 categories)

4. **Calculate averages**:
   - For each column (Total and each category):
     ```
     average = (size_value + type_value) / 2
     ```

5. **Generate the 4-row table**:
   ```
   Row 1: Headers (Total, Space Heating, Cooling, etc.)
   Row 2: Size-based values
   Row 3: Type-based values
   Row 4: Averages (THIS IS WHAT YOU USE FOR AUDITING)
   ```

## Automated Calculation

For faster processing, you can use the automation script:

```bash
python scripts/calculate_benchmark.py --sqft 15000 --type "Office"
```

Or with building details:
```bash
python scripts/calculate_benchmark.py --sqft 15000 --type "Office" --name "Downtown Plaza" --address "123 Main St"
```

See [scripts/README.md](scripts/README.md) for script documentation.

## Supported Building Types

The following building types are available in the CBECS dataset:
- Education
- Food sales
- Food service
- Health care
- Inpatient
- Outpatient
- Lodging
- Mercantile
- Retail (other than mall)
- Enclosed and strip malls
- Office
- Public assembly
- Public order and safety
- Religious worship
- Service
- Warehouse and storage
- Other
- Vacant

## Example Usage

### Example 1: Simple Calculation

**User request:**
"I have a 15,000 sqft office building. Calculate the benchmark for Energize Denver."

**Your process:**
1. Look up "10,001 to 25,000" range in cbecs_by_size.csv
   - Total: 59.5 kBtu/sqft
   - Space Heating: 23.6, Cooling: 6.2, Ventilation: 5.0, etc.

2. Look up "Office" in cbecs_by_type.csv
   - Total: 65.6 kBtu/sqft
   - Space Heating: 20.1, Cooling: 5.1, Ventilation: 12.9, etc.

3. Calculate averages:
   - Total: (59.5 + 65.6) / 2 = 62.55 kBtu/sqft
   - Space Heating: (23.6 + 20.1) / 2 = 21.85 kBtu/sqft
   - Cooling: (6.2 + 5.1) / 2 = 5.65 kBtu/sqft
   - Continue for all categories...

4. Present 4-row table with size values, type values, and averages

### Example 2: Batch Processing

**User request:**
"Process these 3 buildings:
- Building A: 8,500 sqft retail
- Building B: 45,000 sqft warehouse
- Building C: 120,000 sqft office"

**Your process:**
Run the calculation for each building and generate a combined output table or three separate tables.

## Output Format

The standard output is a table like this:

```
Building: [Name]
Address: [Address]
Size: [sqft] sqft
Type: [Building Type]

Energy Use Intensity (kBtu/sqft):

                    Total  Space_Heating  Cooling  Ventilation  Water_Heating  Lighting  Cooking  Refrigeration  Office_Equipment  Computing  Other
Size-based:         59.5   23.6          6.2      5.0          2.8            6.1       10.1     4.2            0.6               3.1        10.4
Type-based:         65.6   20.1          5.1      12.9         1.0            7.8       2.6      1.6            0.8               5.2        11.4
AVERAGE (AUDIT):    62.55  21.85         5.65     8.95         1.90           6.95      6.35     2.90           0.70              4.15       10.90

Total Annual Energy Use: [Total kBtu = Average Total × sqft]
```

## Notes

- All values are in **kBtu/sqft** (thousand BTU per square foot)
- Data source: **CBECS 2018 Table E2** (U.S. Energy Information Administration)
- Some building types may have missing data marked as "Q" (withheld due to high standard error)
- The **AVERAGE row** is what you use for Energize Denver auditing purposes
- Size ranges are defined by CBECS standard brackets

## Troubleshooting

**Building type not found:**
- Check spelling and capitalization
- Use exact names from "Supported Building Types" section above
- For edge cases, use "Other" category

**Size out of range:**
- Valid ranges: 1,001 sqft to Over 500,000
- Buildings under 1,001 sqft: use smallest bracket

**Missing data (Q values):**
- Some categories have withheld data
- Document as "Data not available (Q)" in output
- Consider using "All buildings" average as fallback

## References

- Data file: [data/cbecs_full.csv](data/cbecs_full.csv)
- CBECS 2018 documentation: https://www.eia.gov/consumption/commercial/data/2018/
- Calculation script: [scripts/calculate_benchmark.py](scripts/calculate_benchmark.py)
