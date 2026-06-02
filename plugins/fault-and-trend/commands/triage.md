---
description: Triage and prioritize active SkySpark faults for the current project. Queries live spark data, ranks faults by equipment severity and duration, and produces a client-ready prioritized report.
argument-hint: [building name — "DHHA EastSide", "Wintrust Tower"]
allowed-tools: Bash, mcp__skyspark__about, mcp__skyspark__list_projects, mcp__skyspark__switch_project, mcp__skyspark__eval_axon, mcp__skyspark__get_site_structure, mcp__skyspark__read_records
---

Query active SkySpark faults and produce a prioritized triage report.

## Step 1: Ensure a project is active

Call `about` to check connection status. If no project is connected:
1. Call `list_projects` — this returns each project with a `name` field and a `dis` (display name) field
2. Show the user a list of available projects using the `dis` field so it's readable
3. When the user picks one, call `switch_project` using the `name` field exactly as returned — not the display name and not what the user typed. For example, if `list_projects` returns `name: "dpa"` and `dis: "DPA"`, call `switch_project("dpa")`.

After the initial selection, use the active project for the rest of the session — do not re-prompt unless the user explicitly asks to switch projects.

## Step 2: Gather report context

Ask the user these questions exactly as written — do not generate lists, menus, or options. Wait for plain text responses.

1. **"Which building? Type a name (e.g. 'Pavilion A', 'Eastside Clinic') or type 'all' for the whole project."**
2. **"How far back should I look for faults? (e.g. 'last 30 days', 'last 7 days', 'last month') — press Enter to use 30 days."**
3. **"Any equipment to exclude? (e.g. 'RTU-3 was offline for maintenance') — press Enter to skip."**

Convert the date range answer to an Axon span for use in Step 4:
- "last 30 days" or default → `today()-30day..today()`
- "last 7 days" / "last week" → `today()-7day..today()`
- "last month" → `today()-30day..today()`
- A specific month like "April 2026" → `2026-04-01..2026-04-30`

If a building name was passed as a command argument, skip question 1 and use that value directly.

## Step 3: Resolve building filter and gather site context

If the user provided a building name, find its site record to use as a filter:

```axon
readAll(site).findAll(s => s->dis.lower.contains("building a"))
```

Adjust the search string to match whatever the user provided. Then:

- **If exactly one site matches** — confirm the match with the user before continuing: _"Found: [site dis]. Is this the right building?"_
- **If multiple sites match** — list all matches and ask the user to pick one by name. Do not silently pick the closest match.
- **If no sites match** — tell the user and ask them to retype the building name or type 'all'.

Once the site ID is confirmed, call `get_site_structure` with that site ID to get equipment counts by type (AHUs, VAVs, FCUs, etc.). Include these counts in the executive summary so the reader understands the scope of equipment covered.

If the user wants all buildings or didn't specify one, call `get_site_structure` without a filter to get project-wide counts.

## Step 4: Query active sparks with equipment type enrichment

This project uses `ruleSparks(span)` — the same function that powers the SkySpark Spark app. It is called on a grid of equipment records and returns the sparks that fired within the given time span.

**If filtering to one building**, use the confirmed site display name from Step 3 and the span from Step 2. Use the `siteRef->dis==` pattern exactly as the SkySpark Spark app does internally — this catches all equipment regardless of which specific ref they use, whereas filtering by site ID misses equipment with sub-site refs:

```axon
readAll(siteRef->dis=="Pavilion A").ruleSparks(today()-30day..today()).map(spk => do
  // Some projects have targetRef → point → equipRef (point-targeted sparks)
  // Others have targetRef → equip directly (equipment-targeted sparks)
  // Try equipRef hop first; fall back to targetRef itself as the equip record
  equipRefId: try spk->targetRef->equipRef catch null
  equipRec: if(equipRefId != null)
    try readById(equipRefId) catch null
  else
    try readById(spk->targetRef) catch null
  equipName: if(equipRec != null) equipRec->navName else (try spk->targetRef->navName catch "Unknown")
  equipType: if(equipRec != null)
    if(equipRec.has("ahu") or equipRec.has("rtu")) "ahu"
    else if(equipRec.has("vav") or equipRec.has("vma")) "vav"
    else if(equipRec.has("fcu")) "fcu"
    else if(equipRec.has("boiler")) "boiler"
    else if(equipRec.has("chiller")) "chiller"
    else if(equipRec.has("pump")) "pump"
    else if(equipRec.has("coolingTower")) "tower"
    else if(equipRec.has("elec") or equipRec.has("meter")) "meter"
    else "unknown"
  else "unknown"
  {rule: spk->ruleRef->dis, dur: spk->dur, equip: equipName, equipType: equipType}
end)
```

Replace `"Pavilion A"` with the exact confirmed site display name from Step 3 (preserve the original capitalisation — this is a case-sensitive exact match) and `today()-30day..today()` with the span from Step 2.

**If querying all buildings**, use `readAll(equip)` as the base:

```axon
readAll(equip).ruleSparks(today()-30day..today()).map(spk => do
  equipRefId: try spk->targetRef->equipRef catch null
  equipRec: if(equipRefId != null)
    try readById(equipRefId) catch null
  else
    try readById(spk->targetRef) catch null
  equipName: if(equipRec != null) equipRec->navName else (try spk->targetRef->navName catch "Unknown")
  equipType: if(equipRec != null)
    if(equipRec.has("ahu") or equipRec.has("rtu")) "ahu"
    else if(equipRec.has("vav") or equipRec.has("vma")) "vav"
    else if(equipRec.has("fcu")) "fcu"
    else if(equipRec.has("boiler")) "boiler"
    else if(equipRec.has("chiller")) "chiller"
    else if(equipRec.has("pump")) "pump"
    else if(equipRec.has("coolingTower")) "tower"
    else if(equipRec.has("elec") or equipRec.has("meter")) "meter"
    else "unknown"
  else "unknown"
  {rule: spk->ruleRef->dis, dur: spk->dur, equip: equipName, equipType: equipType}
end)
```

Map the output fields to the triage script's expected CSV columns:

| Query output field | CSV column | Notes |
|---|---|---|
| `rule` | Rule | Rule display name, dereferenced from `ruleRef` |
| `dur` | Duration | Fault duration — e.g. "3.54day", "16.98hr" |
| `equip` | Equips | Equipment display name via `targetRef→equipRef→navName` |
| `equipType` | EquipType | Haystack-derived equipment type |

Write the mapped data as a temp CSV at `_fault_triage_input.csv`.

## Step 5: Run the triage script

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/triage_faults.py" _fault_triage_input.csv
```

## Step 6: Apply context and present the report

**The script's Bash output is input data for you — do not include it, quote it, or render any part of it in your response. Do not run the script more than once.**

Write the report yourself exactly once, using this structure in order:

1. **Report header** — `Fault Triage Report — [Building] — [Date Range]` followed by a scope line (equipment counts from `get_site_structure`)
2. **Executive summary** — 2–3 sentences: total faults, most critical finding, overall pattern
3. **Priority groups** — one section per priority level (Priority 1, 2, 3). Each section contains:
   - Equipment and rule name
   - Fault event count and cumulative hours — only include rows where you have actual data; do not create placeholder rows with "—" or empty cells for units you have no specific data on
   - One paragraph: likely cause and recommended action
   - Group faults of the same rule across multiple units into one section — do not create one section per unit
4. **Summary Action List** — one markdown table: `Priority | Equipment | Action`

After the summary table write this exact line and nothing else:
`Would you like me to save this as a .md file, or export the fault table as CSV for Excel?`

Then run cleanup using the Bash tool — do NOT use Remove-Item or PowerShell syntax:
```bash
rm -f _fault_triage_input.csv
```

**Stop after the cleanup command. Do not restate, reformat, or reprint any section of the report.**
