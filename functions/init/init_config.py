"""
Lambda function to initialize default configuration in DynamoDB
This runs as a CDK custom resource during stack deployment
"""
import json
import os
import boto3
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

dynamodb = boto3.resource('dynamodb')


def load_secrets():
    """Load secrets from secrets.json file"""
    secrets_file = Path(__file__).parent.parent.parent / 'infrastructure' / 'secrets.json'
    
    if secrets_file.exists():
        with open(secrets_file, 'r') as f:
            return json.load(f)
    
    # Return empty dict if file doesn't exist (will use empty strings)
    print("Warning: secrets.json not found, using empty values")
    return {}


def lambda_handler(event, context):
    """
    Initialize default configuration in DynamoDB table
    
    This function is called by CDK custom resource during deployment
    """
    print(f"Event: {json.dumps(event)}")
    
    request_type = event.get('RequestType')
    table_name = os.environ.get('TABLE_NAME')
    environment = os.environ.get('ENVIRONMENT', 'dev')
    
    # Use a fixed physical resource ID to avoid deletion issues
    physical_resource_id = event.get('PhysicalResourceId', f'InitConfig-{table_name}')
    
    if not table_name:
        return send_response(event, context, 'FAILED', {'Error': 'TABLE_NAME not set'}, physical_resource_id)
    
    try:
        table = dynamodb.Table(table_name)
        
        if request_type in ['Create', 'Update']:
            # Initialize default configurations
            initialize_system_config(table, environment)
            initialize_pricing_config(table)
            initialize_notification_config(table)
            initialize_race_definitions(table)
            initialize_rowing_clubs(table)
            
            print("Configuration initialized successfully")
            return send_response(event, context, 'SUCCESS', {
                'Message': 'Configuration initialized',
                'TableName': table_name
            }, physical_resource_id)
        
        elif request_type == 'Delete':
            # Don't delete data on stack deletion
            print("Delete request - no action taken")
            return send_response(event, context, 'SUCCESS', {
                'Message': 'Delete completed'
            }, physical_resource_id)
        
        return send_response(event, context, 'SUCCESS', {}, physical_resource_id)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return send_response(event, context, 'FAILED', {
            'Error': str(e)
        }, physical_resource_id)


def initialize_system_config(table, environment):
    """Initialize system configuration with default values"""
    # Calculate default dates (registration starts in 2 weeks, ends in 6 weeks)
    today = datetime.now()
    registration_start = today + timedelta(days=14)
    registration_end = today + timedelta(days=42)
    payment_deadline = registration_end + timedelta(days=7)
    competition_date = payment_deadline + timedelta(days=7)
    
    system_config = {
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'registration_start_date': registration_start.strftime('%Y-%m-%d'),
        'registration_end_date': registration_end.strftime('%Y-%m-%d'),
        'payment_deadline': payment_deadline.strftime('%Y-%m-%d'),
        'rental_priority_days': 15,
        'competition_date': competition_date.strftime('%Y-%m-%d'),
        'temporary_editing_access_hours': 48,
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'updated_at': datetime.utcnow().isoformat() + 'Z',
        'updated_by': 'system',
        'environment': environment,
    }
    
    # Use put_item with condition to avoid overwriting existing config
    try:
        table.put_item(
            Item=system_config,
            ConditionExpression='attribute_not_exists(PK)'
        )
        print("System configuration initialized")
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        print("System configuration already exists - skipping")


def initialize_pricing_config(table):
    """Initialize pricing configuration with default values"""
    pricing_config = {
        'PK': 'CONFIG',
        'SK': 'PRICING',
        'base_seat_price': Decimal('20.00'),
        'boat_rental_multiplier_skiff': Decimal('2.5'),
        'boat_rental_price_crew': Decimal('20.00'),
        'currency': 'EUR',
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'updated_at': datetime.utcnow().isoformat() + 'Z',
        'updated_by': 'system',
    }
    
    try:
        table.put_item(
            Item=pricing_config,
            ConditionExpression='attribute_not_exists(PK)'
        )
        print("Pricing configuration initialized")
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        print("Pricing configuration already exists - skipping")


def initialize_notification_config(table):
    """Initialize notification configuration with default values"""
    # Load secrets from file
    secrets = load_secrets()
    
    notification_config = {
        'PK': 'CONFIG',
        'SK': 'NOTIFICATION',
        'notification_frequency_days': 7,
        'session_timeout_minutes': 30,
        'notification_channels': ['email', 'in_app', 'slack'],
        'email_from': 'impressionnistes@rcpm-aviron.fr',
        'slack_webhook_admin': secrets.get('slack_webhook_admin', ''),
        'slack_webhook_devops': secrets.get('slack_webhook_devops', ''),
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'updated_at': datetime.utcnow().isoformat() + 'Z',
        'updated_by': 'system',
    }
    
    try:
        table.put_item(
            Item=notification_config,
            ConditionExpression='attribute_not_exists(PK)'
        )
        print("Notification configuration initialized")
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        print("Notification configuration already exists - skipping")


def initialize_race_definitions(table):
    """Initialize race definitions for marathon and semi-marathon events"""
    
    # Marathon races (42km) - Individual skiff races
    marathon_races = [
        {'race_id': 'M01', 'display_order': 1, 'short_name': 'MWF1X', 'name': '1X MASTER F WOMAN', 'event_type': '42km', 'boat_type': 'skiff',
         'age_category': 'master', 'master_category': 'F', 'gender_category': 'women', 'distance': 42},
        {'race_id': 'M02', 'display_order': 2, 'short_name': 'MMF1X', 'name': '1X MASTER F MAN', 'event_type': '42km', 'boat_type': 'skiff',
         'age_category': 'master', 'master_category': 'F', 'gender_category': 'men', 'distance': 42},
        {'race_id': 'M03', 'display_order': 3, 'short_name': 'MWE1X', 'name': '1X MASTER E WOMAN', 'event_type': '42km', 'boat_type': 'skiff',
         'age_category': 'master', 'master_category': 'E', 'gender_category': 'women', 'distance': 42},
        {'race_id': 'M04', 'display_order': 4, 'short_name': 'MME1X', 'name': '1X MASTER E MAN', 'event_type': '42km', 'boat_type': 'skiff',
         'age_category': 'master', 'master_category': 'E', 'gender_category': 'men', 'distance': 42},
        {'race_id': 'M05', 'display_order': 5, 'short_name': 'MWD1X', 'name': '1X MASTER D WOMAN', 'event_type': '42km', 'boat_type': 'skiff',
         'age_category': 'master', 'master_category': 'D', 'gender_category': 'women', 'distance': 42},
        {'race_id': 'M06', 'display_order': 6, 'short_name': 'MMD1X', 'name': '1X MASTER D MAN', 'event_type': '42km', 'boat_type': 'skiff',
         'age_category': 'master', 'master_category': 'D', 'gender_category': 'men', 'distance': 42},
        {'race_id': 'M07', 'display_order': 7, 'short_name': 'MWC1X', 'name': '1X MASTER C WOMAN', 'event_type': '42km', 'boat_type': 'skiff',
         'age_category': 'master', 'master_category': 'C', 'gender_category': 'women', 'distance': 42},
        {'race_id': 'M08', 'display_order': 8, 'short_name': 'MMC1X', 'name': '1X MASTER C MAN', 'event_type': '42km', 'boat_type': 'skiff',
         'age_category': 'master', 'master_category': 'C', 'gender_category': 'men', 'distance': 42},
        {'race_id': 'M09', 'display_order': 9, 'short_name': 'MWB1X', 'name': '1X MASTER B WOMAN', 'event_type': '42km', 'boat_type': 'skiff',
         'age_category': 'master', 'master_category': 'B', 'gender_category': 'women', 'distance': 42},
        {'race_id': 'M10', 'display_order': 10, 'short_name': 'MMB1X', 'name': '1X MASTER B MAN', 'event_type': '42km', 'boat_type': 'skiff',
         'age_category': 'master', 'master_category': 'B', 'gender_category': 'men', 'distance': 42},
        {'race_id': 'M11', 'display_order': 11, 'short_name': 'MWA1X', 'name': '1X MASTER A WOMAN', 'event_type': '42km', 'boat_type': 'skiff',
         'age_category': 'master', 'master_category': 'A', 'gender_category': 'women', 'distance': 42},
        {'race_id': 'M12', 'display_order': 12, 'short_name': 'MMA1X', 'name': '1X MASTER A MAN', 'event_type': '42km', 'boat_type': 'skiff',
         'age_category': 'master', 'master_category': 'A', 'gender_category': 'men', 'distance': 42},
        {'race_id': 'M13', 'display_order': 13, 'short_name': 'SW1X', 'name': '1X SENIOR WOMAN', 'event_type': '42km', 'boat_type': 'skiff', 
         'age_category': 'senior', 'gender_category': 'women', 'distance': 42},
        {'race_id': 'M14', 'display_order': 14, 'short_name': 'SM1X', 'name': '1X SENIOR MAN', 'event_type': '42km', 'boat_type': 'skiff',
         'age_category': 'senior', 'gender_category': 'men', 'distance': 42},
    ]
    
    # Semi-marathon races (21km) - Team races
    # Final list of 41 races
    semi_marathon_races = [
        # J16 races (7 races)
        {'race_id': 'SM08', 'display_order': 22, 'short_name': 'J16W4+', 'name': 'WOMEN-JUNIOR J16-COXED SWEEP FOUR', 'event_type': '21km',
         'boat_type': '4+', 'age_category': 'j16', 'gender_category': 'women', 'distance': 21},
        {'race_id': 'SM09', 'display_order': 23, 'short_name': 'J16W4X+', 'name': 'WOMEN-JUNIOR J16-COXED QUAD SCULL', 'event_type': '21km',
         'boat_type': '4x+', 'age_category': 'j16', 'gender_category': 'women', 'distance': 21},
        {'race_id': 'SM11', 'display_order': 25, 'short_name': 'J16M4+', 'name': 'MEN-JUNIOR J16-COXED SWEEP FOUR', 'event_type': '21km',
         'boat_type': '4+', 'age_category': 'j16', 'gender_category': 'men', 'distance': 21},
        {'race_id': 'SM12', 'display_order': 26, 'short_name': 'J16M4X+', 'name': 'MEN-JUNIOR J16-COXED QUAD SCULL', 'event_type': '21km',
         'boat_type': '4x+', 'age_category': 'j16', 'gender_category': 'men', 'distance': 21},
        {'race_id': 'SM10', 'display_order': 24, 'short_name': 'J16X4X+', 'name': 'MIXED-GENDER-JUNIOR J16-COXED QUAD SCULL', 'event_type': '21km',
         'boat_type': '4x+', 'age_category': 'j16', 'gender_category': 'mixed', 'distance': 21},
        {'race_id': 'SM28', 'display_order': 42, 'short_name': 'J16W8+', 'name': 'WOMEN-JUNIOR J16-SWEEP EIGHT WITH COXSWAIN', 'event_type': '21km',
         'boat_type': '8+', 'age_category': 'j16', 'gender_category': 'women', 'distance': 21},
        {'race_id': 'SM29', 'display_order': 43, 'short_name': 'J16M8+', 'name': 'MEN-JUNIOR J16-SWEEP EIGHT WITH COXSWAIN', 'event_type': '21km',
         'boat_type': '8+', 'age_category': 'j16', 'gender_category': 'men', 'distance': 21},
        
        # J18 races (8 races)
        {'race_id': 'SM18', 'display_order': 32, 'short_name': 'J18W4-', 'name': 'WOMEN-JUNIOR J18-SWEEP FOUR WITHOUT COXSWAIN', 'event_type': '21km',
         'boat_type': '4-', 'age_category': 'j18', 'gender_category': 'women', 'distance': 21},
        {'race_id': 'SM19', 'display_order': 33, 'short_name': 'J18W4X-', 'name': 'WOMEN-JUNIOR J18-QUAD SCULL WITHOUT COXSWAIN', 'event_type': '21km',
         'boat_type': '4x-', 'age_category': 'j18', 'gender_category': 'women', 'distance': 21},
        {'race_id': 'SM21', 'display_order': 35, 'short_name': 'J18M4-', 'name': 'MEN-JUNIOR J18-SWEEP FOUR WITHOUT COXSWAIN', 'event_type': '21km',
         'boat_type': '4-', 'age_category': 'j18', 'gender_category': 'men', 'distance': 21},
        {'race_id': 'SM22', 'display_order': 36, 'short_name': 'J18M4X-', 'name': 'MEN-JUNIOR J18-QUAD SCULL WITHOUT COXSWAIN', 'event_type': '21km',
         'boat_type': '4x-', 'age_category': 'j18', 'gender_category': 'men', 'distance': 21},
        {'race_id': 'SM20', 'display_order': 34, 'short_name': 'J18X4X-', 'name': 'MIXED-GENDER-JUNIOR J18-QUAD SCULL WITHOUT COXSWAIN', 'event_type': '21km',
         'boat_type': '4x-', 'age_category': 'j18', 'gender_category': 'mixed', 'distance': 21},
        {'race_id': 'SM36', 'display_order': 50, 'short_name': 'J18W8+', 'name': 'WOMEN-JUNIOR J18-SWEEP EIGHT WITH COXSWAIN', 'event_type': '21km',
         'boat_type': '8+', 'age_category': 'j18', 'gender_category': 'women', 'distance': 21},
        {'race_id': 'SM38', 'display_order': 52, 'short_name': 'J18M8+', 'name': 'MEN-JUNIOR J18-SWEEP EIGHT WITH COXSWAIN', 'event_type': '21km',
         'boat_type': '8+', 'age_category': 'j18', 'gender_category': 'men', 'distance': 21},
        {'race_id': 'SM37', 'display_order': 51, 'short_name': 'J18X8+', 'name': 'MIXED-GENDER-JUNIOR J18-SWEEP EIGHT WITH COXSWAIN', 'event_type': '21km',
         'boat_type': '8+', 'age_category': 'j18', 'gender_category': 'mixed', 'distance': 21},
        
        # Senior races (8 races)
        {'race_id': 'SM23', 'display_order': 37, 'short_name': 'SW4-', 'name': 'WOMEN-SENIOR-SWEEP FOUR WITHOUT COXSWAIN', 'event_type': '21km',
         'boat_type': '4-', 'age_category': 'senior', 'gender_category': 'women', 'distance': 21},
        {'race_id': 'SM24', 'display_order': 38, 'short_name': 'SW4X-', 'name': 'WOMEN-SENIOR-QUAD SCULL WITHOUT COXSWAIN', 'event_type': '21km',
         'boat_type': '4x-', 'age_category': 'senior', 'gender_category': 'women', 'distance': 21},
        {'race_id': 'SM26', 'display_order': 40, 'short_name': 'SM4-', 'name': 'MEN-SENIOR-SWEEP FOUR WITHOUT COXSWAIN', 'event_type': '21km',
         'boat_type': '4-', 'age_category': 'senior', 'gender_category': 'men', 'distance': 21},
        {'race_id': 'SM27', 'display_order': 41, 'short_name': 'SM4X-', 'name': 'MEN-SENIOR-QUAD SCULL WITHOUT COXSWAIN', 'event_type': '21km',
         'boat_type': '4x-', 'age_category': 'senior', 'gender_category': 'men', 'distance': 21},
        {'race_id': 'SM25', 'display_order': 39, 'short_name': 'SX4X-', 'name': 'MIXED-GENDER-SENIOR-QUAD SCULL WITHOUT COXSWAIN', 'event_type': '21km',
         'boat_type': '4x-', 'age_category': 'senior', 'gender_category': 'mixed', 'distance': 21},
        {'race_id': 'SM39', 'display_order': 53, 'short_name': 'SW8+', 'name': 'WOMEN-SENIOR-SWEEP EIGHT WITH COXSWAIN', 'event_type': '21km',
         'boat_type': '8+', 'age_category': 'senior', 'gender_category': 'women', 'distance': 21},
        {'race_id': 'SM41', 'display_order': 55, 'short_name': 'SM8+', 'name': 'MEN-SENIOR-SWEEP EIGHT WITH COXSWAIN', 'event_type': '21km',
         'boat_type': '8+', 'age_category': 'senior', 'gender_category': 'men', 'distance': 21},
        {'race_id': 'SM40', 'display_order': 54, 'short_name': 'SX8+', 'name': 'MIXED-GENDER-SENIOR-SWEEP EIGHT WITH COXSWAIN', 'event_type': '21km',
         'boat_type': '8+', 'age_category': 'senior', 'gender_category': 'mixed', 'distance': 21},
        
        # Master races (18 races)
        # Yolette category (3 races)
        {'race_id': 'SM01', 'display_order': 15, 'short_name': 'MW4X+Y', 'name': 'WOMEN-MASTER-COXED QUAD SCULL YOLETTE', 'event_type': '21km',
         'boat_type': '4x+', 'age_category': 'master', 'gender_category': 'women', 'distance': 21},
        {'race_id': 'SM03', 'display_order': 17, 'short_name': 'MM4X+Y', 'name': 'MEN-MASTER-COXED QUAD SCULL YOLETTE', 'event_type': '21km',
         'boat_type': '4x+', 'age_category': 'master', 'gender_category': 'men', 'distance': 21},
        {'race_id': 'SM02', 'display_order': 16, 'short_name': 'MX4X+Y', 'name': 'MIXED-GENDER-MASTER-COXED QUAD SCULL YOLETTE', 'event_type': '21km',
         'boat_type': '4x+', 'age_category': 'master', 'gender_category': 'mixed', 'distance': 21},
        
        # Coxed quad scull (3 races)
        {'race_id': 'SM04', 'display_order': 18, 'short_name': 'MW4X+', 'name': 'WOMEN-MASTER-COXED QUAD SCULL', 'event_type': '21km',
         'boat_type': '4x+', 'age_category': 'master', 'gender_category': 'women', 'distance': 21},
        {'race_id': 'SM07', 'display_order': 21, 'short_name': 'MM4X+', 'name': 'MEN-MASTER-COXED QUAD SCULL', 'event_type': '21km',
         'boat_type': '4x+', 'age_category': 'master', 'gender_category': 'men', 'distance': 21},
        {'race_id': 'SM05', 'display_order': 19, 'short_name': 'MX4X+', 'name': 'MIXED-GENDER-MASTER-COXED QUAD SCULL', 'event_type': '21km',
         'boat_type': '4x+', 'age_category': 'master', 'gender_category': 'mixed', 'distance': 21},
        
        # Octuple scull with coxswain (3 races)
        {'race_id': 'SM33', 'display_order': 47, 'short_name': 'MW8X+', 'name': 'WOMEN-MASTER-OCTUPLE SCULL WITH COXSWAIN', 'event_type': '21km',
         'boat_type': '8x+', 'age_category': 'master', 'gender_category': 'women', 'distance': 21},
        {'race_id': 'SM35', 'display_order': 49, 'short_name': 'MM8X+', 'name': 'MEN-MASTER-OCTUPLE SCULL WITH COXSWAIN', 'event_type': '21km',
         'boat_type': '8x+', 'age_category': 'master', 'gender_category': 'men', 'distance': 21},
        {'race_id': 'SM34', 'display_order': 48, 'short_name': 'MX8X+', 'name': 'MIXED-GENDER-MASTER-OCTUPLE SCULL WITH COXSWAIN', 'event_type': '21km',
         'boat_type': '8x+', 'age_category': 'master', 'gender_category': 'mixed', 'distance': 21},
        
        # Coxed sweep four (1 race)
        {'race_id': 'SM06', 'display_order': 20, 'short_name': 'MM4+', 'name': 'MEN-MASTER-COXED SWEEP FOUR', 'event_type': '21km',
         'boat_type': '4+', 'age_category': 'master', 'gender_category': 'men', 'distance': 21},
        
        # Quad scull without coxswain (3 races)
        {'race_id': 'SM14', 'display_order': 28, 'short_name': 'MW4X-', 'name': 'WOMEN-MASTER-QUAD SCULL WITHOUT COXSWAIN', 'event_type': '21km',
         'boat_type': '4x-', 'age_category': 'master', 'gender_category': 'women', 'distance': 21},
        {'race_id': 'SM17', 'display_order': 31, 'short_name': 'MM4X-', 'name': 'MEN-MASTER-QUAD SCULL WITHOUT COXSWAIN', 'event_type': '21km',
         'boat_type': '4x-', 'age_category': 'master', 'gender_category': 'men', 'distance': 21},
        {'race_id': 'SM15', 'display_order': 29, 'short_name': 'MX4X-', 'name': 'MIXED-GENDER-MASTER-QUAD SCULL WITHOUT COXSWAIN', 'event_type': '21km',
         'boat_type': '4x-', 'age_category': 'master', 'gender_category': 'mixed', 'distance': 21},
        
        # Sweep four without coxswain (2 races)
        {'race_id': 'SM16', 'display_order': 30, 'short_name': 'MM4-', 'name': 'MEN-MASTER-SWEEP FOUR WITHOUT COXSWAIN', 'event_type': '21km',
         'boat_type': '4-', 'age_category': 'master', 'gender_category': 'men', 'distance': 21},
        {'race_id': 'SM13', 'display_order': 27, 'short_name': 'MW4-', 'name': 'WOMEN-MASTER-SWEEP FOUR WITHOUT COXSWAIN', 'event_type': '21km',
         'boat_type': '4-', 'age_category': 'master', 'gender_category': 'women', 'distance': 21},
        
        # Sweep eight with coxswain (3 races)
        {'race_id': 'SM32', 'display_order': 46, 'short_name': 'MM8+', 'name': 'MEN-MASTER-SWEEP EIGHT WITH COXSWAIN', 'event_type': '21km',
         'boat_type': '8+', 'age_category': 'master', 'gender_category': 'men', 'distance': 21},
        {'race_id': 'SM30', 'display_order': 44, 'short_name': 'MW8+', 'name': 'WOMEN-MASTER-SWEEP EIGHT WITH COXSWAIN', 'event_type': '21km',
         'boat_type': '8+', 'age_category': 'master', 'gender_category': 'women', 'distance': 21},
        {'race_id': 'SM31', 'display_order': 45, 'short_name': 'MX8+', 'name': 'MIXED-GENDER-MASTER-SWEEP EIGHT WITH COXSWAIN', 'event_type': '21km',
         'boat_type': '8+', 'age_category': 'master', 'gender_category': 'mixed', 'distance': 21},
    ]
    
    # Insert all races
    all_races = marathon_races + semi_marathon_races
    
    for race in all_races:
        race_item = {
            'PK': 'RACE',
            'SK': race['race_id'],
            'GSI2PK': f"{race['event_type']}#{race['boat_type']}",
            'GSI2SK': f"{race['age_category']}#{race['gender_category']}",
            **race,
            'created_at': datetime.utcnow().isoformat() + 'Z',
        }
        
        try:
            table.put_item(
                Item=race_item,
                ConditionExpression='attribute_not_exists(PK)'
            )
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            # Race already exists, skip
            pass
    
    print(f"Initialized {len(all_races)} race definitions (14 marathon + {len(semi_marathon_races)} semi-marathon)")


def initialize_rowing_clubs(table):
    """Initialize rowing clubs from JSON file"""
    # Load clubs data from JSON file (deployed with Lambda)
    clubs_file = Path(__file__).parent / 'rowing_clubs_detailed.json'
    
    if not clubs_file.exists():
        print(f"Warning: rowing_clubs_detailed.json not found at {clubs_file}")
        return
    
    with open(clubs_file, 'r', encoding='utf-8') as f:
        clubs_data = json.load(f)
    
    print(f"Loading {len(clubs_data)} rowing clubs...")
    
    # Track structure_numbers to handle duplicates
    structure_number_counts = {}
    clubs_added = 0
    clubs_skipped = 0
    
    for idx, club in enumerate(clubs_data):
        # Use structure_number as base for unique identifier
        structure_number = club.get('structure_number', '')
        
        if not structure_number:
            # Create a unique ID from name for clubs without structure_number
            club_id = club['name'].lower().replace(' ', '-').replace("'", '').replace('–', '-')
            unique_id = f"UNKNOWN-{club_id}"
        else:
            # Handle duplicate structure_numbers by appending a counter
            if structure_number in structure_number_counts:
                structure_number_counts[structure_number] += 1
                unique_id = f"{structure_number}-{structure_number_counts[structure_number]}"
            else:
                structure_number_counts[structure_number] = 0
                unique_id = structure_number
        
        club_item = {
            'PK': 'CLUB',
            'SK': unique_id,  # Use unique_id as sort key
            'club_id': unique_id,
            'name': club['name'],
            'url': club.get('url', ''),
            'structure_number': structure_number,
            'phone': club.get('phone', []),
            'management_team': club.get('management_team', []),
            'created_at': datetime.utcnow().isoformat() + 'Z',
        }
        
        try:
            table.put_item(
                Item=club_item,
                ConditionExpression='attribute_not_exists(PK) AND attribute_not_exists(SK)'
            )
            clubs_added += 1
        except table.meta.client.exceptions.ConditionalCheckFailedException:
            # Club already exists, skip
            clubs_skipped += 1
        except Exception as e:
            print(f"Error adding club {club['name']}: {str(e)}")
            clubs_skipped += 1
    
    print(f"Initialized {clubs_added} rowing clubs ({clubs_skipped} skipped)")


def send_response(event, context, response_status, response_data, physical_resource_id=None):
    """Send response to CloudFormation"""
    import urllib3
    import json
    
    # Use provided physical_resource_id or fall back to log stream name
    if not physical_resource_id:
        physical_resource_id = context.log_stream_name
    
    response_body = {
        'Status': response_status,
        'Reason': f'See CloudWatch Log Stream: {context.log_stream_name}',
        'PhysicalResourceId': physical_resource_id,
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Data': response_data
    }
    
    print(f'Response: {json.dumps(response_body)}')
    
    http = urllib3.PoolManager()
    try:
        response = http.request(
            'PUT',
            event['ResponseURL'],
            body=json.dumps(response_body).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        print(f'Status code: {response.status}')
    except Exception as e:
        print(f'send_response failed: {e}')
    
    return response_body
