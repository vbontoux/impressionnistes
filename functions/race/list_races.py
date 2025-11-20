"""
Lambda function for listing available races
Returns all race definitions from the database
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

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
def lambda_handler(event, context):
    """
    List all available races
    
    Query parameters (optional):
        - event_type: Filter by event type (21km or 42km)
        - boat_type: Filter by boat type (skiff, 4-, 4+, 8+)
        - age_category: Filter by age category (j16, j18, senior, master)
        - gender_category: Filter by gender category (men, women, mixed)
    
    Returns:
        List of race objects
    """
    logger.info("List races request")
    
    # Get query parameters
    query_params = event.get('queryStringParameters') or {}
    event_type_filter = query_params.get('event_type')
    boat_type_filter = query_params.get('boat_type')
    age_category_filter = query_params.get('age_category')
    gender_category_filter = query_params.get('gender_category')
    
    # Get all races from DynamoDB
    db = get_db_client()
    
    races = db.query_by_pk(
        pk='RACE',
        sk_prefix=''
    )
    
    # Apply filters if provided
    if event_type_filter:
        races = [r for r in races if r.get('event_type') == event_type_filter]
    
    if boat_type_filter:
        races = [r for r in races if r.get('boat_type') == boat_type_filter]
    
    if age_category_filter:
        races = [r for r in races if r.get('age_category') == age_category_filter]
    
    if gender_category_filter:
        races = [r for r in races if r.get('gender_category') == gender_category_filter]
    
    logger.info(f"Found {len(races)} races")
    
    # Return success response
    return success_response(data={'races': races})
