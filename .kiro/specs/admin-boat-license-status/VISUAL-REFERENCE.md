# Admin Boat License Status - Visual Reference

## Table View

### Before (Current)
```
| Boat # | Event | Type | Race      | Club      | Status    | Actions |
|--------|-------|------|-----------|-----------|-----------|---------|
| 42-001 | 42km  | 8+   | SM 8+     | Club A    | Complete  | [...]   |
| 42-002 | 42km  | 4+   | VM 4+     | Club B    | Paid      | [...]   |
| 21-001 | 21km  | 2x   | -         | Club C    | Incomplete| [...]   |
```

### After (With License Column)
```
| Boat # | Event | Type | Race      | Club      | License   | Status    | Actions |
|--------|-------|------|-----------|-----------|-----------|-----------|---------|
| 42-001 | 42km  | 8+   | SM 8+     | Club A    | Verified  | Complete  | [...]   |
| 42-002 | 42km  | 4+   | VM 4+     | Club B    | Invalid   | Paid      | [...]   |
| 21-001 | 21km  | 2x   | -         | Club C    | -         | Incomplete| [...]   |
```

**Legend:**
- `Verified` = Green badge (all crew verified)
- `Invalid` = Red badge (any crew unverified)
- `-` = Grey text (no crew assigned)

---

## Card View

### Before (Current)
```
┌─────────────────────────────────────────────┐
│ 42km - 8+                      [Complete]   │
├─────────────────────────────────────────────┤
│ Boat Number: 42-001                         │
│ Race: SM 8+                                 │
│ First Rower: Doe                            │
│ Filled Seats: 9 / 9                         │
│ Average Age: 32 years                       │
│ Team Manager: John Manager                  │
│ Club: Club Name                             │
│                                             │
│ [Assign Boat] [Set Forfait] [Delete]       │
└─────────────────────────────────────────────┘
```

### After (With License Status)
```
┌─────────────────────────────────────────────┐
│ 42km - 8+                      [Complete]   │
├─────────────────────────────────────────────┤
│ Boat Number: 42-001                         │
│ Race: SM 8+                                 │
│ First Rower: Doe                            │
│ Filled Seats: 9 / 9                         │
│ Average Age: 32 years                       │
│ Team Manager: John Manager                  │
│ Club: Club Name                             │
│ License: [Verified]          ← NEW          │
│                                             │
│ [Assign Boat] [Set Forfait] [Delete]       │
└─────────────────────────────────────────────┘
```

---

## Badge Styles

### Verified Badge (Green)
```
┌─────────────┐
│  Verified   │  ← Green background (#d4edda)
└─────────────┘     Dark green text (#155724)
```

### Invalid Badge (Red)
```
┌─────────────┐
│   Invalid   │  ← Red background (#f8d7da)
└─────────────┘     Dark red text (#721c24)
```

### No Crew (Grey)
```
-  ← Grey text (uses .no-race-text class)
```

---

## Status Logic Examples

### Example 1: All Verified ✅
**Crew:**
- Seat 1: John Doe - `verified_valid`
- Seat 2: Jane Smith - `manually_verified_valid`
- Seat 3: Bob Johnson - `verified_valid`

**Result:** `Verified` (green badge)

---

### Example 2: One Unverified ❌
**Crew:**
- Seat 1: John Doe - `verified_valid`
- Seat 2: Jane Smith - `null` (not verified)
- Seat 3: Bob Johnson - `verified_valid`

**Result:** `Invalid` (red badge)

---

### Example 3: One Invalid ❌
**Crew:**
- Seat 1: John Doe - `verified_valid`
- Seat 2: Jane Smith - `verified_invalid`
- Seat 3: Bob Johnson - `verified_valid`

**Result:** `Invalid` (red badge)

---

### Example 4: No Crew ⚪
**Crew:**
- Seat 1: (empty)
- Seat 2: (empty)
- Seat 3: (empty)

**Result:** `-` (grey text)

---

## Mobile View

### Table View (Horizontal Scroll)
```
┌──────────────────────────────────────────┐
│ Boat # │ Event │ License │ Status │ ... │
├────────┼───────┼─────────┼────────┼─────┤
│ 42-001 │ 42km  │Verified │Complete│ ... │
│ 42-002 │ 42km  │ Invalid │  Paid  │ ... │
└────────┴───────┴─────────┴────────┴─────┘
         ← Swipe to see more →
```

### Card View (Stacked)
```
┌─────────────────────────────┐
│ 42km - 8+      [Complete]   │
├─────────────────────────────┤
│ Boat #: 42-001              │
│ Race: SM 8+                 │
│ Club: Club Name             │
│ License: [Verified]         │
│                             │
│ [Assign] [Forfait] [Delete] │
└─────────────────────────────┘
```

---

## Comparison with Crew Member List

### Crew Member List (Individual Status)
```
| Name      | Age | License # | License Status | Actions |
|-----------|-----|-----------|----------------|---------|
| John Doe  | 32  | 123456    | Verified       | [...]   |
| Jane Smith| 28  | 789012    | Invalid        | [...]   |
```

### Boat List (Combined Status)
```
| Boat # | Event | License   | Status    | Actions |
|--------|-------|-----------|-----------|---------|
| 42-001 | 42km  | Invalid   | Complete  | [...]   |
```

**Note:** Boat shows "Invalid" because Jane Smith (one crew member) has invalid license.

---

## Badge Consistency

All verification badges across the application use the same styling:

**Locations:**
1. ✅ Crew Member List (individual status)
2. ✅ Admin License Checker (individual status)
3. ✅ **Admin Boat List (combined status)** ← NEW

**Styling:**
- Same colors (green/red)
- Same padding and border radius
- Same font size and weight
- Same width behavior (fit-content)

---

## Internationalization

### English
- Column: "License"
- Verified: "Verified"
- Invalid: "Invalid"

### French
- Column: "Licence"
- Verified: "Vérifié"
- Invalid: "Invalide"

---

## User Workflow

1. **Admin navigates to Admin Boats page**
2. **Sees "License" column in table**
3. **Identifies boats with unverified crew** (red "Invalid" badge)
4. **Navigates to License Checker page**
5. **Verifies crew member licenses**
6. **Returns to Admin Boats page**
7. **Refreshes page**
8. **Sees updated license status** (green "Verified" badge)

---

## Technical Notes

- **Calculation:** Backend calculates status on-the-fly
- **Performance:** O(n) complexity per boat (n = number of seats)
- **No Migration:** No database changes needed
- **No Caching:** Status recalculated on each request
- **Read-Only:** Badge is not clickable
- **Always Visible:** Column visible on all screen sizes
