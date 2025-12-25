# Implementation Plan

- [x] 1. Create backend JSON export endpoints
  - Create new Lambda functions that return JSON instead of CSV
  - Implement data aggregation and caching logic
  - Handle pagination for large datasets
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.3, 4.4, 5.1, 5.2, 5.3_

- [x] 1.1 Create export_crew_members_json.py Lambda function
  - Query all crew members from DynamoDB
  - Aggregate team manager information
  - Sort by team manager name, then crew member last name
  - Return JSON response with consistent structure
  - _Requirements: 1.1, 1.2, 1.3, 4.1, 4.3, 4.4, 5.1, 5.2, 5.3_

- [x] 1.2 Create export_boat_registrations_json.py Lambda function
  - Query all boat registrations from DynamoDB
  - Aggregate race names and team manager information
  - Include all boats regardless of status
  - Sort by team manager name, then event type, then boat type
  - Return JSON response with complete boat details
  - _Requirements: 2.1, 2.2, 2.3, 4.1, 4.3, 4.4, 5.1, 5.2, 5.3_

- [x] 1.3 Create export_races_json.py Lambda function
  - Query all races, boats, crew members, and team managers
  - Return comprehensive JSON with all entities
  - Include system configuration (competition date)
  - Cache team manager lookups for performance
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.3, 4.4, 5.1, 5.2, 5.3_

- [x] 1.4 Add API Gateway routes for new endpoints
  - Add GET /admin/export/crew-members route
  - Add GET /admin/export/boat-registrations route
  - Add GET /admin/export/races route
  - Configure CORS and authentication
  - _Requirements: 4.1, 4.2_

- [x] 2. Write backend integration tests
  - Test JSON response structure and content
  - Test data aggregation and sorting
  - Test pagination handling
  - Test error scenarios
  - _Requirements: 6.1, 6.2, 6.3_

- [x] 2.1 Write tests for crew members export
  - Test JSON structure matches design
  - Test team manager information is included
  - Test sorting by team manager and crew member name
  - Test pagination for large datasets
  - Test empty database scenario
  - _Requirements: 6.1, 6.2, 6.3_

- [x] 2.2 Write tests for boat registrations export
  - Test JSON structure matches design
  - Test all boats are included (no status filtering)
  - Test race names are included
  - Test crew composition details are included
  - Test sorting logic
  - _Requirements: 6.1, 6.2, 6.3_

- [x] 2.3 Write tests for races export
  - Test all entities are included (races, boats, crew, managers)
  - Test boats include all statuses (complete, paid, free, incomplete, forfait)
  - Test Decimal to number conversion
  - Test missing team manager handling
  - Test empty database scenario
  - _Requirements: 6.1, 6.2, 6.3_

- [x] 3. Create frontend formatter utilities
  - Implement CSV generation for crew members
  - Implement CSV generation for boat registrations
  - Implement CrewTimer Excel generation
  - Handle special characters and escaping
  - _Requirements: 1.4, 1.5, 2.4, 2.5, 3.6-3.15, 4.5_

- [x] 3.1 Create crewMembersFormatter.js
  - Implement formatCrewMembersToCSV function
  - Define CSV column headers
  - Map JSON fields to CSV columns
  - Handle special character escaping
  - Implement downloadCrewMembersCSV function
  - _Requirements: 1.4, 1.5, 4.5_

- [x] 3.2 Create boatRegistrationsFormatter.js
  - Implement formatBoatRegistrationsToCSV function
  - Define CSV column headers
  - Calculate filled seats as "X/Y" format
  - Format boolean values as Yes/No
  - Handle nested data structures
  - Implement downloadBoatRegistrationsCSV function
  - _Requirements: 2.4, 2.5, 4.5_

- [x] 3.3 Create crewTimerFormatter.js
  - Implement formatRacesToCrewTimer function
  - Filter boats (complete/paid/free, exclude forfait)
  - Sort races (marathon first, then semi-marathon)
  - Format semi-marathon race names (boat_type [Y] age gender)
  - Keep marathon race names unchanged
  - Assign event numbers (per race)
  - Assign bow numbers (global sequential)
  - Calculate average age
  - Extract stroke seat name
  - Implement downloadCrewTimerExcel function
  - _Requirements: 3.6-3.15, 4.5_

- [x] 3.4 Create shared utility functions
  - Implement getBoatTypeDisplay for boat type conversion
  - Implement CSV escaping utility
  - Implement file download utility
  - Implement date formatting utility
  - _Requirements: 4.5_

- [x] 4. Write frontend unit tests
  - Test CSV generation and formatting
  - Test CrewTimer transformations
  - Test edge cases and error handling
  - _Requirements: 6.4, 6.5, 6.6_

- [x] 4.1 Write tests for crewMembersFormatter
  - Test CSV structure and headers
  - Test special character escaping
  - Test empty dataset handling
  - Test missing field handling
  - _Requirements: 6.4, 6.5, 6.6_

- [x] 4.2 Write tests for boatRegistrationsFormatter
  - Test CSV structure and headers
  - Test filled seats calculation
  - Test boolean formatting (Yes/No)
  - Test nested data handling
  - _Requirements: 6.4, 6.5, 6.6_

- [x] 4.3 Write tests for crewTimerFormatter
  - Test boat filtering (complete/paid/free, exclude forfait)
  - Test race sorting (marathon before semi-marathon)
  - Test event numbering (same race = same event num)
  - Test bow numbering (global sequential)
  - Test semi-marathon race name formatting
  - Test marathon race name unchanged
  - Test gender mapping (MAN/WOMAN/MIXED)
  - Test yolette detection (Y marker)
  - Test stroke seat extraction
  - Test average age calculation
  - Test empty dataset handling
  - _Requirements: 6.4, 6.5, 6.6_

- [x] 5. Update frontend UI component
  - Update AdminDataExport.vue to use new endpoints
  - Add loading indicators
  - Add error handling and user feedback
  - Implement download functionality
  - _Requirements: 4.5, 5.4_

- [x] 5.1 Update AdminDataExport.vue component
  - Add methods to call new JSON export endpoints
  - Integrate formatter utilities
  - Add loading state during export
  - Add error handling with user-friendly messages
  - Add success feedback after download
  - Keep fallback to old endpoints for backward compatibility
  - _Requirements: 4.5, 5.4, 7.2_

- [x] 6. Deploy and test in dev environment
  - Deploy backend Lambda functions
  - Deploy frontend changes
  - Test all three export types
  - Verify performance with large datasets
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7. Remove old export endpoints
  - Delete old Lambda functions (export_crew_members.py, export_boat_registrations.py, export_crewtimer.py)
  - Remove old API Gateway routes from api_stack.py
  - Remove fallback logic from frontend component
  - Remove tests for old endpoints
  - _Requirements: 7.3, 7.5_

- [x] 8. Final verification and documentation
  - Verify all three new export types work in dev
  - Verify no errors in production after cleanup
  - Update documentation to reflect new architecture
  - Confirm old endpoints are fully removed
  - _Requirements: 7.5_
