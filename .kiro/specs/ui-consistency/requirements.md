# Requirements Document: UI Consistency

## Introduction

This specification addresses the need for consistent user interface elements across the Impressionnistes Registration System. Currently, the application exhibits inconsistencies in button styling, colors, table functionality, typography, and component reusability. This document defines requirements to establish a unified design system that ensures a cohesive user experience across all pages and user roles (team managers, administrators, and public users).

The implementation will produce two key deliverables:
1. **Design System Documentation** (`docs/design-system.md`) - Comprehensive reference for all UI patterns and standards
2. **UI Consistency Steering File** (`.kiro/steering/ui-consistency.md`) - Automated guardrails to enforce design rules during development

## Glossary

- **System**: The Impressionnistes Registration System web application
- **Design_System**: A collection of reusable components, styles, and guidelines that ensure visual and functional consistency
- **Action_Button**: Interactive elements (buttons) that trigger user actions (create, edit, delete, view, cancel)
- **Status_Badge**: Visual indicator displaying the state of an entity (incomplete, complete, paid, forfait)
- **Table_View**: Tabular display of data with sortable columns
- **Card_View**: Grid-based display of data in card format
- **Color_Palette**: Standardized set of colors used throughout the application for semantic purposes
- **Team_Manager**: User role managing boat registrations and crew members
- **Administrator**: User role with elevated privileges for system management
- **Component**: Reusable Vue.js UI element
- **Steering_File**: Kiro AI guardrail file that provides automated guidance during development

## Requirements

### Requirement 1: Standardized Action Button Styling

**User Story:** As a user, I want all action buttons to have consistent appearance and behavior, so that I can easily identify and interact with them across different pages.

#### Acceptance Criteria

1. THE System SHALL define a standard color scheme for action buttons based on semantic meaning:
   - Primary actions (create, add, save, confirm): Blue (#007bff)
   - Secondary actions (view, edit, cancel): Grey (#6c757d)
   - Destructive actions (delete, remove): Red (#dc3545)
   - Warning actions (forfait, alert): Orange/Yellow (#ffc107)

2. WHEN displaying action buttons in card view, THE System SHALL render them with consistent sizing:
   - Minimum height: 44px (touch-friendly)
   - Padding: 0.75rem 1rem
   - Border-radius: 4px
   - Font-size: 0.875rem
   - Font-weight: 500

3. WHEN displaying action buttons in table view, THE System SHALL render them with consistent sizing:
   - Minimum height: 36px
   - Padding: 0.5rem 0.75rem
   - Border-radius: 4px
   - Font-size: 0.8125rem
   - Full width within actions cell

4. WHEN multiple action buttons are displayed together, THE System SHALL arrange them consistently:
   - Card view: Stacked vertically on mobile, horizontal on desktop
   - Table view: Stacked vertically in actions column
   - Consistent gap spacing: 0.5rem between buttons

5. WHEN a user hovers over an enabled button, THE System SHALL provide visual feedback:
   - Darken background color by 10-15%
   - Smooth transition (0.2s)
   - Cursor changes to pointer

6. WHEN a button is disabled, THE System SHALL display it with:
   - Background color: #ccc
   - Opacity: 0.6
   - Cursor: not-allowed
   - No hover effects

### Requirement 2: Consistent Status Badge Styling

**User Story:** As a user, I want status indicators to look the same across all pages, so that I can quickly understand the state of boats and registrations.

#### Acceptance Criteria

1. THE System SHALL define standard status badge styles:
   - Padding: 0.25rem 0.75rem
   - Border-radius: 12px
   - Font-size: 0.75rem
   - Font-weight: 500
   - White-space: nowrap

2. THE System SHALL use consistent colors for status badges:
   - Incomplete: Yellow background (#ffc107), black text
   - Complete: Green background (#28a745), white text
   - Paid/Free: Blue background (#007bff), white text
   - Forfait: Red background (#dc3545), white text

3. WHEN displaying status text, THE System SHALL use consistent capitalization:
   - Status labels: Sentence case (e.g., "Incomplete", "Complete", "Paid")
   - No all-caps status labels

4. WHEN displaying status in table rows, THE System SHALL use consistent border indicators:
   - Left border width: 4px
   - Border color matches status badge color
   - Applied to entire row

### Requirement 3: Unified Table Functionality

**User Story:** As a user, I want all tables to have consistent sorting capabilities and visual indicators, so that I can organize data in the same way across different pages.

#### Acceptance Criteria

1. WHEN a table column is sortable, THE System SHALL display a sort indicator:
   - Clickable column header
   - Visual indicator (▲ for ascending, ▼ for descending)
   - Cursor changes to pointer on hover

2. THE System SHALL implement sorting for all relevant columns:
   - Boat number (alphanumeric sorting)
   - Event type (alphabetical)
   - Team manager name (alphabetical)
   - Club name (alphabetical)
   - Status (by priority order)

3. WHEN a user clicks a sortable column header, THE System SHALL:
   - Toggle sort direction (ascending ↔ descending)
   - Update the sort indicator
   - Re-render the table with sorted data

4. THE System SHALL maintain consistent table styling:
   - Header background: #f8f9fa
   - Header font-weight: 600
   - Cell padding: 0.75rem (mobile), 1rem (desktop)
   - Border-bottom: 1px solid #dee2e6
   - Hover background: #f8f9fa

5. WHEN displaying tables on mobile devices, THE System SHALL provide horizontal scroll with visual indicators

### Requirement 4: Consistent Typography and Text Styling

**User Story:** As a user, I want text elements to have consistent styling across pages, so that the interface feels cohesive and professional.

#### Acceptance Criteria

1. THE System SHALL use consistent font properties for similar elements:
   - Page titles: Font-size 1.5rem, font-weight 600
   - Section headings: Font-size 1.125rem, font-weight 600
   - Body text: Font-size 0.875rem (mobile), 0.95rem (desktop)
   - Labels: Font-weight 500, color #666

2. WHEN displaying boat numbers, THE System SHALL use consistent styling:
   - Font-weight: 600
   - Color: #007bff (blue)
   - Applied in both card and table views

3. WHEN displaying club names, THE System SHALL use consistent styling:
   - Display in club-box component
   - Background: #f5f5f5
   - Border: 1px solid #ddd
   - Border-radius: 4px
   - Padding: 0.25rem 0.5rem
   - Font-size: 0.75rem

4. WHEN displaying crew member identifiers (crew #), THE System SHALL use consistent styling:
   - Color: #007bff (blue) in all views
   - Font-weight: 600 (optional, for emphasis)

5. THE System SHALL use consistent capitalization rules:
   - Status labels: Sentence case
   - Button labels: Sentence case
   - Table headers: Sentence case
   - No inconsistent use of ALL CAPS

### Requirement 5: Standardized Color Palette

**User Story:** As a user, I want colors to be used consistently throughout the application, so that I can associate colors with specific meanings.

#### Acceptance Criteria

1. THE System SHALL define a semantic color palette:
   - Primary blue: #007bff (links, primary actions, boat numbers)
   - Success green: #28a745 (complete status, success messages)
   - Warning yellow: #ffc107 (incomplete status, warnings)
   - Danger red: #dc3545 (delete actions, forfait status, errors)
   - Secondary grey: #6c757d (secondary actions, labels)
   - Light grey: #f8f9fa (backgrounds, disabled states)
   - Text grey: #666 (secondary text, labels)
   - Dark text: #212529 (primary text)

2. WHEN displaying interactive elements, THE System SHALL use colors consistently:
   - Links: #007bff
   - Hover states: Darkened version of base color
   - Disabled states: #ccc

3. WHEN displaying status or state information, THE System SHALL use semantic colors:
   - Success/Complete: Green
   - Warning/Incomplete: Yellow
   - Error/Forfait: Red
   - Info/Paid: Blue

4. THE System SHALL maintain consistent transparency values:
   - Overlay backgrounds: rgba(0, 0, 0, 0.5)
   - Hover backgrounds: rgba(0, 0, 0, 0.05) or specific color with 0.1 opacity
   - Disabled elements: opacity 0.6

### Requirement 6: Reusable Component Library

**User Story:** As a developer, I want to use shared components for common UI patterns, so that changes can be made in one place and reflected everywhere.

#### Acceptance Criteria

1. THE System SHALL provide reusable button components:
   - BaseButton component with variants (primary, secondary, danger, warning)
   - Consistent props interface (disabled, loading, size)
   - Consistent styling and behavior

2. THE System SHALL provide reusable status badge component:
   - StatusBadge component accepting status prop
   - Automatic color mapping based on status
   - Consistent styling across all uses

3. THE System SHALL provide reusable table components:
   - SortableTable component with sorting logic
   - TableHeader component with sort indicators
   - Consistent table styling

4. THE System SHALL provide reusable card components:
   - DataCard component for displaying entity information
   - Consistent card styling and layout
   - Responsive behavior

5. WHEN a shared component is updated, THE System SHALL reflect changes in all pages using that component

6. THE System SHALL centralize common styles:
   - Shared CSS variables for colors, spacing, typography
   - Utility classes for common patterns
   - Consistent import and usage across components

### Requirement 7: Consistent Spacing and Layout

**User Story:** As a user, I want consistent spacing between elements, so that the interface feels organized and easy to scan.

#### Acceptance Criteria

1. THE System SHALL use consistent spacing units:
   - Base unit: 0.5rem (8px)
   - Small gap: 0.5rem
   - Medium gap: 0.75rem
   - Large gap: 1rem
   - Extra large gap: 1.5rem

2. WHEN displaying cards in a grid, THE System SHALL use consistent gaps:
   - Mobile: 1rem gap
   - Desktop: 1.5rem gap

3. WHEN displaying form elements, THE System SHALL use consistent spacing:
   - Label to input: 0.5rem
   - Between form groups: 1rem
   - Form padding: 1rem (mobile), 1.5rem (desktop)

4. WHEN displaying action buttons, THE System SHALL use consistent gaps:
   - Between buttons: 0.5rem (table), 0.75rem (cards)
   - Button group margin: 1rem from content

5. THE System SHALL use consistent padding for containers:
   - Card padding: 1rem (mobile), 1.5rem (desktop)
   - Modal padding: 1rem (mobile), 1.5rem (desktop)
   - Page padding: 0 (mobile with full-width cards), 1rem (desktop)

### Requirement 8: Responsive Design Consistency

**User Story:** As a user on different devices, I want the interface to adapt consistently, so that I have a good experience regardless of screen size.

#### Acceptance Criteria

1. THE System SHALL use consistent breakpoints:
   - Mobile: < 768px
   - Tablet: 768px - 1023px
   - Desktop: ≥ 1024px

2. WHEN displaying on mobile devices, THE System SHALL:
   - Stack action buttons vertically
   - Use full-width buttons (min-height 44px)
   - Display cards in single column
   - Enable horizontal scroll for tables

3. WHEN displaying on desktop devices, THE System SHALL:
   - Display action buttons horizontally where appropriate
   - Use multi-column card grids
   - Display full tables without scroll
   - Provide hover states for interactive elements

4. THE System SHALL maintain consistent touch targets:
   - Minimum 44px height for all interactive elements on mobile
   - Adequate spacing between touch targets (minimum 8px)

### Requirement 9: Consistent Modal and Overlay Styling

**User Story:** As a user, I want modals and overlays to appear and behave consistently, so that I know how to interact with them.

#### Acceptance Criteria

1. THE System SHALL use consistent modal overlay styling:
   - Background: rgba(0, 0, 0, 0.5)
   - Z-index: 1000
   - Full viewport coverage
   - Click outside to close (where appropriate)

2. THE System SHALL use consistent modal content styling:
   - Background: white
   - Border-radius: 8px (desktop), 12px 12px 0 0 (mobile bottom sheet)
   - Max-width: 600px (desktop)
   - Full width (mobile)
   - Box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1)

3. WHEN displaying modals on mobile, THE System SHALL:
   - Position at bottom of screen (bottom sheet pattern)
   - Slide up animation
   - Max-height: 90vh
   - Scrollable content area

4. WHEN displaying modals on desktop, THE System SHALL:
   - Center on screen
   - Fade in animation
   - Fixed or scrollable content based on height

5. THE System SHALL provide consistent modal header styling:
   - Padding: 1rem 1.5rem
   - Border-bottom: 1px solid #dee2e6
   - Close button: Top-right, consistent styling

6. THE System SHALL provide consistent modal footer styling:
   - Padding: 1rem 1.5rem
   - Border-top: 1px solid #dee2e6
   - Action buttons aligned right
   - Consistent button order (cancel left, primary action right)

### Requirement 10: Consistent Loading and Empty States

**User Story:** As a user, I want loading indicators and empty states to look the same across all pages, so that I understand what's happening.

#### Acceptance Criteria

1. THE System SHALL use consistent loading indicator styling:
   - Spinner: 40px diameter
   - Border: 4px solid #f3f3f3
   - Border-top: 4px solid #4CAF50
   - Animation: 1s linear infinite rotation
   - Centered with loading text below

2. THE System SHALL use consistent empty state styling:
   - Centered text
   - Color: #666
   - Padding: 2rem (mobile), 3rem (desktop)
   - Optional call-to-action button

3. WHEN data is loading, THE System SHALL display:
   - Loading spinner
   - Loading text (e.g., "Loading...")
   - Consistent positioning

4. WHEN no data is available, THE System SHALL display:
   - Empty state message
   - Helpful text explaining why no data is shown
   - Optional action button (e.g., "Add your first boat")

### Requirement 11: Consistent Error and Success Message Styling

**User Story:** As a user, I want error and success messages to be clearly distinguishable and consistently styled, so that I understand the outcome of my actions.

#### Acceptance Criteria

1. THE System SHALL use consistent error message styling:
   - Background: #fee (light red)
   - Border: 1px solid #fcc
   - Border-radius: 4px
   - Color: #c33 (dark red)
   - Padding: 1rem
   - Font-size: 0.875rem

2. THE System SHALL use consistent success message styling:
   - Background: #e7f5ec (light green)
   - Border: 1px solid #c3e6cb
   - Border-radius: 4px
   - Color: #155724 (dark green)
   - Padding: 1rem
   - Font-size: 0.875rem

3. THE System SHALL use consistent warning message styling:
   - Background: #fff9e6 (light yellow)
   - Border: 1px solid #ffc107
   - Border-radius: 4px
   - Color: #856404 (dark yellow)
   - Padding: 1rem
   - Font-size: 0.875rem

4. WHEN displaying messages, THE System SHALL:
   - Position consistently (top of content area or inline)
   - Provide clear, actionable text
   - Include dismiss option where appropriate
   - Auto-dismiss after timeout (optional, for non-critical messages)

### Requirement 12: Consistent Filter and Search Styling

**User Story:** As a user, I want filter controls and search inputs to look and behave the same across all list pages, so that I can easily find what I'm looking for.

#### Acceptance Criteria

1. THE System SHALL use consistent filter control styling:
   - Select inputs: Padding 0.5rem, border 1px solid #ddd, border-radius 4px
   - Text inputs: Padding 0.5rem, border 1px solid #ddd, border-radius 4px
   - Min-height: 44px (mobile)
   - Font-size: 16px (mobile, prevents iOS zoom)
   - Background: white

2. THE System SHALL use consistent filter layout:
   - Horizontal layout on desktop
   - Vertical stack on mobile
   - Consistent gap between filters: 0.5rem
   - Label positioning: Left of input (desktop), above input (mobile)

3. WHEN a filter is active, THE System SHALL provide visual indication:
   - Clear filters button visible
   - Filter count indicator (optional)

4. THE System SHALL use consistent search input styling:
   - Placeholder text color: #999
   - Search icon (optional)
   - Clear button when text is entered
   - Debounced search (300ms delay)

5. THE System SHALL provide consistent "Clear filters" functionality:
   - Button or link to reset all filters
   - Consistent positioning
   - Consistent styling

### Requirement 13: Design System Documentation

**User Story:** As a developer, I want comprehensive design system documentation, so that I can build new features that are consistent with existing UI patterns.

#### Acceptance Criteria

1. THE System SHALL provide a design system documentation file at `docs/design-system.md`

2. THE documentation SHALL include the following sections:
   - Overview and purpose of the design system
   - Color palette with semantic meanings and hex codes
   - Typography scale with font sizes, weights, and usage guidelines
   - Spacing scale with values and usage examples
   - Component library reference with usage examples
   - Button variants and states
   - Status badge styles
   - Table patterns
   - Card patterns
   - Modal patterns
   - Form patterns
   - Loading and empty states
   - Error and success message patterns

3. THE documentation SHALL include code examples for each pattern:
   - HTML/Vue template examples
   - CSS class names
   - Component props and usage
   - Before/after examples where applicable

4. THE documentation SHALL include visual examples:
   - Color swatches with hex codes
   - Typography samples
   - Component screenshots or descriptions
   - Spacing diagrams

5. THE documentation SHALL be maintained and updated:
   - Version number or last updated date
   - Change log for major updates
   - Links to related components in codebase

6. THE documentation SHALL be referenced from the main `docs/README.md` file

### Requirement 14: UI Consistency Steering Rules

**User Story:** As a developer, I want automated guardrails that remind me to follow design system rules, so that I maintain consistency without having to memorize all guidelines.

#### Acceptance Criteria

1. THE System SHALL provide a steering file at `.kiro/steering/ui-consistency.md`

2. THE steering file SHALL enforce design system rules during development:
   - Button styling rules (colors, sizes, variants)
   - Color usage rules (semantic color palette)
   - Typography rules (font sizes, weights, capitalization)
   - Spacing rules (consistent gaps and padding)
   - Component reusability rules (use shared components)

3. WHEN a developer creates or modifies UI components, THE steering file SHALL remind them to:
   - Use shared components instead of creating new ones
   - Follow the established color palette
   - Use consistent button classes and styling
   - Apply consistent spacing values
   - Follow typography guidelines
   - Use status badge component for status displays
   - Implement table sorting consistently
   - Follow responsive design patterns

4. THE steering file SHALL include:
   - Quick reference to common patterns
   - Links to design system documentation
   - Examples of correct and incorrect implementations
   - Checklist for UI consistency review

5. THE steering file SHALL be set to "always included" mode:
   - Automatically loaded for all frontend development tasks
   - Provides proactive guidance during implementation

6. THE steering file SHALL reference the design system documentation:
   - Link to `docs/design-system.md` for detailed guidelines
   - Quick reference for most common patterns
   - Escalation path for questions or exceptions

## Appendix A: Color Reference

### Semantic Colors

| Purpose | Color Code | Usage |
|---------|-----------|-------|
| Primary | #007bff | Primary actions, links, boat numbers |
| Success | #28a745 | Complete status, success messages |
| Warning | #ffc107 | Incomplete status, warnings |
| Danger | #dc3545 | Delete actions, forfait, errors |
| Secondary | #6c757d | Secondary actions, labels |
| Light | #f8f9fa | Backgrounds, table headers |
| Dark | #212529 | Primary text |
| Muted | #666 | Secondary text, labels |

### Status Colors

| Status | Background | Text |
|--------|-----------|------|
| Incomplete | #ffc107 | #000 |
| Complete | #28a745 | #fff |
| Paid | #007bff | #fff |
| Forfait | #dc3545 | #fff |

## Appendix B: Typography Scale

| Element | Mobile | Desktop | Weight |
|---------|--------|---------|--------|
| Page Title | 1.25rem | 1.5rem | 600 |
| Section Heading | 1rem | 1.125rem | 600 |
| Body Text | 0.875rem | 0.95rem | 400 |
| Small Text | 0.75rem | 0.8125rem | 400 |
| Label | 0.875rem | 0.875rem | 500 |
| Button | 0.875rem | 0.875rem | 500 |

## Appendix C: Spacing Scale

| Name | Value | Usage |
|------|-------|-------|
| xs | 0.25rem (4px) | Tight spacing |
| sm | 0.5rem (8px) | Small gaps |
| md | 0.75rem (12px) | Medium gaps |
| lg | 1rem (16px) | Large gaps |
| xl | 1.5rem (24px) | Extra large gaps |
| 2xl | 2rem (32px) | Section spacing |

## Appendix D: Component Inventory

### Current Components Requiring Standardization

1. **Buttons**
   - Location: Scattered across views (Boats.vue, AdminBoats.vue, BoatDetail.vue, etc.)
   - Issues: Inconsistent classes (btn-primary, btn-secondary, btn-danger), varying sizes
   - Action: Create BaseButton component

2. **Status Badges**
   - Location: Boats.vue, AdminBoats.vue, AdminCrewMembers.vue
   - Issues: Inconsistent capitalization, varying styles
   - Action: Create StatusBadge component

3. **Tables**
   - Location: AdminBoats.vue (sortable), Boats.vue (not sortable), AdminCrewMembers.vue
   - Issues: Inconsistent sorting, varying column widths, different styling
   - Action: Create SortableTable component

4. **Cards**
   - Location: Boats.vue, AdminBoats.vue, CrewMemberList.vue
   - Issues: Varying padding, inconsistent detail-row styling
   - Action: Create DataCard component

5. **Filters**
   - Location: ListFilters.vue (shared), but inconsistent usage
   - Issues: Varying filter layouts, inconsistent styling
   - Action: Standardize ListFilters component usage

6. **Modals**
   - Location: Multiple views with inline modal code
   - Issues: Inconsistent overlay styling, varying animations
   - Action: Create BaseModal component

## Appendix E: Pages Requiring Updates

### Team Manager Pages
1. `/boats` (Boats.vue) - Button styling, table sorting, status badges
2. `/boats/:id` (BoatDetail.vue) - Button styling, spacing
3. `/crew-members` (CrewMembers.vue via CrewMemberList.vue) - Button styling, card styling

### Admin Pages
1. `/admin/boats` (AdminBoats.vue) - Button styling, status capitalization, crew # color
2. `/admin/crew-members` (AdminCrewMembers.vue) - Button styling, table sorting
3. `/admin/club-managers` (AdminClubManagers.vue) - Button styling, table consistency
4. `/admin/dashboard` (AdminDashboard.vue) - Card styling, button styling
5. `/admin/event-config` (AdminEventConfig.vue) - Form styling, button styling
6. `/admin/pricing-config` (AdminPricingConfig.vue) - Form styling, button styling

### Shared Components
1. `BoatRegistrationForm.vue` - Button styling, form spacing
2. `CrewMemberForm.vue` - Button styling, form spacing
3. `CrewMemberCard.vue` - Card styling, button styling
4. `ListHeader.vue` - Typography, spacing
5. `ListFilters.vue` - Filter styling, spacing

## Appendix F: Deliverables

### Documentation Deliverable

**File:** `docs/design-system.md`

**Purpose:** Comprehensive reference documentation for the design system that developers can consult when building or modifying UI components.

**Contents:**
- Complete color palette with usage guidelines
- Typography scale and usage rules
- Spacing system
- Component library reference
- Code examples and patterns
- Visual examples
- Maintenance guidelines

### Steering File Deliverable

**File:** `.kiro/steering/ui-consistency.md`

**Purpose:** Automated guardrails that provide real-time guidance during development to ensure UI consistency.

**Contents:**
- Quick reference for common patterns
- Automated reminders for design system rules
- Links to detailed documentation
- Examples of correct/incorrect implementations
- UI consistency checklist

**Configuration:** Always included mode (automatically loaded for frontend work)
