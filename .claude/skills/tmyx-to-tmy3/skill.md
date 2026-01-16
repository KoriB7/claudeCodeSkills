---
name: tmyx-to-tmy3
version: 1.0.0
description: Converts TMYx/EPW weather data files to TMY3 format for legacy tool compatibility. Transforms newer NREL TMYx CSV files and EnergyPlus EPW files into the older TMY3 structure by mapping columns, reformatting dates/times, and restructuring headers.
category: tool
allowed-tools: Read, Write, Bash
---

# TMYx/EPW to TMY3 Converter

Converts newer TMYx (Typical Meteorological Year) and EPW (EnergyPlus Weather) files to the legacy TMY3 format for compatibility with older tools.

## Quick Start

**Input required:**
- Path to TMYx CSV or EPW file
- (Optional) Output directory

**Output:**
- TMY3 formatted CSV file named `{station_id}TMYX.csv`

## How It Works

1. **Read source file** - Load TMYx CSV or EPW file
2. **Extract metadata** - Parse location info from header
3. **Map columns** - Convert EPW columns to TMY3 order
4. **Reformat dates** - Convert (Year, Month, Day, Hour) to (MM/DD/YYYY, HH:MM)
5. **Convert units** - Pressure from Pascals to millibars
6. **Write output** - Save as TMY3 formatted CSV

## Usage

### Manual Invocation

```
/tmyx-to-tmy3
```

You'll be prompted for:
- **file_path**: Path to TMYx CSV or EPW file
- **output_dir**: (Optional) Directory for output

### Command Line

```bash
# Basic usage
python main.py <weather_file> [output_dir]

# TMYx CSV file
python main.py USA_CO_Akron.csv

# EPW file
python main.py USA_CO_Akron.epw

# With output directory
python main.py USA_CO_Akron.epw ./converted
```

### Examples

**Example 1 - TMYx CSV file:**
```
/tmyx-to-tmy3
file_path: c:\weatherdata\USA_CO_Akron-Colorado.Plains.Rgnl.AP.724698_TMYx.2009-2023.csv
output_dir: c:\weatherdata\converted
```

**Example 2 - EPW file:**
```
/tmyx-to-tmy3
file_path: c:\weatherdata\USA_CO_Denver.epw
output_dir: c:\weatherdata\converted
```

Output: `724698TMYX.csv`

## Output Format

### TMY3 Structure

**Row 1 - Station metadata:**
```
Station_ID, Name, State, Latitude, Longitude, Timezone, Elevation
```

**Row 2 - Column headers:**
```
Date (MM/DD/YYYY), Time (HH:MM), ETR (W/m^2), ETRN (W/m^2), GHI (W/m^2), ...
```

**Row 3+ - Hourly data:**
```
1/1/1988, 1:00, 0, 0, 0, ...
```

### Column Mapping

| TMY3 Column | Source (EPW) | Unit Conversion |
|-------------|--------------|-----------------|
| Date | Year, Month, Day | Combined to MM/DD/YYYY |
| Time | Hour, Minute | Combined to HH:MM |
| Pressure | Column 9 | Pa → mbar (÷100) |
| All others | Direct mapping | None |

## Options

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Path to TMYx CSV or EPW file |
| `output_dir` | string | No | Output directory (default: current) |

### Supported Input Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| TMYx | `.csv` | NREL TMYx format (2009-2023) |
| EPW | `.epw` | EnergyPlus Weather format |

## Troubleshooting

**"Error: Input file not found"**
- Verify file path is correct
- Check for typos in filename
- Use absolute path

**Malformed rows skipped:**
- Source file may have incomplete data
- Check source file for corruption
- Rows with <10 columns are skipped

**Wrong station ID in output:**
- Script extracts 6-digit ID from filename
- Falls back to header if not found
- Rename input file if needed

**Encoding errors:**
- Script uses UTF-8 encoding
- Convert source file to UTF-8 if needed

## File Format Reference

### TMYx/EPW Format (Input)
- Multiple metadata header rows (LOCATION, DESIGN CONDITIONS, etc.)
- Data columns: Year, Month, Day, Hour, Minute, ...weather data...
- Pressure in Pascals
- Modern NREL format (2009-2023)

### TMY3 Format (Output)
- Single header row with station info
- Column header row with full field names
- Data: Date (MM/DD/YYYY), Time (HH:MM), ...weather data...
- Pressure in millibars
- Legacy format compatible with older tools

## Notes

- Output filename: `{station_id}TMYX.csv`
- Time hour 0 converts to 24:00 (TMY3 convention)
- Only includes columns present in source file
- Pressure converted from Pascals to millibars

## References

- Script: [main.py](main.py)
- NREL TMYx Data: https://nsrdb.nrel.gov/
- EnergyPlus Weather: https://energyplus.net/weather
