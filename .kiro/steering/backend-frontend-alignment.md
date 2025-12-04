---
inclusion: always
---

# Backend-Frontend Alignment Rule

## Purpose
Ensure that changes made to backend logic are always reflected in the frontend to maintain consistency across the full stack.

## Rule

WHEN making changes to backend code, you MUST:

1. **After every backend change, explicitly check:**
   - "Does the frontend have corresponding logic that needs to be updated?"
   - "Are there API response changes that affect frontend data handling?"
   - "Do validation rules need to be synchronized?"
   - "Are there new fields or data structures the frontend needs to handle?"

2. **Common areas requiring alignment:**
   - **Business logic calculations:**
     - Age category determination
     - Gender category determination
     - Race eligibility rules
     - Pricing calculations
     - Validation rules
   - **API contracts:**
     - Request/response payload structures
     - New or modified fields
     - Enum values or constants
     - Error codes and messages
   - **Data models:**
     - Database schema changes reflected in frontend types
     - New required/optional fields
     - Field name changes
   - **Validation:**
     - Password requirements
     - Email format rules
     - Input constraints
     - Business rule validations

3. **Alignment locations:**
   - **Backend:** `functions/shared/`, `functions/layer/python/`
   - **Frontend:** `frontend/src/utils/`, `frontend/src/composables/`
   - **Types:** Frontend TypeScript interfaces or JSDoc types
   - **Constants:** Shared enums, categories, configuration values

4. **Verification checklist:**
   - [ ] Backend logic updated
   - [ ] Corresponding frontend logic updated (if exists)
   - [ ] API contracts aligned (request/response)
   - [ ] Validation rules synchronized
   - [ ] Constants and enums matched
   - [ ] Error handling consistent

## Process

After making a backend change:

1. **Identify the change type:**
   - Logic change → Check `frontend/src/utils/` for corresponding functions
   - API change → Check components that call this endpoint
   - Validation change → Check form validation in frontend
   - Data model change → Check TypeScript types and data handling

2. **Search for frontend usage:**
   - Use grep/search to find related frontend code
   - Look for similar function names or logic patterns
   - Check API service files for endpoint calls

3. **Update frontend accordingly:**
   - Apply the same logic changes
   - Update API calls and response handling
   - Synchronize validation rules
   - Update types and interfaces

4. **Explicitly state what was aligned:**
   - "I've updated the backend age category calculation in `race_eligibility.py`"
   - "I'm now checking the frontend... Found corresponding logic in `raceEligibility.js`"
   - "Updating frontend to match the backend changes..."
   - "Both backend and frontend are now aligned."

## Examples

### Example 1: Age Category Calculation

**Backend change:**
```python
# functions/shared/race_eligibility.py
def calculate_age_category(members):
    rower_ages = [m['age'] for m in members if m['role'] != 'Barreur']
    max_age = max(rower_ages) if rower_ages else 0
    return 'VM' if max_age >= 55 else 'SM'
```

**Must check and update frontend:**
```javascript
// frontend/src/utils/raceEligibility.js
export function calculateAgeCategory(members) {
  const rowerAges = members
    .filter(m => m.role !== 'Barreur')
    .map(m => m.age)
  const maxAge = rowerAges.length > 0 ? Math.max(...rowerAges) : 0
  return maxAge >= 55 ? 'VM' : 'SM'
}
```

### Example 2: API Response Structure

**Backend change:**
```python
# Added new field to crew response
return {
    'crew_id': crew.crew_id,
    'crew_name': crew.crew_name,
    'age_category': crew.age_category,  # NEW FIELD
}
```

**Must check and update frontend:**
```javascript
// Update components that display crew data
<div>{{ crew.age_category }}</div>  // Add display of new field

// Update types if using TypeScript
interface Crew {
  crew_id: string
  crew_name: string
  age_category: string  // NEW FIELD
}
```

### Example 3: Validation Rules

**Backend change:**
```python
# Updated password requirements
PASSWORD_MIN_LENGTH = 12  # Changed from 8
REQUIRE_SPECIAL_CHAR = True  # NEW
```

**Must check and update frontend:**
```javascript
// frontend/src/components/RegisterForm.vue
const passwordRules = [
  v => v.length >= 12 || 'Minimum 12 caractères',  // Updated
  v => /[!@#$%^&*]/.test(v) || 'Caractère spécial requis'  // NEW
]
```

## Red Flags (Don't Skip Frontend Check)

⚠️ **ALWAYS check frontend when you:**
- Modify calculation logic in `functions/shared/`
- Change API response structures
- Update validation rules
- Modify constants or enums
- Change data models
- Update business rules
- Modify error handling

## Accountability

Before marking a task complete, explicitly state:
- "Backend updated: [what changed]"
- "Frontend checked: [what was found and updated]"
- "Both layers are now aligned."

If no frontend changes are needed, explicitly state why:
- "No frontend changes needed - this is backend-only infrastructure code"
- "No frontend changes needed - frontend doesn't implement this logic locally"
