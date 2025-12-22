# Responsive Design Guide

This guide documents the responsive design utilities and patterns available in the application.

## Table of Contents

1. [Breakpoints](#breakpoints)
2. [JavaScript Utilities](#javascript-utilities)
3. [Vue Composables](#vue-composables)
4. [CSS Utility Classes](#css-utility-classes)
5. [Common Patterns](#common-patterns)
6. [Best Practices](#best-practices)

---

## Breakpoints

Standard breakpoint values used throughout the application:

| Breakpoint | Min Width | Max Width | Description |
|------------|-----------|-----------|-------------|
| Mobile     | 0px       | 767px     | Smartphones |
| Tablet     | 768px     | 1023px    | Tablets |
| Desktop    | 1024px    | 1199px    | Desktop screens |
| XL Desktop | 1200px    | ∞         | Large desktop screens |

### Mobile-First Approach

Base styles target mobile devices. Use media queries to enhance for larger screens:

```css
/* Base styles for mobile */
.element {
  padding: 1rem;
}

/* Enhance for tablet and up */
@media (min-width: 768px) {
  .element {
    padding: 2rem;
  }
}
```

---

## JavaScript Utilities

Import from `@/utils/responsive.js`:

```javascript
import { 
  BREAKPOINTS, 
  MEDIA_QUERIES,
  TOUCH_TARGET_MIN,
  MIN_INPUT_FONT_SIZE,
  matchesBreakpoint,
  getCurrentBreakpoint
} from '@/utils/responsive'
```

### Constants

```javascript
// Breakpoint values
BREAKPOINTS.MOBILE      // 0
BREAKPOINTS.TABLET      // 768
BREAKPOINTS.DESKTOP     // 1024
BREAKPOINTS.XL_DESKTOP  // 1200

// Accessibility constants
TOUCH_TARGET_MIN        // 44px (minimum touch target size)
MIN_INPUT_FONT_SIZE     // 16px (prevents iOS zoom)
```

### Helper Functions

```javascript
// Check if viewport matches a breakpoint
if (matchesBreakpoint('mobile')) {
  // Mobile-specific logic
}

// Get current breakpoint name
const breakpoint = getCurrentBreakpoint() // 'mobile', 'tablet', 'desktop', or 'xl-desktop'
```

---

## Vue Composables

Import from `@/composables/useResponsive.js`:

### useResponsive()

Full-featured responsive detection:

```vue
<script setup>
import { useResponsive } from '@/composables/useResponsive'

const { 
  isMobile, 
  isTablet, 
  isDesktop, 
  isXlDesktop,
  currentBreakpoint,
  viewportWidth 
} = useResponsive()
</script>

<template>
  <div v-if="isMobile">
    Mobile view
  </div>
  <div v-else-if="isTablet">
    Tablet view
  </div>
  <div v-else>
    Desktop view
  </div>
</template>
```

### useIsMobile()

Simplified mobile detection:

```vue
<script setup>
import { useIsMobile } from '@/composables/useResponsive'

const { isMobile } = useIsMobile()
</script>

<template>
  <div :class="{ 'mobile-layout': isMobile }">
    Content
  </div>
</template>
```

### useOrientation()

Detect portrait/landscape orientation:

```vue
<script setup>
import { useOrientation } from '@/composables/useResponsive'

const { isPortrait, isLandscape } = useOrientation()
</script>

<template>
  <div v-if="isLandscape" class="landscape-warning">
    Please rotate your device for the best experience
  </div>
</template>
```

---

## CSS Utility Classes

Import in your component:

```vue
<style scoped>
@import '@/assets/responsive.css';
</style>
```

### Visibility Classes

```html
<!-- Hide on mobile, show on tablet+ -->
<div class="mobile-hidden">Desktop content</div>

<!-- Show on mobile only -->
<div class="mobile-only">Mobile content</div>

<!-- Show on tablet only -->
<div class="tablet-only">Tablet content</div>

<!-- Show on desktop only -->
<div class="desktop-only">Desktop content</div>
```

### Layout Classes

```html
<!-- Responsive container with max-width -->
<div class="responsive-container">
  Content
</div>

<!-- Stack vertically on mobile, horizontal on tablet+ -->
<div class="responsive-stack">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<!-- Responsive grid: 1 col mobile, 2 tablet, 3 desktop -->
<div class="responsive-grid">
  <div>Card 1</div>
  <div>Card 2</div>
  <div>Card 3</div>
</div>
```

### Form Classes

```html
<!-- Responsive form input -->
<input type="text" class="responsive-input" />

<!-- Form row that stacks on mobile -->
<div class="responsive-form-row">
  <div class="responsive-form-group">
    <label>First Name</label>
    <input type="text" class="responsive-input" />
  </div>
  <div class="responsive-form-group">
    <label>Last Name</label>
    <input type="text" class="responsive-input" />
  </div>
</div>
```

### Touch Target Classes

```html
<!-- Ensure minimum 44x44px touch target -->
<button class="touch-button">
  Click me
</button>

<!-- Generic touch target wrapper -->
<div class="touch-target">
  <a href="#">Link</a>
</div>
```

### Table Classes

```html
<!-- Responsive table with horizontal scroll on mobile -->
<div class="responsive-table-wrapper">
  <table class="responsive-table">
    <!-- Table content -->
  </table>
</div>
```

### Card Classes

```html
<!-- Responsive card -->
<div class="responsive-card">
  Card content
</div>

<!-- Card list (single column on mobile) -->
<div class="responsive-card-list">
  <div class="responsive-card">Card 1</div>
  <div class="responsive-card">Card 2</div>
  <div class="responsive-card">Card 3</div>
</div>
```

---

## Common Patterns

### Pattern 1: Responsive Table

We provide two strategies for responsive tables. For detailed documentation, see [responsive-table-patterns.md](./responsive-table-patterns.md).

**Strategy A: Card Conversion (Preferred for complex tables)**

```vue
<template>
  <!-- Desktop: Table view -->
  <div class="desktop-only">
    <table class="data-table">
      <!-- Table markup -->
    </table>
  </div>
  
  <!-- Mobile: Card view -->
  <div class="mobile-only responsive-card-list">
    <div v-for="item in items" :key="item.id" class="responsive-card">
      <!-- Card layout -->
    </div>
  </div>
</template>
```

**Strategy B: Horizontal Scroll with Indicators (For simple tables)**

```vue
<template>
  <TableScrollIndicator>
    <table class="data-table">
      <!-- Table content -->
    </table>
  </TableScrollIndicator>
</template>

<script setup>
import TableScrollIndicator from '@/components/TableScrollIndicator.vue'
</script>
```

**See [responsive-table-patterns.md](./responsive-table-patterns.md) for:**
- Detailed implementation examples
- When to use each strategy
- Best practices and accessibility
- Common issues and solutions

### Pattern 2: Responsive Form

```vue
<template>
  <form class="responsive-form">
    <div class="responsive-form-row">
      <div class="responsive-form-group">
        <label>Field 1</label>
        <input type="text" class="responsive-input" />
      </div>
      <div class="responsive-form-group">
        <label>Field 2</label>
        <input type="text" class="responsive-input" />
      </div>
    </div>
  </form>
</template>

<style scoped>
@import '@/assets/responsive.css';

.responsive-form {
  padding: 1rem;
}

@media (min-width: 768px) {
  .responsive-form {
    padding: 2rem;
  }
}
</style>
```

### Pattern 3: Responsive Modal

```vue
<template>
  <div class="responsive-modal-overlay" @click.self="close">
    <div class="responsive-modal-content">
      <div class="modal-header">
        <h2>{{ title }}</h2>
        <button class="touch-button" @click="close">×</button>
      </div>
      <div class="modal-body">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import '@/assets/responsive.css';

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-body {
  padding: 1rem;
  overflow-y: auto;
  flex: 1;
}

@media (min-width: 768px) {
  .modal-header,
  .modal-body {
    padding: 1.5rem;
  }
}
</style>
```

### Pattern 4: Conditional Rendering

```vue
<script setup>
import { useIsMobile } from '@/composables/useResponsive'

const { isMobile } = useIsMobile()
</script>

<template>
  <!-- Different markup for mobile vs desktop -->
  <div v-if="isMobile" class="mobile-view">
    <!-- Simplified mobile UI -->
  </div>
  <div v-else class="desktop-view">
    <!-- Full desktop UI -->
  </div>
</template>
```

---

## Best Practices

### 1. Mobile-First CSS

Always write base styles for mobile, then enhance for larger screens:

```css
/* ✅ Good: Mobile-first */
.element {
  padding: 1rem;
}

@media (min-width: 768px) {
  .element {
    padding: 2rem;
  }
}

/* ❌ Bad: Desktop-first */
.element {
  padding: 2rem;
}

@media (max-width: 767px) {
  .element {
    padding: 1rem;
  }
}
```

### 2. Touch Targets

Ensure all interactive elements are at least 44x44px:

```css
button, a, input[type="checkbox"] {
  min-width: 44px;
  min-height: 44px;
}
```

### 3. Prevent iOS Zoom

Use 16px minimum font size on inputs:

```css
input, select, textarea {
  font-size: 16px; /* Prevents zoom on iOS */
}
```

### 4. Avoid Fixed Widths

Use max-width instead of width:

```css
/* ✅ Good */
.container {
  width: 100%;
  max-width: 1200px;
}

/* ❌ Bad */
.container {
  width: 1200px;
}
```

### 5. Use Flexbox and Grid

Modern layout tools handle responsiveness better:

```css
.layout {
  display: flex;
  flex-direction: column;
}

@media (min-width: 768px) {
  .layout {
    flex-direction: row;
  }
}
```

### 6. Test on Real Devices

Always test on actual mobile devices, not just browser emulation:

- iOS Safari (iPhone)
- Chrome Mobile (Android)
- Different screen sizes (375px, 390px, 414px)
- Portrait and landscape orientations

### 7. Performance

- Debounce resize handlers (already done in composables)
- Use CSS transforms for animations (better performance)
- Lazy load images on mobile
- Minimize JavaScript execution on resize

### 8. Accessibility

- Maintain color contrast ratios
- Ensure keyboard navigation works
- Test with screen readers
- Provide text alternatives for icons

---

## Testing Checklist

When implementing responsive features, verify:

- [ ] No horizontal scroll on mobile (except intentional table scroll)
- [ ] All touch targets are at least 44x44px
- [ ] Text is readable without zooming (16px minimum)
- [ ] Forms work properly on mobile
- [ ] Modals fit within viewport
- [ ] Tables are usable (card view or horizontal scroll)
- [ ] Navigation is accessible
- [ ] Tested on actual devices (iOS and Android)
- [ ] Tested in portrait and landscape
- [ ] Lighthouse accessibility score is good

---

## Code Locations

- **JavaScript Utilities**: `frontend/src/utils/responsive.js`
- **Vue Composables**: `frontend/src/composables/useResponsive.js`
- **CSS Utilities**: `frontend/src/assets/responsive.css`
- **Table Component**: `frontend/src/components/TableScrollIndicator.vue`

---

## Additional Resources

- [Responsive Table Patterns Guide](./responsive-table-patterns.md)
- [WCAG 2.1 Touch Target Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/target-size.html)
- [MDN: Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)

---

## Spec Documents

For the complete mobile responsiveness implementation plan:
- Design document: `.kiro/specs/mobile-responsiveness/design.md`
- Requirements: `.kiro/specs/mobile-responsiveness/requirements.md`
- Tasks: `.kiro/specs/mobile-responsiveness/tasks.md`

