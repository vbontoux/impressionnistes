# Implementation Plan: UI Consistency

## Overview

This implementation plan breaks down the UI consistency feature into discrete, manageable tasks. The approach is incremental, building from foundation (design tokens and base components) to composite components, then refactoring existing pages, and finally creating documentation and steering rules.

## Tasks

- [x] 1. Set up design token system
  - Create `frontend/src/assets/design-tokens.css` with CSS variables for colors, spacing, typography, and breakpoints
  - Import design tokens in main App.vue
  - Test that CSS variables are accessible throughout the application
  - Create Design System Showcase page at `/design-system` route
  - _Requirements: 5.1, 6.6, 7.1_
  - _Note: Showcase page created as permanent living style guide_

- [x] 2. Create BaseButton component
  - [x] 2.1 Implement BaseButton.vue with variant, size, disabled, loading, and fullWidth props
    - Support variants: primary, secondary, danger, warning
    - Support sizes: small, medium, large
    - Use design tokens for colors and spacing
    - Include hover and active states
    - Handle disabled and loading states
    - _Requirements: 1.1, 1.2, 1.3, 1.5, 1.6_

  - [ ]* 2.2 Write unit tests for BaseButton
    - Test all variant styles
    - Test all size variations
    - Test disabled state prevents clicks
    - Test loading state shows spinner
    - Test click event emission
    - _Requirements: 1.1, 1.2, 1.3, 1.5, 1.6_

  - [x] 2.3 Update Design System Showcase
    - Add BaseButton examples showing all variants
    - Add BaseButton examples showing all sizes
    - Add code examples for BaseButton usage
    - _Requirements: 13.1, 13.3_

- [x] 3. Create StatusBadge component
  - [x] 3.1 Implement StatusBadge.vue with status and size props
    - Auto-apply colors based on status (incomplete, complete, paid, forfait)
    - Use design tokens for colors
    - Support small and medium sizes
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ]* 3.2 Write unit tests for StatusBadge
    - Test color mapping for each status
    - Test unknown status handling
    - Test size variations
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 3.3 Update Design System Showcase
    - Add StatusBadge examples for all statuses
    - Add code examples for StatusBadge usage
    - _Requirements: 13.1, 13.3_

- [x] 4. Create LoadingSpinner component
  - [x] 4.1 Implement LoadingSpinner.vue with size and message props
    - 40px diameter spinner with consistent styling
    - Use design tokens for colors
    - Support optional message text
    - _Requirements: 10.1, 10.3_

  - [ ]* 4.2 Write unit tests for LoadingSpinner
    - Test spinner renders correctly
    - Test message display
    - Test size variations
    - _Requirements: 10.1, 10.3_

- [x] 5. Create EmptyState component
  - [x] 5.1 Implement EmptyState.vue with message and actionLabel props
    - Centered layout with consistent styling
    - Support icon and action slots
    - Use design tokens for spacing and colors
    - _Requirements: 10.2, 10.4_

  - [ ]* 5.2 Write unit tests for EmptyState
    - Test message display
    - Test action button slot
    - Test icon slot
    - _Requirements: 10.2, 10.4_

- [x] 6. Create BaseModal component
  - [x] 6.1 Implement BaseModal.vue with show, title, size, and closeOnOverlay props
    - Consistent overlay styling (rgba(0, 0, 0, 0.5))
    - Support header, default, and footer slots
    - Responsive behavior (bottom sheet on mobile, centered on desktop)
    - Use design tokens for spacing and colors
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [ ]* 6.2 Write unit tests for BaseModal
    - Test show/hide functionality
    - Test overlay click behavior
    - Test slot rendering
    - Test responsive behavior
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 7. Checkpoint - Ensure base components work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Create DataCard component
  - [x] 8.1 Implement DataCard.vue with title, status, and statusBadge props
    - Support header, default, and actions slots
    - Status-based border colors
    - Responsive padding (1rem mobile, 1.5rem desktop)
    - Use design tokens throughout
    - _Requirements: 2.4, 7.5, 8.2_

  - [ ]* 8.2 Write unit tests for DataCard
    - Test slot rendering
    - Test status-based styling
    - Test responsive behavior
    - _Requirements: 2.4, 7.5, 8.2_

- [x] 9. Create SortableTable component and composable
  - [x] 9.1 Create useTableSort.js composable
    - Implement sorting logic for different data types
    - Handle alphanumeric sorting (e.g., boat numbers)
    - Support ascending and descending sort
    - _Requirements: 3.2, 3.3_

  - [x] 9.2 Implement SortableTable.vue with columns and data props
    - Clickable column headers with sort indicators (▲ ▼)
    - Use useTableSort composable for sorting logic
    - Consistent table styling with design tokens
    - Responsive with horizontal scroll on mobile
    - Support cell slots for custom content
    - _Requirements: 3.1, 3.3, 3.4, 3.5_

  - [ ]* 9.3 Write unit tests for SortableTable and useTableSort
    - Test sorting logic for different data types
    - Test sort indicator updates
    - Test sort event emission
    - Test responsive behavior
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 10. Create FormGroup component
  - [x] 10.1 Implement FormGroup.vue with label, required, error, and helpText props
    - Consistent label styling
    - Error message display
    - Help text display
    - Use design tokens for spacing and colors
    - _Requirements: 7.3, 12.1, 12.2_

  - [ ]* 10.2 Write unit tests for FormGroup
    - Test label rendering
    - Test required indicator
    - Test error message display
    - Test help text display
    - _Requirements: 7.3, 12.1, 12.2_

- [x] 11. Create MessageAlert component
  - [x] 11.1 Implement MessageAlert.vue with type, message, dismissible, and autoDismiss props
    - Support types: error, success, warning, info
    - Auto-dismiss functionality with timer
    - Dismissible close button
    - Use design tokens for colors
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [ ]* 11.2 Write unit tests for MessageAlert
    - Test color styling for each type
    - Test auto-dismiss functionality
    - Test dismissible close button
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [x] 12. Checkpoint - Ensure composite components work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Enhance ListHeader component
  - Update ListHeader.vue to use BaseButton component
  - Replace inline styles with design tokens
  - Maintain existing functionality
  - _Requirements: 1.1, 6.1, 6.5_

- [x] 14. Enhance ListFilters component
  - Update ListFilters.vue to use design tokens
  - Standardize filter control styling
  - Maintain existing functionality
  - _Requirements: 12.1, 12.2, 12.5_

- [x] 15. Refactor Boats.vue (Team Manager)
  - [x] 15.1 Replace button elements with BaseButton components
    - Update view/delete buttons in card view
    - Update view/delete buttons in table view
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 15.2 Replace status badge markup with StatusBadge component
    - Update status badges in card view
    - Update status badges in table view
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 15.3 Add table sorting functionality
    - Implement sorting for boat number, event type, club columns
    - Add sort indicators to table headers
    - Use useTableSort composable
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 15.4 Replace loading/empty states with new components
    - Use LoadingSpinner component
    - Use EmptyState component
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [x] 15.5 Update styling to use design tokens
    - Replace hardcoded colors with CSS variables
    - Replace hardcoded spacing with CSS variables
    - Replace hardcoded typography with CSS variables
    - _Requirements: 5.1, 5.2, 6.6, 7.1_

- [x] 16. Refactor AdminBoats.vue
  - [x] 16.1 Replace button elements with BaseButton components
    - Update edit/forfait/delete buttons in card view
    - Update edit/forfait/delete buttons in table view
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 16.2 Replace status badge markup with StatusBadge component
    - Ensure consistent capitalization (sentence case)
    - Update status badges in card view
    - Update status badges in table view
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 16.3 Ensure crew # color consistency
    - Apply blue color (#007bff) to crew member identifiers
    - Use design tokens for color
    - _Requirements: 4.4, 5.1_

  - [x] 16.4 Replace modal with BaseModal component
    - Update create/edit modal
    - Use modal slots for header, body, footer
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [x] 16.5 Update styling to use design tokens
    - Replace hardcoded colors with CSS variables
    - Replace hardcoded spacing with CSS variables
    - Replace hardcoded typography with CSS variables
    - _Requirements: 5.1, 5.2, 6.6, 7.1_

- [x] 17. Refactor CrewMemberList.vue
  - [x] 17.1 Replace button elements with BaseButton components
    - Update action buttons in card view
    - Update action buttons in table view
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 17.2 Add table sorting functionality (if table view exists)
    - Implement sorting for relevant columns
    - Add sort indicators
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 17.3 Update card styling to use DataCard component
    - Refactor crew member cards to use DataCard
    - Use slots for content and actions
    - _Requirements: 6.4, 7.5, 8.2_

  - [x] 17.4 Update styling to use design tokens
    - Replace hardcoded colors with CSS variables
    - Replace hardcoded spacing with CSS variables
    - _Requirements: 5.1, 6.6, 7.1_

- [x] 18. Refactor BoatDetail.vue
  - [x] 18.1 Replace button elements with BaseButton components
    - Update save/cancel buttons
    - Ensure consistent button sizing (size="small" for all buttons)
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 18.2 Update form fields to use FormGroup component
    - Wrap form inputs with FormGroup
    - Display validation errors consistently
    - _Requirements: 7.3, 12.1_

  - [x] 18.3 Update styling to use design tokens
    - Replace hardcoded colors with CSS variables
    - Replace hardcoded spacing with CSS variables
    - _Requirements: 5.1, 6.6, 7.1_

- [-] 19. Refactor remaining admin pages
  - [x] 19.1 Update AdminCrewMembers.vue
    - Replace buttons with BaseButton (size="small" for cards/tables)
    - Add table sorting
    - Use design tokens
    - Fix badge styling to match CrewMemberList.vue (no text-transform on status badges)
    - _Requirements: 1.1, 3.1, 5.1_
    - _Status: Complete - All buttons replaced, table sorting added, design tokens applied, badge styling fixed_

  - [ ] 19.2 Update AdminClubManagers.vue
    - Replace buttons with BaseButton (size="small" for cards/tables)
    - Ensure table consistency
    - Use design tokens
    - _Requirements: 1.1, 3.4, 5.1_

  - [ ] 19.3 Update AdminDashboard.vue
    - Replace buttons with BaseButton (size="small" for cards)
    - Update card styling
    - Use design tokens
    - _Requirements: 1.1, 6.4, 5.1_

  - [ ] 19.4 Update AdminEventConfig.vue
    - Replace buttons with BaseButton (size="small")
    - Use FormGroup for form fields
    - Use design tokens
    - _Requirements: 1.1, 7.3, 5.1_

  - [ ] 19.5 Update AdminPricingConfig.vue
    - Replace buttons with BaseButton (size="small")
    - Use FormGroup for form fields
    - Use design tokens
    - _Requirements: 1.1, 7.3, 5.1_

- [ ] 20. Refactor form components
  - [ ] 20.1 Update BoatRegistrationForm.vue
    - Replace buttons with BaseButton (size="small")
    - Use FormGroup for form fields
    - Use design tokens for spacing
    - _Requirements: 1.1, 7.3, 5.1_

  - [ ] 20.2 Update CrewMemberForm.vue
    - Replace buttons with BaseButton (size="small")
    - Use FormGroup for form fields
    - Use design tokens for spacing
    - _Requirements: 1.1, 7.3, 5.1_

- [ ] 21. Checkpoint - Ensure all pages are refactored correctly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 22. Create design system documentation
  - [ ] 22.1 Write docs/design-system.md
    - Introduction and purpose
    - Design principles
    - Design tokens reference (colors, typography, spacing, breakpoints)
    - Component library with usage examples
    - Patterns (buttons, forms, tables, cards, modals, loading, empty states, errors)
    - Layout guidelines
    - Best practices
    - Migration guide with before/after examples
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

  - [ ] 22.2 Update Design System Showcase page
    - Add new components to showcase as they are created
    - Update code examples to reflect actual implementations
    - Ensure all design tokens are demonstrated
    - Keep usage guidelines current
    - _Requirements: 13.1, 13.2, 13.3_

  - [ ] 22.3 Add link to design system in docs/README.md
    - Update main documentation index
    - Add section for design system
    - Link to showcase page and documentation
    - _Requirements: 13.6_

- [ ] 23. Create UI consistency steering file
  - [ ] 23.1 Write .kiro/steering/ui-consistency.md
    - Purpose and overview
    - Quick reference for common patterns
    - Component usage rules (buttons, status badges, tables, cards, modals)
    - Design token usage guidelines
    - Examples of correct and incorrect implementations
    - UI consistency checklist
    - Links to design system documentation
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.6_

  - [ ] 23.2 Configure steering file for "always included" mode
    - Set front-matter to include automatically
    - Test that steering file loads during frontend work
    - _Requirements: 14.5_

- [ ] 24. Create utility CSS classes
  - Create frontend/src/styles/utilities.css with common utility classes
  - Include spacing utilities, text utilities, display utilities
  - Import in main App.vue
  - _Requirements: 6.6, 7.1_

- [ ] 25. Update global styles
  - Update frontend/src/styles/global.css to use design tokens
  - Remove duplicate styling
  - Ensure consistent base styles
  - _Requirements: 5.1, 6.6_

- [ ] 26. Final validation and testing
  - [ ]* 26.1 Run visual regression tests
    - Capture screenshots of all pages
    - Compare against baseline
    - Verify no unintended visual changes
    - _Requirements: All_

  - [ ]* 26.2 Perform manual QA on all pages
    - Test all pages at mobile, tablet, and desktop breakpoints
    - Verify button styling consistency
    - Verify status badge consistency
    - Verify table sorting works
    - Verify spacing consistency
    - Verify typography consistency
    - Verify responsive behavior
    - _Requirements: All_

  - [ ]* 26.3 Validate against requirements
    - Review each requirement
    - Verify implementation meets acceptance criteria
    - Document any deviations
    - _Requirements: All_

- [ ] 27. Final checkpoint - Complete implementation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The implementation follows an incremental approach: foundation → composite → refactoring → documentation → testing
- Pages are refactored one at a time to minimize risk
- Design tokens and base components are created first to establish the foundation
- Documentation and steering files are created after implementation to reflect actual patterns

## Button Sizing Standard (IMPORTANT)

**For all remaining refactoring tasks:**
- Card view buttons MUST use `size="small"` (matching Boats.vue and CrewMemberList.vue)
- Table view buttons MUST use `size="small"` (matching existing implementations)
- This ensures consistent button sizing across all pages
- Remove any `text-transform: uppercase` from badge styles to maintain sentence case

## Color Consistency Standard (IMPORTANT)

**For all remaining refactoring tasks:**
- ONLY use colors defined in `design-tokens.css`
- DO NOT invent new colors or use hardcoded hex values outside the design system
- Use semantic colors appropriately:
  - **Success/Complete states**: `--color-success` (green #28a745)
  - **Warning/Incomplete states**: `--color-warning` (yellow #ffc107)
  - **Danger/Error states**: `--color-danger` (red #dc3545)
  - **Primary actions/info**: `--color-primary` (blue #007bff)
  - **Secondary actions**: `--color-secondary` (grey #6c757d)
- Replace ALL hardcoded colors with design tokens
- If a color was used before that's not in the design system, change it to the appropriate design token

## CSS Reusability Standard (CRITICAL)

**NEVER duplicate CSS classes across components:**
- Before creating a new CSS class, check if it already exists in:
  1. `design-tokens.css` - Design tokens and utility classes
  2. Other components - Shared styling patterns
  3. Global styles - Application-wide styles
- If the same styling is needed in multiple places:
  1. **First choice**: Add utility class to `design-tokens.css` (for widely reused patterns)
  2. **Second choice**: Create a shared component (for complex reusable UI patterns)
  3. **Last resort**: Component-specific scoped styles (only for truly unique styling)
- Common utility classes that should be in `design-tokens.css`:
  - Text colors and styles (`.boat-number-text`, `.no-race-text`)
  - Status indicators
  - Layout helpers
  - Spacing utilities
- **NEVER** copy-paste CSS between components
- **ALWAYS** reference design tokens using CSS variables (`var(--color-primary)`)
- If you find yourself writing the same CSS twice, STOP and centralize it first

**Example of WRONG approach:**
```css
/* In Boats.vue */
.boat-number-text {
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}

/* In AdminBoats.vue - DUPLICATE! */
.boat-number-text {
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}
```

**Example of CORRECT approach:**
```css
/* In design-tokens.css - DEFINED ONCE */
.boat-number-text {
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}

/* Both Boats.vue and AdminBoats.vue just USE the class */
<span class="boat-number-text">{{ boat.boat_number }}</span>
```
