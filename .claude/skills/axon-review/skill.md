---
name: axon-review
version: 2.0.0
description: Reviews SkySpark Axon code for best practices, efficient Haystack querying, proper function design, performance optimization, and common pitfalls. Use when reviewing Axon scripts, functions, or queries in SkySpark/Project Haystack context.
category: guide
allowed-tools: Read, Grep, Glob
---

# SkySpark Axon Code Review

A comprehensive guide for reviewing Axon code written for SkySpark, the IoT/building automation platform by SkyFoundry. Axon is a functional programming language designed for working with Haystack data models and time-series data.

## Quick Start

When reviewing Axon code:
1. Check function design (names, parameters, documentation)
2. Evaluate query efficiency (avoid N+1 problems)
3. Verify error handling and null checks
4. Review performance implications
5. Assess date/time and timezone handling
6. Validate point naming and tag usage

## How It Works

1. **Read the code** using the allowed tools
2. **Apply the checklist** from each review category below
3. **Identify issues** categorized by severity (HIGH/MEDIUM/LOW)
4. **Provide recommendations** with code examples
5. **Generate summary** using the output format

---

## Review Checklist

### 1. Function Design

**Best Practices**:
- [ ] Function names are clear and descriptive
- [ ] Parameters have proper type hints
- [ ] Return types are documented
- [ ] Functions are focused and single-purpose
- [ ] Proper use of default parameters
- [ ] Doc strings explain purpose and usage

**✅ GOOD**: Clear function with doc and type hints
```axon
/*
 * Calculate average temperature for a given period
 * @param point Ref to temp sensor point
 * @param span DateSpan for calculation
 * @return Number average temperature
 */
(point: Ref, span: DateSpan) => do
  readAll(point).hisRead(span).hisRollup(avg, 1day).avg("v0")
end
```

**❌ BAD**: No documentation, unclear purpose
```axon
(p, s) => readAll(p).hisRead(s).hisRollup(avg, 1day).avg("v0")
```

### 2. Haystack Queries

**Best Practices**:
- [ ] Filters are as specific as possible
- [ ] Avoid overly broad queries (`readAll(site)`)
- [ ] Use indexed tags (id, ref, equipRef, siteRef)
- [ ] Minimize multiple `readAll()` calls
- [ ] Cache query results when reused
- [ ] Use `readAllStream()` for large datasets
- [ ] Use `readCount()` when only count is needed

**✅ GOOD**: Specific filter, single query
```axon
points: readAll(point and siteRef==@siteId and equipRef)
equipIds: points.unique("equipRef")
equips: readByIds(equipIds)
```

**❌ BAD**: Nested readAll (N+1 query problem)
```axon
readAll(equip).map(e =>
  readAll(point and equipRef==e->id)
)
```

**Key Query Functions**:
| Function | Use Case |
|----------|----------|
| `read(filter)` | Single record matching filter |
| `readAll(filter)` | All records matching filter |
| `readById(id)` | Single record by id |
| `readByIds(ids)` | Multiple records by id list |
| `readCount(filter)` | Count only (no data transfer) |
| `readAllStream(filter)` | Large datasets as stream |

### 3. Historical Data Operations

**Best Practices**:
- [ ] Use appropriate date/time ranges
- [ ] Specify explicit timezones
- [ ] Use `hisRollup()` for aggregations
- [ ] Consider memory impact of large reads
- [ ] Use streaming functions for large datasets
- [ ] Handle missing data gracefully
- [ ] Use `hisClip()` to remove edge timestamps

**✅ GOOD**: Explicit range and rollup
```axon
points.hisRead(lastWeek(), {tz: "America/Denver"})
      .hisRollup(avg, 1hr)
      .hisMap(v => v * 1.8 + 32) // Convert C to F
```

**❌ BAD**: No rollup on large dataset
```axon
points.hisRead(lastYear()) // Could return millions of records!
```

**✅ GOOD**: Handle missing data
```axon
temp: point.hisRead(today())
if (temp.isEmpty) return null
temp.avg("v0")
```

**Key History Functions**:
| Function | Purpose |
|----------|---------|
| `hisRead(range)` | Query history for range |
| `hisRollup(fn, interval)` | Aggregate over intervals |
| `hisRollupAuto()` | Auto-select best rollup |
| `hisMap(fn)` | Transform values |
| `hisFindAll(fn)` | Filter history rows |
| `hisJoin(grids)` | Join multiple histories |
| `hisClip()` | Remove leading/trailing rows |
| `hisWrite(grid)` | Write history data |
| `hisClear(range)` | Clear history items |
| `hisInterpolate()` | Fill null values |

**Date Span Functions**:
| Function | Range |
|----------|-------|
| `today()` | Current day |
| `yesterday()` | Previous day |
| `lastWeek()` | Previous 7 days |
| `lastMonth()` | Previous month |
| `lastYear()` | Previous year |
| `thisWeek()` | Current week sun..sat |
| `thisMonth()` | Current month 1st..end |
| `thisYear()` | Current year Jan-1..Dec-31 |
| `pastWeek()` | Last 7 days (today-7..today) |
| `pastMonth()` | Last 30 days |
| `pastYear()` | Last 365 days |

### 4. Data Manipulation

**Best Practices**:
- [ ] Use functional operations (map, filter, fold)
- [ ] Avoid unnecessary iterations
- [ ] Use `each()` for side effects only
- [ ] Use `map()` for transformations
- [ ] Chain operations efficiently
- [ ] Avoid mutating variables in loops

**✅ GOOD**: Functional pipeline
```axon
readAll(point and temp)
  .map(p => {dis: p->dis, val: p->curVal})
  .filter(p => p->val > 72)
  .sortCol("val")
  .reverse
```

**❌ BAD**: Imperative style with mutation
```axon
result: []
readAll(point and temp).each(p => do
  if (p->curVal > 72) result = result.add({dis: p->dis, val: p->curVal})
end)
result
```

**✅ GOOD**: Use fold for accumulation
```axon
points.hisRead(today())
      .fold(0, (acc, row) => acc + row->v0)
```

**Key Collection Functions**:
| Function | Purpose |
|----------|---------|
| `map(fn)` | Transform each item |
| `filter(fn)` | Keep items matching predicate |
| `find(fn)` | First item matching predicate |
| `findAll(fn)` | All items matching predicate |
| `fold(init, fn)` | Reduce to single value |
| `each(fn)` | Side effects only (returns null) |
| `eachWhile(fn)` | Iterate until non-null returned |
| `all(fn)` | True if all match |
| `any(fn)` | True if any match |
| `unique(col)` | Unique values in column |
| `flatMap(fn)` | Map and flatten results |

### 5. Error Handling

**Best Practices**:
- [ ] Validate inputs at function entry
- [ ] Use `try-catch` for external operations
- [ ] Return meaningful error messages
- [ ] Handle null/empty cases explicitly
- [ ] Use `trap()` for error recovery
- [ ] Log errors appropriately with `logErr()`

**✅ GOOD**: Input validation
```axon
(siteId: Ref, days: Number) => do
  if (not isRef(siteId)) throw "Invalid siteId: must be a Ref"
  if (days <= 0) throw "Invalid days: must be positive"

  site: trap(readById(siteId), null)
  if (site == null) throw "Site not found: " + siteId.toStr

  // ... rest of logic
end
```

**❌ BAD**: No validation or error handling
```axon
(siteId, days) => do
  readById(siteId).hisRead(pastDays(days))
end
```

**✅ GOOD**: Graceful degradation with logging
```axon
try
  connSyncCur(points)
catch (err)
  logErr("connSync", "Sync failed: " + err.toStr)
  return {status: "error", msg: err.toStr}
end
```

**Type Checking Functions**:
| Function | Checks For |
|----------|------------|
| `isRef(val)` | Reference type |
| `isNumber(val)` | Number type |
| `isStr(val)` | String type |
| `isBool(val)` | Boolean type |
| `isDict(val)` | Dict type |
| `isGrid(val)` | Grid type |
| `isList(val)` | List type |
| `isNull(val)` | Null value |
| `isNonNull(val)` | Non-null value |
| `isEmpty(val)` | Empty collection |

### 6. Performance Optimization

**Best Practices**:
- [ ] Minimize database reads
- [ ] Cache expensive computations
- [ ] Use streaming for large datasets
- [ ] Avoid nested loops over data
- [ ] Use `readAllStream()` for large queries
- [ ] Profile slow functions with timing

**✅ GOOD**: Batch read and group
```axon
allEquips: readAll(equip and siteRef)
allPoints: readAll(point and siteRef)
sites.each(site => do
  equips: allEquips.findAll(e => e->siteRef == site->id)
  points: allPoints.findAll(p => p->siteRef == site->id)
end)
```

**❌ BAD**: Multiple separate reads (N+1 problem)
```axon
sites.each(site => do
  equips: readAll(equip and siteRef==site->id)  // Query per site!
  points: readAll(point and siteRef==site->id)  // Another query per site!
end)
```

**✅ GOOD**: Use streams for large data
```axon
readAllStream(point and his)
  .filter(p => p.has("temp"))
  .limit(1000)
  .collect
```

### 7. Date/Time Handling

**Best Practices**:
- [ ] Always specify timezones explicitly
- [ ] Use appropriate date span functions
- [ ] Handle DST transitions correctly
- [ ] Use `DateSpan` for date ranges
- [ ] Consider site timezone vs UTC
- [ ] Test across month/year boundaries

**✅ GOOD**: Explicit timezone from site
```axon
site: readById(@siteId)
tz: site->tz
span: today(tz)
data: point.hisRead(span, {tz: tz})
```

**❌ BAD**: No timezone (uses server timezone)
```axon
data: point.hisRead(today())  // Timezone ambiguous!
```

**✅ GOOD**: Normalize timezones for comparison
```axon
// Convert all to site timezone before comparing
tz: site->tz
data1: points1.hisRead(span).toTimeZone(tz)
data2: points2.hisRead(span).toTimeZone(tz)
hisJoin([data1, data2])
```

### 8. Tag Operations

**Best Practices**:
- [ ] Use `has()` to check tag existence
- [ ] Use `get()` with defaults for safety
- [ ] Use `trap()` when accessing potentially missing tags
- [ ] Use proper tag naming conventions
- [ ] Validate tag types before operations
- [ ] Use marker tags appropriately

**✅ GOOD**: Safe tag access
```axon
val: point.get("curVal", 0)
if (point.has("unit")) unit: point->unit else unit: ""
```

**❌ BAD**: Unsafe tag access (throws if missing)
```axon
val: point->curVal  // Error if curVal doesn't exist!
```

**✅ GOOD**: Using trap for safety
```axon
val: trap(point->curVal, null)
if (val == null) return na()
```

### 9. Writing Data

**Best Practices**:
- [ ] Validate values before writing
- [ ] Check point is writable
- [ ] Use appropriate priority levels (1-17)
- [ ] Handle write failures gracefully
- [ ] Log write operations
- [ ] Use `pointAuto()` to release overrides

**Priority Levels**:
| Level | Purpose |
|-------|---------|
| 1 | Emergency override (highest) |
| 8 | Manual override (user level) |
| 10 | Schedule |
| 14 | Min/Max limits |
| 16 | Default (most common) |
| 17 | Relinquish default (lowest) |

**✅ GOOD**: Safe write with validation
```axon
(point: Ref, value: Number, level: Number: 16) => do
  pt: readById(point)
  if (not pt.has("writable"))
    throw "Point is not writable: " + pt->dis

  if (pt.has("maxVal") and value > pt->maxVal)
    throw "Value exceeds maximum: " + pt->maxVal.toStr

  try
    pointWrite(point, level, value)
    logInfo("write", "Write successful: " + pt->dis + " = " + value.toStr)
  catch (err)
    logErr("write", "Write failed: " + err.toStr)
    throw err
  end
end
```

**❌ BAD**: No validation
```axon
pointWrite(point, 16, value)  // No checks!
```

### 10. Grid Operations

**Best Practices**:
- [ ] Use appropriate grid functions
- [ ] Add metadata to grids when needed
- [ ] Use `addCol()` for computed columns
- [ ] Use `keepCols()`/`removeCols()` to shape data
- [ ] Sort and limit results appropriately
- [ ] Return grids from functions when appropriate

**✅ GOOD**: Grid transformation pipeline
```axon
readAll(point and temp and equipRef)
  .addCol("tempF", (row) => row->curVal * 1.8 + 32)
  .addCol("status", (row) =>
    if (row->tempF > 75) "high"
    else if (row->tempF < 65) "low"
    else "normal"
  )
  .keepCols(["dis", "tempF", "status", "equipRef"])
  .sortCol("tempF")
  .findAll(row => row->status == "high")
```

**Key Grid Functions**:
| Function | Purpose |
|----------|---------|
| `addCol(name, fn)` | Add computed column |
| `addRow(dict)` | Add row to grid |
| `addMeta(dict)` | Add grid metadata |
| `keepCols(names)` | Keep only specified columns |
| `removeCols(names)` | Remove specified columns |
| `renameCol(old, new)` | Rename column |
| `reorderCols(names)` | Reorder columns |
| `sortCol(name)` | Sort by column |
| `sortr(fn)` | Reverse sort |
| `join(grid, col)` | Join two grids |
| `pivot(...)` | Pivot table transformation |

---

## Connector Operations

### Current Value Sync
```axon
// Sync current values from remote system
connSyncCur(points)

// Check connector status
conn: read(haystackConn and dis=="MyConn")
conn->connStatus  // "ok", "fault", "disabled", etc.
```

### History Sync
```axon
// Sync history from remote system
connSyncHis(points, lastMonth())

// Check for sync errors
points.findAll(p => p->hisStatus != "ok")
```

### Connector Functions
| Function | Purpose |
|----------|---------|
| `connPing(conn)` | Test connectivity |
| `connSyncCur(points)` | Sync current values |
| `connSyncHis(points, span)` | Sync history |
| `connLearn(conn)` | Discover remote points |
| `connClose(conn)` | Force close connection |

---

## Point Naming Conventions

When working with point queries, be aware of the many naming variations used across different projects and integrations. Always use Haystack tags for queries rather than relying on `navName` or `dis`.

### Common Point Name Variations

**Temperature Points:**
| Point Type | Common navName Variations |
|------------|---------------------------|
| Chilled Water Return Temp | `CHWRT`, `CHWR_T`, `ChwRTmp`, `HxChwRTmp`, `CHWCoil_RetTmp` |
| Chilled Water Supply Temp | `CHWST`, `CHWS_T`, `ChwSTmp`, `HxChwSTmp`, `EvaporatorLeavingWaterTemperature` |
| Hot Water Return Temp | `HWRT`, `HWC_RetTmp`, `HxHwRTmp`, `HwRTmp`, `HX_01.HWRT` |
| Hot Water Supply Temp | `HWST`, `HwSTmp`, `HwsTmp`, `HWS_T`, `DomHWRT` |
| Outside Air Temp | `OAT`, `OA_T`, `OSA_T`, `OaTmp`, `OutsideAirTemp`, `BldgOaTmp` |
| Discharge Air Temp | `DAT`, `DaTmp`, `DA_T`, `DischargeAirTemperature`, `SaTmp` |
| Return Air Temp | `RAT`, `RaTmp`, `RetTmp`, `RATemp`, `ReturnAirTemperature` |
| Mixed Air Temp | `MAT`, `MaTmp`, `MATemp`, `MixAirTemp` |
| Space/Room Temp | `RmT`, `RoomTemp`, `SpaceTemp`, `ZnTmp`, `SpcTmp`, `ZN_T` |

**Valve & Damper Points:**
| Point Type | Common navName Variations |
|------------|---------------------------|
| CHW Valve | `CHWVlv`, `ChwVlv`, `ChwVlvPos`, `ChwVlvCmd`, `CHW_Vlv` |
| HW Valve | `HwVlvPos`, `HwVlvCmd`, `HWVlv`, `HWVlv1`, `HWVlv2` |
| Mixed Air Damper | `MaDprPos`, `MaDmpCmd`, `MADmp`, `MaDmprSignal`, `MixAirDmpr` |
| Exhaust Air Damper | `EADmp`, `EaDprPos`, `EA_Dmpr`, `ExAirDmpr` |
| Damper Position | `DamperPos`, `DmpCmd`, `Damper`, `damperCmd`, `DPR_O` |

**Fan Points:**
| Point Type | Common navName Variations |
|------------|---------------------------|
| Supply Fan VFD | `SFSpd`, `SFVFD`, `SF_VFD`, `SaFanSpdCmd`, `SaFanVfdSpd` |
| Supply Fan Status | `SFSts`, `SaFanSts`, `SF_Sts`, `SF_S`, `SaFan1Sts` |
| Return Fan VFD | `RFSpd`, `RaFanSpdCmd`, `RF1_VFD_Sts`, `RF2_VFD_Sts` |
| Return Fan Status | `RFSts`, `RaFan1Sts`, `N_RaFan`, `S_RaFan` |

**Pressure Points:**
| Point Type | Common navName Variations |
|------------|---------------------------|
| Building Static | `BSP`, `BldgStPr`, `BldgStaticSP`, `BldgStPrs`, `Bldg_Press` |
| Building Static SP | `BSPStpt`, `BldgStPrSetpt`, `BuildingStaticSetpoint` |
| Duct Static | `SDSP`, `DuctStPress`, `SaDSPress`, `SAStaticPress` |
| Duct Static SP | `DSPrSetpt`, `SDSPSetpt`, `SAStaticPressStpt` |

**Setpoint Points:**
| Point Type | Common navName Variations |
|------------|---------------------------|
| DAT Setpoint | `EffDATStpt`, `DaTmpSetpt`, `DATSetpt`, `DaTmpSptActive` |
| SAT Setpoint | `DatStPt`, `ActiveDatStPt`, `DAT_Stpt`, `SaTmpSpt_In` |
| HWST Setpoint | `HWSTStpt`, `HWSTSetpt`, `HWSTReset`, `HwsTempSp` |
| Space Temp SP | `OccSetpt`, `SpaceTemperatureSetPointEff` |
| CO2 Setpoint | `CO2Stpt`, `Co2MaxSP`, `Co2MinSP` |

**Status & Command Points:**
| Point Type | Common navName Variations |
|------------|---------------------------|
| Occupancy | `Occupancy`, `EffectiveOccupancy`, `OccCmd`, `OccSts`, `SchedOcc` |
| Pump Status | `HWP1_PmpSts`, `SchwP1Sts`, `PchwP1Sts`, `ChwP1Sts`, `CHWP1_S` |
| Pump Command | `HWP1_PmpCmd`, `SchwP1Cmd`, `PchwP1Cmd`, `CHWP1_C` |
| DX Command | `DxCmd`, `Dx1Cmd`, `ClgStg1Cmd`, `DxStg1Cmd`, `DX1Cmd` |

### Query Best Practices for Points

**✅ GOOD**: Query by Haystack tags
```axon
// Find discharge air temp regardless of navName
readAll(point and discharge and air and temp and sensor and equipRef==@ahuId)

// Find CHW valve command
readAll(point and chilled and water and valve and cmd and equipRef==@ahuId)

// Find supply fan speed
readAll(point and discharge and fan and speed and cmd)
```

**❌ BAD**: Query by navName (fragile)
```axon
// This will miss points with different naming!
readAll(point and navName=="DAT")
readAll(point and dis.contains("Discharge"))
```

### Standardizing Point Discovery

```axon
/*
 * Find AHU temperature points with fallback patterns
 */
findAhuTempPoints: (equipRef: Ref) => do
  // Primary: Use proper Haystack tags
  points: readAll(point and equipRef==equipRef and temp and sensor)

  // Categorize by tags
  dat: points.find(p => p.has("discharge") and p.has("air"))
  rat: points.find(p => p.has("return") and p.has("air"))
  mat: points.find(p => p.has("mixed") and p.has("air"))
  oat: points.find(p => p.has("outside") and p.has("air"))

  {dat: dat, rat: rat, mat: mat, oat: oat}
end
```

---

## Common Haystack Tags Reference

### Entity Tags
| Tag | Description |
|-----|-------------|
| `site` | Building or facility |
| `space` | Room or area within building |
| `equip` | Equipment asset |
| `point` | Sensor, actuator, or setpoint |
| `device` | Controller or network device |

### Point Classification Tags
| Tag | Description |
|-----|-------------|
| `sensor` | Input/AI/BI point |
| `cmd` | Command/output/AO/BO point |
| `sp` | Setpoint |
| `cur` | Has current value |
| `his` | Has history |
| `writable` | Can be written to |

### HVAC Equipment Tags
| Tag | Description |
|-----|-------------|
| `ahu` | Air Handling Unit |
| `vav` | Variable Air Volume terminal |
| `fcu` | Fan Coil Unit |
| `chiller` | Chiller |
| `boiler` | Boiler |
| `pump` | Pump |
| `fan` | Fan |
| `damper` | Damper |
| `valve` | Valve |

### Medium Tags
| Tag | Description |
|-----|-------------|
| `air` | Air medium |
| `water` | Water medium |
| `steam` | Steam medium |
| `elec` | Electricity |
| `naturalGas` | Natural gas |

### Water System Tags
| Tag | Description |
|-----|-------------|
| `chilled` | Chilled water |
| `hot` | Hot water |
| `condenser` | Condenser water |
| `domestic` | Domestic water |
| `makeup` | Makeup water |

### Air System Tags
| Tag | Description |
|-----|-------------|
| `discharge` | Discharge/supply air |
| `return` | Return air |
| `outside` | Outside air |
| `mixed` | Mixed air |
| `exhaust` | Exhaust air |

### Temperature/Measurement Tags
| Tag | Description |
|-----|-------------|
| `temp` | Temperature |
| `humidity` | Humidity |
| `pressure` | Pressure |
| `flow` | Flow rate |
| `power` | Power |
| `energy` | Energy |
| `speed` | Speed (fan, pump) |
| `level` | Level/position (0-100%) |

### Status Tags
| Tag | Description |
|-----|-------------|
| `run` | Run status |
| `enable` | Enable status |
| `alarm` | Alarm condition |
| `fault` | Fault condition |
| `occ` | Occupied status |

### Reference Tags
| Tag | Description |
|-----|-------------|
| `siteRef` | Reference to site |
| `equipRef` | Reference to equipment |
| `spaceRef` | Reference to space |
| `elecRef` | Reference to elec meter |

---

## Rules and Sparks

### Rule Functions
| Function | Purpose |
|----------|---------|
| `ruleSparks(targets, dates, rules)` | Query sparks |
| `ruleKpis(targets, dates, rules)` | Query KPIs |
| `ruleRecompute(targets, dates, rules)` | Recompute results |
| `ruleTest(rule)` | Test a rule |
| `ruleDebug()` | Debug rule engine |

### Spark Queries
```axon
// Get all sparks for a site this week
sparks: ruleSparks(@siteId, thisWeek())

// Get KPIs for specific rule
kpis: ruleKpis(@siteId, lastMonth(), @myRule)
```

---

## Task and Job Functions

### Async Task Execution
```axon
// Run async task
taskRun(myExpensiveFunction)

// Run with message handling
task: taskRun() (msg) => do
  // Process messages
  echo("Received: " + msg.toStr)
end

// Send message to task
taskSend(task, "hello")
```

### Background Jobs
```axon
// Run as background job
jobRun("myJob", expr)

// Check job status
jobStatus(handle)

// Cancel job
jobCancel(handle)
```

---

## Common Pitfalls

### 1. Memory Issues with Large Datasets
```axon
// ❌ BAD: Reading huge history into memory
allPoints.hisRead(lastYear()) // Could crash!

// ✅ GOOD: Use rollup or streaming
allPoints.hisRead(lastYear()).hisRollup(avg, 1day)
```

### 2. N+1 Query Problem
```axon
// ❌ BAD: Query in loop
sites.map(site => do
  equips: readAll(equip and siteRef==site->id)  // One query per site!
  {site: site, equipCount: equips.size}
end)

// ✅ GOOD: Query once, then filter
allEquips: readAll(equip and siteRef)
sites.map(site => do
  equips: allEquips.findAll(e => e->siteRef == site->id)
  {site: site, equipCount: equips.size}
end)
```

### 3. Timezone Issues
```axon
// ❌ BAD: Mixed timezones
site1Data: points1.hisRead(today("America/New_York"))
site2Data: points2.hisRead(today("America/Los_Angeles"))
combined: hisJoin([site1Data, site2Data])  // Different timezones!

// ✅ GOOD: Normalize to single timezone
tz: "UTC"
site1Data: points1.hisRead(today(tz)).toTimeZone(tz)
site2Data: points2.hisRead(today(tz)).toTimeZone(tz)
combined: hisJoin([site1Data, site2Data])
```

### 4. Missing Null Checks
```axon
// ❌ BAD: Assumes data exists
avg: point.hisRead(today()).avg("v0")

// ✅ GOOD: Handle empty results
data: point.hisRead(today())
if (data.isEmpty) return null
data.avg("v0")
```

### 5. Inefficient String Operations
```axon
// ❌ BAD: String concatenation in loop
result: ""
items.each(item => result = result + item.toStr + ",")

// ✅ GOOD: Use join
result: items.map(i => i.toStr).join(",")
```

### 6. Unhandled Units
```axon
// ❌ BAD: Ignoring units
temps: points.map(p => p->curVal)

// ✅ GOOD: Handle units consistently
temps: points.map(p => do
  val: p->curVal
  unit: p->unit
  if (unit == "°C") val.as(1°F)  // Use unit conversion
  else val
end)
```

### 7. Unsafe Tag Access
```axon
// ❌ BAD: Direct access throws if missing
val: point->curVal

// ✅ GOOD: Safe access with default
val: point.get("curVal", 0)

// ✅ GOOD: Check before access
if (point.has("curVal")) val: point->curVal
```

### 8. Querying by Display Name
```axon
// ❌ BAD: Display names vary
readAll(point and dis.contains("Discharge"))

// ✅ GOOD: Use proper tags
readAll(point and discharge and air and temp)
```

---

## Code Style Guidelines

### Naming Conventions
- **Functions**: camelCase (`calculateAverage`, `getPointData`)
- **Variables**: camelCase (`pointData`, `tempValue`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_TEMP`, `DEFAULT_SPAN`)
- Use descriptive names, not abbreviations

### Formatting
```axon
// ✅ GOOD: Clear formatting
(siteId: Ref, span: DateSpan) => do
  site: readById(siteId)
  points: readAll(point and siteRef==siteId and temp)

  data: points.hisRead(span)
    .hisRollup(avg, 1hr)
    .map(row => {
      ts: row->ts,
      val: row->v0,
      unit: "°F"
    })

  return {
    site: site->dis,
    count: data.size,
    data: data
  }
end

// ❌ BAD: Poor formatting
(s,sp)=>do site:readById(s)points:readAll(point and siteRef==s and temp)
data:points.hisRead(sp).hisRollup(avg,1hr)return data end
```

### Comments and Documentation
```axon
// ✅ GOOD: Doc string with @param and @return
/*
 * Calculate energy usage for a site over a date span
 * @param siteId Ref to the site
 * @param span DateSpan for calculation period
 * @return Grid with hourly energy totals
 */
(siteId: Ref, span: DateSpan) => do
  // Get all kW demand points for the site
  points: readAll(point and siteRef==siteId and power and kind=="Number")

  // Read and rollup to hourly averages
  data: points.hisRead(span).hisRollup(avg, 1hr)

  // Calculate total energy (kWh) from average demand (kW)
  return data.map(row => row.set("energy", row->v0 * 1))
end
```

---

## Output Format

When reviewing code, provide feedback in this format:

**✅ Strengths:**
- Good practices identified in the code

**⚠️ Issues Found:**
- **HIGH**: Critical issues (performance problems, data corruption risk, crashes)
- **MEDIUM**: Best practice violations (inefficient queries, missing validation)
- **LOW**: Minor improvements (style, naming, documentation)

**💡 Recommendations:**
- Specific actionable improvements
- Code examples showing better approaches
- Performance optimization suggestions

**📊 Metrics:**
- Number of functions reviewed
- Number of readAll() calls (watch for N+1 problems)
- History read operations (check for large date ranges)
- Complexity indicators (nested loops, deep call chains)

---

## Troubleshooting

**Code won't execute:**
- Check for syntax errors (missing commas, brackets, `end` statements)
- Verify all referenced functions exist
- Check tag names match exactly (case-sensitive)
- Ensure proper use of `do...end` blocks

**Performance issues:**
- Profile slow sections with timing
- Look for N+1 query patterns (readAll in loops)
- Check history read date ranges
- Use `readAllStream()` for large result sets

**Unexpected results:**
- Verify timezone settings match site timezone
- Check for null values in data
- Validate tag types before operations
- Use `echo()` for debugging intermediate values

**Connector issues:**
- Check `connStatus` for errors
- Verify network connectivity with `connPing()`
- Check `curStatus` and `hisStatus` on points
- Review connector trace logs with `connTrace()`

---

## References

- SkySpark Documentation: https://skyfoundry.com/doc
- Project Haystack: https://project-haystack.org/
- Axon Language Reference: SkySpark Help → Axon
- Haystack Tags: https://project-haystack.org/tag
