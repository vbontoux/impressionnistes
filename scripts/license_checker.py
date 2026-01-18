#!/usr/bin/env python3
"""
French Rowing Federation License Checker

This script checks if rowing licenses are valid by scraping the FFAviron intranet.
A license is considered valid if:
- The state is "Active" 
- The license type contains "compétition"

Usage:
    # Single license check
    python license_checker.py --cookies "COOKIE_STRING" --name "Vincent Bontoux" --license "011820"
    
    # Batch processing from CSV
    python license_checker.py --cookies "COOKIE_STRING" --csv input.csv --output results.csv

CSV Format:
    Input CSV should have columns: name, license
    Output CSV will add columns: valid, details
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

def check_license(name, license_number, cookie_string):
    """Check if a license is valid (active and competition type)"""
    
    cookies = parse_cookie_string(cookie_string)
    search_query = quote_plus(name)
    url = f"https://intranet.ffaviron.fr/licences/recherche?licencies_q={search_query}"
    
    headers = {
        'Accept-Encoding': 'json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, cookies=cookies, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the results table
        table = soup.find('table', class_='table-generated')
        if not table:
            table = soup.find('table')
            if not table:
                return False, "No results table found"
        
        tbody = table.find('tbody')
        if not tbody:
            return False, "No results found in table"
        
        rows = tbody.find_all('tr')
        if not rows:
            return False, "No data rows found"
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 6:
                row_license = cells[0].get_text(strip=True)
                row_name = cells[1].get_text(strip=True)
                row_state = cells[4].get_text(strip=True)
                row_type = cells[5].get_text(strip=True)
                
                # Check if this row matches our criteria
                if license_number and row_license == license_number:
                    is_active = "Active" in row_state
                    is_competition = "compétition" in row_type.lower()
                    
                    if is_active and is_competition:
                        return True, f"Valid: {row_name} - {row_license} - {row_state} - {row_type}"
                    else:
                        return False, f"Invalid: {row_name} - {row_license} - {row_state} - {row_type}"
                
                elif not license_number and name.lower() in row_name.lower():
                    is_active = "Active" in row_state
                    is_competition = "compétition" in row_type.lower()
                    
                    if is_active and is_competition:
                        return True, f"Valid: {row_name} - {row_license} - {row_state} - {row_type}"
                    else:
                        return False, f"Invalid: {row_name} - {row_license} - {row_state} - {row_type}"
        
        return False, f"License {license_number} not found in {len(rows)} results"
        
    except requests.RequestException as e:
        return False, f"Request error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

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
