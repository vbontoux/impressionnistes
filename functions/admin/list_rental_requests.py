"""
Lambda function to list all rental requests
Admin only - retrieves all rental requests with optional filtering
"""
import json
import logging
from boto3.dynamodb.conditions import Attr

from responses import success_response, validation_error, handle_exceptions
from auth_utils import require_admin
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Valid boat types
VALID_BOAT_TYPES = ['skiff', '4-', '4+', '4x-', '4x+', '8+', '8x+', '4+yolette', '4x+yolette']

# Valid statuses
VALID_STATUSES = ['pending', 'accepted', 'paid', 'cancelled']


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    List all rental requests with optional filtering
    
    Query parameters:
        status: Filter by status (optional) - pending, accepted, paid, cancelled
        boat_type: Filter by boat type (optional) - skiff, 4-, 4+, 4x-, 4x+, 8+, 8x+
    
    Returns:
        List of rental requests with requester information, sorted by created_at descending
    """
    logger.info("List rental requests (admin)")
    
    # Get query parameters
    query_params = event.get('queryStringParameters') or {}
    filter_status = query_params.get('status')
    filter_boat_type = query_params.get('boat_type')
    
    # Validate filters
    if filter_status and filter_status not in VALID_STATUSES:
        return validation_error(f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")
    
    if filter_boat_type and filter_boat_type not in VALID_BOAT_TYPES:
        return validation_error(f"Invalid boat_type. Must be one of: {', '.join(VALID_BOAT_TYPES)}")
    
    # Query database for all rental requests
    db = get_db_client()
    
    try:
        # Build filter expression for RENTAL_REQUEST records
        filter_expression = (
            Attr('PK').begins_with('RENTAL_REQUEST#') & 
            Attr('SK').eq('METADATA')
        )
        
        # Add status filter if provided
        if filter_status:
            filter_expression = filter_expression & Attr('status').eq(filter_status)
        
        # Add boat_type filter if provided
        if filter_boat_type:
            filter_expression = filter_expression & Attr('boat_type').eq(filter_boat_type)
        
        # Scan for rental requests with filters
        rental_requests = db.scan_table(filter_expression=filter_expression)
        
        # Sort by created_at (most recent first)
        rental_requests.sort(key=lambda r: r.get('created_at', ''), reverse=True)
        
        # Return all fields including admin-specific fields
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
                'requester_id': request.get('requester_id'),
                'requester_email': request.get('requester_email'),
                'created_at': request.get('created_at')
            }
            
            # Add conditional fields based on status and data availability
            if request.get('assignment_details'):
                result_request['assignment_details'] = request.get('assignment_details')
            
            if request.get('accepted_at'):
                result_request['accepted_at'] = request.get('accepted_at')
            
            if request.get('accepted_by'):
                result_request['accepted_by'] = request.get('accepted_by')
            
            if request.get('paid_at'):
                result_request['paid_at'] = request.get('paid_at')
            
            if request.get('cancelled_at'):
                result_request['cancelled_at'] = request.get('cancelled_at')
            
            if request.get('cancelled_by'):
                result_request['cancelled_by'] = request.get('cancelled_by')
            
            if request.get('rejection_reason'):
                result_request['rejection_reason'] = request.get('rejection_reason')
            
            result_requests.append(result_request)
        
        logger.info(
            f"Retrieved {len(result_requests)} rental requests "
            f"(status={filter_status or 'all'}, boat_type={filter_boat_type or 'all'})"
        )
        
        return success_response(
            data={
                'rental_requests': result_requests,
                'count': len(result_requests)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to list rental requests: {str(e)}")
        return validation_error(f'Failed to list rental requests: {str(e)}')
