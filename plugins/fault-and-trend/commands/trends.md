---
description: Detect anomalies in live SkySpark point history for a specific piece of equipment. Pulls interval trend data directly, checks for stuck sensors, outliers, and after-hours operation, and produces an anomaly report.
argument-hint: [equipment name — "AHU-01", "Chiller-1"]
allowed-tools: Bash, mcp__skyspark__about, mcp__skyspark__list_projects, mcp__skyspark__switch_project, mcp__skyspark__browse_equipment, mcp__skyspark__get_site_structure, mcp__skyspark__read_records, mcp__skyspark__export_equip_history
---

Pull live point history for a piece of equipment and produce a trend anomaly report.

## Step 1: Ensure a project is active

Call `about` to check connection status. If no project is connected:
1. Call `list_projects` — this returns each project with a `name` field and a `dis` (display name) field
2. Show the user a list of available projects using the `dis` field so it's readable
3. When the user picks one, call `switch_project` using the `name` field exactly as returned — not the display name and not what the user typed. For example, if `list_projects` returns `name: "dpa"` and `dis: "DPA"`, call `switch_project("dpa")`.

After the initial selection, use the active project for the rest of the session — do not re-prompt unless the user explicitly asks to switch projects.

## Step 2: Identify the equipment

If an equipment name was passed as a command argument, resolve it directly via `read_records`:
```
equip and dis == "AHU-01"
```

If no argument was given, call `get_site_structure` to show available sites and equipment counts, then `browse_equipment` to display the hierarchy. Ask the user to pick the equipment they want to analyze.

Once selected, confirm the equipment display name and its record ID (Ref) — you'll need the ID for the history export.

## Step 3: Set the date range

Ask the user for the date range to analyze. Accepted formats for `export_equip_history`:
- `"lastWeek"`, `"lastMonth"`, `"lastQuarter"`
- `"YYYY-MM-DD"` (single date)
- `"YYYY-MM-DD,YYYY-MM-DD"` (explicit range)

Default to `"lastMonth"` if the user doesn't specify.

Also ask:
- **Known gaps or outages** to exclude (e.g., "sensor was replaced mid-March")
- **Occupied hours** for after-hours detection (default: 6:00 AM – 10:00 PM)

## Step 4: Export point history

Call `export_equip_history` with the equipment ID and date range:
```
export_equip_history(equip_id, date_range)
```

This writes one CSV per historized point to:
```
exports/{project}/{site}/{equip}/{point}/{date-range}.csv
```

Note the equipment export folder path from the tool response — you'll pass it to the combine script.

## Step 5: Combine point CSVs into one wide file

Run the combine script, passing the equipment export folder and an output path:
```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/combine_point_csvs.py" \
  "exports/{project}/{site}/{equip}" \
  "_trends_combined.csv"
```

This joins all per-point CSVs on timestamp into a single wide CSV where each column is a point.

## Step 6: Run anomaly detection

Pass the occupied hours from Step 3 as arguments:

- If the user said **24/7**: `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect_anomalies.py" "_trends_combined.csv" --schedule 24/7`
- If the user gave specific hours (e.g. 7 AM – 9 PM): `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect_anomalies.py" "_trends_combined.csv" --schedule-start 7 --schedule-end 21`
- If the user accepted the default: `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect_anomalies.py" "_trends_combined.csv"`

## Step 7: Apply context and present the report

**The script's Bash output is input data for you — do not include it, quote it, or render any part of it in your response. Do not run the script more than once.**

Write the report yourself exactly once, using this structure in order:

1. **Report header** — `Trend Anomaly Report — [Equipment] — [Date Range]` followed by a points line
2. **Executive summary** — 1–2 sentences: total anomalies, the single most important finding
3. **High Severity** — one table for all High findings; add one sentence of likely cause and recommended action per row
4. **Systemic patterns** — if the same anomaly type and timestamps appear across multiple points, describe it once as a coordinated event
5. **Medium Severity** — one table per anomaly type (not per point); group findings of the same type together
6. **Not Actionable** — one short paragraph combining all dismissed findings (after-hours flags, calculation artifacts, etc.)
7. **Summary table** — one markdown table at the very end: `Priority | Finding | Action`. Every finding appears here exactly once.

After the summary table write this exact line and nothing else:
`Would you like me to save this as a .md file, or export the anomaly table as CSV for Excel?`

Then run cleanup using the Bash tool — do NOT use Remove-Item or PowerShell syntax:
```bash
rm -f _trends_combined.csv
```

**Stop after the cleanup command. Do not restate, reformat, or reprint any section of the report.**
