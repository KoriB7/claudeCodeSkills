---
name: energize-denver-advanced
description: Advanced energy benchmarking for Energize Denver with two-factor refinement. Calculates estimates using building size plus ONE other factor (type, year built, region/climate, floor count, or operating hours) from CBECS 2018. Always averages exactly 2 factors. Use when you want to focus on a specific building characteristic beyond just size.
---

# Energize Denver Advanced Benchmarking

This skill provides **two-factor energy benchmarking** for Energize Denver auditing. It always averages building size with ONE other factor of your choice, allowing you to focus on the most relevant building characteristic (type, age, climate, floors, or operating hours).

## Quick Start

**You must provide building size + ONE other factor:**

Examples:
```
25,000 sqft office                           (size + type)
25,000 sqft built in 1985                    (size + year)
25,000 sqft in Denver/Mountain region        (size + region)
25,000 sqft with 3 floors                    (size + floors)
25,000 sqft open 50 hours/week               (size + hours)
```

Choose the factor that best represents your building's unique characteristics.

## Available Factors

### 1. Building Size (Always Required)
- 1,001 to 5,000 sqft
- 5,001 to 10,000 sqft
- 10,001 to 25,000 sqft
- 25,001 to 50,000 sqft
- 50,001 to 100,000 sqft
- 100,001 to 200,000 sqft
- 200,001 to 500,000 sqft
- Over 500,000 sqft

### 2. Choose ONE of the following:

#### Building Type
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

#### Year Built
- Before 1920
- 1920 to 1945
- 1946 to 1959
- 1960 to 1969
- 1970 to 1979
- 1980 to 1989
- 1990 to 1999
- 2000 to 2009
- 2010 to 2018

#### Region/Climate
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

#### Number of Floors
- 1 floor
- 2 floors
- 3 floors
- 4 to 9 floors
- 10 or more floors

#### Weekly Operating Hours
- Fewer than 5 hours/week
- 5 to 9 hours/week
- 10 to 19 hours/week
- 20 to 49 hours/week
- 50 to 99 hours/week
- 100 to 249 hours/week
- 250 or more hours/week

## How It Works

The skill averages values from **exactly 2 factors**: building size + one other factor.

**Example: Size + Type**
```
Input: 25,000 sqft office

Lookups:
- Size (25,001 to 50,000): 68.9 kBtu/sqft
- Type (Office): 65.6 kBtu/sqft

Average: (68.9 + 65.6) / 2 = 67.25 kBtu/sqft
```

**Example: Size + Year Built**
```
Input: 25,000 sqft built in 1985

Lookups:
- Size (25,001 to 50,000): 68.9 kBtu/sqft
- Year (1980 to 1989): 72.4 kBtu/sqft

Average: (68.9 + 72.4) / 2 = 70.65 kBtu/sqft
```

**Example: Size + Region**
```
Input: 25,000 sqft in Mountain region

Lookups:
- Size (25,001 to 50,000): 68.9 kBtu/sqft
- Region (Mountain): 77.0 kBtu/sqft

Average: (68.9 + 77.0) / 2 = 72.95 kBtu/sqft
```

## Manual Calculation Steps

1. **Gather building information** - size plus ONE other characteristic
2. **Look up size** in [data/cbecs_by_size.csv](data/cbecs_by_size.csv)
3. **Look up the second factor** in the corresponding file:
   - Type: [data/cbecs_by_type.csv](data/cbecs_by_type.csv)
   - Year: [data/cbecs_by_year.csv](data/cbecs_by_year.csv)
   - Region: [data/cbecs_by_region_climate.csv](data/cbecs_by_region_climate.csv)
   - Floors: [data/cbecs_by_floors.csv](data/cbecs_by_floors.csv)
   - Hours: [data/cbecs_by_hours.csv](data/cbecs_by_hours.csv)
4. **Extract all 11 values** (Total + 10 categories) from both rows
5. **Calculate averages** by adding the two values and dividing by 2 for each column
6. **Generate output table** showing both factor values, percentages, and final average

## Automated Calculation

Use the Python script for faster processing. You must provide --sqft and exactly ONE other factor:

**Size + Type:**
```bash
python scripts/calculate_advanced.py --sqft 25000 --type "Office"
```

**Size + Year:**
```bash
python scripts/calculate_advanced.py --sqft 25000 --year "1980 to 1989"
```

**Size + Region:**
```bash
python scripts/calculate_advanced.py --sqft 25000 --region "Mountain"
```

**Size + Floors:**
```bash
python scripts/calculate_advanced.py --sqft 25000 --floors 3
```

**Size + Hours:**
```bash
python scripts/calculate_advanced.py --sqft 25000 --hours "50 to 99"
```

**With building details (optional):**
```bash
python scripts/calculate_advanced.py \
  --sqft 25000 \
  --type "Office" \
  --name "Downtown Office" \
  --address "123 Main St, Denver, CO"
```

## Output Format

The output shows:
1. Both individual factor lookups with percentages
2. Average of the two factors (AUDIT value)

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

## Comparison: Basic vs Advanced

### Basic Method (energize-denver-audit)
- Uses: Size + Type (always 2 factors)
- Speed: Fast
- Focus: General building type benchmarking
- Best for: Standard office, retail, warehouse buildings where type is the primary differentiator

### Advanced Method (energize-denver-advanced)
- Uses: Size + ONE chosen factor (always 2 factors)
- Speed: Same as basic
- Focus: Targeted characteristic analysis
- Best for: Buildings where a specific characteristic matters more than type

### When to Use Advanced:

Choose advanced when ONE specific factor is more important than building type:

1. **Historic buildings** - Use Size + Year when age is the dominant factor
2. **Climate impact** - Use Size + Region for Denver-specific or climate-adjusted estimates
3. **24/7 operations** - Use Size + Hours for buildings with unusual operating schedules
4. **High-rise buildings** - Use Size + Floors when vertical circulation energy is significant
5. **Unknown building type** - Use Size + another known factor when type is unclear

### When to Use Basic:

1. **Standard buildings** - When building type is the most important characteristic
2. **Mixed-use** - When you need both size and type in the calculation
3. **Quick type comparisons** - Comparing offices vs warehouses vs retail

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

### Use Case 1: Historic Building (Focus on Age)
```
User: "I need to benchmark a 35,000 sqft building built in 1925, but I don't know the building type."

Use: Size + Year (instead of Size + Type)

Process:
- Size: 25,001 to 50,000 → 68.9 kBtu/sqft
- Year: 1920 to 1945 → 71.8 kBtu/sqft

Average: (68.9 + 71.8) / 2 = 70.35 kBtu/sqft

Insight: Historic buildings use significantly more energy due to older insulation and systems
```

### Use Case 2: Climate-Adjusted Benchmark
```
User: "What's the expected energy use for a 15,000 sqft building in Denver's climate?"

Use: Size + Region (to focus on climate impact)

Process:
- Size: 10,001 to 25,000 → 59.5 kBtu/sqft
- Region: Mountain → 77.0 kBtu/sqft

Average: (59.5 + 77.0) / 2 = 68.25 kBtu/sqft

Insight: Denver's mountain climate increases heating loads significantly vs national average
```

### Use Case 3: 24/7 Operations (Focus on Hours)
```
User: "24/7 data center in a 50,000 sqft building"

Use: Size + Hours (operating schedule is most critical)

Process:
- Size: 25,001 to 50,000 → 68.9 kBtu/sqft
- Hours: 250 or more → 106.8 kBtu/sqft

Average: (68.9 + 106.8) / 2 = 87.85 kBtu/sqft

Insight: Continuous operation dramatically increases energy use - much more than building type
```

## Accuracy Considerations

### Factor Impact (How Much Each Factor Matters)

When choosing which factor to use with size, consider the typical energy range:

1. **Operating Hours** - Highest impact (30-106 kBtu/sqft, 250% range)
2. **Building Type** - High impact (32-212 kBtu/sqft, 560% range)
3. **Year Built** - Moderate impact (64-83 kBtu/sqft, 30% range)
4. **Region/Climate** - Moderate impact (56-89 kBtu/sqft, 60% range)
5. **Size** - Moderate impact (60-96 kBtu/sqft, 60% range)
6. **Floors** - Lower impact (63-77 kBtu/sqft, 22% range)

**Choosing Your Factor:**
- If the building operates 24/7 or has unusual hours → use Hours
- If it's a specialized building type (hospital, data center) → use Type (basic skill)
- If it's very old or very new → use Year
- If climate is significantly different from national average → use Region
- If it's a high-rise → use Floors

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

**Can't decide which factor to use:**
- Start with the basic skill (Size + Type) as the default
- Use advanced only when you have strong reason to focus on one specific characteristic
- When in doubt, building type is usually the most important factor

**Missing data (Q values):**
- Try a different factor
- Fall back to basic method
- Document limitation in report

**Unexpected results:**
- Verify the factor value matches your building (check the category ranges)
- Consider if the building has multiple characteristics (old building that's been renovated)
- Compare with basic method to see how much the chosen factor changes the estimate

## References

- Script: [scripts/calculate_advanced.py](scripts/calculate_advanced.py)
- Examples: [examples/](examples/) - Comparison cases
- Data: [data/](data/) - All CBECS lookup tables
- CBECS 2018: https://www.eia.gov/consumption/commercial/data/2018/
