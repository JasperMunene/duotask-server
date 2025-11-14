# import smtplib, ssl
# from email.message import EmailMessage
import os
from dotenv import load_dotenv
import resend
import logging

logger = logging.getLogger(__name__)

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
# SMTP_SERVER = os.getenv("SMTP_SERVER")
# SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
# SMTP_USER = os.getenv("SMTP_USER")
# SMTP_PASS = os.getenv("SMTP_PASS")

def send_email(to_email: str, subject: str, html_content: str, plain_text: str = ""):
    """Reusable email sender using Resend"""
    params = {
        "from": "Duotasks <duotasks@mails.ryfty.net>",  # Or your verified sender domain
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    }

    if plain_text:
        params["text"] = plain_text

    try:
        response = resend.Emails.send(params)
        logger.info("✅ Email sent successfully:", response)
        return response
    except Exception as e:
        logger.error("❌ Failed to send email:", str(e))
        return None