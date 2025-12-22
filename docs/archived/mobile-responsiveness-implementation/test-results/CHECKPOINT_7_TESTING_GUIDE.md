# Checkpoint 7: Core Components Mobile Testing Guide

## Overview
This checkpoint validates that all core mobile responsiveness improvements (Tasks 1-6) are working correctly across different mobile devices and viewports.

## Testing Environment Setup

### Browser DevTools Testing
1. Open Chrome DevTools (F12)
2. Click the device toolbar icon (Ctrl+Shift+M / Cmd+Shift+M)
3. Test at these viewport widths:
   - **375px** - iPhone SE
   - **390px** - iPhone 12/13/14
   - **414px** - iPhone Plus models
   - **768px** - iPad portrait (tablet breakpoint)

### Actual Device Testing (Recommended)
- Test on real iOS device (Safari)
- Test on real Android device (Chrome)

---

## Task 1: Responsive Utilities ✓

### What to Test
- Verify responsive breakpoint constants are working
- Check useResponsive composable functionality

### Test Steps
1. Open browser console
2. Resize viewport from mobile to desktop
3. Verify breakpoint transitions occur at 768px and 1024px

### Expected Results
- [ ] Breakpoints trigger at correct widths (768px, 1024px)
- [ ] No console errors related to responsive utilities
- [ ] Smooth transitions between breakpoints

---

## Task 2: App.vue Mobile Header ✓

### What to Test
- Header layout on mobile devices
- Hamburger menu functionality
- Touch target sizes
- User menu positioning

### Test Steps
1. Navigate to any page at 375px width
2. Check header fits viewport without overflow
3. Click hamburger menu (if present)
4. Test user menu dropdown
5. Verify logo visibility
6. Test language switcher

### Expected Results
- [ ] Header fits within viewport (no horizontal scroll)
- [ ] Hamburger menu opens/closes smoothly
- [ ] All header buttons are at least 44x44px
- [ ] User menu dropdown positions correctly
- [ ] Logo remains visible
- [ ] Language switcher is accessible
- [ ] Reduced padding on mobile vs desktop

### Test at Multiple Widths
- [ ] 375px (iPhone SE)
- [ ] 390px (iPhone 12/13/14)
- [ ] 414px (iPhone Plus)

---

## Task 3: Table Scroll Indicator Component ✓

### What to Test
- TableScrollIndicator component functionality
- Scroll detection
- Gradient indicators

### Test Steps
1. Navigate to a page with tables (e.g., Crew Members)
2. View at 375px width
3. Check for scroll indicators on tables
4. Scroll table horizontally
5. Verify indicators appear/disappear correctly

### Expected Results
- [ ] Left gradient appears when content scrollable to left
- [ ] Right gradient appears when content scrollable to right
- [ ] Indicators disappear when at scroll boundaries
- [ ] Smooth scrolling with touch/swipe
- [ ] No indicators on desktop (>768px)

---

## Task 4: CrewMemberList.vue Mobile ✓

### What to Test
- Card view on mobile
- Table view with horizontal scroll
- Filter controls stacking
- Action button accessibility

### Test Steps
1. Navigate to Crew Members page at 375px
2. Verify default view (card or table)
3. Test view toggle if present
4. Test filter controls
5. Test action buttons (Edit, Delete)
6. Scroll through list

### Expected Results
- [ ] Card view displays properly on mobile (if default)
- [ ] Table scrolls horizontally with indicators (if table view)
- [ ] Filter controls stack vertically
- [ ] All filter inputs are full-width
- [ ] Action buttons are easily tappable (44x44px)
- [ ] No horizontal viewport overflow
- [ ] Reduced card padding on mobile
- [ ] Search input is full-width

### Test Interactions
- [ ] Add new crew member button works
- [ ] Edit button opens modal
- [ ] Delete button works
- [ ] Filter/search functionality works

---

## Task 5: CrewMemberForm.vue Mobile ✓

### What to Test
- Form field stacking
- Input heights and touch targets
- iOS zoom prevention
- Modal fit

### Test Steps
1. Open crew member form (click Add/Edit) at 375px
2. Check form layout
3. Test all input fields
4. Try typing in inputs (check for iOS zoom)
5. Test form submission
6. Test in modal context

### Expected Results
- [ ] All form fields stack vertically
- [ ] All inputs are at least 44px tall
- [ ] Input font-size is 16px (no iOS zoom on focus)
- [ ] Button groups stack vertically
- [ ] Form fits in modal viewport
- [ ] Reduced form padding on mobile
- [ ] Labels remain visible and associated with inputs
- [ ] Adequate spacing between fields

### Test Form Validation
- [ ] Required field validation works
- [ ] Error messages display properly
- [ ] Submit button is easily tappable

---

## Task 6: Modal Components Mobile ✓

### What to Test
- Modal sizing on mobile
- Modal scrolling
- Close button accessibility
- Body scroll prevention

### Test Steps
1. Open any modal at 375px width
2. Check modal fits viewport
3. Test with long content (scroll)
4. Test close button
5. Try scrolling page behind modal
6. Test on different modal types

### Expected Results
- [ ] Modal fits viewport with margins
- [ ] Modal max-height is 90vh or less
- [ ] Vertical scrolling works in modal body
- [ ] Close button is 44x44px minimum
- [ ] Body scroll is prevented when modal open
- [ ] Modal content doesn't exceed viewport width
- [ ] Modal appears from bottom on mobile (slide up)
- [ ] Modal is centered on tablet/desktop

### Test Multiple Modals
- [ ] CrewMemberForm modal
- [ ] BoatRegistrationForm modal (if accessible)
- [ ] Any confirmation dialogs

---

## Cross-Component Testing

### Navigation Flow
1. Start at home page (375px)
2. Navigate to Crew Members
3. Open crew member form
4. Submit form
5. Navigate to other pages
6. Test back button

### Expected Results
- [ ] Smooth navigation between pages
- [ ] No layout shifts during navigation
- [ ] Consistent header across pages
- [ ] Consistent spacing and styling

---

## Viewport Testing Matrix

Test each component at these widths:

| Component | 375px | 390px | 414px | 768px | 1024px |
|-----------|-------|-------|-------|-------|--------|
| App Header | [ ] | [ ] | [ ] | [ ] | [ ] |
| CrewMemberList | [ ] | [ ] | [ ] | [ ] | [ ] |
| CrewMemberForm | [ ] | [ ] | [ ] | [ ] | [ ] |
| Modals | [ ] | [ ] | [ ] | [ ] | [ ] |
| Table Scroll | [ ] | [ ] | [ ] | [ ] | [ ] |

---

## Accessibility Checks

### Touch Targets
- [ ] All buttons are at least 44x44px
- [ ] Adequate spacing between tappable elements (8px min)
- [ ] Links and buttons are easily tappable

### Typography
- [ ] Body text is at least 16px
- [ ] Headings scale appropriately
- [ ] Text is readable without zoom
- [ ] Adequate line height

### Visual Feedback
- [ ] Buttons show active/pressed state
- [ ] Form inputs show focus state
- [ ] Loading states are visible
- [ ] Error messages are prominent

---

## Performance Checks

### Loading
- [ ] Pages load quickly on mobile
- [ ] No layout shifts during load
- [ ] Images load appropriately

### Scrolling
- [ ] Smooth scrolling performance
- [ ] No janky animations
- [ ] Touch scrolling feels natural

---

## Common Issues to Watch For

### Layout Issues
- ❌ Horizontal scroll on viewport
- ❌ Content cut off at edges
- ❌ Overlapping elements
- ❌ Text too small to read

### Interaction Issues
- ❌ Buttons too small to tap
- ❌ iOS zoom on input focus
- ❌ Dropdowns positioned off-screen
- ❌ Modal doesn't fit viewport

### Styling Issues
- ❌ Inconsistent spacing
- ❌ Wrong breakpoint behavior
- ❌ Missing mobile styles
- ❌ Desktop styles on mobile

---

## Actual Device Testing (If Available)

### iOS Safari
1. Open app on iPhone
2. Test in portrait orientation
3. Test in landscape orientation
4. Check for iOS-specific issues

### Android Chrome
1. Open app on Android device
2. Test in portrait orientation
3. Test in landscape orientation
4. Check for Android-specific issues

### Device-Specific Checks
- [ ] Touch interactions feel natural
- [ ] Scrolling is smooth
- [ ] Keyboard doesn't break layout
- [ ] Safe area insets respected (notch devices)

---

## Reporting Issues

If you find any issues during testing, note:
1. **Component/Page**: Which component has the issue
2. **Viewport Width**: At what width does it occur
3. **Description**: What's wrong
4. **Expected**: What should happen
5. **Screenshot**: If possible

---

## Sign-Off

Once all tests pass:
- [ ] All core components tested at mobile widths
- [ ] No horizontal scroll issues
- [ ] All touch targets meet 44x44px minimum
- [ ] Forms work properly on mobile
- [ ] Modals fit viewport correctly
- [ ] Table patterns work as expected
- [ ] Ready to proceed to Task 8 (Admin pages)

**Tester Name**: _______________
**Date**: _______________
**Notes**: _______________
