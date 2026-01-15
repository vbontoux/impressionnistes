"""
Centralized Access Control System

This module provides a unified permission management layer for the Course des 
Impressionnistes registration system. It determines which actions are permitted 
based on user role, impersonation status, event phases (dates), and data state.

Key Components:
- EventPhase: Enum representing the current phase of the event
- UserContext: User information for permission checks
- ResourceContext: Resource information for permission checks
- PermissionResult: Result of a permission check
- PermissionChecker: Main class for evaluating permissions
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
import time


# ============================================================================
# Enums
# ============================================================================

class EventPhase(Enum):
    """
    Represents the current phase of the event based on system dates.
    
    Phases:
    - BEFORE_REGISTRATION: Before registration_start_date
    - DURING_REGISTRATION: Between registration_start_date and registration_end_date
    - AFTER_REGISTRATION: After registration_end_date but before payment_deadline
    - AFTER_PAYMENT_DEADLINE: After payment_deadline
    """
    BEFORE_REGISTRATION = "before_registration"
    DURING_REGISTRATION = "during_registration"
    AFTER_REGISTRATION = "after_registration"
    AFTER_PAYMENT_DEADLINE = "after_payment_deadline"


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class UserContext:
    """
    User information for permission checks.
    
    Attributes:
        user_id: Unique identifier for the user
        role: User role ('admin' or 'team_manager')
        is_impersonating: True if admin is impersonating a team manager
        has_temporary_access: True if user has an active temporary access grant
        team_manager_id: ID of the team manager being impersonated (if applicable)
    """
    user_id: str
    role: str
    is_impersonating: bool = False
    has_temporary_access: bool = False
    team_manager_id: Optional[str] = None


@dataclass
class ResourceContext:
    """
    Resource information for permission checks.
    
    Attributes:
        resource_type: Type of resource ('crew_member', 'boat_registration', 'payment')
        resource_id: Unique identifier for the resource (optional)
        resource_state: Dictionary containing resource state information
                       e.g., {'assigned': True, 'paid': False}
    """
    resource_type: str
    resource_id: Optional[str] = None
    resource_state: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize resource_state to empty dict if None."""
        if self.resource_state is None:
            self.resource_state = {}


@dataclass
class PermissionResult:
    """
    Result of a permission check.
    
    Attributes:
        is_permitted: True if the action is allowed, False otherwise
        denial_reason: Human-readable explanation of why action was denied (optional)
        denial_reason_key: i18n key for the denial reason (optional)
        bypass_reason: Reason for bypass if applicable ('impersonation' or 'temporary_access')
    """
    is_permitted: bool
    denial_reason: Optional[str] = None
    denial_reason_key: Optional[str] = None
    bypass_reason: Optional[str] = None


# ============================================================================
# Constants
# ============================================================================

# Cache TTL in seconds
DEFAULT_CACHE_TTL = 60

# Default permission matrix (used as fallback if database config is missing)
DEFAULT_PERMISSIONS = {
    "create_crew_member": {
        "before_registration": False,
        "during_registration": True,
        "after_registration": False,
        "after_payment_deadline": False,
    },
    "edit_crew_member": {
        "before_registration": False,
        "during_registration": True,
        "after_registration": False,
        "after_payment_deadline": False,
        "requires_not_assigned": True,
    },
    "delete_crew_member": {
        "before_registration": False,
        "during_registration": True,
        "after_registration": False,
        "after_payment_deadline": False,
        "requires_not_assigned": True,
    },
    "create_boat_registration": {
        "before_registration": False,
        "during_registration": True,
        "after_registration": False,
        "after_payment_deadline": False,
    },
    "edit_boat_registration": {
        "before_registration": False,
        "during_registration": True,
        "after_registration": False,
        "after_payment_deadline": False,
        "requires_not_paid": True,
    },
    "delete_boat_registration": {
        "before_registration": False,
        "during_registration": True,
        "after_registration": False,
        "after_payment_deadline": False,
        "requires_not_paid": True,
    },
    "process_payment": {
        "before_registration": False,
        "during_registration": True,
        "after_registration": True,
        "after_payment_deadline": False,
    },
    "view_data": {
        "before_registration": True,
        "during_registration": True,
        "after_registration": True,
        "after_payment_deadline": True,
    },
    "export_data": {
        "before_registration": True,
        "during_registration": True,
        "after_registration": True,
        "after_payment_deadline": True,
    },
}

# Denial reason messages (English)
DENIAL_MESSAGES = {
    "before_registration": "Registration is not yet open. Opens on {date}.",
    "after_registration_closed": "Registration period has ended. Contact the organization for any changes.",
    "after_payment_deadline": "Payment deadline has passed. Contact the organization.",
    "crew_member_assigned": "Cannot edit an assigned crew member. Unassign from boat first.",
    "boat_paid": "Cannot edit a paid boat registration. Contact the organization.",
    "temporary_access_expired": "Your temporary access has expired. Contact an administrator.",
}

# Denial reason keys for i18n
DENIAL_REASON_KEYS = {
    "before_registration": "errors.permission.registration_not_open",
    "after_registration_closed": "errors.permission.registration_closed",
    "after_payment_deadline": "errors.permission.payment_deadline_passed",
    "crew_member_assigned": "errors.permission.crew_member_assigned",
    "boat_paid": "errors.permission.boat_paid",
    "temporary_access_expired": "errors.permission.temporary_access_expired",
}


# ============================================================================
# Main Permission Checker Class
# ============================================================================

class PermissionChecker:
    """
    Main class for evaluating permissions.
    
    This class provides methods to check if actions are permitted based on:
    - Current event phase (calculated from system dates)
    - User role and context (admin, team manager, impersonation)
    - Resource state (assigned crew, paid boat)
    - Temporary access grants
    
    The class implements caching for performance optimization.
    """
    
    def __init__(self, db_client=None, cache_ttl: int = DEFAULT_CACHE_TTL, table_name: str = None):
        """
        Initialize the PermissionChecker.
        
        Args:
            db_client: DynamoDB client for querying configuration and grants
            cache_ttl: Cache time-to-live in seconds (default: 60)
            table_name: DynamoDB table name (optional, defaults to TABLE_NAME env var)
        """
        self.db = db_client
        self.cache_ttl = cache_ttl
        self.table_name = table_name
        
        # Cache storage
        self._permission_cache = {}
        self._config_cache = {}
        self._phase_cache = None
        self._phase_cache_time = 0
        
    def check_permission(
        self,
        user_context: UserContext,
        action: str,
        resource_context: ResourceContext
    ) -> PermissionResult:
        """
        Check if an action is permitted.
        
        This is the main entry point for permission checking. It evaluates:
        1. Event phase restrictions
        2. Data state restrictions
        3. Impersonation bypass rules
        4. Temporary access grant bypass rules
        
        Args:
            user_context: User information
            action: Action to perform (e.g., 'create_crew_member')
            resource_context: Resource information
        
        Returns:
            PermissionResult with is_permitted and optional denial_reason
        """
        # Step 1: Get current event phase
        current_phase = self.get_current_event_phase()
        
        # Step 2: Load permission matrix
        permission_matrix = self.get_permission_matrix()
        
        # Step 3: Get action rules from matrix
        action_rules = permission_matrix.get(action)
        if action_rules is None:
            # Unknown action - deny by default
            return PermissionResult(
                is_permitted=False,
                denial_reason=f"Unknown action: {action}",
                denial_reason_key="errors.unknown_action"
            )
        
        # Step 4: Check if user has bypass (impersonation or temporary access)
        has_bypass = False
        bypass_reason = None
        
        if user_context.is_impersonating:
            has_bypass = True
            bypass_reason = "impersonation"
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Admin impersonation detected - bypassing ALL restrictions for action: {action}")
            # Admin with impersonation gets FULL override - bypass everything
            return PermissionResult(
                is_permitted=True,
                bypass_reason="impersonation"
            )
        elif user_context.has_temporary_access:
            # Verify temporary access is still active
            if self.check_temporary_access_grant(user_context.user_id):
                has_bypass = True
                bypass_reason = "temporary_access"
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Temporary access grant detected - bypassing phase restrictions for action: {action}")
        
        # Step 5: Check data state restrictions (apply to non-impersonating users)
        # Note: Impersonation bypasses these checks (returned early above)
        data_state_result = self._check_data_state_restrictions(
            action_rules,
            resource_context
        )
        if not data_state_result.is_permitted:
            return data_state_result
        
        # Step 6: Check phase-based permissions
        phase_key = current_phase.value
        phase_allowed = action_rules.get(phase_key, False)
        
        if not phase_allowed and not has_bypass:
            # Phase restriction applies and no bypass available
            denial_reason = self._get_phase_denial_message(current_phase)
            denial_reason_key = self._get_phase_denial_key(current_phase)
            return PermissionResult(
                is_permitted=False,
                denial_reason=denial_reason,
                denial_reason_key=denial_reason_key
            )
        
        # Action is permitted
        return PermissionResult(
            is_permitted=True,
            bypass_reason=bypass_reason
        )
    
    def _check_data_state_restrictions(
        self,
        action_rules: Dict[str, Any],
        resource_context: ResourceContext
    ) -> PermissionResult:
        """
        Check data state restrictions for an action.
        
        Data state restrictions apply to team managers and users with temporary
        access grants, but NOT to admins using impersonation (they get full override).
        
        Args:
            action_rules: Rules for the action from permission matrix
            resource_context: Resource information
        
        Returns:
            PermissionResult indicating if data state allows the action
        """
        resource_state = resource_context.resource_state or {}
        
        # Check if action requires crew member to not be assigned
        if action_rules.get('requires_not_assigned', False):
            if resource_state.get('assigned', False):
                return PermissionResult(
                    is_permitted=False,
                    denial_reason=DENIAL_MESSAGES['crew_member_assigned'],
                    denial_reason_key=DENIAL_REASON_KEYS['crew_member_assigned']
                )
        
        # Check if action requires boat to not be paid
        if action_rules.get('requires_not_paid', False):
            if resource_state.get('paid', False):
                return PermissionResult(
                    is_permitted=False,
                    denial_reason=DENIAL_MESSAGES['boat_paid'],
                    denial_reason_key=DENIAL_REASON_KEYS['boat_paid']
                )
        
        # No data state restrictions violated
        return PermissionResult(is_permitted=True)
    
    def _get_phase_denial_message(self, phase: EventPhase) -> str:
        """
        Get denial message for a specific event phase.
        
        Args:
            phase: Current event phase
        
        Returns:
            Human-readable denial message
        """
        if phase == EventPhase.BEFORE_REGISTRATION:
            return DENIAL_MESSAGES['before_registration']
        elif phase == EventPhase.AFTER_REGISTRATION:
            return DENIAL_MESSAGES['after_registration_closed']
        elif phase == EventPhase.AFTER_PAYMENT_DEADLINE:
            return DENIAL_MESSAGES['after_payment_deadline']
        else:
            return "Action not permitted in current phase"
    
    def _get_phase_denial_key(self, phase: EventPhase) -> str:
        """
        Get i18n key for phase denial message.
        
        Args:
            phase: Current event phase
        
        Returns:
            i18n key for denial message
        """
        if phase == EventPhase.BEFORE_REGISTRATION:
            return DENIAL_REASON_KEYS['before_registration']
        elif phase == EventPhase.AFTER_REGISTRATION:
            return DENIAL_REASON_KEYS['after_registration_closed']
        elif phase == EventPhase.AFTER_PAYMENT_DEADLINE:
            return DENIAL_REASON_KEYS['after_payment_deadline']
        else:
            return "errors.phase_restriction"
    
    def get_current_event_phase(self) -> EventPhase:
        """
        Determine current event phase based on system time and config dates.
        
        Uses caching to avoid repeated database queries within the cache TTL.
        
        Returns:
            EventPhase enum value
        """
        # Check cache first
        current_time = time.time()
        if self._phase_cache is not None and (current_time - self._phase_cache_time) < self.cache_ttl:
            return self._phase_cache
        
        # Import configuration module
        from configuration import ConfigurationManager
        
        # Get system configuration
        if self.table_name:
            config_manager = ConfigurationManager(table_name=self.table_name)
        else:
            from configuration import get_config_manager
            config_manager = get_config_manager()
        
        system_config = config_manager.get_system_config()
        
        # Extract dates from configuration
        registration_start_str = system_config.get('registration_start_date')
        registration_end_str = system_config.get('registration_end_date')
        payment_deadline_str = system_config.get('payment_deadline')
        
        # Handle missing configuration - default to most restrictive phase
        if not all([registration_start_str, registration_end_str, payment_deadline_str]):
            import logging
            logger = logging.getLogger(__name__)
            logger.error("Missing date configuration for event phase detection")
            # Default to most restrictive phase for safety
            phase = EventPhase.AFTER_PAYMENT_DEADLINE
            self._phase_cache = phase
            self._phase_cache_time = current_time
            return phase
        
        # Parse dates (handle both date-only and ISO datetime formats)
        try:
            # Try parsing as date-only format first (YYYY-MM-DD)
            if 'T' in registration_start_str:
                registration_start = datetime.fromisoformat(registration_start_str.replace('Z', '+00:00'))
                # Remove timezone info to make it naive for comparison
                registration_start = registration_start.replace(tzinfo=None)
            else:
                registration_start = datetime.fromisoformat(registration_start_str + 'T00:00:00')
            
            if 'T' in registration_end_str:
                registration_end = datetime.fromisoformat(registration_end_str.replace('Z', '+00:00'))
                # Remove timezone info to make it naive for comparison
                registration_end = registration_end.replace(tzinfo=None)
            else:
                registration_end = datetime.fromisoformat(registration_end_str + 'T23:59:59')
            
            if 'T' in payment_deadline_str:
                payment_deadline = datetime.fromisoformat(payment_deadline_str.replace('Z', '+00:00'))
                # Remove timezone info to make it naive for comparison
                payment_deadline = payment_deadline.replace(tzinfo=None)
            else:
                payment_deadline = datetime.fromisoformat(payment_deadline_str + 'T23:59:59')
        except (ValueError, AttributeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Invalid date format in configuration: {e}")
            # Default to most restrictive phase for safety
            phase = EventPhase.AFTER_PAYMENT_DEADLINE
            self._phase_cache = phase
            self._phase_cache_time = current_time
            return phase
        
        # Get current time (use UTC for consistency)
        now = datetime.utcnow()
        
        # Determine phase based on current time
        if now < registration_start:
            phase = EventPhase.BEFORE_REGISTRATION
        elif registration_start <= now <= registration_end:
            phase = EventPhase.DURING_REGISTRATION
        elif registration_end < now <= payment_deadline:
            phase = EventPhase.AFTER_REGISTRATION
        else:  # now > payment_deadline
            phase = EventPhase.AFTER_PAYMENT_DEADLINE
        
        # Cache the result
        self._phase_cache = phase
        self._phase_cache_time = current_time
        
        return phase
    
    def get_permission_matrix(self) -> Dict[str, Any]:
        """
        Retrieve permission matrix from database (with caching).
        
        Falls back to DEFAULT_PERMISSIONS if database config is missing.
        Uses 60-second caching to avoid repeated database queries.
        
        Returns:
            Dictionary mapping actions to phase-based rules
        """
        # Check cache first
        current_time = time.time()
        if self._config_cache.get('matrix') is not None and \
           (current_time - self._config_cache.get('matrix_time', 0)) < self.cache_ttl:
            return self._config_cache['matrix']
        
        # Import configuration module
        from configuration import ConfigurationManager
        
        # Get permission configuration from database
        try:
            if self.table_name:
                config_manager = ConfigurationManager(table_name=self.table_name)
            else:
                from configuration import get_config_manager
                config_manager = get_config_manager()
            
            # Query for CONFIG#PERMISSIONS
            import boto3
            if self.db is None:
                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table(config_manager.table_name)
            else:
                table = self.db.Table(config_manager.table_name)
            
            response = table.get_item(
                Key={
                    'PK': 'CONFIG',
                    'SK': 'PERMISSIONS'
                }
            )
            
            if 'Item' in response and 'permissions' in response['Item']:
                matrix = response['Item']['permissions']
                # Cache the result
                self._config_cache['matrix'] = matrix
                self._config_cache['matrix_time'] = current_time
                return matrix
            else:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning("Permission matrix not found in database, using defaults")
                # Fall back to defaults
                matrix = DEFAULT_PERMISSIONS.copy()
                # Cache the default matrix
                self._config_cache['matrix'] = matrix
                self._config_cache['matrix_time'] = current_time
                return matrix
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading permission matrix: {e}")
            # Fall back to defaults
            matrix = DEFAULT_PERMISSIONS.copy()
            # Cache the default matrix
            self._config_cache['matrix'] = matrix
            self._config_cache['matrix_time'] = current_time
            return matrix
    
    def check_temporary_access_grant(self, user_id: str) -> bool:
        """
        Check if user has an active temporary access grant.
        
        Queries DynamoDB for active grants and checks expiration.
        Automatically marks expired grants as expired.
        
        Args:
            user_id: User ID to check
        
        Returns:
            True if active grant exists, False otherwise
        """
        # Import configuration module
        from configuration import ConfigurationManager
        
        try:
            # Get table
            if self.table_name:
                config_manager = ConfigurationManager(table_name=self.table_name)
            else:
                from configuration import get_config_manager
                config_manager = get_config_manager()
            
            import boto3
            if self.db is None:
                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table(config_manager.table_name)
            else:
                table = self.db.Table(config_manager.table_name)
            
            # Query for temporary access grant
            response = table.get_item(
                Key={
                    'PK': 'TEMP_ACCESS',
                    'SK': f'USER#{user_id}'
                }
            )
            
            if 'Item' not in response:
                return False
            
            grant = response['Item']
            
            # Check if grant is active
            if grant.get('status') != 'active':
                return False
            
            # Check if grant has expired
            expiration_str = grant.get('expiration_timestamp')
            if not expiration_str:
                return False
            
            # Parse expiration timestamp
            try:
                if 'T' in expiration_str:
                    expiration = datetime.fromisoformat(expiration_str.replace('Z', '+00:00'))
                    # Remove timezone info for comparison
                    expiration = expiration.replace(tzinfo=None)
                else:
                    expiration = datetime.fromisoformat(expiration_str + 'T23:59:59')
            except (ValueError, AttributeError):
                return False
            
            # Get current time (UTC)
            now = datetime.utcnow()
            
            # Check if expired
            if now > expiration:
                # Mark grant as expired
                try:
                    table.update_item(
                        Key={
                            'PK': 'TEMP_ACCESS',
                            'SK': f'USER#{user_id}'
                        },
                        UpdateExpression='SET #status = :expired, updated_at = :now',
                        ExpressionAttributeNames={
                            '#status': 'status'
                        },
                        ExpressionAttributeValues={
                            ':expired': 'expired',
                            ':now': datetime.utcnow().isoformat() + 'Z'
                        }
                    )
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to mark grant as expired: {e}")
                
                return False
            
            # Grant is active and not expired
            return True
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error checking temporary access grant: {e}")
            return False
    
    def invalidate_cache(self):
        """
        Invalidate all caches.
        
        Should be called when configuration is updated to ensure
        permission checks reflect the latest rules.
        """
        self._permission_cache.clear()
        self._config_cache.clear()
        self._phase_cache = None
        self._phase_cache_time = 0


# ============================================================================
# Helper Functions
# ============================================================================

def require_permission(action: str):
    """
    Decorator for Lambda handlers to enforce permissions.
    
    This decorator extracts user and resource context from the Lambda event,
    checks permissions, and returns HTTP 403 if denied.
    
    Usage:
        @require_permission('create_crew_member')
        def lambda_handler(event, context):
            # Handler code
    
    Args:
        action: Action to check permission for
    
    Returns:
        Decorator function
    """
    from functools import wraps
    import json
    
    def decorator(func):
        @wraps(func)
        def wrapper(event, context):
            import logging
            logger = logging.getLogger(__name__)
            
            try:
                # Get table name from environment first
                import os
                table_name = os.environ.get('TABLE_NAME')
                
                # Step 1: Extract user context from event
                user_context = get_user_context_from_event(event)
                
                # Log user context for debugging
                logger.info(f"Permission check for action '{action}': user_id={user_context.user_id}, "
                           f"role={user_context.role}, is_impersonating={user_context.is_impersonating}, "
                           f"has_temporary_access={user_context.has_temporary_access}")
                
                # Step 2: Extract resource context from body
                # Parse body if it's a string
                body = event.get('body', {})
                if isinstance(body, str):
                    try:
                        body = json.loads(body) if body else {}
                    except json.JSONDecodeError:
                        body = {}
                
                # Determine resource type from action
                resource_type = _get_resource_type_from_action(action)
                resource_context = get_resource_context_from_body(body, resource_type, event, table_name)
                
                # Step 3: Check permission
                checker = PermissionChecker(table_name=table_name)
                result = checker.check_permission(user_context, action, resource_context)
                
                # Step 4: Handle result
                if not result.is_permitted:
                    # Log denial with details
                    logger.warning(f"Permission denied for action '{action}': "
                                 f"reason={result.denial_reason}, "
                                 f"user_id={user_context.user_id}, "
                                 f"is_impersonating={user_context.is_impersonating}, "
                                 f"resource_type={resource_context.resource_type}, "
                                 f"resource_state={resource_context.resource_state}")
                    
                    # Log denial
                    log_permission_denial(
                        user_context,
                        action,
                        resource_context,
                        result.denial_reason or "Permission denied"
                    )
                    
                    # Return HTTP 403
                    return {
                        'statusCode': 403,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({
                            'success': False,
                            'error': 'Permission denied',
                            'reason': result.denial_reason,
                            'reason_key': result.denial_reason_key,
                            'action': action
                        })
                    }
                
                # Step 5: Log bypass if applicable
                if result.bypass_reason:
                    log_permission_grant_with_bypass(
                        user_context,
                        action,
                        resource_context,
                        result.bypass_reason
                    )
                
                # Step 6: Permission granted - execute handler
                return func(event, context)
                
            except Exception as e:
                logger.error(f"Error in permission check: {e}", exc_info=True)
                # On error, deny access for safety
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Internal server error',
                        'message': 'Permission check failed'
                    })
                }
        
        return wrapper
    return decorator


def _get_resource_type_from_action(action: str) -> str:
    """
    Determine resource type from action name.
    
    Args:
        action: Action name (e.g., 'create_crew_member')
    
    Returns:
        Resource type (e.g., 'crew_member')
    """
    if 'crew_member' in action:
        return 'crew_member'
    elif 'boat_registration' in action or 'boat' in action:
        return 'boat_registration'
    elif 'payment' in action:
        return 'payment'
    else:
        return 'unknown'


def get_user_context_from_event(event: Dict[str, Any]) -> UserContext:
    """
    Extract user context from Lambda event.
    
    Parses the event to extract user ID, role, impersonation status, etc.
    Uses the existing auth_utils pattern for consistency.
    
    Args:
        event: Lambda event dictionary
    
    Returns:
        UserContext with user information
    """
    import logging
    import os
    logger = logging.getLogger(__name__)
    
    try:
        # Import auth utilities
        from auth_utils import get_user_from_event, is_admin
        
        # Get user info from event (Cognito claims)
        user_info = get_user_from_event(event)
        
        if not user_info or not user_info.get('user_id'):
            # No authenticated user - return minimal context
            return UserContext(
                user_id="anonymous",
                role="anonymous",
                is_impersonating=False,
                has_temporary_access=False
            )
        
        # Extract actual user ID and role from Cognito
        actual_user_id = user_info['user_id']
        role = 'admin' if is_admin(user_info) else 'team_manager'
        
        # Check for impersonation (admin override)
        # Check both the event flag and the Cognito claims
        is_impersonating = event.get('_is_admin_override', False)
        team_manager_id = event.get('_effective_user_id') if is_impersonating else None
        
        # Also check for impersonation in Cognito claims
        if not is_impersonating:
            claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
            impersonated_user_id = claims.get('custom:impersonated_user_id')
            if impersonated_user_id:
                is_impersonating = True
                team_manager_id = impersonated_user_id
        
        # Determine effective user ID for permission checks
        # When impersonating, use the impersonated user's ID for permission checks
        # This allows checking temporary access grants for the impersonated user
        effective_user_id = team_manager_id if is_impersonating else actual_user_id
        
        # Check for temporary access grant using effective user ID
        table_name = os.environ.get('TABLE_NAME')
        checker = PermissionChecker(table_name=table_name)
        has_temporary_access = checker.check_temporary_access_grant(effective_user_id)
        
        return UserContext(
            user_id=effective_user_id,  # Use effective user ID for permission checks
            role=role,
            is_impersonating=is_impersonating,
            has_temporary_access=has_temporary_access,
            team_manager_id=team_manager_id
        )
        
    except Exception as e:
        logger.error(f"Error extracting user context: {e}", exc_info=True)
        # Return minimal context on error
        return UserContext(
            user_id="error",
            role="anonymous",
            is_impersonating=False,
            has_temporary_access=False
        )


def get_resource_context_from_body(
    body: Dict[str, Any],
    resource_type: str,
    event: Dict[str, Any] = None,
    table_name: str = None
) -> ResourceContext:
    """
    Extract resource context from request body and event.
    
    Parses the request body to extract resource information and state.
    For update/delete operations, may need to query database for current state.
    
    Args:
        body: Request body dictionary
        resource_type: Type of resource ('crew_member', 'boat_registration', etc.)
        event: Full Lambda event (optional, for path parameters)
        table_name: DynamoDB table name (optional)
    
    Returns:
        ResourceContext with resource information
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Extract resource ID from path parameters or body
        resource_id = None
        if event:
            path_params = event.get('pathParameters', {}) or {}
            resource_id = (
                path_params.get('crew_member_id') or
                path_params.get('boat_registration_id') or
                path_params.get('id')
            )
        
        if not resource_id:
            resource_id = body.get('crew_member_id') or body.get('boat_registration_id')
        
        # Extract team_manager_id from event for querying
        team_manager_id = None
        if event:
            # Try to get from _effective_user_id (set by auth decorator)
            team_manager_id = event.get('_effective_user_id')
            # If not set, try to get from user context
            if not team_manager_id:
                from auth_utils import get_user_from_event
                user_info = get_user_from_event(event)
                if user_info:
                    team_manager_id = user_info.get('user_id')
        
        # Extract resource state from body or query database
        resource_state = {}
        
        if resource_type == 'crew_member':
            # Check if crew member is assigned to a boat
            # For create operations, not assigned
            # For update/delete, need to check database
            if resource_id and team_manager_id:
                resource_state = _get_crew_member_state(resource_id, team_manager_id, table_name)
            else:
                resource_state = {'assigned': False}
        
        elif resource_type == 'boat_registration':
            # Check if boat is paid
            # For create operations, not paid
            # For update/delete, need to check database
            if resource_id and team_manager_id:
                resource_state = _get_boat_registration_state(resource_id, team_manager_id, table_name)
            else:
                resource_state = {'paid': False}
        
        return ResourceContext(
            resource_type=resource_type,
            resource_id=resource_id,
            resource_state=resource_state
        )
        
    except Exception as e:
        logger.error(f"Error extracting resource context: {e}", exc_info=True)
        # Return minimal context on error
        return ResourceContext(
            resource_type=resource_type,
            resource_id=None,
            resource_state={}
        )


def _get_crew_member_state(crew_member_id: str, team_manager_id: str, table_name: str = None) -> Dict[str, Any]:
    """
    Query database to get crew member state.
    
    Args:
        crew_member_id: Crew member ID
        team_manager_id: Team manager ID who owns the crew member
        table_name: DynamoDB table name (optional)
    
    Returns:
        Dictionary with state information (e.g., {'assigned': True})
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from database import DatabaseClient
        
        # Create a new client with the specified table name
        db = DatabaseClient(table_name=table_name)
        
        # Query crew member using the correct PK/SK structure
        crew_member = db.get_item(
            pk=f'TEAM#{team_manager_id}',
            sk=f'CREW#{crew_member_id}'
        )
        
        if not crew_member:
            return {'assigned': False}
        
        # Check if assigned to a boat
        assigned = bool(crew_member.get('assigned_boat_id'))
        
        return {'assigned': assigned}
        
    except Exception as e:
        logger.error(f"Error getting crew member state: {e}", exc_info=True)
        # Default to not assigned on error (safer)
        return {'assigned': False}


def _get_boat_registration_state(boat_registration_id: str, team_manager_id: str, table_name: str = None) -> Dict[str, Any]:
    """
    Query database to get boat registration state.
    
    Args:
        boat_registration_id: Boat registration ID
        team_manager_id: Team manager ID who owns the boat registration
        table_name: DynamoDB table name (optional)
    
    Returns:
        Dictionary with state information (e.g., {'paid': True})
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from database import DatabaseClient
        
        # Create a new client with the specified table name
        db = DatabaseClient(table_name=table_name)
        
        # Query boat registration using the correct PK/SK structure
        boat = db.get_item(
            pk=f'TEAM#{team_manager_id}',
            sk=f'BOAT#{boat_registration_id}'
        )
        
        if not boat:
            return {'paid': False}
        
        # Check if paid
        paid = boat.get('registration_status') == 'paid'
        
        return {'paid': paid}
        
    except Exception as e:
        logger.error(f"Error getting boat registration state: {e}", exc_info=True)
        # Default to not paid on error (safer)
        return {'paid': False}


def log_permission_denial(
    user_context: UserContext,
    action: str,
    resource_context: ResourceContext,
    reason: str,
    db_client=None,
    table_name: str = None
):
    """
    Log permission denial to DynamoDB audit table.
    
    Creates an audit log entry for denied permission checks.
    Handles write failures gracefully by logging to CloudWatch.
    
    Args:
        user_context: User who attempted the action
        action: Action that was denied
        resource_context: Resource that was targeted
        reason: Reason for denial
        db_client: DynamoDB client (optional)
        table_name: DynamoDB table name (optional)
    """
    import logging
    import boto3
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get table
        if table_name:
            from configuration import ConfigurationManager
            config_manager = ConfigurationManager(table_name=table_name)
        else:
            from configuration import get_config_manager
            config_manager = get_config_manager()
        
        if db_client is None:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(config_manager.table_name)
        else:
            table = db_client.Table(config_manager.table_name)
        
        # Create timestamp
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Create audit log entry
        audit_entry = {
            'PK': 'AUDIT#PERMISSION_DENIAL',
            'SK': f'{timestamp}#{user_context.user_id}',
            'user_id': user_context.user_id,
            'action': action,
            'resource_type': resource_context.resource_type,
            'resource_id': resource_context.resource_id or 'N/A',
            'denial_reason': reason,
            'timestamp': timestamp
        }
        
        # Add optional fields if available
        if resource_context.resource_state:
            audit_entry['resource_state'] = resource_context.resource_state
        
        # Write to DynamoDB
        table.put_item(Item=audit_entry)
        
        logger.info(f"Permission denial logged: user={user_context.user_id}, action={action}, reason={reason}")
        
    except Exception as e:
        # Handle write failures gracefully - log to CloudWatch but don't fail the request
        logger.error(f"Failed to log permission denial to DynamoDB: {e}")
        logger.error(f"Denial details: user={user_context.user_id}, action={action}, reason={reason}")


def log_permission_grant_with_bypass(
    user_context: UserContext,
    action: str,
    resource_context: ResourceContext,
    bypass_reason: str,
    db_client=None,
    table_name: str = None
):
    """
    Log permission grant that used impersonation or temporary access.
    
    Creates an audit log entry for actions that bypassed normal restrictions.
    Handles write failures gracefully by logging to CloudWatch.
    
    Args:
        user_context: User who performed the action
        action: Action that was performed
        resource_context: Resource that was targeted
        bypass_reason: Reason for bypass ('impersonation' or 'temporary_access')
        db_client: DynamoDB client (optional)
        table_name: DynamoDB table name (optional)
    """
    import logging
    import boto3
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get table
        if table_name:
            from configuration import ConfigurationManager
            config_manager = ConfigurationManager(table_name=table_name)
        else:
            from configuration import get_config_manager
            config_manager = get_config_manager()
        
        if db_client is None:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(config_manager.table_name)
        else:
            table = db_client.Table(config_manager.table_name)
        
        # Create timestamp
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Create audit log entry
        audit_entry = {
            'PK': 'AUDIT#PERMISSION_BYPASS',
            'SK': f'{timestamp}#{user_context.user_id}',
            'user_id': user_context.user_id,
            'action': action,
            'resource_type': resource_context.resource_type,
            'resource_id': resource_context.resource_id or 'N/A',
            'bypass_reason': bypass_reason,
            'timestamp': timestamp
        }
        
        # Add impersonated_user_id if applicable
        if bypass_reason == 'impersonation' and user_context.team_manager_id:
            audit_entry['impersonated_user_id'] = user_context.team_manager_id
        
        # Add optional fields if available
        if resource_context.resource_state:
            audit_entry['resource_state'] = resource_context.resource_state
        
        # Write to DynamoDB
        table.put_item(Item=audit_entry)
        
        logger.info(f"Permission bypass logged: user={user_context.user_id}, action={action}, bypass={bypass_reason}")
        
    except Exception as e:
        # Handle write failures gracefully - log to CloudWatch but don't fail the request
        logger.error(f"Failed to log permission bypass to DynamoDB: {e}")
        logger.error(f"Bypass details: user={user_context.user_id}, action={action}, bypass={bypass_reason}")


def get_default_permissions():
    """
    Get the default permission matrix.
    
    Returns:
        dict: Default permission configuration matching requirements appendix A
    """
    return {
        'create_crew_member': {
            'before_registration': False,
            'during_registration': True,
            'after_registration': False,
            'after_payment_deadline': False,
            'description': 'Create new crew member'
        },
        'edit_crew_member': {
            'before_registration': False,
            'during_registration': True,
            'after_registration': False,
            'after_payment_deadline': False,
            'requires_not_assigned': True,
            'description': 'Edit existing crew member'
        },
        'delete_crew_member': {
            'before_registration': False,
            'during_registration': True,
            'after_registration': False,
            'after_payment_deadline': False,
            'requires_not_assigned': True,
            'description': 'Delete crew member'
        },
        'create_boat_registration': {
            'before_registration': False,
            'during_registration': True,
            'after_registration': False,
            'after_payment_deadline': False,
            'description': 'Create new boat registration'
        },
        'edit_boat_registration': {
            'before_registration': False,
            'during_registration': True,
            'after_registration': False,
            'after_payment_deadline': False,
            'requires_not_paid': True,
            'description': 'Edit boat registration'
        },
        'delete_boat_registration': {
            'before_registration': False,
            'during_registration': True,
            'after_registration': False,
            'after_payment_deadline': False,
            'requires_not_paid': True,
            'description': 'Delete boat registration'
        },
        'process_payment': {
            'before_registration': False,
            'during_registration': True,
            'after_registration': True,
            'after_payment_deadline': False,
            'description': 'Process payment for boat registration'
        },
        'view_data': {
            'before_registration': True,
            'during_registration': True,
            'after_registration': True,
            'after_payment_deadline': True,
            'description': 'View data (always allowed)'
        },
        'export_data': {
            'before_registration': True,
            'during_registration': True,
            'after_registration': True,
            'after_payment_deadline': True,
            'description': 'Export data (always allowed)'
        }
    }
