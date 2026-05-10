# CrewTimer Export Improvements Bugfix Design

## Overview

The CrewTimer export formatter has two formatting issues that produce incorrect output for CrewTimer timing software:
1. The column header "Race Info" should be "Race Type"
2. For marathon races (42km), the Event column should display "1x Marathon" (unified) and the Race Type column should display "Sprint" instead of "Head"

The fix is localized to a single file: `frontend/src/utils/exportFormatters/crewTimerFormatter.js`. The `raceAssignments` object already carries an `isMarathon` flag from `raceNumbering.js`, so the formatter just needs to use it when building each row.

## Glossary

- **Bug_Condition (C)**: The condition that triggers incorrect output — marathon race boats getting individual race names in Event and "Head" in Race Type
- **Property (P)**: The desired behavior — marathon boats get "1x Marathon" in Event and "Sprint" in Race Type; column header is "Race Type"
- **Preservation**: Semi-marathon behavior and all other columns must remain unchanged
- **`formatRacesToCrewTimer`**: The function in `crewTimerFormatter.js` that builds the CrewTimer row array from JSON data
- **`raceAssignments`**: Object from `raceNumbering.js` mapping race_id to `{ raceNumber, startTime, isMarathon, shortName, name }`
- **`isMarathon`**: Boolean flag already computed in `raceNumbering.js` — true when `race.distance === 42 || race.event_type === '42km'`

## Bug Details

### Bug Condition

The bug manifests when a boat belongs to a marathon race (42km). The `formatRacesToCrewTimer` function currently:
1. Uses the hardcoded column key `'Race Info'` instead of `'Race Type'`
2. Always sets the Race Info/Type value to `'Head'` regardless of race distance
3. Always uses the full translated race name for the Event column regardless of race distance

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type { boat, raceAssignment }
  OUTPUT: boolean
  
  RETURN raceAssignment.isMarathon === true
END FUNCTION
```

Note: The column header rename (Race Info → Race Type) applies unconditionally to all rows, but the value change (Head → Sprint) and Event override (race name → "1x Marathon") only apply when `isMarathon` is true.

### Examples

- **Marathon boat (current)**: Event = "1X MASTER F WOMAN", Race Info = "Head"
  **Expected**: Event = "1x Marathon", Race Type = "Sprint"

- **Marathon boat (current)**: Event = "1X SENIOR MAN", Race Info = "Head"
  **Expected**: Event = "1x Marathon", Race Type = "Sprint"

- **Semi-marathon boat (current)**: Event = "WOMEN-MASTER-COXED QUAD SCULL YOLETTE", Race Info = "Head"
  **Expected**: Event = "WOMEN-MASTER-COXED QUAD SCULL YOLETTE", Race Type = "Head" (unchanged except column name)

- **Edge case — no races**: Export produces empty array, no columns generated — no change needed

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Semi-marathon (21km) boats must continue to display the full translated race name in the Event column
- Semi-marathon boats must continue to display "Head" in the Race Type column
- All other columns (Event Time, Event Num, Event Abbrev, Crew, Crew Abbrev, Stroke, Bow, Status, Age, Handicap, Note) must remain unchanged for all boats
- Sorting logic (by display_order, then by average age within race) must remain unchanged
- Boat filtering logic (complete/paid/free, not forfait) must remain unchanged
- Time formatting, short name translation, and all other formatting logic must remain unchanged

**Scope:**
All inputs that do NOT involve marathon race boats should be completely unaffected by this fix. This includes:
- All semi-marathon (21km) boats — same Event value, same Race Type value ("Head")
- All column values other than Event and Race Type
- The overall structure and sorting of the export

## Hypothesized Root Cause

Based on the code analysis, the root causes are straightforward:

1. **Hardcoded column key**: Line 271 in `crewTimerFormatter.js` uses `'Race Info': 'Head'` — the column key is a literal string that should be `'Race Type'`

2. **No marathon-specific logic for Race Type value**: The value `'Head'` is hardcoded without checking `raceAssignment.isMarathon`. Marathon races should output `'Sprint'`

3. **No marathon-specific logic for Event value**: The Event column always uses `fullRaceName` (the translated individual race name). For marathon races, it should use the fixed string `'1x Marathon'`

4. **Available data not used**: The `raceAssignment.isMarathon` flag is already computed and available in the loop but never consulted when building the row object

## Correctness Properties

Property 1: Bug Condition - Marathon Boats Get Correct Event and Race Type

_For any_ boat where the race assignment has `isMarathon === true`, the fixed `formatRacesToCrewTimer` function SHALL output `"1x Marathon"` in the Event column and `"Sprint"` in the Race Type column.

**Validates: Requirements 2.2, 2.3**

Property 2: Preservation - Semi-Marathon Boats Unchanged

_For any_ boat where the race assignment has `isMarathon === false`, the fixed `formatRacesToCrewTimer` function SHALL produce the same Event value (full translated race name) and the same Race Type value (`"Head"`) as the original function, preserving all existing semi-marathon formatting.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

Property 3: Column Header Rename

_For any_ export output, the column key SHALL be `"Race Type"` (not `"Race Info"`), applying to all rows regardless of race distance.

**Validates: Requirements 2.1**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File**: `frontend/src/utils/exportFormatters/crewTimerFormatter.js`

**Function**: `formatRacesToCrewTimer`

**Specific Changes**:

1. **Rename column key**: Change `'Race Info': 'Head'` to `'Race Type': ...` in the row object construction (around line 271)

2. **Conditional Race Type value**: Use `raceAssignment.isMarathon` to determine the value:
   - Marathon (`isMarathon === true`): `'Sprint'`
   - Semi-marathon (`isMarathon === false`): `'Head'`

3. **Conditional Event value**: Use `raceAssignment.isMarathon` to determine the Event column:
   - Marathon: `'1x Marathon'` (fixed string, not translated)
   - Semi-marathon: `fullRaceName` (existing translated race name)

4. **Pass isMarathon from raceAssignment**: The `raceAssignment` object already contains `isMarathon` — just read it in the loop where the row is built

5. **Update documentation**: Update `docs/reference/crewtimer-export.md` and `frontend/src/utils/exportFormatters/README.md` to reflect the new column name and marathon-specific behavior

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write unit tests that call `formatRacesToCrewTimer` with marathon race data and assert the expected column name and values. Run these tests on the UNFIXED code to observe failures.

**Test Cases**:
1. **Marathon Event Value Test**: Call formatter with a marathon boat, assert Event === "1x Marathon" (will fail on unfixed code — currently outputs individual race name)
2. **Marathon Race Type Value Test**: Call formatter with a marathon boat, assert Race Type === "Sprint" (will fail on unfixed code — currently outputs "Head")
3. **Column Header Test**: Call formatter with any boat, assert the row has key "Race Type" not "Race Info" (will fail on unfixed code)
4. **Multiple Marathon Boats Test**: Call formatter with multiple marathon boats from different race categories, assert all have Event === "1x Marathon" (will fail on unfixed code)

**Expected Counterexamples**:
- Marathon boats will have Event = "1X MASTER F WOMAN" (individual name) instead of "1x Marathon"
- All rows will have key "Race Info" instead of "Race Type"
- Race Info value will be "Head" instead of "Sprint" for marathon boats

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL boat WHERE raceAssignment.isMarathon === true DO
  result := formatRacesToCrewTimer_fixed(input)
  row := findRow(result, boat)
  ASSERT row['Event'] === '1x Marathon'
  ASSERT row['Race Type'] === 'Sprint'
  ASSERT 'Race Info' NOT IN row.keys
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL boat WHERE raceAssignment.isMarathon === false DO
  row_fixed := findRow(formatRacesToCrewTimer_fixed(input), boat)
  ASSERT row_fixed['Event'] === fullTranslatedRaceName
  ASSERT row_fixed['Race Type'] === 'Head'
  ASSERT row_fixed['Event Time'] is unchanged
  ASSERT row_fixed['Event Num'] is unchanged
  ASSERT row_fixed['Bow'] is unchanged
  // ... all other columns unchanged
END FOR
```

**Testing Approach**: Explicit example-based tests are sufficient here because:
- The input domain is well-defined (marathon vs semi-marathon, determined by `distance === 42`)
- The logic change is a simple conditional branch
- The preservation surface is small (only Event and Race Type columns change for marathon)

**Test Cases**:
1. **Semi-Marathon Event Preservation**: Verify semi-marathon boats still show full translated race name in Event
2. **Semi-Marathon Race Type Preservation**: Verify semi-marathon boats still show "Head" in Race Type
3. **Other Columns Preservation**: Verify Event Time, Event Num, Bow, Stroke, Age, etc. are unchanged for both marathon and semi-marathon boats
4. **Sorting Preservation**: Verify output order is unchanged (display_order, then avg_age)

### Unit Tests

- Test `formatRacesToCrewTimer` with marathon-only data → verify Event = "1x Marathon", Race Type = "Sprint"
- Test `formatRacesToCrewTimer` with semi-marathon-only data → verify Event = translated name, Race Type = "Head"
- Test `formatRacesToCrewTimer` with mixed data (both marathon and semi-marathon) → verify correct values per race type
- Test column key is "Race Type" (not "Race Info") in all output rows
- Test edge case: empty races array → no rows, no error

### Property-Based Tests

Not applicable per project guidelines (no Hypothesis library; explicit test cases preferred for this project).

### Integration Tests

- Test full export flow with realistic data containing both marathon and semi-marathon races
- Verify the generated Excel file has correct column headers including "Race Type"
- Verify marathon rows in the Excel have "1x Marathon" and "Sprint"
- Verify semi-marathon rows retain their full race names and "Head"
