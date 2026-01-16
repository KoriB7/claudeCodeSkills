---
name: energize-denver-audit
version: 1.0.0
description: Calculates estimated energy usage benchmarks for Energize Denver auditing using CBECS 2018 data. Takes building size and type, looks up benchmark values, averages them, and splits into usage categories (heating, cooling, ventilation, water heating, lighting, cooking, refrigeration, office equipment, computing, other). Use when benchmarking buildings for Energize Denver or working with CBECS data.
category: tool
allowed-tools: Read, Bash
---

# Energize Denver Audit Benchmarking

Calculates estimated energy usage for buildings using CBECS 2018 benchmarking data for Energize Denver auditing purposes.

## Quick Start

**Input required:**
- Building square footage
- Building type (e.g., Office, Retail, Warehouse, Food service, Education)

**Output:**
A 4-row table showing:
1. Total values with category breakdowns
2. Values based on building size lookup
3. Values based on building type lookup
4. **Average values (for auditing)** - average of rows 2 and 3

## How It Works

1. **Look up by size** - Find energy intensity (kBtu/sqft) in size range table
2. **Look up by type** - Find energy intensity (kBtu/sqft) for building type
3. **Calculate average** - `(size_value + type_value) / 2`
4. **Calculate total energy** - `average_kBtu_per_sqft × building_sqft`
5. **Split into categories** - Apply category breakdown percentages
6. **Generate table** - Create the 4-row output table

## Usage

### Manual Calculation

1. **Extract inputs**: Square footage, building type, name (optional), address (optional)

2. **Look up size-based values** in [data/cbecs_by_size.csv](data/cbecs_by_size.csv):
   - Find row matching building size range
   - Extract all 11 values (Total + 10 categories)

3. **Look up type-based values** in [data/cbecs_by_type.csv](data/cbecs_by_type.csv):
   - Find row matching building type
   - Extract all 11 values (Total + 10 categories)

4. **Calculate averages** for each column:
   ```
   average = (size_value + type_value) / 2
   ```

5. **Generate 4-row table**:
   - Row 1: Headers
   - Row 2: Size-based values
   - Row 3: Type-based values
   - Row 4: Averages (USE THIS FOR AUDITING)

### Automated Calculation

```bash
python scripts/calculate_benchmark.py --sqft 15000 --type "Office"
```

With building details:
```bash
python scripts/calculate_benchmark.py --sqft 15000 --type "Office" --name "Downtown Plaza" --address "123 Main St"
```

See [scripts/README.md](scripts/README.md) for script documentation.

## Output Format

```
Building: [Name]
Address: [Address]
Size: [sqft] sqft
Type: [Building Type]

Energy Use Intensity (kBtu/sqft):

                    Total  Space_Heating  Cooling  Ventilation  Water_Heating  Lighting  Cooking  Refrigeration  Office_Equipment  Computing  Other
Size-based:         59.5   23.6          6.2      5.0          2.8            6.1       10.1     4.2            0.6               3.1        10.4
Percentage (%)      100%   40%           10%      8%           5%             10%       17%      7%             1%                5%         17%
Type-based:         65.6   20.1          5.1      12.9         1.0            7.8       2.6      1.6            0.8               5.2        11.4
Percentage (%)      100%   31%           8%       20%          2%             12%       4%       2%             1%                8%         17%
AVERAGE (AUDIT):    62.55  21.85         5.65     8.95         1.90           6.95      6.35     2.90           0.70              4.15       10.90
Percentage (%)      100%   35%           9%       14%          3%             11%       10%      5%             1%                7%         17%

Total Annual Energy Use: [Total kBtu = Average Total × sqft]
```

## Options

### Supported Building Types

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

### Energy Categories

| Category | Description |
|----------|-------------|
| Space Heating | HVAC heating |
| Cooling | HVAC cooling |
| Ventilation | Air handling |
| Water Heating | Domestic hot water |
| Lighting | Interior/exterior |
| Cooking | Kitchen equipment |
| Refrigeration | Cold storage |
| Office Equipment | Copiers, printers |
| Computing | Servers, computers |
| Other | Miscellaneous |

## Example Usage

### Example 1: Simple Calculation

**Request**: "15,000 sqft office building for Energize Denver"

**Process**:
1. Look up "10,001 to 25,000" in cbecs_by_size.csv → Total: 59.5 kBtu/sqft
2. Look up "Office" in cbecs_by_type.csv → Total: 65.6 kBtu/sqft
3. Average: (59.5 + 65.6) / 2 = 62.55 kBtu/sqft
4. Present 4-row table

### Example 2: Batch Processing

**Request**: "Process 3 buildings: 8,500 sqft retail, 45,000 sqft warehouse, 120,000 sqft office"

**Process**: Run calculation for each building, generate combined or separate tables.

## Troubleshooting

**Building type not found:**
- Check spelling and capitalization
- Use exact names from "Supported Building Types"
- For edge cases, use "Other" category

**Size out of range:**
- Valid: 1,001 sqft to Over 500,000
- Under 1,001 sqft: use smallest bracket

**Missing data (Q values):**
- Some categories have withheld data
- Document as "Data not available (Q)"
- Consider "All buildings" average as fallback

## References

- Data: [data/cbecs_full.csv](data/cbecs_full.csv)
- Script: [scripts/calculate_benchmark.py](scripts/calculate_benchmark.py)
- CBECS 2018: https://www.eia.gov/consumption/commercial/data/2018/

## Notes

- All values in **kBtu/sqft** (thousand BTU per square foot)
- Data source: **CBECS 2018 Table E2** (U.S. Energy Information Administration)
- The **AVERAGE row** is what you use for Energize Denver auditing
- Size ranges defined by CBECS standard brackets
