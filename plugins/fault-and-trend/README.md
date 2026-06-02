# fault-and-trend

Live fault triage and trend anomaly detection for SkySpark. Pulls active spark data and point history directly — no manual CSV export needed.

## Prerequisites

### 1. Claude Code CLI
Install Node.js (if not already installed):
```
winget install OpenJS.NodeJS.LTS
```
Then install Claude Code:
```
npm install -g @anthropic-ai/claude-code
```

### 2. Python 3.8+
All scripts use the Python standard library — no additional packages required. Verify your installation:
```
python --version
```

### 3. skyspark-dev plugin
This plugin requires skyspark-dev to be installed and configured. skyspark-dev handles the SkySpark connection and provides the MCP tools this plugin calls. Without it, neither command will work.

**To install skyspark-dev**, clone the repo and follow its setup instructions:
```
git clone https://github.com/CEG-Solutions/ceg-skyspark-architecture
```

**To configure your credentials**, copy the template file included in this plugin:

```
copy plugins\fault-and-trend\skyspark-dev.local.md.example %USERPROFILE%\.claude\skyspark-dev.local.md
```

Then open `%USERPROFILE%\.claude\skyspark-dev.local.md` and fill in your own values:
```
skyspark_uri: "http://your-skyspark-server.com"
skyspark_user: "your_username"
skyspark_password: "your_password"
write_enabled: false
ssl_verify: false
```

> This file is gitignored and must never be committed or shared. Each person sets up their own copy with their own credentials.

---

## Installation

Clone the ceg-plugins repo (if you haven't already):
```
git clone https://github.com/CEG-Solutions/ceg-plugins
```

Launch Claude Code with both plugins loaded:
```
claude --plugin-dir "path\to\ceg-skyspark-architecture\plugins\skyspark-dev" --plugin-dir "path\to\ceg-plugins\plugins\fault-and-trend"
```

### Verify the connection
Before running either command, confirm SkySpark is reachable by asking Claude:
```
What SkySpark projects are available?
```
Claude will call `list_projects` and show you the available projects. If this fails, check your credentials file and that skyspark-dev loaded correctly.

---

## Commands

### `/fault-and-trend:triage`

Queries active sparks on the current SkySpark project and produces a prioritized fault report ranked by equipment severity, duration, and fault pattern.

**Usage:**
```
/fault-and-trend:triage
/fault-and-trend:triage "Building A"
```

**What it asks you:**
1. Which project to connect to (once per session, if not already connected)
2. Which building — type a name or "all" for the whole project
3. How far back to look for faults (e.g. "last 30 days") — used as the actual query window, defaults to 30 days
4. Any equipment to exclude (e.g. known offline units)

**What it produces:**
- An executive summary covering total faults, dominant patterns, and equipment scope
- Priority-grouped findings with fault event counts, cumulative hours, likely causes, and recommended actions
- A summary action table at the end: Priority | Equipment | Action

> **Note:** Triage requires fault rules to be configured and evaluated in the SkySpark project. If no faults are found, the command will report that and stop cleanly.

---

### `/fault-and-trend:trends`

Pulls interval history for a specific piece of equipment and detects anomalies: stuck sensors, statistical outliers, and missing data gaps.

**Usage:**
```
/fault-and-trend:trends
/fault-and-trend:trends "AHU-01"
```

**What it asks you:**
1. Which project to connect to (once per session, if not already connected)
2. Which equipment to analyze (browse by site if no argument passed)
3. Date range (defaults to last month)
4. Any known outages to exclude
5. Occupied hours for after-hours detection — type "24/7" for hospitals or continuous facilities (defaults to 6 AM – 10 PM)

**What it produces:**
- An executive summary with the single most important finding
- High and Medium severity sections with likely cause and recommended action per finding
- Coordinated multi-point events (e.g., AHU shutdowns) identified as a single pattern rather than separate anomalies
- A summary table at the end: Priority | Finding | Action

---

## Scripts

| Script | Purpose |
|--------|---------|
| `triage_faults.py` | Parses fault CSV and ranks by priority |
| `detect_anomalies.py` | Detects anomalies in interval or summary trend data |
| `combine_point_csvs.py` | Joins per-point CSVs from export_equip_history into one wide CSV; automatically detects and corrects COV timestamp inflation when one point records at sub-minute resolution |

All scripts use Python standard library only — no pip installs needed.

---

## Notes for testers

- **Projects without spark rules configured** — triage will report that no faults were found and stop. This is expected; fault rules must be set up and evaluated in SkySpark before triage can run.
- **Equipment showing as `unknown` type** — the classification uses Haystack tags (`ahu`, `vav`, `fcu`, `boiler`, `chiller`, `pump`, `elec`, `meter`, etc.) with equipment name keyword matching as a fallback. Equipment with none of these tags will be `unknown` and ranked Low by default. Check the Haystack tags on that record in SkySpark.
- **COV points in trend exports** — if a point records change-of-value at sub-minute resolution (e.g., a setpoint), `combine_point_csvs.py` will automatically detect this and snap all timestamps to the dominant interval. You'll see a message like `COV inflation detected — snapping to 300s interval` in the output.
- **After-hours anomalies on 24/7 facilities** — when asked for occupied hours, type `24/7` to disable after-hours detection entirely for hospitals or continuously-operated buildings.

---

## Author

Korine Bucher — Iconergy/CEG
