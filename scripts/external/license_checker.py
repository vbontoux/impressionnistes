#!/usr/bin/env python3
"""
French Rowing Federation License Checker

This script checks if rowing licenses are valid by scraping the FFAviron intranet.
A license is considered valid if:
- The state is "Active" 
- The license type contains "compétition"

Search Strategy:
1. First searches by name
2. If not found, retries by license number
3. Provides detailed reasons for any validation issues

Usage:
    # Single license check
    python license_checker.py --cookies "COOKIE_STRING" --name "Vincent Bontoux" --license "011820"
    
    # Batch processing from CSV
    python license_checker.py --cookies "COOKIE_STRING" --csv input.csv --output results.csv

CSV Format:
    Input CSV should have columns: name, license
    Output CSV will add columns: valid, details (with detailed reason for each result)
"""

import requests
import csv
import sys
import argparse
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def parse_cookie_string(cookie_string):
    """Parse cookie string into dictionary"""
    cookies = {}
    for cookie in cookie_string.split(';'):
        if '=' in cookie:
            key, value = cookie.strip().split('=', 1)
            cookies[key] = value
    return cookies

def search_by_query(query, cookies, headers):
    """
    Search FFAviron intranet by query string (name or license number)
    
    Returns:
        tuple: (success, rows, error_message)
    """
    try:
        search_query = quote_plus(query)
        url = f"https://intranet.ffaviron.fr/licences/recherche?licencies_q={search_query}"
        
        response = requests.get(url, cookies=cookies, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the results table
        table = soup.find('table', class_='table-generated')
        if not table:
            table = soup.find('table')
            if not table:
                return False, [], "No results table found"
        
        tbody = table.find('tbody')
        if not tbody:
            return False, [], "No results found in table"
        
        rows = tbody.find_all('tr')
        if not rows:
            return False, [], "No data rows found"
        
        return True, rows, None
        
    except requests.RequestException as e:
        return False, [], f"Request error: {str(e)}"
    except Exception as e:
        return False, [], f"Error: {str(e)}"


def validate_license_row(row_license, row_name, row_state, row_type, expected_name, expected_license):
    """
    Validate a license row and return detailed result
    
    Returns:
        tuple: (is_valid, reason_message)
    """
    is_active = "Active" in row_state
    is_competition = "compétition" in row_type.lower()
    
    # Check if name matches (if we're validating by name)
    name_matches = expected_name.lower() in row_name.lower() if expected_name else True
    
    # Build detailed reason
    if is_active and is_competition:
        if expected_name and not name_matches:
            return True, f"License found but registered to different person: {row_name} (expected: {expected_name}). License: {row_license}, Status: {row_state}, Type: {row_type}"
        return True, f"Valid license: {row_name}, License: {row_license}, Status: {row_state}, Type: {row_type}"
    else:
        reasons = []
        if not is_active:
            reasons.append(f"Status is '{row_state}' (not Active)")
        if not is_competition:
            reasons.append(f"Type is '{row_type}' (not competition)")
        
        reason_text = " and ".join(reasons)
        return False, f"Invalid license: {row_name}, License: {row_license}. Reason: {reason_text}"


def check_license(name, license_number, cookie_string):
    """
    Check if a license is valid (active and competition type)
    
    Strategy:
    1. First, search by name
    2. If name search fails or doesn't find the license, retry by license number
    3. Provide detailed reasons for any issues found
    """
    
    cookies = parse_cookie_string(cookie_string)
    headers = {
        'Accept-Encoding': 'json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    found_in_name_search = False
    
    # Strategy 1: Search by name
    if name:
        success, rows, error = search_by_query(name, cookies, headers)
        
        if success:
            # Look for matching license in name search results
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 6:
                    row_license = cells[0].get_text(strip=True)
                    row_name = cells[1].get_text(strip=True)
                    row_state = cells[4].get_text(strip=True)
                    row_type = cells[5].get_text(strip=True)
                    
                    # If we have a license number, match exactly
                    if license_number and row_license == license_number:
                        found_in_name_search = True
                        return validate_license_row(row_license, row_name, row_state, row_type, name, license_number)
                    
                    # If no license number provided, match by name
                    elif not license_number and name.lower() in row_name.lower():
                        found_in_name_search = True
                        return validate_license_row(row_license, row_name, row_state, row_type, name, None)
    
    # Strategy 2: If name search didn't find the license, try searching by license number
    if license_number and not found_in_name_search:
        success, rows, error = search_by_query(license_number, cookies, headers)
        
        if success:
            # Look for exact license match
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 6:
                    row_license = cells[0].get_text(strip=True)
                    row_name = cells[1].get_text(strip=True)
                    row_state = cells[4].get_text(strip=True)
                    row_type = cells[5].get_text(strip=True)
                    
                    if row_license == license_number:
                        # Found by license number - check if name matches
                        is_valid, reason = validate_license_row(row_license, row_name, row_state, row_type, name, license_number)
                        
                        if name and name.lower() not in row_name.lower():
                            # License found but name doesn't match
                            return is_valid, f"License found by number but name mismatch. Found: {row_name} (expected: {name}). {reason}"
                        
                        return is_valid, f"License found by license number search. {reason}"
            
            # License number search returned results but didn't find exact match
            return False, f"License number {license_number} not found in search results (searched by license number after name search failed)"
        else:
            # License number search failed
            return False, f"License number {license_number} not found. Name search also failed. {error if error else 'No results'}"
    
    # Both strategies failed
    if name and license_number:
        return False, f"License not found by name '{name}' or license number '{license_number}'. Person may not be registered in FFAviron database."
    elif name:
        return False, f"No license found for name '{name}'. Person may not be registered in FFAviron database."
    else:
        return False, "No name or license number provided for search"

def main():
    parser = argparse.ArgumentParser(
        description='Check French rowing federation licenses',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--cookies', required=True, 
                       help='Full cookie string from browser (copy from curl command)')
    parser.add_argument('--name', help='Name to search for')
    parser.add_argument('--license', help='License number to check')
    parser.add_argument('--csv', help='CSV file with names and licenses')
    parser.add_argument('--output', help='Output CSV file (required for CSV mode)')
    
    args = parser.parse_args()
    
    if args.csv:
        # CSV batch processing mode
        if not args.output:
            print("Error: --output required when using --csv")
            sys.exit(1)
            
        try:
            with open(args.csv, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                output_rows = []
                
                for row in reader:
                    name = row.get('name', '').strip()
                    license_num = row.get('license', '').strip()
                    
                    if name:
                        is_valid, message = check_license(name, license_num, args.cookies)
                        
                        output_row = dict(row)
                        output_row['valid'] = 'Yes' if is_valid else 'No'
                        output_row['details'] = message
                        output_rows.append(output_row)
                        
                        print(f"✓ {name} ({license_num}): {'VALID' if is_valid else 'INVALID'}")
                
                # Write results
                if output_rows:
                    fieldnames = list(output_rows[0].keys())
                    with open(args.output, 'w', newline='', encoding='utf-8') as outfile:
                        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(output_rows)
                    
                    print(f"\n✓ Results written to {args.output}")
                
        except FileNotFoundError:
            print(f"Error: CSV file '{args.csv}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error processing CSV: {str(e)}")
            sys.exit(1)
    
    elif args.name:
        # Single license check mode
        is_valid, message = check_license(args.name, args.license, args.cookies)
        
        print(f"Name: {args.name}")
        if args.license:
            print(f"License: {args.license}")
        print(f"Result: {'✓ VALID' if is_valid else '✗ INVALID'}")
        print(f"Details: {message}")
        
        sys.exit(0 if is_valid else 1)
    
    else:
        print("Error: Either --name or --csv must be provided")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
