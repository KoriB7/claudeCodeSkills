"""
Combine per-point CSV exports from skyspark-dev's export_equip_history into a
single wide-format CSV suitable for detect_anomalies.py.

Each point is exported as a separate CSV with two columns:
  timestamp, value (<unit>)

This script joins all point CSVs under an equipment folder on timestamp,
producing one wide CSV where each column is a point (by folder name).

When points have mismatched sampling rates (e.g., a COV setpoint at sub-minute
resolution alongside 5-minute interval data), timestamps are automatically snapped
to the dominant interval. This prevents a sparse matrix where regular-interval
points appear nearly 100% null against a dense COV timestamp spine.

Usage:
  python combine_point_csvs.py <equip_export_folder> [output.csv]

  If output.csv is omitted, writes to stdout.

Example:
  python combine_point_csvs.py exports/dhha/EastSide/AHU-01 _trends_combined.csv
"""

import sys
import csv
import os
import re
import statistics
from collections import defaultdict
from datetime import datetime, timedelta


def find_point_csvs(equip_folder):
    """Return {point_name: [sorted csv paths]} for all point subfolders."""
    point_data = {}
    try:
        entries = sorted(os.scandir(equip_folder), key=lambda e: e.name)
    except FileNotFoundError:
        return point_data

    for entry in entries:
        if not entry.is_dir():
            continue
        csvs = sorted(
            os.path.join(entry.path, f)
            for f in os.listdir(entry.path)
            if f.endswith('.csv') and not f.startswith('_')
        )
        if csvs:
            point_data[entry.name] = csvs
    return point_data


def read_point_csv(csv_path):
    """Read a two-column point CSV and return list of (timestamp_str, value_str)."""
    rows = []
    with open(csv_path, newline='', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if len(row) >= 2 and row[0].strip():
                rows.append((row[0].strip(), row[1].strip()))
    return rows


def _count_csv_rows(path):
    """Count data rows in a CSV file (excluding header) without reading values."""
    count = 0
    try:
        with open(path, encoding='utf-8', errors='ignore') as f:
            for i, _ in enumerate(f):
                if i > 0:
                    count += 1
    except OSError:
        pass
    return count


def _parse_ts(ts_str):
    """Parse a timestamp string into a naive datetime. Returns None on failure."""
    s = re.sub(r'([+-]\d{2}:\d{2}|Z)$', '', ts_str.strip())
    for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S',
                '%m/%d/%Y %H:%M:%S', '%Y-%m-%d %H:%M'):
        try:
            return datetime.strptime(s[:19], fmt[:19])
        except ValueError:
            pass
    return None


def _snap_ts(ts_str, interval_secs):
    """Round a timestamp string down to the nearest interval boundary."""
    dt = _parse_ts(ts_str)
    if dt is None:
        return ts_str
    interval = timedelta(seconds=int(interval_secs))
    ref = datetime(2000, 1, 1)
    snapped = ((dt - ref) // interval) * interval
    return (ref + snapped).strftime('%Y-%m-%dT%H:%M:%S')


def _sample_interval_secs(csv_paths, sample=15):
    """Estimate the sampling interval by inspecting the first few timestamps."""
    timestamps = []
    for path in csv_paths[:1]:
        rows = read_point_csv(path)
        for ts_str, _ in rows[:sample]:
            dt = _parse_ts(ts_str)
            if dt is not None:
                timestamps.append(dt)

    if len(timestamps) < 2:
        return None

    gaps = [
        (timestamps[i] - timestamps[i - 1]).total_seconds()
        for i in range(1, len(timestamps))
        if (timestamps[i] - timestamps[i - 1]).total_seconds() > 0
    ]
    return statistics.median(gaps) if gaps else None


def _infer_snap_interval(row_counts, point_data):
    """
    Return the interval in seconds to snap timestamps to, or None if all points
    have similar row counts and no snapping is needed.

    Triggers when any point has >5x the median row count — a strong signal that
    one point is COV-based (sub-minute resolution) while others are interval-based.
    """
    counts = list(row_counts.values())
    if len(counts) < 2:
        return None

    median_count = statistics.median(counts)
    max_count = max(counts)

    if median_count == 0 or max_count <= 5 * median_count:
        return None

    # Find a point near the median to sample its interval
    normal_point = None
    for name, count in row_counts.items():
        if 0.5 * median_count <= count <= 2 * median_count:
            normal_point = name
            break

    if normal_point is None:
        return None

    interval = _sample_interval_secs(point_data[normal_point])
    if interval is None:
        return None

    # Round to the nearest standard interval
    for std in (60, 300, 600, 900, 1800, 3600):
        if abs(interval - std) <= std * 0.25:
            return std

    return round(interval)


def combine(equip_folder):
    """
    Combine all point CSVs under equip_folder into a wide dict.

    Automatically detects and corrects COV timestamp inflation: if any point has
    >5x more rows than the median, all timestamps are snapped to the inferred
    common interval. Within each interval bucket the most recent value wins.

    Returns (combined_dict, point_names) where:
      combined_dict = {timestamp_str: {point_name: value_str}}
      point_names   = sorted list of point names
    """
    point_data = find_point_csvs(equip_folder)
    if not point_data:
        return {}, []

    # Count rows per point to detect sampling rate mismatch
    row_counts = {
        name: sum(_count_csv_rows(p) for p in paths)
        for name, paths in point_data.items()
    }

    snap_secs = _infer_snap_interval(row_counts, point_data)

    if snap_secs:
        dense = [n for n, c in row_counts.items() if c > 5 * statistics.median(list(row_counts.values()))]
        print(
            f'COV inflation detected — {", ".join(dense)} has high-frequency data. '
            f'Snapping all timestamps to {snap_secs}s interval.',
            file=sys.stderr,
        )

    combined = defaultdict(dict)
    for point_name, csv_paths in sorted(point_data.items()):
        for csv_path in csv_paths:
            for ts, val in read_point_csv(csv_path):
                key = _snap_ts(ts, snap_secs) if snap_secs else ts
                combined[key][point_name] = val

    point_names = sorted(point_data.keys())
    return combined, point_names


def write_combined_csv(combined, point_names, output_path=None):
    """Write the wide CSV to output_path or stdout."""
    timestamps = sorted(combined.keys())
    header = ['timestamp'] + point_names

    if output_path:
        out = open(output_path, 'w', newline='', encoding='utf-8')
    else:
        out = sys.stdout

    try:
        writer = csv.writer(out)
        writer.writerow(header)
        for ts in timestamps:
            row = [ts] + [combined[ts].get(p, '') for p in point_names]
            writer.writerow(row)
    finally:
        if output_path:
            out.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python combine_point_csvs.py <equip_folder> [output.csv]', file=sys.stderr)
        sys.exit(1)

    equip_folder = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    combined, point_names = combine(equip_folder)
    if not combined:
        print(f'No point CSVs found in: {equip_folder}', file=sys.stderr)
        sys.exit(1)

    write_combined_csv(combined, point_names, output_path)

    if output_path:
        print(
            f'Combined {len(point_names)} points across {len(combined)} timestamps → {output_path}',
            file=sys.stderr,
        )
