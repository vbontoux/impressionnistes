"""
Lambda function for getting payment summary
Team managers can view their total paid and outstanding balance
"""
import json
import logging

# Import from Lambda layer
from responses import (
    success_response,
    internal_error,
    handle_exceptions
)
from database import get_db_client
from auth_utils import get_user_from_event, require_team_manager_or_admin_override
from access_control import require_permission
from configuration import ConfigurationManager
from payment_queries import query_payments_by_team, query_unpaid_boats
from payment_calculations import calculate_total_paid, calculate_outstanding_balance, count_boats_in_payments

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager_or_admin_override
@require_permission('view_payment_history')
def lambda_handler(event, context):
    """
    Get payment summary for a team manager
    
    Returns:
        {
            "paid": {
                "total_amount": 500.00,
                "currency": "EUR",
                "payment_count": 5,
                "boat_count": 10
            },
            "outstanding": {
                "total_amount": 100.00,
                "currency": "EUR",
                "boat_count": 2,
                "boats": [...]
            },
            "total_registered_boats": 12
        }
    """
    logger.info("Get payment summary request")
    
    # Get authenticated user (respects admin impersonation via _effective_user_id)
    team_manager_id = event.get('_effective_user_id')
    if not team_manager_id:
        user = get_user_from_event(event)
        team_manager_id = user['user_id']
    
    # Get database client
    db = get_db_client()
    
    try:
        # Query all payments for team manager
        payments = query_payments_by_team(
            db=db,
            team_manager_id=team_manager_id
        )
        
        # Calculate total paid
        total_paid = calculate_total_paid(payments)
        payment_count = len(payments)
        boats_paid_count = count_boats_in_payments(payments)
        
        # Query unpaid boats
        unpaid_boats = query_unpaid_boats(db, team_manager_id)
        
        # Get pricing configuration
        config_manager = ConfigurationManager()
        pricing_config = config_manager.get_pricing_config()
        
        # Calculate outstanding balance
        total_outstanding = calculate_outstanding_balance(
            boats=unpaid_boats,
            pricing_config=pricing_config
        )
        
        # Use unpaid boats as boat details
        boat_details = unpaid_boats
        
        # Calculate total registered boats
        all_boats = db.query_by_pk(
            pk=f'TEAM#{team_manager_id}',
            sk_prefix='BOAT#'
        )
        total_registered_boats = len(all_boats)
        
        logger.info(f"Payment summary for team manager {team_manager_id}: "
                   f"paid={float(total_paid)}, outstanding={float(total_outstanding)}")
        
        # Return success response
        return success_response(data={
            'paid': {
                'total_amount': float(total_paid),
                'currency': 'EUR',
                'payment_count': payment_count,
                'boat_count': boats_paid_count
            },
            'outstanding': {
                'total_amount': float(total_outstanding),
                'currency': 'EUR',
                'boat_count': len(unpaid_boats),
                'boats': boat_details
            },
            'total_registered_boats': total_registered_boats
        })
        
    except Exception as e:
        logger.error(f"Failed to get payment summary: {str(e)}", exc_info=True)
        return internal_error(message='Failed to retrieve payment summary')

