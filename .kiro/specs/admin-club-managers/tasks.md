# Implementation Plan: Admin Club Managers Page

## Overview

This implementation plan creates a new admin page for viewing and contacting club managers. The backend API already exists, so we focus on frontend implementation, routing, and dashboard integration.

## Tasks

- [x] 1. Create AdminClubManagers Vue component
  - Create `frontend/src/views/admin/AdminClubManagers.vue`
  - Implement data fetching from `/admin/team-managers` endpoint
  - Create table layout with columns: checkbox, name, email, club affiliation
  - Add loading and error states
  - Add empty state for no managers
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Implement search and filter functionality
  - Add search input field
  - Implement client-side filtering across all searchable fields
  - Update filtered results reactively
  - Show "no results" message when search returns empty
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 3. Implement selection and bulk email features
  - Add checkbox for each manager row
  - Implement individual selection toggle
  - Add "Select All" and "Deselect All" buttons
  - Display count of selected managers
  - Add "Email Selected" button (disabled when no selection)
  - Generate mailto URL with BCC field containing selected emails
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [x] 4. Implement individual email links
  - Make email addresses clickable mailto links
  - Style email links appropriately
  - _Requirements: 2.1, 2.2_

- [x] 5. Add responsive design and styling
  - Match existing admin page styling
  - Ensure mobile responsiveness
  - Add hover states and visual feedback
  - Style selected rows
  - _Requirements: 6.1, 6.2_

- [x] 6. Add route configuration
  - Update `frontend/src/router/index.js`
  - Add lazy-loaded route for `/admin/club-managers`
  - Set meta flags: `requiresAuth: true, requiresAdmin: true`
  - _Requirements: 5.3_

- [x] 7. Integrate with admin dashboard
  - Update `frontend/src/views/admin/AdminDashboard.vue`
  - Add new section card for "Club Managers"
  - Add appropriate icon (users/people icon)
  - Link to `/admin/club-managers`
  - _Requirements: 5.1, 5.2_

- [x] 8. Add translations
  - Update `frontend/src/locales/en.json`
  - Update `frontend/src/locales/fr.json`
  - Add keys for:
    - Page title
    - Column headers
    - Button labels (Select All, Deselect All, Email Selected)
    - Search placeholder
    - Empty state messages
    - Error messages
    - Dashboard card title and description
  - _Requirements: All_

- [x] 9. Manual testing and verification
  - Test page loads and displays managers correctly
  - Test search functionality
  - Test selection (individual, select all, deselect all)
  - Test bulk email button opens email client
  - Test individual email links
  - Test responsive design on mobile
  - Test admin-only access enforcement
  - Test loading and error states
  - _Requirements: All_

## Notes

- Backend API endpoint already exists and is tested
- Focus on minimal, clean implementation
- Reuse styling patterns from existing admin pages
- Client-side filtering is sufficient for expected data size
- mailto URL length limit (~2000 chars) supports ~60 email addresses
