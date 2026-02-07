"""
Lambda function for creating boat registrations
Team managers can create boat registrations for their crews
"""
import json
import logging
import os
import uuid

# Import from Lambda layer
from responses import (
    success_response,
    validation_error,
    internal_error,
    handle_exceptions
)
from validation import validate_boat_registration, sanitize_dict, sanitize_xss, boat_registration_schema
from database import get_db_client, get_timestamp
from auth_utils import get_user_from_event, require_team_manager_or_admin_override
from access_control import require_permission
from boat_registration_utils import (
    get_required_seats_for_boat_type,
    validate_boat_type_for_event,
    calculate_registration_status,
    detect_multi_club_crew,
    get_assigned_crew_members,
    calculate_boat_club_info
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager_or_admin_override
@require_permission('create_boat_registration')
def lambda_handler(event, context):
    """
    Create a new boat registration
    
    Request body:
        - event_type: Event type (21km or 42km) (required)
        - boat_type: Boat type (skiff, 4-, 4+, 8+) (required)
        - race_id: Race ID (optional, can be set later)
        - seats: List of seat assignments (optional, can be filled later)
        - is_boat_rental: Boolean indicating if boat is rented (optional)
    
    Returns:
        Boat registration object with boat_registration_id
    """
    logger.info("Create boat registration request")
    
    # Get effective user ID (impersonated or real)
    team_manager_id = event['_effective_user_id']
    is_admin_override = event['_is_admin_override']
    
    # Audit logging for admin override
    if is_admin_override:
        admin_id = event['_admin_user_id']
        logger.info(f"Admin {admin_id} creating boat registration for team manager {team_manager_id}")
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error({'body': 'Invalid JSON'})
    
    # Extract required fields
    event_type = body.get('event_type', '').strip()
    boat_type = body.get('boat_type', '').strip()
    
    if not event_type or not boat_type:
        return validation_error({
            'event_type': 'Event type is required' if not event_type else None,
            'boat_type': 'Boat type is required' if not boat_type else None
        })
    
    # Validate boat type for event
    if not validate_boat_type_for_event(event_type, boat_type):
        return validation_error({
            'boat_type': f"Boat type '{boat_type}' is not valid for event '{event_type}'"
        })
    
    # Get or create seat structure
    seats = body.get('seats')
    if not seats:
        # Create default seat structure for boat type
        seats = get_required_seats_for_boat_type(boat_type)
    
    # Extract boat request fields
    boat_request_enabled = body.get('boat_request_enabled', False)
    boat_request_comment = body.get('boat_request_comment')
    
    # Validate boat request comment length BEFORE sanitization
    if boat_request_enabled and boat_request_comment:
        if len(boat_request_comment) > 500:
            return validation_error({
                'boat_request_comment': 'Boat request comment cannot exceed 500 characters'
            })
        # Sanitize XSS from boat_request_comment
        boat_request_comment = sanitize_xss(boat_request_comment, preserve_newlines=True)
    
    # Clear boat request fields if boat_request_enabled is false
    if not boat_request_enabled:
        boat_request_comment = None
    
    # Prepare boat registration data
    boat_data = {
        'event_type': event_type,
        'boat_type': boat_type,
        'race_id': body.get('race_id'),
        'seats': seats,
        'is_boat_rental': body.get('is_boat_rental', False),
        'boat_request_enabled': boat_request_enabled,
        'boat_request_comment': boat_request_comment,
        'assigned_boat_identifier': None,  # Only admins can set this
        'assigned_boat_comment': None,  # Only admins can set this
        'is_multi_club_crew': False,  # Will be calculated
        'registration_status': 'incomplete',
        'flagged_issues': []
    }
    
    # Sanitize data
    boat_data = sanitize_dict(boat_data, boat_registration_schema)
    
    # Validate boat registration data
    is_valid, errors = validate_boat_registration(boat_data)
    if not is_valid:
        return validation_error(errors)
    
    # Generate boat registration ID
    boat_registration_id = str(uuid.uuid4())
    
    # Generate boat_number if race is assigned
    boat_number = None
    if boat_data.get('race_id'):
        try:
            # Fetch the race to get event_type and display_order
            db = get_db_client()
            race = db.get_item(
                pk='RACE',
                sk=boat_data['race_id']
            )
            
            if race:
                event_type = race.get('event_type')
                display_order = race.get('display_order', 0)
                
                if event_type:
                    if display_order == 0:
                        logger.warning(f"Race missing display_order: {boat_data['race_id']}, using 0 as fallback")
                    
                    # Scan all boats with the same race_id
                    from boto3.dynamodb.conditions import Attr
                    response = db.table.scan(
                        FilterExpression=Attr('race_id').eq(boat_data['race_id']) & Attr('SK').begins_with('BOAT#')
                    )
                    all_boats_in_race = response.get('Items', [])
                    
                    # Handle pagination
                    while 'LastEvaluatedKey' in response:
                        response = db.table.scan(
                            FilterExpression=Attr('race_id').eq(boat_data['race_id']) & Attr('SK').begins_with('BOAT#'),
                            ExclusiveStartKey=response['LastEvaluatedKey']
                        )
                        all_boats_in_race.extend(response.get('Items', []))
                    
                    # Generate boat_number
                    from boat_registration_utils import generate_boat_number
                    boat_number = generate_boat_number(
                        event_type=event_type,
                        display_order=display_order,
                        race_id=boat_data['race_id'],
                        all_boats_in_race=all_boats_in_race
                    )
                    logger.info(f"Generated boat_number: {boat_number}")
                else:
                    logger.error(f"Race missing event_type: {boat_data['race_id']}")
            else:
                logger.error(f"Race not found: {boat_data['race_id']}")
        except Exception as e:
            logger.error(f"Failed to generate boat_number: {e}")
            boat_number = None
    
    # Calculate registration status
    registration_status = calculate_registration_status(boat_data)
    
    # Get team manager's club affiliation for club field initialization
    if 'db' not in locals():
        db = get_db_client()
    team_manager = db.get_item(
        pk=f'USER#{team_manager_id}',
        sk='PROFILE'
    )
    team_manager_club = team_manager.get('club_affiliation', '') if team_manager else ''
    
    # Initialize club fields with team manager's club
    # When boat is created, no crew is assigned yet, so use team manager's club
    club_info = calculate_boat_club_info([], team_manager_club)
    boat_club_display = club_info['boat_club_display']
    club_list = club_info['club_list']
    
    # Store boat registration in DynamoDB
    
    boat_registration_item = {
        'PK': f'TEAM#{team_manager_id}',
        'SK': f'BOAT#{boat_registration_id}',
        'boat_registration_id': boat_registration_id,
        'team_manager_id': team_manager_id,
        'event_type': boat_data['event_type'],
        'boat_type': boat_data['boat_type'],
        'race_id': boat_data.get('race_id'),
        'boat_number': boat_number,
        'seats': boat_data['seats'],
        'is_boat_rental': boat_data['is_boat_rental'],
        'boat_request_enabled': boat_data['boat_request_enabled'],
        'boat_request_comment': boat_data.get('boat_request_comment'),
        'assigned_boat_identifier': boat_data.get('assigned_boat_identifier'),
        'assigned_boat_comment': boat_data.get('assigned_boat_comment'),
        'is_multi_club_crew': boat_data['is_multi_club_crew'],
        'boat_club_display': boat_club_display,
        'club_list': club_list,
        'registration_status': registration_status,
        'flagged_issues': boat_data.get('flagged_issues', []),
        'created_at': get_timestamp(),
        'updated_at': get_timestamp()
    }
    
    db.put_item(boat_registration_item)
    logger.info(f"Boat registration created: {boat_registration_id}")
    
    # Send Slack notification for new boat registration
    try:
        from slack_utils import notify_new_boat_registration, set_webhook_urls
        from secrets_manager import get_slack_admin_webhook
        
        slack_webhook = get_slack_admin_webhook()
        
        if slack_webhook:
            set_webhook_urls(admin_webhook=slack_webhook)
            environment = os.environ.get('ENVIRONMENT', 'dev')
            
            # Get race name if race is assigned
            race_name = None
            if boat_data.get('race_id'):
                try:
                    race = db.get_item(pk='RACE', sk=boat_data['race_id'])
                    if race:
                        race_name = race.get('race_name', race.get('race_id'))
                except Exception as e:
                    logger.warning(f"Failed to fetch race name: {e}")
            
            notify_new_boat_registration(
                boat_number=boat_number,
                event_type=boat_data['event_type'],
                boat_type=boat_data['boat_type'],
                race_name=race_name,
                team_manager_name=f"{team_manager.get('first_name', '')} {team_manager.get('last_name', '')}".strip(),
                team_manager_email=team_manager.get('email', ''),
                club_affiliation=boat_club_display,
                registration_status=registration_status,
                boat_request_enabled=boat_data['boat_request_enabled'],
                boat_request_comment=boat_data.get('boat_request_comment'),
                environment=environment
            )
            logger.info("Slack notification sent for new boat registration")
        else:
            logger.info("Slack webhook not configured - skipping notification")
    except Exception as e:
        # Don't fail boat creation if Slack notification fails
        logger.warning(f"Failed to send Slack notification: {e}")
    
    # Return success response
    return success_response(
        data=boat_registration_item,
        status_code=201
    )
