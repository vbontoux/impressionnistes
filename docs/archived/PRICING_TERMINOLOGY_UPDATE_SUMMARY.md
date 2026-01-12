# Pricing Terminology Update Summary

**Date:** 2026-01-10  
**Status:** Complete

## Overview

Updated pricing terminology across the application to provide clearer, more user-friendly language while maintaining existing code structure. This was a documentation and UI-only update - no code refactoring was performed.

## Strategy

**Hybrid Approach:** Keep internal variable names unchanged in code, but use clear terminology in user-facing areas and documentation.

### Internal Code (Unchanged)
- `base_seat_price` - kept as-is in Python/JavaScript code
- `rental_price` / `boat_rental_price_crew` - kept as-is in code
- `boat_rental_multiplier_skiff` - kept as-is in code

### User-Facing (Updated)
- **"Participation Fee"** (EN) / **"Frais de participation"** (FR) - replaces "Base Seat Price" in UI
- **"Boat Rental (per seat)"** (EN) / **"Location bateau (par place)"** (FR) - replaces "Rental Price" in UI

## What Each Fee Covers

### Participation Fee (`base_seat_price`)
- Event registration
- Insurance coverage
- Organization costs
- Timing services
- **Who pays:** External club members only (RCPM = €0)
- **Default:** €20 per person

### Boat Rental Fee (`rental_price`)
- Use of RCPM-owned boat equipment (hull, oars, etc.)
- Physical seat in an RCPM boat
- **Who pays:** Non-RCPM members using RCPM boats
- **Who doesn't pay:** RCPM members, or anyone using their own boat
- **Default:** €20 per seat (crew boats), €50 for skiffs (2.5x multiplier)

## Files Updated

### Documentation
1. ✅ **`docs/reference/terminology.md`** - NEW
   - Comprehensive glossary with pricing definitions
   - Examples and scenarios
   - Usage guidelines

2. ✅ **`.kiro/specs/impressionnistes-registration-system/requirements.md`**
   - Added pricing terminology section
   - Updated all pricing references throughout
   - Added code/UI mapping table
   - Clarified pricing examples

3. ✅ **`.kiro/specs/impressionnistes-registration-system/design.md`**
   - Added pricing terminology section
   - Updated pricing calculation comments
   - Added implementation guidelines with examples

### Frontend - Locale Files
4. ✅ **`frontend/src/locales/fr.json`**
   - Updated pricing configuration labels
   - Changed "Prix de base par siège" → "Frais de participation"
   - Changed "Prix location bateau" → "Location bateau (par place)"
   - Added clarifying help text

5. ✅ **`frontend/src/locales/en.json`**
   - Updated pricing configuration labels
   - Changed "Base Seat Price" → "Participation Fee"
   - Changed "Crew Boat Rental Price" → "Boat Rental (per seat)"
   - Added clarifying help text

### Backend - Code Comments
6. ✅ **`functions/shared/pricing.py`**
   - Added terminology note in module docstring
   - Updated constant comments
   - Added clarifying comments in pricing calculation function

## Key Changes by Section

### Requirements Document
- Added "Pricing Terminology" section with mapping table
- Updated 15+ references from "Base_Seat_Price" to "Participation Fee (`base_seat_price`)"
- Updated references from "Seat_Rental" to "Boat Rental fees (`rental_price`)"
- Added pricing examples with clear explanations
- Linked to terminology glossary

### Design Document
- Added comprehensive "Pricing Terminology" section
- Updated pricing calculation function comments
- Added implementation examples for backend and frontend
- Clarified who pays what and when

### UI Labels (Locales)
**French:**
- "Tarification de base" → "Frais de participation"
- "Prix de base par siège" → "Frais de participation (clubs externes)"
- "Prix location bateau d'équipe" → "Location bateau (par place)"
- "Siège normal" → "Participation normale"
- Updated help text to explain what fees cover

**English:**
- "Base Pricing" → "Participation Fee"
- "Base Seat Price" → "Participation Fee (external clubs)"
- "Crew Boat Rental Price" → "Boat Rental (per seat)"
- "Regular Seat" → "Regular Participation"
- Updated help text to explain what fees cover

### Backend Comments
- Added module-level terminology note
- Updated constant comments to clarify purpose
- Added inline comments in pricing calculations

## Benefits

✅ **No code refactoring** - zero risk of breaking existing functionality  
✅ **Improved clarity** - users see clear, understandable terminology  
✅ **Easy to implement** - only strings and documentation updated  
✅ **Future-proof** - new features can use better naming from the start  
✅ **Consistent documentation** - all docs now use same clear terms  
✅ **Developer-friendly** - comments help developers understand pricing logic  

## Pricing Examples (Updated Terminology)

### Example 1: RCPM crew in RCPM boat
- Participation Fee: €0 (all RCPM members)
- Boat Rental: €0 (RCPM members don't pay)
- **Total: €0**

### Example 2: External club crew (4 rowers) in own boat
- Participation Fee: 4 × €20 = €80
- Boat Rental: €0 (using own boat)
- **Total: €80**

### Example 3: External club crew (4 rowers) in RCPM boat
- Participation Fee: 4 × €20 = €80
- Boat Rental: 4 × €20 = €80
- **Total: €160**

### Example 4: Mixed crew (2 RCPM + 2 external) in RCPM boat
- Participation Fee: 2 × €20 = €40 (only external members)
- Boat Rental: 2 × €20 = €40 (only external members)
- **Total: €80**

### Example 5: External club member in skiff (RCPM boat)
- Participation Fee: 1 × €20 = €20
- Boat Rental: 1 × €50 = €50 (2.5x multiplier)
- **Total: €70**

## For Developers

### When Writing New Code
- **Backend:** Continue using `base_seat_price` and `rental_price` in code
- **Frontend:** Use same variable names, but display "Participation Fee" and "Boat Rental" in UI
- **Comments:** Add clarifying comments when implementing pricing logic
- **Documentation:** Use user-facing terms with code names in parentheses

### Example Pattern
```python
# Backend
def calculate_price(members):
    # base_seat_price = Participation Fee (registration, insurance, organization)
    base_seat_price = config['base_seat_price']
    
    # rental_price = Boat Rental fee per seat (equipment rental)
    rental_price = config['rental_price']
    
    return calculate_total(members, base_seat_price, rental_price)
```

```javascript
// Frontend
<div class="pricing-line">
  <span>{{ $t('pricing.participationFee') }}</span>  <!-- "Participation Fee" -->
  <span>{{ formatCurrency(baseSeatPrice) }}</span>
</div>
```

## Related Documentation

- [Terminology Glossary](../reference/terminology.md) - Complete pricing definitions
- [Requirements](../../.kiro/specs/impressionnistes-registration-system/requirements.md) - Updated requirements
- [Design](../../.kiro/specs/impressionnistes-registration-system/design.md) - Updated design doc

## Next Steps

When implementing boat assignment feature:
1. Use clear naming for new fields (e.g., `assigned_boat_rental_fee_per_seat`)
2. Add clarifying comments in new pricing logic
3. Update locale files with clear user-facing terms
4. Reference this glossary in new documentation

---

**Note:** This update maintains backward compatibility - all existing code continues to work unchanged. Only user-facing labels and documentation were improved.
