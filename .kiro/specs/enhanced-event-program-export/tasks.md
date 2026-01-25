# Implementation Plan: Enhanced Event Program Export

## Overview

This implementation plan enhances the existing event program export (currently 2 sheets) to generate a comprehensive 4-sheet Excel file. The existing implementation already has:
- xlsx library installed and working
- Event program formatter (`eventProgramFormatter.js`) with crew member list and race schedule
- Comprehensive tests for existing functionality
- Race numbering and boat filtering utilities

This plan focuses on adding 2 new sheets and enhancing the existing crew member list with additional columns.

## Tasks

- [x] 1. Verify existing infrastructure
  - [x] 1.1 Review existing event program export
    - Verify `frontend/src/utils/exportFormatters/eventProgramFormatter.js` works correctly
    - Verify xlsx library (v0.18.5) is installed and functional
    - Review existing tests in `eventProgramFormatter.test.js`
    - Understand current 2-sheet structure (Crew Member List + Race Schedule)
    - _Requirements: 5.1, 5.4, 5.5_
  
  - [x] 1.2 Review existing utilities to reuse
    - Review `filterEligibleBoats()` in `raceNumbering.js`
    - Review `assignRaceAndBowNumbers()` for race/bow number logic
    - Review `formatDateForFilename()` in `shared.js`
    - Identify which helper functions can be reused
    - _Requirements: 5.1, 5.4, 5.5_

- [x] 2. Enhance existing crew member list (Sheet 1)
  - [x] 2.1 Add new columns to crew member list
    - Add Age column (from crew_member.age)
    - Add Gender column (from crew_member.gender)
    - Add License # column (from crew_member.license_number)
    - Add Place in boat column (from seat.seat_type)
    - Add Assigned Boat column (formatted as "name - comment")
    - Update column order per requirements
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_
  
  - [x] 2.2 Implement assigned boat formatting helper
    - Add `formatAssignedBoat(boat)` function
    - Format as "name - comment" when both present
    - Format as just name when only name present
    - Return empty string when neither present
    - _Requirements: 1.6, 1.8_
  
  - [x] 2.3 Update existing tests for enhanced crew member list
    - Extend existing tests in `eventProgramFormatter.test.js`
    - Add tests for new columns (age, gender, license, seat position)
    - Add tests for assigned boat formatting
    - Reuse existing test structure and patterns
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6_
  
  - [x] 2.4 Write property test for assigned boat formatting
    - **Property 3: Assigned Boat Formatting**
    - **Validates: Requirements 1.6, 3.6**
    - Test formatting with various combinations of name/comment
    - Keep test simple - verify format rules only
    - _Requirements: 1.6, 3.6_

- [x] 3. Implement Sheet 3: Crews in Races
  - [x] 3.1 Create generateCrewsInRaces function
    - Add `generateCrewsInRaces(jsonData, boatAssignments, raceAssignments, locale, t)` to eventProgramFormatter.js
    - Include columns: Race #, Race name, Crew #, Boat assignment
    - Include 9 crew member positions × 5 fields each (45 columns)
    - Sort boats by race number (reuse existing sorting logic)
    - _Requirements: 3.1, 3.2, 3.3, 3.7_
  
  - [x] 3.2 Implement crew member column generation
    - For each boat, extract up to 9 crew members
    - For each member: Last name, First name, Club, Age, Gender
    - Fill empty strings for positions beyond crew size
    - Maintain seat order from boat.seats array
    - _Requirements: 3.3, 3.4, 3.5_
  
  - [x] 3.3 Add localized headers for Sheet 3
    - Create `getCrewsInRacesHeaders(locale)` function
    - Support French and English column headers
    - Include headers for all 49 columns (4 + 45)
    - _Requirements: 3.9, 6.1, 6.2_
  
  - [x] 3.4 Write unit tests for Sheet 3 generation
    - Test with boats of varying crew sizes (1-9 members)
    - Test empty position handling
    - Test race number sorting
    - Test assigned boat formatting
    - Extend existing test file
    - _Requirements: 3.1, 3.3, 3.5, 3.7_
  
  - [x] 3.5 Write property test for variable crew size handling
    - **Property 5: Variable Crew Size Handling**
    - **Validates: Requirements 3.3, 3.5**
    - Test that rows have correct data for N members and empty for remaining
    - Keep test simple - verify structure only
    - _Requirements: 3.3, 3.5_
  
  - [x] 3.6 Write property test for race number ordering
    - **Property 7: Race Number Ordering**
    - **Validates: Requirements 3.7**
    - Test that rows are sorted by race number ascending
    - Keep test simple - verify sort order only
    - _Requirements: 3.7_

- [x] 4. Implement Sheet 4: Synthesis by Club Manager
  - [x] 4.1 Create generateSynthesis function
    - Add `generateSynthesis(jsonData, boatAssignments, locale, t)` to eventProgramFormatter.js
    - Group boats by team_manager_id
    - Calculate counts: assigned boats, marathon crews, semi-marathon crews
    - Include columns: Club, Full name, Email, Phone, counts
    - _Requirements: 4.1, 4.2, 4.10_
  
  - [x] 4.2 Implement team manager aggregation logic
    - Count assigned boats (non-empty assigned_boat_identifier)
    - Count marathon crews (event_type === 'Marathon')
    - Count semi-marathon crews (event_type === 'Semi-Marathon')
    - Only count eligible boats (reuse filterEligibleBoats)
    - _Requirements: 4.4, 4.5, 4.6, 4.8_
  
  - [x] 4.3 Implement name formatting helper
    - Add `formatTeamManagerName(manager)` function
    - Format as "FirstName LastName"
    - Handle missing names gracefully
    - _Requirements: 4.3_
  
  - [x] 4.4 Add localized headers for Sheet 4
    - Create `getSynthesisHeaders(locale)` function
    - Support French and English column headers
    - Include all 7 columns
    - _Requirements: 4.9, 6.1, 6.2_
  
  - [x] 4.5 Write unit tests for Sheet 4 generation
    - Test team manager grouping
    - Test count calculations
    - Test name formatting
    - Test with missing phone numbers
    - Extend existing test file
    - _Requirements: 4.1, 4.3, 4.4, 4.5, 4.6, 4.7_
  
  - [x] 4.6 Write property test for team manager aggregation
    - **Property 11: Team Manager Aggregation**
    - **Validates: Requirements 4.10**
    - Test that each manager appears exactly once with correct counts
    - Keep test simple - verify uniqueness and count presence
    - _Requirements: 4.10_
  
  - [x] 4.7 Write property test for counting logic
    - **Property 9: Assigned Boat Counting**
    - **Property 10: Event Type Crew Counting**
    - **Validates: Requirements 4.4, 4.5, 4.6, 4.8**
    - Test count calculations with various boat distributions
    - Keep test simple - verify counts match input data
    - _Requirements: 4.4, 4.5, 4.6, 4.8_

- [x] 5. Update main export function for 4 sheets
  - [x] 5.1 Modify downloadEventProgramExcel function
    - Keep existing Sheet 1 (enhanced crew member list) and Sheet 2 (race schedule)
    - Add Sheet 3 (Crews in Races) generation
    - Add Sheet 4 (Synthesis) generation
    - Update sheet names for all 4 sheets based on locale
    - Maintain existing error handling and validation
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 6.3, 7.1, 7.2_
  
  - [x] 5.2 Update filename generation
    - Keep existing `formatDateForFilename()` usage
    - Update filename to reflect 4-sheet export
    - Maintain format: "programme_evenement_YYYY-MM-DD.xlsx"
    - _Requirements: 7.6_
  
  - [x] 5.3 Write property test for export completeness
    - **Property 1: Eligible Boat Filtering**
    - **Validates: Requirements 1.1, 3.8, 4.8, 5.2, 5.3**
    - Test that all sheets only include eligible boats
    - Keep test simple - verify filtering consistency
    - _Requirements: 1.1, 3.8, 4.8, 5.2, 5.3_
  
  - [x] 5.4 Write property test for 4-sheet structure
    - **Property 2: Required Field Completeness**
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.5**
    - Test that workbook has exactly 4 sheets with correct names
    - Test that each sheet has required columns
    - Keep test simple - verify structure only
    - _Requirements: 7.1, 7.2_

- [ ] 6. Checkpoint - Verify 4-sheet export works
  - Manually test export with sample data
  - Verify all 4 sheets are present with correct names
  - Verify Sheet 1 has new columns (age, gender, license, seat, assigned boat)
  - Verify Sheet 2 (race schedule) is unchanged
  - Verify Sheet 3 has crews organized by race
  - Verify Sheet 4 has team manager synthesis
  - Open Excel file in Excel/LibreOffice to verify formatting
  - Ask the user if questions arise

- [x] 7. Update localization
  - [x] 7.1 Add missing translation keys
    - Review existing keys in `frontend/src/locales/fr.json` and `en.json`
    - Add keys for new column headers (age, gender, license, place in boat, assigned boat)
    - Add keys for Sheet 3 and Sheet 4 names
    - Add keys for Sheet 3 column headers (member 1-9 fields)
    - Add keys for Sheet 4 column headers
    - _Requirements: 1.9, 3.9, 4.9, 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 7.2 Write property test for localization consistency
    - **Property 4: Localization Consistency**
    - **Validates: Requirements 1.9, 3.9, 4.9, 6.1, 6.2, 6.3, 7.2**
    - Test that all headers are translated in both locales
    - Test that sheet names are translated in both locales
    - Keep test simple - verify translation key existence
    - _Requirements: 1.9, 3.9, 4.9, 6.1, 6.2, 6.3, 7.2_

- [x] 8. Handle edge cases and error scenarios
  - [x] 8.1 Handle missing crew member data
    - Test with boats that have missing crew_member_id references
    - Use placeholder values for missing members (similar to existing code)
    - Log warnings for missing data
    - _Requirements: 8.3_
  
  - [x] 8.2 Handle missing team manager data
    - Test with boats that have missing team_manager_id references
    - Skip boats without team managers in synthesis sheet
    - Log warnings for missing data
    - _Requirements: 8.3_
  
  - [x] 8.3 Handle empty assigned boat fields
    - Test with boats that have null/empty assigned_boat_name
    - Display empty string in assigned boat column
    - _Requirements: 1.8, 3.6_
  
  - [x] 8.4 Handle missing phone numbers
    - Test with team managers that have null/empty phone
    - Display empty string in phone column
    - _Requirements: 4.7_
  
  - [x] 8.5 Write property test for malformed data handling
    - **Property 13: Malformed Data Handling**
    - **Validates: Requirements 8.3**
    - Test that missing/malformed data doesn't cause exceptions
    - Keep test simple - verify no crashes with bad data
    - _Requirements: 8.3_

- [x] 9. Verify UI integration (already exists)
  - [x] 9.1 Review existing UI integration
    - Verify `AdminDataExport.vue` already has event program export button
    - Verify button calls `exportEventProgram()` function
    - Verify loading states and error handling work correctly
    - No changes needed - UI already integrated
    - _Requirements: 8.1, 8.2, 8.5_
  
  - [x] 9.2 Test export from admin dashboard
    - Navigate to admin data export page
    - Click "Export Event Program" button
    - Verify 4-sheet Excel file downloads
    - Verify all sheets have correct data
    - _Requirements: 7.5, 8.1_

- [x] 10. Final integration and testing
  - [ ] 10.1 Run all existing tests
    - Run `npm test` to verify all tests pass
    - Verify no regressions in existing functionality
    - Fix any broken tests
    - _Requirements: All_
  
  - [x] 10.2 Integration testing with real data
    - Test export with actual race program data from dev environment
    - Verify all 4 sheets have correct data
    - Verify column headers match requirements
    - Verify data formatting (dates, numbers, text)
    - _Requirements: All_
  
  - [x] 10.3 Cross-browser testing
    - Test in Chrome, Firefox, Safari
    - Verify download works in all browsers
    - Verify Excel file opens correctly
    - _Requirements: 7.5_
  
  - [x] 10.4 Test with various data scenarios
    - Test with small dataset (few boats)
    - Test with large dataset (many boats)
    - Test with boats of varying crew sizes (1-9 members)
    - Test with multi-club crews
    - Test with missing optional data (phone, assigned boat)
    - _Requirements: All_

- [x] 11. Final checkpoint - Complete feature verification
  - Run full test suite (unit + property tests)
  - Verify no console errors or warnings
  - Test complete user flow from button click to file download
  - Verify all 4 sheets match requirements specification
  - Ask the user if questions arise

## Notes

- **Reuse existing code**: The event program export already exists with 2 sheets. This task enhances it to 4 sheets.
- **xlsx library**: Already installed (v0.18.5) and working. No need to install or change.
- **Existing tests**: Extend `eventProgramFormatter.test.js` rather than creating new test files.
- **Existing utilities**: Reuse `filterEligibleBoats()`, `assignRaceAndBowNumbers()`, `formatDateForFilename()`, etc.
- **UI integration**: Already exists in `AdminDataExport.vue`. No changes needed to UI component.
- **Property tests**: Use fast-check library (already installed v4.5.3). Keep tests simple with 100 iterations minimum.
- **Localization**: Extend existing translation files. Follow existing patterns for column headers.
- **Error handling**: Follow existing patterns in `eventProgramFormatter.js` for graceful degradation.
- **Testing approach**: Extend existing tests rather than recreating. Add new test cases to existing describe blocks.
