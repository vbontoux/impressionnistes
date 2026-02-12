# Admin Boat License Status - Summary

## Feature Overview

Add a "License" column to the admin boat list that shows whether all crew members in a boat have verified licenses.

**Status Display:**
- 🟢 **"Verified"** - ALL crew members have valid licenses
- 🔴 **"Invalid"** - ANY crew member has invalid or unverified license
- ⚪ **"-"** - No crew assigned to boat

**Locations:**
- Admin Boats table view (new column)
- Admin Boats card view (new detail row)

## Quick Start

1. **Review Requirements:** `.kiro/specs/admin-boat-license-status/requirements.md`
2. **Review Design:** `.kiro/specs/admin-boat-license-status/design.md`
3. **Start Implementation:** `.kiro/specs/admin-boat-license-status/tasks.md`

## Task Summary

### Backend (3 sections, ~1h 10min)
1. **Add Combined License Status** (30 min)
   - Add `calculate_crew_license_status()` function
   - Modify lambda handler to include status
   
2. **Write Tests** (30 min)
   - Unit tests for calculation function
   - Integration test for API endpoint
   
3. **Deploy** (10 min)
   - Deploy to dev and prod

### Frontend (5 sections, ~1h 5min)
4. **Add License Column to Table** (15 min)
   - Update table columns
   - Add template slot
   
5. **Add License Status to Card View** (15 min)
   - Add detail row to cards
   
6. **Add Badge Styles** (15 min)
   - Add verification badge CSS
   
7. **Add Internationalization** (10 min)
   - English and French translations
   
8. **Deploy** (10 min)
   - Deploy to dev and prod

### Testing (4 sections, ~50min)
9. **Manual Testing - Table View** (15 min)
10. **Manual Testing - Card View** (15 min)
11. **Manual Testing - Integration** (15 min)
12. **Documentation** (5 min)

**Total Estimated Time: ~3 hours**

## Files to Modify

### Backend (1 file)
- `functions/admin/admin_list_all_boats.py` - Add status calculation

### Frontend (3 files)
- `frontend/src/views/admin/AdminBoats.vue` - Add column, card view, styles
- `frontend/src/locales/en.json` - English translations
- `frontend/src/locales/fr.json` - French translations

### Tests (1 file)
- `tests/integration/test_admin_boat_license_status.py` - New test file

## Key Design Decisions

1. **Backend Calculation:** Status is calculated on backend for consistency
2. **No Sorting:** Column is not sortable (informational only)
3. **No Filtering:** No filter dropdown for license status
4. **Not Clickable:** Badge is informational only, no drill-down
5. **Reuse Styles:** Badge styles match existing verification badges
6. **Always Visible:** Column visible on all screen sizes

## Success Criteria

✅ "License" column appears in admin boats table  
✅ Badge shows "Verified" (green) when ALL crew verified  
✅ Badge shows "Invalid" (red) when ANY crew unverified  
✅ Badge shows "-" when no crew assigned  
✅ Card view shows same license status  
✅ Badge styling matches crew member list  
✅ Status updates when crew verification changes  
✅ Works on mobile devices  

## Dependencies

- Existing license verification on crew members
- Existing admin boats endpoint
- Existing boat seat data structure
- Existing verification badge styles

## Next Steps

1. **Start with Backend:** Begin with Section 1 in tasks.md
2. **Test Backend:** Complete Section 2 before moving to frontend
3. **Deploy Backend:** Complete Section 3 before frontend work
4. **Frontend Implementation:** Sections 4-8
5. **Manual Testing:** Sections 9-11
6. **Documentation:** Section 12

## Questions?

- **Requirements:** See `requirements.md` for detailed acceptance criteria
- **Design:** See `design.md` for technical implementation details
- **Tasks:** See `tasks.md` for step-by-step implementation guide
