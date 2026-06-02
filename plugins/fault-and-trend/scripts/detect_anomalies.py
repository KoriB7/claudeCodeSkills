"""
Detect anomalies in SkySpark trend data exports (CSV format).
Handles both:
  - Summary-level data: monthly min/max/avg tables
  - Interval data: 15-minute or hourly time-series

Usage:
  python detect_anomalies.py <csv_file>
  python detect_anomalies.py <csv_file> --schedule 24/7
  python detect_anomalies.py <csv_file> --schedule-start 7 --schedule-end 21
  cat trends.csv | python detect_anomalies.py

Options:
  --schedule 24/7        Disable after-hours detection entirely (hospitals, 24/7 facilities)
  --schedule-start HOUR  Occupied hours start, 0-23 (default: 6)
  --schedule-end HOUR    Occupied hours end, 0-23 (default: 22)
"""

import sys
import csv
import io
import re
import statistics
from datetime import datetime

TIMESTAMP_FORMATS = [
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%d %H:%M:%S',
    '%m/%d/%Y %H:%M',
    '%Y-%m-%d %H:%M',
    '%m/%d/%Y %H:%M:%S',
]

DATE_ONLY_FORMATS = ['%Y-%m-%d', '%m/%d/%Y', '%B', '%b']


def parse_value(val_str):
    """Parse a numeric value, stripping units like lb/h, kW, °F, etc."""
    if not val_str or str(val_str).strip().lower() in ('', 'empty', 'null', 'na', 'nan', '-', 'n/a'):
        return None
    cleaned = re.sub(r'[^\d.\-]', '', str(val_str).strip())
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def parse_timestamp(ts_str):
    """Parse a timestamp string into a datetime, trying multiple common formats.

    Strips timezone offsets before parsing since strptime doesn't handle them.
    Returns None if the string is empty or no format matches.
    """
    if not ts_str:
        return None
    ts_str = str(ts_str).strip()
    # Strip timezone offset (e.g. -06:00, +00:00, Z) so strptime formats work
    ts_str = re.sub(r'([+-]\d{2}:\d{2}|Z)$', '', ts_str)
    for fmt in TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            pass
    return None


def detect_data_type(headers, rows):
    """Determine whether the CSV contains interval or summary-level data.

    Returns ('interval', date_col) if the first two consecutive timestamps are
    <= 1 hour apart, otherwise ('summary', date_col). Falls back to 'summary'
    if timestamps can't be parsed or fewer than 2 rows are present.
    """
    date_col = None
    for h in headers:
        if any(kw in h.lower().strip() for kw in ['ts', 'timestamp', 'time', 'date', 'month']):
            date_col = h
            break

    if not date_col or len(rows) < 2:
        return 'summary', date_col

    timestamps = []
    for row in rows[:5]:
        ts = parse_timestamp(row.get(date_col, ''))
        if ts:
            timestamps.append(ts)

    if len(timestamps) >= 2:
        delta = abs((timestamps[1] - timestamps[0]).total_seconds())
        if delta <= 3600:
            return 'interval', date_col

    return 'summary', date_col


def detect_summary_anomalies(headers, rows, date_col):
    """Detect anomalies in summary-level data (monthly or daily aggregates).

    Checks each value column for missing/zero periods and statistical outliers
    (> 2.5 standard deviations from the column mean). Missing periods are
    aggregated into one finding per column rather than one per row.
    Returns (anomalies, normal_points).
    """
    anomalies = []
    normal_points = []
    label_cols = {'month', 'site', 'building', 'equip', 'name', 'location'}
    value_cols = [
        h for h in headers
        if h != date_col and h.lower().strip() not in label_cols
    ]

    for col in value_cols:
        entries = []
        for row in rows:
            raw = row.get(col, '')
            val = parse_value(raw)
            label = row.get(date_col, '') if date_col else ''
            entries.append((label, val, raw))

        actual = [(d, v) for d, v, _ in entries if v is not None and v != 0]
        zeros = [(d, r) for d, v, r in entries if v is None or v == 0]

        if len(actual) < 2:
            if zeros:
                anomalies.append({
                    'severity': 'Medium',
                    'point': col,
                    'type': 'No Data',
                    'when': 'All periods',
                    'description': f'No valid readings found — meter may be offline or data not collected',
                })
            continue

        vals = [v for _, v in actual]
        mean = statistics.mean(vals)
        stdev = statistics.stdev(vals) if len(vals) >= 3 else 0

        col_anomalies = []

        if mean > 0 and zeros:
            periods = [label for label, _ in zeros]
            if len(periods) <= 3:
                period_str = ', '.join(p or 'Unknown' for p in periods)
            else:
                period_str = ', '.join(p or 'Unknown' for p in periods[:3]) + f' (+{len(periods) - 3} more)'
            col_anomalies.append({
                'severity': 'High',
                'point': col,
                'type': 'Missing/Zero Reading',
                'when': f'{len(zeros)} of {len(entries)} periods',
                'description': (
                    f'{len(zeros)} period(s) show missing or zero data '
                    f'(avg in valid periods: {mean:.1f}) — '
                    f'possible meter issue or data gap. Periods: {period_str}'
                ),
            })

        if stdev > 0:
            for date_label, val in actual:
                if abs(val - mean) / stdev > 2.5:
                    direction = 'high' if val > mean else 'low'
                    col_anomalies.append({
                        'severity': 'Medium',
                        'point': col,
                        'type': 'Statistical Outlier',
                        'when': date_label or 'Unknown period',
                        'description': (
                            f'Unusually {direction} ({val:.1f} vs avg {mean:.1f}) — '
                            f'verify reading or check for equipment event'
                        ),
                    })

        if col_anomalies:
            anomalies.extend(col_anomalies)
        else:
            normal_points.append(col)

    return anomalies, normal_points


def detect_interval_anomalies(headers, rows, date_col, schedule_start=6, schedule_end=22):
    """Detect anomalies in interval time-series data (15-min or hourly readings).

    Runs four checks per point column:
      - Data gaps: flags if >= 10% of readings are null, as one aggregated finding
      - Stuck sensor: flags if the last 8 consecutive non-null values are identical
      - Statistical outliers: flags readings > 3 std deviations from the mean,
        grouping consecutive outliers within 1 hour into a single event
      - After-hours operation: flags active readings outside schedule_start/schedule_end

    Pass schedule_start=0, schedule_end=24 to disable after-hours detection for
    24/7 facilities. Returns (anomalies, normal_points).
    """
    anomalies = []
    normal_points = []
    label_cols = {'site', 'building', 'equip', 'name', 'location'}
    value_cols = [
        h for h in headers
        if h != date_col and h.lower().strip() not in label_cols
    ]

    for col in value_cols:
        entries = []
        for row in rows:
            ts = parse_timestamp(row.get(date_col, '') if date_col else '')
            val = parse_value(row.get(col, ''))
            entries.append((ts, val))

        actual_vals = [v for _, v in entries if v is not None]
        if len(actual_vals) < 4:
            continue

        mean = statistics.mean(actual_vals)
        stdev = statistics.stdev(actual_vals) if len(actual_vals) >= 3 else 0
        col_anomalies = []

        # Detect data gaps — one aggregated finding per point, not one per missing reading
        none_count = sum(1 for _, v in entries if v is None)
        if none_count > 0:
            pct_missing = none_count / len(entries) * 100
            if pct_missing >= 10:
                gap_ts = [ts for ts, v in entries if v is None and ts is not None]
                if gap_ts:
                    first = min(gap_ts).strftime('%Y-%m-%d')
                    last = max(gap_ts).strftime('%Y-%m-%d')
                    when = f'{first} to {last}' if first != last else first
                else:
                    when = 'Throughout period'
                col_anomalies.append({
                    'severity': 'High',
                    'point': col,
                    'type': 'Missing/Zero Reading',
                    'when': when,
                    'description': (
                        f'{none_count} of {len(entries)} readings missing '
                        f'({pct_missing:.0f}%) — '
                        f'possible BACnet/historian connectivity issue or point mapping problem'
                    ),
                })

        non_none = [v for _, v in entries if v is not None]
        if len(non_none) >= 8:
            recent = non_none[-8:]
            if len(set(recent)) == 1 and recent[0] != 0:
                col_anomalies.append({
                    'severity': 'High',
                    'point': col,
                    'type': 'Stuck Sensor',
                    'when': 'Recent readings',
                    'description': (
                        f'Same value ({recent[0]}) repeated for last {len(recent)} intervals — '
                        f'sensor may be failed or frozen'
                    ),
                })

        if stdev > 0:
            # Collect outlier timestamps, then group consecutive events (gap <= 1 hour)
            raw_outliers = []
            for ts, val in entries:
                if val is None:
                    continue
                if abs(val - mean) / stdev > 3.0:
                    raw_outliers.append((ts, val, 'spike' if val > mean else 'drop'))

            if raw_outliers:
                raw_outliers.sort(key=lambda x: x[0] or datetime.min)
                events = []
                cur = None
                for ts, val, direction in raw_outliers:
                    if (cur is None or cur['direction'] != direction
                            or (ts and cur['end'] and
                                (ts - cur['end']).total_seconds() > 3600)):
                        if cur:
                            events.append(cur)
                        cur = {'direction': direction, 'start': ts, 'end': ts,
                               'count': 1, 'peak': val}
                    else:
                        cur['count'] += 1
                        cur['end'] = ts
                        if abs(val - mean) > abs(cur['peak'] - mean):
                            cur['peak'] = val
                if cur:
                    events.append(cur)

                for ev in events:
                    s = ev['start'].strftime('%Y-%m-%d %H:%M') if ev['start'] else '?'
                    e = ev['end'].strftime('%Y-%m-%d %H:%M') if ev['end'] and ev['end'] != ev['start'] else ''
                    when = f'{s} to {e}' if e else s
                    cnt = f' ({ev["count"]} readings)' if ev['count'] > 1 else ''
                    col_anomalies.append({
                        'severity': 'Medium',
                        'point': col,
                        'type': f'Value {ev["direction"].title()}',
                        'when': when,
                        'description': (
                            f'Unusual {ev["direction"]}{cnt} '
                            f'(peak {ev["peak"]:.1f} vs avg {mean:.1f})'
                        ),
                    })

        if mean > 0:
            after_hours = [
                ts for ts, val in entries
                if ts and val and val > mean * 0.2
                and (ts.hour < schedule_start or ts.hour >= schedule_end)
            ]
            if len(after_hours) >= 3:
                col_anomalies.append({
                    'severity': 'Medium',
                    'point': col,
                    'type': 'After-Hours Operation',
                    'when': f'Outside {schedule_start:02d}:00–{schedule_end:02d}:00',
                    'description': (
                        f'Active values during {len(after_hours)} unoccupied-hours intervals — '
                        f'verify schedule or investigate unintended operation'
                    ),
                })

        if col_anomalies:
            anomalies.extend(col_anomalies)
        else:
            normal_points.append(col)

    return anomalies, normal_points


def format_report(anomalies, normal_points, data_type, building='[Building/Point Name]', date_range='[Date Range]'):
    """Render anomaly detection results as a markdown report string."""
    severity_order = {'High': 0, 'Medium': 1, 'Low': 2}
    anomalies.sort(key=lambda a: severity_order.get(a['severity'], 2))

    lines = [
        f'## Trend Anomaly Report — {building} — {date_range}',
        '',
        f'**Data type detected:** {data_type.title()}-level  |  '
        f'**Anomalies found:** {len(anomalies)}  |  '
        f'**Points that look normal:** {len(normal_points)}',
        '',
        '---',
        '',
    ]

    if anomalies:
        lines += [
            '### Anomalies Found',
            '',
            '| Severity | Point | Anomaly Type | When | Description |',
            '|----------|-------|--------------|------|-------------|',
        ]
        for a in anomalies:
            lines.append(
                f'| **{a["severity"]}** | {a["point"]} | {a["type"]} | {a["when"]} | {a["description"]} |'
            )
        lines.append('')
    else:
        lines += ['### No Anomalies Detected', '', 'All points appear within normal ranges.', '']

    if normal_points:
        lines += [
            '---',
            '',
            '### Points That Look Normal',
            '',
            ', '.join(normal_points),
            '',
        ]

    lines += [
        '---',
        '',
        '### Notes',
        '- Review **High** severity items first — these often indicate equipment failure or data gaps',
        '- **Medium** anomalies may be explainable by known events (maintenance, setpoint changes)',
        '- Provide known outage context before investigation to avoid false positives',
    ]

    return '\n'.join(lines)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_file', nargs='?', help='CSV file to analyze (reads stdin if omitted)')
    parser.add_argument('--schedule-start', type=int, default=6, metavar='HOUR',
                        help='Occupied hours start 0-23 (default 6)')
    parser.add_argument('--schedule-end', type=int, default=22, metavar='HOUR',
                        help='Occupied hours end 0-23 (default 22)')
    parser.add_argument('--schedule', choices=['24/7'],
                        help='Pass "24/7" to disable after-hours detection entirely')
    args = parser.parse_args()

    if args.schedule == '24/7':
        schedule_start, schedule_end = 0, 24
    else:
        schedule_start, schedule_end = args.schedule_start, args.schedule_end

    csv_text = open(args.csv_file, encoding='utf-8', errors='replace').read() if args.csv_file else sys.stdin.read()
    reader = csv.DictReader(io.StringIO(csv_text))
    headers = reader.fieldnames or []
    rows = list(reader)

    data_type, date_col = detect_data_type(headers, rows)

    if data_type == 'summary':
        anomalies, normal_points = detect_summary_anomalies(headers, rows, date_col)
    else:
        anomalies, normal_points = detect_interval_anomalies(
            headers, rows, date_col,
            schedule_start=schedule_start, schedule_end=schedule_end,
        )

    print(format_report(anomalies, normal_points, data_type))
