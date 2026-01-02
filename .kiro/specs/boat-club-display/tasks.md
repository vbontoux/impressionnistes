# Implementation Plan: Boat Club Display

## Overview

This implementation adds calculated club display fields to boat registrations, showing either a single club name or "Multi-Club" with a detailed club list. The implementation follows a phased approach: backend calculation → data migration → frontend display → export updates.

## Tasks

- [ ] 1. Implement backend club calculation logic
  - [x] 1.1 Add calculate_boat_club_info function to boat_registration_utils.py
    - Create function that takes crew members and team manager club
    - Extract non-empty club affiliations from crew members
    - Normalize to uppercase for comparison, preserve original case for display
    - Return boat_club_display (club name or "Multi-Club") and club_list (sorted unique clubs)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 1.2 Write property test for calculate_boat_club_info
    - **Property 1: Single Club Display**
    - **Validates: Requirements 1.1**

  - [x] 1.3 Write property test for multi-club detection
    - **Property 2: Multi-Club Display**
    - **Validates: Requirements 1.2**

  - [x] 1.4 Write property test for empty boat fallback
    - **Property 3: Empty Boat Fallback**
    - **Validates: Requirements 1.3**

  - [x] 1.5 Write property test for club list uniqueness
    - **Property 4: Club List Uniqueness**
    - **Validates: Requirements 2.1, 2.2**

  - [x] 1.6 Write property test for club list sorting
    - **Property 5: Club List Sorting**
    - **Validates: Requirements 2.4**

  - [x] 1.7 Write property test for case-insensitive comparison
    - **Property 10: Case Insensitive Comparison**
    - **Validates: Requirements 1.4**

  - [x] 1.8 Write unit tests for edge cases
    - Test all empty clubs
    - Test null vs empty string handling
    - Test whitespace trimming
    - Test single crew member
    - _Requirements: 9.3, 9.4, 9.5_

- [x] 2. Update database schema and validation
  - [x] 2.1 Add boat_club_display and club_list to boat_registration_schema in validation.py
    - Add boat_club_display as optional string field
    - Add club_list as optional list of strings
    - Update both functions/shared/validation.py and functions/layer/python/validation.py
    - _Requirements: 3.1, 3.2_

  - [x] 2.2 Write unit tests for schema validation
    - Test boat_club_display accepts string
    - Test club_list accepts array of strings
    - Test fields are optional
    - _Requirements: 3.1, 3.2_

- [x] 3. Update boat creation to initialize club fields
  - [x] 3.1 Modify create_boat_registration.py to set initial club values
    - Get team manager's club_affiliation
    - Set boat_club_display to team manager's club
    - Set club_list to [team_manager_club] (if not empty)
    - Set is_multi_club_crew to False
    - _Requirements: 3.5_

  - [x] 3.2 Write integration test for boat creation
    - Create boat, verify club fields are initialized
    - Verify boat_club_display equals team manager club
    - Verify club_list contains only team manager club
    - _Requirements: 3.5_

- [x] 4. Update seat assignment to recalculate club fields
  - [x] 4.1 Modify assign_seat.py to calculate club info after assignment
    - After seat assignment, get all assigned crew members
    - Get team manager's club
    - Call calculate_boat_club_info
    - Update boat_registration with boat_club_display and club_list
    - Update is_multi_club_crew for backward compatibility
    - _Requirements: 3.3, 10.2, 10.3_

  - [x] 4.2 Write property test for seat assignment recalculation
    - **Property 12: Recalculation on Assignment**
    - **Validates: Requirements 3.3**

  - [x] 4.3 Write integration test for seat assignment
    - Assign crew from single club, verify club display
    - Assign crew from multiple clubs, verify "Multi-Club"
    - Remove crew member, verify recalculation
    - _Requirements: 3.3_

- [x] 5. Update boat update endpoint to recalculate club fields
  - [x] 5.1 Modify update_boat_registration.py to calculate club info
    - After updating seats, get assigned crew members
    - Get team manager's club
    - Call calculate_boat_club_info
    - Update boat with boat_club_display and club_list
    - Update is_multi_club_crew for backward compatibility
    - _Requirements: 3.4, 10.2, 10.3_

  - [x] 5.2 Write integration test for boat update
    - Update boat seats, verify club recalculation
    - Test with single club and multi-club scenarios
    - Test bulk unassignment recalculates correctly
    - _Requirements: 3.4_

- [x] 6. Update admin boat endpoints
  - [x] 6.1 Modify admin_create_boat.py to initialize club fields
    - Same logic as create_boat_registration.py
    - _Requirements: 3.5_

  - [x] 6.2 Modify admin_update_boat.py to recalculate club fields
    - Same logic as update_boat_registration.py
    - _Requirements: 3.4_

  - [x] 6.3 Modify export_boat_registrations_json.py to include club fields
    - Ensure boat_club_display and club_list are included in export
    - _Requirements: 3.1, 3.2_

- [x] 7. Checkpoint - Ensure all backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Create and run database migration
  - [x] 8.1 Create migration script calculate_boat_clubs.py
    - Scan all boat registrations
    - For each boat, fetch assigned crew and team manager
    - Calculate boat_club_display and club_list
    - Update boat registration in database
    - Log progress and errors
    - _Requirements: 3.3, 3.4, 3.5_

  - [x] 8.2 Test migration on dev database
    - Run migration script
    - Verify all boats have club fields
    - Spot-check accuracy of calculations
    - _Requirements: 3.1, 3.2_

  - [x] 8.3 Run migration on production database
    - Backup database before migration
    - Run migration script
    - Verify completion
    - Monitor for errors
    - _Requirements: 3.1, 3.2_

- [x] 9. Update admin boats page frontend
  - [x] 9.1 Replace team_manager_club with boat_club_display in AdminBoats.vue
    - ✅ Updated table column to show boat_club_display
    - ✅ Updated card view to show boat_club_display
    - ✅ Updated filter logic to search boat_club_display and club_list
    - ✅ Updated sort logic to use boat_club_display
    - _Requirements: 4.1, 4.4, 4.5_

  - [x] 9.2 Create ClubListPopover.vue component
    - Create reusable component for displaying club list
    - Show list of clubs in a tooltip or popover
    - Style for readability
    - _Requirements: 4.2, 4.3_

  - [x] 9.3 Add multi-club indicator with popover to AdminBoats.vue
    - When boat_club_display is "Multi-Club", show badge
    - Add click/hover handler to show ClubListPopover
    - Pass club_list to popover component
    - _Requirements: 4.2, 4.3_

  - [x] 9.4 Write unit tests for club display components
    - Test single club display
    - Test multi-club badge rendering
    - Test popover shows correct clubs
    - Test filtering by club
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 10. Update team manager boats interface
  - [x] 10.1 Update MyBoats.vue to display boat_club_display
    - Replace any team manager club references with boat_club_display
    - Show club list for multi-club crews in boat details
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 10.2 Add club list display to boat details view
    - Show complete club_list when viewing boat details
    - Use ClubListPopover component for consistency
    - _Requirements: 5.3_

- [x] 11. Update CSV export formatter
  - [x] 11.1 Modify boatRegistrationsFormatter.js to include club columns
    - Add "Club" column with boat_club_display
    - Add "Club List" column with club_list.join('; ')
    - Keep "Team Manager Club" column for reference
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 11.2 Write unit tests for CSV export
    - Test single club export
    - Test multi-club export with club list
    - Test semicolon separation in club list
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 12. Update CrewTimer export formatter
  - [x] 12.1 Modify crewTimerFormatter.js to use boat_club_display
    - Replace club calculation logic with boat.boat_club_display
    - Remove fallback to boat.club_affiliation (dead code)
    - Simplify to: const clubName = boat.boat_club_display || 'Unknown'
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x] 12.2 Write unit tests for CrewTimer export
    - Test single club in Crew field
    - Test "Multi-Club" in Crew field
    - Test fallback to "Unknown" if missing
    - _Requirements: 7.1, 7.2, 7.3_

- [x] 13. Update event program export formatter
  - [x] 13.1 Modify eventProgramFormatter.js to use boat_club_display
    - Use boat.boat_club_display for club field
    - No translation needed ("Multi-Club" works in both languages)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 13.2 Write unit tests for event program export
    - Test single club display
    - Test "Multi-Club" display
    - Test in both English and French locales
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 14. Handle crew member club updates
  - [x] 14.1 Modify update_crew_member.py to trigger boat recalculation
    - When club_affiliation is updated, find all boats the crew member is assigned to
    - For each boat, recalculate boat_club_display and club_list
    - Update all affected boats
    - _Requirements: 9.1_

  - [x] 14.2 Write integration test for crew member club update
    - Update crew member's club
    - Verify all assigned boats recalculate club info
    - _Requirements: 9.1_

- [x] 15. Handle team manager club updates
  - [x] 15.1 Modify update_profile.py to trigger boat recalculation
    - When team manager's club_affiliation is updated, find all their boats with no crew
    - For each empty boat, recalculate boat_club_display and club_list
    - Update all affected boats
    - _Requirements: 9.2_

  - [x] 15.2 Write integration test for team manager club update
    - Update team manager's club
    - Verify empty boats recalculate club info
    - Verify boats with crew are not affected
    - _Requirements: 9.2_

- [x] 16. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 17. Deploy to dev environment
  - Deploy backend changes
  - Deploy frontend changes
  - Verify club display in dev
  - Test all export formats
  - _Requirements: 10.5_

- [x] 18. Deploy to production
  - Deploy backend changes
  - Deploy frontend changes
  - Monitor for errors
  - Verify club display in production
  - Test exports with real data
  - _Requirements: 10.5_

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Migration must be tested on dev before running on production
- Backend changes should be deployed before frontend to ensure API compatibility
