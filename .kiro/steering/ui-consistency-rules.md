---
inclusion: always
---

# UI Consistency Rules

## Critical Rules for Design System Usage

### 1. NEVER Duplicate CSS Classes

**Before writing ANY CSS class:**
1. Check if it exists in `frontend/src/assets/design-tokens.css`
2. Check if it exists in other components
3. Check if a similar pattern exists that can be reused

**If the same styling is needed in multiple places:**
- Add it to `design-tokens.css` as a utility class
- Use the utility class in all components
- NEVER copy-paste CSS between files

### 2. ALWAYS Use Design Tokens

**For colors:**
- Use `var(--color-primary)` NOT `#007bff`
- Use `var(--color-success)` NOT `#28a745`
- Use `var(--color-warning)` NOT `#ffc107`
- Use `var(--color-danger)` NOT `#dc3545`
- Use `var(--color-secondary)` NOT `#6c757d`

**For spacing:**
- Use `var(--spacing-xs)` through `var(--spacing-3xl)`
- NEVER use hardcoded values like `8px` or `1rem`

**For typography:**
- Use `var(--font-size-xs)` through `var(--font-size-3xl)`
- Use `var(--font-weight-normal)`, `var(--font-weight-medium)`, etc.

**For component-specific tokens:**
- Use `var(--badge-padding)`, `var(--badge-font-size)`, etc.
- Use `var(--button-padding-sm)`, `var(--button-min-height-md)`, etc.

### 3. Component Sizing Standards

**Buttons:**
- Card view buttons: `size="small"`
- Table view buttons: `size="small"`
- Modal action buttons: `size="medium"`

**Status Badges:**
- Always use `StatusBadge` component
- Default size is "medium" (matches design tokens)
- NEVER create custom badge styling

**Custom Badges (non-status):**
- MUST use `display: inline-block` or `display: inline-flex`
- MUST use `width: fit-content` to prevent full-width stretching
- NEVER use `text-transform: uppercase` (use sentence case)
- Use design system colors only

### 4. Utility Classes in design-tokens.css

**Current utility classes available:**
- `.boat-number-text`, `.boat-number-cell` - Blue semibold text for boat numbers
- `.no-race-text`, `.no-race-cell` - Grey italic text for empty states

**When to add new utility classes:**
- Pattern is used in 2+ components
- Pattern is simple and reusable (text color, font weight, etc.)
- Pattern follows design system principles

### 5. Checklist Before Committing Code

- [ ] No hardcoded colors (all use `var(--color-*)`)
- [ ] No hardcoded spacing (all use `var(--spacing-*)`)
- [ ] No hardcoded font sizes (all use `var(--font-size-*)`)
- [ ] No duplicate CSS classes across files
- [ ] All buttons use `BaseButton` component
- [ ] All status badges use `StatusBadge` component
- [ ] All utility classes are in `design-tokens.css`
- [ ] Component sizing follows standards (size="small" for cards/tables)
- [ ] NO `text-transform: uppercase` on badges (use sentence case)
- [ ] All badges use `width: fit-content` (not full width)

## Quick Reference

### Design Token Categories

```css
/* Colors */
--color-primary, --color-success, --color-warning, --color-danger, --color-secondary
--color-light, --color-dark, --color-muted, --color-border

/* Spacing */
--spacing-xs (4px), --spacing-sm (8px), --spacing-md (12px), --spacing-lg (16px)
--spacing-xl (24px), --spacing-xxl (32px), --spacing-3xl (48px)

/* Typography */
--font-size-xs (12px), --font-size-sm (13px), --font-size-base (14px)
--font-size-md (15.2px), --font-size-lg (16px), --font-size-xl (18px)
--font-weight-normal (400), --font-weight-medium (500), --font-weight-semibold (600)

/* Badges */
--badge-padding (0.25rem 0.75rem), --badge-font-size (0.75rem), --badge-border-radius (12px)

/* Buttons */
--button-padding-sm, --button-padding-md, --button-padding-lg
--button-min-height-sm (36px), --button-min-height-md (44px)
```

### Common Patterns

**Blue semibold text (boat numbers, IDs):**
```html
<span class="boat-number-text">{{ value }}</span>
```

**Grey italic text (empty states):**
```html
<span class="no-race-text">-</span>
```

**Status badge:**
```html
<StatusBadge :status="boat.registration_status" size="medium" />
```

**Button in card/table:**
```html
<BaseButton size="small" variant="secondary" @click="handleAction">
  Action
</BaseButton>
```

## Why This Matters

1. **Consistency**: Users see the same UI patterns everywhere
2. **Maintainability**: Change once in design-tokens.css, updates everywhere
3. **Performance**: Smaller CSS bundle, better caching
4. **Developer Experience**: Clear patterns, less decision-making
5. **Quality**: Fewer bugs from inconsistent styling

## Red Flags to Watch For

🚩 Writing the same CSS class in multiple files
🚩 Using hardcoded hex colors like `#007bff`
🚩 Using hardcoded pixel values like `8px` or `1rem`
🚩 Creating custom badge styling instead of using `StatusBadge`
🚩 Creating custom button styling instead of using `BaseButton`
🚩 Different button sizes in similar contexts (all cards should match)
🚩 Different badge sizes across the application
🚩 Using `text-transform: uppercase` on badges (ALWAYS use sentence case)
🚩 Badges taking full width (ALWAYS use `width: fit-content`)

If you see any of these, STOP and refactor to use the design system properly.
