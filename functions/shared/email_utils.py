"""
Email Utility for sending notifications via AWS SES
Centralized email sending logic to be reused across Lambda functions
"""
import boto3
import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# SES client (initialized once)
_ses_client = None

# Default sender email (can be overridden by configuration)
DEFAULT_SENDER_EMAIL = 'impressionnistes@aviron-rcpm.fr'


def get_ses_client():
    """Get or create SES client"""
    global _ses_client
    if _ses_client is None:
        _ses_client = boto3.client('ses', region_name='eu-west-1')  # Paris region
    return _ses_client


def get_sender_email() -> str:
    """
    Get sender email from configuration or use default
    
    Returns:
        Sender email address
    """
    # TODO: In future, fetch from ConfigurationManager if needed
    # For now, use the default
    return DEFAULT_SENDER_EMAIL


def send_email(
    recipient_email: str,
    subject: str,
    html_body: str,
    text_body: str,
    sender_email: Optional[str] = None
) -> bool:
    """
    Generic email sending function
    Use this for custom email content
    
    Args:
        recipient_email: Email address of the recipient
        subject: Email subject line
        html_body: HTML version of the email body
        text_body: Plain text version of the email body
        sender_email: Optional sender email (uses default if not provided)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        ses = get_ses_client()
        
        # Use provided sender or default
        from_email = sender_email or get_sender_email()
        
        response = ses.send_email(
            Source=from_email,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                    'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                }
            }
        )
        
        logger.info(f"Email sent to {recipient_email}, Subject: {subject}, MessageId: {response['MessageId']}")
        return True
        
    except ClientError as e:
        logger.error(f"Failed to send email: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {str(e)}")
        return False


def send_payment_confirmation_email(
    recipient_email: str,
    team_manager_name: str,
    payment_details: Dict[str, Any],
    boat_registrations: List[Dict[str, Any]],
    rental_boats: List[Dict[str, Any]],
    receipt_url: Optional[str] = None,
    sender_email: Optional[str] = None
) -> bool:
    """
    Send payment confirmation email to team manager
    
    Args:
        recipient_email: Email address of the team manager
        team_manager_name: Name of the team manager
        payment_details: Dict with 'amount', 'currency', 'payment_id', 'paid_at'
        boat_registrations: List of boat registration details
        rental_boats: List of rental boat details
        receipt_url: Optional Stripe receipt URL
        sender_email: Optional sender email (uses default if not provided)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Build email content
        subject = "Confirmation de paiement - Course des Impressionnistes"
        
        # Build boat list
        boat_list_html = ""
        if boat_registrations:
            boat_list_html += "<h3>Inscriptions d'équipages :</h3><ul>"
            for boat in boat_registrations:
                boat_type = boat.get('boat_type', 'N/A')
                crew_name = boat.get('crew_name', 'N/A')
                race = boat.get('selected_race', {})
                race_name = race.get('race_name', 'N/A') if isinstance(race, dict) else 'N/A'
                boat_list_html += f"<li><strong>{boat_type}</strong> - {crew_name} - Course: {race_name}</li>"
            boat_list_html += "</ul>"
        
        if rental_boats:
            boat_list_html += "<h3>Locations de bateaux :</h3><ul>"
            for rental in rental_boats:
                boat_type = rental.get('boat_type', 'N/A')
                boat_name = rental.get('boat_name', 'Bateau de location')
                boat_list_html += f"<li><strong>{boat_type}</strong> - {boat_name}</li>"
            boat_list_html += "</ul>"
        
        # Format amount
        amount = payment_details.get('amount', 0)
        currency = payment_details.get('currency', 'EUR')
        amount_str = f"{amount:.2f} {currency}"
        
        # Receipt link
        receipt_link = ""
        if receipt_url:
            receipt_link = f'<p><a href="{receipt_url}" style="color: #0066cc;">Télécharger le reçu Stripe</a></p>'
        
        # HTML body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0066cc; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .amount {{ font-size: 24px; font-weight: bold; color: #0066cc; }}
                ul {{ padding-left: 20px; }}
                li {{ margin-bottom: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Paiement confirmé ✓</h1>
                </div>
                <div class="content">
                    <p>Bonjour {team_manager_name},</p>
                    
                    <p>Votre paiement pour la Course des Impressionnistes a été confirmé avec succès.</p>
                    
                    <p class="amount">Montant payé : {amount_str}</p>
                    
                    {boat_list_html}
                    
                    <p><strong>Numéro de paiement :</strong> {payment_details.get('payment_id', 'N/A')}</p>
                    
                    {receipt_link}
                    
                    <p>Vos inscriptions sont maintenant confirmées. Vous pouvez consulter vos bateaux inscrits dans votre espace personnel.</p>
                    
                    <p>À bientôt sur l'eau !</p>
                    
                    <p>L'équipe de la Course des Impressionnistes</p>
                </div>
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement. Merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
Paiement confirmé - Course des Impressionnistes

Bonjour {team_manager_name},

Votre paiement pour la Course des Impressionnistes a été confirmé avec succès.

Montant payé : {amount_str}

Numéro de paiement : {payment_details.get('payment_id', 'N/A')}

Vos inscriptions sont maintenant confirmées.

À bientôt sur l'eau !

L'équipe de la Course des Impressionnistes
        """
        
        # Send using generic function
        return send_email(
            recipient_email=recipient_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            sender_email=sender_email
        )
        
    except Exception as e:
        logger.error(f"Error building payment confirmation email: {str(e)}")
        return False


def send_registration_confirmation_email(
    recipient_email: str,
    team_manager_name: str,
    boat_details: Dict[str, Any],
    sender_email: Optional[str] = None
) -> bool:
    """
    Send registration confirmation email when a boat is registered
    
    Args:
        recipient_email: Email address of the team manager
        team_manager_name: Name of the team manager
        boat_details: Dict with boat registration details
        sender_email: Optional sender email (uses default if not provided)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        boat_type = boat_details.get('boat_type', 'N/A')
        crew_name = boat_details.get('crew_name', 'N/A')
        race = boat_details.get('selected_race', {})
        race_name = race.get('race_name', 'N/A') if isinstance(race, dict) else 'N/A'
        
        subject = "Inscription enregistrée - Course des Impressionnistes"
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0066cc; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Inscription enregistrée</h1>
                </div>
                <div class="content">
                    <p>Bonjour {team_manager_name},</p>
                    
                    <p>Votre inscription a été enregistrée avec succès :</p>
                    
                    <ul>
                        <li><strong>Type de bateau :</strong> {boat_type}</li>
                        <li><strong>Nom d'équipage :</strong> {crew_name}</li>
                        <li><strong>Course :</strong> {race_name}</li>
                    </ul>
                    
                    <p>N'oubliez pas de finaliser votre inscription en effectuant le paiement avant la date limite.</p>
                    
                    <p>À bientôt sur l'eau !</p>
                    
                    <p>L'équipe de la Course des Impressionnistes</p>
                </div>
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement. Merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
Inscription enregistrée - Course des Impressionnistes

Bonjour {team_manager_name},

Votre inscription a été enregistrée avec succès :

Type de bateau : {boat_type}
Nom d'équipage : {crew_name}
Course : {race_name}

N'oubliez pas de finaliser votre inscription en effectuant le paiement avant la date limite.

À bientôt sur l'eau !

L'équipe de la Course des Impressionnistes
        """
        
        return send_email(
            recipient_email=recipient_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            sender_email=sender_email
        )
        
    except Exception as e:
        logger.error(f"Unexpected error sending registration email: {str(e)}")
        return False


def send_race_reminder_email(
    recipient_email: str,
    team_manager_name: str,
    race_details: Dict[str, Any],
    boats: List[Dict[str, Any]],
    sender_email: Optional[str] = None
) -> bool:
    """
    Send reminder email before the race
    
    Args:
        recipient_email: Email address of the team manager
        team_manager_name: Name of the team manager
        race_details: Dict with race information (date, time, location)
        boats: List of registered boats
        sender_email: Optional sender email (uses default if not provided)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        race_date = race_details.get('date', 'N/A')
        race_time = race_details.get('time', 'N/A')
        race_location = race_details.get('location', 'N/A')
        
        boat_list_html = "<ul>"
        for boat in boats:
            boat_type = boat.get('boat_type', 'N/A')
            crew_name = boat.get('crew_name', 'N/A')
            boat_list_html += f"<li><strong>{boat_type}</strong> - {crew_name}</li>"
        boat_list_html += "</ul>"
        
        subject = "Rappel - Course des Impressionnistes"
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0066cc; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .highlight {{ background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Rappel - Course à venir</h1>
                </div>
                <div class="content">
                    <p>Bonjour {team_manager_name},</p>
                    
                    <p>La Course des Impressionnistes approche !</p>
                    
                    <div class="highlight">
                        <p><strong>Date :</strong> {race_date}</p>
                        <p><strong>Heure :</strong> {race_time}</p>
                        <p><strong>Lieu :</strong> {race_location}</p>
                    </div>
                    
                    <h3>Vos bateaux inscrits :</h3>
                    {boat_list_html}
                    
                    <p>N'oubliez pas d'arriver au moins 30 minutes avant le départ pour l'échauffement.</p>
                    
                    <p>Bonne course !</p>
                    
                    <p>L'équipe de la Course des Impressionnistes</p>
                </div>
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement. Merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
Rappel - Course des Impressionnistes

Bonjour {team_manager_name},

La Course des Impressionnistes approche !

Date : {race_date}
Heure : {race_time}
Lieu : {race_location}

Vos bateaux inscrits :
{chr(10).join([f"- {b.get('boat_type', 'N/A')} - {b.get('crew_name', 'N/A')}" for b in boats])}

N'oubliez pas d'arriver au moins 30 minutes avant le départ pour l'échauffement.

Bonne course !

L'équipe de la Course des Impressionnistes
        """
        
        return send_email(
            recipient_email=recipient_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            sender_email=sender_email
        )
        
    except Exception as e:
        logger.error(f"Unexpected error sending reminder email: {str(e)}")
        return False


def send_rental_confirmation_email(
    recipient_email: str,
    team_manager_name: str,
    rental_details: Dict[str, Any],
    sender_email: Optional[str] = None
) -> bool:
    """
    Send rental boat confirmation email
    
    Args:
        recipient_email: Email address of the team manager
        team_manager_name: Name of the team manager
        rental_details: Dict with rental boat details
        sender_email: Optional sender email (uses default if not provided)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        boat_type = rental_details.get('boat_type', 'N/A')
        boat_name = rental_details.get('boat_name', 'Bateau de location')
        status = rental_details.get('status', 'pending')
        
        subject = "Confirmation de location - Course des Impressionnistes"
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0066cc; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Location confirmée</h1>
                </div>
                <div class="content">
                    <p>Bonjour {team_manager_name},</p>
                    
                    <p>Votre demande de location a été confirmée :</p>
                    
                    <ul>
                        <li><strong>Type de bateau :</strong> {boat_type}</li>
                        <li><strong>Nom :</strong> {boat_name}</li>
                        <li><strong>Statut :</strong> {status}</li>
                    </ul>
                    
                    <p>Le bateau sera disponible le jour de la course. Merci de vous présenter au stand de location.</p>
                    
                    <p>À bientôt sur l'eau !</p>
                    
                    <p>L'équipe de la Course des Impressionnistes</p>
                </div>
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement. Merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
Location confirmée - Course des Impressionnistes

Bonjour {team_manager_name},

Votre demande de location a été confirmée :

Type de bateau : {boat_type}
Nom : {boat_name}
Statut : {status}

Le bateau sera disponible le jour de la course. Merci de vous présenter au stand de location.

À bientôt sur l'eau !

L'équipe de la Course des Impressionnistes
        """
        
        return send_email(
            recipient_email=recipient_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            sender_email=sender_email
        )
        
    except Exception as e:
        logger.error(f"Unexpected error sending rental email: {str(e)}")
        return False


def send_test_email(recipient_email: str, sender_email: Optional[str] = None) -> bool:
    """
    Send a test email to verify SES configuration
    
    Args:
        recipient_email: Email address to send test to
        sender_email: Optional sender email address (uses default if not provided)
    
    Returns:
        True if successful, False otherwise
    """
    subject = 'Test Email - Course des Impressionnistes'
    html_body = '<p>This is a test email from the Course des Impressionnistes registration system.</p>'
    text_body = 'This is a test email from the Course des Impressionnistes registration system.'
    
    return send_email(
        recipient_email=recipient_email,
        subject=subject,
        html_body=html_body,
        text_body=text_body,
        sender_email=sender_email
    )
