---
name: xlsx-to-csv
version: 1.0.0
description: Converts Excel (.xlsx) files to CSV format. Handles single and multi-sheet workbooks, preserving data structure and formatting. Use when you need to convert Excel files to CSV for data processing, analysis, or integration with other tools.
category: tool
allowed-tools: Read, Write, Bash
---

# XLSX to CSV Converter

Converts Excel (.xlsx) files to CSV (Comma-Separated Values) format.

## Quick Start

**Input required:**
- Path to the .xlsx file
- (Optional) Sheet name or index for multi-sheet workbooks
- (Optional) Output directory for the CSV file(s)

**Output:**
- One or more CSV files depending on workbook structure
- Confirmation message with file location(s)

## How It Works

1. **Locate the file** - Verify .xlsx exists at provided path
2. **Check dependencies** - Ensure pandas/openpyxl are available
3. **Read the workbook** - Load Excel file and identify sheets
4. **Convert to CSV** - Single sheet: one CSV; Multiple sheets: separate CSVs or prompt for selection
5. **Save output** - Write CSV file(s) to specified location

## Usage

### Method 1: Using Python with pandas (Recommended)

Handles complex Excel features well.

**Installation:**
```bash
pip install pandas openpyxl
```

**Conversion script:**
```python
import pandas as pd
import os
import sys

def convert_xlsx_to_csv(xlsx_path, output_dir=None, sheet_name=None):
    """
    Convert XLSX file to CSV format.

    Args:
        xlsx_path: Path to the input .xlsx file
        output_dir: Directory to save CSV files (defaults to same directory as xlsx)
        sheet_name: Specific sheet name/index to convert (if None, converts all sheets)

    Returns:
        List of created CSV file paths
    """
    # Verify input file exists
    if not os.path.exists(xlsx_path):
        raise FileNotFoundError(f"File not found: {xlsx_path}")

    # Set output directory
    if output_dir is None:
        output_dir = os.path.dirname(xlsx_path) or '.'
    os.makedirs(output_dir, exist_ok=True)

    # Get base filename
    base_name = os.path.splitext(os.path.basename(xlsx_path))[0]

    # Read Excel file
    excel_file = pd.ExcelFile(xlsx_path)
    created_files = []

    # Determine which sheets to convert
    if sheet_name is not None:
        sheets_to_convert = [sheet_name]
    else:
        sheets_to_convert = excel_file.sheet_names

    # Convert each sheet
    for sheet in sheets_to_convert:
        # Read sheet
        df = pd.read_excel(xlsx_path, sheet_name=sheet)

        # Generate output filename
        if len(sheets_to_convert) == 1:
            csv_filename = f"{base_name}.csv"
        else:
            # Sanitize sheet name for filename
            safe_sheet_name = "".join(c for c in sheet if c.isalnum() or c in (' ', '-', '_')).strip()
            csv_filename = f"{base_name}_{safe_sheet_name}.csv"

        csv_path = os.path.join(output_dir, csv_filename)

        # Write to CSV
        df.to_csv(csv_path, index=False, encoding='utf-8')
        created_files.append(csv_path)
        print(f"Created: {csv_path}")

    return created_files

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_xlsx_to_csv.py <xlsx_file> [output_dir] [sheet_name]")
        sys.exit(1)

    xlsx_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    sheet_name = sys.argv[3] if len(sys.argv) > 3 else None

    created = convert_xlsx_to_csv(xlsx_file, output_dir, sheet_name)
    print(f"\nSuccessfully converted {len(created)} sheet(s)")
```

### Method 2: Alternative Libraries

If pandas is not available, alternatives include:
- **openpyxl + csv module** (Python standard library + openpyxl)
- **xlsx2csv** (dedicated command-line tool)
- **LibreOffice** (headless conversion via command line)

## Examples

### Example 1: Convert single file

**User request:**
"Convert the file data.xlsx to CSV"

**Your process:**
1. Check if the file exists at the provided path
2. Check if pandas/openpyxl are installed
3. If not installed, ask user if they want to install them
4. Run the conversion script
5. Inform user of the output location

### Example 2: Multi-sheet workbook

**User request:**
"Convert financial_report.xlsx to CSV - it has 3 sheets"

**Your process:**
1. Load the workbook and list available sheets
2. Ask user if they want:
   - All sheets converted to separate CSV files
   - A specific sheet only
3. Perform conversion based on user choice
4. Report all created files

### Example 3: Batch conversion

**User request:**
"Convert all .xlsx files in the reports folder to CSV"

**Your process:**
1. Find all .xlsx files in the specified directory
2. For each file, run the conversion
3. Provide summary of all conversions completed

### Example 4: Custom output location

**User request:**
"Convert sales_data.xlsx and save the CSV to the processed_data folder"

**Your process:**
1. Convert the file
2. Save output to the specified directory
3. Confirm the new location

## Options

### Check Dependencies
```bash
python -c "import pandas, openpyxl" 2>/dev/null && echo "OK" || echo "Need install"
```

### Inspect Workbook
```python
import pandas as pd
excel_file = pd.ExcelFile('file.xlsx')
print("Sheets:", excel_file.sheet_names)
```

## Edge Cases

**Large files:**
- Files over 100MB may take time to process
- Consider using chunking for very large datasets
- Warn user about processing time

**Complex formatting:**
- CSV format doesn't preserve Excel formatting (colors, fonts, formulas)
- Formulas are converted to their calculated values
- Multiple sheets require separate CSV files
- Inform user about these limitations upfront

**Special characters:**
- Use UTF-8 encoding to preserve special characters
- Handle commas in data by proper quoting

**Empty sheets:**
- Skip empty sheets or inform user
- Create empty CSV files only if user requests

**Protected/encrypted files:**
- Cannot convert password-protected Excel files without the password
- Ask user to provide unprotected version

## Output Format

Standard confirmation message:

```
Converted: data.xlsx
Output: data.csv (123 KB)
Location: C:\Users\Public\VSwork\data.csv
Sheets processed: Sheet1
Rows: 1,250
Columns: 15
```

For multiple sheets:

```
Converted: financial_report.xlsx
Created 3 CSV files:
  1. financial_report_Summary.csv (45 KB) - 100 rows
  2. financial_report_Q1_Data.csv (230 KB) - 2,500 rows
  3. financial_report_Q2_Data.csv (235 KB) - 2,550 rows
Location: C:\Users\Public\VSwork\
```

## Installation Script

Save this as a helper script in the skill directory:

```bash
#!/bin/bash
# install_dependencies.sh
echo "Installing XLSX to CSV conversion dependencies..."
pip install pandas openpyxl
echo "Installation complete!"
```

Or for Windows:

```batch
@echo off
REM install_dependencies.bat
echo Installing XLSX to CSV conversion dependencies...
pip install pandas openpyxl
echo Installation complete!
```

## Troubleshooting

**ModuleNotFoundError for pandas or openpyxl:**
- Solution: `pip install pandas openpyxl`

**File not found error:**
- Verify file path is correct
- Check for typos in filename
- Use absolute path if relative fails

**Encoding issues:**
- Script uses UTF-8 encoding
- Try specifying encoding explicitly if issues persist

**Memory errors with large files:**
- Process sheets individually
- Use chunking for very large datasets
- Consider xlsx2csv tool for extremely large files

## Notes

- CSV files use UTF-8 encoding by default
- Formulas are evaluated; only values saved
- Date/time formats preserved as ISO text
- Charts, images, macros not included
- Multiple sheets create multiple CSV files with suffixed names

## References

- pandas: https://pandas.pydata.org/docs/
- openpyxl: https://openpyxl.readthedocs.io/
