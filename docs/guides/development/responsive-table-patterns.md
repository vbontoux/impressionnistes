# Responsive Table Patterns

This document describes the two strategies for making tables responsive on mobile devices, along with implementation examples and best practices.

## Table of Contents

1. [Overview](#overview)
2. [Strategy A: Card Conversion](#strategy-a-card-conversion-preferred)
3. [Strategy B: Horizontal Scroll with Indicators](#strategy-b-horizontal-scroll-with-indicators)
4. [Choosing a Strategy](#choosing-a-strategy)
5. [Implementation Examples](#implementation-examples)
6. [Best Practices](#best-practices)
7. [Accessibility Considerations](#accessibility-considerations)

---

## Overview

Tables with many columns don't fit well on mobile screens. We provide two strategies to handle this:

1. **Card Conversion**: Transform table rows into vertical cards on mobile
2. **Horizontal Scroll**: Keep table structure but allow horizontal scrolling with visual indicators

Both strategies maintain usability while adapting to mobile constraints.

---

## Strategy A: Card Conversion (Preferred)

### When to Use

- Tables with 5+ columns
- Tables with complex data that benefits from vertical layout
- Tables where all information should be visible without scrolling
- User-facing tables (crew members, boat registrations, etc.)

### Advantages

- No horizontal scrolling required
- All data visible at once
- Better readability on small screens
- More mobile-friendly interaction

### Disadvantages

- Requires duplicate markup (table + cards)
- More code to maintain
- May not work well for very wide tables (10+ columns)

### Implementation

See [full implementation examples](#implementation-examples) below.

---

## Strategy B: Horizontal Scroll with Indicators

### When to Use

- Simple tables with 3-5 columns
- Tables where maintaining row structure is important
- Admin tables where users expect traditional table layout
- Tables with sortable columns

### Advantages

- Single markup (no duplication)
- Maintains familiar table structure
- Works well for sortable/filterable tables
- Less code to maintain

### Disadvantages

- Requires horizontal scrolling
- Some data may be hidden off-screen
- Less mobile-friendly than cards

### TableScrollIndicator Component

Location: `frontend/src/components/TableScrollIndicator.vue`

The `TableScrollIndicator` component automatically:
- Detects scroll position
- Shows gradient indicators on left/right when content is scrollable
- Hides indicators on tablet/desktop
- Provides smooth touch scrolling on mobile

**Props:**
- `indicatorColor`: Color of gradient (default: `'rgba(0, 0, 0, 0.1)'`)
- `indicatorWidth`: Width in pixels (default: `20`)
- `disabled`: Disable indicators (default: `false`)
- `ariaLabel`: Accessibility label (default: `'Scrollable table'`)

**Basic Usage:**

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

<style scoped>
.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px; /* Forces horizontal scroll on mobile */
}

@media (min-width: 768px) {
  .data-table {
    min-width: auto; /* Remove on larger screens */
  }
}
</style>
```

**Custom Styling:**

```vue
<TableScrollIndicator
  indicator-color="rgba(74, 144, 226, 0.15)"
  :indicator-width="30"
  aria-label="Crew members table"
>
  <table>
    <!-- Table content -->
  </table>
</TableScrollIndicator>
```

---

## Choosing a Strategy

Use this decision tree:

```
Is the table user-facing (not admin)?
├─ Yes → Use Card Conversion (Strategy A)
└─ No → Continue

Does the table have 5+ columns?
├─ Yes → Use Card Conversion (Strategy A)
└─ No → Continue

Is maintaining table structure important (sorting, filtering)?
├─ Yes → Use Horizontal Scroll (Strategy B)
└─ No → Use Card Conversion (Strategy A)
```

### Examples by Component

| Component | Strategy | Reason |
|-----------|----------|--------|
| CrewMemberList | Card Conversion | User-facing, 6+ columns, better mobile UX |
| AdminBoats | Card Conversion or Scroll | Admin table, many columns, user preference |
| Payment Summary | Card Conversion | User-facing, better readability |
| Race List | Horizontal Scroll | Simple table, 3-4 columns, sorting needed |

---

## Implementation Examples

### Example 1: Card Conversion Pattern

```vue
<template>
  <div>
    <!-- Desktop: Table view -->
    <div class="desktop-only">
      <table class="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>{{ item.name }}</td>
            <td>{{ item.email }}</td>
            <td>{{ item.role }}</td>
            <td>{{ item.status }}</td>
            <td>
              <button @click="edit(item)">Edit</button>
              <button @click="delete(item)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Mobile: Card view -->
    <div class="mobile-only">
      <div class="card-list">
        <div v-for="item in items" :key="item.id" class="data-card">
          <div class="card-row">
            <span class="card-label">Name:</span>
            <span class="card-value">{{ item.name }}</span>
          </div>
          <div class="card-row">
            <span class="card-label">Email:</span>
            <span class="card-value">{{ item.email }}</span>
          </div>
          <div class="card-row">
            <span class="card-label">Role:</span>
            <span class="card-value">{{ item.role }}</span>
          </div>
          <div class="card-row">
            <span class="card-label">Status:</span>
            <span class="card-value">{{ item.status }}</span>
          </div>
          <div class="card-actions">
            <button class="touch-button" @click="edit(item)">Edit</button>
            <button class="touch-button" @click="delete(item)">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import '@/assets/responsive.css';

/* Desktop table styles */
.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.data-table th {
  font-weight: 600;
  background: #f5f5f5;
}

/* Mobile card styles */
.card-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.data-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.card-row:last-of-type {
  border-bottom: none;
}

.card-label {
  font-weight: 600;
  color: #666;
  font-size: 0.875rem;
}

.card-value {
  color: #333;
  font-size: 0.875rem;
  text-align: right;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f0f0f0;
}

.card-actions button {
  flex: 1;
  min-height: 44px;
}
</style>
```

### Example 2: Horizontal Scroll Pattern

```vue
<template>
  <TableScrollIndicator aria-label="Data table">
    <table class="data-table">
      <thead>
        <tr>
          <th>Column 1</th>
          <th>Column 2</th>
          <th>Column 3</th>
          <th>Column 4</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.col1 }}</td>
          <td>{{ item.col2 }}</td>
          <td>{{ item.col3 }}</td>
          <td>{{ item.col4 }}</td>
          <td>
            <div class="action-buttons">
              <button class="touch-button btn-sm" @click="edit(item)">Edit</button>
              <button class="touch-button btn-sm" @click="delete(item)">Delete</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </TableScrollIndicator>
</template>

<script setup>
import TableScrollIndicator from '@/components/TableScrollIndicator.vue'
</script>

<style scoped>
.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

.data-table th,
.data-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
  white-space: nowrap;
}

.data-table th {
  font-weight: 600;
  background: #f5f5f5;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: nowrap;
}

@media (min-width: 768px) {
  .data-table {
    min-width: auto;
  }
  
  .data-table th,
  .data-table td {
    white-space: normal;
  }
}
</style>
```

---

## Best Practices

### 1. Consistent Column Order

Keep the same information order in both table and card views.

### 2. Touch-Friendly Actions

Ensure action buttons meet minimum touch target size (44x44px):

```css
.action-button {
  min-width: 44px;
  min-height: 44px;
  padding: 0.5rem 1rem;
}
```

### 3. Visual Hierarchy in Cards

Use typography and spacing to create clear hierarchy:

```css
.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.card-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #666;
}

.card-value {
  font-size: 0.875rem;
  color: #333;
}
```

### 4. Loading and Empty States

Provide clear feedback for loading and empty states.

### 5. Maintain Table Width

For horizontal scroll strategy, set appropriate min-width:

```css
.data-table {
  min-width: 600px; /* Adjust based on content */
}
```

---

## Accessibility Considerations

### 1. Semantic HTML

Use proper table markup with `<thead>`, `<tbody>`, and `scope` attributes.

### 2. ARIA Labels

Provide descriptive labels for screen readers:

```vue
<TableScrollIndicator aria-label="List of crew members">
  <table>
    <!-- Content -->
  </table>
</TableScrollIndicator>
```

### 3. Keyboard Navigation

Ensure tables are keyboard accessible with proper focus styles.

### 4. Touch Target Size

All interactive elements must be at least 44x44px.

---

## Testing Checklist

- [ ] Table displays correctly on mobile (375px, 390px, 414px)
- [ ] Scroll indicators appear/disappear correctly (Strategy B)
- [ ] Cards display all information clearly (Strategy A)
- [ ] Action buttons are easily tappable (44x44px minimum)
- [ ] No horizontal viewport overflow (except intentional table scroll)
- [ ] Table works on tablet (768px, 1024px)
- [ ] Desktop view displays properly (1024px+)
- [ ] Keyboard navigation works
- [ ] Screen reader announces content correctly
- [ ] Touch scrolling is smooth on mobile devices
- [ ] Tested on actual iOS and Android devices

---

## Common Issues and Solutions

### Issue 1: Scroll Indicators Not Showing

**Solution**: Ensure table has `min-width` set wider than container.

### Issue 2: Cards Too Tall on Mobile

**Solution**: Reduce padding and font sizes.

### Issue 3: Action Buttons Too Small

**Solution**: Ensure minimum 44x44px touch target size.

### Issue 4: Table Breaks Layout on Mobile

**Solution**: Wrap table in `TableScrollIndicator` component.

---

## Code Locations

- **TableScrollIndicator Component**: `frontend/src/components/TableScrollIndicator.vue`
- **Example Component**: `frontend/src/components/TableScrollIndicatorExample.vue`
- **Responsive Utilities**: `frontend/src/utils/responsive.js`
- **CSS Utilities**: `frontend/src/assets/responsive.css`

---

## Related Documentation

- [Responsive Design Guide](./responsive-design.md) - Main responsive design documentation
- [Frontend Testing Guide](./frontend-testing.md) - Testing responsive components
- Mobile Responsiveness Spec: `.kiro/specs/mobile-responsiveness/`

