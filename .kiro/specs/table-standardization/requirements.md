# Requirements Document: Table Standardization

## Introduction

This document specifies the requirements for standardizing table components across the Impressionnistes Registration System. The goal is to create a consistent, accessible, and performant table experience across all admin and user views by enhancing the existing SortableTable component and migrating all custom table implementations to use it.

## Glossary

- **SortableTable**: The reusable Vue component for displaying tabular data with sorting capabilities
- **HDPI Screen**: High-density pixel interface screen (e.g., 1440x900 resolution)
- **MDPI Screen**: Medium-density pixel interface screen (e.g., 1024x768 resolution)
- **Sticky Column**: A table column that remains visible while horizontally scrolling
- **Responsive Column**: A table column that can be hidden on smaller screens to improve usability
- **Design Token**: CSS custom property defined in design-tokens.css for consistent styling
- **Horizontal Scroll**: The ability to scroll table content left and right when it exceeds container width
- **Compact Mode**: A display mode with reduced padding for viewing more data in limited space
- **Custom Cell Slot**: A Vue slot that allows custom rendering of table cell content

## Requirements

### Requirement 1: Enhanced Horizontal Scrolling

**User Story:** As a user viewing tables on HDPI or MDPI screens, I want to see a visible scrollbar and be able to scroll horizontally, so that I can access all table columns without content being cut off.

#### Acceptance Criteria

1. WHEN a table's content width exceeds its container width, THE SortableTable SHALL display a horizontal scrollbar
2. WHEN viewing on HDPI screens (1440x900), THE scrollbar SHALL be visible and styled consistently
3. WHEN viewing on MDPI screens (1024x768), THE scrollbar SHALL be visible and styled consistently
4. THE scrollbar SHALL use design tokens for consistent styling across the application
5. WHEN scrolling horizontally, THE table content SHALL move smoothly without lag
6. THE scrollbar SHALL be at least 8px in height for easy interaction
7. WHEN the table fits within its container, THE scrollbar SHALL not be displayed

### Requirement 2: Sticky Column Support (Optional Feature)

**User Story:** As an admin managing boats with many columns, I want critical columns like actions to remain visible while scrolling, so that I can always access important functionality.

**Note:** This is an OPTIONAL feature that will be configured per-view during migration. The developer will determine which columns (if any) should be sticky based on the specific view's needs and user workflow.

#### Acceptance Criteria

1. WHEN a column is marked as sticky-left, THE SortableTable SHALL keep it fixed on the left side during horizontal scroll
2. WHEN a column is marked as sticky-right, THE SortableTable SHALL keep it fixed on the right side during horizontal scroll
3. WHEN scrolling horizontally, THE sticky columns SHALL remain in their fixed positions
4. THE sticky columns SHALL have a visual indicator (shadow or border) to show they are fixed
5. WHEN multiple columns are sticky, THE SortableTable SHALL maintain their relative order
6. THE sticky column feature SHALL be optional and configurable per column
7. WHEN a sticky column contains interactive elements, THE elements SHALL remain fully functional
8. WHEN no columns are marked as sticky, THE table SHALL behave as a standard scrollable table
9. THE sticky column configuration SHALL be determined during migration based on view-specific needs

### Requirement 3: Responsive Column Hiding (Optional Feature)

**User Story:** As a user on a tablet or smaller desktop screen, I want less critical columns to be hidden automatically, so that I can focus on the most important information without horizontal scrolling.

**Note:** This is an OPTIONAL feature that will be configured per-view during migration. The developer will determine which columns (if any) should be hidden at different breakpoints based on the specific view's needs.

#### Acceptance Criteria

1. WHEN a column is marked with a responsive priority, THE SortableTable SHALL hide it based on screen size
2. WHEN the screen width is below 1024px, THE columns marked as low-priority SHALL be hidden
3. WHEN the screen width is below 768px, THE columns marked as medium-priority SHALL be hidden
4. THE column visibility SHALL update automatically when the screen is resized
5. THE hidden columns SHALL not affect the table's sorting functionality
6. WHEN all responsive columns are hidden, THE table SHALL still display at least the required columns
7. THE responsive behavior SHALL be configurable per column through column definitions
8. WHEN no columns are marked as responsive, ALL columns SHALL remain visible at all desktop/tablet sizes
9. THE responsive column hiding SHALL NOT apply on mobile (<768px) where card view is used instead

### Requirement 4: Column Width Management

**User Story:** As a developer implementing tables, I want to control column widths and minimum widths, so that tables display data optimally across different screen sizes.

#### Acceptance Criteria

1. WHEN a column definition includes a width property, THE SortableTable SHALL apply that width
2. WHEN a column definition includes a minWidth property, THE SortableTable SHALL enforce that minimum width
3. WHEN no width is specified, THE column SHALL size automatically based on content
4. THE column widths SHALL be specified using design tokens or standard CSS units
5. WHEN the total column width exceeds the container, THE horizontal scroll SHALL activate
6. THE column width properties SHALL accept both fixed (px) and flexible (%, fr) units
7. WHEN using percentage widths, THE total SHALL not exceed 100% of the container width

### Requirement 5: Compact Display Mode

**User Story:** As an admin viewing large datasets, I want a compact table mode with reduced padding, so that I can see more rows on screen at once.

#### Acceptance Criteria

1. WHEN compact mode is enabled, THE SortableTable SHALL reduce cell padding by 50%
2. WHEN compact mode is enabled, THE font size SHALL remain unchanged for readability
3. THE compact mode SHALL be toggleable through a component prop
4. WHEN compact mode is toggled, THE table SHALL update immediately without page reload
5. THE compact mode preference SHALL be optional to persist in localStorage
6. WHEN in compact mode, THE minimum touch target size SHALL remain 44px for interactive elements
7. THE compact mode SHALL apply to both header and body cells

### Requirement 6: Design Token Integration

**User Story:** As a developer maintaining the design system, I want all table styling to use design tokens, so that visual changes can be made consistently across all tables.

#### Acceptance Criteria

1. THE SortableTable SHALL use design tokens for all color values
2. THE SortableTable SHALL use design tokens for all spacing values
3. THE SortableTable SHALL use design tokens for all typography values
4. THE SortableTable SHALL use design tokens for border radius and shadows
5. WHEN a design token value changes, THE table styling SHALL update automatically
6. THE SortableTable SHALL not contain any hardcoded color hex values
7. THE SortableTable SHALL not contain any hardcoded pixel spacing values

### Requirement 7: Custom Cell Rendering

**User Story:** As a developer implementing complex table views, I want to render custom content in cells using slots, so that I can display badges, buttons, and formatted data.

#### Acceptance Criteria

1. WHEN a slot is provided for a column, THE SortableTable SHALL render the slot content instead of the raw value
2. THE slot SHALL receive the row data, cell value, and column definition as props
3. WHEN no slot is provided, THE SortableTable SHALL display the raw cell value
4. THE custom cell content SHALL support Vue components like BaseButton and StatusBadge
5. WHEN custom content includes interactive elements, THE elements SHALL be fully functional
6. THE slot content SHALL have access to the parent component's scope
7. WHEN multiple cells use the same slot pattern, THE slot SHALL be reusable across columns

### Requirement 8: Sorting Functionality Preservation

**User Story:** As a user sorting table data, I want the enhanced table to maintain all existing sorting capabilities, so that I can organize data as I currently do.

#### Acceptance Criteria

1. WHEN a sortable column header is clicked, THE SortableTable SHALL sort the data by that column
2. WHEN clicking a sorted column header again, THE sort direction SHALL toggle between ascending and descending
3. THE sort indicator SHALL display the current sort direction (▲ or ▼)
4. WHEN a column is marked as non-sortable, THE header SHALL not be clickable
5. THE sorting SHALL work with all data types (strings, numbers, dates)
6. WHEN sorting by a column with null values, THE null values SHALL appear at the end
7. THE sorting functionality SHALL emit events for parent components to track sort state

### Requirement 9: Accessibility Compliance

**User Story:** As a user relying on assistive technology, I want tables to be fully accessible, so that I can navigate and understand the data using screen readers and keyboard.

#### Acceptance Criteria

1. THE SortableTable SHALL use semantic HTML table elements (table, thead, tbody, th, td)
2. WHEN navigating with keyboard, THE sortable headers SHALL be focusable and activatable with Enter/Space
3. THE table SHALL include appropriate ARIA labels for screen readers
4. WHEN a column is sorted, THE sort state SHALL be announced to screen readers
5. THE table SHALL support keyboard navigation between cells using arrow keys
6. WHEN interactive elements are in cells, THE tab order SHALL be logical and sequential
7. THE table SHALL maintain a minimum contrast ratio of 4.5:1 for all text

### Requirement 10: Performance Optimization

**User Story:** As a user viewing tables with 50+ rows, I want the table to render quickly and scroll smoothly, so that I can work efficiently without lag.

#### Acceptance Criteria

1. WHEN rendering 50 rows, THE SortableTable SHALL display within 500ms
2. WHEN rendering 100 rows, THE SortableTable SHALL display within 1000ms
3. WHEN scrolling horizontally, THE frame rate SHALL remain above 30fps
4. WHEN sorting data, THE table SHALL update within 300ms
5. THE SortableTable SHALL not cause memory leaks when mounted and unmounted repeatedly
6. WHEN using custom cell slots, THE rendering performance SHALL not degrade significantly
7. THE SortableTable SHALL use efficient Vue reactivity patterns to minimize re-renders

### Requirement 11: Mobile Card View Preservation

**User Story:** As a user on mobile devices, I want tables to switch to card view automatically, so that I can view data comfortably on small screens without any degradation in functionality.

#### Acceptance Criteria

1. WHEN the screen width is below 768px, THE table view SHALL be hidden
2. WHEN the screen width is below 768px, THE card view SHALL be displayed
3. THE card view SHALL display the same data as the table view
4. THE card view SHALL use the same data source and sorting as the table view
5. WHEN switching between table and card views, THE sort state SHALL be preserved
6. THE card view SHALL be implemented separately from SortableTable (not part of this component)
7. THE parent component SHALL control the view mode switching logic
8. THE SortableTable migration SHALL NOT modify or impair existing card view implementations
9. THE card view SHALL maintain all current functionality including actions, badges, and formatting
10. WHEN migrating a view, THE card view code SHALL remain unchanged unless explicitly needed
11. THE responsive breakpoints for card/table switching SHALL remain at 768px as currently implemented

### Requirement 12: Migration Path for Existing Views

**User Story:** As a developer migrating existing table views, I want clear migration patterns and backward compatibility, so that I can update views incrementally without breaking functionality.

#### Acceptance Criteria

1. THE enhanced SortableTable SHALL maintain backward compatibility with existing implementations
2. WHEN migrating a view, THE existing functionality SHALL be preserved
3. THE migration SHALL not require changes to data fetching or business logic
4. THE SortableTable SHALL provide clear prop documentation for all features
5. WHEN a view uses custom table styling, THE migration SHALL preserve the visual appearance
6. THE SortableTable SHALL support gradual feature adoption (sticky columns, responsive hiding, etc.)
7. WHEN migration is complete, THE custom table code SHALL be removed from the view component
8. THE migration process SHALL include a review step to determine which columns should be sticky
9. THE migration process SHALL include a review step to determine which columns should be responsive
10. THE developer SHALL test the migrated view on HDPI (1440x900), MDPI (1024x768), tablet (768px), and mobile (<768px) screens
11. THE card view implementation SHALL remain unchanged unless explicitly needed for the migration

### Requirement 13: Column Configuration During Migration

**User Story:** As a developer migrating a view, I want to make informed decisions about column configuration, so that the table provides the best user experience for that specific view.

#### Acceptance Criteria

1. WHEN migrating a view, THE developer SHALL review all columns to determine sticky column needs
2. WHEN migrating a view, THE developer SHALL review all columns to determine responsive hiding priorities
3. THE developer SHALL consider user workflows when deciding which columns should be sticky
4. THE developer SHALL consider screen real estate when deciding which columns can be hidden responsively
5. WHEN a view has an actions column, THE developer SHALL evaluate if it should be sticky-right
6. WHEN a view has an identifier column (boat number, name), THE developer SHALL evaluate if it should be sticky-left
7. THE column configuration decisions SHALL be documented in the migration commit message
8. WHEN uncertain about column configuration, THE developer SHALL start with no sticky columns and no responsive hiding
9. THE column configuration SHALL be tested on multiple screen sizes before finalizing

## Priority Views for Migration

The following views contain custom table implementations and should be migrated in priority order:

### High Priority
1. **AdminBoats** - 11 columns, complex actions, boat request status
2. **AdminCrewMembers** - 8+ columns, team manager filtering
3. **PaymentHistory** - Payment records with date filtering

### Medium Priority
4. **AdminLicenseChecker** - License validation table
5. **AdminClubManagers** - Manager list with permissions
6. **Boats** - Team manager boat view

### Low Priority
7. **CrewMemberList** - Team manager crew view
8. **AdminPaymentAnalytics** - Analytics table (already simple)
9. **AdminPermissionAuditLogs** - Audit log table

## Technical Constraints

1. **Design System Compliance**: All styling MUST use existing design tokens from design-tokens.css
2. **Component Compatibility**: MUST work with existing BaseButton, StatusBadge, and other base components
3. **Browser Support**: MUST support modern browsers (Chrome, Firefox, Safari, Edge) from the last 2 years
4. **Vue 3 Composition API**: MUST use Vue 3 Composition API patterns
5. **Accessibility Standards**: MUST comply with WCAG 2.1 Level AA standards
6. **Performance Budget**: Table rendering MUST not block the main thread for more than 100ms
7. **Mobile First**: MUST work on mobile devices (iOS Safari, Chrome Android) with touch interactions
8. **No External Dependencies**: MUST NOT introduce new npm dependencies for table functionality

## Non-Functional Requirements

### Usability
- Tables SHALL be intuitive to use without training
- Scrollbars SHALL be discoverable and easy to interact with
- Sorting SHALL provide immediate visual feedback

### Maintainability
- Code SHALL follow existing Vue component patterns in the codebase
- Component props SHALL have clear TypeScript-style JSDoc comments
- Complex logic SHALL be extracted to composables

### Testability
- Component SHALL be testable with Vue Test Utils
- Sorting logic SHALL be unit testable
- Responsive behavior SHALL be testable with viewport mocking

### Compatibility
- SHALL work with existing i18n translations
- SHALL work with existing API response formats
- SHALL work with existing state management patterns
