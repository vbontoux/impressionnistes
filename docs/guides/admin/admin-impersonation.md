# Admin Impersonation Feature

**Status:** ✅ Complete and Production-Ready  
**Last Updated:** January 5, 2026

## Overview

The Admin Impersonation feature allows administrators to view and manage data as if they were another team manager. This is useful for:
- Troubleshooting user issues
- Providing support without requiring credentials
- Testing features from a team manager's perspective
- Verifying data visibility and permissions

## How It Works

### User Experience

1. **Starting Impersonation**
   - Admin navigates to the Admin Dashboard (`/admin`)
   - Finds the "Impersonate Team Manager" card
   - Selects a team manager from the dropdown
   - Page reloads with the selected team manager's data

2. **While Impersonating**
   - A purple banner appears at the top showing who you're viewing as
   - All data (crew members, boats, payments) belongs to the impersonated user
   - Navigation between pages preserves impersonation
   - URL includes `?team_manager_id=xxx` parameter

3. **Exiting Impersonation**
   - Click "Exit Impersonation ✕" button in the purple banner
   - Page reloads and returns to admin's own data
   - Banner disappears

### Technical Implementation

**Frontend:**
- `AdminImpersonationCard.vue` - Card on admin dashboard for selecting team manager
- `AdminImpersonationBar.vue` - Purple banner shown when impersonating
- `authStore.js` - Manages impersonation state in localStorage
- `apiClient.js` - Reads `team_manager_id` from URL and adds to all API requests
- `App.vue` - Navigation guard preserves URL parameter across routes

**Backend:**
- `@require_team_manager_or_admin_override` decorator in `auth_utils.py`
- Decorator checks for `team_manager_id` query parameter
- Sets `event['_effective_user_id']` for Lambda functions to use
- Audit logging for all impersonation actions

**Updated Lambda Functions:**
- `get_boat_registration.py`
- `get_crew_member.py`
- `assign_seat.py`
- `get_cox_substitutes.py`
- All list endpoints (already had the decorator)

## Security

- Only users in the `admins` Cognito group can impersonate
- Non-admins attempting impersonation receive 403 Forbidden
- All impersonation actions are logged to CloudWatch with:
  - Admin user ID and email
  - Impersonated user ID
  - Action performed
  - Timestamp

## Testing

### Manual Testing Checklist

- [ ] Admin can see impersonation card on dashboard
- [ ] Dropdown shows all team managers
- [ ] Selecting a team manager loads their data
- [ ] Purple banner appears with correct name
- [ ] Browser refresh (F5) maintains impersonation
- [ ] Menu navigation preserves impersonation
- [ ] Can view/edit boats while impersonating
- [ ] Can view/edit crew members while impersonating
- [ ] Exit button returns to admin data
- [ ] Banner disappears after exit
- [ ] Mobile layout works correctly

### Integration Tests

Backend integration tests are located in `tests/integration/test_admin_impersonation.py`:
- Test admin can impersonate team manager
- Test non-admin cannot impersonate
- Test impersonation with invalid team manager ID
- Test audit logging

Run tests:
```bash
cd infrastructure
make test
```

## Troubleshooting

### Issue: Wrong data loads after refresh

**Symptom:** Browser refresh shows admin's data instead of impersonated user's data.

**Solution:** The URL is the source of truth. Check that:
1. URL has `?team_manager_id=xxx` parameter
2. `apiClient.js` reads from URL (not localStorage)
3. Lambda functions use `event['_effective_user_id']`

### Issue: Impersonation lost when navigating

**Symptom:** URL parameter disappears when clicking menu items.

**Solution:** Navigation guard in `App.vue` should preserve the parameter. Check:
1. `router.beforeEach` in App.vue adds parameter to all routes
2. Guard runs before navigation completes

### Issue: 404 error when viewing boat/crew details

**Symptom:** Can see list but clicking on item shows 404.

**Solution:** Lambda function needs admin override decorator:
1. Import `require_team_manager_or_admin_override`
2. Use decorator instead of `require_team_manager`
3. Read `event['_effective_user_id']` instead of calling `get_user_from_event()`

## Files Modified

**Frontend:**
- `frontend/src/components/AdminImpersonationCard.vue` (new)
- `frontend/src/components/AdminImpersonationBar.vue` (modified)
- `frontend/src/services/apiClient.js` (modified)
- `frontend/src/stores/authStore.js` (modified)
- `frontend/src/App.vue` (modified)
- `frontend/src/views/admin/AdminDashboard.vue` (modified)
- `frontend/src/locales/en.json` (modified)
- `frontend/src/locales/fr.json` (modified)

**Backend:**
- `functions/layer/python/auth_utils.py` (decorator already existed)
- `functions/boat/get_boat_registration.py` (modified)
- `functions/boat/assign_seat.py` (modified)
- `functions/boat/get_cox_substitutes.py` (modified)
- `functions/crew/get_crew_member.py` (modified)

**Tests:**
- `tests/integration/test_admin_impersonation.py` (existing)

## Deployment

The feature is deployed and requires both backend and frontend updates:

```bash
# Backend
cd infrastructure
make deploy-backend-dev

# Frontend (if needed)
cd frontend
npm run build
# Deploy via CDK or manual upload
```

## Future Enhancements

Potential improvements for future iterations:
- Add impersonation history/audit log viewer in admin UI
- Add "quick switch" between recently impersonated users
- Add impersonation duration tracking
- Add notification to impersonated user (optional)
