"""
Lambda function for generating invoices for payments
Team managers can download invoices for their payments
"""
import json
import logging
from datetime import datetime
from decimal import Decimal

# Import from Lambda layer
from responses import (
    success_response,
    not_found_error,
    internal_error,
    handle_exceptions
)
from database import get_db_client
from auth_utils import get_user_from_event, require_team_manager_or_admin_override
from access_control import require_permission

# PDF generation commented out for now - using text instead
# # ReportLab imports
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import cm
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# PDF generation commented out - using text invoice instead
# def generate_pdf_invoice(payment, team_manager, boats):
#     """
#     Generate PDF invoice for a payment
#     
#     Args:
#         payment: Payment record dict
#         team_manager: Team manager profile dict
#         boats: List of boat registration dicts
#     
#     Returns:
#         bytes: PDF content
#     """
#     # Create PDF buffer
#     buffer = BytesIO()
#     
#     # Create PDF document
#     doc = SimpleDocTemplate(
#         buffer,
#         pagesize=A4,
#         rightMargin=2*cm,
#         leftMargin=2*cm,
#         topMargin=2*cm,
#         bottomMargin=2*cm
#     )
#     
#     # Container for PDF elements
#     elements = []
#     
#     # Get styles
#     styles = getSampleStyleSheet()
#     
#     # Custom styles
#     title_style = ParagraphStyle(
#         'CustomTitle',
#         parent=styles['Heading1'],
#         fontSize=24,
#         textColor=colors.HexColor('#1a1a1a'),
#         spaceAfter=30,
#         alignment=TA_CENTER
#     )
#     
#     heading_style = ParagraphStyle(
#         'CustomHeading',
#         parent=styles['Heading2'],
#         fontSize=14,
#         textColor=colors.HexColor('#333333'),
#         spaceAfter=12,
#         spaceBefore=20
#     )
#     
#     normal_style = ParagraphStyle(
#         'CustomNormal',
#         parent=styles['Normal'],
#         fontSize=10,
#         textColor=colors.HexColor('#333333')
#     )
#     
#     # Title
#     title = Paragraph("FACTURE / INVOICE", title_style)
#     elements.append(title)
#     
#     # Event name
#     event_name = Paragraph(
#         "<b>Course des Impressionnistes</b>",
#         ParagraphStyle('EventName', parent=normal_style, fontSize=12, alignment=TA_CENTER)
#     )
#     elements.append(event_name)
#     elements.append(Spacer(1, 1*cm))
#     
#     # Payment information section
#     elements.append(Paragraph("Informations de paiement / Payment Information", heading_style))
#     
#     payment_date = datetime.fromisoformat(payment['paid_at'].replace('Z', '+00:00'))
#     formatted_date = payment_date.strftime('%d/%m/%Y %H:%M')
#     
#     payment_info = [
#         ['ID de paiement / Payment ID:', payment['payment_id']],
#         ['Date:', formatted_date],
#         ['Montant / Amount:', f"{float(payment['amount']):.2f} {payment['currency']}"],
#         ['Statut / Status:', payment['status'].capitalize()],
#     ]
#     
#     payment_table = Table(payment_info, colWidths=[6*cm, 10*cm])
#     payment_table.setStyle(TableStyle([
#         ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
#         ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
#         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#         ('LEFTPADDING', (0, 0), (-1, -1), 0),
#         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
#     ]))
#     elements.append(payment_table)
#     elements.append(Spacer(1, 0.5*cm))
#     
#     # Team manager information section
#     elements.append(Paragraph("Informations du club / Club Information", heading_style))
#     
#     tm_info = [
#         ['Nom / Name:', f"{team_manager.get('first_name', '')} {team_manager.get('last_name', '')}"],
#         ['Club:', team_manager.get('club_affiliation', 'N/A')],
#         ['Email:', team_manager.get('email', 'N/A')],
#     ]
#     
#     tm_table = Table(tm_info, colWidths=[6*cm, 10*cm])
#     tm_table.setStyle(TableStyle([
#         ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
#         ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
#         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#         ('LEFTPADDING', (0, 0), (-1, -1), 0),
#         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
#     ]))
#     elements.append(tm_table)
#     elements.append(Spacer(1, 0.5*cm))
#     
#     # Boats section
#     elements.append(Paragraph("Bateaux payés / Boats Paid", heading_style))
#     
#     boat_data = [['Type d\'événement / Event Type', 'Type de bateau / Boat Type', 'Montant / Amount']]
#     
#     for boat in boats:
#         event_type = boat.get('event_type', 'N/A')
#         boat_type = boat.get('boat_type', 'N/A')
#         
#         # Get amount from locked_pricing or pricing
#         amount = 0.0
#         if boat.get('locked_pricing') and boat['locked_pricing'].get('total'):
#             amount = float(boat['locked_pricing']['total'])
#         elif boat.get('pricing') and boat['pricing'].get('total'):
#             amount = float(boat['pricing']['total'])
#         
#         boat_data.append([event_type, boat_type, f"{amount:.2f} EUR"])
#     
#     # Add total row
#     total_amount = float(payment['amount'])
#     boat_data.append(['', 'TOTAL', f"{total_amount:.2f} EUR"])
#     
#     boat_table = Table(boat_data, colWidths=[6*cm, 6*cm, 4*cm])
#     boat_table.setStyle(TableStyle([
#         # Header row
#         ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, 0), 10),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
#         ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
#         
#         # Data rows
#         ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
#         ('FONTSIZE', (0, 1), (-1, -2), 10),
#         ('TEXTCOLOR', (0, 1), (-1, -2), colors.HexColor('#333333')),
#         ('ALIGN', (2, 1), (2, -2), 'RIGHT'),
#         ('BOTTOMPADDING', (0, 1), (-1, -2), 6),
#         
#         # Total row
#         ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, -1), (-1, -1), 11),
#         ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1a1a1a')),
#         ('ALIGN', (1, -1), (2, -1), 'RIGHT'),
#         ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#333333')),
#         ('TOPPADDING', (0, -1), (-1, -1), 8),
#         
#         # Grid
#         ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#cccccc')),
#     ]))
#     elements.append(boat_table)
#     elements.append(Spacer(1, 1*cm))
#     
#     # Stripe receipt link if available
#     if payment.get('stripe_receipt_url'):
#         receipt_text = Paragraph(
#             f"<b>Reçu Stripe / Stripe Receipt:</b><br/>"
#             f"<link href='{payment['stripe_receipt_url']}'>{payment['stripe_receipt_url']}</link>",
#             normal_style
#         )
#         elements.append(receipt_text)
#         elements.append(Spacer(1, 0.5*cm))
#     
#     # Footer
#     footer_text = Paragraph(
#         "<i>Merci pour votre participation / Thank you for your participation</i>",
#         ParagraphStyle('Footer', parent=normal_style, fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#666666'))
#     )
#     elements.append(Spacer(1, 1*cm))
#     elements.append(footer_text)
#     
#     # Build PDF
#     doc.build(elements)
#     
#     # Get PDF content
#     pdf_content = buffer.getvalue()
#     buffer.close()
#     
#     return pdf_content


def generate_text_invoice(payment, team_manager, boats):
    """
    Generate plain text invoice for a payment
    
    Args:
        payment: Payment record dict
        team_manager: Team manager profile dict
        boats: List of boat registration dicts
    
    Returns:
        str: Text invoice content
    """
    payment_date = datetime.fromisoformat(payment['paid_at'].replace('Z', '+00:00'))
    formatted_date = payment_date.strftime('%d/%m/%Y %H:%M')
    
    lines = []
    lines.append("=" * 80)
    lines.append("FACTURE / INVOICE".center(80))
    lines.append("Course des Impressionnistes".center(80))
    lines.append("=" * 80)
    lines.append("")
    
    # Payment information
    lines.append("INFORMATIONS DE PAIEMENT / PAYMENT INFORMATION")
    lines.append("-" * 80)
    lines.append(f"ID de paiement / Payment ID: {payment['payment_id']}")
    lines.append(f"Date: {formatted_date}")
    lines.append(f"Montant / Amount: {float(payment['amount']):.2f} {payment['currency']}")
    lines.append(f"Statut / Status: {payment['status'].capitalize()}")
    lines.append("")
    
    # Team manager information
    lines.append("INFORMATIONS DU CLUB / CLUB INFORMATION")
    lines.append("-" * 80)
    lines.append(f"Nom / Name: {team_manager.get('first_name', '')} {team_manager.get('last_name', '')}")
    lines.append(f"Club: {team_manager.get('club_affiliation', 'N/A')}")
    lines.append(f"Email: {team_manager.get('email', 'N/A')}")
    lines.append("")
    
    # Boats section
    lines.append("BATEAUX PAYÉS / BOATS PAID")
    lines.append("-" * 80)
    event_type_header = "Type d'événement / Event Type"
    boat_type_header = "Type de bateau / Boat Type"
    amount_header = "Montant / Amount"
    lines.append(f"{event_type_header:<30} {boat_type_header:<30} {amount_header:>18}")
    lines.append("-" * 80)
    
    total_amount = 0.0
    for boat in boats:
        event_type = boat.get('event_type', 'N/A')
        boat_type = boat.get('boat_type', 'N/A')
        
        # Get amount from pricing (works for both snapshot and full boat record)
        amount = 0.0
        if boat.get('pricing') and boat['pricing'].get('total'):
            amount = float(boat['pricing']['total'])
            logger.info(f"Boat {boat.get('boat_registration_id', 'unknown')}: Using pricing = {amount}")
        elif boat.get('locked_pricing') and boat['locked_pricing'].get('total'):
            amount = float(boat['locked_pricing']['total'])
            logger.info(f"Boat {boat.get('boat_registration_id', 'unknown')}: Using locked_pricing = {amount}")
        else:
            logger.warning(f"Boat {boat.get('boat_registration_id', 'unknown')}: No pricing found. Keys: {list(boat.keys())}")
        
        total_amount += amount
        lines.append(f"{event_type:<30} {boat_type:<30} {amount:>15.2f} EUR")
    
    lines.append("-" * 80)
    lines.append(f"{'TOTAL':>60} {float(payment['amount']):>15.2f} EUR")
    lines.append("=" * 80)
    lines.append("")
    
    # Stripe receipt link if available
    if payment.get('stripe_receipt_url'):
        lines.append("REÇU STRIPE / STRIPE RECEIPT")
        lines.append("-" * 80)
        lines.append(payment['stripe_receipt_url'])
        lines.append("")
    
    # Footer
    lines.append("")
    lines.append("Merci pour votre participation / Thank you for your participation".center(80))
    lines.append("=" * 80)
    
    return "\n".join(lines)


@handle_exceptions
@require_team_manager_or_admin_override
@require_permission('download_payment_invoice')
def lambda_handler(event, context):
    """
    Generate and return text invoice for a payment
    
    Path parameters:
        - payment_id: UUID of the payment
    
    Returns:
        Text file response
    """
    logger.info("Get payment invoice request")
    
    # Get authenticated user (respects admin impersonation via _effective_user_id)
    team_manager_id = event.get('_effective_user_id')
    if not team_manager_id:
        user = get_user_from_event(event)
        team_manager_id = user['user_id']
    
    # Get payment ID from path parameters
    path_params = event.get('pathParameters') or {}
    payment_id = path_params.get('payment_id')
    
    if not payment_id:
        return not_found_error('payment')
    
    # Get database client
    db = get_db_client()
    
    # Retrieve payment record
    payment = db.get_item(
        f'TEAM#{team_manager_id}',
        f'PAYMENT#{payment_id}'
    )
    
    if not payment:
        logger.warning(f"Payment {payment_id} not found for team manager {team_manager_id}")
        return not_found_error('payment', payment_id)
    
    try:
        # Retrieve team manager profile
        team_manager = db.get_item(
            f'USER#{team_manager_id}',
            'PROFILE'
        )
        
        if not team_manager:
            logger.error(f"Team manager profile not found: {team_manager_id}")
            return internal_error(message='Team manager profile not found')
        
        # Retrieve boat details
        # First try to use boat_details from payment record (snapshot at payment time)
        # This includes pricing information that was locked at payment time
        boats = []
        
        if payment.get('boat_details'):
            # Use snapshot from payment record
            logger.info(f"Using boat_details snapshot from payment record ({len(payment['boat_details'])} boats)")
            boats = payment['boat_details']
        else:
            # Fallback: fetch current boat records
            logger.info(f"No boat_details in payment record, fetching current boat records")
            boat_ids = payment.get('boat_registration_ids', [])
            
            for boat_id in boat_ids:
                boat = db.get_item(
                    f'TEAM#{team_manager_id}',
                    f'BOAT#{boat_id}'
                )
                if boat:
                    boats.append(boat)
        
        # Log what we're about to do
        logger.info(f"Generating text invoice for payment {payment_id} with {len(boats)} boats")
        
        # Generate text invoice
        text_content = generate_text_invoice(payment, team_manager, boats)
        
        # Generate filename
        payment_date = datetime.fromisoformat(payment['paid_at'].replace('Z', '+00:00'))
        filename = f"invoice-payment-{payment_id}-{payment_date.strftime('%Y-%m-%d')}.txt"
        
        logger.info(f"Successfully generated text invoice for payment {payment_id}, size: {len(text_content)} bytes")
        
        # Return text response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/plain; charset=utf-8',
                'Content-Disposition': f'attachment; filename={filename}',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': text_content
        }
        
    except Exception as e:
        logger.error(f"Failed to generate text invoice: {str(e)}", exc_info=True)
        return internal_error(message=f'Failed to generate text invoice: {str(e)}')
