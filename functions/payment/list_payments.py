"""
Lambda function for listing payment history
Team managers can view all their past payments
"""
import json
import logging

# Import from Lambda layer
from responses import (
    success_response,
    validation_error,
    internal_error,
    handle_exceptions
)
from database import get_db_client
from auth_utils import get_user_from_event, require_team_manager_or_admin_override
from access_control import require_permission
from payment_queries import query_payments_by_team
from payment_formatters import format_payment_list_response, sort_payments_by_field
from payment_calculations import calculate_payment_summary_stats

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager_or_admin_override
@require_permission('view_payment_history')
def lambda_handler(event, context):
    """
    List all payments for a team manager
    
    Query parameters:
        - start_date: Optional ISO 8601 timestamp to filter from
        - end_date: Optional ISO 8601 timestamp to filter to
        - limit: Optional maximum number of payments to return
        - sort: Optional sort order ('asc' or 'desc', default: 'desc')
    
    Returns:
        {
            "payments": [
                {
                    "payment_id": "uuid",
                    "stripe_payment_intent_id": "pi_xxx",
                    "amount": 100.00,
                    "currency": "EUR",
                    "paid_at": "2026-01-15T10:30:00Z",
                    "boat_count": 2,
                    "boat_registration_ids": ["boat-1", "boat-2"],
                    "stripe_receipt_url": "https://...",
                    "status": "succeeded"
                }
            ],
            "summary": {
                "total_payments": 5,
                "total_amount": 500.00,
                "currency": "EUR",
                "date_range": {
                    "first_payment": "2026-01-01T...",
                    "last_payment": "2026-01-15T..."
                }
            }
        }
    """
    logger.info("List payments request")
    
    # Get authenticated user (respects admin impersonation via _effective_user_id)
    team_manager_id = event.get('_effective_user_id')
    if not team_manager_id:
        user = get_user_from_event(event)
        team_manager_id = user['user_id']
    
    # Get query parameters
    query_params = event.get('queryStringParameters') or {}
    start_date = query_params.get('start_date')
    end_date = query_params.get('end_date')
    limit = query_params.get('limit')
    sort_order = query_params.get('sort', 'desc').lower()
    
    # Validate sort order
    if sort_order not in ['asc', 'desc']:
        return validation_error({'sort': 'Sort order must be "asc" or "desc"'})
    
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
        # Query payments for team manager
        scan_forward = (sort_order == 'asc')
        payments = query_payments_by_team(
            db=db.table,  # Pass the table resource, not DatabaseClient
            team_manager_id=team_manager_id,
            start_date=start_date,
            end_date=end_date,
            scan_forward=scan_forward
        )
        
        # Apply limit if provided
        if limit and len(payments) > limit:
            payments = payments[:limit]
        
        # Format payments for response
        formatted_payments = format_payment_list_response(payments)
        
        # Calculate summary statistics
        summary = calculate_payment_summary_stats(payments)
        
        logger.info(f"Retrieved {len(formatted_payments)} payments for team manager {team_manager_id}")
        
        # Return success response
        return success_response(data={
            'payments': formatted_payments,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Failed to list payments: {str(e)}", exc_info=True)
        return internal_error(message='Failed to retrieve payment data')

