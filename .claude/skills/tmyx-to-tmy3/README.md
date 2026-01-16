# TMYx/EPW to TMY3 Converter

Converts newer TMYx (Typical Meteorological Year) and EPW (EnergyPlus Weather) files to the legacy TMY3 format for compatibility with older tools.

## What it does

This skill transforms NREL TMYx CSV files and EnergyPlus EPW files into the older TMY3 structure by:
- Restructuring metadata headers
- Converting date/time from separate columns (Year, Month, Day, Hour) to combined format (MM/DD/YYYY, HH:MM)
- Mapping weather data columns to TMY3 column order
- Converting units where necessary (e.g., Pascals to millibars for pressure)
- Adding appropriate source and uncertainty codes

## Usage

Run the skill from Claude Code:

```
/tmyx-to-tmy3
```

You'll be prompted for:
- **file_path**: Path to the TMYx CSV or EPW file to convert
- **output_dir**: (Optional) Directory to save the converted file

## Example

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

This will create a file like: `724698TMYX.csv`

## File Format Reference

### TMYx/EPW Format (Input)
- **File Types**: `.csv` (TMYx) or `.epw` (EnergyPlus Weather)
- Both use the same EPW data structure
- Multiple metadata header rows (LOCATION, DESIGN CONDITIONS, etc.)
- Data columns: Year, Month, Day, Hour, Minute, ...weather data...
- Pressure in Pascals
- Modern NREL format (2009-2023)

### TMY3 Format (Output)
- Single header row with station info
- Column header row with full field names
- Data format: Date (MM/DD/YYYY), Time (HH:MM), ...weather data...
- Pressure in millibars
- Legacy format compatible with older tools

## Notes

- **Supported formats**: `.csv` (TMYx) and `.epw` (EnergyPlus Weather) files
- Both formats use the same EPW data structure internally
- Output filename format: `{station_id}TMYX.csv` (e.g., `724698TMYX.csv`)
- Time hour 0 is converted to 24:00 (TMY3 convention)
- Only includes columns that have data in the source file
- Pressure is converted from Pascals to millibars
- Date/Time columns are combined into TMY3 format
