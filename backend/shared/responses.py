"""
Standardized response helpers for Lambda functions
Provides consistent response format across all API endpoints
"""
import json
import logging
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def decimal_default(obj):
    """
    JSON serializer for Decimal objects
    
    Args:
        obj: Object to serialize
        
    Returns:
        Serializable object
    """
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def success_response(data, status_code=200, message=None):
    """
    Create a successful API response
    
    Args:
        data: Response data
        status_code: HTTP status code (default: 200)
        message: Optional success message
        
    Returns:
        dict: API Gateway response
    """
    body = {
        'success': True,
        'data': data
    }
    
    if message:
        body['message'] = message
    
    body['timestamp'] = datetime.utcnow().isoformat() + 'Z'
    
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # CORS
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body, default=decimal_default)
    }
    
    logger.info(f"Success response: {status_code}")
    return response


def error_response(status_code, error_code, message, details=None):
    """
    Create an error API response
    
    Args:
        status_code: HTTP status code
        error_code: Application-specific error code
        message: Error message
        details: Optional error details
        
    Returns:
        dict: API Gateway response
    """
    body = {
        'success': False,
        'error': {
            'code': error_code,
            'message': message
        },
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    if details:
        body['error']['details'] = details
    
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # CORS
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body, default=decimal_default)
    }
    
    logger.warning(f"Error response: {status_code} - {error_code}: {message}")
    return response


# Common error responses
def validation_error(errors):
    """
    Create a validation error response
    
    Args:
        errors: Validation errors dictionary
        
    Returns:
        dict: API Gateway response
    """
    return error_response(
        status_code=400,
        error_code='VALIDATION_ERROR',
        message='Invalid input data',
        details=errors
    )


def not_found_error(resource_type, resource_id=None):
    """
    Create a not found error response
    
    Args:
        resource_type: Type of resource (e.g., 'crew_member', 'boat')
        resource_id: Optional resource ID
        
    Returns:
        dict: API Gateway response
    """
    message = f"{resource_type.replace('_', ' ').title()} not found"
    if resource_id:
        message += f": {resource_id}"
    
    return error_response(
        status_code=404,
        error_code='NOT_FOUND',
        message=message
    )


def unauthorized_error(message='Authentication required'):
    """
    Create an unauthorized error response
    
    Args:
        message: Error message
        
    Returns:
        dict: API Gateway response
    """
    return error_response(
        status_code=401,
        error_code='UNAUTHORIZED',
        message=message
    )


def forbidden_error(message='Insufficient permissions'):
    """
    Create a forbidden error response
    
    Args:
        message: Error message
        
    Returns:
        dict: API Gateway response
    """
    return error_response(
        status_code=403,
        error_code='FORBIDDEN',
        message=message
    )


def conflict_error(message, details=None):
    """
    Create a conflict error response
    
    Args:
        message: Error message
        details: Optional error details
        
    Returns:
        dict: API Gateway response
    """
    return error_response(
        status_code=409,
        error_code='CONFLICT',
        message=message,
        details=details
    )


def internal_error(message='An unexpected error occurred', details=None):
    """
    Create an internal server error response
    
    Args:
        message: Error message
        details: Optional error details (should not expose sensitive info)
        
    Returns:
        dict: API Gateway response
    """
    return error_response(
        status_code=500,
        error_code='INTERNAL_ERROR',
        message=message,
        details=details
    )


def bad_request_error(message, details=None):
    """
    Create a bad request error response
    
    Args:
        message: Error message
        details: Optional error details
        
    Returns:
        dict: API Gateway response
    """
    return error_response(
        status_code=400,
        error_code='BAD_REQUEST',
        message=message,
        details=details
    )


def service_unavailable_error(message='Service temporarily unavailable'):
    """
    Create a service unavailable error response
    
    Args:
        message: Error message
        
    Returns:
        dict: API Gateway response
    """
    return error_response(
        status_code=503,
        error_code='SERVICE_UNAVAILABLE',
        message=message
    )


# Response decorators
def handle_exceptions(func):
    """
    Decorator to handle exceptions in Lambda functions
    
    Usage:
        @handle_exceptions
        def lambda_handler(event, context):
            # Your code here
    """
    def wrapper(event, context):
        try:
            return func(event, context)
        except ValueError as e:
            logger.error(f"ValueError: {str(e)}")
            return bad_request_error(str(e))
        except KeyError as e:
            logger.error(f"KeyError: {str(e)}")
            return bad_request_error(f"Missing required field: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return internal_error()
    
    return wrapper


def require_fields(*required_fields):
    """
    Decorator to validate required fields in request body
    
    Usage:
        @require_fields('first_name', 'last_name', 'email')
        def lambda_handler(event, context):
            # Your code here
    """
    def decorator(func):
        def wrapper(event, context):
            try:
                body = json.loads(event.get('body', '{}'))
            except json.JSONDecodeError:
                return bad_request_error('Invalid JSON in request body')
            
            missing_fields = [field for field in required_fields if field not in body]
            if missing_fields:
                return validation_error({
                    'missing_fields': missing_fields
                })
            
            return func(event, context)
        
        return wrapper
    return decorator


# Helper functions
def parse_request_body(event):
    """
    Parse and validate request body from API Gateway event
    
    Args:
        event: API Gateway event
        
    Returns:
        dict: Parsed body
        
    Raises:
        ValueError: If body is invalid JSON
    """
    body = event.get('body', '{}')
    
    if isinstance(body, str):
        try:
            return json.loads(body)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in request body: {str(e)}")
    
    return body


def get_user_id(event):
    """
    Extract user ID from API Gateway event (from Cognito authorizer)
    
    Args:
        event: API Gateway event
        
    Returns:
        str: User ID or None
    """
    request_context = event.get('requestContext', {})
    authorizer = request_context.get('authorizer', {})
    claims = authorizer.get('claims', {})
    
    # Try different claim fields
    user_id = claims.get('sub') or claims.get('cognito:username') or claims.get('username')
    
    return user_id


def get_path_parameter(event, parameter_name):
    """
    Extract path parameter from API Gateway event
    
    Args:
        event: API Gateway event
        parameter_name: Name of the path parameter
        
    Returns:
        str: Parameter value or None
    """
    path_parameters = event.get('pathParameters', {})
    return path_parameters.get(parameter_name)


def get_query_parameter(event, parameter_name, default=None):
    """
    Extract query parameter from API Gateway event
    
    Args:
        event: API Gateway event
        parameter_name: Name of the query parameter
        default: Default value if parameter not found
        
    Returns:
        str: Parameter value or default
    """
    query_parameters = event.get('queryStringParameters', {}) or {}
    return query_parameters.get(parameter_name, default)


def cors_preflight_response():
    """
    Create a CORS preflight response for OPTIONS requests
    
    Returns:
        dict: API Gateway response
    """
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': ''
    }
