"""
Lambda function to get rental requests for the authenticated team manager
Team manager accessible - shows their own rental requests
"""
import json
import logging
from boto3.dynamodb.conditions import Attr

from responses import success_response, validation_error, handle_exceptions
from auth_utils import require_team_manager, get_user_from_event
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager
def lambda_handler(event, context):
    """
    Get rental requests for the authenticated team manager
    
    Returns:
        List of rental requests for this team manager, sorted by created_at descending
    """
    logger.info("Get my rental requests")
    
    # Get authenticated user
    user_info = get_user_from_event(event)
    requester_id = user_info['user_id']
    
    # Query database for rental requests by this team manager
    db = get_db_client()
    
    try:
        # Scan for RENTAL_REQUEST records where requester_id matches
        filter_expression = (
            Attr('PK').begins_with('RENTAL_REQUEST#') & 
            Attr('SK').eq('METADATA') & 
            Attr('requester_id').eq(requester_id)
        )
        
        rental_requests = db.scan_table(filter_expression=filter_expression)
        
        # Sort by created_at (most recent first)
        rental_requests.sort(key=lambda r: r.get('created_at', ''), reverse=True)
        
        # Return all required fields for team managers
        result_requests = []
        for request in rental_requests:
            # Strip RENTAL_REQUEST# prefix from ID for frontend
            full_id = request.get('rental_request_id', '')
            clean_id = full_id.replace('RENTAL_REQUEST#', '') if full_id else ''
            
            result_request = {
                'rental_request_id': clean_id,
                'boat_type': request.get('boat_type'),
                'desired_weight_range': request.get('desired_weight_range'),
                'request_comment': request.get('request_comment'),
                'status': request.get('status'),
                'created_at': request.get('created_at')
            }
            
            # Add conditional fields based on status
            if request.get('assignment_details'):
                result_request['assignment_details'] = request.get('assignment_details')
            
            if request.get('accepted_at'):
                result_request['accepted_at'] = request.get('accepted_at')
            
            if request.get('paid_at'):
                result_request['paid_at'] = request.get('paid_at')
            
            if request.get('cancelled_at'):
                result_request['cancelled_at'] = request.get('cancelled_at')
            
            if request.get('rejected_at'):
                result_request['rejected_at'] = request.get('rejected_at')
            
            if request.get('rejection_reason'):
                result_request['rejection_reason'] = request.get('rejection_reason')
            
            result_requests.append(result_request)
        
        logger.info(f"Retrieved {len(result_requests)} rental requests for team manager {requester_id}")
        
        return success_response(
            data={
                'rental_requests': result_requests,
                'count': len(result_requests)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get rental requests: {str(e)}")
        return validation_error(f'Failed to get rental requests: {str(e)}')