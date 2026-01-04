# Implementation Plan: Boat Identifier and Simplified Club List

## Overview

This implementation adds a unique boat number identifier and simplifies the club display format. The approach follows: backend logic → database migration → frontend updates → export updates.

## Tasks

- [x] 1. Implement backend boat number generation
  - [x] 1.1 Add generate_boat_number function to boat_registration_utils.py
    - Create function that takes event_type, display_order, race_id, and all_boats_in_race
    - Determine prefix: "M" for 42km, "SM" for 21km
    - Parse existing boat_numbers to find max sequence in race
    - Increment max sequence by 1
    - Return formatted boat_number: "{prefix}.{display_order}.{sequence}"
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 3.1, 14.1, 14.2, 14.3, 14.4, 14.5_

  - [x] 1.2 Write property test for boat number format
    - **Property 1: Boat Number Format**
    - **Validates: Requirements 2.1, 2.2, 2.3, 14.1, 14.3, 14.4, 14.5**

  - [x] 1.3 Write property test for boat number prefix
    - **Property 2: Boat Number Prefix - Marathon**
    - **Property 3: Boat Number Prefix - Semi-Marathon**
    - **Validates: Requirements 2.2, 2.3**

  - [x] 1.4 Write property test for boat number uniqueness
    - **Property 5: Boat Number Uniqueness**
    - **Validates: Requirements 3.1, 3.5**

  - [x] 1.5 Write property test for sequence increment
    - **Property 6: Boat Number Sequence Increment**
    - **Validates: Requirements 3.1, 3.4**

  - [x] 1.6 Write unit tests for edge cases
    - Test with no existing boats in race (sequence = 1)
    - Test with gaps in sequence numbers
    - Test with invalid boat_number formats (skip them)
    - Test with very high sequence numbers (9999)
    - _Requirements: 3.2, 3.4, 14.2_

- [x] 2. Update club display calculation to simplified format
  - [x] 2.1 Modify calculate_boat_club_info function in boat_registration_utils.py
    - Remove team manager priority logic
    - Remove "(Multi-Club)" and "({crew_club})" formatting
    - Create comma-separated list: ', '.join(club_list)
    - Calculate is_multi_club_crew as: len(club_list) > 1
    - Return boat_club_display, club_list, is_multi_club_crew
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 11.1, 11.2, 11.5_

  - [x] 2.2 Write property test for club display format
    - **Property 8: Club Display Comma Separation**
    - **Property 9: Club Display Alphabetical Order**
    - **Property 10: Club Display Matches Club List**
    - **Validates: Requirements 1.1, 1.2, 1.5, 1.7**

  - [x] 2.3 Write property test for multi-club flag
    - **Property 11: Multi-Club Flag Consistency**
    - **Validates: Requirements 11.5, 12.2, 12.3, 12.4**

  - [x] 2.4 Write unit tests for club display
    - Test single club: "RCPM"
    - Test multiple clubs: "Club Elite, RCPM, SN Versailles"
    - Test empty crew: team manager's club
    - Test case-insensitive sorting
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 3. Update database schema
  - [x] 3.1 Add boat_number field to boat_registration_schema in validation.py
    - Add boat_number as optional string field
    - Set maxlength to 20
    - Add regex validation: ^(M|SM)\.[0-9]{1,2}\.[0-9]{1,4}$
    - Update both functions/shared/validation.py and functions/layer/python/validation.py
    - _Requirements: 4.1_

  - [x] 3.2 Write unit tests for schema validation
    - Test boat_number accepts valid formats
    - Test boat_number rejects invalid formats
    - Test boat_number is optional (can be null)
    - _Requirements: 4.1_

- [x] 4. Update race assignment to generate boat_number
  - [x] 4.1 Modify update_boat_registration.py to generate boat_number when race is assigned
    - When race_id is set, fetch the race to get event_type and display_order
    - Query all boats with the same race_id
    - Call generate_boat_number with race info and existing boats
    - Set boat_number on boat registration
    - When race_id is cleared, set boat_number to null
    - _Requirements: 2.8, 4.3, 4.4, 4.5_

  - [x] 4.2 Write property test for boat_number generation on race assignment
    - **Property 7: Boat Number Null When No Race**
    - **Property 13: Boat Number Regeneration on Race Change**
    - **Validates: Requirements 2.9, 4.2, 4.4**

  - [x] 4.3 Write integration test for race assignment
    - Assign race to boat, verify boat_number is generated
    - Change boat's race, verify boat_number updates
    - Remove race from boat, verify boat_number is null
    - Assign multiple boats to same race, verify unique sequences
    - _Requirements: 2.6, 2.7, 2.8, 2.9, 3.1_

- [x] 5. Update admin boat endpoints
  - [x] 5.1 Modify admin_update_boat.py to regenerate boat_number on race change
    - Same logic as update_boat_registration.py
    - _Requirements: 2.8, 4.4_

  - [x] 5.2 Modify export_boat_registrations_json.py to include boat_number
    - Ensure boat_number is included in export
    - _Requirements: 4.1, 5.5_

- [x] 6. Checkpoint - Ensure all backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Create and run database migration
  - [x] 7.1 Create migration script generate_boat_numbers_and_simplify_clubs.py
    - Phase 1: Update all boat_club_display to simplified format
      - For each boat, recalculate boat_club_display using new format
      - Update is_multi_club_crew based on club_list.length
      - Keep club_list unchanged
    - Phase 2: Generate boat_numbers for all boats with races
      - Group boats by race_id
      - Sort boats by created_at within each race
      - Assign sequence numbers starting from 1
      - Generate and store boat_number for each boat
    - Log progress and errors
    - _Requirements: 1.1, 2.1, 2.4, 2.5, 4.3_

  - [x] 7.2 Test migration on dev database
    - Run migration script
    - Verify all boats have updated boat_club_display
    - Verify boats with races have boat_number
    - Verify no duplicate boat_numbers within same race
    - Spot-check accuracy
    - _Requirements: 4.1, 4.3_

  - [x] 7.3 Run migration on production database
    - Backup database before migration
    - Run migration script
    - Verify completion
    - Monitor for errors
    - _Requirements: 4.1, 4.3_

- [x] 8. Update admin boats page frontend
  - [x] 8.1 Add boat_number column to AdminBoats.vue
    - Add "Boat #" column header with sort functionality
    - Display boat.boat_number or "-" if null
    - Update table and card views
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 8.2 Update club display in AdminBoats.vue
    - Replace boat_club_display rendering (remove multi-club logic)
    - Display boat.boat_club_display directly (comma-separated)
    - Remove ClubListPopover component usage
    - Update filter logic to search boat_club_display
    - _Requirements: 10.1, 11.3, 11.4_

  - [x] 8.3 Add boat_number filtering and sorting
    - Add boat_number to filter search
    - Implement alphanumeric sorting for boat_number
    - _Requirements: 5.4_

  - [ ]* 8.4 Write unit tests for admin boats page
    - Test boat_number column display
    - Test boat_number sorting
    - Test boat_number filtering
    - Test simplified club display
    - _Requirements: 5.1, 5.3, 5.4, 10.1_

- [x] 9. Remove ClubListPopover component
  - [x] 9.1 Delete ClubListPopover.vue component
    - Remove component file
    - Remove all imports from other components
    - _Requirements: 11.3_

  - [x] 9.2 Remove multi-club detection logic from frontend
    - Remove isMultiClub functions
    - Remove multi-club badge styling
    - Simplify club display throughout frontend
    - _Requirements: 11.4_

- [x] 10. Update team manager boats interface
  - [x] 10.1 Add boat_number display to Boats.vue
    - Display boat_number prominently in boat cards
    - Show "No race" or "-" if boat_number is null
    - Update boat details view to show boat_number
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 10.2 Update club display in Boats.vue
    - Display simplified boat_club_display (comma-separated)
    - Remove multi-club indicator logic
    - _Requirements: 10.2, 11.4_

  - [ ]* 10.3 Write unit tests for team manager boats view
    - Test boat_number display
    - Test "No race" fallback
    - Test simplified club display
    - _Requirements: 6.1, 6.2, 10.2_

- [x] 11. Update CSV export formatter
  - [x] 11.1 Modify boatRegistrationsFormatter.js to include boat_number
    - Add "Boat Number" column with boat.boat_number
    - Update "Club" column to use simplified boat_club_display
    - Keep "Club List" column (semicolon-separated for compatibility)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 10.3_

  - [ ]* 11.2 Write unit tests for CSV export
    - Test boat_number column
    - Test simplified club display in "Club" column
    - Test empty boat_number handling
    - _Requirements: 7.1, 7.2, 7.3_

- [x] 12. Update CrewTimer export formatter
  - [x] 12.1 Modify crewTimerFormatter.js to use boat_number and simplified club
    - Use boat.boat_number for "Crew Abbrev" field
    - Use simplified boat.boat_club_display for "Crew" field
    - Keep "Bow" field unchanged (sequential bow number)
    - _Requirements: 8.1, 8.2, 8.3, 10.4_

  - [ ]* 12.2 Write unit tests for CrewTimer export
    - Test boat_number in Bow field
    - Test simplified club in Crew field
    - Test fallback when boat_number is null
    - _Requirements: 8.1, 8.2, 8.3_

- [x] 13. Update event program export formatter
  - [x] 13.1 Modify eventProgramFormatter.js to use boat_number and simplified club
    - Include boat.boat_number in program layout
    - Use simplified boat.boat_club_display for club field
    - Handle null boat_number gracefully (show "TBD" or omit)
    - _Requirements: 9.1, 9.2, 9.3, 10.5_

  - [ ]* 13.2 Write unit tests for event program export
    - Test boat_number display
    - Test simplified club display
    - Test null boat_number handling
    - Test in both English and French locales
    - _Requirements: 9.1, 9.2, 9.3_

- [x] 14. Handle crew member club updates
  - [x] 14.1 Verify update_crew_member.py recalculates club display
    - Existing logic should work with updated calculate_boat_club_info
    - Verify it produces simplified format
    - _Requirements: 13.4_

  - [ ]* 14.2 Write integration test for crew member club update
    - Update crew member's club
    - Verify boat_club_display updates to simplified format
    - _Requirements: 13.4_

- [x] 15. Handle edge cases
  - [x] 15.1 Add error handling for boat_number generation failures
    - If race not found, log error and set boat_number to null
    - If display_order missing, log error and use 0 as fallback
    - Allow boat to save even if boat_number generation fails
    - _Requirements: 13.2, 13.3_

  - [ ]* 15.2 Write integration tests for edge cases
    - Test boat_number generation with invalid race
    - Test boat_number with missing display_order
    - Test club display with all empty clubs
    - _Requirements: 13.2, 13.3, 13.5_

- [x] 16. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 17. Deploy to dev environment
  - Deploy backend changes
  - Deploy frontend changes
  - Verify boat_number generation in dev
  - Verify simplified club display in dev
  - Test all export formats
  - _Requirements: 12.5_

- [x] 18. Deploy to production
  - Deploy backend changes
  - Deploy frontend changes
  - Monitor for errors
  - Verify boat_number and club display in production
  - Test exports with real data
  - _Requirements: 12.5_

## Notes

- Tasks marked with `*` are optional test tasks that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Migration must be tested on dev before running on production
- Backend changes should be deployed before frontend to ensure API compatibility
- The boat_number generation logic queries all boats in a race, so performance should be monitored for races with many boats (though typically < 50 boats per race)
