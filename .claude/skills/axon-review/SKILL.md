---
name: axon-review
description: Reviews SkySpark Axon code for best practices, efficient Haystack querying, proper function design, performance optimization, and common pitfalls. Use when reviewing Axon scripts, functions, or queries in SkySpark/Project Haystack context.
allowed-tools: Read, Grep, Glob
---

# SkySpark Axon Code Review

## Overview

This skill reviews Axon code written for SkySpark (the IoT/building automation platform by SkyFoundry). Axon is a functional programming language designed for working with Haystack data models and time-series data.

## Review Checklist

### 1. Function Design

**Best Practices**:
- [ ] Function names are clear and descriptive
- [ ] Parameters have proper type hints
- [ ] Return types are documented
- [ ] Functions are focused and single-purpose
- [ ] Proper use of default parameters
- [ ] Doc strings explain purpose and usage

**Function Syntax**:
```axon
// ✅ GOOD: Clear function with doc and type hints
/*
 * Calculate average temperature for a given period
 * @param point Ref to temp sensor point
 * @param span DateSpan for calculation
 * @return Number average temperature
 */
(point: Ref, span: DateSpan) => do
  readAll(point).hisRead(span).hisRollup(avg, 1day).avg("v0")
end

// ❌ BAD: No documentation, unclear purpose
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

**Query Optimization**:
```axon
// ❌ BAD: Too broad, multiple queries
readAll(site).each(site => do
  points: readAll(point and equipRef==site->id)
  // ... processing
end)

// ✅ GOOD: Specific filter, single query
points: readAll(point and siteRef==@siteId and equipRef)
equipIds: points.unique("equipRef")
equips: readById(equipIds)

// ❌ BAD: Nested readAll (N+1 query problem)
readAll(equip).map(e =>
  readAll(point and equipRef==e->id)
)

// ✅ GOOD: Single query with join
points: readAll(point and equipRef)
points.groupBy("equipRef")
```

### 3. Historical Data Operations

**Best Practices**:
- [ ] Use appropriate date/time ranges
- [ ] Specify explicit timezones
- [ ] Use `hisRollup()` for aggregations
- [ ] Consider memory impact of large reads
- [ ] Use streaming functions for large datasets
- [ ] Handle missing data gracefully

**History Read Patterns**:
```axon
// ✅ GOOD: Explicit range and rollup
points.hisRead(lastWeek(), {tz: "New_York"})
      .hisRollup(avg, 1hr)
      .hisMap(v => v * 1.8 + 32) // Convert C to F

// ❌ BAD: No rollup on large dataset
points.hisRead(lastYear()) // Could return millions of records!

// ✅ GOOD: Use rollup for large ranges
points.hisRead(lastYear()).hisRollup(avg, 1day)

// ✅ GOOD: Handle missing data
temp: point.hisRead(today())
if (temp.isEmpty) return null
temp.avg("v0")
```

### 4. Data Manipulation

**Best Practices**:
- [ ] Use functional operations (map, filter, fold)
- [ ] Avoid unnecessary iterations
- [ ] Use `each()` for side effects only
- [ ] Use `map()` for transformations
- [ ] Chain operations efficiently
- [ ] Avoid mutating variables in loops

**Functional Programming**:
```axon
// ✅ GOOD: Functional pipeline
readAll(point and temp)
  .map(p => {dis: p->dis, val: p->curVal})
  .filter(p => p->val > 72)
  .sortCol("val")
  .reverse

// ❌ BAD: Imperative style with mutation
result: []
readAll(point and temp).each(p => do
  if (p->curVal > 72) result = result.add({dis: p->dis, val: p->curVal})
end)
result

// ✅ GOOD: Use fold for accumulation
points.hisRead(today())
      .fold(0, (acc, row) => acc + row->v0)

// ❌ BAD: Manual accumulation
sum: 0
points.hisRead(today()).each(row => sum = sum + row->v0)
```

### 5. Error Handling

**Best Practices**:
- [ ] Validate inputs at function entry
- [ ] Use `try-catch` for external operations
- [ ] Return meaningful error messages
- [ ] Handle null/empty cases explicitly
- [ ] Use `trap` for error recovery
- [ ] Log errors appropriately

**Error Handling Patterns**:
```axon
// ✅ GOOD: Input validation
(siteId: Ref, days: Number) => do
  if (not siteId.isRef) throw "Invalid siteId: must be a Ref"
  if (days <= 0) throw "Invalid days: must be positive"

  site: trap(readById(siteId), null)
  if (site == null) throw "Site not found: " + siteId.toStr

  // ... rest of logic
end

// ❌ BAD: No validation or error handling
(siteId, days) => do
  readById(siteId).hisRead(pastDays(days))
end

// ✅ GOOD: Use trap for recovery
temp: trap(point->curVal, null)
if (temp == null) temp = point.hisRead(yesterday()).last->v0

// ✅ GOOD: Graceful degradation
try
  externalApiCall(data)
catch (err)
  logErr("API call failed: " + err.toStr)
  return {status: "error", msg: err.toStr}
end
```

### 6. Performance Optimization

**Best Practices**:
- [ ] Minimize database reads
- [ ] Cache expensive computations
- [ ] Use streaming for large datasets
- [ ] Avoid nested loops over data
- [ ] Use `readAllStream()` for large queries
- [ ] Profile slow functions with `elapsed()`

**Performance Patterns**:
```axon
// ❌ BAD: Multiple separate reads
sites.each(site => do
  equips: readAll(equip and siteRef==site->id)
  points: readAll(point and siteRef==site->id)
end)

// ✅ GOOD: Batch read and group
allEquips: readAll(equip and siteRef)
allPoints: readAll(point and siteRef)
sites.each(site => do
  equips: allEquips.findAll(e => e->siteRef == site->id)
  points: allPoints.findAll(p => p->siteRef == site->id)
end)

// ✅ GOOD: Use streaming for large datasets
readAllStream(point and siteRef==@bigSiteId)
  .map(p => processPoint(p))
  .collect

// ✅ GOOD: Cache expensive operations
cachedData: () => do
  cached: context.get("myCache")
  if (cached != null) return cached

  result: expensiveComputation()
  context.set("myCache", result, 1hr)
  return result
end

// ✅ GOOD: Measure performance
elapsed("myQuery", () => readAll(point and temp))
```

### 7. Date/Time Handling

**Best Practices**:
- [ ] Always specify timezones explicitly
- [ ] Use appropriate date span functions
- [ ] Handle DST transitions correctly
- [ ] Use `DateSpan` for date ranges
- [ ] Consider site timezone vs UTC
- [ ] Test across month/year boundaries

**Date/Time Patterns**:
```axon
// ✅ GOOD: Explicit timezone
tz: readById(@siteId)->tz
span: today(tz)
data: point.hisRead(span, {tz: tz})

// ❌ BAD: No timezone (uses server timezone)
data: point.hisRead(today())

// ✅ GOOD: Date span construction
span: dateSpan(2024-01-01, 2024-01-31)
data: point.hisRead(span)

// ✅ GOOD: Handle timezone conversions
utcTime: now()
localTime: utcTime.toTimeZone(site->tz)

// ✅ GOOD: Use built-in date functions
lastWeek()
yesterday()
pastMonth()
thisMonth()
dateSpan(date.firstOfMonth, date.lastOfMonth)
```

### 8. Tag Operations

**Best Practices**:
- [ ] Use `has()` to check tag existence
- [ ] Use `get()` with defaults for safety
- [ ] Use `trap()` when accessing potentially missing tags
- [ ] Use proper tag naming conventions
- [ ] Validate tag types before operations
- [ ] Use marker tags appropriately

**Tag Handling**:
```axon
// ✅ GOOD: Safe tag access
val: point.get("curVal", 0)
if (point.has("unit")) unit: point->unit

// ❌ BAD: Unsafe tag access (throws if missing)
val: point->curVal  // Error if curVal doesn't exist

// ✅ GOOD: Trap for optional tags
temp: trap(point->temp, null)
if (temp != null) processTemp(temp)

// ✅ GOOD: Check marker tags
if (point.has("writable"))
  pointWrite(point, 16, newVal)

// ✅ GOOD: Type checking
if (point->curVal.isNumber)
  scaled: point->curVal * 1.8 + 32
```

### 9. Writing Data

**Best Practices**:
- [ ] Validate values before writing
- [ ] Check point is writable
- [ ] Use appropriate priority levels (1-17)
- [ ] Handle write failures gracefully
- [ ] Log write operations
- [ ] Verify write succeeded if critical

**Write Operations**:
```axon
// ✅ GOOD: Safe write with validation
(point: Ref, value: Number, level: Number: 16) => do
  pt: readById(point)
  if (not pt.has("writable"))
    throw "Point is not writable: " + pt->dis

  if (pt.has("maxVal") and value > pt->maxVal)
    throw "Value exceeds maximum: " + pt->maxVal.toStr

  if (pt.has("minVal") and value < pt->minVal)
    throw "Value below minimum: " + pt->minVal.toStr

  try
    pointWrite(point, level, value)
    logInfo("Write successful: " + pt->dis + " = " + value.toStr)
  catch (err)
    logErr("Write failed: " + err.toStr)
    throw err
  end
end

// ❌ BAD: No validation or error handling
pointWrite(point, 16, value)
```

### 10. Grid Operations

**Best Practices**:
- [ ] Use appropriate grid functions
- [ ] Add metadata to grids when needed
- [ ] Use `addCol()` for computed columns
- [ ] Use `keepCols()`/`removeCols()` to shape data
- [ ] Sort and limit results appropriately
- [ ] Return grids from functions when appropriate

**Grid Manipulation**:
```axon
// ✅ GOOD: Grid transformation pipeline
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

// ✅ GOOD: Add grid metadata
result: readAll(point).addMeta({
  title: "Temperature Points",
  generated: now(),
  siteRef: @siteId
})
```

## Common Pitfalls to Check

### 1. **Memory Issues with Large Datasets**
```axon
// ❌ BAD: Reading huge history into memory
allPoints.hisRead(lastYear()) // Could crash!

// ✅ GOOD: Use rollup or streaming
allPoints.hisRead(lastYear()).hisRollup(avg, 1day)
// OR
readAllStream(point).map(p => p.hisRead(lastYear()).hisRollup(avg, 1day))
```

### 2. **N+1 Query Problem**
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

### 3. **Timezone Issues**
```axon
// ❌ BAD: Mixed timezones
site1Data: points1.hisRead(today("New_York"))
site2Data: points2.hisRead(today("Los_Angeles"))
combined: site1Data.union(site2Data)  // Different timezones!

// ✅ GOOD: Normalize to UTC or single timezone
tz: "UTC"
site1Data: points1.hisRead(today(tz), {tz: tz})
site2Data: points2.hisRead(today(tz), {tz: tz})
combined: site1Data.union(site2Data)
```

### 4. **Missing Null Checks**
```axon
// ❌ BAD: Assumes data exists
avg: point.hisRead(today()).avg("v0")

// ✅ GOOD: Handle empty results
data: point.hisRead(today())
if (data.isEmpty) return null
avg: data.avg("v0")
```

### 5. **Inefficient String Operations**
```axon
// ❌ BAD: String concatenation in loop
result: ""
items.each(item => result = result + item.toStr + ",")

// ✅ GOOD: Use join
result: items.map(i => i.toStr).join(",")
```

### 6. **Unhandled Units**
```axon
// ❌ BAD: Ignoring units
temps: points.map(p => p->curVal)

// ✅ GOOD: Handle units consistently
temps: points.map(p => do
  val: p->curVal
  unit: p->unit
  if (unit == "°C") val * 1.8 + 32  // Convert to F
  else val
end)
```

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
// ✅ GOOD: Doc string and inline comments
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

## Testing Considerations

**Manual Testing**:
- [ ] Test with empty datasets
- [ ] Test with single record
- [ ] Test with large datasets
- [ ] Test across timezone boundaries
- [ ] Test with missing tags
- [ ] Test error conditions
- [ ] Test with different units

**Test Data Patterns**:
```axon
// Create test data
testPoint: {
  id: @testPoint,
  dis: "Test Point",
  point,
  temp,
  kind: "Number",
  unit: "°F"
}

// Test function with various inputs
testFunc: (point: Ref) => do
  // Function logic
end

// Test cases
testFunc(@validPoint)        // Normal case
testFunc(@missingPoint)      // Missing point
testFunc(@pointNoHistory)    // Point with no history
```

## SkySpark Specific Best Practices

### Task Functions
- [ ] Use appropriate task scheduling
- [ ] Handle task errors gracefully
- [ ] Log task execution
- [ ] Use proper task priorities

### Extensions
- [ ] Follow extension naming conventions
- [ ] Document extension functions thoroughly
- [ ] Version extension functions
- [ ] Handle backward compatibility

### Rules and Schedules
- [ ] Keep rules simple and focused
- [ ] Test rules thoroughly before deployment
- [ ] Use appropriate rule priorities
- [ ] Consider performance impact of rules

## Output Format

Provide review feedback as:

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

## Resources

- SkySpark Documentation: https://skyfoundry.com/doc
- Project Haystack: https://project-haystack.org/
- Axon Language Reference: Check SkySpark's built-in documentation
