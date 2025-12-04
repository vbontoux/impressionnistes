---
inclusion: always
---

# Requirements Synchronization Rule

## Purpose
Ensure that requirements documentation stays aligned with implementation changes.

## Rule

WHEN you make changes to business logic, algorithms, or functional behavior in the codebase, you MUST:

1. **Identify if it affects requirements:**
   - Changes to calculation logic (age categories, gender categories, pricing, eligibility, etc.)
   - Changes to business rules or validation logic
   - Changes to user workflows or processes
   - Changes to data structures that affect functionality

2. **Ask the user:**
   - "This change affects the business logic. Would you like me to update the requirements documentation to reflect this change?"
   - Wait for explicit confirmation (yes/no)

3. **If user says YES:**
   - Locate the relevant section in `.kiro/specs/impressionnistes-registration-system/requirements.md`
   - Update the requirements to accurately reflect the new implementation
   - Update both:
     - Acceptance criteria in functional requirements
     - Reference data in appendices if applicable
   - Ensure the language is clear and matches the existing requirements style

4. **If user says NO:**
   - Proceed without updating requirements
   - Note that requirements may be out of sync

## Examples of Changes That Require Requirements Updates

✅ **DO ask about requirements updates for:**
- Age category calculation logic changes (e.g., excluding coxswains)
- Gender category determination changes (e.g., rowers-only calculation)
- Pricing calculation modifications
- Race eligibility rule changes
- Validation logic updates
- Workflow or process changes

❌ **DON'T ask for:**
- UI styling changes (colors, fonts, spacing)
- Bug fixes that restore intended behavior
- Performance optimizations that don't change logic
- Code refactoring without behavior changes

## Requirements File Location

Primary requirements file: `.kiro/specs/impressionnistes-registration-system/requirements.md`