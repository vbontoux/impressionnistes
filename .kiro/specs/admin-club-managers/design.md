# Design Document: Admin Club Managers Page

## Overview

The Admin Club Managers page provides administrators with a centralized interface to view and contact all club managers in the system. The feature reuses the existing `GET /admin/team-managers` API endpoint and implements a Vue.js component with table display, search functionality, and bulk email capabilities.

## Architecture

### Component Structure

```
AdminClubManagers.vue (Main Page Component)
├── Data fetching via apiClient
├── Search/filter logic
├── Selection state management
└── Email composition logic
```

### Data Flow

1. Component mounts → Fetch club managers from API
2. User searches → Filter local data
3. User selects managers → Update selection state
4. User clicks "Email Selected" → Generate mailto URL with BCC

## Components and Interfaces

### Frontend Component

**File:** `frontend/src/views/admin/AdminClubManagers.vue`

**Responsibilities:**
- Fetch club managers from API on mount
- Display managers in a responsive table
- Handle search/filter functionality
- Manage checkbox selection state
- Generate mailto links for bulk email

**Key Methods:**
```javascript
loadClubManagers()      // Fetch data from API
filterManagers()        // Filter based on search term
toggleSelection(id)     // Toggle individual checkbox
selectAll()             // Select all visible managers
deselectAll()           // Clear all selections
emailSelected()         // Open email client with selected addresses
```

**State:**
```javascript
{
  managers: [],           // All club managers
  filteredManagers: [],   // Filtered list based on search
  selectedIds: Set(),     // Set of selected manager IDs
  searchTerm: '',         // Current search input
  loading: false,         // Loading state
  error: null            // Error message if any
}
```

### API Integration

**Endpoint:** `GET /admin/team-managers`

**Response Format:**
```json
{
  "data": {
    "team_managers": [
      {
        "user_id": "string",
        "first_name": "string",
        "last_name": "string",
        "email": "string",
        "club_affiliation": "string"
      }
    ],
    "count": 0
  }
}
```

### Router Configuration

**File:** `frontend/src/router/index.js`

**New Route:**
```javascript
{
  path: '/admin/club-managers',
  name: 'AdminClubManagers',
  component: () => import('../views/admin/AdminClubManagers.vue'),
  meta: { requiresAuth: true, requiresAdmin: true }
}
```

### Dashboard Integration

**File:** `frontend/src/views/admin/AdminDashboard.vue`

**New Section Card:**
- Icon: Users/people SVG icon
- Title: "Club Managers" (i18n key)
- Description: "View and contact club managers" (i18n key)
- Link: `/admin/club-managers`

## Data Models

### ClubManager Interface

```typescript
interface ClubManager {
  user_id: string;
  first_name: string;
  last_name: string;
  email: string;
  club_affiliation: string;
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Search Filter Consistency

*For any* search term and list of club managers, all filtered results should contain the search term in at least one of the searchable fields (first name, last name, email, or club affiliation).

**Validates: Requirements 4.1, 4.2**

### Property 2: Selection State Integrity

*For any* selection operation (select, deselect, select all, deselect all), the selection state should accurately reflect the user's actions and the selected count should match the number of selected managers.

**Validates: Requirements 3.2, 3.3, 3.4, 3.5**

### Property 3: Email Generation Correctness

*For any* set of selected managers, the generated mailto URL should include all and only the email addresses of the selected managers in the BCC field.

**Validates: Requirements 3.6**

### Property 4: Admin Access Control

*For any* user attempting to access the club managers page, access should be granted if and only if the user has admin privileges.

**Validates: Requirements 5.3**

## Error Handling

### API Errors

- **Network failure:** Display error message with "Retry" button
- **Authentication failure:** Redirect to login page
- **Authorization failure:** Redirect to dashboard with warning
- **Server error:** Display user-friendly error message

### Email Client Errors

- **mailto URL too long:** Display warning and suggest using "Copy Emails" feature (future enhancement)
- **No email client configured:** Browser will handle gracefully (opens system dialog)

### Edge Cases

- **Empty list:** Display "No club managers found" message
- **No search results:** Display "No managers match your search" message
- **No selection:** Disable "Email Selected" button

## Testing Strategy

### Unit Tests

- Test search filter logic with various search terms
- Test selection state management (select, deselect, select all)
- Test mailto URL generation with different email sets
- Test empty state and error state rendering

### Integration Tests

- Test API integration with mocked responses
- Test router navigation and access control
- Test component lifecycle (mount, unmount, data loading)

### Manual Testing

- Verify responsive design on mobile devices
- Test email client integration on different platforms
- Verify accessibility (keyboard navigation, screen readers)
- Test with large datasets (100+ managers)

## Implementation Notes

### Email URL Limitations

The `mailto:` protocol has URL length limitations (~2000 characters). For typical email addresses (~30 chars), this supports approximately 60 managers. For the initial implementation, this is acceptable. Future enhancement could add a "Copy Emails" button for larger selections.

### Performance Considerations

- Client-side filtering is acceptable for expected dataset size (<500 managers)
- Use Vue's reactivity efficiently (computed properties for filtered list)
- Debounce search input to avoid excessive re-renders

### Accessibility

- Ensure proper ARIA labels for checkboxes
- Maintain keyboard navigation support
- Provide screen reader announcements for selection changes
- Use semantic HTML elements

### Styling

- Match existing admin page styling (AdminBoats.vue, AdminCrewMembers.vue)
- Use consistent color scheme and spacing
- Ensure hover states and visual feedback for interactive elements
- Maintain responsive grid layout
