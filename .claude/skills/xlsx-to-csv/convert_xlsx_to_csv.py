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
        print(f"  Rows: {len(df):,}")
        print(f"  Columns: {len(df.columns)}")

    return created_files

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_xlsx_to_csv.py <xlsx_file> [output_dir] [sheet_name]")
        sys.exit(1)

    xlsx_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    sheet_name = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        created = convert_xlsx_to_csv(xlsx_file, output_dir, sheet_name)
        print(f"\nSuccessfully converted {len(created)} sheet(s)")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
