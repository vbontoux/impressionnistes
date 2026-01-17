"""
Payment query utilities for DynamoDB
Shared query logic for payment-related Lambda functions
"""
import logging
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger()


def query_payments_by_team(db, team_manager_id, start_date=None, end_date=None, scan_forward=False):
    """
    Query all payments for a team manager
    
    Args:
        db: DynamoDB table resource
        team_manager_id: Team manager ID
        start_date: Optional ISO 8601 date string to filter from
        end_date: Optional ISO 8601 date string to filter to
        scan_forward: If True, sort ascending; if False, sort descending
    
    Returns:
        List of payment records
    """
    try:
        # Build query parameters
        query_params = {
            'KeyConditionExpression': 'PK = :pk AND begins_with(SK, :sk_prefix)',
            'ExpressionAttributeValues': {
                ':pk': f'TEAM#{team_manager_id}',
                ':sk_prefix': 'PAYMENT#'
            },
            'ScanIndexForward': scan_forward
        }
        
        # Add date range filter if provided
        if start_date or end_date:
            filter_expressions = []
            
            if start_date:
                query_params['ExpressionAttributeValues'][':start_date'] = start_date
                filter_expressions.append('paid_at >= :start_date')
            
            if end_date:
                query_params['ExpressionAttributeValues'][':end_date'] = end_date
                filter_expressions.append('paid_at <= :end_date')
            
            if filter_expressions:
                query_params['FilterExpression'] = ' AND '.join(filter_expressions)
        
        # Execute query
        response = db.table.query(**query_params)
        payments = response.get('Items', [])
        
        logger.info(f"Found {len(payments)} payments for team manager {team_manager_id}")
        return payments
        
    except Exception as e:
        logger.error(f"Error querying payments: {str(e)}", exc_info=True)
        raise


def scan_all_payments(db, start_date=None, end_date=None):
    """
    Scan all payment records across all team managers (admin only)
    
    Args:
        db: DynamoDB table resource
        start_date: Optional ISO 8601 date string to filter from
        end_date: Optional ISO 8601 date string to filter to
    
    Returns:
        List of payment records
    """
    try:
        # Build scan parameters
        scan_params = {
            'FilterExpression': 'begins_with(SK, :sk_prefix)',
            'ExpressionAttributeValues': {
                ':sk_prefix': 'PAYMENT#'
            }
        }
        
        # Add date range filter if provided
        if start_date or end_date:
            filter_expressions = ['begins_with(SK, :sk_prefix)']
            
            if start_date:
                scan_params['ExpressionAttributeValues'][':start_date'] = start_date
                filter_expressions.append('paid_at >= :start_date')
            
            if end_date:
                scan_params['ExpressionAttributeValues'][':end_date'] = end_date
                filter_expressions.append('paid_at <= :end_date')
            
            scan_params['FilterExpression'] = ' AND '.join(filter_expressions)
        
        # Execute scan with pagination
        payments = []
        last_evaluated_key = None
        
        while True:
            if last_evaluated_key:
                scan_params['ExclusiveStartKey'] = last_evaluated_key
            
            response = db.table.scan(**scan_params)
            payments.extend(response.get('Items', []))
            
            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break
        
        logger.info(f"Scanned {len(payments)} total payments")
        return payments
        
    except Exception as e:
        logger.error(f"Error scanning payments: {str(e)}", exc_info=True)
        raise


def get_payment_by_id(db, team_manager_id, payment_id):
    """
    Get a single payment by ID
    
    Args:
        db: DynamoDB table resource
        team_manager_id: Team manager ID
        payment_id: Payment ID
    
    Returns:
        Payment record or None if not found
    """
    try:
        response = db.get_item(
            Key={
                'PK': f'TEAM#{team_manager_id}',
                'SK': f'PAYMENT#{payment_id}'
            }
        )
        
        return response.get('Item')
        
    except Exception as e:
        logger.error(f"Error getting payment: {str(e)}", exc_info=True)
        raise


def query_unpaid_boats(db, team_manager_id):
    """
    Query all unpaid boats for a team manager (status='complete')
    
    Args:
        db: DynamoDB table resource
        team_manager_id: Team manager ID
    
    Returns:
        List of boat registration records
    """
    try:
        response = db.table.query(
            KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
            FilterExpression='registration_status = :status',
            ExpressionAttributeValues={
                ':pk': f'TEAM#{team_manager_id}',
                ':sk_prefix': 'BOAT#',
                ':status': 'complete'
            }
        )
        
        boats = response.get('Items', [])
        logger.info(f"Found {len(boats)} unpaid boats for team manager {team_manager_id}")
        return boats
        
    except Exception as e:
        logger.error(f"Error querying unpaid boats: {str(e)}", exc_info=True)
        raise
