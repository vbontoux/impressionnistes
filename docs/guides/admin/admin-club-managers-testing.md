# Admin Club Managers - Manual Testing Guide

## Overview

This guide provides a comprehensive checklist for manually testing the Admin Club Managers feature. Complete all test cases to ensure the feature works correctly across different scenarios and devices.

## Prerequisites

- Admin user account with proper permissions
- Development or staging environment running
- Multiple club managers in the database (at least 5-10 for meaningful testing)
- Access to different devices/browsers for responsive testing

## Test Cases

### 1. Page Load and Display

**Test 1.1: Initial Page Load**
- [ ] Navigate to `/admin/club-managers`
- [ ] Verify page loads without errors
- [ ] Verify loading spinner appears briefly
- [ ] Verify table/cards display after loading completes
- [ ] Verify all manager data is visible (name, email, club affiliation)

**Test 1.2: Data Accuracy**
- [ ] Verify first names are displayed correctly
- [ ] Verify last names are displayed correctly
- [ ] Verify email addresses are displayed correctly
- [ ] Verify club affiliations are displayed correctly
- [ ] Verify count matches the number of displayed managers

**Test 1.3: Empty State**
- [ ] If no managers exist, verify "No club managers found" message displays
- [ ] Verify no table/cards are shown in empty state

---

### 2. Search Functionality

**Test 2.1: Search by First Name**
- [ ] Enter a first name in the search field
- [ ] Verify only matching managers are displayed
- [ ] Verify search is case-insensitive
- [ ] Verify partial matches work (e.g., "Joh" matches "John")

**Test 2.2: Search by Last Name**
- [ ] Enter a last name in the search field
- [ ] Verify only matching managers are displayed
- [ ] Verify search is case-insensitive

**Test 2.3: Search by Email**
- [ ] Enter an email or part of an email in the search field
- [ ] Verify only matching managers are displayed
- [ ] Verify partial email matches work

**Test 2.4: Search by Club Affiliation**
- [ ] Enter a club name in the search field
- [ ] Verify only managers from that club are displayed
- [ ] Verify partial club name matches work

**Test 2.5: No Search Results**
- [ ] Enter a search term that matches no managers
- [ ] Verify "No managers match your search" message displays
- [ ] Verify "Clear Search" button appears
- [ ] Click "Clear Search" and verify all managers reappear

**Test 2.6: Clear Search**
- [ ] Enter a search term
- [ ] Clear the search field manually
- [ ] Verify all managers reappear

---

### 3. Selection Functionality

**Test 3.1: Individual Selection**
- [ ] Click checkbox next to a manager
- [ ] Verify checkbox becomes checked
- [ ] Verify row/card highlights (background color changes)
- [ ] Verify selection count updates
- [ ] Click checkbox again to deselect
- [ ] Verify checkbox becomes unchecked
- [ ] Verify highlight is removed
- [ ] Verify selection count updates

**Test 3.2: Select All**
- [ ] Click "Select All" button
- [ ] Verify all visible managers are selected
- [ ] Verify all checkboxes are checked
- [ ] Verify all rows/cards are highlighted
- [ ] Verify selection count shows total number
- [ ] Verify "Select All" button becomes disabled

**Test 3.3: Deselect All**
- [ ] Select multiple managers
- [ ] Click "Deselect All" button
- [ ] Verify all selections are cleared
- [ ] Verify all checkboxes are unchecked
- [ ] Verify all highlights are removed
- [ ] Verify selection count shows 0
- [ ] Verify "Deselect All" button becomes disabled

**Test 3.4: Header Checkbox (Table View)**
- [ ] Switch to table view
- [ ] Click the checkbox in the table header
- [ ] Verify all managers are selected
- [ ] Click header checkbox again
- [ ] Verify all managers are deselected

**Test 3.5: Selection with Search**
- [ ] Select some managers
- [ ] Enter a search term that filters the list
- [ ] Verify previously selected managers remain selected if they match the search
- [ ] Verify selection count reflects only visible selected managers
- [ ] Clear search
- [ ] Verify all original selections are still active

---

### 4. Bulk Email Functionality

**Test 4.1: Email Selected Button State**
- [ ] With no selections, verify "Email Selected" button is disabled
- [ ] Select one manager, verify button becomes enabled
- [ ] Select multiple managers, verify button remains enabled
- [ ] Deselect all, verify button becomes disabled again

**Test 4.2: Email Selected - Single Manager**
- [ ] Select one manager
- [ ] Click "Email Selected" button
- [ ] Verify email client opens
- [ ] Verify selected email is in the BCC field
- [ ] Verify BCC field is properly formatted

**Test 4.3: Email Selected - Multiple Managers**
- [ ] Select 3-5 managers
- [ ] Click "Email Selected" button
- [ ] Verify email client opens
- [ ] Verify all selected emails are in the BCC field
- [ ] Verify emails are comma-separated
- [ ] Verify no duplicate emails appear

**Test 4.4: Email Selected - Large Selection**
- [ ] Select 10+ managers (if available)
- [ ] Click "Email Selected" button
- [ ] Verify email client opens successfully
- [ ] Verify all emails are included in BCC field
- [ ] Note: mailto URL has ~2000 char limit (~60 emails)

---

### 5. Individual Email Links

**Test 5.1: Email Link Click**
- [ ] Click on any manager's email address
- [ ] Verify email client opens
- [ ] Verify the clicked email is in the "To" field
- [ ] Verify email is properly formatted

**Test 5.2: Email Link Styling**
- [ ] Verify email addresses are styled as links (blue color)
- [ ] Hover over email link
- [ ] Verify hover state (underline, color change)
- [ ] Verify cursor changes to pointer

**Test 5.3: Email Link Accessibility**
- [ ] Tab to an email link using keyboard
- [ ] Verify focus outline is visible
- [ ] Press Enter to activate link
- [ ] Verify email client opens

---

### 6. View Modes (Table vs Cards)

**Test 6.1: Switch to Card View**
- [ ] Click the card view icon in the header
- [ ] Verify display switches to card layout
- [ ] Verify all manager data is visible in cards
- [ ] Verify checkboxes work in card view
- [ ] Verify selection highlighting works

**Test 6.2: Switch to Table View**
- [ ] Click the table view icon in the header
- [ ] Verify display switches to table layout
- [ ] Verify all columns are visible
- [ ] Verify checkboxes work in table view
- [ ] Verify selection highlighting works

**Test 6.3: View Mode Persistence**
- [ ] Switch to card view
- [ ] Refresh the page
- [ ] Verify card view is still active
- [ ] Switch to table view
- [ ] Refresh the page
- [ ] Verify table view is still active

---

### 7. Sorting (Table View)

**Test 7.1: Sort by Name**
- [ ] Switch to table view
- [ ] Click on "Name" column header
- [ ] Verify managers are sorted alphabetically by last name (ascending)
- [ ] Verify sort indicator (▲) appears
- [ ] Click "Name" header again
- [ ] Verify sort order reverses (descending)
- [ ] Verify sort indicator changes (▼)

**Test 7.2: Sort by Email**
- [ ] Click on "Email" column header
- [ ] Verify managers are sorted alphabetically by email (ascending)
- [ ] Click again to verify descending sort

**Test 7.3: Sort by Club Affiliation**
- [ ] Click on "Club Affiliation" column header
- [ ] Verify managers are sorted alphabetically by club (ascending)
- [ ] Click again to verify descending sort

---

### 8. Responsive Design

**Test 8.1: Desktop View (1920x1080)**
- [ ] View page on large desktop screen
- [ ] Verify table layout is comfortable and readable
- [ ] Verify all columns fit without horizontal scroll
- [ ] Verify buttons are properly sized and spaced

**Test 8.2: Laptop View (1366x768)**
- [ ] View page on laptop screen
- [ ] Verify layout adjusts appropriately
- [ ] Verify table remains usable
- [ ] Verify no layout breaking

**Test 8.3: Tablet View (768x1024)**
- [ ] View page on tablet or resize browser to tablet size
- [ ] Verify card view works well on tablet
- [ ] Verify table view has horizontal scroll if needed
- [ ] Verify buttons remain accessible
- [ ] Verify touch targets are adequate (min 44x44px)

**Test 8.4: Mobile View (375x667 - iPhone SE)**
- [ ] View page on mobile device or resize browser
- [ ] Verify card view is default or works better on mobile
- [ ] Verify table has horizontal scroll
- [ ] Verify search field is full width
- [ ] Verify buttons stack vertically
- [ ] Verify selection actions are accessible
- [ ] Verify touch targets are adequate

**Test 8.5: Mobile Landscape**
- [ ] Rotate mobile device to landscape
- [ ] Verify layout adjusts appropriately
- [ ] Verify all functionality remains accessible

---

### 9. Admin Access Control

**Test 9.1: Admin User Access**
- [ ] Log in as admin user
- [ ] Navigate to `/admin/club-managers`
- [ ] Verify page loads successfully
- [ ] Verify all features are accessible

**Test 9.2: Non-Admin User Access**
- [ ] Log in as regular (non-admin) user
- [ ] Attempt to navigate to `/admin/club-managers`
- [ ] Verify user is redirected to dashboard
- [ ] Verify appropriate message is shown (if any)

**Test 9.3: Unauthenticated Access**
- [ ] Log out completely
- [ ] Attempt to navigate to `/admin/club-managers`
- [ ] Verify user is redirected to login page
- [ ] After login, verify appropriate redirect behavior

**Test 9.4: Dashboard Link Access**
- [ ] Log in as admin
- [ ] Go to admin dashboard
- [ ] Verify "Club Managers" card is visible
- [ ] Verify card appears after "Manage Crews" card
- [ ] Click on "Club Managers" card
- [ ] Verify navigation to club managers page works

---

### 10. Loading and Error States

**Test 10.1: Loading State**
- [ ] Refresh the page
- [ ] Verify loading spinner appears immediately
- [ ] Verify "Loading..." text is displayed
- [ ] Verify no table/cards are shown during loading
- [ ] Verify loading state disappears when data loads

**Test 10.2: API Error Handling**
- [ ] Simulate API error (disconnect network or use dev tools)
- [ ] Refresh the page
- [ ] Verify error message is displayed
- [ ] Verify error message is user-friendly
- [ ] Verify "Retry" button appears
- [ ] Click "Retry" button
- [ ] Verify page attempts to reload data

**Test 10.3: Network Recovery**
- [ ] Start with network disconnected
- [ ] Load page and see error
- [ ] Reconnect network
- [ ] Click "Retry" button
- [ ] Verify data loads successfully

---

### 11. Internationalization (i18n)

**Test 11.1: English Language**
- [ ] Set language to English
- [ ] Verify all labels are in English
- [ ] Verify page title is correct
- [ ] Verify button labels are correct
- [ ] Verify empty state messages are correct

**Test 11.2: French Language**
- [ ] Set language to French
- [ ] Verify all labels are in French
- [ ] Verify page title is correct
- [ ] Verify button labels are correct
- [ ] Verify empty state messages are correct

**Test 11.3: Language Switching**
- [ ] Start in English
- [ ] Select some managers
- [ ] Switch to French
- [ ] Verify selections are maintained
- [ ] Verify all text updates to French
- [ ] Switch back to English
- [ ] Verify everything still works

---

### 12. Browser Compatibility

**Test 12.1: Chrome**
- [ ] Test all core functionality in Chrome
- [ ] Verify no console errors
- [ ] Verify styling is correct

**Test 12.2: Firefox**
- [ ] Test all core functionality in Firefox
- [ ] Verify no console errors
- [ ] Verify styling is correct

**Test 12.3: Safari**
- [ ] Test all core functionality in Safari
- [ ] Verify no console errors
- [ ] Verify styling is correct
- [ ] Verify mailto links work correctly

**Test 12.4: Edge**
- [ ] Test all core functionality in Edge
- [ ] Verify no console errors
- [ ] Verify styling is correct

---

### 13. Accessibility

**Test 13.1: Keyboard Navigation**
- [ ] Tab through all interactive elements
- [ ] Verify focus indicators are visible
- [ ] Verify tab order is logical
- [ ] Use Enter/Space to activate buttons
- [ ] Verify all functionality is keyboard accessible

**Test 13.2: Screen Reader**
- [ ] Use screen reader (NVDA, JAWS, or VoiceOver)
- [ ] Verify page title is announced
- [ ] Verify table structure is announced correctly
- [ ] Verify checkbox labels are meaningful
- [ ] Verify button purposes are clear

**Test 13.3: High Contrast Mode**
- [ ] Enable high contrast mode in OS
- [ ] Verify all text is readable
- [ ] Verify borders and separators are visible
- [ ] Verify focus indicators are visible

**Test 13.4: Reduced Motion**
- [ ] Enable reduced motion in OS settings
- [ ] Verify animations are disabled or reduced
- [ ] Verify functionality still works

---

### 14. Performance

**Test 14.1: Large Dataset**
- [ ] Test with 50+ managers (if available)
- [ ] Verify page loads in reasonable time (<3 seconds)
- [ ] Verify search is responsive
- [ ] Verify selection is responsive
- [ ] Verify no lag when interacting

**Test 14.2: Slow Network**
- [ ] Throttle network to "Slow 3G" in dev tools
- [ ] Load the page
- [ ] Verify loading state is shown
- [ ] Verify page eventually loads
- [ ] Verify no timeout errors

---

## Test Results Template

Use this template to record your test results:

```
Date: _______________
Tester: _______________
Environment: _______________
Browser: _______________
Device: _______________

Test Section | Status | Notes
-------------|--------|------
1. Page Load | ✅/❌  |
2. Search    | ✅/❌  |
3. Selection | ✅/❌  |
4. Bulk Email| ✅/❌  |
5. Individual Email | ✅/❌ |
6. View Modes | ✅/❌ |
7. Sorting   | ✅/❌  |
8. Responsive| ✅/❌  |
9. Access Control | ✅/❌ |
10. Loading/Errors | ✅/❌ |
11. i18n     | ✅/❌  |
12. Browsers | ✅/❌  |
13. Accessibility | ✅/❌ |
14. Performance | ✅/❌ |

Overall Status: ✅ PASS / ❌ FAIL

Critical Issues:
-

Minor Issues:
-

Recommendations:
-
```

## Known Limitations

1. **mailto URL Length**: The mailto protocol has a URL length limit of approximately 2000 characters. This supports roughly 60 email addresses. For larger selections, consider implementing a "Copy Emails" feature.

2. **Email Client Dependency**: The bulk email feature depends on the user having a default email client configured. If no client is configured, the browser will show a system dialog.

3. **Client-Side Filtering**: Search and filtering are performed client-side. For very large datasets (500+ managers), consider implementing server-side filtering.

## Reporting Issues

When reporting issues, please include:
- Test case number and description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots or screen recordings
- Browser and device information
- Console errors (if any)
