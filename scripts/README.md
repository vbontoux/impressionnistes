# French Rowing Federation License Checker

This script scrapes the FFAviron intranet to check if rowing licenses are valid.

## Requirements

- Python 3.6+
- requests library
- beautifulsoup4 library

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install requests beautifulsoup4
```

## Usage

### Getting Cookies

1. Log into https://intranet.ffaviron.fr in your browser
2. Open Developer Tools (F12)
3. Go to Network tab
4. Perform a license search
5. Find the request to `/licences/recherche`
6. Copy the Cookie header value

### Single License Check

```bash
python license_checker.py --cookies "COOKIE_STRING" --name "Vincent Bontoux" --license "011820"
```

### Batch Processing

1. Create a CSV file with columns: `name`, `license`
```csv
name,license
Vincent Bontoux,011820
John Doe,123456
```

2. Run the script:
```bash
python license_checker.py --cookies "COOKIE_STRING" --csv input.csv --output results.csv
```

The output CSV will include additional columns:
- `valid`: "Yes" or "No"
- `details`: Detailed information about the license

## License Validation Rules

A license is considered **VALID** if:
- State is "Active" (contains "Active")
- License type contains "compétition"

## Example Output

```
✓ Vincent Bontoux (011820): VALID
✗ Vincent Bontoux (445577): INVALID

✓ Results written to results.csv
```

## Troubleshooting

- **"No results table found"**: Cookie may have expired, get fresh cookies
- **"Request error"**: Check internet connection and cookie format
- **"License not found"**: Verify name spelling and license number

## Security Note

Keep your cookies secure and don't share them. They provide access to your FFAviron account.
