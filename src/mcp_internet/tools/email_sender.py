"""
Email Sender Tool - Send emails via SMTP.

Requires SMTP configuration (Gmail, Outlook, or custom SMTP server).
"""

import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    body: str,
    smtp_server: str = "",
    smtp_port: int = 587,
    sender_email: str = "",
    sender_password: str = ""
) -> str:
    """
    Send an email via SMTP.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        body: Email body text
        smtp_server: SMTP server (default: from env MCP_SMTP_SERVER, or smtp.gmail.com)
        smtp_port: SMTP port (default: 587 for TLS)
        sender_email: Sender email (default: from env MCP_SMTP_EMAIL)
        sender_password: Sender password/app password (default: from env MCP_SMTP_PASSWORD)
        
    Returns:
        Success or error message
        
    Note:
        For Gmail, you need to use an App Password (not your regular password).
        Enable 2FA and create an App Password at:
        https://myaccount.google.com/apppasswords
        
    Environment Variables (optional):
        MCP_SMTP_SERVER: SMTP server address
        MCP_SMTP_PORT: SMTP port
        MCP_SMTP_EMAIL: Sender email address
        MCP_SMTP_PASSWORD: Sender password or app password
    """
    if not to_email.strip():
        return "❌ Error: Please provide a recipient email address."
    
    if not subject.strip():
        return "❌ Error: Please provide an email subject."
    
    if not body.strip():
        return "❌ Error: Please provide an email body."
    
    # Get SMTP configuration from parameters or environment
    smtp_server = smtp_server or os.environ.get("MCP_SMTP_SERVER", "smtp.gmail.com")
    smtp_port = smtp_port or int(os.environ.get("MCP_SMTP_PORT", "587"))
    sender_email = sender_email or os.environ.get("MCP_SMTP_EMAIL", "")
    sender_password = sender_password or os.environ.get("MCP_SMTP_PASSWORD", "")
    
    if not sender_email or not sender_password:
        return """❌ Error: SMTP credentials not configured.

To use email sending, set the following environment variables:
  - MCP_SMTP_SERVER (default: smtp.gmail.com)
  - MCP_SMTP_PORT (default: 587)
  - MCP_SMTP_EMAIL (your email address)
  - MCP_SMTP_PASSWORD (your password or app password)

For Gmail:
1. Enable 2-Factor Authentication
2. Create an App Password at: https://myaccount.google.com/apppasswords
3. Use the App Password as MCP_SMTP_PASSWORD

Or pass credentials directly to this function.
"""
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        
        msg.attach(MIMEText(body, "plain"))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Enable TLS
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return f"""✅ **Email Sent Successfully**
{'=' * 40}

📧 To: {to_email}
📝 Subject: {subject}
📄 Body: {body[:100]}{'...' if len(body) > 100 else ''}

Sent from: {sender_email}
"""
        
    except smtplib.SMTPAuthenticationError:
        return """❌ Error: SMTP authentication failed.

For Gmail:
- Make sure you're using an App Password (not your regular password)
- Create an App Password at: https://myaccount.google.com/apppasswords

For other providers:
- Check your SMTP credentials
- Some providers require "less secure app access" or app-specific passwords
"""
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return f"❌ Error: Failed to send email. {str(e)}"
    except Exception as e:
        logger.error(f"Email error: {e}")
        return f"❌ Error: {str(e)}"
