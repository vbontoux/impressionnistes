"""
Shared utilities for Course des Impressionnistes Registration System Backend
"""
from .configuration import (
    ConfigurationManager,
    get_config_manager,
    get_base_seat_price,
    get_registration_period,
    is_registration_active,
    is_payment_active
)

from .database import (
    DatabaseClient,
    get_db_client,
    generate_id,
    get_timestamp,
    decimal_to_float,
    float_to_decimal
)

from .validation import (
    validate_crew_member,
    validate_boat_registration,
    validate_team_manager,
    validate_config_update,
    validate_email,
    validate_phone,
    sanitize_string,
    sanitize_dict
)

from .responses import (
    success_response,
    error_response,
    validation_error,
    not_found_error,
    unauthorized_error,
    forbidden_error,
    conflict_error,
    internal_error,
    bad_request_error,
    service_unavailable_error,
    handle_exceptions,
    require_fields,
    parse_request_body,
    get_user_id,
    get_path_parameter,
    get_query_parameter,
    cors_preflight_response
)

__all__ = [
    # Configuration
    'ConfigurationManager',
    'get_config_manager',
    'get_base_seat_price',
    'get_registration_period',
    'is_registration_active',
    'is_payment_active',
    
    # Database
    'DatabaseClient',
    'get_db_client',
    'generate_id',
    'get_timestamp',
    'decimal_to_float',
    'float_to_decimal',
    
    # Validation
    'validate_crew_member',
    'validate_boat_registration',
    'validate_team_manager',
    'validate_config_update',
    'validate_email',
    'validate_phone',
    'sanitize_string',
    'sanitize_dict',
    
    # Responses
    'success_response',
    'error_response',
    'validation_error',
    'not_found_error',
    'unauthorized_error',
    'forbidden_error',
    'conflict_error',
    'internal_error',
    'bad_request_error',
    'service_unavailable_error',
    'handle_exceptions',
    'require_fields',
    'parse_request_body',
    'get_user_id',
    'get_path_parameter',
    'get_query_parameter',
    'cors_preflight_response',
]
