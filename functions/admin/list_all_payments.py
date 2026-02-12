"""
Lambda function for listing all payments (admin only)
Admins can view all payments across all team managers
"""
import json
import logging
from collections import defaultdict

# Import from Lambda layer
from responses import (
    success_response,
    validation_error,
    internal_error,
    handle_exceptions
)
from database import get_db_client
from auth_utils import require_admin
from access_control import require_permission
from payment_formatters import format_payment_list_response, sort_payments_by_field
from payment_calculations import calculate_payment_summary_stats

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
@require_permission('view_payment_analytics')
def lambda_handler(event, context):
    """
    List all payments across all team managers (admin only)
    
    Query parameters:
        - start_date: Optional ISO 8601 timestamp to filter from
        - end_date: Optional ISO 8601 timestamp to filter to
        - team_manager_id: Optional filter by specific team manager
        - limit: Optional maximum number of payments to return
        - sort_by: Optional sort field ('date', 'amount', 'team_manager_name', 'club')
        - sort_order: Optional sort order ('asc' or 'desc', default: 'desc')
    
    Returns:
        {
            "payments": [
                {
                    "payment_id": "uuid",
                    "team_manager_id": "user-id",
                    "team_manager_name": "Club Name",
                    "team_manager_email": "email@example.com",
                    "club_affiliation": "Club Name",
                    "amount": 100.00,
                    "currency": "EUR",
                    "paid_at": "2026-01-15T10:30:00Z",
                    "boat_count": 2,
                    "stripe_receipt_url": "https://..."
                }
            ],
            "total_count": 50,
            "total_amount": 5000.00
        }
    """
    logger.info("List all payments request (admin)")
    
    # Get query parameters
    query_params = event.get('queryStringParameters') or {}
    start_date = query_params.get('start_date')
    end_date = query_params.get('end_date')
    team_manager_filter = query_params.get('team_manager_id')
    limit = query_params.get('limit')
    sort_by = query_params.get('sort_by', 'date').lower()
    sort_order = query_params.get('sort_order', 'desc').lower()
    
    # Validate sort parameters
    valid_sort_fields = ['date', 'amount', 'team_manager_name', 'club']
    if sort_by not in valid_sort_fields:
        return validation_error({
            'sort_by': f'Sort field must be one of: {", ".join(valid_sort_fields)}'
        })
    
    if sort_order not in ['asc', 'desc']:
        return validation_error({'sort_order': 'Sort order must be "asc" or "desc"'})
    
    # Validate limit if provided
    if limit:
        try:
            limit = int(limit)
            if limit <= 0:
                return validation_error({'limit': 'Limit must be a positive integer'})
        except ValueError:
            return validation_error({'limit': 'Limit must be a valid integer'})
    
    # Get database client
    db = get_db_client()
    
    try:
        # Scan all PAYMENT# records across all teams
        all_payments = []
        
        # Use scan with filter expression
        scan_kwargs = {
            'FilterExpression': 'begins_with(SK, :payment_prefix)',
            'ExpressionAttributeValues': {
                ':payment_prefix': 'PAYMENT#'
            }
        }
        
        # Scan with pagination
        while True:
            response = db.table.scan(**scan_kwargs)
            all_payments.extend(response.get('Items', []))
            
            # Check if there are more items
            if 'LastEvaluatedKey' not in response:
                break
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
        
        logger.info(f"Scanned {len(all_payments)} total payments")
        
        # Apply date filters
        if start_date or end_date:
            filtered_payments = []
            for payment in all_payments:
                paid_at = payment.get('paid_at', '')
                if start_date and paid_at < start_date:
                    continue
                if end_date and paid_at > end_date:
                    continue
                filtered_payments.append(payment)
            all_payments = filtered_payments
        
        # Apply team manager filter
        if team_manager_filter:
            all_payments = [
                p for p in all_payments
                if p.get('team_manager_id') == team_manager_filter
            ]
        
        # Cache team manager lookups for performance
        team_manager_cache = {}
        
        def get_team_manager_info(team_manager_id):
            """Get team manager info with caching"""
            if team_manager_id in team_manager_cache:
                return team_manager_cache[team_manager_id]
            
            # Query team manager profile
            profile = db.get_item(
                pk=f'TEAM#{team_manager_id}',
                sk='PROFILE'
            )
            
            if profile:
                info = {
                    'name': f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip(),
                    'email': profile.get('email', ''),
                    'club': profile.get('club_affiliation', '')
                }
            else:
                info = {
                    'name': 'Unknown',
                    'email': '',
                    'club': ''
                }
            
            team_manager_cache[team_manager_id] = info
            return info
        
        # Enrich payments with team manager info
        enriched_payments = []
        for payment in all_payments:
            team_manager_id = payment.get('team_manager_id', '')
            tm_info = get_team_manager_info(team_manager_id)
            
            enriched_payment = {
                'payment_id': payment.get('payment_id'),
                'team_manager_id': team_manager_id,
                'team_manager_name': tm_info['name'],
                'team_manager_email': tm_info['email'],
                'club_affiliation': tm_info['club'],
                'amount': float(payment.get('amount', 0)),
                'currency': payment.get('currency', 'EUR'),
                'paid_at': payment.get('paid_at'),
                'boat_count': len(payment.get('boat_registration_ids', [])),
                'boat_registration_ids': payment.get('boat_registration_ids', []),
                'stripe_receipt_url': payment.get('stripe_receipt_url', ''),
                'status': payment.get('status', 'succeeded')
            }
            enriched_payments.append(enriched_payment)
        
        # Sort payments
        if sort_by == 'date':
            sort_field = 'paid_at'
        elif sort_by == 'amount':
            sort_field = 'amount'
        elif sort_by == 'team_manager_name':
            sort_field = 'team_manager_name'
        elif sort_by == 'club':
            sort_field = 'club_affiliation'
        
        enriched_payments = sort_payments_by_field(
            enriched_payments,
            sort_field,
            reverse=(sort_order == 'desc')
        )
        
        # Apply limit if provided
        if limit and len(enriched_payments) > limit:
            enriched_payments = enriched_payments[:limit]
        
        # Calculate totals
        total_count = len(all_payments)  # Before limit
        total_amount = sum(p['amount'] for p in all_payments)
        
        logger.info(f"Returning {len(enriched_payments)} payments (total: {total_count}, amount: {total_amount})")
        
        # Return success response
        return success_response(data={
            'payments': enriched_payments,
            'total_count': total_count,
            'total_amount': float(total_amount),
            'currency': 'EUR'
        })
        
    except Exception as e:
        logger.error(f"Failed to list all payments: {str(e)}", exc_info=True)
        return internal_error(message='Failed to retrieve payment data')
