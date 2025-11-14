import logging
from celery_app import celery
from flask import current_app
from models import db, User
from services.email_service import send_email
from utils.templates.email_templates import verification_email_template, password_recovery_email_template, wallet_topup_email_template
import time
from datetime import datetime
logger = logging.getLogger(__name__)

@celery.task(bind=True, name="workers.send_verification_email", max_retries=3, default_retry_delay=30)
def send_verification_email(self, name, email, token):
    try:
        with current_app.app_context():
            html = verification_email_template(name, token)
            send_email(email, "Verify your Duotasks account", html, f"Your code is {token}")
            logger.info(f"Verification email sent to {email}")
    except Exception as e:
        logger.exception(f"Failed to send verification email to user {name}")
        raise self.retry(exc=e)


@celery.task(bind=True, name="workers.send_reset_email", max_retries=3, default_retry_delay=30)
def send_reset_email(self, name, email, token):
    try:
        with current_app.app_context():
            html = password_recovery_email_template(name, token)
            send_email(email, "Password Recovery for Duotasks account", html, f"Your OTP is {token}")
            logger.info(f"Password recovery email sent to {email}")
    except Exception as e:
        logger.exception(f"Failed to send password recovery email to user {name}")
        raise self.retry(exc=e)

@celery.task(name="workers.send_email_async_task")
def send_email_async_task(email, subject, html, text):
    """Separate task just for sending emails"""
    start_time = time.time()
    try:
        send_email(email, subject, html, text)
        email_time = time.time() - start_time
        logger.info(f"Async email sent to {email} in {email_time:.3f}s")
    except Exception as e:
        email_time = time.time() - start_time
        logger.exception(f"Failed to send async email to {email} after {email_time:.3f}s")
        raise

@celery.task(bind=True, name="workers.send_wallet_top_up_mail", max_retries=3, default_retry_delay=30)
def send_wallet_top_up_mail(self, user_id, amount, transaction_id):
    """Helper function to send wallet top-up email"""
    user = User.query.get(user_id)
    if not user:
        logger.error(f"User with ID {user_id} not found for wallet top-up email")
        return
    name = user.name or "User"
    email = user.email

    html_content = wallet_topup_email_template(
        name=name,
        transaction_id=transaction_id,
        amount=amount,
        timestamp=datetime.now().strftime("%b %d, %Y at %I:%M %p"),
        payment_method="M-Pesa"
    )

    send_email_async_task.delay(
        email,
        "Wallet Top-up Successful",
        html_content,
        f"Hi {name}, Your wallet has been topped up with ${amount:.2f}. Thank you for using Duotasks!"
    )