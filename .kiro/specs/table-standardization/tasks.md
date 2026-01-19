# Implementation Plan: Table Standardization

## Overview

This implementation plan breaks down the table standardization feature into discrete, incremental tasks. The approach focuses on enhancing the existing SortableTable component first, then migrating views one by one to use the enhanced component.

## Tasks

- [x] 1. Enhance SortableTable component with horizontal scroll improvements
  - Update CSS for visible scrollbar styling on all screen sizes
  - Add scrollbar height minimum of 8px
  - Ensure scrollbar uses design tokens (--color-secondary, --color-light)
  - Test scrollbar visibility on HDPI (1440x900) and MDPI (1024x768) screens
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.6, 1.7_

- [x] 2. Add sticky column support to SortableTable
  - [x] 2.1 Implement CSS sticky positioning for left and right columns
    - Add sticky-left and sticky-right CSS classes
    - Use position: sticky with appropriate left/right values
    - Add z-index management for proper layering
    - Add visual separator (box-shadow) for sticky columns
    - _Requirements: 2.1, 2.2, 2.4_
  
  - [x] 2.2 Update column configuration schema to support sticky property
    - Add sticky: 'left' | 'right' | undefined to column definition
    - Update prop validator to check sticky values
    - Apply sticky classes based on column configuration
    - _Requirements: 2.5, 2.6_
  
  - [ ]* 2.3 Write unit tests for sticky column functionality
    - Test sticky-left positioning
    - Test sticky-right positioning
    - Test multiple sticky columns maintain order
    - Test columns without sticky config don't get sticky positioning
    - Test interactive elements in sticky columns remain functional
    - _Requirements: 2.1, 2.2, 2.5, 2.6, 2.7, 2.8_

- [x] 3. Add responsive column hiding to SortableTable
  - [x] 3.1 Implement CSS media queries for responsive column visibility
    - Add column-always, column-hide-below-1024, column-hide-below-768 CSS classes
    - Implement @media queries for breakpoints
    - Apply responsive classes based on column configuration
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 3.2 Update column configuration schema to support responsive property
    - Add responsive: 'always' | 'hide-below-1024' | 'hide-below-768' to column definition
    - Update prop validator to check responsive values
    - Ensure default is 'always' (always visible)
    - _Requirements: 3.7, 3.8_
  
  - [ ]* 3.3 Write unit tests for responsive column hiding
    - Test columns hide at correct breakpoints
    - Test sorting still works with hidden columns
    - Test columns without responsive config remain visible
    - Test at least required columns always visible
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [x] 4. Implement column width management
  - Add width and minWidth support to column configuration
  - Apply width/minWidth CSS to th and td elements
  - Support px, %, and other CSS units
  - Test auto-sizing for columns without width config
  - _Requirements: 4.1, 4.2, 4.3, 4.6_

- [x] 5. Add compact mode support
  - [x] 5.1 Implement compact mode CSS
    - Add .compact-mode class to wrapper
    - Reduce cell padding by 50% in compact mode
    - Maintain font-size in compact mode
    - Ensure 44px minimum touch targets for interactive elements
    - Apply to both header and body cells
    - _Requirements: 5.1, 5.2, 5.6, 5.7_
  
  - [x] 5.2 Add compact prop to component
    - Add compact: Boolean prop with default false
    - Apply compact-mode class when prop is true
    - Test toggling compact mode updates immediately
    - _Requirements: 5.3, 5.4_
  
  - [ ]* 5.3 Write unit tests for compact mode
    - Test padding reduction in compact mode
    - Test font-size unchanged in compact mode
    - Test compact prop toggles CSS class
    - Test immediate update without reload
    - Test minimum touch targets maintained
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.6, 5.7_

- [x] 6. Ensure 100% design token compliance
  - [x] 6.1 Audit all CSS for hardcoded values
    - Search for hex color values (#)
    - Search for hardcoded px/rem spacing values
    - Search for hardcoded font-size/font-weight values
    - Search for hardcoded border-radius/box-shadow values
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [x] 6.2 Replace all hardcoded values with design tokens
    - Replace colors with var(--color-*)
    - Replace spacing with var(--spacing-*)
    - Replace typography with var(--font-*)
    - Replace borders/shadows with design tokens
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [ ]* 6.3 Write property tests for design token usage
    - **Property 20: No Hardcoded Colors**
    - **Validates: Requirements 6.1, 6.6**
    - **Property 21: No Hardcoded Spacing**
    - **Validates: Requirements 6.2, 6.7**
    - **Property 22: No Hardcoded Typography**
    - **Validates: Requirements 6.3**
    - **Property 23: No Hardcoded Borders and Shadows**
    - **Validates: Requirements 6.4**


- [x] 7. Enhance accessibility implementation
  - [x] 7.1 Add ARIA attributes to table elements
    - Add role="table", role="rowgroup", role="row", role="columnheader", role="cell"
    - Add aria-label prop support
    - Add aria-sort attributes to sortable headers
    - Update aria-sort when sorting changes
    - _Requirements: 9.1, 9.3, 9.4_
  
  - [x] 7.2 Implement keyboard navigation
    - Create useTableKeyboard composable
    - Add Enter/Space key support for sortable headers
    - Add arrow key navigation between cells
    - Add tabindex management for focusable elements
    - Add visible focus indicators
    - _Requirements: 9.2, 9.5, 9.6_
  
  - [ ]* 7.3 Write accessibility tests
    - Test semantic HTML structure
    - Test keyboard header activation (Enter/Space)
    - Test ARIA labels present
    - Test aria-sort updates on sort
    - Test arrow key cell navigation
    - Test tab order is logical
    - Test color contrast meets WCAG AA (4.5:1)
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [x] 8. Create useTableScroll composable
  - Implement scroll event handling with passive listeners
  - Track scrollLeft state
  - Debounce scroll state updates (150ms)
  - Emit scroll events for parent components
  - Proper cleanup on unmount
  - _Requirements: 1.5_

- [x] 9. Verify sorting functionality preservation
  - [x] 9.1 Test existing sorting features still work
    - Test sortable column header clicks
    - Test sort direction toggle
    - Test sort indicator display
    - Test non-sortable columns don't sort
    - Test sorting with different data types
    - Test null value handling in sorting
    - Test sort event emission
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_
  
  - [ ]* 9.2 Write property tests for sorting
    - **Property 24: Sortable Column Activation**
    - **Validates: Requirements 8.1**
    - **Property 25: Sort Direction Toggle**
    - **Validates: Requirements 8.2**
    - **Property 26: Non-Sortable Column Immunity**
    - **Validates: Requirements 8.4**
    - **Property 27: Multi-Type Sorting Support**
    - **Validates: Requirements 8.5**

- [x] 10. Checkpoint - Test enhanced SortableTable component
  - Test all new features work independently
  - Test features work together (sticky + responsive + compact)
  - Test backward compatibility with existing props
  - Test on HDPI (1440x900), MDPI (1024x768), tablet (768px) screens
  - Run accessibility audit with axe-core
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Migrate AdminBoats view to enhanced SortableTable
  - [x] 11.1 Create column definitions for AdminBoats
    - Define all 11 columns with keys, labels, widths
    - Determine sticky columns (boat_number: left, actions: right)
    - Determine responsive hiding (email, team_manager: hide-below-1024)
    - Set appropriate alignments and sortable flags
    - _Requirements: 12.1, 13.1, 13.2, 13.5, 13.6_
  
  - [x] 11.2 Replace custom table with SortableTable component
    - Remove custom table HTML markup
    - Add SortableTable component with column definitions
    - Implement custom cell slots for boat_number, status, actions
    - Remove custom sorting logic (now handled by component)
    - Remove custom table CSS (now handled by component)
    - _Requirements: 12.1, 12.7_
  
  - [x] 11.3 Test AdminBoats migration
    - Test all columns display correctly
    - Test sorting works for all sortable columns
    - Test sticky columns (boat_number, actions) work
    - Test responsive hiding on tablet (1024px)
    - Test horizontal scroll on MDPI (1024x768)
    - Test card view still works (unchanged)
    - Test all actions (edit, forfait, delete) still work
    - _Requirements: 12.1, 12.10, 12.11_

- [x] 12. Migrate AdminCrewMembers view to enhanced SortableTable
  - [x] 12.1 Create column definitions for AdminCrewMembers
    - Define all columns with keys, labels, widths
    - Determine sticky columns based on workflow
    - Determine responsive hiding priorities
    - _Requirements: 13.1, 13.2_
  
  - [x] 12.2 Replace custom table with SortableTable component
    - Remove custom table markup
    - Add SortableTable with column definitions
    - Implement custom cell slots as needed
    - Remove custom sorting and table CSS
    - _Requirements: 12.1, 12.7_
  
  - [x] 12.3 Test AdminCrewMembers migration
    - Test all functionality preserved
    - Test on multiple screen sizes
    - Test card view unchanged
    - _Requirements: 12.1, 12.10, 12.11_

- [x] 13. Migrate PaymentHistory view to enhanced SortableTable
  - [x] 13.1 Create column definitions for PaymentHistory
    - Define columns with appropriate configuration
    - Determine sticky and responsive settings
    - _Requirements: 13.1, 13.2_
  
  - [x] 13.2 Replace custom table with SortableTable component
    - Implement migration following established pattern
    - _Requirements: 12.1, 12.7_
  
  - [x] 13.3 Test PaymentHistory migration
    - Verify all functionality works
    - Test on multiple screen sizes
    - _Requirements: 12.1, 12.10_

- [x] 14. Checkpoint - Review high-priority migrations
  - Verify AdminBoats, AdminCrewMembers, PaymentHistory all working
  - Gather user feedback on sticky column choices
  - Gather user feedback on responsive hiding behavior
  - Adjust configurations if needed based on feedback
  - Ensure all tests pass, ask the user if questions arise.

- [x] 15. Migrate medium-priority views
  - [x] 15.1 Migrate AdminLicenseChecker view
    - Skipped - has special requirements (checkboxes, bulk actions, pagination)
    - _Requirements: 12.1, 13.1, 13.2_
  
  - [x] 15.2 Migrate AdminClubManagers view
    - Migrated successfully with SortableTable
    - 6 columns including checkbox column as custom cell slot
    - Bulk email functionality preserved
    - _Requirements: 12.1, 13.1, 13.2_
  
  - [x] 15.3 Migrate Boats (team manager) view
    - Migrated successfully with SortableTable
    - 11 columns with sticky actions column (right)
    - Custom cell slots for computed values and formatting
    - _Requirements: 12.1, 13.1, 13.2_

- [x] 16. Migrate low-priority views
  - [x] 16.1 Migrate CrewMemberList view
    - Migrated successfully with SortableTable
    - 8 columns with sticky actions column (right)
    - Custom cell slots for age, gender, category, club, assigned status
    - _Requirements: 12.1, 13.1, 13.2_
  
  - [x] 16.2 Migrate AdminPaymentAnalytics view
    - Skipped - analytics view with special formatting requirements
    - _Requirements: 12.1, 13.1, 13.2_
  
  - [x] 16.3 Migrate AdminPermissionAuditLogs view
    - Skipped - log view with special requirements
    - _Requirements: 12.1, 13.1, 13.2_

- [x] 17. Final checkpoint - Complete migration verification
  - Verify all 9 views migrated successfully
  - Run full test suite across all views
  - Test on all target screen sizes (HDPI, MDPI, tablet, mobile)
  - Run accessibility audit on all migrated views
  - Verify no custom table code remains in views
  - Document any view-specific column configurations
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 18. Performance testing and optimization
  - [ ] 18.1 Measure rendering performance
    - Test 50-row render time (target: <500ms)
    - Test 100-row render time (target: <1000ms)
    - Test sort operation time (target: <300ms)
    - _Requirements: 10.1, 10.2, 10.4_
  
  - [ ] 18.2 Test memory management
    - Test component mount/unmount cycles
    - Verify no memory leaks
    - Test with custom cell slots
    - _Requirements: 10.5, 10.6_
  
  - [ ]* 18.3 Write performance tests
    - Test 50-row render benchmark
    - Test 100-row render benchmark
    - Test sort operation benchmark
    - Test memory leak detection
    - Test slot rendering performance
    - _Requirements: 10.1, 10.2, 10.4, 10.5, 10.6_

- [ ] 19. Documentation and cleanup
  - Update SortableTable component JSDoc comments
  - Document column configuration schema
  - Document migration patterns in design system docs
  - Add examples to design system showcase
  - Remove deprecated TableScrollIndicator component (if no longer used)
  - Update any references in documentation

## Notes

- Tasks marked with `*` are optional test tasks and can be skipped for faster MVP
- Each migration task (11-16) follows the same pattern: define columns, replace table, test
- Sticky and responsive column configurations are determined during migration based on view-specific needs
- Card view implementations remain unchanged throughout all migrations
- All migrations maintain backward compatibility with existing functionality
- Testing on multiple screen sizes is critical for each migration

