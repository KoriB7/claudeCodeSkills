#!/usr/bin/env python3
"""
TMYx/EPW to TMY3 Converter
Converts newer TMYx and EPW weather data files to legacy TMY3 format
Creates output with only the columns present in the source file
Supports both .csv (TMYx) and .epw (EnergyPlus Weather) formats
"""

import csv
import sys
import os
import re
from pathlib import Path

def extract_location_info(tmyx_file):
    """Extract location metadata from TMYx file header"""
    with open(tmyx_file, 'r', encoding='utf-8') as f:
        location_line = f.readline().strip()

    parts = location_line.split(',')
    location_data = {
        'station_id': parts[5] if len(parts) > 5 else '',
        'location_name': parts[1] if len(parts) > 1 else '',
        'state': parts[2] if len(parts) > 2 else '',
        'latitude': parts[6] if len(parts) > 6 else '',
        'longitude': parts[7] if len(parts) > 7 else '',
        'tz': parts[8] if len(parts) > 8 else '',
        'elevation': parts[9] if len(parts) > 9 else ''
    }
    return location_data

def find_data_start_row(tmyx_file):
    """Find the row where actual weather data starts (after metadata headers)"""
    with open(tmyx_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            # Data rows start with a year (4 digits)
            if line.strip() and line.split(',')[0].isdigit() and len(line.split(',')[0]) == 4:
                return i
    return 9  # Default if not found

def convert_tmyx_to_tmy3(input_file, output_dir=None):
    """
    Convert a TMYx or EPW file to TMY3 format
    Creates headers for only the columns that exist in the source file

    Args:
        input_file: Path to TMYx CSV or EPW file
        output_dir: Directory to save output (default: current directory)
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: Input file not found: {input_file}")
        return False

    # Determine output path
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    # Extract location info from file header (needed for header row)
    location_info = extract_location_info(input_file)

    # Extract station ID from filename (look for 6-digit number)
    filename_match = re.search(r'(\d{6})', input_path.name)

    if filename_match:
        station_id = filename_match.group(1)
    else:
        # Fallback to station ID from file header
        station_id = location_info['station_id']

    # Create output filename: {station_id}TMYX.csv
    output_filename = f"{station_id}TMYX.csv"
    output_file = output_path / output_filename

    # Detect file type
    file_extension = input_path.suffix.lower()
    file_type = "EPW" if file_extension == ".epw" else "TMYx"

    print(f"Converting {file_type} file: {input_path.name} to TMY3 format...")
    print(f"Output: {output_file}")

    # Find where data starts
    data_start_row = find_data_start_row(input_file)

    # Read TMYx data
    with open(input_file, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()

    # Write TMY3 format
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Row 1: Station metadata header (matching TMY3 format)
        # Format: Station ID, Name, State, Lat, Lon, TZ, Elevation (meters)
        header_row1 = [
            location_info['station_id'],
            location_info['location_name'],
            location_info['state'],
            location_info['latitude'],
            location_info['longitude'],
            location_info['tz'],
            location_info['elevation']
        ]
        writer.writerow(header_row1)

        # Row 2: Column headers for TMY3 format
        # Based on TMYx EPW columns 0-34 that have data
        tmy3_headers = [
            'Date (MM/DD/YYYY)',           # Combined from cols 0-2
            'Time (HH:MM)',                 # Combined from cols 3-4
            'ETR (W/m^2)',                  # Col 10
            'ETRN (W/m^2)',                 # Col 11
            'GHI (W/m^2)',                  # Col 13
            'DNI (W/m^2)',                  # Col 14
            'DHI (W/m^2)',                  # Col 15
            'GH illum (lx)',                # Col 16
            'DN illum (lx)',                # Col 17
            'DH illum (lx)',                # Col 18
            'Zenith lum (cd/m^2)',          # Col 19
            'Dry-bulb (C)',                 # Col 6
            'Dew-point (C)',                # Col 7
            'RHum (%)',                     # Col 8
            'Pressure (mbar)',              # Col 9 (converted from Pa)
            'Wdir (degrees)',               # Col 20
            'Wspd (m/s)',                   # Col 21
            'TotCld (tenths)',              # Col 22
            'OpqCld (tenths)',              # Col 23
            'Hvis (m)',                     # Col 24
            'CeilHgt (m)',                  # Col 25
            'Present Wx Obs',               # Col 26
            'Present Wx Codes',             # Col 27
            'Pwat (mm)',                    # Col 28
            'AOD (unitless)',               # Col 29
            'Snow Depth (cm)',              # Col 30
            'Days Since Snow',              # Col 31
            'Alb (unitless)',               # Col 32
            'Lprecip depth (mm)',           # Col 33
            'Lprecip quantity (hr)'         # Col 34
        ]
        writer.writerow(tmy3_headers)

        # Process data rows
        for line in all_lines[data_start_row - 1:]:
            if not line.strip():
                continue

            # Use CSV reader to properly parse the line
            tmyx_row = next(csv.reader([line.strip()]))

            # Skip if not enough columns
            if len(tmyx_row) < 10:
                continue

            try:
                # Parse date/time from TMYx
                year = tmyx_row[0]
                month = tmyx_row[1]
                day = tmyx_row[2]
                hour = tmyx_row[3]
                minute = tmyx_row[4]

                # Convert to TMY3 date/time format
                date_str = f"{month}/{day}/{year}"

                # Handle hour 0 as 24:00 (TMY3 convention)
                if hour == '0':
                    time_str = '24:00:00' if minute == '0' else f'24:{minute}'
                else:
                    time_str = f"{hour}:{minute if minute != '0' else '00'}"

                # Convert pressure from Pa to mbar (divide by 100)
                pressure_pa = float(tmyx_row[9]) if tmyx_row[9] and tmyx_row[9].replace('.','').replace('-','').isdigit() else 0
                pressure_mbar = int(pressure_pa / 100) if pressure_pa > 0 else ''

                # Build TMY3 row using ONLY columns from TMYx (no extra source/uncert columns)
                tmy3_row = [
                    date_str,                                        # Date (MM/DD/YYYY)
                    time_str,                                        # Time (HH:MM)
                    tmyx_row[10],                                    # ETR
                    tmyx_row[11],                                    # ETRN
                    tmyx_row[13],                                    # GHI
                    tmyx_row[14],                                    # DNI
                    tmyx_row[15],                                    # DHI
                    tmyx_row[16],                                    # GH illum
                    tmyx_row[17],                                    # DN illum
                    tmyx_row[18],                                    # DH illum
                    tmyx_row[19],                                    # Zenith lum
                    tmyx_row[6],                                     # Dry-bulb
                    tmyx_row[7],                                     # Dew-point
                    tmyx_row[8],                                     # RHum
                    str(pressure_mbar),                              # Pressure (mbar)
                    tmyx_row[20],                                    # Wdir
                    tmyx_row[21],                                    # Wspd
                    tmyx_row[22],                                    # TotCld
                    tmyx_row[23],                                    # OpqCld
                    tmyx_row[24],                                    # Hvis
                    tmyx_row[25] if len(tmyx_row) > 25 else '',     # CeilHgt
                    tmyx_row[26] if len(tmyx_row) > 26 else '',     # Present Wx Obs
                    tmyx_row[27] if len(tmyx_row) > 27 else '',     # Present Wx Codes
                    tmyx_row[28] if len(tmyx_row) > 28 else '',     # Pwat
                    tmyx_row[29] if len(tmyx_row) > 29 else '',     # AOD
                    tmyx_row[30] if len(tmyx_row) > 30 else '',     # Snow Depth
                    tmyx_row[31] if len(tmyx_row) > 31 else '',     # Days Since Snow
                    tmyx_row[32] if len(tmyx_row) > 32 else '',     # Alb
                    tmyx_row[33] if len(tmyx_row) > 33 else '',     # Lprecip depth
                    tmyx_row[34] if len(tmyx_row) > 34 else ''      # Lprecip quantity
                ]

                writer.writerow(tmy3_row)

            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping malformed row: {e}")
                continue

    print(f"[SUCCESS] Conversion complete!")
    print(f"[SUCCESS] Output saved to: {output_file}")
    return True

def main():
    """Main entry point for the skill"""
    if len(sys.argv) < 2:
        print("Usage: python main.py <weather_file> [output_dir]")
        print("\nSupported formats: .csv (TMYx), .epw (EnergyPlus Weather)")
        print("\nExamples:")
        print("  python main.py USA_CO_Akron.csv")
        print("  python main.py USA_CO_Akron.epw")
        print("  python main.py weather_data.epw ./converted")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    success = convert_tmyx_to_tmy3(input_file, output_dir)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
