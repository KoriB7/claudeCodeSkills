---
name: energize-denver-advanced
version: 1.0.0
description: Calculates advanced energy benchmarks for Energize Denver using two-factor refinement (building size plus one other factor). Averages building size with type, year built, region/climate, floor count, or operating hours from CBECS 2018. Use when focusing on a specific building characteristic beyond just size and type.
category: tool
allowed-tools: Read, Bash
---

# Energize Denver Advanced Benchmarking

Two-factor energy benchmarking for Energize Denver auditing. Averages building size with ONE other factor of your choice, allowing focus on the most relevant building characteristic.

## Quick Start

Provide building size + ONE other factor:

```
25,000 sqft office                     (size + type)
25,000 sqft built in 1985              (size + year)
25,000 sqft in Denver/Mountain region  (size + region)
25,000 sqft with 3 floors              (size + floors)
25,000 sqft open 50 hours/week         (size + hours)
```

Choose the factor that best represents your building's unique characteristics.

## How It Works

1. **Gather building information** - size plus ONE other characteristic
2. **Look up size** in [data/cbecs_by_size.csv](data/cbecs_by_size.csv)
3. **Look up second factor** in corresponding data file
4. **Extract all 11 values** (Total + 10 categories) from both rows
5. **Calculate averages** by adding and dividing by 2 for each column
6. **Generate output table** with both factor values, percentages, and final average

**Example: Size + Type**
```
Input: 25,000 sqft office

Lookups:
- Size (25,001 to 50,000): 68.9 kBtu/sqft
- Type (Office): 65.6 kBtu/sqft

Average: (68.9 + 65.6) / 2 = 67.25 kBtu/sqft
```

## Usage

### Manual Calculation

1. Look up size in [data/cbecs_by_size.csv](data/cbecs_by_size.csv)
2. Look up the second factor:
   - Type: [data/cbecs_by_type.csv](data/cbecs_by_type.csv)
   - Year: [data/cbecs_by_year.csv](data/cbecs_by_year.csv)
   - Region: [data/cbecs_by_region_climate.csv](data/cbecs_by_region_climate.csv)
   - Floors: [data/cbecs_by_floors.csv](data/cbecs_by_floors.csv)
   - Hours: [data/cbecs_by_hours.csv](data/cbecs_by_hours.csv)
3. Average each column from both rows

### Automated Calculation

```bash
# Size + Type
python scripts/calculate_advanced.py --sqft 25000 --type "Office"

# Size + Year
python scripts/calculate_advanced.py --sqft 25000 --year "1980 to 1989"

# Size + Region
python scripts/calculate_advanced.py --sqft 25000 --region "Mountain"

# Size + Floors
python scripts/calculate_advanced.py --sqft 25000 --floors 3

# Size + Hours
python scripts/calculate_advanced.py --sqft 25000 --hours "50 to 99"

# With building details
python scripts/calculate_advanced.py \
  --sqft 25000 \
  --type "Office" \
  --name "Downtown Office" \
  --address "123 Main St, Denver, CO"
```

## Output Format

```
Building: Downtown Office
Address: 123 Main St, Denver, CO
Size: 25,000 sqft
Type: Office

Refinement Factors Used: 2
- Building Size: 25,001 to 50,000
- Building Type: Office

Energy Use Intensity (kBtu/sqft):

                          Total  Space_Heating  Cooling  Ventilation  ...
Building Size (25,001 to 50,000)
                          68.9   25.6          7.1      2.9          ...
Percentage (%)            100%   37%           10%      4%           ...

Building Type (Office)
                          65.6   20.1          5.1      3.2          ...
Percentage (%)            100%   31%           8%       5%           ...

--------------------------------------------------------------------------------
AVERAGE (AUDIT)           67.25  22.85         6.1      3.05         ...
Percentage (%)            100%   34%           9%       5%           ...

Total Annual Energy Use: 1,681,250 kBtu (67.25 kBtu/sqft × 25,000 sqft)
```

## Options

### Building Size (Always Required)

| Range | Description |
|-------|-------------|
| 1,001 to 5,000 sqft | Small |
| 5,001 to 10,000 sqft | Small-Medium |
| 10,001 to 25,000 sqft | Medium |
| 25,001 to 50,000 sqft | Medium-Large |
| 50,001 to 100,000 sqft | Large |
| 100,001 to 200,000 sqft | Very Large |
| 200,001 to 500,000 sqft | Extra Large |
| Over 500,000 sqft | Jumbo |

### Choose ONE Additional Factor

**Building Type**: Education, Food sales/service, Health care, Lodging, Mercantile/Retail, Office, Public assembly, Public order and safety, Religious worship, Service, Warehouse and storage, Other/Vacant

**Year Built**: Before 1920, 1920-1945, 1946-1959, 1960-1969, 1970-1979, 1980-1989, 1990-1999, 2000-2009, 2010-2018

**Region/Climate**:
- Regions: Northeast, Midwest, South, West (Mountain, Pacific)
- Climate Zones: Cold/very cold, Cool, Mixed mild, Warm, Hot/very hot
- For Denver: Use "Mountain" or "Cool"

**Number of Floors**: 1, 2, 3, 4-9, 10+

**Weekly Operating Hours**: <5, 5-9, 10-19, 20-49, 50-99, 100-249, 250+

## When to Use Advanced vs Basic

### Use Advanced When:
- **Historic buildings** - Use Size + Year when age is dominant factor
- **Climate impact** - Use Size + Region for Denver-specific estimates
- **24/7 operations** - Use Size + Hours for unusual schedules
- **High-rise buildings** - Use Size + Floors for vertical circulation energy
- **Unknown building type** - Use Size + another known factor

### Use Basic (energize-denver-audit) When:
- Standard buildings where type is most important
- Mixed-use buildings needing both size and type
- Quick type comparisons (offices vs warehouses vs retail)

## Accuracy Considerations

### Factor Impact (Energy Range)

| Factor | Range | Impact |
|--------|-------|--------|
| Operating Hours | 30-106 kBtu/sqft | 250% |
| Building Type | 32-212 kBtu/sqft | 560% |
| Year Built | 64-83 kBtu/sqft | 30% |
| Region/Climate | 56-89 kBtu/sqft | 60% |
| Size | 60-96 kBtu/sqft | 60% |
| Floors | 63-77 kBtu/sqft | 22% |

### Limitations

- All data is national averages from CBECS 2018
- Individual building performance varies widely
- Does not account for equipment efficiency, occupancy, renovations
- Some categories have "Q" (withheld data)

### Best Practice

**Use this skill for**: Estimating without utility data, normalizing comparisons, setting baselines, planning audits

**Don't use for**: Buildings with actual bills (use real data), LEED certification, legal compliance, precise cost calculations

## Troubleshooting

**Can't decide which factor to use:**
- Start with basic skill (Size + Type) as default
- Use advanced only when one characteristic strongly dominates
- Building type is usually most important

**Missing data (Q values):**
- Try a different factor
- Fall back to basic method
- Document limitation in report

**Unexpected results:**
- Verify factor value matches your building
- Consider if building has multiple characteristics
- Compare with basic method

## References

- Script: [scripts/calculate_advanced.py](scripts/calculate_advanced.py)
- Examples: [examples/](examples/)
- Data: [data/](data/) - All CBECS lookup tables
- CBECS 2018: https://www.eia.gov/consumption/commercial/data/2018/
