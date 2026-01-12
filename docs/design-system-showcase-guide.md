# Design System Showcase

## Purpose

The Design System Showcase (`DesignSystemShowcase.vue`) is a permanent, living style guide that documents all design tokens, components, and patterns used in the Impressionnistes Registration System.

## Location

**Route:** `/design-system`  
**File:** `frontend/src/views/DesignSystemShowcase.vue`

## What It Shows

### 1. Design Tokens
- **Color Palette:** All semantic colors with hex codes and CSS variable names
- **Spacing Scale:** Visual demonstration of all spacing values (xs through 3xl)
- **Typography Scale:** All font sizes with examples
- **Font Weights:** Visual comparison of all weight values

### 2. Component Tokens
- **Button Tokens:** Small, medium, and large button sizing
- **Status Badge Tokens:** All status colors and styling
- **Card Tokens:** Card padding, borders, and shadows

### 3. Responsive Breakpoints
- Mobile, tablet, and desktop breakpoints
- Live indicator showing current viewport size

### 4. Usage Examples
- Code snippets showing how to use design tokens
- Best practices for implementing tokens in components

## When to Update

This page should be updated whenever:
- New design tokens are added to `design-tokens.css`
- New component patterns are established
- New color variants are introduced
- Spacing or typography scales change
- New component-specific tokens are created

## How to Update

1. **Add New Token Demonstrations:**
   - Add a new subsection in the appropriate section
   - Show visual examples of the token in use
   - Include the CSS variable name and value
   - Add code examples if applicable

2. **Add New Components:**
   - Create a new subsection under "Component Tokens"
   - Show all variants and states
   - Document the tokens used
   - Provide usage examples

3. **Update Code Examples:**
   - Keep code examples current with actual implementation
   - Show real-world usage patterns
   - Include both simple and complex examples

## Benefits

### For Developers
- Quick reference for available design tokens
- Visual confirmation that tokens are working
- Code examples for common patterns
- Understanding of the design system structure

### For Designers
- Visual representation of the design system
- Consistency verification across components
- Documentation of design decisions
- Reference for creating new designs

### For the Team
- Single source of truth for design patterns
- Onboarding resource for new team members
- Quality assurance tool
- Communication tool between design and development

## Maintenance

This is a **living document** that should evolve with the design system:

- ✅ Keep it up-to-date with new tokens and components
- ✅ Remove deprecated patterns
- ✅ Add new usage examples as patterns emerge
- ✅ Update documentation when tokens change
- ✅ Ensure all examples use current best practices

## Related Documentation

- **Design Tokens:** `frontend/src/assets/design-tokens.css`
- **Design System Docs:** `docs/design-system.md` (to be created in Task 22)
- **UI Consistency Steering:** `.kiro/steering/ui-consistency.md` (to be created in Task 23)

## Access

The showcase is accessible to all users (no authentication required) at:
```
http://localhost:3001/design-system (development)
https://your-domain.com/design-system (production)
```

Consider making this page:
- Accessible only in development/staging environments, OR
- Available to all users as a public design system reference

## Future Enhancements

Potential improvements for the showcase:

1. **Interactive Examples:**
   - Editable code examples
   - Live preview of token changes
   - Toggle between light/dark modes

2. **Component Library:**
   - Add actual component examples (BaseButton, StatusBadge, etc.)
   - Show all component states (hover, active, disabled)
   - Interactive component playground

3. **Accessibility:**
   - Color contrast checker
   - Touch target size validator
   - Screen reader compatibility notes

4. **Export Features:**
   - Download design tokens as JSON
   - Export color palette for design tools
   - Generate CSS/SCSS variables

5. **Search and Filter:**
   - Search for specific tokens
   - Filter by category
   - Quick navigation

## Notes

- This page uses only design tokens for styling (no hardcoded values)
- It serves as both documentation and validation
- Keep it simple and focused on the design system
- Avoid adding application-specific content
