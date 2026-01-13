---
inclusion: always
---

# UI Consistency Steering Guide

## Purpose

This guide ensures consistent UI implementation across the Impressionnistes Registration System. Follow these rules when working on any frontend code to maintain visual consistency, accessibility, and maintainability.

## Quick Reference

### Component Usage
- **Buttons**: Always use `BaseButton` component
- **Status Badges**: Always use `StatusBadge` component
- **Forms**: Always use `FormGroup` component
- **Messages**: Always use `MessageAlert` component
- **Modals**: Always use `BaseModal` component
- **Tables**: Always use `SortableTable` component for sortable data
- **Cards**: Always use `DataCard` component for data display

### Design Tokens
- **Colors**: `var(--color-primary)`, `var(--color-success)`, etc.
- **Spacing**: `var(--spacing-xs)` through `var(--spacing-3xl)`
- **Typography**: `var(--font-size-xs)` through `var(--font-size-3xl)`
- **Never hardcode**: colors, spacing, or font sizes

## MUST Rules

### 1. Tags and Status Badges - MUST Align

**MUST use StatusBadge component for all status displays:**
```vue
<!-- ✅ CORRECT -->
<StatusBadge :status="boat.registration_status" size="medium" />

<!-- ❌ WRONG -->
<span class="badge badge-success">Complete</span>
<div style="color: green">Complete</div>
```

**MUST use consistent status values:**
- `incomplete` - Yellow (warning)
- `complete` - Green (success)
- `paid` - Blue (info)
- `forfait` - Red (danger)

**MUST use sentence case (not uppercase):**
```vue
<!-- ✅ CORRECT -->
<StatusBadge status="complete" />  <!-- Displays: "Complete" -->

<!-- ❌ WRONG -->
<span style="text-transform: uppercase">complete</span>  <!-- Displays: "COMPLETE" -->
```

**MUST use consistent sizing:**
- Default: `size="medium"` for most contexts
- Small: `size="small"` only when space is very limited

### 2. Forms - MUST Align

**MUST use FormGroup for all form fields:**
```vue
<!-- ✅ CORRECT -->
<FormGroup
  :label="$t('form.firstName')"
  :required="true"
  :error="errors.first_name"
  :help-text="$t('form.firstNameHint')"
>
  <input v-model="form.first_name" type="text" required />
</FormGroup>

<!-- ❌ WRONG -->
<div class="form-group">
  <label>First Name *</label>
  <input v-model="form.first_name" />
  <span class="error">{{ errors.first_name }}</span>
</div>
```

**MUST use MessageAlert for form-level errors:**
```vue
<!-- ✅ CORRECT -->
<MessageAlert
  v-if="errorMessage"
  type="error"
  :message="errorMessage"
  :dismissible="true"
  @dismiss="errorMessage = ''"
/>

<!-- ❌ WRONG -->
<div v-if="errorMessage" class="alert alert-error">
  {{ errorMessage }}
</div>
```

**MUST use consistent input styling:**
- All inputs MUST use design tokens for borders, padding, and colors
- Mobile inputs MUST be 16px font size (prevents iOS zoom)
- All inputs MUST have 44px minimum height (touch target)

### 3. Colors - MUST Align

**MUST use design tokens for ALL colors:**
```css
/* ✅ CORRECT */
color: var(--color-primary);
background: var(--color-success);
border-color: var(--color-border);

/* ❌ WRONG */
color: #007bff;
background: #28a745;
border-color: #ddd;
```

**MUST use semantic colors appropriately:**
- **Primary** (`--color-primary`): Primary actions, links, boat numbers
- **Success** (`--color-success`): Success states, complete status
- **Warning** (`--color-warning`): Warning states, incomplete status
- **Danger** (`--color-danger`): Error states, delete actions, forfait status
- **Secondary** (`--color-secondary`): Secondary actions, muted text

**MUST NOT invent new colors:**
- Only use colors defined in `design-tokens.css`
- If you need a new color, add it to design tokens first
- Never use hardcoded hex values

### 4. Buttons - MUST Align Placement, Size, and Colors

**MUST use BaseButton for all buttons:**
```vue
<!-- ✅ CORRECT -->
<BaseButton variant="primary" size="small" @click="save">
  Save
</BaseButton>

<!-- ❌ WRONG -->
<button class="btn btn-primary" @click="save">Save</button>
<button style="background: blue" @click="save">Save</button>
```

**MUST use consistent sizing by context:**
```vue
<!-- Card view buttons -->
<BaseButton size="small" variant="secondary">View</BaseButton>

<!-- Table view buttons -->
<BaseButton size="small" variant="danger">Delete</BaseButton>

<!-- Modal action buttons -->
<BaseButton size="medium" variant="primary">Save</BaseButton>

<!-- Mobile full-width buttons -->
<BaseButton size="medium" variant="primary" :full-width="true">Submit</BaseButton>
```

**MUST use consistent colors by action type:**
```vue
<!-- Primary actions (save, submit, create) -->
<BaseButton variant="primary">Save</BaseButton>

<!-- Secondary actions (cancel, close, back) -->
<BaseButton variant="secondary">Cancel</BaseButton>

<!-- Destructive actions (delete, remove) -->
<BaseButton variant="danger">Delete</BaseButton>

<!-- Warning actions (forfait, archive) -->
<BaseButton variant="warning">Mark Forfait</BaseButton>
```

**MUST use consistent placement:**
```vue
<!-- Desktop: Primary on right, secondary on left -->
<div class="button-group">
  <BaseButton variant="secondary">Cancel</BaseButton>
  <BaseButton variant="primary">Save</BaseButton>
</div>

<!-- Mobile: Stack vertically, primary on bottom -->
<div class="button-group">
  <BaseButton variant="secondary">Cancel</BaseButton>
  <BaseButton variant="primary">Save</BaseButton>
</div>
```

### 5. Layout - MUST Align Similar Views

**MUST use consistent layout for card vs table views:**

**Card View Pattern:**
```vue
<div class="card-grid">
  <DataCard
    v-for="item in items"
    :key="item.id"
    :title="item.name"
    :status="item.status"
  >
    <!-- Card content -->
    <div class="card-field">
      <span class="label">{{ $t('field.label') }}:</span>
      <span class="value">{{ item.value }}</span>
    </div>
    
    <!-- Actions -->
    <template #actions>
      <BaseButton size="small" variant="secondary">View</BaseButton>
      <BaseButton size="small" variant="danger">Delete</BaseButton>
    </template>
  </DataCard>
</div>
```

**Table View Pattern:**
```vue
<SortableTable
  :columns="columns"
  :data="items"
>
  <template #cell-status="{ row }">
    <StatusBadge :status="row.status" />
  </template>
  
  <template #cell-actions="{ row }">
    <BaseButton size="small" variant="secondary" @click="view(row)">
      View
    </BaseButton>
    <BaseButton size="small" variant="danger" @click="deleteItem(row)">
      Delete
    </BaseButton>
  </template>
</SortableTable>
```

**MUST maintain consistency between views:**
- Same button sizes in both views (size="small")
- Same button variants in both views
- Same status badge display in both views
- Same action button order in both views
- Same data fields displayed in both views

**MUST use responsive patterns:**
```css
/* Mobile: Card view only */
@media (max-width: 767px) {
  .table-view { display: none; }
  .card-view { display: block; }
}

/* Desktop: Toggle between views */
@media (min-width: 768px) {
  .table-view { display: block; }
  .card-view { display: none; }
}
```

### 6. Card Headers - MUST Have Visual Separator

**MUST add a visual separator between card header and body:**

All card headers MUST include a bottom border to visually separate the header from the card body content. This applies to ALL card views across the application (admin views, team manager views, etc.).

```css
/* ✅ CORRECT - Card header with separator */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--spacing-lg);
}

/* ❌ WRONG - Card header without separator */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-lg);
}
```

**Why this matters:**
- Creates clear visual hierarchy within cards
- Separates title/status information from detailed content
- Maintains consistency across admin and team manager views
- Improves readability and scannability

**Example:**
```vue
<div class="boat-card">
  <div class="boat-header">
    <h3>Event Type - Boat Type</h3>
    <StatusBadge :status="boat.status" />
  </div>
  <!-- Separator creates clear division here -->
  <div class="boat-details">
    <!-- Card body content -->
  </div>
</div>
```

### 7. Spacing - MUST Align

**MUST use design tokens for all spacing:**
```css
/* ✅ CORRECT */
margin: var(--spacing-lg);
padding: var(--spacing-sm) var(--spacing-md);
gap: var(--spacing-xl);

/* ❌ WRONG */
margin: 16px;
padding: 8px 12px;
gap: 24px;
```

**MUST use consistent spacing patterns:**
- Between form fields: `var(--spacing-lg)`
- Between sections: `var(--spacing-xl)` or `var(--spacing-xxl)`
- Card padding: `var(--spacing-lg)` mobile, `var(--spacing-xl)` desktop
- Button groups: `var(--spacing-sm)` or `var(--spacing-md)`
- Modal padding: `var(--spacing-lg)` to `var(--spacing-xl)`

## Component Usage Rules

### BaseButton

**When to use:**
- All clickable actions (save, cancel, delete, etc.)
- Form submissions
- Navigation actions
- Modal actions

**Props:**
- `variant`: 'primary' | 'secondary' | 'danger' | 'warning'
- `size`: 'small' | 'medium' | 'large'
- `disabled`: boolean
- `loading`: boolean
- `fullWidth`: boolean (mobile)

**Example:**
```vue
<BaseButton
  variant="primary"
  size="small"
  :disabled="loading"
  :loading="saving"
  @click="handleSave"
>
  {{ saving ? $t('common.saving') : $t('common.save') }}
</BaseButton>
```

### StatusBadge

**When to use:**
- Displaying registration status
- Displaying payment status
- Any status that maps to: incomplete, complete, paid, forfait

**Props:**
- `status`: 'incomplete' | 'complete' | 'paid' | 'forfait'
- `size`: 'small' | 'medium'

**Example:**
```vue
<StatusBadge :status="boat.registration_status" size="medium" />
```

### FormGroup

**When to use:**
- All form input fields
- Text inputs, selects, textareas, date inputs
- Any field that needs a label and error display

**Props:**
- `label`: string (required)
- `required`: boolean
- `error`: string
- `helpText`: string

**Slots:**
- `default`: Input element
- `help`: Custom help content

**Example:**
```vue
<FormGroup
  :label="$t('crew.form.firstName')"
  :required="true"
  :error="errors.first_name"
  :help-text="$t('crew.form.firstNameHint')"
>
  <input
    v-model="form.first_name"
    type="text"
    required
    @blur="validateField('first_name')"
  />
</FormGroup>
```

### MessageAlert

**When to use:**
- Form-level error messages
- Success messages after actions
- Warning messages
- Info messages

**Props:**
- `type`: 'error' | 'success' | 'warning' | 'info'
- `message`: string (required)
- `dismissible`: boolean
- `autoDismiss`: boolean (5 seconds)

**Example:**
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

### DataCard

**When to use:**
- Displaying data in card view
- Mobile-first layouts
- Dashboard widgets

**Props:**
- `title`: string
- `status`: string
- `statusBadge`: boolean

**Slots:**
- `header`: Custom header
- `default`: Card body
- `actions`: Action buttons

**Example:**
```vue
<DataCard :title="boat.boat_number" :status="boat.registration_status">
  <div class="card-field">
    <span class="label">{{ $t('boat.eventType') }}:</span>
    <span class="value">{{ boat.event_type }}</span>
  </div>
  
  <template #actions>
    <BaseButton size="small" variant="secondary" @click="viewBoat">
      {{ $t('common.view') }}
    </BaseButton>
    <BaseButton size="small" variant="danger" @click="deleteBoat">
      {{ $t('common.delete') }}
    </BaseButton>
  </template>
</DataCard>
```

### BaseModal

**When to use:**
- Create/edit forms
- Confirmation dialogs
- Detail views
- Any overlay content

**Props:**
- `show`: boolean (required)
- `title`: string
- `size`: 'small' | 'medium' | 'large'
- `closeOnOverlay`: boolean (default: true)

**Slots:**
- `header`: Custom header
- `default`: Modal body
- `footer`: Action buttons

**Example:**
```vue
<BaseModal
  :show="showModal"
  :title="$t('boat.createTitle')"
  @close="showModal = false"
>
  <FormGroup label="Field">
    <input v-model="form.field" />
  </FormGroup>
  
  <template #footer>
    <BaseButton variant="secondary" @click="showModal = false">
      {{ $t('common.cancel') }}
    </BaseButton>
    <BaseButton variant="primary" @click="handleSave">
      {{ $t('common.save') }}
    </BaseButton>
  </template>
</BaseModal>
```

## Examples of Correct vs Incorrect

### Example 1: Button Styling

**❌ WRONG:**
```vue
<button class="btn btn-primary" style="padding: 8px 16px">
  Save
</button>
```

**✅ CORRECT:**
```vue
<BaseButton variant="primary" size="small" @click="save">
  Save
</BaseButton>
```

### Example 2: Status Display

**❌ WRONG:**
```vue
<span class="badge" :class="statusClass" style="text-transform: uppercase">
  {{ status }}
</span>
```

**✅ CORRECT:**
```vue
<StatusBadge :status="status" size="medium" />
```

### Example 3: Form Field

**❌ WRONG:**
```vue
<div class="form-group">
  <label>Name *</label>
  <input v-model="name" style="padding: 12px; border: 1px solid #ddd" />
  <span class="error" style="color: red">{{ errors.name }}</span>
</div>
```

**✅ CORRECT:**
```vue
<FormGroup :label="$t('form.name')" :required="true" :error="errors.name">
  <input v-model="name" type="text" required />
</FormGroup>
```

### Example 4: Card vs Table Consistency

**❌ WRONG - Inconsistent button sizes:**
```vue
<!-- Card view -->
<BaseButton size="medium">View</BaseButton>

<!-- Table view -->
<BaseButton size="small">View</BaseButton>
```

**✅ CORRECT - Consistent button sizes:**
```vue
<!-- Card view -->
<BaseButton size="small">View</BaseButton>

<!-- Table view -->
<BaseButton size="small">View</BaseButton>
```

## UI Consistency Checklist

Before committing any frontend code, verify:

### Design Tokens
- [ ] No hardcoded colors (all use `var(--color-*)`)
- [ ] No hardcoded spacing (all use `var(--spacing-*)`)
- [ ] No hardcoded font sizes (all use `var(--font-size-*)`)
- [ ] No hardcoded font weights (all use `var(--font-weight-*)`)

### Components
- [ ] All buttons use `BaseButton` component
- [ ] All status badges use `StatusBadge` component
- [ ] All form fields use `FormGroup` component
- [ ] All messages use `MessageAlert` component
- [ ] All modals use `BaseModal` component

### Sizing
- [ ] Card view buttons use `size="small"`
- [ ] Table view buttons use `size="small"`
- [ ] Modal buttons use `size="medium"`
- [ ] Status badges use `size="medium"` (default)

### Colors
- [ ] Button variants match action types (primary/secondary/danger/warning)
- [ ] Status badges use correct status values
- [ ] All colors come from design tokens

### Layout
- [ ] Card and table views show same data
- [ ] Card and table views use same button sizes
- [ ] Card and table views use same button variants
- [ ] Responsive behavior works on mobile and desktop

### Accessibility
- [ ] All touch targets are at least 44px
- [ ] Mobile inputs use 16px font size
- [ ] Proper contrast ratios maintained
- [ ] Keyboard navigation works

## Resources

- **Design System Documentation**: `docs/design-system.md`
- **Design System Showcase**: Visit `/design-system` in the app
- **Design Tokens**: `frontend/src/assets/design-tokens.css`
- **Components**: `frontend/src/components/`

## Questions?

If you're unsure about how to implement something:
1. Check the Design System Showcase (`/design-system`)
2. Review the Design System Documentation (`docs/design-system.md`)
3. Look at similar pages for patterns
4. Ask the team for guidance

---

**Remember**: Consistency is key. When in doubt, follow existing patterns and use the design system components.

