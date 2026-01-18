"""
Lambda function to proxy HTML requests to external websites
Admin only - acts as a CORS proxy to bypass browser restrictions

This is a generic proxy that:
1. Receives HTTP request details (URL, cookies, headers) from frontend
2. Forwards request to external website
3. Returns raw HTML response to frontend
4. Frontend handles all parsing and business logic

Use cases:
- FFAviron license checking
- Any external website that doesn't support CORS
- Web scraping with authentication
"""
import json
import logging
import requests
from urllib.parse import urlparse

from responses import success_response, error_response, validation_error, handle_exceptions
from auth_utils import require_admin

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Whitelist of allowed domains for security
ALLOWED_DOMAINS = [
    'intranet.ffaviron.fr',
    'ffaviron.fr',
    # Add more domains as needed
]


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Proxy HTML request to external website
    
    POST body:
        url: Target URL (required)
        cookies: Cookie string from browser (optional)
        headers: Additional headers (optional)
        method: HTTP method (default: GET)
    
    Returns:
        Raw HTML response from target website
    """
    logger.info("HTML proxy request")
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error('Invalid JSON in request body')
    
    url = body.get('url', '').strip()
    cookie_string = body.get('cookies', '').strip()
    custom_headers = body.get('headers', {})
    method = body.get('method', 'GET').upper()
    
    # Validate required fields
    if not url:
        return validation_error('URL is required')
    
    # Validate URL format
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return validation_error('Invalid URL format')
    except Exception:
        return validation_error('Invalid URL format')
    
    # Security: Check domain whitelist
    domain = parsed_url.netloc
    if not any(domain.endswith(allowed) for allowed in ALLOWED_DOMAINS):
        logger.warning(f"Blocked request to non-whitelisted domain: {domain}")
        return error_response(f'Domain {domain} is not whitelisted', 403)
    
    # Parse cookies if provided
    cookies = {}
    if cookie_string:
        for cookie in cookie_string.split(';'):
            if '=' in cookie:
                key, value = cookie.strip().split('=', 1)
                cookies[key] = value
    
    # Build headers
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    # Add custom headers
    if custom_headers and isinstance(custom_headers, dict):
        headers.update(custom_headers)
    
    # Make request to external website
    try:
        if method == 'GET':
            response = requests.get(url, cookies=cookies, headers=headers, timeout=15)
        elif method == 'POST':
            post_data = body.get('data', {})
            response = requests.post(url, cookies=cookies, headers=headers, data=post_data, timeout=15)
        else:
            return validation_error(f'HTTP method {method} not supported')
        
        response.raise_for_status()
        
        logger.info(f"Proxy request successful to {domain}")
        
        # Return raw HTML to frontend for parsing
        return success_response(
            data={
                'html': response.text,
                'status_code': response.status_code,
                'url': url,
                'content_type': response.headers.get('Content-Type', 'text/html')
            }
        )
        
    except requests.Timeout:
        logger.error(f"Request timeout to {url}")
        return error_response('Request timed out', 504)
    
    except requests.HTTPError as e:
        logger.error(f"HTTP error for {url}: {e}")
        if e.response.status_code == 401 or e.response.status_code == 403:
            return error_response('Authentication failed. Cookies may have expired.', 401)
        return error_response(f'Target server returned error: {e.response.status_code}', e.response.status_code)
    
    except requests.RequestException as e:
        logger.error(f"Request error for {url}: {str(e)}")
        return error_response(f'Failed to connect to target: {str(e)}', 502)
    
    except Exception as e:
        logger.error(f"Unexpected error in HTML proxy: {str(e)}", exc_info=True)
        return error_response(f'Unexpected error: {str(e)}', 500)
