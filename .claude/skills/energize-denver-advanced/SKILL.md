---
name: energize-denver-advanced
description: Advanced energy benchmarking for Energize Denver with multi-factor refinement. Calculates estimates using building size, type, year built, region/climate, floor count, and operating hours from CBECS 2018. Provides more accurate benchmarks than basic size+type lookup by averaging multiple factors. Use when you need refined estimates or have detailed building information.
---

# Energize Denver Advanced Benchmarking

This skill provides **advanced multi-factor energy benchmarking** for Energize Denver auditing. Unlike the basic skill which only uses size and type, this version allows you to refine estimates with additional building characteristics for greater accuracy.

## Quick Start

**Basic usage (size + type only):**
```
25,000 sqft office
```

**Refined usage (multiple factors):**
```
25,000 sqft office built in 1985 in Denver with 3 floors, open 50 hours/week
```

The more factors you provide, the more accurate the benchmark.

## Available Refinement Factors

### 1. Building Size (Required)
- 1,001 to 5,000 sqft
- 5,001 to 10,000 sqft
- 10,001 to 25,000 sqft
- 25,001 to 50,000 sqft
- 50,001 to 100,000 sqft
- 100,001 to 200,000 sqft
- 200,001 to 500,000 sqft
- Over 500,000 sqft

### 2. Building Type (Required)
- Education
- Food sales / Food service
- Health care / Inpatient / Outpatient
- Lodging
- Mercantile / Retail / Enclosed and strip malls
- Office
- Public assembly
- Public order and safety
- Religious worship
- Service
- Warehouse and storage
- Other / Vacant

### 3. Year Built (Optional)
- Before 1920
- 1920 to 1945
- 1946 to 1959
- 1960 to 1969
- 1970 to 1979
- 1980 to 1989
- 1990 to 1999
- 2000 to 2009
- 2010 to 2018

### 4. Region/Climate (Optional)
**Regions:**
- Northeast (New England, Middle Atlantic)
- Midwest (East North Central, West North Central)
- South (South Atlantic, East South Central, West South Central)
- West (Mountain, Pacific)

**Climate Zones:**
- Cold or very cold
- Cool
- Mixed mild
- Warm
- Hot or very hot

**For Denver:** Use "Mountain" or "Cool" climate zone

### 5. Number of Floors (Optional)
- 1 floor
- 2 floors
- 3 floors
- 4 to 9 floors
- 10 or more floors

### 6. Weekly Operating Hours (Optional)
- Fewer than 5 hours/week
- 5 to 9 hours/week
- 10 to 19 hours/week
- 20 to 49 hours/week
- 50 to 99 hours/week
- 100 to 249 hours/week
- 250 or more hours/week

## How It Works

The skill averages values from **all provided factors**:

**Example with 3 factors:**
```
Input: 25,000 sqft office built in 1985

Lookups:
- Size (25,001 to 50,000): 68.9 kBtu/sqft
- Type (Office): 65.6 kBtu/sqft
- Year (1980 to 1989): 72.4 kBtu/sqft

Average: (68.9 + 65.6 + 72.4) / 3 = 68.97 kBtu/sqft
```

**Example with 5 factors:**
```
Input: 25,000 sqft office built in 1985 in Mountain region, 3 floors, 50 hours/week

Lookups:
- Size: 68.9 kBtu/sqft
- Type: 65.6 kBtu/sqft
- Year: 72.4 kBtu/sqft
- Region: 77.0 kBtu/sqft
- Floors: 71.5 kBtu/sqft
- Hours: 78.2 kBtu/sqft

Average: (68.9 + 65.6 + 72.4 + 77.0 + 71.5 + 78.2) / 6 = 72.27 kBtu/sqft
```

More factors = more refined estimate.

## Manual Calculation Steps

1. **Gather building information** from the user
2. **Look up each factor** in the corresponding data file:
   - [data/cbecs_by_size.csv](data/cbecs_by_size.csv)
   - [data/cbecs_by_type.csv](data/cbecs_by_type.csv)
   - [data/cbecs_by_year.csv](data/cbecs_by_year.csv)
   - [data/cbecs_by_region_climate.csv](data/cbecs_by_region_climate.csv)
   - [data/cbecs_by_floors.csv](data/cbecs_by_floors.csv)
   - [data/cbecs_by_hours.csv](data/cbecs_by_hours.csv)
3. **Extract all 11 values** (Total + 10 categories) from each matching row
4. **Calculate averages** across all factors for each column
5. **Generate output table** showing individual factor values and final averages

## Automated Calculation

Use the Python script for faster processing:

**Basic (size + type):**
```bash
python scripts/calculate_advanced.py --sqft 25000 --type "Office"
```

**With year built:**
```bash
python scripts/calculate_advanced.py --sqft 25000 --type "Office" --year "1980 to 1989"
```

**With region:**
```bash
python scripts/calculate_advanced.py --sqft 25000 --type "Office" --region "Mountain"
```

**Full refinement:**
```bash
python scripts/calculate_advanced.py \
  --sqft 25000 \
  --type "Office" \
  --year "1980 to 1989" \
  --region "Mountain" \
  --floors 3 \
  --hours "50 to 99"
```

**With building details:**
```bash
python scripts/calculate_advanced.py \
  --sqft 25000 \
  --type "Office" \
  --year "1980 to 1989" \
  --region "Mountain" \
  --name "Downtown Office" \
  --address "123 Main St, Denver, CO"
```

## Output Format

The output shows:
1. All individual factor lookups
2. Average across all factors (AUDIT value)
3. Comparison to basic method (size + type only)

```
Building: Downtown Office
Address: 123 Main St, Denver, CO
Size: 25,000 sqft
Type: Office

Refinement Factors Used: 4
- Building Size: 25,001 to 50,000
- Building Type: Office
- Year Built: 1980 to 1989
- Region: Mountain

Energy Use Intensity (kBtu/sqft):

                          Total  Space_Heating  Cooling  ...
Size-based                68.9   25.6          7.1      ...
Type-based                65.6   20.1          5.1      ...
Year-based                72.4   21.1          6.4      ...
Region-based              77.0   24.4          5.1      ...
──────────────────────────────────────────────────────────
AVERAGE (AUDIT)           70.98  22.8          5.93     ...

Basic Method (size+type): 67.25  22.85         6.1      ...
Difference:               +3.73  -0.05         -0.17    ...

Total Annual Energy: 1,774,500 kBtu
```

## Comparison: Basic vs Advanced

### Basic Method (energize-denver-audit)
- Uses: Size + Type (2 factors)
- Speed: Fast
- Accuracy: Good for general estimates
- Best for: Quick benchmarks, simple buildings

### Advanced Method (energize-denver-advanced)
- Uses: Size + Type + Year + Region + Floors + Hours (up to 6 factors)
- Speed: Slightly slower
- Accuracy: Higher for specific buildings
- Best for: Detailed audits, older buildings, climate-specific analysis

### When to Use Advanced:

1. **Older buildings** - Year built significantly affects energy use
2. **Climate matters** - Denver's climate vs national average
3. **Detailed audits** - When you have comprehensive building data
4. **Variance analysis** - Understanding why a building differs from typical
5. **Justifying recommendations** - More refined baseline for savings calculations

### When to Use Basic:

1. **Quick estimates** - Don't have detailed building info
2. **New construction** - Less variation by age
3. **Multiple buildings** - Batch processing many properties
4. **Initial screening** - First-pass analysis

## Data Sources

All lookup tables in [data/](data/):
- **cbecs_by_size.csv** - 8 size ranges
- **cbecs_by_type.csv** - 18 building types
- **cbecs_by_year.csv** - 9 age brackets
- **cbecs_by_region_climate.csv** - 19 geographic/climate zones
- **cbecs_by_floors.csv** - 5 floor count ranges
- **cbecs_by_hours.csv** - 7 operating hour ranges
- **cbecs_full.csv** - Complete CBECS 2018 Table E2 dataset

Source: U.S. Energy Information Administration, CBECS 2018

## Example Use Cases

### Use Case 1: Historic Building Audit
```
User: "I need to benchmark a 35,000 sqft office building built in 1925 in downtown Denver."

Process:
- Size: 25,001 to 50,000 → 68.9 kBtu/sqft
- Type: Office → 65.6 kBtu/sqft
- Year: 1920 to 1945 → 71.8 kBtu/sqft
- Region: Mountain → 77.0 kBtu/sqft

Average: 70.83 kBtu/sqft (vs 67.25 basic method)

Insight: Historic buildings in Denver climate use ~5% more energy than national office average
```

### Use Case 2: Climate-Adjusted Benchmark
```
User: "What's the expected energy use for a 15,000 sqft warehouse in Denver?"

Basic: 46.1 kBtu/sqft (size + type average)

Advanced with climate:
- Size: 10,001 to 25,000 → 59.5 kBtu/sqft
- Type: Warehouse → 32.3 kBtu/sqft
- Region: Mountain → 77.0 kBtu/sqft

Average: 56.27 kBtu/sqft

Insight: Denver warehouses use more heating energy than national average
```

### Use Case 3: Operating Hours Impact
```
User: "24/7 data center in a 50,000 sqft office building built in 2005"

Factors:
- Size: 25,001 to 50,000 → 68.9
- Type: Office → 65.6
- Year: 2000 to 2009 → 80.7
- Hours: Open continuously → 106.8

Average: 80.5 kBtu/sqft (vs 67.25 basic)

Insight: 24/7 operation increases energy use by ~20%
```

## Accuracy Considerations

### Factor Importance (Ranked)

1. **Building Type** - Highest impact (varies 200+ kBtu/sqft)
2. **Operating Hours** - Major impact for 24/7 vs limited hours
3. **Size** - Moderate impact (economies of scale)
4. **Year Built** - Moderate impact (efficiency improvements)
5. **Region/Climate** - Moderate impact (heating/cooling loads)
6. **Floors** - Minor impact (elevator/circulation energy)

### Limitations

- All data is **national averages** from CBECS 2018
- Individual building performance varies widely
- Does not account for:
  - Specific equipment efficiency
  - Occupancy patterns
  - Recent renovations
  - Actual utility data (when available, use actual over estimated)
- Some categories have "Q" (withheld data due to high error)

### Best Practice

**Use this skill for:**
- Estimating when no utility data exists
- Normalizing for comparisons
- Setting baseline expectations
- Planning energy audits

**Don't use this skill for:**
- Buildings with actual utility bills (use real data instead)
- LEED certification (requires measured data)
- Legal compliance (may require certified methods)
- Precise cost calculations (too much variability)

## Troubleshooting

**Too many factors create outliers:**
- Review which factors are pulling average up/down
- Consider removing outlier factors
- Prioritize building type and size as most reliable

**Missing data (Q values):**
- Use fewer factors
- Fall back to basic method
- Document limitation in report

**Conflicting information:**
- "Office building open 24/7" - may be data center, use Service category
- Verify building type classification
- Check if refinement factors match building use

## References

- Script: [scripts/calculate_advanced.py](scripts/calculate_advanced.py)
- Examples: [examples/](examples/) - Comparison cases
- Data: [data/](data/) - All CBECS lookup tables
- CBECS 2018: https://www.eia.gov/consumption/commercial/data/2018/
