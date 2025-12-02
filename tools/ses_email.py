"""AWS SES email sending tool."""

import boto3
import logging
from typing import Optional, List, Dict
from botocore.exceptions import ClientError
from strands import tool

logger = logging.getLogger(__name__)


@tool
def send_email_ses(
    recipients: List[str],
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    sender: Optional[str] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    reply_to: Optional[List[str]] = None,
    aws_region: Optional[str] = None
) -> Dict:
    """
    Send email using AWS SES.

    Args:
        recipients: List of recipient email addresses
        subject: Email subject line
        body_text: Plain text email body
        body_html: Optional HTML email body
        sender: Sender email address (uses SES_SENDER_EMAIL if not provided)
        cc: Optional list of CC recipients
        bcc: Optional list of BCC recipients
        reply_to: Optional list of reply-to addresses
        aws_region: AWS region (uses AWS_REGION config if not provided)

    Returns:
        Dict with success status, message_id, recipients_sent, or error details
    """
    from config import config

    # Use provided values or fall back to config
    sender_email = sender or config.SES_SENDER_EMAIL
    sender_name = config.SES_SENDER_NAME
    region = aws_region or config.AWS_REGION or "us-west-2"

    if not sender_email:
        return {
            "success": False,
            "error": "Sender email not configured. Set SES_SENDER_EMAIL environment variable."
        }

    # Format sender with display name if provided
    if sender_name and not sender:  # Only use name if using config email
        formatted_sender = f"{sender_name} <{sender_email}>"
    else:
        formatted_sender = sender_email

    if not recipients:
        return {
            "success": False,
            "error": "No recipients provided"
        }

    try:
        # Create SES client
        ses_client = boto3.client('ses', region_name=region)

        # Build destination
        destination = {"ToAddresses": recipients}
        if cc:
            destination["CcAddresses"] = cc
        if bcc:
            destination["BccAddresses"] = bcc

        # Build message
        message = {
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {
                "Text": {"Data": body_text, "Charset": "UTF-8"}
            }
        }

        if body_html:
            message["Body"]["Html"] = {"Data": body_html, "Charset": "UTF-8"}

        # Build send_email parameters
        send_params = {
            "Source": formatted_sender,
            "Destination": destination,
            "Message": message
        }

        if reply_to:
            send_params["ReplyToAddresses"] = reply_to

        # Send email
        response = ses_client.send_email(**send_params)

        total_recipients = len(recipients) + len(cc or []) + len(bcc or [])

        logger.info(f"Email sent successfully. MessageId: {response['MessageId']}")

        return {
            "success": True,
            "message_id": response['MessageId'],
            "recipients_sent": total_recipients,
            "sender": formatted_sender,
            "subject": subject
        }

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"SES ClientError: {error_code} - {error_message}")

        return {
            "success": False,
            "error": f"AWS SES Error: {error_code} - {error_message}",
            "error_code": error_code
        }

    except Exception as e:
        logger.error(f"Unexpected error sending email: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }
