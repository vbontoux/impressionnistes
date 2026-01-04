"""
Validation utilities using Cerberus
Provides schemas and validation functions for all data models
"""
import re
from cerberus import Validator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Custom validators
class CustomValidator(Validator):
    """Extended Validator with custom validation rules"""
    
    def _validate_license_number(self, constraint, field, value):
        """
        Validate license number format (alphanumeric, 6-12 characters)
        
        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if constraint and value:
            if not re.match(r'^[A-Z0-9]{6,12}$', value):
                self._error(field, "Must be alphanumeric and 6-12 characters")
    
    def _validate_date_format(self, constraint, field, value):
        """
        Validate date format (YYYY-MM-DD)
        
        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if constraint and value:
            try:
                datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                self._error(field, "Must be in YYYY-MM-DD format")
    
    def _validate_future_date(self, constraint, field, value):
        """
        Validate that date is in the future
        
        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if constraint and value:
            try:
                date = datetime.strptime(value, '%Y-%m-%d').date()
                if date <= datetime.now().date():
                    self._error(field, "Must be a future date")
            except ValueError:
                pass  # Date format error will be caught by date_format validator
    
    def _validate_birth_date_range(self, constraint, field, value):
        """
        Validate that birth date is within acceptable range for rowers
        Age is calculated as the age the person will reach during the current year.
        Minimum age is J14 (14 years old).
        Cannot be in the future.
        
        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if constraint and value:
            try:
                birth_date = datetime.strptime(value, '%Y-%m-%d').date()
                today = datetime.now().date()
                current_year = today.year
                birth_year = birth_date.year
                
                # Calculate age the person will reach during the current year
                age_this_year = current_year - birth_year
                
                # Minimum age is J14 (14 years old)
                min_age = 14
                
                if birth_date > today:
                    self._error(field, "Date of birth cannot be in the future")
                elif age_this_year < min_age:
                    # Too young - will not reach minimum age this year
                    min_birth_year = current_year - min_age
                    self._error(field, f"Rower must be born in {min_birth_year} or earlier (minimum age J14)")
            except ValueError:
                pass  # Date format error will be caught by date_format validator


# Crew Member Schema
crew_member_schema = {
    'first_name': {
        'type': 'string',
        'required': True,
        'minlength': 1,
        'maxlength': 50,
        'empty': False
    },
    'last_name': {
        'type': 'string',
        'required': True,
        'minlength': 1,
        'maxlength': 50,
        'empty': False
    },
    'date_of_birth': {
        'type': 'string',
        'required': True,
        'date_format': True,
        'birth_date_range': True
    },
    'gender': {
        'type': 'string',
        'required': True,
        'allowed': ['M', 'F']
    },
    'license_number': {
        'type': 'string',
        'required': True,
        'license_number': True
    },
    'club_affiliation': {
        'type': 'string',
        'required': False,
        'maxlength': 100,
        'nullable': True
    },
    'is_rcpm_member': {
        'type': 'boolean',
        'required': False,
        'default': False
    },
    'assigned_boat_id': {
        'type': 'string',
        'required': False,
        'nullable': True
    }
}


# Boat Registration Schema
boat_registration_schema = {
    'event_type': {
        'type': 'string',
        'required': True,
        'allowed': ['21km', '42km']
    },
    'boat_type': {
        'type': 'string',
        'required': True,
        'allowed': ['skiff', '4-', '4+', '8+']
    },
    'race_id': {
        'type': 'string',
        'required': False,  # Optional until race is selected
        'nullable': True
    },
    'seats': {
        'type': 'list',
        'required': True,
        'schema': {
            'type': 'dict',
            'schema': {
                'position': {
                    'type': 'integer',
                    'required': True,
                    'min': 1,
                    'max': 9
                },
                'type': {
                    'type': 'string',
                    'required': True,
                    'allowed': ['rower', 'cox']
                },
                'crew_member_id': {
                    'type': 'string',
                    'required': False,
                    'nullable': True
                }
            }
        }
    },
    'is_multi_club_crew': {
        'type': 'boolean',
        'required': False,
        'default': False
    },
    'boat_club_display': {
        'type': 'string',
        'required': False,
        'nullable': True,
        'maxlength': 200
    },
    'club_list': {
        'type': 'list',
        'required': False,
        'nullable': True,
        'schema': {
            'type': 'string',
            'maxlength': 100
        }
    },
    'boat_number': {
        'type': 'string',
        'required': False,
        'nullable': True,
        'maxlength': 20,
        'regex': r'^(M|SM)\.[0-9]{1,2}\.[0-9]{1,4}$'
    },
    'is_boat_rental': {
        'type': 'boolean',
        'required': False,
        'default': False
    },
    'registration_status': {
        'type': 'string',
        'required': False,
        'allowed': ['incomplete', 'complete', 'free', 'paid'],
        'default': 'incomplete'
    },
    'flagged_issues': {
        'type': 'list',
        'required': False,
        'default': [],
        'schema': {
            'type': 'dict',
            'schema': {
                'issue_type': {
                    'type': 'string',
                    'required': True
                },
                'description': {
                    'type': 'string',
                    'required': True
                },
                'flagged_at': {
                    'type': 'string',
                    'required': True
                },
                'flagged_by': {
                    'type': 'string',
                    'required': True
                },
                'resolved': {
                    'type': 'boolean',
                    'required': False,
                    'default': False
                },
                'resolved_at': {
                    'type': 'string',
                    'required': False,
                    'nullable': True
                }
            }
        }
    }
}


# Team Manager Profile Schema
team_manager_schema = {
    'first_name': {
        'type': 'string',
        'required': True,
        'minlength': 1,
        'maxlength': 50
    },
    'last_name': {
        'type': 'string',
        'required': True,
        'minlength': 1,
        'maxlength': 50
    },
    'email': {
        'type': 'string',
        'required': True,
        'regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    },
    'club_affiliation': {
        'type': 'string',
        'required': True,
        'minlength': 1,
        'maxlength': 100
    },
    'mobile_number': {
        'type': 'string',
        'required': True,
        'regex': r'^\+[1-9]\d{1,14}$'  # E.164 format: +country_code followed by digits
    }
}


# Configuration Update Schemas
system_config_schema = {
    'registration_start_date': {
        'type': 'string',
        'required': False,
        'date_format': True
    },
    'registration_end_date': {
        'type': 'string',
        'required': False,
        'date_format': True
    },
    'payment_deadline': {
        'type': 'string',
        'required': False,
        'date_format': True
    },
    'rental_priority_days': {
        'type': 'integer',
        'required': False,
        'min': 0,
        'max': 90
    },
    'competition_date': {
        'type': 'string',
        'required': False,
        'date_format': True
    },
    'temporary_editing_access_hours': {
        'type': 'integer',
        'required': False,
        'min': 1,
        'max': 168  # Max 1 week
    }
}


pricing_config_schema = {
    'base_seat_price': {
        'type': 'number',
        'required': False,
        'min': 0
    },
    'boat_rental_multiplier_skiff': {
        'type': 'number',
        'required': False,
        'min': 0
    },
    'boat_rental_price_crew': {
        'type': 'number',
        'required': False,
        'min': 0
    }
}


notification_config_schema = {
    'notification_frequency_days': {
        'type': 'integer',
        'required': False,
        'min': 1,
        'max': 30
    },
    'session_timeout_minutes': {
        'type': 'integer',
        'required': False,
        'min': 5,
        'max': 120
    },
    'notification_channels': {
        'type': 'list',
        'required': False,
        'schema': {
            'type': 'string',
            'allowed': ['email', 'in_app', 'slack']
        }
    },
    'email_from': {
        'type': 'string',
        'required': False,
        'regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    },
    'slack_webhook_admin': {
        'type': 'string',
        'required': False
    },
    'slack_webhook_devops': {
        'type': 'string',
        'required': False
    }
}


# Validation functions
def validate_crew_member(data):
    """
    Validate crew member data
    
    Args:
        data: Crew member data to validate
        
    Returns:
        tuple: (is_valid, errors)
    """
    v = CustomValidator(crew_member_schema, allow_unknown=True)
    is_valid = v.validate(data)
    return is_valid, v.errors


def validate_boat_registration(data):
    """
    Validate boat registration data
    
    Args:
        data: Boat registration data to validate
        
    Returns:
        tuple: (is_valid, errors)
    """
    v = CustomValidator(boat_registration_schema, allow_unknown=True)
    is_valid = v.validate(data)
    return is_valid, v.errors


def validate_team_manager(data):
    """
    Validate team manager profile data
    
    Args:
        data: Team manager data to validate
        
    Returns:
        tuple: (is_valid, errors)
    """
    v = CustomValidator(team_manager_schema)
    is_valid = v.validate(data)
    return is_valid, v.errors


def validate_config_update(config_type, data):
    """
    Validate configuration update data
    
    Args:
        config_type: Type of configuration (system, pricing, notification)
        data: Configuration data to validate
        
    Returns:
        tuple: (is_valid, errors)
    """
    schemas = {
        'system': system_config_schema,
        'pricing': pricing_config_schema,
        'notification': notification_config_schema
    }
    
    schema = schemas.get(config_type.lower())
    if not schema:
        return False, {'config_type': f'Invalid configuration type: {config_type}'}
    
    v = CustomValidator(schema)
    is_valid = v.validate(data)
    return is_valid, v.errors


def validate_email(email):
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone):
    """
    Validate phone number format (E.164 format required)
    
    Args:
        phone: Phone number to validate
        
    Returns:
        bool: True if valid
    """
    pattern = r'^\+[1-9]\d{1,14}$'  # E.164 format: +country_code followed by digits
    return bool(re.match(pattern, phone))


def sanitize_string(value, max_length=None):
    """
    Sanitize string input (remove dangerous characters)
    
    Args:
        value: String to sanitize
        max_length: Maximum length to truncate to
        
    Returns:
        str: Sanitized string
    """
    if not isinstance(value, str):
        return value
    
    # Remove null bytes and control characters
    sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def sanitize_dict(data, schema=None):
    """
    Sanitize all string values in a dictionary
    
    Args:
        data: Dictionary to sanitize
        schema: Optional schema to determine max lengths
        
    Returns:
        dict: Sanitized dictionary
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            max_length = None
            if schema and key in schema:
                max_length = schema[key].get('maxlength')
            sanitized[key] = sanitize_string(value, max_length)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_dict(item) if isinstance(item, dict) else item for item in value]
        else:
            sanitized[key] = value
    
    return sanitized


def is_rcpm_member(club_affiliation):
    """
    Determine if a crew member is an RCPM member based on club affiliation
    
    According to requirements FR-4.3, a crew member is identified as an RCPM_Member
    when their club_affiliation contains "RCPM" or "Port-Marly" or "Port Marly"
    (case-insensitive matching)
    
    Args:
        club_affiliation: Club affiliation string
        
    Returns:
        bool: True if RCPM member, False otherwise
    """
    if not club_affiliation or not isinstance(club_affiliation, str):
        return False
    
    club_lower = club_affiliation.lower()
    
    # Check for RCPM or Port-Marly variations
    return ('rcpm' in club_lower or 
            'port-marly' in club_lower or 
            'port marly' in club_lower)
