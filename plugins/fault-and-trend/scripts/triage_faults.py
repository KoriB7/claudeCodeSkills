"""
Parse SkySpark fault/spark CSV export and produce a prioritized triage report.

Expected CSV columns (from SkySpark "Copy data as CSV" on the sparks/rules view,
or from the /fault-and-trend:triage command which builds this CSV from live MCP data):
  - Rule (fault name)
  - Duration (e.g., "6min", "8hr", "14.1hr", "1.34day")
  - Equips (equipment name)

Usage:
  python triage_faults.py <csv_file>
  echo "<csv_text>" | python triage_faults.py
"""

import sys
import csv
import re
import io

MAJOR_EQUIPMENT = [
    'chiller', 'boiler', 'ahu', 'air handler', 'air handling',
    'cooling tower', 'chw', 'chilled water', 'hot water', 'steam',
    'pump', 'rtu', 'rooftop', 'heat exchanger', 'hx', 'compressor',
    'condenser', 'evaporator', 'plant', 'central'
]

MINOR_EQUIPMENT = [
    'fcu', 'fan coil', 'vav', 'vma', 'variable air', 'unit heater',
    'exhaust fan', 'elec', 'meter', 'sensor', 'gauge', 'terminal'
]

# Haystack tag → equipment tier mapping (used when EquipType column is present)
_HAYSTACK_MAJOR = {'ahu', 'rtu', 'boiler', 'chiller', 'pump', 'plant', 'tower'}
_HAYSTACK_MINOR = {'vav', 'vma', 'fcu', 'terminal', 'elec', 'meter'}


def parse_duration_to_hours(duration_str):
    """Convert a SkySpark duration string to decimal hours.

    Accepts formats like '6min', '8hr', '14.1hr', '1.34day'. Returns 0 if
    the string is empty or no recognizable pattern is found.
    """
    if not duration_str:
        return 0
    s = str(duration_str).strip().lower()
    for pattern, multiplier in [
        (r'(\d+\.?\d*)\s*day', 24),
        (r'(\d+\.?\d*)\s*hr', 1),
        (r'(\d+\.?\d*)\s*min', 1 / 60),
        (r'(\d+\.?\d*)\s*sec', 1 / 3600),
    ]:
        m = re.search(pattern, s)
        if m:
            return float(m.group(1)) * multiplier
    return 0


def classify_equipment(equip_name, equip_type=None):
    """Return 'major', 'minor', or 'unknown' equipment tier.

    Checks the Haystack-derived equip_type tag first (most reliable). Falls back
    to keyword matching on the equipment display name if the type is absent or
    unrecognized — handles projects where Haystack tags are incomplete.
    """
    if equip_type and equip_type.strip().lower() not in ('', 'unknown'):
        t = equip_type.strip().lower()
        if t in _HAYSTACK_MAJOR:
            return 'major'
        if t in _HAYSTACK_MINOR:
            return 'minor'
    name = equip_name.lower()
    for kw in MAJOR_EQUIPMENT:
        if kw in name:
            return 'major'
    for kw in MINOR_EQUIPMENT:
        if kw in name:
            return 'minor'
    return 'unknown'


def classify_fault_pattern(rule_name, duration_hours):
    """Classify a fault rule into a pattern category based on keywords in the rule name.

    Returns (fault_type, why_it_matters). fault_type is one of:
    'schedule', 'controls', 'sensor', 'equipment', 'general'.
    Controls faults that have persisted >= 24 hours get a more urgent description.
    """
    rule = rule_name.lower()
    if any(kw in rule for kw in ['schedule', 'outside', 'unoccupied', 'after hour', 'designated']):
        return 'schedule', 'Equipment running outside scheduled hours — check occupancy schedule'
    if any(kw in rule for kw in ['setpoint', 'above', 'below', 'dat', 'sat', 'deviation']):
        if duration_hours >= 24:
            return 'controls', 'Persistent setpoint deviation — likely controls or mechanical issue'
        return 'controls', 'Setpoint deviation — monitor for recurrence'
    if any(kw in rule for kw in ['sensor', 'voltage', 'discrepancy', 'stuck', 'offline']):
        return 'sensor', 'Sensor or measurement issue — verify equipment and wiring'
    if duration_hours >= 24:
        return 'equipment', 'Extended fault duration — likely equipment or controls issue'
    return 'general', 'Fault detected — review for root cause'


def assign_priority(equip_tier, duration_hours, fault_type):
    """Return 'High', 'Medium', or 'Low' priority for a fault.

    Major equipment (AHU, chiller, boiler, etc.) is always High regardless of
    duration. Minor equipment (VAV, FCU, etc.) or any fault active 24h+ is Medium.
    Schedule faults active 8h+ are Medium even on minor equipment.
    """
    if equip_tier == 'major':
        return 'High'
    if equip_tier == 'minor' and duration_hours >= 24:
        return 'Medium'
    if fault_type == 'schedule' and duration_hours >= 8:
        return 'Medium'
    if duration_hours >= 24:
        return 'Medium'
    return 'Low'


def find_column(headers, candidates):
    """Find the first header containing any of the candidate substrings (case-insensitive).

    Returns the original header string (preserving its case) or None if no match.
    Used to handle CSV exports where column names vary slightly between SkySpark versions.
    """
    lower = [h.lower().strip() for h in headers]
    for candidate in candidates:
        for i, h in enumerate(lower):
            if candidate in h:
                return headers[i]
    return None


def triage_faults(csv_text):
    """Parse fault CSV text and return a prioritized list of fault dicts.

    Returns (faults, error). On success, faults is sorted High → Medium → Low
    then by descending duration, and error is None. On failure, faults is None
    and error is a descriptive string.
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    headers = reader.fieldnames or []

    rule_col = find_column(headers, ['rule', 'fault', 'name'])
    duration_col = find_column(headers, ['duration', 'dur'])
    equip_col = find_column(headers, ['equip', 'equipment', 'device'])
    equip_type_col = find_column(headers, ['equiptype', 'equip_type', 'type'])

    if not rule_col:
        return None, f"Could not find a Rule column. Columns found: {headers}"

    faults = []
    for row in reader:
        rule = row.get(rule_col, '').strip()
        if not rule:
            continue
        duration_str = row.get(duration_col, '') if duration_col else ''
        equip = row.get(equip_col, 'Unknown') if equip_col else 'Unknown'
        equip = re.sub(r'^\(i\)\s*', '', equip).strip()
        equip_type = row.get(equip_type_col, '') if equip_type_col else ''

        duration_hours = parse_duration_to_hours(duration_str)
        equip_tier = classify_equipment(equip, equip_type)
        fault_type, why = classify_fault_pattern(rule, duration_hours)
        priority = assign_priority(equip_tier, duration_hours, fault_type)

        faults.append({
            'rule': rule,
            'equip': equip,
            'duration_str': duration_str or 'Unknown',
            'duration_hours': duration_hours,
            'equip_tier': equip_tier,
            'fault_type': fault_type,
            'priority': priority,
            'why': why,
        })

    priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
    faults.sort(key=lambda f: (priority_order[f['priority']], -f['duration_hours']))
    return faults, None


def format_report(faults, building='[Building Name]', date_range='[Date Range]'):
    """Render the prioritized fault list as a markdown report string."""
    high = [f for f in faults if f['priority'] == 'High']
    medium = [f for f in faults if f['priority'] == 'Medium']
    low = [f for f in faults if f['priority'] == 'Low']

    lines = [
        f'## Fault Triage Report — {building} — {date_range}',
        '',
        f'**Total faults reviewed:** {len(faults)}  |  '
        f'**High:** {len(high)}  |  **Medium:** {len(medium)}  |  **Low:** {len(low)}',
        '',
        '---',
        '',
        '### Prioritized Fault Table',
        '',
        '| Priority | Rule | Equipment | Duration | Pattern | Why It Matters |',
        '|----------|------|-----------|----------|---------|----------------|',
    ]

    pattern_labels = {
        'schedule': 'Schedule',
        'controls': 'Controls/Setpoint',
        'sensor': 'Sensor',
        'equipment': 'Equipment',
        'general': 'General',
    }

    for f in faults:
        label = pattern_labels.get(f['fault_type'], f['fault_type'].title())
        lines.append(
            f'| **{f["priority"]}** | {f["rule"]} | {f["equip"]} | {f["duration_str"]} | {label} | {f["why"]} |'
        )

    lines += ['', '---', '', '### Recommended Next Steps', '']
    step = 1

    if high:
        equips = ', '.join(list(dict.fromkeys(f['equip'] for f in high))[:3])
        lines.append(f'{step}. **Address high-priority faults first** — Focus on: {equips}')
        step += 1

    schedule_faults = [f for f in faults if f['fault_type'] == 'schedule' and f['priority'] != 'Low']
    if schedule_faults:
        equips = ', '.join(list(dict.fromkeys(f['equip'] for f in schedule_faults))[:3])
        lines.append(
            f'{step}. **Review occupancy schedules** for: {equips} — '
            f'Confirm BAS schedule matches actual building hours'
        )
        step += 1

    controls_faults = [f for f in faults if f['fault_type'] == 'controls' and f['priority'] != 'Low']
    if controls_faults:
        equips = ', '.join(list(dict.fromkeys(f['equip'] for f in controls_faults))[:3])
        lines.append(
            f'{step}. **Investigate controls/setpoints** on: {equips} — '
            f'Check PID tuning and sensor calibration'
        )
        step += 1

    sensor_faults = [f for f in faults if f['fault_type'] == 'sensor']
    if sensor_faults:
        equips = ', '.join(list(dict.fromkeys(f['equip'] for f in sensor_faults))[:2])
        lines.append(f'{step}. **Verify sensors** on: {equips} — Inspect wiring and calibration')
        step += 1

    lines.append(f'{step}. **Log findings** and schedule follow-up review after corrections are made')

    return '\n'.join(lines)


if __name__ == '__main__':
    csv_text = open(sys.argv[1], encoding='utf-8', errors='replace').read() if len(sys.argv) > 1 else sys.stdin.read()
    faults, error = triage_faults(csv_text)
    if error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
    print(format_report(faults))
