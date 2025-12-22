# Design Document: Mobile Responsiveness Improvements

## Overview

This design document outlines the technical approach for implementing mobile responsiveness improvements across the Course des Impressionnistes registration system frontend. The design focuses on creating a consistent, accessible, and performant mobile experience using Vue 3 composition API, scoped CSS, and mobile-first responsive patterns.

## Architecture

### Design Principles

1. **Mobile-First Approach**: Base styles target mobile devices, with progressive enhancement for larger screens
2. **Component-Based**: Each Vue component manages its own responsive styles
3. **Consistency**: Shared responsive patterns across all components
4. **Accessibility**: Minimum 44x44px touch targets, proper contrast, semantic HTML
5. **Performance**: Minimal CSS, efficient media queries, no layout thrashing
6. **No Backend Changes**: All modifications are frontend presentation layer only

### Technology Stack

- **Framework**: Vue 3 with Composition API
- **Styling**: Scoped CSS with media queries
- **Build Tool**: Vite
- **Target Browsers**: Modern mobile browsers (iOS Safari, Chrome Mobile, Firefox Mobile)

### Responsive Breakpoints

```css
/* Mobile: Base styles (no media query needed - mobile first) */
/* Applies to: < 768px */

/* Tablet: Medium screens */
@media (min-width: 768px) { }

/* Desktop: Large screens */
@media (min-width: 1024px) { }

/* Extra Large Desktop */
@media (min-width: 1200px) { }
```

## Components and Interfaces

### 1. Responsive Table Component Pattern

**Problem**: Tables with many columns overflow on mobile devices.

**Solution**: Implement adaptive table display with two strategies:

#### Strategy A: Card Conversion (Preferred for complex tables)

```vue
<template>
  <!-- Desktop: Table view -->
  <div class="table-container desktop-only">
    <table class="data-table">
      <!-- Standard table markup -->
    </table>
  </div>
  
  <!-- Mobile: Card view -->
  <div class="card-list mobile-only">
    <div v-for="item in items" :key="item.id" class="data-card">
      <!-- Card layout with key-value pairs -->
    </div>
  </div>
</template>

<style scoped>
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
    display: block;
  }
}
</style>
```

#### Strategy B: Horizontal Scroll with Indicators (For simple tables)

```vue
<template>
  <div class="table-scroll-container">
    <div class="scroll-indicator left" v-if="showLeftIndicator"></div>
    <div class="table-wrapper" @scroll="handleScroll">
      <table class="data-table">
        <!-- Table content -->
      </table>
    </div>
    <div class="scroll-indicator right" v-if="showRightIndicator"></div>
  </div>
</template>

<style scoped>
.table-scroll-container {
  position: relative;
}

.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.data-table {
  min-width: 800px; /* Maintain table structure */
}

.scroll-indicator {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 20px;
  pointer-events: none;
  z-index: 1;
}

.scroll-indicator.left {
  left: 0;
  background: linear-gradient(to right, rgba(0,0,0,0.1), transparent);
}

.scroll-indicator.right {
  right: 0;
  background: linear-gradient(to left, rgba(0,0,0,0.1), transparent);
}

@media (min-width: 768px) {
  .table-wrapper {
    overflow-x: visible;
  }
  
  .scroll-indicator {
    display: none;
  }
}
</style>
```

### 2. Responsive Form Layout Pattern

**Problem**: Multi-column forms don't fit mobile screens.

**Solution**: Stack all form elements vertically on mobile.

```vue
<template>
  <form class="responsive-form">
    <div class="form-row">
      <div class="form-group">
        <label>Field 1</label>
        <input type="text" />
      </div>
      <div class="form-group">
        <label>Field 2</label>
        <input type="text" />
      </div>
    </div>
  </form>
</template>

<style scoped>
.responsive-form {
  padding: 1rem;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  font-size: 0.875rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  font-size: 16px; /* Prevents zoom on iOS */
  border: 1px solid #ddd;
  border-radius: 4px;
  min-height: 44px; /* Touch target size */
}

@media (min-width: 768px) {
  .responsive-form {
    padding: 2rem;
  }
  
  .form-row {
    flex-direction: row;
  }
  
  .form-group {
    flex: 1;
  }
}
</style>
```

### 3. Responsive Filter Controls Pattern

**Problem**: Horizontal filter rows overflow on mobile.

**Solution**: Stack filters vertically with full-width controls.

```vue
<template>
  <div class="filters">
    <div class="search-box">
      <input type="text" placeholder="Search..." class="search-input" />
    </div>
    
    <div class="filter-row">
      <button class="filter-btn">All</button>
      <button class="filter-btn">Active</button>
      
      <div class="filter-group">
        <label>Category</label>
        <select class="filter-select">
          <option>All</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Sort By</label>
        <select class="filter-select">
          <option>Name</option>
        </select>
      </div>
    </div>
  </div>
</template>

<style scoped>
.filters {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.search-box {
  margin-bottom: 0.75rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-height: 44px;
}

.filter-row {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.filter-btn {
  width: 100%;
  padding: 0.75rem;
  min-height: 44px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  font-size: 0.875rem;
}

.filter-select {
  width: 100%;
  padding: 0.75rem;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-height: 44px;
}

@media (min-width: 768px) {
  .filters {
    padding: 1.5rem;
  }
  
  .filter-row {
    flex-direction: row;
    flex-wrap: wrap;
    align-items: flex-end;
  }
  
  .filter-btn {
    width: auto;
    flex: 0 0 auto;
  }
  
  .filter-group {
    flex: 1;
    min-width: 150px;
  }
}
</style>
```

### 4. Responsive Modal Pattern

**Problem**: Modals extend beyond viewport on mobile.

**Solution**: Full-width modals with proper scrolling.

```vue
<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h2>{{ title }}</h2>
        <button class="close-btn" @click="close">×</button>
      </div>
      <div class="modal-body">
        <slot></slot>
      </div>
      <div class="modal-footer" v-if="$slots.footer">
        <slot name="footer"></slot>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
  padding: 0;
}

.modal-content {
  background: white;
  border-radius: 12px 12px 0 0;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  padding: 0;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.modal-body {
  padding: 1rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 1rem;
  border-top: 1px solid #e0e0e0;
  flex-shrink: 0;
}

@media (min-width: 768px) {
  .modal-overlay {
    align-items: center;
    padding: 1rem;
  }
  
  .modal-content {
    border-radius: 12px;
    width: 90%;
    max-width: 600px;
    max-height: 90vh;
  }
  
  .modal-header {
    padding: 1.5rem;
  }
  
  .modal-header h2 {
    font-size: 1.5rem;
  }
  
  .modal-body {
    padding: 1.5rem;
  }
  
  .modal-footer {
    padding: 1.5rem;
  }
}
</style>
```

### 5. Responsive Card Grid Pattern

**Problem**: Card grids don't adapt to mobile screens.

**Solution**: Single column on mobile, multi-column on larger screens.

```vue
<template>
  <div class="card-grid">
    <div v-for="item in items" :key="item.id" class="card">
      <!-- Card content -->
    </div>
  </div>
</template>

<style scoped>
.card-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

@media (min-width: 768px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
  
  .card {
    padding: 1.5rem;
  }
}

@media (min-width: 1024px) {
  .card-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
```

### 6. Responsive Button Group Pattern

**Problem**: Multiple action buttons don't fit in mobile table cells.

**Solution**: Stack buttons vertically or use icon-only buttons.

```vue
<template>
  <div class="button-group">
    <button class="btn btn-primary">
      <span class="btn-icon">✏️</span>
      <span class="btn-text">Edit</span>
    </button>
    <button class="btn btn-danger">
      <span class="btn-icon">🗑️</span>
      <span class="btn-text">Delete</span>
    </button>
  </div>
</template>

<style scoped>
.button-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem;
  min-height: 44px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-text {
  display: none;
}

.btn-icon {
  font-size: 1.25rem;
}

@media (min-width: 768px) {
  .button-group {
    flex-direction: row;
  }
  
  .btn {
    padding: 0.5rem 1rem;
  }
  
  .btn-text {
    display: inline;
  }
}
</style>
```

## Data Models

No new data models are required. All changes are presentational only.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Viewport Fit

*For any* page or component, when rendered on a mobile device (width < 768px), the content width should not exceed the viewport width, ensuring no horizontal scroll appears (except for intentionally scrollable tables).

**Validates: Requirements 1.1, 1.2, 1.3, 14.5**

### Property 2: Touch Target Minimum Size

*For any* interactive element (button, link, input, checkbox), the clickable/tappable area should be at least 44x44 pixels on mobile devices.

**Validates: Requirements 3.4, 7.1, 7.3**

### Property 3: Form Field Stacking

*For any* form with multiple fields, when rendered on mobile devices (width < 768px), all form fields should be stacked vertically in a single column.

**Validates: Requirements 3.1, 3.2, 3.3**

### Property 4: Table Responsiveness

*For any* data table, when rendered on mobile devices (width < 768px), the table should either convert to card layout OR provide horizontal scroll with visual indicators.

**Validates: Requirements 2.1, 2.2, 2.3**

### Property 5: Modal Viewport Fit

*For any* modal dialog, when displayed on mobile devices (width < 768px), the modal width should not exceed viewport width minus appropriate margins, and height should not exceed 90vh.

**Validates: Requirements 4.1, 4.3, 4.6**

### Property 6: Filter Control Stacking

*For any* filter row with multiple controls, when rendered on mobile devices (width < 768px), all filter controls should stack vertically.

**Validates: Requirements 3.3, 5.4**

### Property 7: Button Spacing

*For any* group of interactive elements, the minimum spacing between touch targets should be at least 8 pixels on mobile devices.

**Validates: Requirements 7.2**

### Property 8: Font Size Minimum

*For any* body text content, the font size should be at least 16 pixels on mobile devices to prevent automatic zoom on iOS.

**Validates: Requirements 8.1, 3.4**

### Property 9: Card Grid Single Column

*For any* card grid layout, when rendered on mobile devices (width < 768px), the grid should display cards in a single column.

**Validates: Requirements 5.1, 5.2**

### Property 10: Consistent Breakpoints

*For any* component with responsive styles, the breakpoint values used should be 768px for mobile/tablet and 1024px for tablet/desktop transitions.

**Validates: Requirements 1.1, 1.2, 1.3**

### Property 11: Action Button Accessibility

*For any* table row with action buttons, when rendered on mobile devices (width < 768px), the buttons should either stack vertically OR use icon-only display with adequate touch target size.

**Validates: Requirements 2.4, 7.1**

### Property 12: Input Height Minimum

*For any* form input field (text, select, textarea), the minimum height should be 44 pixels on mobile devices.

**Validates: Requirements 3.4, 7.1**

## Error Handling

### Viewport Overflow

**Issue**: Content extends beyond viewport width on mobile.

**Detection**: Visual testing, browser developer tools mobile emulation.

**Resolution**: 
- Add `max-width: 100%` to container elements
- Use `overflow-x: hidden` on body (with caution)
- Identify and fix fixed-width elements

### Touch Target Too Small

**Issue**: Interactive elements smaller than 44x44px.

**Detection**: Accessibility audit tools, manual testing.

**Resolution**:
- Increase padding on buttons and links
- Add `min-height: 44px` and `min-width: 44px`
- Increase clickable area with pseudo-elements if needed

### Text Too Small

**Issue**: Font size below 16px causing zoom on iOS.

**Detection**: iOS device testing.

**Resolution**:
- Set `font-size: 16px` on inputs
- Adjust body text to minimum 16px on mobile
- Use `font-size: max(16px, 1rem)` for responsive scaling

### Modal Overflow

**Issue**: Modal content extends beyond viewport.

**Detection**: Mobile device testing, developer tools.

**Resolution**:
- Set `max-height: 90vh` on modal content
- Enable `overflow-y: auto` on modal body
- Reduce modal padding on mobile

## Testing Strategy

### Unit Testing

Unit tests are not applicable for CSS/styling changes. Visual regression testing is more appropriate.

### Visual Regression Testing

**Manual Testing Checklist**:

1. **Viewport Sizes**:
   - 375px (iPhone SE)
   - 390px (iPhone 12/13/14)
   - 414px (iPhone Plus models)
   - 768px (iPad portrait)
   - 1024px (iPad landscape)

2. **Test Scenarios per Component**:
   - Load page at mobile width
   - Verify no horizontal scroll
   - Check all touch targets are 44x44px minimum
   - Verify text is readable without zoom
   - Test all interactive elements
   - Rotate to landscape orientation
   - Test on actual devices (iOS Safari, Chrome Mobile)

3. **Browser Testing**:
   - Chrome DevTools mobile emulation
   - Firefox Responsive Design Mode
   - Safari iOS Simulator
   - Actual mobile devices (preferred)

### Component-Specific Testing

**CrewMemberList.vue**:
- [ ] Card view displays properly on mobile
- [ ] Table view scrolls horizontally with indicators
- [ ] Filter controls stack vertically
- [ ] Action buttons are tappable
- [ ] Modal forms fit viewport

**AdminBoats.vue**:
- [ ] Table converts to cards or scrolls properly
- [ ] Filter controls stack vertically
- [ ] Action buttons are accessible
- [ ] Pagination controls are tappable

**Forms (CrewMemberForm, BoatRegistrationForm)**:
- [ ] All fields stack vertically
- [ ] Inputs are 44px minimum height
- [ ] Labels remain visible
- [ ] Buttons are easily tappable
- [ ] Form fits in modal on mobile

**Payment Components**:
- [ ] Payment summary is readable
- [ ] Stripe checkout fits viewport
- [ ] Payment buttons are tappable
- [ ] Success page displays properly

### Accessibility Testing

- [ ] Run Lighthouse accessibility audit
- [ ] Verify touch target sizes
- [ ] Check color contrast ratios
- [ ] Test with screen reader (VoiceOver on iOS)
- [ ] Verify keyboard navigation (for tablet users)

## Implementation Notes

### CSS Best Practices

1. **Use Mobile-First Media Queries**:
   ```css
   /* Base styles for mobile */
   .element {
     padding: 1rem;
   }
   
   /* Enhance for larger screens */
   @media (min-width: 768px) {
     .element {
       padding: 2rem;
     }
   }
   ```

2. **Avoid Fixed Widths**:
   ```css
   /* Bad */
   .container {
     width: 1200px;
   }
   
   /* Good */
   .container {
     width: 100%;
     max-width: 1200px;
   }
   ```

3. **Use Flexbox and Grid**:
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

4. **Prevent iOS Zoom**:
   ```css
   input, select, textarea {
     font-size: 16px; /* Minimum to prevent zoom */
   }
   ```

### Vue Component Patterns

1. **Conditional Rendering for Mobile/Desktop**:
   ```vue
   <script setup>
   import { ref, onMounted, onUnmounted } from 'vue'
   
   const isMobile = ref(window.innerWidth < 768)
   
   const handleResize = () => {
     isMobile.value = window.innerWidth < 768
   }
   
   onMounted(() => {
     window.addEventListener('resize', handleResize)
   })
   
   onUnmounted(() => {
     window.removeEventListener('resize', handleResize)
   })
   </script>
   
   <template>
     <div v-if="isMobile" class="mobile-view">
       <!-- Mobile-specific markup -->
     </div>
     <div v-else class="desktop-view">
       <!-- Desktop-specific markup -->
     </div>
   </template>
   ```

2. **Responsive Composable** (Optional):
   ```javascript
   // composables/useResponsive.js
   import { ref, onMounted, onUnmounted } from 'vue'
   
   export function useResponsive() {
     const isMobile = ref(window.innerWidth < 768)
     const isTablet = ref(window.innerWidth >= 768 && window.innerWidth < 1024)
     const isDesktop = ref(window.innerWidth >= 1024)
     
     const handleResize = () => {
       const width = window.innerWidth
       isMobile.value = width < 768
       isTablet.value = width >= 768 && width < 1024
       isDesktop.value = width >= 1024
     }
     
     onMounted(() => {
       window.addEventListener('resize', handleResize)
     })
     
     onUnmounted(() => {
       window.removeEventListener('resize', handleResize)
     })
     
     return { isMobile, isTablet, isDesktop }
   }
   ```

### Performance Considerations

1. **Minimize Reflows**: Use CSS transforms instead of layout properties for animations
2. **Debounce Resize Handlers**: Prevent excessive recalculations
3. **Lazy Load Images**: Use `loading="lazy"` attribute
4. **Optimize CSS**: Remove unused styles, minimize specificity

### Browser Compatibility

- **Target**: iOS Safari 14+, Chrome Mobile 90+, Firefox Mobile 90+
- **Fallbacks**: Provide graceful degradation for older browsers
- **Vendor Prefixes**: Use autoprefixer in build process

## Migration Strategy

### Phase 1: Core Components (Week 1)
- App.vue (header, navigation)
- CrewMemberList.vue
- CrewMemberForm.vue

### Phase 2: Admin Pages (Week 2)
- AdminBoats.vue
- AdminDataExport.vue
- AdminPricingConfig.vue

### Phase 3: Payment & Checkout (Week 3)
- Payment.vue
- PaymentCheckout.vue
- StripeCheckout.vue
- PaymentSummary.vue

### Phase 4: Remaining Pages (Week 4)
- Boats.vue
- BoatRentalPage.vue
- Dashboard.vue
- Profile.vue
- Home.vue

### Testing After Each Phase
- Manual testing on mobile devices
- Visual regression checks
- Accessibility audit
- User acceptance testing
