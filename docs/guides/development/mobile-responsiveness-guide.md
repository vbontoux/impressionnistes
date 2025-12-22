# Mobile Responsiveness Guide

## Overview

This guide documents the mobile responsiveness patterns and best practices used throughout the Course des Impressionnistes registration system. All components follow a mobile-first approach with consistent breakpoints and touch-optimized interactions.

## Table of Contents

1. [Responsive Breakpoints](#responsive-breakpoints)
2. [Mobile-First Approach](#mobile-first-approach)
3. [Common Patterns](#common-patterns)
4. [Touch Target Guidelines](#touch-target-guidelines)
5. [Component Examples](#component-examples)
6. [Testing Checklist](#testing-checklist)
7. [Troubleshooting](#troubleshooting)

---

## Responsive Breakpoints

### Standard Breakpoints

```css
/* Mobile: Base styles (no media query) */
/* Applies to: < 768px */

/* Tablet: Medium screens */
@media (min-width: 768px) {
  /* Tablet styles */
}

/* Desktop: Large screens */
@media (min-width: 1024px) {
  /* Desktop styles */
}
```

### Why These Breakpoints?

- **768px**: Common tablet portrait width, separates mobile from tablet
- **1024px**: Common tablet landscape width, separates tablet from desktop
- **Mobile-first**: Base styles target mobile, enhanced for larger screens

### Usage in Components

```vue
<style scoped>
/* Mobile styles (default) */
.container {
  padding: 1rem;
  flex-direction: column;
}

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    padding: 2rem;
    flex-direction: row;
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
    margin: 0 auto;
  }
}
</style>
```

---

## Mobile-First Approach

### Principles

1. **Start with mobile**: Write base styles for mobile devices
2. **Progressive enhancement**: Add features for larger screens
3. **Content priority**: Most important content first on mobile
4. **Touch-optimized**: All interactions designed for touch

### Example: Button Styling

```css
/* Mobile-first button */
.btn {
  /* Mobile base styles */
  width: 100%;
  padding: 0.875rem 1.5rem;
  min-height: 44px;
  font-size: 1rem;
}

/* Desktop enhancement */
@media (min-width: 768px) {
  .btn {
    width: auto;
    padding: 0.75rem 2rem;
  }
  
  .btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
}
```

---

## Common Patterns

### 1. Responsive Forms

**Pattern**: Stack fields vertically on mobile, side-by-side on desktop

```vue
<template>
  <form class="responsive-form">
    <div class="form-row">
      <div class="form-group">
        <label>First Name</label>
        <input type="text" />
      </div>
      <div class="form-group">
        <label>Last Name</label>
        <input type="text" />
      </div>
    </div>
  </form>
</template>

<style scoped>
/* Mobile: Stack vertically */
.form-row {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group input {
  width: 100%;
  min-height: 44px;
  font-size: 16px; /* Prevents iOS zoom */
}

/* Desktop: Side by side */
@media (min-width: 768px) {
  .form-row {
    flex-direction: row;
  }
  
  .form-group {
    flex: 1;
  }
}
</style>
```

### 2. Responsive Modals

**Pattern**: Bottom sheet on mobile, centered on desktop

```vue
<style scoped>
/* Mobile: Bottom sheet */
.modal-overlay {
  align-items: flex-end;
  padding: 0;
}

.modal-content {
  width: 100%;
  max-height: 90vh;
  border-radius: 12px 12px 0 0;
  padding: 1.5rem;
}

/* Desktop: Centered */
@media (min-width: 768px) {
  .modal-overlay {
    align-items: center;
    padding: 1rem;
  }
  
  .modal-content {
    width: 90%;
    max-width: 600px;
    border-radius: 12px;
    padding: 2rem;
  }
}
</style>
```

### 3. Responsive Tables

**Pattern**: Card view on mobile, table on desktop

```vue
<template>
  <!-- Mobile: Card view -->
  <div class="card-list mobile-only">
    <div v-for="item in items" :key="item.id" class="card">
      <!-- Card content -->
    </div>
  </div>
  
  <!-- Desktop: Table view -->
  <div class="table-container desktop-only">
    <table>
      <!-- Table content -->
    </table>
  </div>
</template>

<style scoped>
/* Mobile: Show cards, hide table */
.mobile-only {
  display: block;
}

.desktop-only {
  display: none;
}

/* Desktop: Show table, hide cards */
@media (min-width: 768px) {
  .mobile-only {
    display: none;
  }
  
  .desktop-only {
    display: block;
  }
}
</style>
```

### 4. Responsive Card Grids

**Pattern**: Single column on mobile, multi-column on larger screens

```css
/* Mobile: Single column */
.card-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

/* Tablet: Two columns */
@media (min-width: 768px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
}

/* Desktop: Three columns */
@media (min-width: 1024px) {
  .card-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### 5. Responsive Navigation

**Pattern**: Hamburger menu on mobile, full nav on desktop

```vue
<template>
  <header class="header">
    <!-- Mobile: Hamburger -->
    <button class="hamburger mobile-only" @click="toggleMenu">
      ☰
    </button>
    
    <!-- Desktop: Full nav -->
    <nav class="nav desktop-only">
      <a href="#">Link 1</a>
      <a href="#">Link 2</a>
    </nav>
  </header>
</template>

<style scoped>
.hamburger {
  min-width: 44px;
  min-height: 44px;
}

.mobile-only {
  display: block;
}

.desktop-only {
  display: none;
}

@media (min-width: 768px) {
  .mobile-only {
    display: none;
  }
  
  .desktop-only {
    display: flex;
  }
}
</style>
```

---

## Touch Target Guidelines

### Minimum Sizes

**WCAG 2.1 Level AAA**: 44x44 CSS pixels

```css
/* All interactive elements */
button,
a,
input,
select,
textarea {
  min-height: 44px;
  min-width: 44px;
}

/* Buttons */
.btn {
  min-height: 44px;
  padding: 0.875rem 1.5rem;
}

/* Form inputs */
input,
select,
textarea {
  min-height: 44px;
  padding: 0.75rem;
  font-size: 16px; /* Prevents iOS zoom */
}

/* Icon buttons */
.icon-btn {
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

### Spacing Between Targets

**Minimum**: 8px between touch targets

```css
/* Button groups */
.button-group {
  display: flex;
  gap: 0.5rem; /* 8px minimum */
}

/* Form fields */
.form-group {
  margin-bottom: 0.75rem; /* 12px */
}

/* Navigation items */
.nav-items {
  display: flex;
  gap: 0.5rem; /* 8px minimum */
}
```

### Touch Feedback

```css
/* Mobile: Active state (no hover) */
.btn:active {
  background-color: #45a049;
  transform: scale(0.98);
}

/* Desktop: Hover state */
@media (min-width: 768px) {
  .btn:hover {
    background-color: #45a049;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
}

/* Remove tap highlight */
.btn {
  -webkit-tap-highlight-color: transparent;
}
```

---

## Component Examples

### Responsive Button Component

```vue
<template>
  <button class="responsive-btn" :class="variant">
    <slot></slot>
  </button>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary'
  }
});
</script>

<style scoped>
/* Mobile-first */
.responsive-btn {
  width: 100%;
  min-height: 44px;
  padding: 0.875rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.responsive-btn:active {
  transform: scale(0.98);
}

.primary {
  background-color: #4CAF50;
  color: white;
}

.primary:active {
  background-color: #45a049;
}

/* Desktop enhancements */
@media (min-width: 768px) {
  .responsive-btn {
    width: auto;
    padding: 0.75rem 2rem;
  }
  
  .primary:hover {
    background-color: #45a049;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
  }
  
  .primary:active {
    transform: translateY(0);
  }
}
</style>
```

### Responsive Card Component

```vue
<template>
  <div class="responsive-card">
    <slot></slot>
  </div>
</template>

<style scoped>
/* Mobile */
.responsive-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Desktop */
@media (min-width: 768px) {
  .responsive-card {
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .responsive-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }
}
</style>
```

---

## Testing Checklist

### Before Committing Changes

- [ ] Test at 375px width (iPhone SE)
- [ ] Test at 390px width (iPhone 12/13/14)
- [ ] Test at 414px width (iPhone Plus)
- [ ] Test at 768px width (iPad portrait)
- [ ] Test at 1024px width (iPad landscape)
- [ ] Verify no horizontal scroll on mobile
- [ ] Check all touch targets are 44x44px minimum
- [ ] Test in portrait orientation
- [ ] Test in landscape orientation
- [ ] Verify input font-size is 16px (no iOS zoom)
- [ ] Test with Chrome DevTools mobile emulation
- [ ] Check hover effects only on desktop
- [ ] Verify active states on mobile

### Accessibility Checks

- [ ] All buttons meet 44x44px minimum
- [ ] All form inputs meet 44px height minimum
- [ ] Adequate spacing between touch targets (8px+)
- [ ] Color contrast ratios meet WCAG AA
- [ ] Focus indicators visible
- [ ] Semantic HTML used
- [ ] Form labels associated with inputs

### Performance Checks

- [ ] No layout shifts during load (CLS < 0.1)
- [ ] Animations run at 60 FPS
- [ ] Page loads in < 3s on 3G
- [ ] Images lazy-loaded where appropriate
- [ ] CSS transforms used for animations

---

## Troubleshooting

### Issue: Horizontal Scroll on Mobile

**Symptoms**: Content extends beyond viewport width

**Solutions**:
```css
/* Add to container */
.container {
  max-width: 100%;
  overflow-x: hidden;
}

/* Check for fixed widths */
.element {
  width: 100%; /* Not: width: 1200px; */
  max-width: 1200px;
}

/* Check for large padding/margins */
.element {
  padding: 1rem; /* Not: padding: 100px; */
}
```

### Issue: iOS Auto-Zoom on Input Focus

**Symptoms**: Page zooms in when tapping input fields

**Solution**:
```css
/* Set input font-size to 16px minimum */
input,
select,
textarea {
  font-size: 16px; /* Prevents zoom */
}
```

### Issue: Touch Targets Too Small

**Symptoms**: Buttons hard to tap on mobile

**Solution**:
```css
/* Ensure minimum 44x44px */
button,
a {
  min-height: 44px;
  min-width: 44px;
  padding: 0.75rem 1rem;
}
```

### Issue: Modal Extends Beyond Viewport

**Symptoms**: Modal content cut off on mobile

**Solution**:
```css
.modal-content {
  max-height: 90vh;
  overflow-y: auto;
  width: 100%;
  max-width: 100%;
}
```

### Issue: Hover Effects on Mobile

**Symptoms**: Hover states stick on mobile after tap

**Solution**:
```css
/* Remove hover on mobile */
.element {
  /* No hover styles here */
}

/* Add hover only on desktop */
@media (min-width: 768px) {
  .element:hover {
    /* Hover styles here */
  }
}

/* Use active state on mobile */
.element:active {
  /* Touch feedback */
}
```

### Issue: Table Overflow on Mobile

**Symptoms**: Table extends beyond viewport

**Solutions**:

**Option 1: Card View**
```vue
<template>
  <div class="mobile-only">
    <!-- Card layout -->
  </div>
  <div class="desktop-only">
    <!-- Table layout -->
  </div>
</template>
```

**Option 2: Horizontal Scroll**
```css
.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.table {
  min-width: 800px;
}
```

---

## Utilities and Helpers

### Responsive Composable

Use `useResponsive()` composable for JavaScript-based responsive logic:

```vue
<script setup>
import { useResponsive } from '@/composables/useResponsive';

const { isMobile, isTablet, isDesktop } = useResponsive();
</script>

<template>
  <div v-if="isMobile">Mobile view</div>
  <div v-else-if="isTablet">Tablet view</div>
  <div v-else>Desktop view</div>
</template>
```

### Responsive Utility Classes

Available in `frontend/src/assets/responsive.css`:

```css
/* Visibility utilities */
.mobile-only { /* Visible only on mobile */ }
.tablet-only { /* Visible only on tablet */ }
.desktop-only { /* Visible only on desktop */ }

/* Layout utilities */
.stack-mobile { /* Stack vertically on mobile */ }
.full-width-mobile { /* Full width on mobile */ }
```

---

## Best Practices Summary

### Do's ✅

- ✅ Start with mobile styles
- ✅ Use min-width media queries
- ✅ Ensure 44x44px touch targets
- ✅ Set input font-size to 16px
- ✅ Use CSS transforms for animations
- ✅ Test on actual devices
- ✅ Provide touch feedback (active states)
- ✅ Stack content vertically on mobile
- ✅ Use flexbox and grid for layouts
- ✅ Lazy load images

### Don'ts ❌

- ❌ Don't use fixed widths
- ❌ Don't use max-width media queries
- ❌ Don't make touch targets < 44px
- ❌ Don't use hover-only interactions
- ❌ Don't animate layout properties
- ❌ Don't forget landscape testing
- ❌ Don't use small font sizes (< 16px on inputs)
- ❌ Don't create horizontal scroll
- ❌ Don't skip accessibility testing
- ❌ Don't assume desktop-first

---

## Resources

### Internal Documentation
- [Responsive Design Guide](./responsive-design.md)
- [Responsive Table Patterns](./responsive-table-patterns.md)
- [Testing Guide](./testing-guide.md)

### External Resources
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
- [CSS Tricks: A Complete Guide to Flexbox](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)
- [CSS Tricks: A Complete Guide to Grid](https://css-tricks.com/snippets/css/complete-guide-grid/)

---

**Last Updated:** December 22, 2025
**Maintained by:** Development Team
