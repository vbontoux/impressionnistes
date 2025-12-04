---
inclusion: always
---

# Incremental Bug Fixing Rule

## Purpose
Fix bugs one at a time with user testing between each fix to ensure quality and avoid introducing new issues.

## Rule

WHEN correcting bugs, you MUST:

1. **Work on ONE bug at a time:**
   - Identify the specific bug to fix
   - Make the minimal changes needed to fix that bug
   - Stop after completing the fix

2. **Wait for user testing:**
   - After implementing the fix, explicitly tell the user: "I've fixed [bug description]. Please test this change before we move to the next issue."
   - Do NOT proceed to the next bug automatically
   - Wait for user confirmation that the fix works

3. **Only proceed when confirmed:**
   - User says "it works" or "looks good" → Move to next bug
   - User reports issues → Debug and fix the current bug first
   - User asks to move on → Proceed to next bug

4. **Track progress:**
   - Keep a mental note of which bugs are fixed and which remain
   - If multiple bugs were reported, remind the user which ones are left

## Why This Matters

- **Quality assurance:** Each fix is tested before moving forward
- **Avoid cascading issues:** Don't introduce new bugs while fixing old ones
- **Clear communication:** User knows exactly what changed and can test effectively
- **Easier debugging:** If something breaks, we know exactly what caused it
- **User control:** User decides the pace and priority

## Examples

✅ **DO:**
```
Bug 1: Age category calculation is wrong
→ Fix age category calculation
→ "I've fixed the age category calculation to exclude coxswains. Please test this before we move to the next issue."
→ Wait for user confirmation
→ User: "Works great!"
→ Bug 2: Gender category is incorrect
→ Fix gender category
→ "I've fixed the gender category logic. Please test this change."
```

❌ **DON'T:**
```
Bug 1: Age category calculation is wrong
Bug 2: Gender category is incorrect
Bug 3: UI spacing issues
→ Fix all three bugs at once
→ Deploy everything
→ User finds new issues but doesn't know which change caused them
```

## Exception

If bugs are clearly related or in the same file/function and fixing them together makes sense, you can ask:
"These bugs are related. Would you like me to fix them together, or one at a time?"