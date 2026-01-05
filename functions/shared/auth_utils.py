"""
Authentication and authorization utilities
Helpers for Cognito JWT validation and role-based access control
"""
import logging
from functools import wraps
from responses import forbidden_error, unauthorized_error

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_user_from_event(event):
    """
    Extract user information from API Gateway event (Cognito authorizer)
    
    Args:
        event: API Gateway event with Cognito authorizer
        
    Returns:
        dict: User information with id, email, groups, etc.
    """
    request_context = event.get('requestContext', {})
    authorizer = request_context.get('authorizer', {})
    claims = authorizer.get('claims', {})
    
    if not claims:
        return None
    
    # Extract user information
    user_info = {
        'user_id': claims.get('sub'),
        'email': claims.get('email'),
        'given_name': claims.get('given_name'),
        'family_name': claims.get('family_name'),
        'club_affiliation': claims.get('custom:club_affiliation'),
        'role': claims.get('custom:role'),
        'groups': []
    }
    
    # Extract groups from cognito:groups claim
    groups_claim = claims.get('cognito:groups', '')
    if groups_claim:
        if isinstance(groups_claim, str):
            user_info['groups'] = [g.strip() for g in groups_claim.split(',') if g.strip()]
        elif isinstance(groups_claim, list):
            user_info['groups'] = groups_claim
    
    return user_info


def is_admin(user_info):
    """
    Check if user is an admin
    
    Args:
        user_info: User information dict from get_user_from_event
        
    Returns:
        bool: True if user is admin
    """
    if not user_info:
        return False
    return 'admins' in user_info.get('groups', [])


def is_team_manager(user_info):
    """
    Check if user is a team manager
    
    Args:
        user_info: User information dict from get_user_from_event
        
    Returns:
        bool: True if user is team manager
    """
    if not user_info:
        return False
    return 'team_managers' in user_info.get('groups', [])


def is_devops(user_info):
    """
    Check if user is devops
    
    Args:
        user_info: User information dict from get_user_from_event
        
    Returns:
        bool: True if user is devops
    """
    if not user_info:
        return False
    return 'devops' in user_info.get('groups', [])


def require_auth(func):
    """
    Decorator to require authentication
    
    Usage:
        @require_auth
        def lambda_handler(event, context):
            user = get_user_from_event(event)
            # user is guaranteed to exist
    """
    @wraps(func)
    def wrapper(event, context):
        user_info = get_user_from_event(event)
        if not user_info or not user_info.get('user_id'):
            logger.warning("Unauthorized access attempt")
            return unauthorized_error('Authentication required')
        
        return func(event, context)
    
    return wrapper


def require_admin(func):
    """
    Decorator to require admin group membership
    
    Usage:
        @require_admin
        def lambda_handler(event, context):
            # Only admins can access this
    """
    @wraps(func)
    def wrapper(event, context):
        user_info = get_user_from_event(event)
        
        if not user_info or not user_info.get('user_id'):
            logger.warning("Unauthorized access attempt")
            return unauthorized_error('Authentication required')
        
        if not is_admin(user_info):
            logger.warning(f"Forbidden: User {user_info.get('email')} attempted admin access")
            return forbidden_error('Admin access required')
        
        return func(event, context)
    
    return wrapper


def require_team_manager(func):
    """
    Decorator to require team manager group membership
    
    Usage:
        @require_team_manager
        def lambda_handler(event, context):
            # Only team managers can access this
    """
    @wraps(func)
    def wrapper(event, context):
        user_info = get_user_from_event(event)
        
        if not user_info or not user_info.get('user_id'):
            logger.warning("Unauthorized access attempt")
            return unauthorized_error('Authentication required')
        
        if not is_team_manager(user_info) and not is_admin(user_info):
            logger.warning(f"Forbidden: User {user_info.get('email')} attempted team manager access")
            return forbidden_error('Team manager access required')
        
        return func(event, context)
    
    return wrapper


def require_devops(func):
    """
    Decorator to require devops group membership
    
    Usage:
        @require_devops
        def lambda_handler(event, context):
            # Only devops can access this
    """
    @wraps(func)
    def wrapper(event, context):
        user_info = get_user_from_event(event)
        
        if not user_info or not user_info.get('user_id'):
            logger.warning("Unauthorized access attempt")
            return unauthorized_error('Authentication required')
        
        if not is_devops(user_info) and not is_admin(user_info):
            logger.warning(f"Forbidden: User {user_info.get('email')} attempted devops access")
            return forbidden_error('DevOps access required')
        
        return func(event, context)
    
    return wrapper


def require_any_role(*allowed_groups):
    """
    Decorator to require any of the specified groups
    
    Usage:
        @require_any_role('admins', 'devops')
        def lambda_handler(event, context):
            # Admins or devops can access this
    """
    def decorator(func):
        @wraps(func)
        def wrapper(event, context):
            user_info = get_user_from_event(event)
            
            if not user_info or not user_info.get('user_id'):
                logger.warning("Unauthorized access attempt")
                return unauthorized_error('Authentication required')
            
            user_groups = user_info.get('groups', [])
            if not any(group in user_groups for group in allowed_groups):
                logger.warning(f"Forbidden: User {user_info.get('email')} lacks required role")
                return forbidden_error(f'Access requires one of: {", ".join(allowed_groups)}')
            
            return func(event, context)
        
        return wrapper
    return decorator


def require_team_manager_or_admin_override(func):
    """
    Decorator to require team manager access or admin with override
    
    Allows:
    - Team managers to access their own data
    - Admins to access their own data
    - Admins to access any team manager's data via ?team_manager_id parameter
    
    Sets event['_effective_user_id'] for use in handler
    Sets event['_is_admin_override'] to track impersonation
    Sets event['_admin_user_id'] when impersonating
    
    Usage:
        @require_team_manager_or_admin_override
        def lambda_handler(event, context):
            team_manager_id = event['_effective_user_id']
            is_admin_override = event['_is_admin_override']
            # Use team_manager_id for data access
    """
    @wraps(func)
    def wrapper(event, context):
        user_info = get_user_from_event(event)
        
        if not user_info or not user_info.get('user_id'):
            logger.warning("Unauthorized access attempt")
            return unauthorized_error('Authentication required')
        
        # Check for admin override
        query_params = event.get('queryStringParameters', {}) or {}
        override_id = query_params.get('team_manager_id')
        
        if override_id:
            # Admin override requested
            if not is_admin(user_info):
                logger.warning(
                    f"Non-admin {user_info.get('email')} (user_id: {user_info.get('user_id')}) "
                    f"attempted impersonation of team manager {override_id}"
                )
                return forbidden_error('Admin access required for impersonation')
            
            # Set effective user ID and admin override flag
            event['_effective_user_id'] = override_id
            event['_is_admin_override'] = True
            event['_admin_user_id'] = user_info['user_id']
            
            # Audit logging for impersonation
            logger.info({
                'event': 'admin_impersonation',
                'admin_user_id': user_info['user_id'],
                'admin_email': user_info.get('email'),
                'impersonated_user_id': override_id,
                'action': context.function_name,
                'endpoint': event.get('path'),
                'method': event.get('httpMethod'),
                'message': f"Admin {user_info.get('email')} impersonating team manager {override_id}"
            })
        else:
            # Normal access - check team manager or admin permission
            if not is_team_manager(user_info) and not is_admin(user_info):
                logger.warning(
                    f"Forbidden: User {user_info.get('email')} (user_id: {user_info.get('user_id')}) "
                    f"attempted team manager access without proper permissions"
                )
                return forbidden_error('Team manager access required')
            
            # Set effective user ID to the authenticated user's ID
            event['_effective_user_id'] = user_info['user_id']
            event['_is_admin_override'] = False
        
        return func(event, context)
    
    return wrapper


def check_resource_ownership(user_info, resource_user_id):
    """
    Check if user owns a resource or is an admin
    
    Args:
        user_info: User information from get_user_from_event
        resource_user_id: User ID that owns the resource
        
    Returns:
        bool: True if user owns resource or is admin
    """
    if not user_info:
        return False
    
    # Admins can access any resource
    if is_admin(user_info):
        return True
    
    # Check ownership
    return user_info.get('user_id') == resource_user_id
