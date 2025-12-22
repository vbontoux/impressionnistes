# Frontend Utilities

This directory contains reusable JavaScript utility functions and constants.

## Available Utilities

### Responsive Design Utilities

**File**: `responsive.js`

Provides standardized breakpoint values, media queries, and helper functions for responsive design.

**Documentation**: See [docs/guides/development/responsive-design.md](../../../docs/guides/development/responsive-design.md)

**Quick Import**:
```javascript
import { 
  BREAKPOINTS, 
  MEDIA_QUERIES,
  TOUCH_TARGET_MIN,
  matchesBreakpoint,
  getCurrentBreakpoint
} from '@/utils/responsive'
```

### Other Utilities

- **dateFormatter.js** - Date formatting utilities
- **raceEligibility.js** - Race eligibility calculation logic
- **rentalPricing.js** - Rental pricing calculations

## Documentation

For comprehensive guides on using these utilities:

- **Responsive Design**: [docs/guides/development/responsive-design.md](../../../docs/guides/development/responsive-design.md)
- **Responsive Table Patterns**: [docs/guides/development/responsive-table-patterns.md](../../../docs/guides/development/responsive-table-patterns.md)

## Related Resources

- **Vue Composables**: `frontend/src/composables/`
- **CSS Utilities**: `frontend/src/assets/responsive.css`
- **Components**: `frontend/src/components/`

