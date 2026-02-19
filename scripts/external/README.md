# External Tools

External and third-party tools not directly related to the main application.

## Tools

### license_checker.py
French Rowing Federation (FFAviron) license validation tool.

**Purpose:** Scrape FFAviron intranet to check if rowing licenses are valid.

**Requirements:**
- Python 3.6+
- requests library
- beautifulsoup4 library

**Installation:**
```bash
cd scripts/external
python3 -m venv venv
source venv/bin/activate
pip install requests beautifulsoup4
```

**Usage:**

**Single license check:**
```bash
python license_checker.py \
  --cookies "COOKIE_STRING" \
  --name "Vincent Bontoux" \
  --license "011820"
```

**Batch processing:**
```bash
# Create input CSV with columns: name, license
python license_checker.py \
  --cookies "COOKIE_STRING" \
  --csv input.csv \
  --output results.csv
```

**Getting cookies:**
1. Log into https://intranet.ffaviron.fr
2. Open Developer Tools (F12)
3. Go to Network tab
4. Perform a license search
5. Find request to `/licences/recherche`
6. Copy Cookie header value

**License validation rules:**
A license is considered VALID if:
- State is "Active"
- License type contains "compétition"

**Output:**
```
✓ Vincent Bontoux (011820): VALID
✗ Vincent Bontoux (445577): INVALID

✓ Results written to results.csv
```

**Output CSV columns:**
- `name` - Rower name
- `license` - License number
- `valid` - "Yes" or "No"
- `details` - Detailed license information

## Files

- `license_checker.py` - Main script
- `test_licenses.csv` - Sample input file
- `results.csv` - Sample output file
- `venv/` - Python virtual environment (gitignored)

## Security Note

Keep your cookies secure and don't share them. They provide access to your FFAviron account.

## Troubleshooting

**"No results table found"**
- Cookie may have expired, get fresh cookies
- Check internet connection

**"Request error"**
- Verify cookie format
- Check FFAviron website is accessible

**"License not found"**
- Verify name spelling matches FFAviron records
- Check license number is correct

## Integration with Main Application

This tool is **not integrated** with the main registration system. It's a standalone utility for manual license verification.

For automated license verification in the application, see:
- `functions/admin/update_crew_member_license_verification.py`
- `functions/admin/bulk_update_license_verification.py`

## Related Documentation

- FFAviron website: https://intranet.ffaviron.fr
- License verification guide: `docs/guides/admin/license-verification.md`
