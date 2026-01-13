# Design System Documentation

## Introduction

This design system provides a comprehensive set of reusable components, design tokens, and patterns to ensure consistency across the Impressionnistes Registration System. By following these guidelines, developers can build interfaces that are visually cohesive, accessible, and maintainable.

### Purpose

- **Consistency**: Ensure all UI elements follow the same visual language
- **Efficiency**: Reduce development time by reusing components
- **Maintainability**: Centralize styling decisions for easier updates
- **Accessibility**: Build interfaces that work for all users
- **Quality**: Maintain high standards across the application

### How to Use This Guide

1. **Design Tokens**: Start with the foundational values (colors, spacing, typography)
2. **Components**: Use pre-built components for common UI patterns
3. **Patterns**: Follow established patterns for complex interactions
4. **Best Practices**: Apply guidelines for optimal implementation

## Design Principles

### 1. Consistency First
Use design tokens and components consistently across all pages. Never hardcode values that exist in the design system.

### 2. Mobile-First Responsive
Design for mobile devices first, then enhance for larger screens. All touch targets must be at least 44px for accessibility.

### 3. Accessibility by Default
Components are built with accessibility in mind. Maintain proper contrast ratios, keyboard navigation, and screen reader support.

### 4. Progressive Enhancement
Start with core functionality that works everywhere, then add enhancements for modern browsers.

### 5. Performance Matters
Keep bundle sizes small, use CSS variables for theming, and optimize for fast rendering.

## Design Tokens

Design tokens are the foundational values of our design system. They are defined as CSS custom properties in `frontend/src/assets/design-tokens.css`.

### Colors

#### Primary Colors
```css
--color-primary: #007bff        /* Primary actions, links */
--color-primary-hover: #0056b3  /* Hover state */
--color-primary-active: #004085 /* Active/pressed state */
```

#### Semantic Colors
```css
--color-success: #28a745  /* Success states, complete */
--color-warning: #ffc107  /* Warning states, incomplete */
--color-danger: #dc3545   /* Error states, delete actions */
--color-secondary: #6c757d /* Secondary actions */
```

#### Neutral Colors
```css
--color-light: #f8f9fa    /* Light backgrounds */
--color-dark: #212529     /* Text, headings */
--color-muted: #666       /* Secondary text */
--color-border: #dee2e6   /* Borders, dividers */
--color-white: #ffffff    /* White backgrounds */
```

### Spacing Scale

Use the spacing scale for consistent margins, padding, and gaps:

```css
--spacing-xs: 0.25rem   /* 4px  - Tight spacing */
--spacing-sm: 0.5rem    /* 8px  - Small spacing */
--spacing-md: 0.75rem   /* 12px - Medium spacing */
--spacing-lg: 1rem      /* 16px - Large spacing */
--spacing-xl: 1.5rem    /* 24px - Extra large */
--spacing-xxl: 2rem     /* 32px - Double extra large */
--spacing-3xl: 3rem     /* 48px - Triple extra large */
```

### Typography

#### Font Sizes
```css
--font-size-xs: 0.75rem      /* 12px - Small labels */
--font-size-sm: 0.8125rem    /* 13px - Secondary text */
--font-size-base: 0.875rem   /* 14px - Body text */
--font-size-md: 0.95rem      /* 15.2px - Emphasized text */
--font-size-lg: 1rem         /* 16px - Large text */
--font-size-xl: 1.125rem     /* 18px - Headings */
--font-size-2xl: 1.25rem     /* 20px - Large headings */
--font-size-3xl: 1.5rem      /* 24px - Page titles */
```

#### Font Weights
```css
--font-weight-normal: 400    /* Regular text */
--font-weight-medium: 500    /* Emphasized text */
--font-weight-semibold: 600  /* Headings, labels */
--font-weight-bold: 700      /* Strong emphasis */
```

### Breakpoints

```css
--breakpoint-mobile: 768px   /* Tablet and up */
--breakpoint-tablet: 1024px  /* Desktop and up */
--breakpoint-desktop: 1280px /* Large desktop */
```

## Component Library

### BaseButton

Primary button component for all actions.

**Props:**
- `variant`: 'primary' | 'secondary' | 'danger' | 'warning'
- `size`: 'small' | 'medium' | 'large'
- `disabled`: boolean
- `loading`: boolean
- `fullWidth`: boolean

**Usage:**
```vue
<BaseButton variant="primary" size="small" @click="handleAction">
  Save
</BaseButton>

<BaseButton variant="secondary" size="small" @click="handleCancel">
  Cancel
</BaseButton>

<BaseButton variant="danger" size="small" :disabled="loading">
  Delete
</BaseButton>
```

**Sizing Guidelines:**
- Card view buttons: `size="small"`
- Table view buttons: `size="small"`
- Modal action buttons: `size="medium"`
- Full-width mobile buttons: `size="medium"` with `fullWidth`

### StatusBadge

Displays status with automatic color coding.

**Props:**
- `status`: 'incomplete' | 'complete' | 'paid' | 'forfait'
- `size`: 'small' | 'medium'

**Usage:**
```vue
<StatusBadge :status="boat.registration_status" size="medium" />
```

**Status Colors:**
- `incomplete`: Yellow (warning)
- `complete`: Green (success)
- `paid`: Blue (info)
- `forfait`: Red (danger)

### FormGroup

Wraps form inputs with consistent label, error, and help text styling.

**Props:**
- `label`: string (required)
- `required`: boolean
- `error`: string
- `helpText`: string

**Slots:**
- `default`: Input element
- `help`: Custom help content

**Usage:**
```vue
<FormGroup
  :label="$t('form.firstName')"
  :required="true"
  :error="errors.first_name"
  :help-text="$t('form.firstNameHint')"
>
  <input
    v-model="form.first_name"
    type="text"
    required
  />
</FormGroup>
```

### MessageAlert

Displays error, success, warning, or info messages.

**Props:**
- `type`: 'error' | 'success' | 'warning' | 'info'
- `message`: string (required)
- `dismissible`: boolean
- `autoDismiss`: boolean (auto-dismiss after 5 seconds)

**Usage:**
```vue
<MessageAlert
  v-if="errorMessage"
  type="error"
  :message="errorMessage"
  :dismissible="true"
  @dismiss="errorMessage = ''"
/>

<MessageAlert
  v-if="successMessage"
  type="success"
  :message="successMessage"
  :dismissible="true"
  :auto-dismiss="true"
  @dismiss="successMessage = ''"
/>
```

### LoadingSpinner

Displays a loading indicator with optional message.

**Props:**
- `size`: number (default: 40)
- `message`: string

**Usage:**
```vue
<LoadingSpinner v-if="loading" :message="$t('common.loading')" />
```

### EmptyState

Displays when no data is available.

**Props:**
- `message`: string (required)
- `actionLabel`: string

**Slots:**
- `icon`: Custom icon
- `action`: Custom action button

**Usage:**
```vue
<EmptyState :message="$t('boats.noBoats')">
  <template #action>
    <BaseButton variant="primary" @click="createBoat">
      {{ $t('boats.create') }}
    </BaseButton>
  </template>
</EmptyState>
```

### BaseModal

Modal dialog with responsive behavior.

**Props:**
- `show`: boolean (required)
- `title`: string
- `size`: 'small' | 'medium' | 'large'
- `closeOnOverlay`: boolean (default: true)

**Slots:**
- `header`: Custom header content
- `default`: Modal body
- `footer`: Modal footer with actions

**Usage:**
```vue
<BaseModal :show="showModal" :title="$t('modal.title')" @close="showModal = false">
  <p>Modal content goes here</p>
  
  <template #footer>
    <BaseButton variant="primary" @click="handleSave">Save</BaseButton>
    <BaseButton variant="secondary" @click="showModal = false">Cancel</BaseButton>
  </template>
</BaseModal>
```

### DataCard

Card component with status-based border colors.

**Props:**
- `title`: string
- `status`: string
- `statusBadge`: boolean

**Slots:**
- `header`: Custom header content
- `default`: Card body
- `actions`: Action buttons

**Usage:**
```vue
<DataCard :title="boat.boat_number" :status="boat.registration_status">
  <p>{{ boat.event_type }}</p>
  
  <template #actions>
    <BaseButton size="small" variant="secondary" @click="viewBoat">View</BaseButton>
    <BaseButton size="small" variant="danger" @click="deleteBoat">Delete</BaseButton>
  </template>
</DataCard>
```

### SortableTable

Table with sortable columns.

**Props:**
- `columns`: Array of column definitions
- `data`: Array of data rows

**Slots:**
- `cell-{key}`: Custom cell content for specific columns

**Usage:**
```vue
<SortableTable
  :columns="[
    { key: 'boat_number', label: 'Boat #', sortable: true },
    { key: 'event_type', label: 'Event', sortable: true },
    { key: 'status', label: 'Status', sortable: false }
  ]"
  :data="boats"
>
  <template #cell-status="{ row }">
    <StatusBadge :status="row.registration_status" />
  </template>
</SortableTable>
```

## Patterns

### Buttons

**Placement:**
- Primary action on the right (or bottom on mobile)
- Secondary/cancel action on the left (or top on mobile)
- Destructive actions (delete) should be visually separated

**Colors:**
- Primary actions: `variant="primary"` (blue)
- Secondary actions: `variant="secondary"` (gray)
- Destructive actions: `variant="danger"` (red)
- Warning actions: `variant="warning"` (yellow)

**Sizing:**
- Cards: `size="small"`
- Tables: `size="small"`
- Modals: `size="medium"`
- Mobile full-width: `size="medium"` with `fullWidth`

### Forms

**Structure:**
```vue
<form @submit.prevent="handleSubmit">
  <FormGroup label="Field Label" :required="true" :error="errors.field">
    <input v-model="form.field" type="text" required />
  </FormGroup>
  
  <MessageAlert v-if="errorMessage" type="error" :message="errorMessage" />
  
  <div class="button-group">
    <BaseButton type="submit" variant="primary" size="small">Save</BaseButton>
    <BaseButton type="button" variant="secondary" size="small" @click="cancel">Cancel</BaseButton>
  </div>
</form>
```

**Validation:**
- Show errors on blur or submit
- Use FormGroup's error prop for field-level errors
- Use MessageAlert for form-level errors
- Clear errors when user starts typing

### Tables

**Card vs Table View:**
- Mobile: Always use card view
- Desktop: Provide toggle between card and table views
- Maintain consistent button placement in both views

**Sorting:**
- Use SortableTable component
- Show sort indicators (▲ ▼)
- Support alphanumeric sorting for boat numbers

**Empty States:**
- Use EmptyState component
- Provide action to create first item
- Show helpful message

### Cards

**Structure:**
```vue
<DataCard :title="item.name" :status="item.status">
  <!-- Card content -->
  <div class="card-field">
    <span class="label">Label:</span>
    <span class="value">Value</span>
  </div>
  
  <!-- Actions -->
  <template #actions>
    <BaseButton size="small" variant="secondary">View</BaseButton>
    <BaseButton size="small" variant="danger">Delete</BaseButton>
  </template>
</DataCard>
```

**Status Borders:**
- Complete: Green border
- Incomplete: Yellow border
- Paid: Blue border
- Forfait: Red border

### Modals

**Structure:**
```vue
<BaseModal :show="showModal" :title="modalTitle" @close="closeModal">
  <!-- Modal content -->
  <FormGroup label="Field">
    <input v-model="form.field" />
  </FormGroup>
  
  <!-- Actions in footer -->
  <template #footer>
    <BaseButton variant="primary" @click="save">Save</BaseButton>
    <BaseButton variant="secondary" @click="closeModal">Cancel</BaseButton>
  </template>
</BaseModal>
```

**Behavior:**
- Close on overlay click (default)
- Close on Escape key
- Trap focus within modal
- Restore focus on close

### Loading States

**Full Page:**
```vue
<LoadingSpinner v-if="loading" :message="$t('common.loading')" />
<div v-else>
  <!-- Content -->
</div>
```

**Inline:**
```vue
<BaseButton :loading="saving" :disabled="saving">
  {{ saving ? $t('common.saving') : $t('common.save') }}
</BaseButton>
```

### Empty States

```vue
<EmptyState
  v-if="!loading && items.length === 0"
  :message="$t('items.noItems')"
>
  <template #action>
    <BaseButton variant="primary" @click="createItem">
      {{ $t('items.create') }}
    </BaseButton>
  </template>
</EmptyState>
```

### Error Handling

**Form Errors:**
```vue
<MessageAlert
  v-if="errorMessage"
  type="error"
  :message="errorMessage"
  :dismissible="true"
  @dismiss="errorMessage = ''"
/>
```

**Field Errors:**
```vue
<FormGroup :error="errors.field">
  <input v-model="form.field" @blur="validateField('field')" />
</FormGroup>
```

## Layout Guidelines

### Spacing

Use the spacing scale consistently:
- Between form fields: `var(--spacing-lg)`
- Between sections: `var(--spacing-xl)` or `var(--spacing-xxl)`
- Card padding: `var(--spacing-lg)` mobile, `var(--spacing-xl)` desktop
- Button groups: `var(--spacing-sm)` or `var(--spacing-md)`

### Responsive Behavior

**Mobile (< 768px):**
- Stack elements vertically
- Full-width buttons
- Card view for lists
- Bottom sheet modals

**Tablet (768px - 1024px):**
- 2-column layouts where appropriate
- Side-by-side buttons
- Table view option
- Centered modals

**Desktop (> 1024px):**
- Multi-column layouts
- Horizontal button groups
- Table view default
- Larger modals

### Grid Layouts

Use CSS Grid for complex layouts:
```css
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-lg);
}
```

## Best Practices

### DO ✅

- **Use design tokens** for all colors, spacing, and typography
- **Use components** instead of custom HTML/CSS
- **Follow sizing standards** (small buttons in cards/tables)
- **Maintain consistency** across similar pages
- **Test on mobile** devices and different screen sizes
- **Use semantic HTML** for accessibility
- **Provide loading states** for async operations
- **Show empty states** when no data exists
- **Handle errors gracefully** with clear messages

### DON'T ❌

- **Hardcode colors** - use `var(--color-primary)` not `#007bff`
- **Hardcode spacing** - use `var(--spacing-lg)` not `1rem`
- **Duplicate CSS** - centralize in design-tokens.css
- **Create custom buttons** - use BaseButton
- **Create custom badges** - use StatusBadge
- **Mix sizing** - keep buttons consistent within context
- **Ignore mobile** - always test responsive behavior
- **Skip loading states** - users need feedback
- **Hide errors** - show clear error messages

### Code Examples

**❌ Wrong:**
```vue
<button style="background: #007bff; padding: 8px 16px;">
  Save
</button>
```

**✅ Correct:**
```vue
<BaseButton variant="primary" size="small" @click="save">
  Save
</BaseButton>
```

**❌ Wrong:**
```vue
<div style="color: #28a745; padding: 4px 12px; border-radius: 12px;">
  Complete
</div>
```

**✅ Correct:**
```vue
<StatusBadge status="complete" size="medium" />
```

## Migration Guide

### Migrating Existing Components

1. **Replace hardcoded colors:**
   ```css
   /* Before */
   color: #007bff;
   background: #28a745;
   
   /* After */
   color: var(--color-primary);
   background: var(--color-success);
   ```

2. **Replace hardcoded spacing:**
   ```css
   /* Before */
   margin: 16px;
   padding: 8px 12px;
   
   /* After */
   margin: var(--spacing-lg);
   padding: var(--spacing-sm) var(--spacing-md);
   ```

3. **Replace custom buttons:**
   ```vue
   <!-- Before -->
   <button class="btn btn-primary" @click="save">Save</button>
   
   <!-- After -->
   <BaseButton variant="primary" size="small" @click="save">Save</BaseButton>
   ```

4. **Replace form fields:**
   ```vue
   <!-- Before -->
   <div class="form-group">
     <label>Name *</label>
     <input v-model="name" />
     <span class="error">{{ errors.name }}</span>
   </div>
   
   <!-- After -->
   <FormGroup label="Name" :required="true" :error="errors.name">
     <input v-model="name" />
   </FormGroup>
   ```

### Common Patterns

**Before:**
```vue
<div class="card">
  <h3>{{ title }}</h3>
  <p>{{ content }}</p>
  <div class="actions">
    <button @click="edit">Edit</button>
    <button @click="delete">Delete</button>
  </div>
</div>
```

**After:**
```vue
<DataCard :title="title">
  <p>{{ content }}</p>
  <template #actions>
    <BaseButton size="small" variant="secondary" @click="edit">Edit</BaseButton>
    <BaseButton size="small" variant="danger" @click="delete">Delete</BaseButton>
  </template>
</DataCard>
```

## Resources

- **Design System Showcase**: `/design-system` - Interactive component examples
- **Design Tokens**: `frontend/src/assets/design-tokens.css` - All token definitions
- **Components**: `frontend/src/components/` - Component source code
- **Steering Rules**: `.kiro/steering/ui-consistency-rules.md` - Quick reference guide

## Support

For questions or suggestions about the design system:
1. Check the Design System Showcase page
2. Review this documentation
3. Consult the steering rules
4. Ask the team for guidance

---

**Last Updated**: January 2026
**Version**: 1.0
