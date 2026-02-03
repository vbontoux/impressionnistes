# Design Document - Course des Impressionnistes Registration System

## Overview

The Course des Impressionnistes Registration System is a serverless web application built on AWS that enables rowing club club managers to register crews and boats for the RCPM Competition. The system provides multilingual support (French/English), secure payment processing via Stripe, and comprehensive administrative tools for validation and management.

## Terminology Mapping: Database/API vs UI

**CRITICAL DESIGN NOTE:** The system uses different terminology in the database/API layer versus the user interface. This is intentional to maintain consistency with existing code while providing clear, user-friendly language.

### Database/API Layer (Backend)
- Uses **"boat"** to refer to crew registrations
- Examples: `boat_id`, `boat_registration`, `create_boat`, `update_boat`, `list_boats`
- Database table fields: `boat_type`, `boat_status`, `assigned_boat_id`
- API endpoints: `/boats`, `/boats/{boat_id}`

### User Interface Layer (Frontend)
- Uses **"Crew"** (English) / **"Équipage"** (French) to refer to crew registrations
- Examples: "Create Crew", "Manage Crews", "Crew Information"
- Translation keys: `boat.createRegistration` → "Create Crew"

### When "Boat" Stays "Boat"
The term "boat" is used in BOTH layers when referring to physical equipment:
- **Boat Type**: Physical boat types (skiff, four, eight)
- **Boat Rental**: Renting physical boats from RCPM
- **Rental Boats**: Physical boat inventory

### Mapping Table

| Context | Database/API | UI (English) | UI (French) |
|---------|--------------|--------------|-------------|
| Team registration | `boat`, `boat_registration` | Crew | Équipage |
| Database ID | `boat_id` | (internal, not shown) | (internal, not shown) |
| Create action | `create_boat_registration()` | "Create Crew" | "Créer un équipage" |
| List view | `list_boats()` | "Crews" | "Équipages" |
| Physical boat type | `boat_type` | "Boat Type" | "Type de bateau" |
| Equipment rental | `boat_rental` | "Boat Rental" | "Location de bateau" |

### Implementation Guidelines

1. **Backend Code**: Continue using "boat" terminology in all Python code, database schemas, and API responses
2. **Frontend Code**: Use "boat" in variable names and API calls, but display "Crew/Équipage" in UI
3. **Translation Files**: Map "boat" keys to "Crew/Équipage" translations
4. **Documentation**: Clearly indicate when "boat" means crew vs. physical equipment

**Example:**
```python
# Backend API (unchanged)
def create_boat_registration(user_id, boat_data):
    boat_id = generate_id()
    boat = {
        "boat_id": boat_id,
        "boat_type": boat_data["boat_type"],
        "status": "incomplete"
    }
    return boat
```

```javascript
// Frontend (variable names use "boat", UI shows "Crew")
async function createCrew(crewData) {
    const response = await api.post('/boats', crewData)  // API uses "boats"
    const boat = response.data  // Variable uses "boat"
    showNotification(t('boat.createSuccess'))  // Translation: "Crew created successfully!"
    return boat
}
```

```json
// Translation file
{
  "boat": {
    "createRegistration": "Create Crew",
    "addNew": "Add Crew",
    "boatType": "Boat Type"  // Physical boat type stays "Boat"
  }
}
```

## Pricing Terminology

**IMPORTANT:** The system uses different terminology for pricing in the database/API versus the user interface to provide clarity to end users.

### Database/API Layer (Backend)
- `base_seat_price`: Internal field name for participation fee
- `rental_price` / `boat_rental_price_crew`: Internal field name for boat rental fee per seat
- `boat_rental_multiplier_skiff`: Multiplier for single-person boats

### User Interface Layer (Frontend)
- **"Participation Fee"** (English) / **"Frais de participation"** (French): What users see for `base_seat_price`
- **"Boat Rental (per seat)"** (English) / **"Location bateau (par place)"** (French): What users see for `rental_price`

### Pricing Components

| Code/Database Field | UI Display (EN) | UI Display (FR) | What It Covers |
|---------------------|-----------------|-----------------|----------------|
| `base_seat_price` | Participation Fee | Frais de participation | Event registration, insurance, organization costs |
| `rental_price` / `boat_rental_price_crew` | Boat Rental (per seat) | Location bateau (par place) | Equipment rental for using RCPM boat seat |
| `boat_rental_multiplier_skiff` | Skiff Rental Multiplier | Multiplicateur location skiff | Multiplier for single-person boats (default: 2.5x) |

### Who Pays What

- **RCPM Members**: €0 for participation, €0 for boat rental (free)
- **External Club Members (own boat)**: Participation Fee only
- **External Club Members (RCPM boat)**: Participation Fee + Boat Rental per seat
- **Mixed Crews**: External members pay both fees, RCPM members pay nothing

### Implementation Guidelines

1. **Backend Code**: Use `base_seat_price` and `rental_price` in all Python code and database schemas
2. **Frontend Code**: Use same variable names internally, but display "Participation Fee" and "Boat Rental" in UI
3. **Translation Files**: Map pricing keys to user-friendly terms
4. **Comments**: Add clarifying comments in pricing calculation functions

**Example:**
```python
# Backend pricing calculation
def calculate_price(members, pricing_config):
    # base_seat_price = Participation Fee (covers registration, insurance, organization)
    base_seat_price = pricing_config['base_seat_price']
    
    # rental_price = Boat Rental fee per seat (equipment rental)
    rental_price = pricing_config.get('boat_rental_price_crew', base_seat_price)
    
    total = 0
    for member in members:
        if not is_rcpm_member(member):
            total += base_seat_price  # Participation Fee
            if using_rcpm_boat:
                total += rental_price  # Boat Rental
    return total
```

```javascript
// Frontend display
<div class="pricing-breakdown">
  <div class="fee-line">
    <span>{{ $t('pricing.participationFee') }}</span>  <!-- "Participation Fee" -->
    <span>{{ formatCurrency(baseSeatPrice) }}</span>
  </div>
  <div class="fee-line">
    <span>{{ $t('pricing.boatRental') }}</span>  <!-- "Boat Rental (per seat)" -->
    <span>{{ formatCurrency(rentalPrice) }}</span>
  </div>
</div>
```

See [Terminology Glossary](../../../docs/reference/terminology.md) for complete pricing definitions and examples.

## Architecture

### High-Level Architecture

The system follows a serverless architecture pattern on AWS with the following key components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CloudFront    │    │   API Gateway    │    │   Lambda        │
│   (Frontend)    │◄──►│   (REST API)     │◄──►│   Functions     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│      S3         │    │   DynamoDB       │    │   Stripe        │
│  (Static Web)   │    │   (Database)     │    │  (Payments)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                       ┌──────────────────┐    ┌─────────────────┐
                       │   CloudWatch     │    │   EventBridge   │
                       │ (Logs/Monitoring)│    │   (Scheduler)   │
                       └──────────────────┘    └─────────────────┘
                                                         │
                                                ┌─────────────────┐
                                                │      SES        │
                                                │ (Email Service) │
                                                └─────────────────┘
                                                         │
                                                ┌─────────────────┐
                                                │     Slack       │
                                                │  (Admin/DevOps  │
                                                │ Notifications)  │
                                                └─────────────────┘
```

### Technology Stack

- **Frontend**: Vue.js 3 with Composition API, served via S3/CloudFront
- **Backend**: Python Lambda functions
- **Database**: Amazon DynamoDB with encryption at rest
- **API**: AWS API Gateway (REST)
- **Authentication**: Amazon Cognito with social login support
- **Payments**: Stripe integration
- **Infrastructure**: AWS CDK (Python)
- **Monitoring**: CloudWatch logs and alarms

## Components and Interfaces

### Frontend Components

#### Core Application Structure
```
src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.vue
│   │   ├── RegisterForm.vue
│   │   └── PasswordReset.vue
│   ├── base/                           # NEW: NFR-7
│   │   ├── BaseButton.vue
│   │   ├── StatusBadge.vue
│   │   ├── BaseModal.vue
│   │   ├── LoadingSpinner.vue
│   │   └── EmptyState.vue
│   ├── composite/                      # NEW: NFR-7
│   │   ├── DataCard.vue
│   │   ├── SortableTable.vue
│   │   ├── FormGroup.vue
│   │   └── MessageAlert.vue
│   ├── crew/
│   │   ├── CrewMemberForm.vue
│   │   ├── CrewMemberList.vue
│   │   └── CrewMemberCard.vue
│   ├── boat/
│   │   ├── BoatRegistrationForm.vue
│   │   ├── BoatList.vue
│   │   ├── SeatAssignment.vue
│   │   └── RaceSelector.vue
│   ├── payment/
│   │   ├── PaymentSummary.vue
│   │   ├── StripeCheckout.vue
│   │   ├── PaymentHistory.vue          # NEW: FR-25
│   │   └── PaymentBalance.vue          # NEW: FR-25
│   ├── admin/
│   │   ├── Dashboard.vue
│   │   ├── ConfigurationPanel.vue
│   │   ├── RegistrationValidation.vue
│   │   ├── ReportsExport.vue
│   │   ├── ImpersonationBanner.vue     # NEW: FR-16
│   │   └── ImpersonationSelector.vue   # NEW: FR-16
│   ├── shared/
│   │   ├── PermissionGuard.vue         # NEW: FR-17
│   │   ├── MobileNav.vue               # NEW: NFR-8
│   │   └── BottomSheet.vue             # NEW: NFR-8
│   └── common/
│       ├── Navigation.vue
│       ├── LanguageSelector.vue
│       └── NotificationCenter.vue
├── views/
│   ├── HomePage.vue
│   ├── DashboardView.vue
│   ├── RegistrationView.vue
│   ├── AdminView.vue
│   └── admin/
│       └── AdminClubManagers.vue       # NEW: FR-15
├── composables/
│   ├── usePermissions.js               # NEW: FR-17
│   └── useTableSort.js                 # NEW: NFR-9
├── stores/
│   ├── auth.js
│   ├── registration.js
│   ├── payment.js
│   └── admin.js
├── services/
│   ├── api.js
│   ├── auth.js
│   └── stripe.js
├── utils/
│   └── exportFormatters.js             # NEW: FR-21
└── assets/
    └── design-tokens.css               # NEW: NFR-7
```

### Backend Lambda Functions

#### Function Organization
```
functions/
├── auth/
│   ├── login.py
│   ├── register.py
│   └── password_reset.py
├── crew/
│   ├── create_crew_member.py
│   ├── update_crew_member.py
│   ├── delete_crew_member.py
│   └── list_crew_members.py
├── boat/
│   ├── create_boat_registration.py
│   ├── update_boat_registration.py
│   ├── delete_boat_registration.py
│   └── list_boat_registrations.py
├── payment/
│   ├── create_payment_intent.py
│   ├── confirm_payment.py
│   ├── webhook_handler.py
│   ├── get_payment_history.py          # NEW: FR-25
│   └── calculate_balance.py            # NEW: FR-25
├── admin/
│   ├── get_dashboard_stats.py
│   ├── update_configuration.py
│   ├── validate_registration.py
│   ├── export_data.py
│   ├── list_club_managers.py           # NEW: FR-15
│   ├── start_impersonation.py          # NEW: FR-16
│   ├── end_impersonation.py            # NEW: FR-16
│   ├── get_impersonation_status.py     # NEW: FR-16
│   ├── grant_temporary_access.py       # NEW: FR-18
│   ├── revoke_temporary_access.py      # NEW: FR-18
│   ├── export_crew_members_json.py     # NEW: FR-21
│   ├── export_boats_json.py            # NEW: FR-21
│   ├── export_races_json.py            # NEW: FR-21
│   ├── export_event_program.py         # NEW: FR-22
│   ├── verify_license.py               # NEW: FR-24
│   ├── invalidate_license.py           # NEW: FR-24
│   └── process_deletion_request.py     # NEW: FR-23
├── user/
│   ├── export_my_data.py               # NEW: FR-23
│   └── request_deletion.py             # NEW: FR-23
├── notifications/
│   ├── send_notification.py
│   ├── schedule_notifications.py
│   ├── process_notification_queue.py
│   └── notification_scheduler.py
└── shared/
    ├── database.py
    ├── auth_utils.py
    ├── validation.py
    ├── notifications.py
    ├── access_control.py               # NEW: FR-17, TC-7
    ├── event_phase.py                  # NEW: FR-17
    └── boat_club_calculator.py         # NEW: FR-19
```

## Data Models

### DynamoDB Table Design

#### Single Table Design Pattern
Using a single DynamoDB table with the following access patterns:

**Table: `impressionnistes-registration`**

| Entity | PK | SK | Attributes |
|--------|----|----|------------|
| Club Manager | `USER#{user_id}` | `PROFILE` | first_name, last_name, email, club_affiliation, mobile_number, created_at |
| Crew Member | `USER#{user_id}` | `CREW#{crew_id}` | first_name, last_name, date_of_birth, gender, license_number, club_affiliation, is_rcpm_member, assigned_boat_id, flagged_issues |
| Boat Registration | `USER#{user_id}` | `BOAT#{boat_id}` | event_type, boat_type, race_id, seats, crew_assignments, status, created_at, updated_at |
| Payment | `USER#{user_id}` | `PAYMENT#{payment_id}` | stripe_payment_intent_id, amount, status, boat_registrations, created_at |
| Configuration | `CONFIG` | `SYSTEM` | registration_start, registration_end, payment_deadline, base_seat_price, rental_priority_days |
| Configuration | `CONFIG` | `NOTIFICATION` | notification_frequency, session_timeout, notification_channels |
| Configuration | `CONFIG` | `PRICING` | base_seat_price, boat_rental_multiplier_skiff, boat_rental_price_crew |
| Race Definition | `RACE` | `#{race_id}` | name, event_type, boat_type, age_category, gender_category, distance |

#### GSI Indexes

**GSI1: Registration Status Index**
- PK: `status` (e.g., "INCOMPLETE", "COMPLETE", "PAID")
- SK: `created_at`
- Purpose: Admin queries for registration validation

**GSI2: Race Lookup Index**
- PK: `event_type#{boat_type}`
- SK: `age_category#{gender_category}`
- Purpose: Race filtering and selection

**GSI3: License Number Uniqueness Index**
- PK: `license_number`
- SK: `USER#{user_id}#CREW#{crew_id}`
- Purpose: Enforce license number uniqueness across all crew members in the competition
- Note: This index enables efficient duplicate detection when adding new crew members

**GSI4: License Verification Index** *(NEW: FR-24)*
- PK: `license_verification_status`
- SK: `USER#{user_id}#CREW#{crew_id}`
- Purpose: Query crew members by verification status

**GSI5: Access Grant Index** *(NEW: FR-18)*
- PK: `status`
- SK: `expires_at`
- Purpose: Query active/expired access grants

#### New Entity Types

**Impersonation Session** *(NEW: FR-16)*
```python
{
    "PK": "ADMIN#{admin_id}",
    "SK": "IMPERSONATION#{timestamp}",
    "impersonated_user_id": "string",
    "started_at": "timestamp",
    "ended_at": "timestamp"  # optional
}
```

**Temporary Access Grant** *(NEW: FR-18)*
```python
{
    "PK": "USER#{user_id}",
    "SK": "ACCESS_GRANT#{grant_id}",
    "granted_by": "admin_id",
    "granted_at": "timestamp",
    "expires_at": "timestamp",
    "status": "active|expired|revoked"
}
```

**License Verification** *(NEW: FR-24)*
```python
# Added to existing crew member entity
{
    "PK": "USER#{user_id}",
    "SK": "CREW#{crew_id}",
    # ... existing fields ...
    "license_verification_status": "pending|verified|invalid",
    "verified_at": "timestamp",  # optional
    "verified_by": "admin_id"    # optional
}
```

**Payment History** *(NEW: FR-25)*
```python
{
    "PK": "USER#{user_id}",
    "SK": "PAYMENT#{payment_id}",
    "amount": "decimal",
    "payment_method": "string",
    "stripe_payment_intent_id": "string",
    "boat_ids": ["list"],
    "created_at": "timestamp",
    "status": "succeeded|failed|refunded"
}
```

**Boat Club Display** *(NEW: FR-19)*
```python
# Added to existing boat registration entity
{
    "PK": "USER#{user_id}",
    "SK": "BOAT#{boat_id}",
    # ... existing fields ...
    "boat_club_display": "string",
    "club_list": ["list"]
}
```

**Hull Assignment** *(NEW: FR-20, FR-26)*
```python
# Added to existing boat registration entity
{
    "PK": "USER#{user_id}",
    "SK": "BOAT#{boat_id}",
    # ... existing fields ...
    "hull_assignment": "string",  # optional
    "hull_requested": "boolean",
    "hull_request_status": "pending|approved|rejected"
}
```

### Configuration Management

#### Storage Strategy
Configuration parameters are stored in **DynamoDB only** for simplicity and efficiency. DevOps users can access DynamoDB directly when needed for emergency operations.

#### DynamoDB Configuration Schema
```python
# System configuration in DynamoDB
system_config = {
    "PK": "CONFIG",
    "SK": "SYSTEM",
    "registration_start_date": "2024-03-19",
    "registration_end_date": "2024-04-19", 
    "payment_deadline": "2024-04-25",
    "rental_priority_days": 15,
    "competition_date": "2024-05-01",
    "updated_at": "2024-03-15T10:30:00Z",
    "updated_by": "admin_user_id"
}

pricing_config = {
    "PK": "CONFIG",
    "SK": "PRICING", 
    "base_seat_price": 20.00,
    "boat_rental_multiplier_skiff": 2.5,
    "boat_rental_price_crew": 20.00,  # Same as base_seat_price
    "currency": "EUR",
    "updated_at": "2024-03-15T10:30:00Z"
}

notification_config = {
    "PK": "CONFIG",
    "SK": "NOTIFICATION",
    "notification_frequency_days": 7,
    "session_timeout_minutes": 30,
    "notification_channels": ["email", "in_app", "slack"],
    "email_from": "impressionnistes@rcpm-aviron.fr",
    "slack_webhook_admin": "",
    "slack_webhook_devops": "",
    "updated_at": "2024-03-15T10:30:00Z"
}

# NEW: FR-17, FR-18, TC-7
access_control_config = {
    "PK": "CONFIG",
    "SK": "ACCESS_CONTROL",
    "temporary_access_duration_hours": 48,
    "permission_cache_ttl_seconds": 60,
    "event_phase_cache_ttl_seconds": 60,
    "updated_at": "2024-03-15T10:30:00Z",
    "updated_by": "admin_user_id"
}

# NEW: FR-23
gdpr_config = {
    "PK": "CONFIG",
    "SK": "GDPR",
    "deleted_data_retention_years": 5,
    "consent_required": True,
    "updated_at": "2024-03-15T10:30:00Z"
}
```

#### Default Configuration Initialization
```python
# Default configuration values loaded at deployment
DEFAULT_SYSTEM_CONFIG = {
    "PK": "CONFIG",
    "SK": "SYSTEM",
    "registration_start_date": "2024-03-19",
    "registration_end_date": "2024-04-19", 
    "payment_deadline": "2024-04-25",
    "rental_priority_days": 15,
    "competition_date": "2024-05-01",
    "temporary_editing_access_hours": 48,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}

DEFAULT_PRICING_CONFIG = {
    "PK": "CONFIG",
    "SK": "PRICING", 
    "base_seat_price": 20.00,
    "boat_rental_multiplier_skiff": 2.5,
    "boat_rental_price_crew": 20.00,
    "currency": "EUR",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}

DEFAULT_NOTIFICATION_CONFIG = {
    "PK": "CONFIG",
    "SK": "NOTIFICATION",
    "notification_frequency_days": 7,
    "session_timeout_minutes": 30,
    "notification_channels": ["email", "in_app", "slack"],
    "email_from": "impressionnistes@rcpm-aviron.fr",
    "slack_webhook_admin": "",  # To be configured by admin
    "slack_webhook_devops": "",  # To be configured by admin
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Configuration Access Layer
```python
# shared/configuration.py
import boto3
from functools import lru_cache
from datetime import datetime, timedelta

class ConfigurationManager:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('impressionnistes-registration')
        self._cache = {}
        self._cache_ttl = timedelta(minutes=5)  # Cache for 5 minutes
    
    @lru_cache(maxsize=10)
    def get_system_config(self):
        """Get system configuration from DynamoDB with caching"""
        try:
            response = self.table.get_item(
                Key={'PK': 'CONFIG', 'SK': 'SYSTEM'}
            )
            config = response.get('Item')
            if not config:
                # Initialize with defaults if not found
                config = self._initialize_default_config('SYSTEM')
            return config
        except Exception as e:
            logger.error(f"Failed to get system config: {str(e)}")
            # Return defaults as fallback
            return DEFAULT_SYSTEM_CONFIG.copy()
    
    def get_pricing_config(self):
        """Get pricing configuration"""
        try:
            response = self.table.get_item(
                Key={'PK': 'CONFIG', 'SK': 'PRICING'}
            )
            config = response.get('Item')
            if not config:
                config = self._initialize_default_config('PRICING')
            return config
        except Exception as e:
            logger.error(f"Failed to get pricing config: {str(e)}")
            return DEFAULT_PRICING_CONFIG.copy()
    
    def get_notification_config(self):
        """Get notification configuration"""
        try:
            response = self.table.get_item(
                Key={'PK': 'CONFIG', 'SK': 'NOTIFICATION'}
            )
            config = response.get('Item')
            if not config:
                config = self._initialize_default_config('NOTIFICATION')
            return config
        except Exception as e:
            logger.error(f"Failed to get notification config: {str(e)}")
            return DEFAULT_NOTIFICATION_CONFIG.copy()
    
    def _initialize_default_config(self, config_type):
        """Initialize default configuration if not exists"""
        defaults = {
            'SYSTEM': DEFAULT_SYSTEM_CONFIG,
            'PRICING': DEFAULT_PRICING_CONFIG,
            'NOTIFICATION': DEFAULT_NOTIFICATION_CONFIG
        }
        
        default_config = defaults[config_type].copy()
        
        try:
            # Insert default configuration
            self.table.put_item(
                Item=default_config,
                ConditionExpression='attribute_not_exists(PK)'
            )
            logger.info(f"Initialized default {config_type} configuration")
        except ClientError as e:
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                logger.error(f"Failed to initialize {config_type} config: {str(e)}")
        
        return default_config
    
    def update_config(self, config_type, updates, admin_user_id):
        """Update configuration with audit trail"""
        current_time = datetime.utcnow().isoformat() + 'Z'
        
        # Build update expression dynamically
        update_expression_parts = ['#updated_at = :time', '#updated_by = :user']
        expression_attribute_names = {
            '#updated_at': 'updated_at',
            '#updated_by': 'updated_by'
        }
        expression_attribute_values = {
            ':time': current_time,
            ':user': admin_user_id
        }
        
        # Add updates to expression
        for key, value in updates.items():
            attr_name = f'#{key}'
            attr_value = f':{key}'
            update_expression_parts.append(f'{attr_name} = {attr_value}')
            expression_attribute_names[attr_name] = key
            expression_attribute_values[attr_value] = value
        
        # Update DynamoDB
        self.table.update_item(
            Key={'PK': 'CONFIG', 'SK': config_type.upper()},
            UpdateExpression='SET ' + ', '.join(update_expression_parts),
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
        
        # Clear cache to force refresh
        self.get_system_config.cache_clear()
        logger.info(f"Updated {config_type} configuration: {list(updates.keys())}")

# Global configuration instance
config_manager = ConfigurationManager()

def get_base_seat_price():
    """Helper function to get current base seat price"""
    pricing_config = config_manager.get_pricing_config()
    return float(pricing_config.get('base_seat_price', 20.00))

def get_registration_period():
    """Helper function to get registration period dates"""
    system_config = config_manager.get_system_config()
    return {
        'start': system_config.get('registration_start_date'),
        'end': system_config.get('registration_end_date'),
        'payment_deadline': system_config.get('payment_deadline')
    }

def is_registration_active():
    """Check if registration period is currently active"""
    period = get_registration_period()
    today = datetime.now().date()
    start_date = datetime.fromisoformat(period['start']).date()
    end_date = datetime.fromisoformat(period['end']).date()
    
    return start_date <= today <= end_date
```

#### Admin Configuration Interface
```python
# admin/update_configuration.py
from shared.configuration import config_manager
from shared.auth_utils import require_admin
from shared.validation import validate_config_update

@require_admin
def lambda_handler(event, context):
    """Admin endpoint to update system configuration"""
    try:
        body = json.loads(event['body'])
        config_type = body.get('config_type')  # 'system', 'pricing', 'notification'
        updates = body.get('updates', {})
        admin_user_id = get_current_user_id(event)
        
        # Validate configuration updates
        validation_errors = validate_config_update(config_type, updates)
        if validation_errors:
            return error_response(400, "VALIDATION_ERROR", "Invalid configuration", validation_errors)
        
        # Apply updates
        config_manager.update_config(config_type, updates, admin_user_id)
        
        # Log configuration change
        log_admin_action(admin_user_id, 'CONFIG_UPDATE', {
            'config_type': config_type,
            'changes': updates
        })
        
        return success_response({
            'message': 'Configuration updated successfully',
            'config_type': config_type,
            'updated_fields': list(updates.keys())
        })
        
    except Exception as e:
        logger.error(f"Configuration update failed: {str(e)}", exc_info=True)
        return error_response(500, "CONFIG_UPDATE_ERROR", "Failed to update configuration")
```

#### DevOps DynamoDB Access
```python
# DevOps utility script for emergency configuration access
import boto3
import json
from datetime import datetime

def get_all_configuration(table_name='impressionnistes-registration'):
    """Get all configuration for DevOps review"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    # Get all configuration items
    response = table.query(
        KeyConditionExpression=Key('PK').eq('CONFIG')
    )
    
    configs = {}
    for item in response['Items']:
        config_type = item['SK'].lower()
        configs[config_type] = {k: v for k, v in item.items() if k not in ['PK', 'SK']}
    
    return configs

def emergency_update_config(table_name, config_type, key, value, devops_user):
    """Emergency configuration update by DevOps"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    current_time = datetime.utcnow().isoformat() + 'Z'
    
    try:
        table.update_item(
            Key={'PK': 'CONFIG', 'SK': config_type.upper()},
            UpdateExpression='SET #key = :value, #updated_at = :time, #updated_by = :user',
            ExpressionAttributeNames={
                '#key': key,
                '#updated_at': 'updated_at',
                '#updated_by': 'updated_by'
            },
            ExpressionAttributeValues={
                ':value': value,
                ':time': current_time,
                ':user': f'devops:{devops_user}'
            }
        )
        
        print(f"Emergency update successful: {config_type}.{key} = {value}")
        
        # Log the emergency change
        table.put_item(
            Item={
                'PK': 'AUDIT',
                'SK': f'EMERGENCY#{current_time}',
                'action': 'EMERGENCY_CONFIG_UPDATE',
                'config_type': config_type,
                'key': key,
                'value': value,
                'devops_user': devops_user,
                'timestamp': current_time
            }
        )
        
    except Exception as e:
        print(f"Emergency update failed: {str(e)}")

# Example usage:
# python devops_config.py --get-all
# python devops_config.py --update system registration_end_date 2024-04-20 --user john.doe
```

#### Infrastructure Initialization
```python
# CDK deployment initialization
class DatabaseStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # ... table creation code ...
        
        # Lambda function to initialize default configuration
        init_config_function = lambda_.Function(
            self, "InitConfigFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="init_config.lambda_handler",
            code=lambda_.Code.from_asset("functions/init"),
            environment={
                'TABLE_NAME': self.table.table_name
            }
        )
        
        # Grant permissions
        self.table.grant_write_data(init_config_function)
        
        # Custom resource to run initialization
        init_config_provider = cr.Provider(
            self, "InitConfigProvider",
            on_event_handler=init_config_function
        )
        
        CustomResource(
            self, "InitConfigResource",
            service_token=init_config_provider.service_token
        )

# functions/init/init_config.py
def lambda_handler(event, context):
    """Initialize default configuration on deployment"""
    if event['RequestType'] == 'Create':
        config_manager = ConfigurationManager()
        
        # Initialize all default configurations
        config_manager._initialize_default_config('SYSTEM')
        config_manager._initialize_default_config('PRICING') 
        config_manager._initialize_default_config('NOTIFICATION')
        
        return {'Status': 'SUCCESS', 'Data': {'Message': 'Configuration initialized'}}
    
    return {'Status': 'SUCCESS'}
```

### Data Validation Rules

#### Crew Member Validation
```python
crew_member_schema = {
    "first_name": {"type": "string", "required": True, "maxlength": 50},
    "last_name": {"type": "string", "required": True, "maxlength": 50},
    "date_of_birth": {"type": "date", "required": True},
    "gender": {"type": "string", "allowed": ["M", "F"], "required": True},
    "license_number": {"type": "string", "regex": "^[A-Z0-9]{6,12}$", "required": True},
    "club_affiliation": {"type": "string", "required": False, "maxlength": 100},  # Optional, defaults to club manager's club
    "is_rcpm_member": {"type": "boolean", "required": False, "default": False}  # Calculated based on club_affiliation
}
```

#### Boat Registration Validation
```python
boat_registration_schema = {
    "event_type": {"type": "string", "allowed": ["21km", "42km"], "required": True},
    "boat_type": {"type": "string", "allowed": ["skiff", "4-", "4+", "8+"], "required": True},
    "race_id": {"type": "string", "required": True},
    "seats": {"type": "list", "schema": seat_schema, "required": True},
    "is_multi_club_crew": {"type": "boolean", "default": False},  # Calculated based on crew members
    "is_boat_rental": {"type": "boolean", "default": False}
}

seat_schema = {
    "position": {"type": "integer", "min": 1, "max": 9},
    "type": {"type": "string", "allowed": ["rower", "cox"]},
    "crew_member_id": {"type": "string", "nullable": True},
    "can_substitute_cox": {"type": "boolean", "default": False}  # FR-3.11: Can this crew member substitute as cox
}
```

#### Multi_Club_Crew Detection Logic
```python
def detect_multi_club_crew(boat_registration, crew_members, club_manager):
    """
    Determine if a boat registration is a Multi_Club_Crew
    
    A Multi_Club_Crew is identified when:
    - The boat contains crew members from different clubs
    - At least one crew member has a different club_affiliation than the club manager
    """
    club_manager_club = club_manager['club_affiliation']
    
    # Get all crew members assigned to this boat
    assigned_crew_ids = [
        seat['crew_member_id'] 
        for seat in boat_registration['seats'] 
        if seat.get('crew_member_id')
    ]
    
    assigned_crew = [
        crew for crew in crew_members 
        if crew['crew_id'] in assigned_crew_ids
    ]
    
    # Check if any crew member is from a different club
    has_external_members = any(
        crew.get('club_affiliation', club_manager_club) != club_manager_club
        for crew in assigned_crew
    )
    
    return has_external_members

def calculate_boat_registration_price(boat_registration, crew_members, club_manager, pricing_config):
    """
    Calculate the total price for a boat registration
    
    Pricing rules:
    - RCPM members: 0 euros per seat
    - External club members: Participation Fee (base_seat_price) per seat
    - Boat rental (if applicable): 2.5x Participation Fee for skiffs, Boat Rental fee (rental_price) per seat for crew boats
    
    Note: base_seat_price = Participation Fee (registration, insurance, organization)
          rental_price = Boat Rental fee (equipment rental per seat)
    """
    # base_seat_price = Participation Fee per member
    base_seat_price = pricing_config['base_seat_price']
    club_manager_club = club_manager['club_affiliation']
    is_rcpm = club_manager_club == 'RCPM'
    
    total_price = 0.0
    seat_breakdown = []
    
    # Get all assigned crew members
    assigned_crew_ids = [
        seat['crew_member_id'] 
        for seat in boat_registration['seats'] 
        if seat.get('crew_member_id')
    ]
    
    assigned_crew = [
        crew for crew in crew_members 
        if crew['crew_id'] in assigned_crew_ids
    ]
    
    # Calculate price per seat
    for crew in assigned_crew:
        crew_club = crew.get('club_affiliation', club_manager_club)
        is_crew_rcpm = crew_club == 'RCPM'
        
        if is_crew_rcpm:
            seat_price = 0.0
            seat_breakdown.append({
                'crew_member': f"{crew['first_name']} {crew['last_name']}",
                'club': crew_club,
                'price': 0.0,
                'reason': 'RCPM member'
            })
        else:
            seat_price = base_seat_price
            seat_breakdown.append({
                'crew_member': f"{crew['first_name']} {crew['last_name']}",
                'club': crew_club,
                'price': base_seat_price,  # Participation Fee
                'reason': 'External club member'
            })
        
        total_price += seat_price
    
    # Add boat rental fee if applicable
    if boat_registration.get('is_boat_rental', False):
        if boat_registration['boat_type'] == 'skiff':
            # Skiff rental = 2.5x Participation Fee
            rental_fee = base_seat_price * pricing_config['boat_rental_multiplier_skiff']
            seat_breakdown.append({
                'item': 'Boat rental (skiff)',
                'price': rental_fee,
                'reason': f"{pricing_config['boat_rental_multiplier_skiff']}x Participation Fee"
            })
        else:
            # Crew boat rental: Boat Rental fee per seat
            num_seats = len(boat_registration['seats'])
            rental_fee = base_seat_price * num_seats  # Using base_seat_price as default rental_price
            seat_breakdown.append({
                'item': f'Boat rental ({num_seats} seats)',
                'price': rental_fee,
                'reason': f"{num_seats} seats × Boat Rental fee"
            })
        
        total_price += rental_fee
    
    return {
        'total_price': total_price,
        'breakdown': seat_breakdown,
        'is_multi_club_crew': detect_multi_club_crew(boat_registration, crew_members, club_manager)
    }
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: License Number Uniqueness

*For any* crew member registration attempt, if a license number already exists in the competition database, the system should reject the registration and return an error indicating the license number is already in use.

**Validates: Requirements FR-2.4, FR-2.5**

**Implementation Details:**
- Before creating a new crew member, query DynamoDB to check if the license number exists
- Use a Global Secondary Index (GSI) on license_number for efficient lookups
- Return a 409 Conflict error with a clear message when a duplicate is detected
- The uniqueness check must be performed atomically to prevent race conditions

**Testing Approach:**
- Generate random crew members with random license numbers
- Attempt to add a second crew member with the same license number
- Verify the system rejects the duplicate and returns the appropriate error
- Test across different club managers to ensure uniqueness is competition-wide, not per-manager

## Error Handling

### Error Response Format
```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid crew member data",
        "details": {
            "license_number": "Must be alphanumeric and 6-12 characters"
        },
        "timestamp": "2024-03-19T10:30:00Z"
    }
}
```

### Error Categories

#### Client Errors (4xx)
- **400 Bad Request**: Invalid input data, validation failures
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Insufficient permissions for operation
- **404 Not Found**: Resource does not exist
- **409 Conflict**: Resource already exists or constraint violation

#### Server Errors (5xx)
- **500 Internal Server Error**: Unexpected server error
- **502 Bad Gateway**: External service (Stripe) unavailable
- **503 Service Unavailable**: System maintenance or overload

### Error Handling Strategy

#### Frontend Error Handling
```javascript
// Global error handler
app.config.errorHandler = (error, instance, info) => {
    if (error.response?.status === 401) {
        // Redirect to login
        router.push('/login');
    } else if (error.response?.status >= 500) {
        // Show system error message
        showNotification('System temporarily unavailable', 'error');
    } else {
        // Show specific error message
        showNotification(error.response?.data?.error?.message, 'error');
    }
};
```

#### Backend Error Handling
```python
def lambda_handler(event, context):
    try:
        # Business logic
        result = process_request(event)
        return success_response(result)
    except ValidationError as e:
        return error_response(400, "VALIDATION_ERROR", str(e), e.details)
    except AuthenticationError as e:
        return error_response(401, "AUTH_ERROR", str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return error_response(500, "INTERNAL_ERROR", "An unexpected error occurred")
```

## Notification System

### Architecture Overview

The notification system handles automated email notifications for registration events, payment reminders, and issue alerts using AWS EventBridge for scheduling and SES for email delivery.

#### Notification Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   EventBridge   │    │   Lambda         │    │      SES        │
│   (Scheduler)   │───►│   (Processor)    │───►│ (Email Service) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         │              ┌──────────────────┐
         └─────────────►│   DynamoDB       │
                        │ (Notification    │
                        │  Tracking)       │
                        └──────────────────┘
```

### Notification Types

#### Immediate Notifications
- Registration confirmation emails
- Payment confirmation emails
- Issue flagging alerts
- Boat rental confirmations

#### Scheduled Notifications
- Payment deadline reminders (configurable frequency)
- Registration deadline warnings
- Recurring issue notifications (weekly default)
- System maintenance alerts

### Implementation Details

#### EventBridge Scheduler
```python
# notification_scheduler.py
import boto3
from datetime import datetime, timedelta

def schedule_payment_reminders():
    """Schedule payment reminder notifications"""
    eventbridge = boto3.client('events')
    
    # Get users with unpaid registrations
    unpaid_users = get_unpaid_registrations()
    
    for user in unpaid_users:
        # Schedule reminder based on notification frequency
        schedule_time = datetime.now() + timedelta(days=get_notification_frequency())
        
        eventbridge.put_events(
            Entries=[
                {
                    'Source': 'impressionnistes.notifications',
                    'DetailType': 'Payment Reminder',
                    'Detail': json.dumps({
                        'user_id': user['user_id'],
                        'type': 'payment_reminder',
                        'registration_ids': user['unpaid_registrations']
                    }),
                    'Time': schedule_time
                }
            ]
        )

def schedule_recurring_issue_notifications():
    """Schedule weekly notifications for unresolved issues"""
    flagged_registrations = get_flagged_registrations()
    
    for registration in flagged_registrations:
        if not registration.get('resolved', False):
            # Schedule weekly reminder
            schedule_notification(
                user_id=registration['user_id'],
                type='issue_reminder',
                data=registration,
                delay_days=7
            )
```

#### Notification Processor
```python
# process_notification_queue.py
import boto3
import json
from email_templates import get_template

def lambda_handler(event, context):
    """Process EventBridge notification events"""
    
    for record in event.get('Records', []):
        detail = json.loads(record['body'])
        notification_type = detail['type']
        user_id = detail['user_id']
        
        # Get user details
        user = get_user_by_id(user_id)
        
        # Process based on notification type
        if notification_type == 'payment_reminder':
            send_payment_reminder(user, detail['registration_ids'])
        elif notification_type == 'issue_reminder':
            send_issue_reminder(user, detail['issues'])
        elif notification_type == 'deadline_warning':
            send_deadline_warning(user, detail['deadline_type'])
        
        # Track notification sent
        track_notification_sent(user_id, notification_type)

def send_payment_reminder(user, registration_ids):
    """Send payment reminder email"""
    registrations = get_registrations_by_ids(registration_ids)
    total_amount = calculate_total_amount(registrations)
    
    template_data = {
        'user_name': f"{user['first_name']} {user['last_name']}",
        'registrations': registrations,
        'total_amount': total_amount,
        'payment_deadline': get_payment_deadline(),
        'language': user.get('language', 'fr')
    }
    
    send_email(
        to_email=user['email'],
        template='payment_reminder',
        data=template_data,
        language=user.get('language', 'fr')
    )
```

#### Email Service Integration
```python
# send_notification.py
import boto3
from jinja2 import Environment, FileSystemLoader

def send_email(to_email, template, data, language='fr'):
    """Send email using SES with multilingual templates"""
    ses = boto3.client('ses')
    
    # Load template based on language
    template_env = Environment(loader=FileSystemLoader('templates'))
    email_template = template_env.get_template(f'{template}_{language}.html')
    
    # Render email content
    html_content = email_template.render(**data)
    subject = get_email_subject(template, language, data)
    
    # Send email via SES
    response = ses.send_email(
        Source='noreply@impressionnistes.rcpm.fr',
        Destination={'ToAddresses': [to_email]},
        Message={
            'Subject': {'Data': subject, 'Charset': 'UTF-8'},
            'Body': {
                'Html': {'Data': html_content, 'Charset': 'UTF-8'}
            }
        }
    )
    
    return response['MessageId']

def get_email_subject(template, language, data):
    """Get localized email subject"""
    subjects = {
        'payment_reminder': {
            'fr': f"Rappel de paiement - Course des Impressionnistes",
            'en': f"Payment Reminder - Course des Impressionnistes"
        },
        'issue_reminder': {
            'fr': f"Action requise - Inscription Course des Impressionnistes",
            'en': f"Action Required - Course des Impressionnistes Registration"
        },
        'deadline_warning': {
            'fr': f"Date limite approche - Course des Impressionnistes",
            'en': f"Deadline Approaching - Course des Impressionnistes"
        }
    }
    
    return subjects.get(template, {}).get(language, 'Course des Impressionnistes')
```

### Email Templates

#### Multilingual Template Structure
```
templates/
├── payment_reminder_fr.html
├── payment_reminder_en.html
├── issue_reminder_fr.html
├── issue_reminder_en.html
├── deadline_warning_fr.html
├── deadline_warning_en.html
├── registration_confirmation_fr.html
├── registration_confirmation_en.html
└── base_template.html
```

#### Example Template (payment_reminder_fr.html)
```html
{% extends "base_template.html" %}

{% block content %}
<h2>Rappel de paiement - Course des Impressionnistes</h2>

<p>Bonjour {{ user_name }},</p>

<p>Nous vous rappelons que le paiement pour vos inscriptions à la Course des Impressionnistes est en attente.</p>

<h3>Détails de vos inscriptions :</h3>
<ul>
{% for registration in registrations %}
    <li>{{ registration.boat_type }} - {{ registration.race_name }} : {{ registration.amount }}€</li>
{% endfor %}
</ul>

<p><strong>Montant total : {{ total_amount }}€</strong></p>
<p><strong>Date limite de paiement : {{ payment_deadline }}</strong></p>

<p>
    <a href="{{ payment_url }}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
        Procéder au paiement
    </a>
</p>

<p>Cordialement,<br>L'équipe RCPM</p>
{% endblock %}
```

### Notification Tracking

#### DynamoDB Schema for Notifications
```python
# Notification tracking table structure
notification_record = {
    "PK": "USER#{user_id}",
    "SK": "NOTIFICATION#{timestamp}#{type}",
    "notification_type": "payment_reminder",
    "sent_at": "2024-03-19T10:30:00Z",
    "status": "sent",  # sent, failed, bounced
    "template_used": "payment_reminder_fr",
    "recipient_email": "user@example.com",
    "message_id": "ses_message_id",
    "retry_count": 0
}
```

#### Notification Frequency Management
```python
def get_notification_frequency():
    """Get notification frequency from configuration"""
    config = get_system_configuration()
    return config.get('notification_frequency_days', 7)  # Default weekly

def should_send_notification(user_id, notification_type):
    """Check if notification should be sent based on frequency"""
    last_notification = get_last_notification(user_id, notification_type)
    
    if not last_notification:
        return True
    
    frequency_days = get_notification_frequency()
    time_since_last = datetime.now() - last_notification['sent_at']
    
    return time_since_last.days >= frequency_days
```

### EventBridge Rules Configuration

#### CDK Infrastructure for Notifications
```python
# In monitoring_stack.py
from aws_cdk import (
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda as lambda_,
    aws_ses as ses
)

class NotificationStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # SES Configuration
        self.ses_identity = ses.EmailIdentity(
            self, "SESIdentity",
            identity=ses.Identity.domain("rcpm.fr")
        )
        
        # Notification processor Lambda
        self.notification_processor = lambda_.Function(
            self, "NotificationProcessor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="process_notification_queue.lambda_handler",
            code=lambda_.Code.from_asset("functions/notifications")
        )
        
        # Daily notification scheduler
        daily_rule = events.Rule(
            self, "DailyNotificationRule",
            schedule=events.Schedule.cron(hour="9", minute="0")  # 9 AM daily
        )
        
        daily_rule.add_target(
            targets.LambdaFunction(
                self.notification_processor,
                event=events.RuleTargetInput.from_object({
                    "type": "daily_check",
                    "source": "scheduler"
                })
            )
        )
        
        # Payment deadline reminders
        payment_reminder_rule = events.Rule(
            self, "PaymentReminderRule",
            schedule=events.Schedule.cron(hour="10", minute="0")  # 10 AM daily
        )
        
        payment_reminder_rule.add_target(
            targets.LambdaFunction(self.notification_processor)
        )
```

## Testing Strategy

### Unit Testing

#### Frontend Testing (Vitest + Vue Test Utils)
```javascript
// Example: CrewMemberForm.test.js
describe('CrewMemberForm', () => {
    test('validates required fields', async () => {
        const wrapper = mount(CrewMemberForm);
        await wrapper.find('form').trigger('submit');
        
        expect(wrapper.find('.error-message').text())
            .toContain('First name is required');
    });
    
    test('validates license number format', async () => {
        const wrapper = mount(CrewMemberForm);
        await wrapper.find('input[name="license"]').setValue('invalid');
        await wrapper.find('form').trigger('submit');
        
        expect(wrapper.find('.error-message').text())
            .toContain('Invalid license number format');
    });
});
```

#### Backend Testing (pytest)
```python
# Example: test_crew_member.py
def test_create_crew_member_success():
    event = {
        'body': json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'license_number': 'ABC123'
        })
    }
    
    response = create_crew_member.lambda_handler(event, {})
    
    assert response['statusCode'] == 201
    assert 'crew_id' in json.loads(response['body'])

def test_create_crew_member_validation_error():
    event = {'body': json.dumps({'first_name': 'John'})}  # Missing required fields
    
    response = create_crew_member.lambda_handler(event, {})
    
    assert response['statusCode'] == 400
    assert 'VALIDATION_ERROR' in response['body']
```

### Integration Testing

#### API Integration Tests
```python
# Example: test_registration_flow.py
def test_complete_registration_flow():
    # 1. Create club manager
    manager = create_club_manager()
    
    # 2. Create crew members
    crew_members = [create_crew_member(manager.id) for _ in range(4)]
    
    # 3. Create boat registration
    boat = create_boat_registration(manager.id, crew_members)
    
    # 4. Process payment
    payment = process_payment(manager.id, [boat.id])
    
    # 5. Verify complete registration
    assert boat.status == 'PAID'
    assert payment.status == 'succeeded'
```

### End-to-End Testing

#### Cypress E2E Tests
```javascript
// Example: registration-flow.cy.js
describe('Registration Flow', () => {
    it('completes full registration process', () => {
        // Login
        cy.visit('/login');
        cy.get('[data-cy=email]').type('manager@club.com');
        cy.get('[data-cy=password]').type('password');
        cy.get('[data-cy=login-btn]').click();
        
        // Create crew member
        cy.get('[data-cy=add-crew-member]').click();
        cy.get('[data-cy=first-name]').type('John');
        cy.get('[data-cy=last-name]').type('Doe');
        // ... fill form
        cy.get('[data-cy=save-crew-member]').click();
        
        // Create boat registration
        cy.get('[data-cy=add-boat]').click();
        cy.get('[data-cy=event-21km]').click();
        cy.get('[data-cy=boat-type-4plus]').click();
        // ... assign crew members
        cy.get('[data-cy=save-boat]').click();
        
        // Process payment
        cy.get('[data-cy=proceed-payment]').click();
        // ... Stripe checkout flow
        
        // Verify success
        cy.get('[data-cy=registration-status]').should('contain', 'Paid');
    });
});
```

## Security Considerations

### Authentication & Authorization

#### JWT Token Management
```javascript
// Token refresh strategy
const refreshToken = async () => {
    try {
        const response = await api.post('/auth/refresh');
        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);
        return access_token;
    } catch (error) {
        // Redirect to login if refresh fails
        router.push('/login');
        throw error;
    }
};
```

#### Role-Based Access Control
```python
def require_admin(func):
    def wrapper(event, context):
        user = get_current_user(event)
        if not user or user.role != 'admin':
            return error_response(403, "FORBIDDEN", "Admin access required")
        return func(event, context)
    return wrapper

@require_admin
def update_configuration(event, context):
    # Admin-only function
    pass
```

### Data Protection

#### Input Sanitization
```python
import bleach
from cerberus import Validator

def sanitize_input(data):
    """Sanitize user input to prevent XSS and injection attacks"""
    if isinstance(data, str):
        return bleach.clean(data.strip())
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data

def validate_and_sanitize(data, schema):
    """Validate and sanitize input data"""
    sanitized_data = sanitize_input(data)
    validator = Validator(schema)
    
    if not validator.validate(sanitized_data):
        raise ValidationError("Invalid input", validator.errors)
    
    return validator.normalized(sanitized_data)
```

#### GDPR Compliance
```python
def handle_data_deletion_request(user_id):
    """Handle GDPR data deletion request"""
    # 1. Anonymize personal data
    anonymize_user_data(user_id)
    
    # 2. Remove from active systems
    deactivate_user_account(user_id)
    
    # 3. Schedule backup cleanup
    schedule_backup_cleanup(user_id)
    
    # 4. Log compliance action
    log_gdpr_action('DELETE', user_id)
```

## Performance Optimization

### Frontend Optimization

#### Code Splitting
```javascript
// Route-based code splitting
const routes = [
    {
        path: '/',
        component: () => import('./views/HomePage.vue')
    },
    {
        path: '/dashboard',
        component: () => import('./views/DashboardView.vue')
    },
    {
        path: '/admin',
        component: () => import('./views/AdminView.vue')
    }
];
```

#### Caching Strategy
```javascript
// Service worker for offline support
self.addEventListener('fetch', event => {
    if (event.request.url.includes('/api/')) {
        // Network first for API calls
        event.respondWith(
            fetch(event.request)
                .catch(() => caches.match(event.request))
        );
    } else {
        // Cache first for static assets
        event.respondWith(
            caches.match(event.request)
                .then(response => response || fetch(event.request))
        );
    }
});
```

### Backend Optimization

#### DynamoDB Query Optimization
```python
def get_user_registrations(user_id, status=None):
    """Optimized query using GSI when filtering by status"""
    if status:
        # Use GSI for status-based queries
        response = dynamodb.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('status').eq(status),
            FilterExpression=Attr('user_id').eq(user_id)
        )
    else:
        # Use main table for user-based queries
        response = dynamodb.query(
            KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') & 
                                 Key('SK').begins_with('BOAT#')
        )
    
    return response['Items']
```

#### Lambda Cold Start Optimization
```python
# Global connection reuse
import boto3
from functools import lru_cache

@lru_cache(maxsize=1)
def get_dynamodb_client():
    return boto3.resource('dynamodb')

# Minimize import time
def lambda_handler(event, context):
    # Lazy imports for faster cold starts
    from business_logic import process_request
    
    dynamodb = get_dynamodb_client()
    return process_request(event, dynamodb)
```

## Deployment Strategy

### Infrastructure as Code (AWS CDK)

#### Stack Organization
```python
# infrastructure/app.py
from aws_cdk import App
from stacks.database_stack import DatabaseStack
from stacks.api_stack import ApiStack
from stacks.frontend_stack import FrontendStack
from stacks.monitoring_stack import MonitoringStack

app = App()

# Environment-specific stacks
env = app.node.try_get_context("env") or "dev"

database_stack = DatabaseStack(app, f"Database-{env}")
api_stack = ApiStack(app, f"Api-{env}", database=database_stack.table)
frontend_stack = FrontendStack(app, f"Frontend-{env}", api=api_stack.api)
monitoring_stack = MonitoringStack(app, f"Monitoring-{env}")

app.synth()
```

#### Database Stack
```python
# stacks/database_stack.py
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    RemovalPolicy
)

class DatabaseStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        self.table = dynamodb.Table(
            self, "RegistrationTable",
            table_name="impressionnistes-registration",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK", 
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.ON_DEMAND,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.RETAIN
        )
        
        # GSI for registration status queries
        self.table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=dynamodb.Attribute(
                name="status",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            )
        )
```

### CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy Registration System

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          npm ci
          pip install -r requirements.txt
      
      - name: Run frontend tests
        run: npm run test:unit
      
      - name: Run backend tests
        run: pytest
      
      - name: Run E2E tests
        run: npm run test:e2e

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-1
      
      - name: Deploy infrastructure
        run: |
          cd infrastructure
          npm ci
          npx cdk deploy --all --require-approval never
      
      - name: Deploy frontend
        run: |
          npm run build
          aws s3 sync dist/ s3://${{ secrets.S3_BUCKET }} --delete
          aws cloudfront create-invalidation --distribution-id ${{ secrets.CLOUDFRONT_ID }} --paths "/*"
```

This design document provides a comprehensive technical foundation for implementing the Course des Impressionnistes Registration System based on the approved requirements. The serverless architecture ensures scalability and cost-effectiveness, while the detailed component design enables efficient development and maintenance.

## Custom Domains and SSL Certificates

### Overview

The system uses custom domains for both development and production environments to provide professional URLs and secure HTTPS access. Custom domains are configured using AWS Certificate Manager (ACM) for SSL certificates and CloudFront for content delivery.

### Domain Configuration

#### Environment-Specific Domains

**Development Environment:**
- Domain: `impressionnistes-dev.aviron-rcpm.fr`
- Purpose: Testing and development access
- Certificate: ACM certificate in us-east-1 region

**Production Environment:**
- Domain: `impressionnistes.aviron-rcpm.fr`
- Purpose: Live competition registration system
- Certificate: ACM certificate in us-east-1 region

### SSL Certificate Setup

#### Certificate Requirements

CloudFront requires SSL certificates to be created in the **us-east-1 region** regardless of where other resources are deployed. This is a CloudFront global distribution requirement.

#### Certificate Creation Process

**Automated Script (`create-certificates.sh`):**
```bash
#!/bin/bash
# Create SSL certificates for CloudFront custom domains

# Create certificate for dev domain
DEV_CERT_ARN=$(aws acm request-certificate \
    --domain-name impressionnistes-dev.aviron-rcpm.fr \
    --validation-method DNS \
    --region us-east-1 \
    --query 'CertificateArn' \
    --output text)

# Create certificate for prod domain
PROD_CERT_ARN=$(aws acm request-certificate \
    --domain-name impressionnistes.aviron-rcpm.fr \
    --validation-method DNS \
    --region us-east-1 \
    --query 'CertificateArn' \
    --output text)

# Display validation records
aws acm describe-certificate \
    --certificate-arn "$DEV_CERT_ARN" \
    --region us-east-1 \
    --query 'Certificate.DomainValidationOptions[0].ResourceRecord'
```

**Manual Certificate Creation:**
```bash
# Alternative manual approach
aws acm request-certificate \
  --domain-name impressionnistes-dev.aviron-rcpm.fr \
  --validation-method DNS \
  --region us-east-1
```

#### DNS Validation Records

After certificate creation, ACM provides CNAME records for DNS validation:

**Example Validation Record:**
```
Name: _abc123def456.impressionnistes-dev.aviron-rcpm.fr
Type: CNAME
Value: _xyz789.acm-validations.aws.
TTL: 300
```

These records must be added to the domain's DNS configuration (domain registrar or Route53).

#### Certificate Status Verification

```bash
# Check certificate validation status
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:ACCOUNT:certificate/CERT_ID \
  --region us-east-1 \
  --query 'Certificate.Status' \
  --output text

# Expected output: ISSUED (after DNS validation completes)
```

### Infrastructure Configuration

#### Environment Configuration (`infrastructure/config.py`)

```python
class EnvironmentConfig:
    """Helper class to manage environment-specific configuration"""
    
    DEV_CONFIG = {
        "region": "eu-west-3",
        "table_name": "impressionnistes-registration-dev",
        # CloudFront custom domain configuration
        "custom_domain": "impressionnistes-dev.aviron-rcpm.fr",
        "certificate_arn": "arn:aws:acm:us-east-1:ACCOUNT:certificate/DEV_CERT_ID",
    }
    
    PROD_CONFIG = {
        "region": "eu-west-3",
        "table_name": "impressionnistes-registration-prod",
        # CloudFront custom domain configuration
        "custom_domain": "impressionnistes.aviron-rcpm.fr",
        "certificate_arn": "arn:aws:acm:us-east-1:ACCOUNT:certificate/PROD_CERT_ID",
    }
```

#### Frontend Stack Implementation (`infrastructure/stacks/frontend_stack.py`)

```python
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_certificatemanager as acm,
    CfnOutput
)

class FrontendStack(Stack):
    def __init__(self, scope, construct_id, env_name, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # Get custom domain configuration
        from config import EnvironmentConfig
        config = EnvironmentConfig.get_config(env_name)
        custom_domain = config.get("custom_domain")
        certificate_arn = config.get("certificate_arn")
        
        # S3 bucket for static website hosting
        website_bucket = s3.Bucket(
            self, "WebsiteBucket",
            # ... bucket configuration ...
        )
        
        # CloudFront distribution configuration
        distribution_config = {
            "default_behavior": cloudfront.BehaviorOptions(
                origin=origins.S3Origin(website_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            "default_root_object": "index.html",
            "error_responses": [
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(5)
                )
            ]
        }
        
        # Add custom domain and certificate if configured
        if custom_domain and certificate_arn:
            # Import the certificate from ACM (must be in us-east-1 for CloudFront)
            certificate = acm.Certificate.from_certificate_arn(
                self,
                "Certificate",
                certificate_arn
            )
            distribution_config["domain_names"] = [custom_domain]
            distribution_config["certificate"] = certificate
        
        # Create CloudFront distribution
        self.distribution = cloudfront.Distribution(
            self, "Distribution",
            **distribution_config
        )
        
        # Output CloudFront domain name for DNS configuration
        CfnOutput(
            self,
            "DistributionDomainName",
            value=self.distribution.distribution_domain_name,
            description="CloudFront distribution domain name"
        )
        
        # Output website URL
        CfnOutput(
            self,
            "WebsiteURL",
            value=f"https://{custom_domain}" if custom_domain else f"https://{self.distribution.distribution_domain_name}",
            description="Frontend website URL",
            export_name=f"ImpressiornistesFrontendURL-{env_name}"
        )
        
        # Output DNS configuration instructions
        if custom_domain:
            CfnOutput(
                self,
                "CustomDomain",
                value=custom_domain,
                description="Custom domain name configured for CloudFront"
            )
            CfnOutput(
                self,
                "DNSConfiguration",
                value=f"Create CNAME record: {custom_domain} -> {self.distribution.distribution_domain_name}",
                description="DNS configuration required"
            )
```

#### Cognito Integration (`infrastructure/stacks/auth_stack.py`)

Custom domains must be added to Cognito callback and logout URLs:

```python
class AuthStack(Stack):
    def __init__(self, scope, construct_id, env_name, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # Get custom domain configuration
        from config import EnvironmentConfig
        config = EnvironmentConfig.get_config(env_name)
        custom_domain = config.get("custom_domain")
        
        # Build callback URLs
        callback_urls = [
            f"https://{cloudfront_domain}/callback"  # CloudFront default
        ]
        logout_urls = [
            f"https://{cloudfront_domain}/"
        ]
        
        # Add custom domain URLs if configured
        if custom_domain:
            callback_urls.append(f"https://{custom_domain}/callback")
            logout_urls.append(f"https://{custom_domain}/")
        
        # Create Cognito User Pool Client
        user_pool_client = cognito.UserPoolClient(
            self, "UserPoolClient",
            user_pool=user_pool,
            callback_urls=callback_urls,
            logout_urls=logout_urls,
            # ... other configuration ...
        )
```

### DNS Configuration

#### Required DNS Records

**Step 1: Certificate Validation (Add First)**

For each environment, add the CNAME record provided by ACM:

```
# Dev Certificate Validation
Name: _abc123.impressionnistes-dev.aviron-rcpm.fr
Type: CNAME
Value: _xyz789.acm-validations.aws.
TTL: 300

# Prod Certificate Validation
Name: _def456.impressionnistes.aviron-rcpm.fr
Type: CNAME
Value: _uvw012.acm-validations.aws.
TTL: 300
```

**Step 2: CloudFront CNAME (Add After Deployment)**

After deploying the frontend stack, add CNAME records pointing to CloudFront:

```
# Dev Environment
Name: impressionnistes-dev.aviron-rcpm.fr
Type: CNAME
Value: d1234567890abc.cloudfront.net  # From CDK output
TTL: 300

# Prod Environment
Name: impressionnistes.aviron-rcpm.fr
Type: CNAME
Value: d0987654321xyz.cloudfront.net  # From CDK output
TTL: 300
```

### Deployment Workflow

#### Complete Setup Process

**1. Create SSL Certificates**
```bash
cd infrastructure
chmod +x create-certificates.sh
./create-certificates.sh
```

**2. Add DNS Validation Records**
- Copy CNAME records from script output
- Add to DNS configuration (domain registrar or Route53)
- Wait 5-10 minutes for validation

**3. Verify Certificate Status**
```bash
aws acm describe-certificate \
  --certificate-arn <cert-arn> \
  --region us-east-1 \
  --query 'Certificate.Status'
```

**4. Update Configuration**
- Edit `infrastructure/config.py`
- Add certificate ARNs to DEV_CONFIG and PROD_CONFIG

**5. Deploy Infrastructure**
```bash
cd infrastructure
make deploy-dev    # Deploy development environment
make deploy-prod   # Deploy production environment
```

**6. Add CloudFront CNAME Records**
- Get CloudFront domain from deployment output
- Add CNAME records to DNS configuration

**7. Test Custom Domains**
```bash
# Test dev
curl -I https://impressionnistes-dev.aviron-rcpm.fr

# Test prod
curl -I https://impressionnistes.aviron-rcpm.fr
```

### Troubleshooting

#### Certificate Validation Issues

**Problem:** Certificate stays in "Pending validation" status

**Solutions:**
1. Verify DNS records are correct: `dig _abc123.impressionnistes-dev.aviron-rcpm.fr`
2. Check DNS propagation: Use online DNS checker tools
3. Wait up to 30 minutes for DNS propagation
4. If stuck, delete and recreate certificate

#### 403 Error After Deployment

**Problem:** Getting 403 error when accessing custom domain

**Solutions:**
1. Verify certificate ARN is correctly configured in `config.py`
2. Redeploy the frontend stack
3. Check CloudFront distribution in AWS Console shows custom domain
4. Verify certificate status is "ISSUED"

#### DNS Not Resolving

**Problem:** Domain doesn't resolve to CloudFront

**Solutions:**
1. Verify CNAME record exists: `dig impressionnistes-dev.aviron-rcpm.fr`
2. Wait for DNS propagation (up to 48 hours, usually much faster)
3. Clear local DNS cache: `sudo dscacheutil -flushcache` (macOS)
4. Test from different network/location

#### CloudFront Distribution Not Using Certificate

**Problem:** HTTPS not working or showing certificate error

**Solutions:**
1. Verify certificate is in us-east-1 region
2. Check certificate ARN matches in config.py
3. Verify custom domain is added to CloudFront distribution
4. Redeploy frontend stack with correct configuration

### Documentation Files

The system provides comprehensive documentation for custom domain setup:

- **`SETUP_CUSTOM_DOMAINS.md`**: Step-by-step setup guide with all commands
- **`DNS_RECORDS_TO_ADD.md`**: Specific DNS records with actual values for current deployment
- **`create-certificates.sh`**: Automated script for certificate creation
- **`config.py`**: Environment-specific configuration including certificate ARNs

### Security Considerations

1. **HTTPS Enforcement**: CloudFront configured with `REDIRECT_TO_HTTPS` policy
2. **Certificate Validation**: DNS validation ensures domain ownership
3. **Regional Requirements**: Certificates must be in us-east-1 for CloudFront
4. **Certificate Renewal**: ACM automatically renews certificates before expiration
5. **Access Control**: S3 bucket access restricted to CloudFront via Origin Access Identity

## Slack Notifications for Admin and DevOps

### Overview

The system sends real-time Slack notifications to Admin and DevOps channels for important registration events, enabling immediate awareness and response to system activities.

### Slack Integration Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Lambda        │    │   Slack          │    │   Slack         │
│   (Event)       │───►│   Webhook        │───►│   Channel       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
         │
┌─────────────────┐
│   DynamoDB      │
│   (Config)      │
└─────────────────┘
```

### Notification Events

#### Admin Channel Notifications
- **New Boat Registration**: When a club manager completes a boat registration
- **Payment Completed**: When a payment is successfully processed
- **Boat Rental Request**: When an external club requests a boat rental
- **Registration Issue Flagged**: When an admin flags an issue with a registration
- **Registration Issue Resolved**: When a club manager marks an issue as resolved
- **Registration Period Milestones**: Daily summary of registrations and payments

#### DevOps Channel Notifications
- **System Errors**: Lambda function failures, API errors
- **Payment Gateway Issues**: Stripe webhook failures or payment processing errors
- **Database Issues**: DynamoDB throttling or connection errors
- **High Traffic Alerts**: When concurrent users exceed thresholds
- **Deployment Events**: Successful/failed deployments
- **Backup Status**: Daily backup completion status

### Implementation

#### Slack Notification Function
```python
# functions/notifications/send_slack_notification.py
import json
import urllib3
from datetime import datetime

http = urllib3.PoolManager()

def send_slack_notification(webhook_url, message_data):
    """
    Send notification to Slack via incoming webhook
    
    Args:
        webhook_url: Slack incoming webhook URL
        message_data: Dictionary containing message details
    """
    if not webhook_url:
        logger.warning("Slack webhook URL not configured")
        return None
    
    # Build Slack message blocks
    blocks = build_slack_blocks(message_data)
    
    payload = {
        "blocks": blocks,
        "username": "Impressionnistes Registration",
        "icon_emoji": ":rowing:"
    }
    
    try:
        response = http.request(
            'POST',
            webhook_url,
            body=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status == 200:
            logger.info(f"Slack notification sent successfully: {message_data['event_type']}")
            return response.status
        else:
            logger.error(f"Slack notification failed: {response.status} - {response.data}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {str(e)}")
        return None

def build_slack_blocks(message_data):
    """Build Slack message blocks based on event type"""
    event_type = message_data['event_type']
    
    if event_type == 'new_registration':
        return build_registration_blocks(message_data)
    elif event_type == 'payment_completed':
        return build_payment_blocks(message_data)
    elif event_type == 'boat_rental_request':
        return build_rental_blocks(message_data)
    elif event_type == 'system_error':
        return build_error_blocks(message_data)
    elif event_type == 'daily_summary':
        return build_summary_blocks(message_data)
    else:
        return build_generic_blocks(message_data)

def build_registration_blocks(data):
    """Build Slack blocks for new registration notification"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🚣 New Boat Registration",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Club Manager:*\n{data['club_manager_name']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Club:*\n{data['club_name']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Boat Type:*\n{data['boat_type']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Race:*\n{data['race_name']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Crew Size:*\n{data['crew_size']} members"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Multi-Club:*\n{'Yes' if data.get('is_multi_club') else 'No'}"
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Registration ID: `{data['registration_id']}` | {data['timestamp']}"
                }
            ]
        }
    ]

def build_payment_blocks(data):
    """Build Slack blocks for payment notification"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "💳 Payment Completed",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Club Manager:*\n{data['club_manager_name']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Club:*\n{data['club_name']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Amount:*\n€{data['amount']:.2f}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Boats:*\n{data['boat_count']} registrations"
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Payment ID: `{data['payment_id']}` | Stripe: `{data['stripe_id']}` | {data['timestamp']}"
                }
            ]
        }
    ]

def build_rental_blocks(data):
    """Build Slack blocks for boat rental request"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "⛵ Boat Rental Request",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Club Manager:*\n{data['club_manager_name']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Club:*\n{data['club_name']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Boat Type:*\n{data['boat_type']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Status:*\n{data['status']}"
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Request ID: `{data['request_id']}` | {data['timestamp']}"
                }
            ]
        }
    ]

def build_error_blocks(data):
    """Build Slack blocks for system error notification"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🚨 System Error",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Error Type:*\n{data['error_type']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Function:*\n{data['function_name']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Severity:*\n{data['severity']}"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Error Message:*\n```{data['error_message']}```"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Request ID: `{data['request_id']}` | {data['timestamp']}"
                }
            ]
        }
    ]

def build_summary_blocks(data):
    """Build Slack blocks for daily summary"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 Daily Registration Summary",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*New Registrations:*\n{data['new_registrations']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Payments Received:*\n{data['payments_count']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Total Revenue:*\n€{data['total_revenue']:.2f}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Pending Payments:*\n{data['pending_payments']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Total Participants:*\n{data['total_participants']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Boat Rentals:*\n{data['boat_rentals']}"
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Report Date: {data['date']} | Days until competition: {data['days_until_competition']}"
                }
            ]
        }
    ]

def build_generic_blocks(data):
    """Build generic Slack blocks for any event"""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{data.get('title', 'Notification')}*\n{data.get('message', '')}"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": data.get('timestamp', datetime.utcnow().isoformat())
                }
            ]
        }
    ]
```

#### Integration with Event Handlers
```python
# Example: Integration in boat registration handler
def lambda_handler(event, context):
    """Create boat registration with Slack notification"""
    try:
        # Create boat registration
        registration = create_boat_registration(event)
        
        # Send Slack notification to admin channel
        config = get_notification_config()
        if config.get('slack_webhook_admin'):
            send_slack_notification(
                webhook_url=config['slack_webhook_admin'],
                message_data={
                    'event_type': 'new_registration',
                    'club_manager_name': registration['club_manager_name'],
                    'club_name': registration['club_name'],
                    'boat_type': registration['boat_type'],
                    'race_name': registration['race_name'],
                    'crew_size': len(registration['seats']),
                    'is_multi_club': registration.get('is_multi_club_crew', False),
                    'registration_id': registration['registration_id'],
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
        
        return success_response(registration)
        
    except Exception as e:
        # Send error notification to DevOps channel
        config = get_notification_config()
        if config.get('slack_webhook_devops'):
            send_slack_notification(
                webhook_url=config['slack_webhook_devops'],
                message_data={
                    'event_type': 'system_error',
                    'error_type': type(e).__name__,
                    'function_name': 'create_boat_registration',
                    'severity': 'HIGH',
                    'error_message': str(e),
                    'request_id': context.aws_request_id,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
        
        raise
```

#### Daily Summary Scheduler
```python
# functions/notifications/daily_summary.py
def lambda_handler(event, context):
    """Generate and send daily summary to admin Slack channel"""
    
    # Calculate summary statistics
    today = datetime.now().date()
    summary = {
        'new_registrations': count_registrations_today(),
        'payments_count': count_payments_today(),
        'total_revenue': calculate_revenue_today(),
        'pending_payments': count_pending_payments(),
        'total_participants': count_total_participants(),
        'boat_rentals': count_boat_rentals(),
        'date': today.isoformat(),
        'days_until_competition': (get_competition_date() - today).days
    }
    
    # Send to admin Slack channel
    config = get_notification_config()
    if config.get('slack_webhook_admin'):
        send_slack_notification(
            webhook_url=config['slack_webhook_admin'],
            message_data={
                'event_type': 'daily_summary',
                **summary
            }
        )
    
    return {'statusCode': 200, 'body': json.dumps(summary)}
```

### EventBridge Schedule for Daily Summary
```python
# In CDK stack
daily_summary_rule = events.Rule(
    self, "DailySummaryRule",
    schedule=events.Schedule.cron(hour="18", minute="0")  # 6 PM daily
)

daily_summary_rule.add_target(
    targets.LambdaFunction(daily_summary_function)
)
```

### Configuration Management

#### Admin Interface for Slack Configuration
```python
# Admin endpoint to configure Slack webhooks
@require_admin
def update_slack_config(event, context):
    """Update Slack webhook URLs"""
    body = json.loads(event['body'])
    
    config_manager = ConfigurationManager()
    
    updates = {}
    if 'slack_webhook_admin' in body:
        # Validate webhook URL
        if validate_slack_webhook(body['slack_webhook_admin']):
            updates['slack_webhook_admin'] = body['slack_webhook_admin']
        else:
            return error_response(400, "INVALID_WEBHOOK", "Invalid Slack webhook URL")
    
    if 'slack_webhook_devops' in body:
        if validate_slack_webhook(body['slack_webhook_devops']):
            updates['slack_webhook_devops'] = body['slack_webhook_devops']
        else:
            return error_response(400, "INVALID_WEBHOOK", "Invalid Slack webhook URL")
    
    if updates:
        config_manager.update_config('NOTIFICATION', updates, get_current_user_id(event))
        
        # Test the webhooks
        test_results = test_slack_webhooks(updates)
        
        return success_response({
            'message': 'Slack configuration updated',
            'test_results': test_results
        })
    
    return error_response(400, "NO_UPDATES", "No updates provided")

def validate_slack_webhook(url):
    """Validate Slack webhook URL format"""
    return url.startswith('https://hooks.slack.com/services/')

def test_slack_webhooks(webhooks):
    """Send test messages to verify webhooks work"""
    results = {}
    
    for key, webhook_url in webhooks.items():
        try:
            status = send_slack_notification(
                webhook_url=webhook_url,
                message_data={
                    'event_type': 'generic',
                    'title': '✅ Slack Integration Test',
                    'message': 'This is a test message from Impressionnistes Registration System',
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            results[key] = 'success' if status == 200 else 'failed'
        except Exception as e:
            results[key] = f'error: {str(e)}'
    
    return results
```

### Security Considerations

#### Webhook URL Storage
- Slack webhook URLs are stored in DynamoDB configuration (encrypted at rest)
- URLs are never exposed in logs or error messages
- Only Admin users can view/update webhook URLs
- Webhook URLs should be rotated periodically

#### Rate Limiting
```python
# Implement rate limiting to prevent Slack API abuse
from functools import lru_cache
from datetime import datetime, timedelta

class SlackRateLimiter:
    def __init__(self):
        self.message_counts = {}
        self.window_minutes = 1
        self.max_messages_per_window = 10
    
    def can_send(self, channel_type):
        """Check if we can send a message without exceeding rate limits"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.window_minutes)
        
        # Clean old entries
        self.message_counts = {
            k: v for k, v in self.message_counts.items()
            if v['timestamp'] > window_start
        }
        
        # Count messages in current window
        count = sum(
            1 for k, v in self.message_counts.items()
            if k.startswith(channel_type) and v['timestamp'] > window_start
        )
        
        if count >= self.max_messages_per_window:
            logger.warning(f"Slack rate limit reached for {channel_type}")
            return False
        
        # Record this message
        self.message_counts[f"{channel_type}_{now.timestamp()}"] = {
            'timestamp': now
        }
        
        return True

rate_limiter = SlackRateLimiter()

def send_slack_notification_with_rate_limit(webhook_url, message_data, channel_type='admin'):
    """Send Slack notification with rate limiting"""
    if not rate_limiter.can_send(channel_type):
        logger.warning(f"Skipping Slack notification due to rate limit: {message_data['event_type']}")
        return None
    
    return send_slack_notification(webhook_url, message_data)
```

### Monitoring and Alerting

#### CloudWatch Metrics for Slack Notifications
```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def track_slack_notification(event_type, status, channel_type):
    """Track Slack notification metrics in CloudWatch"""
    cloudwatch.put_metric_data(
        Namespace='Impressionnistes/Notifications',
        MetricData=[
            {
                'MetricName': 'SlackNotificationsSent',
                'Value': 1 if status == 'success' else 0,
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'EventType', 'Value': event_type},
                    {'Name': 'Channel', 'Value': channel_type},
                    {'Name': 'Status', 'Value': status}
                ]
            }
        ]
    )
```

This comprehensive Slack integration ensures that Admin and DevOps teams stay informed about all critical registration events and system issues in real-time, enabling quick response and better system monitoring.


## Contact Us Feature

### Overview

The Contact Us feature provides a user-friendly way for anyone (authenticated or anonymous) to send messages to the RCPM organization. Messages are delivered via email to admins and posted to the admin Slack channel for immediate visibility.

### Frontend Component

#### Contact Form Component
```vue
<!-- components/contact/ContactForm.vue -->
<template>
  <div class="contact-form-container">
    <h2>{{ $t('contact.title') }}</h2>
    <p class="contact-intro">{{ $t('contact.intro') }}</p>
    
    <form @submit.prevent="submitContactForm" class="contact-form">
      <div class="form-group">
        <label for="name">{{ $t('contact.name') }} *</label>
        <input
          id="name"
          v-model="form.name"
          type="text"
          :placeholder="$t('contact.namePlaceholder')"
          required
          :disabled="isSubmitting"
        />
      </div>
      
      <div class="form-group">
        <label for="email">{{ $t('contact.email') }} *</label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          :placeholder="$t('contact.emailPlaceholder')"
          required
          :disabled="isSubmitting"
        />
      </div>
      
      <div class="form-group">
        <label for="subject">{{ $t('contact.subject') }} *</label>
        <select
          id="subject"
          v-model="form.subject"
          required
          :disabled="isSubmitting"
        >
          <option value="">{{ $t('contact.selectSubject') }}</option>
          <option value="registration">{{ $t('contact.subjects.registration') }}</option>
          <option value="payment">{{ $t('contact.subjects.payment') }}</option>
          <option value="boat_rental">{{ $t('contact.subjects.boatRental') }}</option>
          <option value="technical">{{ $t('contact.subjects.technical') }}</option>
          <option value="general">{{ $t('contact.subjects.general') }}</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="message">{{ $t('contact.message') }} *</label>
        <textarea
          id="message"
          v-model="form.message"
          rows="6"
          :placeholder="$t('contact.messagePlaceholder')"
          required
          :disabled="isSubmitting"
        ></textarea>
      </div>
      
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
      
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>
      
      <button
        type="submit"
        class="submit-button"
        :disabled="isSubmitting"
      >
        {{ isSubmitting ? $t('contact.sending') : $t('contact.send') }}
      </button>
    </form>
    
    <div class="contact-info">
      <h3>{{ $t('contact.otherWays') }}</h3>
      <p>
        <strong>{{ $t('contact.email') }}:</strong> 
        <a href="mailto:contact@impressionnistes.rcpm.fr">contact@impressionnistes.rcpm.fr</a>
      </p>
      <p>
        <strong>{{ $t('contact.phone') }}:</strong> +33 1 23 45 67 89
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useI18n } from 'vue-i18n';
import api from '@/services/api';

const { t } = useI18n();
const authStore = useAuthStore();

const form = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
});

const isSubmitting = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// Pre-fill form if user is authenticated
onMounted(() => {
  if (authStore.isAuthenticated) {
    form.value.name = `${authStore.user.first_name} ${authStore.user.last_name}`;
    form.value.email = authStore.user.email;
  }
});

const submitContactForm = async () => {
  isSubmitting.value = true;
  errorMessage.value = '';
  successMessage.value = '';
  
  try {
    const response = await api.post('/contact', {
      ...form.value,
      user_id: authStore.user?.user_id || null,
      language: useI18n().locale.value
    });
    
    successMessage.value = t('contact.successMessage');
    
    // Reset form
    form.value = {
      name: authStore.isAuthenticated ? `${authStore.user.first_name} ${authStore.user.last_name}` : '',
      email: authStore.isAuthenticated ? authStore.user.email : '',
      subject: '',
      message: ''
    };
    
  } catch (error) {
    errorMessage.value = error.response?.data?.error?.message || t('contact.errorMessage');
  } finally {
    isSubmitting.value = false;
  }
};
</script>
```

### Backend Implementation

#### Contact Form Lambda Function
```python
# functions/contact/submit_contact_form.py
import json
import boto3
from datetime import datetime
from shared.configuration import config_manager
from shared.notifications import send_email, send_slack_notification
from shared.validation import validate_email

def lambda_handler(event, context):
    """Handle contact form submission"""
    try:
        body = json.loads(event['body'])
        
        # Validate input
        validation_errors = validate_contact_form(body)
        if validation_errors:
            return error_response(400, "VALIDATION_ERROR", "Invalid form data", validation_errors)
        
        # Get user context if authenticated
        user_context = get_user_context(body.get('user_id'))
        
        # Send email to admin
        send_contact_email_to_admin(body, user_context)
        
        # Send auto-reply to user
        send_contact_auto_reply(body)
        
        # Send Slack notification to admin channel
        send_contact_slack_notification(body, user_context)
        
        # Log contact form submission
        log_contact_submission(body, user_context)
        
        return success_response({
            'message': 'Contact form submitted successfully',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Contact form submission failed: {str(e)}", exc_info=True)
        return error_response(500, "SUBMISSION_ERROR", "Failed to submit contact form")

def validate_contact_form(data):
    """Validate contact form data"""
    errors = {}
    
    if not data.get('name') or len(data['name'].strip()) < 2:
        errors['name'] = 'Name is required and must be at least 2 characters'
    
    if not data.get('email') or not validate_email(data['email']):
        errors['email'] = 'Valid email address is required'
    
    if not data.get('subject'):
        errors['subject'] = 'Subject is required'
    
    if not data.get('message') or len(data['message'].strip()) < 10:
        errors['message'] = 'Message is required and must be at least 10 characters'
    
    return errors if errors else None

def get_user_context(user_id):
    """Get additional context if user is authenticated"""
    if not user_id:
        return None
    
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('impressionnistes-registration')
        
        # Get user profile
        response = table.get_item(
            Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'}
        )
        
        if 'Item' in response:
            user = response['Item']
            
            # Get user's registrations count
            registrations_response = table.query(
                KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') & 
                                     Key('SK').begins_with('BOAT#')
            )
            
            return {
                'user_id': user_id,
                'club_affiliation': user.get('club_affiliation'),
                'mobile_number': user.get('mobile_number'),
                'registrations_count': len(registrations_response.get('Items', []))
            }
    except Exception as e:
        logger.warning(f"Failed to get user context: {str(e)}")
    
    return None

def send_contact_email_to_admin(form_data, user_context):
    """Send contact form email to admin"""
    config = config_manager.get_notification_config()
    admin_email = config.get('admin_contact_email', 'contact@impressionnistes.rcpm.fr')
    
    # Build email content
    subject = f"[Contact Form] {form_data['subject']} - {form_data['name']}"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #007bff;">New Contact Form Submission</h2>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p><strong>From:</strong> {form_data['name']}</p>
            <p><strong>Email:</strong> <a href="mailto:{form_data['email']}">{form_data['email']}</a></p>
            <p><strong>Subject:</strong> {form_data['subject']}</p>
            <p><strong>Date:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        </div>
        
        <div style="margin: 20px 0;">
            <h3>Message:</h3>
            <p style="white-space: pre-wrap;">{form_data['message']}</p>
        </div>
        
        {build_user_context_html(user_context) if user_context else ''}
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
        <p style="font-size: 12px; color: #666;">
            This message was sent via the Course des Impressionnistes registration system contact form.
        </p>
    </body>
    </html>
    """
    
    send_email(
        to_email=admin_email,
        subject=subject,
        html_content=html_content,
        reply_to=form_data['email']
    )

def build_user_context_html(user_context):
    """Build HTML for user context information"""
    return f"""
    <div style="background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3>User Context:</h3>
        <p><strong>User ID:</strong> {user_context['user_id']}</p>
        <p><strong>Club:</strong> {user_context.get('club_affiliation', 'N/A')}</p>
        <p><strong>Mobile:</strong> {user_context.get('mobile_number', 'N/A')}</p>
        <p><strong>Registrations:</strong> {user_context.get('registrations_count', 0)} boat(s)</p>
    </div>
    """

def send_contact_auto_reply(form_data):
    """Send auto-reply confirmation to user"""
    language = form_data.get('language', 'fr')
    
    if language == 'fr':
        subject = "Confirmation de réception - Course des Impressionnistes"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #007bff;">Merci de nous avoir contactés</h2>
            
            <p>Bonjour {form_data['name']},</p>
            
            <p>Nous avons bien reçu votre message concernant : <strong>{form_data['subject']}</strong></p>
            
            <p>Notre équipe vous répondra dans les plus brefs délais, généralement sous 24-48 heures.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>Votre message :</h3>
                <p style="white-space: pre-wrap;">{form_data['message']}</p>
            </div>
            
            <p>Cordialement,<br>
            L'équipe Course des Impressionnistes<br>
            RCPM - Rowing Club de Port Marly</p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
            <p style="font-size: 12px; color: #666;">
                Ceci est un message automatique, merci de ne pas y répondre directement.
            </p>
        </body>
        </html>
        """
    else:  # English
        subject = "Confirmation of receipt - Course des Impressionnistes"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #007bff;">Thank you for contacting us</h2>
            
            <p>Hello {form_data['name']},</p>
            
            <p>We have received your message regarding: <strong>{form_data['subject']}</strong></p>
            
            <p>Our team will respond to you as soon as possible, typically within 24-48 hours.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>Your message:</h3>
                <p style="white-space: pre-wrap;">{form_data['message']}</p>
            </div>
            
            <p>Best regards,<br>
            Course des Impressionnistes Team<br>
            RCPM - Rowing Club de Port Marly</p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
            <p style="font-size: 12px; color: #666;">
                This is an automated message, please do not reply directly.
            </p>
        </body>
        </html>
        """
    
    send_email(
        to_email=form_data['email'],
        subject=subject,
        html_content=html_content
    )

def send_contact_slack_notification(form_data, user_context):
    """Send Slack notification to admin channel"""
    config = config_manager.get_notification_config()
    webhook_url = config.get('slack_webhook_admin')
    
    if not webhook_url:
        return
    
    # Build Slack blocks
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📧 New Contact Form Submission",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*From:*\n{form_data['name']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Email:*\n{form_data['email']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Subject:*\n{form_data['subject']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Language:*\n{form_data.get('language', 'fr').upper()}"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Message:*\n{form_data['message'][:500]}{'...' if len(form_data['message']) > 500 else ''}"
            }
        }
    ]
    
    # Add user context if available
    if user_context:
        blocks.append({
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*User ID:*\n`{user_context['user_id']}`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Club:*\n{user_context.get('club_affiliation', 'N/A')}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Registrations:*\n{user_context.get('registrations_count', 0)} boat(s)"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Mobile:*\n{user_context.get('mobile_number', 'N/A')}"
                }
            ]
        })
    
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"Submitted at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
            }
        ]
    })
    
    send_slack_notification(webhook_url, {'blocks': blocks})

def log_contact_submission(form_data, user_context):
    """Log contact form submission to DynamoDB"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('impressionnistes-registration')
    
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    table.put_item(
        Item={
            'PK': 'CONTACT',
            'SK': f'{timestamp}#{form_data["email"]}',
            'name': form_data['name'],
            'email': form_data['email'],
            'subject': form_data['subject'],
            'message': form_data['message'],
            'language': form_data.get('language', 'fr'),
            'user_id': form_data.get('user_id'),
            'user_context': user_context,
            'timestamp': timestamp,
            'status': 'submitted'
        }
    )
```

### Translations

#### French (fr.json)
```json
{
  "contact": {
    "title": "Contactez-nous",
    "intro": "Vous avez une question ou besoin d'aide ? N'hésitez pas à nous contacter.",
    "name": "Nom",
    "namePlaceholder": "Votre nom complet",
    "email": "Email",
    "emailPlaceholder": "votre.email@example.com",
    "subject": "Sujet",
    "selectSubject": "Sélectionnez un sujet",
    "subjects": {
      "registration": "Inscription",
      "payment": "Paiement",
      "boatRental": "Location de bateau",
      "technical": "Problème technique",
      "general": "Question générale"
    },
    "message": "Message",
    "messagePlaceholder": "Décrivez votre question ou problème...",
    "send": "Envoyer",
    "sending": "Envoi en cours...",
    "successMessage": "Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.",
    "errorMessage": "Une erreur s'est produite lors de l'envoi de votre message. Veuillez réessayer.",
    "otherWays": "Autres moyens de nous contacter"
  }
}
```

#### English (en.json)
```json
{
  "contact": {
    "title": "Contact Us",
    "intro": "Have a question or need help? Feel free to contact us.",
    "name": "Name",
    "namePlaceholder": "Your full name",
    "email": "Email",
    "emailPlaceholder": "your.email@example.com",
    "subject": "Subject",
    "selectSubject": "Select a subject",
    "subjects": {
      "registration": "Registration",
      "payment": "Payment",
      "boatRental": "Boat Rental",
      "technical": "Technical Issue",
      "general": "General Question"
    },
    "message": "Message",
    "messagePlaceholder": "Describe your question or issue...",
    "send": "Send",
    "sending": "Sending...",
    "successMessage": "Your message has been sent successfully. We will respond as soon as possible.",
    "errorMessage": "An error occurred while sending your message. Please try again.",
    "otherWays": "Other ways to contact us"
  }
}
```

### Router Configuration
```javascript
// router/index.js
{
  path: '/contact',
  name: 'Contact',
  component: () => import('@/views/ContactView.vue'),
  meta: {
    title: 'Contact Us',
    requiresAuth: false  // Available to everyone
  }
}
```

### API Gateway Endpoint
```python
# CDK Stack configuration
contact_function = lambda_.Function(
    self, "ContactFunction",
    runtime=lambda_.Runtime.PYTHON_3_11,
    handler="submit_contact_form.lambda_handler",
    code=lambda_.Code.from_asset("functions/contact"),
    environment={
        'TABLE_NAME': database_stack.table.table_name
    }
)

# Grant permissions
database_stack.table.grant_write_data(contact_function)

# API Gateway integration
api.add_routes(
    path="/contact",
    methods=[apigw.HttpMethod.POST],
    integration=apigw_integrations.HttpLambdaIntegration(
        "ContactIntegration",
        contact_function
    )
)
```

This comprehensive Contact Us feature provides users with an easy way to reach out to admins, while ensuring admins are immediately notified via both email and Slack, with full context about the user if they're authenticated.


## Access Control System

### Overview

The Access Control System (FR-17, TC-7) provides centralized permission management for all operations in the registration system. It determines which actions are permitted based on user role, event phase (dates), impersonation status, and data state.

### Architecture

```
┌─────────────────┐
│  Event Phase    │
│   Detection     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐    ┌──────────────────┐
│   Permission    │◄───│  Temporary       │
│     Matrix      │    │  Access Grants   │
└────────┬────────┘    └──────────────────┘
         │
         ▼
┌─────────────────┐
│   Backend &     │
│   Frontend      │
│   Enforcement   │
└─────────────────┘
```

### Event Phase Detection

```python
# shared/event_phase.py
from datetime import datetime
from functools import lru_cache
from shared.configuration import config_manager

@lru_cache(maxsize=1, ttl=60)  # Cache for 60 seconds
def get_current_event_phase():
    """Determine current event phase based on configuration dates"""
    config = config_manager.get_system_config()
    now = datetime.utcnow().date()
    
    reg_start = datetime.fromisoformat(config['registration_start_date']).date()
    reg_end = datetime.fromisoformat(config['registration_end_date']).date()
    payment_deadline = datetime.fromisoformat(config['payment_deadline']).date()
    
    if now < reg_start:
        return 'before_registration'
    elif reg_start <= now <= reg_end:
        return 'during_registration'
    elif reg_end < now <= payment_deadline:
        return 'after_registration'
    else:
        return 'after_payment_deadline'
```

### Permission Matrix

```python
# shared/access_control.py
PERMISSION_MATRIX = {
    'create_crew_member': {
        'before_registration': {'club_manager': False, 'admin': True},
        'during_registration': {'club_manager': True, 'admin': True},
        'after_registration': {'club_manager': False, 'admin': True},
        'after_payment_deadline': {'club_manager': False, 'admin': True}
    },
    'edit_crew_member': {
        'before_registration': {'club_manager': False, 'admin': True},
        'during_registration': {'club_manager': True, 'admin': True},
        'after_registration': {'club_manager': False, 'admin': True},
        'after_payment_deadline': {'club_manager': False, 'admin': True}
    },
    'delete_crew_member': {
        'before_registration': {'club_manager': False, 'admin': True},
        'during_registration': {'club_manager': True, 'admin': True},
        'after_registration': {'club_manager': False, 'admin': True},
        'after_payment_deadline': {'club_manager': False, 'admin': True}
    },
    'create_boat_registration': {
        'before_registration': {'club_manager': False, 'admin': True},
        'during_registration': {'club_manager': True, 'admin': True},
        'after_registration': {'club_manager': False, 'admin': True},
        'after_payment_deadline': {'club_manager': False, 'admin': True}
    },
    'edit_boat_registration': {
        'before_registration': {'club_manager': False, 'admin': True},
        'during_registration': {'club_manager': True, 'admin': True},
        'after_registration': {'club_manager': False, 'admin': True},
        'after_payment_deadline': {'club_manager': False, 'admin': True}
    },
    'delete_boat_registration': {
        'before_registration': {'club_manager': False, 'admin': True},
        'during_registration': {'club_manager': True, 'admin': True},
        'after_registration': {'club_manager': False, 'admin': True},
        'after_payment_deadline': {'club_manager': False, 'admin': True}
    },
    'process_payment': {
        'before_registration': {'club_manager': False, 'admin': True},
        'during_registration': {'club_manager': True, 'admin': True},
        'after_registration': {'club_manager': True, 'admin': True},
        'after_payment_deadline': {'club_manager': False, 'admin': True}
    }
}

def check_permission(user_id, action, context=None):
    """
    Check if user has permission to perform action
    
    Returns: PermissionResult(allowed=bool, reason=str)
    """
    user = get_user(user_id)
    role = user.get('role', 'club_manager')
    
    # Admins bypass all restrictions
    if role == 'admin':
        return PermissionResult(allowed=True, reason='Admin access')
    
    # Check for temporary access grant
    if has_active_access_grant(user_id):
        return PermissionResult(allowed=True, reason='Temporary access grant')
    
    # Check event phase
    phase = get_current_event_phase()
    
    # Check permission matrix
    if action in PERMISSION_MATRIX:
        allowed = PERMISSION_MATRIX[action][phase].get(role, False)
        
        if not allowed:
            reason = f"Action '{action}' not permitted during {phase.replace('_', ' ')}"
            return PermissionResult(allowed=False, reason=reason)
        
        # Additional data state checks
        if context:
            data_check = check_data_state_restrictions(action, context)
            if not data_check.allowed:
                return data_check
        
        return PermissionResult(allowed=True, reason='Permission granted')
    
    return PermissionResult(allowed=False, reason=f"Unknown action: {action}")

def check_data_state_restrictions(action, context):
    """Check data state restrictions (paid boats, assigned crew)"""
    if action == 'delete_boat_registration':
        if context.get('boat_status') == 'paid':
            return PermissionResult(allowed=False, reason='Cannot delete paid boat')
    
    if action == 'delete_crew_member':
        if context.get('assigned_to_boat'):
            return PermissionResult(allowed=False, reason='Cannot delete assigned crew member')
    
    return PermissionResult(allowed=True, reason='Data state check passed')
```

### Frontend Integration

```javascript
// composables/usePermissions.js
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

export function usePermissions() {
    const authStore = useAuthStore()
    const permissions = ref({})
    
    async function loadPermissions() {
        const response = await api.get('/permissions/current')
        permissions.value = response.data
    }
    
    function canPerform(action, context = null) {
        // Check cached permissions
        const key = context ? `${action}:${JSON.stringify(context)}` : action
        return permissions.value[key] ?? false
    }
    
    return {
        loadPermissions,
        canPerform
    }
}
```

```vue
<!-- Usage in components -->
<script setup>
import { usePermissions } from '@/composables/usePermissions'

const { canPerform } = usePermissions()
const canCreateCrew = canPerform('create_crew_member')
</script>

<template>
  <BaseButton 
    :disabled="!canCreateCrew" 
    @click="createCrew"
  >
    Create Crew Member
  </BaseButton>
</template>
```

### Temporary Access Grants

```python
# admin/grant_temporary_access.py
def lambda_handler(event, context):
    """Grant temporary access to club manager"""
    admin_id = get_current_user_id(event)
    body = json.loads(event['body'])
    
    grant = {
        'PK': f"USER#{body['user_id']}",
        'SK': f"ACCESS_GRANT#{generate_id()}",
        'granted_by': admin_id,
        'granted_at': datetime.utcnow().isoformat(),
        'expires_at': (datetime.utcnow() + timedelta(hours=body['duration_hours'])).isoformat(),
        'status': 'active'
    }
    
    table.put_item(Item=grant)
    
    return success_response(grant)

def has_active_access_grant(user_id):
    """Check if user has active temporary access grant"""
    response = table.query(
        IndexName='GSI5',
        KeyConditionExpression=Key('status').eq('active'),
        FilterExpression=Attr('PK').eq(f'USER#{user_id}') & 
                        Attr('expires_at').gt(datetime.utcnow().isoformat())
    )
    return len(response['Items']) > 0
```

## Design System and UI Consistency

### Overview

The Design System (NFR-7) provides standardized UI components, styles, and patterns to ensure consistency across the application.

### Design Tokens

```css
/* assets/design-tokens.css */
:root {
  /* Colors - Semantic */
  --color-primary: #007bff;
  --color-success: #28a745;
  --color-warning: #ffc107;
  --color-danger: #dc3545;
  --color-secondary: #6c757d;
  --color-light: #f8f9fa;
  --color-dark: #212529;
  --color-muted: #666;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 0.75rem;
  --spacing-lg: 1rem;
  --spacing-xl: 1.5rem;
  --spacing-2xl: 2rem;
  
  /* Typography */
  --font-size-sm: 0.75rem;
  --font-size-base: 0.875rem;
  --font-size-lg: 1rem;
  --font-size-xl: 1.125rem;
  --font-size-2xl: 1.5rem;
  
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  /* Breakpoints */
  --breakpoint-mobile: 768px;
  --breakpoint-tablet: 1024px;
}
```

### Base Components

See `docs/design-system.md` for complete component documentation including:
- BaseButton variants and states
- StatusBadge color mapping
- BaseModal responsive behavior
- LoadingSpinner and EmptyState patterns
- DataCard and SortableTable usage
- FormGroup and MessageAlert styling

### Mobile Responsiveness (NFR-8)

```css
/* Mobile-first responsive patterns */
@media (max-width: 768px) {
  .button-group {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .button {
    width: 100%;
    min-height: 44px; /* Touch-friendly */
  }
  
  .modal {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    border-radius: 12px 12px 0 0; /* Bottom sheet */
    max-height: 90vh;
  }
}
```

## Export Architecture

### JSON API Pattern (FR-21)

All exports follow a consistent pattern: backend returns JSON, frontend handles formatting.

```python
# admin/export_crew_members_json.py
def lambda_handler(event, context):
    """Export crew members as JSON"""
    crew_members = []
    
    # Paginate through all crew members
    response = table.scan()
    crew_members.extend(response['Items'])
    
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        crew_members.extend(response['Items'])
    
    # Convert Decimal to float for JSON compatibility
    crew_members = convert_decimals(crew_members)
    
    return success_response({
        'data': crew_members,
        'count': len(crew_members),
        'exported_at': datetime.utcnow().isoformat()
    })
```

```javascript
// utils/exportFormatters.js
export function exportToCSV(data, columns) {
    const headers = columns.map(c => c.label).join(',')
    const rows = data.map(row => 
        columns.map(c => formatCell(row[c.key])).join(',')
    )
    return [headers, ...rows].join('\n')
}

export function exportToExcel(data, columns, sheetName) {
    const worksheet = XLSX.utils.json_to_sheet(data)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)
    return XLSX.write(workbook, { type: 'buffer', bookType: 'xlsx' })
}
```

### Event Program Export (FR-22)

Priority export for race day printing with professional formatting.

```python
# admin/export_event_program.py
def lambda_handler(event, context):
    """Generate multi-sheet Excel for race day"""
    
    # Sheet 1: Crew Members
    crew_members = get_all_crew_members()
    crew_sheet = format_crew_member_sheet(crew_members)
    
    # Sheet 2: Race Schedule
    races = get_all_races()
    eligible_boats = get_eligible_boats()  # complete/paid/free, not forfait
    
    # Assign race and bow numbers
    race_schedule = []
    race_number = 1
    
    for race in sorted(races, key=lambda r: r['display_order']):
        boats_in_race = [b for b in eligible_boats if b['race_id'] == race['race_id']]
        
        if boats_in_race:
            bow_number = 1
            for boat in boats_in_race:
                race_schedule.append({
                    'race_number': race_number,
                    'race_name': race['name'],
                    'bow_number': bow_number,
                    'boat_id': boat['boat_id'],
                    'club': boat['boat_club_display'],
                    'crew': format_crew_names(boat)
                })
                bow_number += 1
            race_number += 1
    
    # Generate Excel with professional formatting
    workbook = create_formatted_workbook([
        ('Crew Members', crew_sheet),
        ('Race Schedule', race_schedule)
    ])
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Content-Disposition': 'attachment; filename=event-program.xlsx'
        },
        'body': base64.b64encode(workbook).decode('utf-8'),
        'isBase64Encoded': True
    }
```

This completes the design document updates with all new components, patterns, and architectural additions from the breakdown specifications.
