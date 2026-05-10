# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Marathon Boats Get Wrong Event and Race Type
  - **IMPORTANT**: Write this test BEFORE implementing the fix
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped Approach**: Scope to marathon boats (race with `distance: 42` / `event_type: '42km'`) where `raceAssignment.isMarathon === true`
  - Add test in `frontend/src/utils/exportFormatters/crewTimerFormatter.test.js` under a new `describe('Bug condition: Marathon export formatting')` block
  - Test 1: Call `formatRacesToCrewTimer` with a marathon boat, assert `row['Event'] === '1x Marathon'` (will FAIL — currently outputs individual race name like "1X SENIOR MAN")
  - Test 2: Call `formatRacesToCrewTimer` with a marathon boat, assert `row['Race Type'] === 'Sprint'` (will FAIL — currently outputs "Head" under key "Race Info")
  - Test 3: Call `formatRacesToCrewTimer` with any boat, assert the row has key `'Race Type'` and does NOT have key `'Race Info'` (will FAIL — currently uses "Race Info")
  - Test 4: Call `formatRacesToCrewTimer` with multiple marathon boats from different race categories, assert all have `Event === '1x Marathon'` (will FAIL)
  - Run test on UNFIXED code: `cd frontend && npx vitest run src/utils/exportFormatters/crewTimerFormatter.test.js`
  - **EXPECTED OUTCOME**: Tests FAIL (this is correct - it proves the bug exists)
  - Document counterexamples: marathon boats have `Event = "1X SENIOR MAN"` instead of `"1x Marathon"`, key is `"Race Info"` not `"Race Type"`, value is `"Head"` not `"Sprint"`
  - Mark task complete when tests are written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Write preservation tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Semi-Marathon Boats Unchanged
  - **IMPORTANT**: Follow observation-first methodology
  - **IMPORTANT**: Write these tests BEFORE implementing the fix
  - Observe on UNFIXED code: semi-marathon boats (distance: 21) display full translated race name in Event column
  - Observe on UNFIXED code: semi-marathon boats display "Head" in Race Info column (will become Race Type after fix)
  - Observe on UNFIXED code: all other columns (Event Time, Event Num, Event Abbrev, Crew, Crew Abbrev, Stroke, Bow, Status, Age, Handicap, Note) are unchanged for all boats
  - Add test in `frontend/src/utils/exportFormatters/crewTimerFormatter.test.js` under a new `describe('Preservation: Semi-marathon behavior unchanged')` block
  - Test 1: Semi-marathon boat Event value equals full translated race name (e.g., "WOMEN-MASTER-COXED QUAD SCULL YOLETTE")
  - Test 2: Semi-marathon boat Race Type/Info value equals "Head"
  - Test 3: Mixed data (marathon + semi-marathon) — verify semi-marathon rows retain full race name and "Head", while other columns (Event Time, Event Num, Bow, Stroke, Age, Note) are correct
  - Test 4: Sorting preservation — verify output order is by Event Num then Bow (display_order then avg_age within race)
  - Run tests on UNFIXED code: `cd frontend && npx vitest run src/utils/exportFormatters/crewTimerFormatter.test.js`
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Note: On unfixed code, the column key is "Race Info" — write assertions using the key that exists on unfixed code (`'Race Info': 'Head'`), then update to `'Race Type': 'Head'` after the fix is applied
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3. Fix CrewTimer export for marathon boats

  - [x] 3.1 Implement the fix in `frontend/src/utils/exportFormatters/crewTimerFormatter.js`
    - Rename column key `'Race Info'` → `'Race Type'` in the row object (around line 271)
    - Add conditional logic using `raceAssignment.isMarathon`:
      - If `isMarathon === true`: set `'Event': '1x Marathon'` and `'Race Type': 'Sprint'`
      - If `isMarathon === false`: set `'Event': fullRaceName` and `'Race Type': 'Head'`
    - The `raceAssignment` object already contains `isMarathon` from `raceNumbering.js` — just read it in the row-building section
    - _Bug_Condition: isBugCondition(input) where raceAssignment.isMarathon === true_
    - _Expected_Behavior: Event === '1x Marathon' AND Race Type === 'Sprint' for marathon boats_
    - _Preservation: Semi-marathon boats keep fullRaceName in Event and 'Head' in Race Type_
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2_

  - [x] 3.2 Update preservation tests to use new column key
    - Change assertions from `row['Race Info']` to `row['Race Type']` in preservation tests
    - Ensure all preservation tests still assert `'Head'` for semi-marathon boats under the new key name
    - _Requirements: 3.1, 3.2_

  - [x] 3.3 Update existing tests that reference 'Race Info'
    - Search existing test file for any assertions using `'Race Info'` key
    - Update them to use `'Race Type'` key
    - _Requirements: 2.1_

  - [x] 3.4 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Marathon Boats Get Correct Event and Race Type
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run: `cd frontend && npx vitest run src/utils/exportFormatters/crewTimerFormatter.test.js`
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 3.5 Verify preservation tests still pass
    - **Property 2: Preservation** - Semi-Marathon Boats Unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run: `cd frontend && npx vitest run src/utils/exportFormatters/crewTimerFormatter.test.js`
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4. Checkpoint - Ensure all tests pass
  - Run full test suite: `cd frontend && npx vitest run`
  - Ensure all existing tests pass (no regressions in other formatters or utilities)
  - Ensure all new bug condition and preservation tests pass
  - Ask the user if questions arise
