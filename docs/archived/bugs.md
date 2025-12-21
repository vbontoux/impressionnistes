# Bug Tracking - Course des Impressionnistes

This document tracks all reported bugs, issues, and improvements for the registration system.

## Status Legend
- 🔴 **Critical** - Blocks core functionality, needs immediate fix
- 🟠 **High** - Important issue affecting user experience
- 🟡 **Medium** - Issue that should be fixed but has workarounds
- 🟢 **Low** - Minor issue or enhancement
- ✅ **Fixed** - Issue resolved
- 🚫 **Won't Fix** - Issue acknowledged but won't be addressed
- 🔄 **In Progress** - Currently being worked on

---

## Open Bugs

### Critical Issues 🔴

#### Bug #4: License Number Uniqueness
**Status**: Open  
**Reporter**: Philippe Coulloy  
**Date**: 2024-11-27  
**Source**: [raw-files/tests-philippe-2025-11-24.md](raw-files/tests-philippe-2025-11-24.md)

**Description**: System allows the same license number to be used for multiple different crew members

**Steps to Reproduce**:
1. Create crew member with license number "ABC123"
2. Create another crew member with the same license number "ABC123"
3. Both are accepted

**Expected**: System should reject duplicate license numbers  
**Actual**: Duplicate license numbers are allowed

---

### High Priority Issues 🟠

None currently

### Medium Priority Issues 🟡

None currently

### Low Priority Issues 🟢

None currently

---

## Fixed Bugs ✅

### 2024-11-27 - Philippe Test Session

#### Bug #1: Date of Birth Validation
**Severity**: 🔴 Critical  
**Reporter**: Philippe Coulloy  
**Fixed**: 2024-11-27

**Description**: System allowed entering crew members with birth dates in the future (e.g., born in 2026) or too far in the past

**Fix**: Added validation to:
- Prevent future dates
- Enforce minimum age (J14 = born 2011 or later for 2025 season)
- Show clear error messages in French and English

**Files Changed**:
- `frontend/src/components/CrewMemberForm.vue`
- `frontend/src/locales/en.json`
- `frontend/src/locales/fr.json`

---

#### Bug #2: Gender Category Detection
**Severity**: 🔴 Critical  
**Reporter**: Philippe Coulloy  
**Fixed**: 2024-11-27

**Description**: Boat with 2 women and 2 men (50/50) was incorrectly classified as "men" instead of "mixed"

**Fix**: Corrected gender category logic:
- 100% women → "women"
- 100% men → "men"
- Any mix with at least 1 man AND at least 50% women → "mixed"
- More than 50% men → "men"

**Files Changed**:
- `functions/shared/race_eligibility.py`
- `functions/layer/python/race_eligibility.py`

**Tests**: All gender category tests pass

---

#### Bug #3: J14 Rower Restriction
**Severity**: 🔴 Critical  
**Reporter**: Philippe Coulloy  
**Fixed**: 2024-11-27

**Description**: J14 rowers (14-15 years old, born 2010-2011) could be assigned as rowers when they should only be allowed as coxswains

**Fix**: Added validation in seat assignment:
- Check crew member's age category
- If J14, only allow assignment to coxswain positions
- Block assignment to rower positions with clear error message

**Files Changed**:
- `functions/shared/boat_registration_utils.py`
- `functions/layer/python/boat_registration_utils.py`
- `functions/boat/assign_seat.py`

---

#### Bug #0: Payment Webhook Not Configured
**Severity**: 🔴 Critical  
**Reporter**: System testing  
**Fixed**: 2024-11-27

**Description**: Boats were not being marked as paid after successful Stripe payments

**Root Cause**: Stripe webhook endpoint was not configured in Stripe dashboard

**Fix**: Added webhook configuration instructions to STRIPE_SETUP.md

---

## Enhancement Requests

### From Philippe Test Session (2024-11-27)

1. **Forfaits Management** - Allow declaring forfaits and modifying crews after forfait
2. **Password Policy Feedback** - Show green indicator when password meets requirements
3. **Club Dropdown** - Standardized club list for statistics
4. **Default Club** - Pre-fill team manager's club instead of leaving empty
5. **Display Age Category** - Show calculated age category for crew members
6. **License Simplification** - Use medical certificate date + competition checkbox
7. **Position Labels** - Add "avant" for position 1, "nage" for position 4/8
8. **Validate Button Position** - Move to bottom of form instead of top
9. **4+ Options** - Add 4x+ option (currently shows 4+ twice)
10. **Session Timeout** - Increase timeout or save state to prevent data loss
11. **Multi-Club Skiff** - Clarify why non-RCPM members can't register for skiff

---

## Testing Feedback

### Test Session: 2024-11-27
**Tester**: Philippe Coulloy  
**Environment**: dev  
**Source Document**: [raw-files/tests-philippe-2025-11-24.md](raw-files/tests-philippe-2025-11-24.md)

**Summary**: Comprehensive testing of crew and boat registration flows

**Issues Found**: 17 total
- **Fixed**: 3 critical bugs
- **Open**: 1 critical bug (license uniqueness)
- **Enhancements**: 11 improvement suggestions
- **Positive**: Table view appreciated

---

## How to Report a Bug

1. **Add your feedback document** to `raw-requirements/testing/` folder
2. **Create an entry** in this BUGS.md file under the appropriate section
3. **Include**:
   - Clear description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Severity level
   - Your name/contact

## Bug Triage Process

1. **New bugs** are added to "Open Bugs" section with severity
2. **Critical bugs** are addressed immediately
3. **High priority** bugs are scheduled for next sprint
4. **Medium/Low** bugs are backlogged
5. **Fixed bugs** are moved to "Fixed Bugs" section with date
6. **Won't Fix** bugs are documented with reasoning

---

## Notes

- This file is the single source of truth for all bugs and issues
- Check this file before starting new work
- Update status when working on or fixing bugs
- Link to related tasks in tasks.md when creating fixes
- Run `make build-layer` after fixing backend bugs
