# Mobile Testing Checklist

## Overview

Use this checklist when developing or modifying components to ensure mobile responsiveness and accessibility compliance.

---

## Quick Reference

### Breakpoints
- **Mobile:** < 768px
- **Tablet:** 768px - 1024px
- **Desktop:** > 1024px

### Touch Targets
- **Minimum:** 44x44 CSS pixels
- **Spacing:** 8px minimum between targets

### Typography
- **Body text:** 16px minimum
- **Input text:** 16px (prevents iOS zoom)

---

## Pre-Development Checklist

Before starting development:

- [ ] Review mobile responsiveness guide
- [ ] Check existing responsive patterns
- [ ] Identify which breakpoints will be affected
- [ ] Plan mobile-first approach
- [ ] Consider touch interactions

---

## During Development Checklist

### Layout & Structure

- [ ] Start with mobile styles (no media query)
- [ ] Use flexbox or grid for layouts
- [ ] Stack content vertically on mobile
- [ ] Use `min-width` media queries for enhancements
- [ ] Avoid fixed widths (use max-width instead)
- [ ] Set `max-width: 100%` on containers
- [ ] Use relative units (rem, %, vh/vw) over px

### Touch Targets

- [ ] All buttons minimum 44x44px
- [ ] All links minimum 44px height
- [ ] All form inputs minimum 44px height
- [ ] Icon buttons minimum 44x44px
- [ ] Adequate spacing between targets (8px+)
- [ ] Full-width buttons on mobile where appropriate

### Typography

- [ ] Body text minimum 16px on mobile
- [ ] Input font-size 16px (prevents iOS zoom)
- [ ] Headings scale appropriately for mobile
- [ ] Line height comfortable (1.5+)
- [ ] Text color contrast meets WCAG AA (4.5:1)

### Forms

- [ ] All fields stack vertically on mobile
- [ ] Labels visible and associated with inputs
- [ ] Input height minimum 44px
- [ ] Input font-size 16px
- [ ] Buttons full-width on mobile
- [ ] Validation messages visible
- [ ] Form fits in modal on mobile (if applicable)

### Modals

- [ ] Modal fits viewport (max-height: 90vh)
- [ ] Bottom sheet style on mobile
- [ ] Centered on tablet/desktop
- [ ] Close button 44x44px
- [ ] Scrolling enabled when needed
- [ ] Body scroll prevented when modal open
- [ ] No horizontal scroll within modal

### Tables

- [ ] Card view OR horizontal scroll on mobile
- [ ] Scroll indicators if using horizontal scroll
- [ ] Filter controls stack vertically on mobile
- [ ] Action buttons properly sized (44x44px)
- [ ] Pagination controls mobile-optimized

### Navigation

- [ ] Hamburger menu functional on mobile
- [ ] Navigation items minimum 44px height
- [ ] Logo visible on mobile
- [ ] User menu accessible
- [ ] Language switcher accessible
- [ ] No overlap or crowding

### Images & Media

- [ ] Images have width/height attributes
- [ ] Images use max-width: 100%
- [ ] Lazy loading implemented where appropriate
- [ ] Alt text provided for accessibility
- [ ] Responsive images (srcset) if needed

### Animations

- [ ] Use CSS transforms (not layout properties)
- [ ] Duration < 300ms for mobile
- [ ] 60 FPS performance
- [ ] Reduced motion support
- [ ] No hover-only animations on mobile
- [ ] Active states for touch feedback

### Interactions

- [ ] No hover-only interactions
- [ ] Active states for touch feedback
- [ ] Tap highlight removed (-webkit-tap-highlight-color)
- [ ] No gesture-only interactions
- [ ] All actions available via tap

---

## Testing Checklist

### Viewport Testing

Test at these specific widths:

- [ ] **375px** - iPhone SE (smallest common)
- [ ] **390px** - iPhone 12/13/14 (most common)
- [ ] **414px** - iPhone Plus models
- [ ] **768px** - iPad Portrait
- [ ] **1024px** - iPad Landscape

### Orientation Testing

- [ ] Portrait orientation works
- [ ] Landscape orientation works
- [ ] Smooth transition between orientations
- [ ] Content adapts appropriately
- [ ] No layout breaks in landscape

### Horizontal Scroll Testing

- [ ] No unwanted horizontal scroll at 375px
- [ ] No unwanted horizontal scroll at 390px
- [ ] No unwanted horizontal scroll at 414px
- [ ] Intentional table scroll has indicators
- [ ] All content fits within viewport

### Touch Target Testing

- [ ] All buttons meet 44x44px minimum
- [ ] All links meet 44px height minimum
- [ ] All form inputs meet 44px height minimum
- [ ] Icon buttons meet 44x44px minimum
- [ ] Adequate spacing between targets (8px+)
- [ ] Easy to tap without precision

### Typography Testing

- [ ] Text readable without zoom
- [ ] Input focus doesn't trigger iOS zoom
- [ ] Headings properly sized
- [ ] Line height comfortable
- [ ] Color contrast sufficient

### Form Testing

- [ ] All fields accessible on mobile
- [ ] Can fill out entire form
- [ ] Validation works
- [ ] Submit button accessible
- [ ] Keyboard doesn't obscure fields
- [ ] Form submission works

### Modal Testing

- [ ] Modal opens properly
- [ ] Modal fits viewport
- [ ] Can scroll modal content
- [ ] Close button accessible
- [ ] Can interact with form (if applicable)
- [ ] Modal closes properly

### Navigation Testing

- [ ] Hamburger menu opens/closes
- [ ] All nav items accessible
- [ ] Logo visible and clickable
- [ ] User menu works
- [ ] Language switcher works
- [ ] No overlap or crowding

### Performance Testing

- [ ] Page loads in < 3s on 3G
- [ ] No layout shifts (CLS < 0.1)
- [ ] Animations smooth (60 FPS)
- [ ] No jank or stuttering
- [ ] Scroll performance smooth

---

## Browser Testing

### Required Browsers

- [ ] **Chrome Mobile** (Android)
- [ ] **Safari** (iOS)
- [ ] **Firefox Mobile** (optional)

### Testing Methods

- [ ] Chrome DevTools device emulation
- [ ] Firefox Responsive Design Mode
- [ ] Safari Responsive Design Mode
- [ ] Actual mobile device (preferred)

---

## Accessibility Testing

### Touch Targets

- [ ] All interactive elements 44x44px minimum
- [ ] Adequate spacing (8px+)
- [ ] Clear visual feedback on interaction

### Color Contrast

- [ ] Text contrast meets WCAG AA (4.5:1)
- [ ] Large text contrast meets WCAG AA (3:1)
- [ ] Button contrast sufficient
- [ ] Focus indicators visible (3:1)

### Semantic HTML

- [ ] Proper heading hierarchy
- [ ] Form labels associated
- [ ] ARIA attributes where needed
- [ ] Landmark regions defined
- [ ] Buttons vs links used correctly

### Keyboard Navigation (Tablet)

- [ ] Logical tab order
- [ ] Focus indicators visible
- [ ] No keyboard traps
- [ ] All interactive elements reachable

### Screen Reader (Optional)

- [ ] Test with VoiceOver (iOS)
- [ ] Test with TalkBack (Android)
- [ ] All content announced correctly
- [ ] Form labels read properly

---

## Post-Development Checklist

### Code Review

- [ ] Mobile-first approach used
- [ ] Consistent breakpoints (768px, 1024px)
- [ ] No duplicate media queries
- [ ] CSS organized and clean
- [ ] Comments added where needed

### Documentation

- [ ] Component documented
- [ ] Mobile considerations noted
- [ ] Responsive patterns explained
- [ ] Edge cases documented

### Performance

- [ ] No unnecessary CSS
- [ ] No unused styles
- [ ] Animations optimized
- [ ] Images optimized

---

## Common Issues Checklist

### If horizontal scroll appears:

- [ ] Check for fixed widths
- [ ] Check for large padding/margins
- [ ] Check for viewport units (vw)
- [ ] Add `max-width: 100%` to containers
- [ ] Add `overflow-x: hidden` if needed

### If iOS zooms on input focus:

- [ ] Set input font-size to 16px
- [ ] Set select font-size to 16px
- [ ] Set textarea font-size to 16px

### If touch targets too small:

- [ ] Add `min-height: 44px`
- [ ] Add `min-width: 44px`
- [ ] Increase padding
- [ ] Add spacing between targets

### If modal extends beyond viewport:

- [ ] Set `max-height: 90vh`
- [ ] Add `overflow-y: auto`
- [ ] Set `width: 100%` on mobile
- [ ] Set `max-width: 100%` on mobile

### If hover effects stick on mobile:

- [ ] Remove hover styles from base
- [ ] Add hover only in desktop media query
- [ ] Add active state for touch feedback
- [ ] Remove tap highlight

### If table overflows:

- [ ] Implement card view on mobile
- [ ] OR add horizontal scroll with indicators
- [ ] Stack filter controls vertically
- [ ] Ensure action buttons sized properly

---

## Quick Test Commands

### Start Dev Server
```bash
cd frontend
npm run dev
```

### Open in Browser
- Navigate to `http://localhost:5173`
- Open DevTools (F12)
- Toggle device toolbar (Ctrl+Shift+M)

### Test Viewports
1. Select device from dropdown
2. Or enter custom width (375, 390, 414, 768, 1024)
3. Test in portrait and landscape
4. Check for horizontal scroll
5. Test all interactions

---

## Sign-Off Checklist

Before marking work complete:

- [ ] All viewport sizes tested
- [ ] Both orientations tested
- [ ] No horizontal scroll
- [ ] All touch targets meet minimum
- [ ] Typography readable
- [ ] Forms functional
- [ ] Modals functional
- [ ] Navigation functional
- [ ] Performance acceptable
- [ ] Accessibility compliant
- [ ] Code reviewed
- [ ] Documentation updated

---

## Resources

- [Mobile Responsiveness Guide](./mobile-responsiveness-guide.md)
- [Responsive Design Guide](./responsive-design.md)
- [Responsive Table Patterns](./responsive-table-patterns.md)
- [Testing Guide](./testing-guide.md)

---

**Last Updated:** December 22, 2025
**Version:** 1.0
