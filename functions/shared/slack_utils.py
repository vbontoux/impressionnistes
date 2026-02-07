"""
Slack Notification Utility for sending notifications via Slack webhooks
Centralized Slack notification logic to be reused across Lambda functions
"""
import json
import logging
from typing import Optional, Dict, Any
from urllib import request
from urllib.error import URLError, HTTPError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Slack webhook URLs (loaded from configuration)
_slack_webhook_admin = None
_slack_webhook_devops = None


def set_webhook_urls(admin_webhook: Optional[str] = None, devops_webhook: Optional[str] = None):
    """
    Set Slack webhook URLs
    
    Args:
        admin_webhook: Webhook URL for admin notifications
        devops_webhook: Webhook URL for devops/error notifications
    """
    global _slack_webhook_admin, _slack_webhook_devops
    _slack_webhook_admin = admin_webhook
    _slack_webhook_devops = devops_webhook


def send_slack_message(webhook_url: str, message: Dict[str, Any]) -> bool:
    """
    Send a message to Slack via webhook
    
    Args:
        webhook_url: Slack webhook URL
        message: Message payload (Slack Block Kit format)
    
    Returns:
        True if successful, False otherwise
    """
    if not webhook_url:
        logger.warning("Slack webhook URL not configured - skipping notification")
        return False
    
    try:
        payload = json.dumps(message).encode('utf-8')
        req = request.Request(
            webhook_url,
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        with request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                logger.info("Slack notification sent successfully")
                return True
            else:
                logger.error(f"Slack notification failed with status: {response.status}")
                return False
                
    except HTTPError as e:
        logger.error(f"HTTP error sending Slack notification: {e.code} - {e.reason}")
        return False
    except URLError as e:
        logger.error(f"URL error sending Slack notification: {e.reason}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending Slack notification: {str(e)}")
        return False


def notify_new_user_registration(
    user_name: str,
    user_email: str,
    club_name: Optional[str] = None,
    environment: str = 'dev'
) -> bool:
    """
    Send notification when a new team manager registers
    
    Args:
        user_name: Name of the new user
        user_email: Email of the new user
        club_name: Name of the rowing club (optional)
        environment: Environment (dev/prod)
    
    Returns:
        True if successful, False otherwise
    """
    if not _slack_webhook_admin:
        logger.warning("Admin webhook not configured - skipping notification")
        return False
    
    # Build club info
    club_info = f" from *{club_name}*" if club_name else ""
    
    # Environment emoji
    env_emoji = "🟢" if environment == "prod" else "🔵"
    
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{env_emoji} New Team Manager Registration",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Name:*\n{user_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Email:*\n{user_email}"
                    }
                ]
            }
        ]
    }
    
    # Add club info if available
    if club_name:
        message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Club:* {club_name}"
            }
        })
    
    # Add environment info
    message["blocks"].append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"Environment: *{environment}*"
            }
        ]
    })
    
    return send_slack_message(_slack_webhook_admin, message)


def notify_payment_completed(
    user_name: str,
    user_email: str,
    amount: float,
    currency: str,
    boat_count: int,
    rental_count: int,
    payment_id: str,
    environment: str = 'dev'
) -> bool:
    """
    Send notification when a payment is completed successfully
    
    Args:
        user_name: Name of the team manager
        user_email: Email of the team manager
        amount: Payment amount
        currency: Currency code (e.g., 'EUR')
        boat_count: Number of boats registered
        rental_count: Number of rental boats
        payment_id: Stripe payment ID
        environment: Environment (dev/prod)
    
    Returns:
        True if successful, False otherwise
    """
    if not _slack_webhook_admin:
        logger.warning("Admin webhook not configured - skipping notification")
        return False
    
    # Environment emoji
    env_emoji = "🟢" if environment == "prod" else "🔵"
    
    # Format amount
    amount_str = f"{amount:.2f} {currency}"
    
    # Build items summary
    items = []
    if boat_count > 0:
        items.append(f"{boat_count} boat{'s' if boat_count > 1 else ''}")
    if rental_count > 0:
        items.append(f"{rental_count} rental{'s' if rental_count > 1 else ''}")
    items_str = " + ".join(items) if items else "No items"
    
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{env_emoji} 💰 Payment Completed",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Team Manager:*\n{user_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Amount:*\n{amount_str}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Email:*\n{user_email}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Items:*\n{items_str}"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Payment ID: `{payment_id}` | Environment: *{environment}*"
                    }
                ]
            }
        ]
    }
    
    return send_slack_message(_slack_webhook_admin, message)


def notify_payment_failed(
    user_name: str,
    user_email: str,
    amount: float,
    currency: str,
    error_message: str,
    payment_id: Optional[str] = None,
    environment: str = 'dev'
) -> bool:
    """
    Send notification when a payment fails
    
    Args:
        user_name: Name of the team manager
        user_email: Email of the team manager
        amount: Payment amount attempted
        currency: Currency code (e.g., 'EUR')
        error_message: Error message from Stripe
        payment_id: Stripe payment ID (if available)
        environment: Environment (dev/prod)
    
    Returns:
        True if successful, False otherwise
    """
    if not _slack_webhook_admin:
        logger.warning("Admin webhook not configured - skipping notification")
        return False
    
    # Environment emoji
    env_emoji = "🟢" if environment == "prod" else "🔵"
    
    # Format amount
    amount_str = f"{amount:.2f} {currency}"
    
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{env_emoji} ❌ Payment Failed",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Team Manager:*\n{user_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Amount:*\n{amount_str}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Email:*\n{user_email}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Error:*\n{error_message}"
                    }
                ]
            }
        ]
    }
    
    # Add payment ID if available
    context_text = f"Environment: *{environment}*"
    if payment_id:
        context_text = f"Payment ID: `{payment_id}` | {context_text}"
    
    message["blocks"].append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": context_text
            }
        ]
    })
    
    return send_slack_message(_slack_webhook_admin, message)


def notify_new_boat_registration(
    boat_number: Optional[str],
    event_type: str,
    boat_type: str,
    race_name: Optional[str],
    team_manager_name: str,
    team_manager_email: str,
    club_affiliation: str,
    registration_status: str,
    boat_request_enabled: bool,
    boat_request_comment: Optional[str],
    environment: str = 'dev'
) -> bool:
    """
    Send notification when a new boat registration is created
    
    Args:
        boat_number: Boat number (if race assigned)
        event_type: Event type (21km or 42km)
        boat_type: Boat type (skiff, 4-, 4+, 8+)
        race_name: Race name (if assigned)
        team_manager_name: Name of the team manager
        team_manager_email: Email of the team manager
        club_affiliation: Rowing club
        registration_status: Registration status (incomplete/complete)
        boat_request_enabled: Whether team requested a boat from organizers
        boat_request_comment: Comment about boat request (if any)
        environment: Environment (dev/prod)
    
    Returns:
        True if successful, False otherwise
    """
    if not _slack_webhook_admin:
        logger.warning("Admin webhook not configured - skipping notification")
        return False
    
    # Environment emoji
    env_emoji = "🟢" if environment == "prod" else "🔵"
    
    # Build boat identifier
    boat_identifier = boat_number if boat_number else "No race assigned yet"
    
    # Build race info
    race_info = race_name if race_name else "Not assigned"
    
    # Status emoji
    status_emoji = "✅" if registration_status == "complete" else "⏳"
    
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{env_emoji} 🚣 New Boat Registration",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Boat:*\n{boat_identifier}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Event:*\n{event_type}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Boat Type:*\n{boat_type}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Race:*\n{race_info}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Team Manager:*\n{team_manager_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Club:*\n{club_affiliation}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{status_emoji} {registration_status.title()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Email:*\n{team_manager_email}"
                    }
                ]
            }
        ]
    }
    
    # Add boat request info if enabled
    if boat_request_enabled:
        boat_request_text = "🚤 *Boat Request:* Team needs a boat from organizers"
        if boat_request_comment:
            # Truncate comment if too long for Slack
            comment = boat_request_comment[:200] + "..." if len(boat_request_comment) > 200 else boat_request_comment
            boat_request_text += f"\n_{comment}_"
        
        message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": boat_request_text
            }
        })
    
    # Add environment info
    message["blocks"].append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"Environment: *{environment}*"
            }
        ]
    })
    
    return send_slack_message(_slack_webhook_admin, message)


def notify_system_error(
    error_type: str,
    error_message: str,
    function_name: str,
    additional_context: Optional[Dict[str, Any]] = None,
    environment: str = 'dev'
) -> bool:
    """
    Send notification for system errors (for devops team)
    
    Args:
        error_type: Type of error (e.g., 'DatabaseError', 'APIError')
        error_message: Error message
        function_name: Name of the Lambda function
        additional_context: Additional context information
        environment: Environment (dev/prod)
    
    Returns:
        True if successful, False otherwise
    """
    if not _slack_webhook_devops:
        logger.warning("Devops webhook not configured - skipping notification")
        return False
    
    # Environment emoji
    env_emoji = "🟢" if environment == "prod" else "🔵"
    
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{env_emoji} 🚨 System Error",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Error Type:*\n{error_type}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Function:*\n{function_name}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error Message:*\n```{error_message}```"
                }
            }
        ]
    }
    
    # Add additional context if provided
    if additional_context:
        context_items = [f"*{k}:* {v}" for k, v in additional_context.items()]
        message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\n".join(context_items)
            }
        })
    
    # Add environment info
    message["blocks"].append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"Environment: *{environment}*"
            }
        ]
    })
    
    return send_slack_message(_slack_webhook_devops, message)
