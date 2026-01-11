---
inclusion: always
---

# Code Reusability Rule

## Purpose
Avoid code duplication by implementing shared logic once and reusing it across multiple locations.

## Rule

WHEN implementing logic that will be used in multiple places (particularly across multiple frontend pages), you MUST:

1. **Identify shared logic:**
   - Business calculations (age categories, gender categories, pricing, eligibility)
   - Validation rules
   - Data transformations
   - API calls and data fetching patterns
   - Formatting functions (dates, currency, names)

2. **Implement once in a centralized location:**
   - **Frontend utilities:** `frontend/src/utils/` for pure functions
   - **Frontend composables:** `frontend/src/composables/` for Vue composition functions with state
   - **Backend shared:** `functions/shared/` for Python utilities used across Lambda functions
   - **Backend layer:** `functions/layer/python/` for code shared across all Lambdas

3. **Import and reuse:**
   - Import the shared function/module in all locations that need it
   - Never copy-paste logic between files
   - Keep the implementation DRY (Don't Repeat Yourself)

## Benefits

- **Easier maintenance:** Fix bugs or make changes in one place only
- **Consistency:** Same logic produces same results everywhere
- **Faster development:** No need to update multiple files for one change
- **Reduced errors:** Less code duplication means fewer places for bugs to hide

## Examples

✅ **DO centralize:**
- Race eligibility calculations → `frontend/src/utils/raceEligibility.js`
- Age category determination → Shared function in utils
- Gender category logic → Shared function in utils
- API authentication → Composable or service class
- Date formatting → Utility function

❌ **DON'T duplicate:**
- Copy-pasting the same calculation into multiple Vue components
- Reimplementing validation logic in different forms
- Duplicating API call patterns across pages

## Implementation Pattern

**Before (duplicated):**
```javascript
// Page1.vue
const ageCategory = crew.members.reduce((max, m) => Math.max(max, m.age), 0) >= 55 ? 'VM' : 'SM'

// Page2.vue  
const ageCategory = crew.members.reduce((max, m) => Math.max(max, m.age), 0) >= 55 ? 'VM' : 'SM'
```

**After (centralized):**
```javascript
// utils/raceEligibility.js
export function calculateAgeCategory(members) {
  const maxAge = members.reduce((max, m) => Math.max(max, m.age), 0)
  return maxAge >= 55 ? 'VM' : 'SM'
}

// Page1.vue & Page2.vue
import { calculateAgeCategory } from '@/utils/raceEligibility'
const ageCategory = calculateAgeCategory(crew.members)
```