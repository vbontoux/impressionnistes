# License Checker Admin Guide

## Overview

The License Checker is an admin tool that verifies the validity of French Rowing Federation (FFAviron) licenses for crew members. It scrapes the FFAviron intranet to check if licenses are active and valid for competition.

## Features

- **Bulk License Checking**: Select multiple crew members and check their licenses in batch
- **Cookie-Based Authentication**: Uses your FFAviron session cookies to access the intranet
- **Real-time Progress**: Shows progress as licenses are being checked
- **Status Tracking**: Displays validation status (valid, invalid, error, unchecked) for each crew member
- **Filtering**: Filter by team manager, status, or search by name/license
- **Detailed Results**: Shows detailed information about each license check

## How to Use

### 1. Get FFAviron Cookies

Before you can check licenses, you need to obtain your FFAviron session cookies:

1. Log into https://intranet.ffaviron.fr in your browser
2. Open Developer Tools (F12)
3. Go to the **Network** tab
4. Perform a license search on the FFAviron site
5. Find the request to `/licences/recherche`
6. Right-click on the request → Copy → Copy as cURL
7. Extract the Cookie header value from the cURL command

**Example Cookie String:**
```
_session=abc123; user_token=xyz789; remember_token=def456
```

### 2. Configure Cookies in the Page

1. Navigate to **Admin → Vérification Licences**
2. Paste your cookie string in the **Cookies FFAviron** textarea
3. The cookies will be used for all subsequent license checks

### 3. Select Crew Members

1. Use the checkboxes to select crew members you want to verify
2. You can:
   - Select individual members
   - Select all visible members (filtered view)
   - Use filters to narrow down the list

### 4. Check Licenses

1. Click **Vérifier X licence(s)** button
2. The system will check each selected license sequentially
3. Progress bar shows current status
4. Results appear in real-time in the table

### 5. Review Results

Each crew member will show one of these statuses:

- **✓ Valide**: License is active and valid for competition
- **✗ Invalide**: License exists but is not active or not for competition
- **⚠ Erreur**: Error occurred during check (network, parsing, etc.)
- **Non vérifié**: License has not been checked yet

The **Details** column shows:
- For valid/invalid: Full license information (name, number, state, type)
- For errors: Error message explaining what went wrong

## Validation Rules

A license is considered **VALID** if:
1. The license state contains "Active"
2. The license type contains "compétition"

Any other combination is considered **INVALID**.

## Important Notes

### CORS Limitations

⚠️ **Important**: Due to browser CORS (Cross-Origin Resource Sharing) restrictions, the license checker currently makes requests directly from the browser to the FFAviron intranet. This may fail in some browsers or configurations.

**If you encounter CORS errors:**
- The feature may need to be implemented as a backend proxy
- Contact the development team to implement server-side license checking

### Cookie Expiration

- FFAviron session cookies expire after a period of inactivity
- If you get authentication errors, obtain fresh cookies
- You'll need to re-paste cookies each time you use the tool

### Rate Limiting

- The tool adds a 500ms delay between each license check
- This prevents overwhelming the FFAviron server
- Checking 100 licenses will take approximately 50 seconds

### Data Privacy

- Cookies provide access to your FFAviron account
- Never share your cookie string with others
- Cookies are stored only in browser memory (not saved)
- Clear the cookie field when done for security

## Troubleshooting

### "No results table found"

**Cause**: Cookie may have expired or FFAviron page structure changed

**Solution**: 
1. Get fresh cookies from FFAviron
2. Verify you can search licenses manually on FFAviron
3. Contact development team if issue persists

### "Request error: Failed to fetch"

**Cause**: CORS restrictions or network issues

**Solution**:
1. Check your internet connection
2. Verify FFAviron intranet is accessible
3. Try a different browser
4. Contact development team for backend proxy implementation

### "License not found in X results"

**Cause**: License number or name doesn't match FFAviron records

**Solution**:
1. Verify the license number is correct
2. Check the crew member's name spelling
3. Manually search on FFAviron to confirm license exists

### Slow Performance

**Cause**: Checking many licenses sequentially with delays

**Solution**:
- This is expected behavior to avoid overwhelming FFAviron
- Check licenses in smaller batches
- Use filters to reduce the number of checks needed

## Technical Details

### Implementation

- **Frontend**: Vue.js component at `frontend/src/views/admin/AdminLicenseChecker.vue`
- **Utility**: License checking logic at `frontend/src/utils/licenseChecker.js`
- **API**: Uses existing admin endpoint `/admin/crew` to fetch crew members
- **No Backend Changes**: Reuses existing infrastructure

### License Check Process

1. Fetch crew members from admin API
2. For each selected member:
   - Build search URL with crew member name
   - Make request to FFAviron with cookies
   - Parse HTML response to find license table
   - Extract license information (number, state, type)
   - Validate against rules (active + competition)
   - Display result with details

### Data Flow

```
User → Select Members → Click Check
  ↓
For each member:
  ↓
Browser → FFAviron Intranet (with cookies)
  ↓
Parse HTML Response
  ↓
Validate License
  ↓
Update UI with Result
```

## Future Enhancements

Potential improvements for future versions:

1. **Backend Proxy**: Implement server-side license checking to avoid CORS
2. **License Storage**: Save validated licenses to database
3. **Automatic Validation**: Check licenses during crew member creation
4. **Batch Export**: Export validation results to CSV
5. **Scheduled Checks**: Automatically re-check licenses periodically
6. **Email Notifications**: Alert team managers about invalid licenses

## Related Documentation

- [Admin Crew Members Guide](./admin-crew-members.md)
- [FFAviron Integration](../../reference/ffaviron-integration.md)
- [Admin Dashboard Guide](./admin-dashboard.md)
