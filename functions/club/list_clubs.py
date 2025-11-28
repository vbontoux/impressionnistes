"""
List Clubs Lambda Function
Returns list of rowing clubs for searchable dropdown
"""
import json
import logging
import os
import sys

# Add shared layer to path
sys.path.insert(0, '/opt/python')

from shared.database import DatabaseClient
from shared.responses import success_response, error_response, unauthorized_error
from shared.auth_utils import get_user_from_event

logger = logging.getLogger()
logger.setLevel(logging.INFO)

db = DatabaseClient()


def lambda_handler(event, context):
    """
    List all rowing clubs
    
    Returns:
        200: List of clubs with id, name, and url
        500: Server error
    """
    try:
        # No authentication required - this is a public endpoint for registration
        logger.info("Listing clubs (public endpoint)")
        
        # Query all clubs from database
        # Clubs have PK=CLUB and SK=<club_id>
        response = db.table.query(
            KeyConditionExpression='PK = :pk',
            ExpressionAttributeValues={
                ':pk': 'CLUB'
            }
        )
        
        clubs = []
        for item in response.get('Items', []):
            clubs.append({
                'club_id': item.get('club_id'),
                'name': item.get('name'),
                'url': item.get('url', '')
            })
        
        # Sort by name for better UX
        clubs.sort(key=lambda x: x['name'])
        
        logger.info(f"Found {len(clubs)} clubs")
        
        return success_response({
            'clubs': clubs,
            'count': len(clubs)
        })
        
    except Exception as e:
        logger.error(f"Error listing clubs: {str(e)}", exc_info=True)
        from shared.responses import internal_error
        return internal_error('Failed to list clubs')
