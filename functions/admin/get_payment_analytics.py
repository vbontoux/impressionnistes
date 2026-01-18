"""
Lambda function for payment analytics (admin only)
Provides comprehensive payment statistics and trends
"""
import json
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from collections import defaultdict

# Import from Lambda layer
from responses import (
    success_response,
    validation_error,
    internal_error,
    handle_exceptions
)
from database import get_db_client
from auth_utils import require_admin
from access_control import require_permission
from configuration import ConfigurationManager
from payment_queries import query_unpaid_boats

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
@require_permission('view_payment_analytics')
def lambda_handler(event, context):
    """
    Get payment analytics and trends (admin only)
    
    Query parameters:
        - start_date: Optional ISO 8601 timestamp to filter from
        - end_date: Optional ISO 8601 timestamp to filter to
        - group_by: Optional grouping ('day', 'week', 'month', default: 'day')
    
    Returns:
        {
            "total_revenue": 5000.00,
            "total_payments": 50,
            "total_boats_paid": 100,
            "total_team_managers": 20,
            "outstanding_balance": 500.00,
            "outstanding_boats": 10,
            "payment_timeline": [
                {
                    "date": "2026-01-15",
                    "amount": 500.00,
                    "payment_count": 5,
                    "boat_count": 10
                }
            ],
            "top_team_managers": [
                {
                    "team_manager_id": "user-id",
                    "name": "Club Name",
                    "total_paid": 500.00,
                    "payment_count": 5,
                    "boat_count": 10
                }
            ]
        }
    """
    logger.info("Get payment analytics request (admin)")
    
    # Get query parameters
    query_params = event.get('queryStringParameters') or {}
    start_date = query_params.get('start_date')
    end_date = query_params.get('end_date')
    group_by = query_params.get('group_by', 'day').lower()
    
    # Validate group_by
    valid_groupings = ['day', 'week', 'month']
    if group_by not in valid_groupings:
        return validation_error({
            'group_by': f'Grouping must be one of: {", ".join(valid_groupings)}'
        })
    
    # Get database client
    db = get_db_client()
    
    try:
        # Scan all PAYMENT# records
        all_payments = []
        scan_kwargs = {
            'FilterExpression': 'begins_with(SK, :payment_prefix)',
            'ExpressionAttributeValues': {
                ':payment_prefix': 'PAYMENT#'
            }
        }
        
        while True:
            response = db.table.scan(**scan_kwargs)
            all_payments.extend(response.get('Items', []))
            if 'LastEvaluatedKey' not in response:
                break
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
        
        logger.info(f"Scanned {len(all_payments)} total payments")
        
        # Apply date filters
        filtered_payments = all_payments
        if start_date or end_date:
            filtered_payments = []
            for payment in all_payments:
                paid_at = payment.get('paid_at', '')
                if start_date and paid_at < start_date:
                    continue
                if end_date and paid_at > end_date:
                    continue
                filtered_payments.append(payment)
        
        # Calculate total revenue and statistics
        total_revenue = sum(float(p.get('amount', 0)) for p in filtered_payments)
        total_payments = len(filtered_payments)
        total_boats_paid = sum(len(p.get('boat_registration_ids', [])) for p in filtered_payments)
        
        # Count unique team managers
        unique_team_managers = set(p.get('team_manager_id') for p in filtered_payments if p.get('team_manager_id'))
        total_team_managers = len(unique_team_managers)
        
        # Calculate outstanding balance (all unpaid boats across all teams)
        config_manager = ConfigurationManager()
        pricing_config = config_manager.get_pricing_config()
        
        # Scan all unpaid boats
        all_boats = []
        scan_kwargs = {
            'FilterExpression': 'begins_with(SK, :boat_prefix) AND registration_status = :status',
            'ExpressionAttributeValues': {
                ':boat_prefix': 'BOAT#',
                ':status': 'complete'
            }
        }
        
        while True:
            response = db.table.scan(**scan_kwargs)
            all_boats.extend(response.get('Items', []))
            if 'LastEvaluatedKey' not in response:
                break
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
        
        # Calculate outstanding balance with dynamic pricing recalculation
        outstanding_balance = Decimal('0')
        outstanding_boats = 0
        
        # Group boats by team manager for efficient crew member lookup
        boats_by_team = defaultdict(list)
        for boat in all_boats:
            team_id = boat.get('PK', '').replace('TEAM#', '')
            if team_id:
                boats_by_team[team_id].append(boat)
        
        # Calculate outstanding for each team
        from pricing import calculate_boat_pricing
        
        for team_id, team_boats in boats_by_team.items():
            # Get all crew members for this team
            try:
                crew_response = db.table.query(
                    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
                    ExpressionAttributeValues={
                        ':pk': f'TEAM#{team_id}',
                        ':sk': 'CREW#'
                    }
                )
                team_crew_members = crew_response.get('Items', [])
            except Exception as e:
                logger.warning(f"Failed to get crew for team {team_id}: {e}")
                team_crew_members = []
            
            # Calculate pricing for each boat
            for boat in team_boats:
                try:
                    # Use locked pricing if available
                    if 'locked_pricing' in boat and boat['locked_pricing']:
                        amount = Decimal(str(boat['locked_pricing'].get('total', 0)))
                    # Otherwise recalculate dynamically
                    elif team_crew_members:
                        pricing = calculate_boat_pricing(boat, team_crew_members, pricing_config)
                        amount = pricing.get('total', Decimal('0'))
                    # Fallback to stored pricing (may be stale)
                    elif boat.get('pricing', {}).get('total'):
                        amount = Decimal(str(boat['pricing']['total']))
                    else:
                        amount = Decimal('0')
                    
                    outstanding_balance += amount
                    outstanding_boats += 1
                except Exception as e:
                    logger.warning(f"Failed to calculate pricing for boat {boat.get('boat_registration_id')}: {e}")
                    continue
        
        # Group payments by time period
        payment_timeline = defaultdict(lambda: {
            'amount': 0.0,
            'payment_count': 0,
            'boat_count': 0
        })
        
        for payment in filtered_payments:
            paid_at = payment.get('paid_at', '')
            if not paid_at:
                continue
            
            # Parse date
            try:
                dt = datetime.fromisoformat(paid_at.replace('Z', '+00:00'))
            except:
                continue
            
            # Group by period
            if group_by == 'day':
                period_key = dt.strftime('%Y-%m-%d')
            elif group_by == 'week':
                # ISO week format
                period_key = dt.strftime('%Y-W%W')
            elif group_by == 'month':
                period_key = dt.strftime('%Y-%m')
            
            payment_timeline[period_key]['amount'] += float(payment.get('amount', 0))
            payment_timeline[period_key]['payment_count'] += 1
            payment_timeline[period_key]['boat_count'] += len(payment.get('boat_registration_ids', []))
        
        # Convert timeline to sorted list
        timeline_list = [
            {
                'date': date,
                'amount': data['amount'],
                'payment_count': data['payment_count'],
                'boat_count': data['boat_count']
            }
            for date, data in sorted(payment_timeline.items())
        ]
        
        # Rank team managers by total paid
        team_manager_stats = defaultdict(lambda: {
            'total_paid': 0.0,
            'payment_count': 0,
            'boat_count': 0,
            'name': '',
            'club': ''
        })
        
        for payment in filtered_payments:
            tm_id = payment.get('team_manager_id')
            if not tm_id:
                continue
            
            team_manager_stats[tm_id]['total_paid'] += float(payment.get('amount', 0))
            team_manager_stats[tm_id]['payment_count'] += 1
            team_manager_stats[tm_id]['boat_count'] += len(payment.get('boat_registration_ids', []))
        
        # Enrich with team manager info
        for tm_id in team_manager_stats.keys():
            profile = db.get_item(f'USER#{tm_id}', 'PROFILE')
            if profile:
                team_manager_stats[tm_id]['name'] = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
                team_manager_stats[tm_id]['club'] = profile.get('club_affiliation', '')
        
        # Sort by total paid (descending) and take top 10
        top_team_managers = sorted(
            [
                {
                    'team_manager_id': tm_id,
                    'name': stats['name'],
                    'club': stats['club'],
                    'total_paid': stats['total_paid'],
                    'payment_count': stats['payment_count'],
                    'boat_count': stats['boat_count']
                }
                for tm_id, stats in team_manager_stats.items()
            ],
            key=lambda x: x['total_paid'],
            reverse=True
        )[:10]
        
        logger.info(f"Analytics: revenue={total_revenue}, payments={total_payments}, outstanding={float(outstanding_balance)}")
        
        # Return success response
        return success_response(data={
            'total_revenue': float(total_revenue),
            'total_payments': total_payments,
            'total_boats_paid': total_boats_paid,
            'total_team_managers': total_team_managers,
            'outstanding_balance': float(outstanding_balance),
            'outstanding_boats': outstanding_boats,
            'currency': 'EUR',
            'payment_timeline': timeline_list,
            'top_team_managers': top_team_managers
        })
        
    except Exception as e:
        logger.error(f"Failed to get payment analytics: {str(e)}", exc_info=True)
        return internal_error(message='Failed to retrieve payment analytics')
