import logging
from celery_app import celery
from flask import current_app
from models import db, User
from services.email_service import send_email
from utils.templates.email_templates import payment_received_email_template, task_completion_email_template, task_assignment_email_template, wallet_authorization_email_template,verification_email_template, password_recovery_email_template, wallet_topup_email_template
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

@celery.task(bind=True, name="workers.send_payment_authorization_email", max_retries=3, default_retry_delay=30)
def send_payment_authorization_email(self, user_id, task_name, task_id,amount, worker_name, worker_phone = None, worker_profile_image = None):
    """Function to send payment authorization email synchronously"""
    try:
        user = User.query.get(user_id)
        if not user:
            logger.error(f"User with ID {user_id} not found for payment authorization email")
            return

        recipient_email = user.email
        timestamp = datetime.now().strftime("%b %d, %Y at %I:%M %p")

        email_html = wallet_authorization_email_template(
            name=user.name or "User",
            task_name=task_name,
            task_id=task_id,
            amount=amount,
            worker_name=worker_name,
            worker_phone=worker_phone,
            worker_profile_image=worker_profile_image,
            timestamp=timestamp
        )

        send_email(
            to_email=recipient_email,
            subject=f"Payment Authorized - {task_name}",
            html_content=email_html
        )

        logger.info(f"Payment authorization email sent to {recipient_email} for task {task_id}")

    except Exception as e:
        logger.exception(f"Failed to send payment authorization email to user ID {user_id} for task {task_id}")
        raise self.retry(exc=e)
    
@celery.task(name="workers.send_task_assignment_email", max_retries=3, default_retry_delay=30)
def send_task_assignment_email(self, worker_name, worker_email, amount, task_name, task_id, task_description, client_name, client_phone, client_profile_image, timestamp):
    """Wrapper function to call the Celery task for sending payment authorization email"""
    try:
        email_html = task_assignment_email_template(
            worker_name=worker_name,
            amount=amount,
            task_name=task_name,
            task_id=task_id,
            task_description=task_description,
            client_name=client_name,
            client_phone=client_phone,
            client_profile_image=client_profile_image,
            timestamp=timestamp
        )
 
        send_email_async_task.delay(
            to_email=worker_email,
            subject=f"Task Assigned - {task_name}",
            html_content=email_html
        )

        logger.info(f"Task assignment email sent to {client_name} for task {task_id}")

    except Exception as e:
        logger.exception(f"Failed to send task assignment email to {client_name} for task {task_id}")
        raise self.retry(exc=e)
    
@celery.task(name="workers.send_task_completion_email", max_retries=3, default_retry_delay=30)
def send_task_completion_email(self, worker_name, worker_email, amount, task_name, task_id, task_description, client_name, worker_phone, worker_profile_image, completion_timestamp, review_link):
    """Wrapper function to call the Celery task for sending payment authorization email"""
    try:
        email_html = task_completion_email_template(
            client_name,
            worker_name, 
            amount,
            task_name,
            task_id,
            task_description,
            worker_phone,
            worker_profile_image,
            completion_timestamp,
            review_link
        )
 
        send_email_async_task.delay(
            to_email=worker_email,
            subject=f"Task Assigned - {task_name}",
            html_content=email_html
        )

        logger.info(f"Task assignment email sent to {client_name} for task {task_id}")

    except Exception as e:
        logger.exception(f"Failed to send task assignment email to {client_name} for task {task_id}")
        raise self.retry(exc=e) 
    
@celery.task(name="workers.task_settlement_email", max_retries=3, default_retry_delay=30)
def task_settlement_email(self,worker_email, worker_name, agreed_amount, task_name, task_id, client_name, client_profile_image, completion_timestamp, settlement_timestamp):
    """Function to send task settlement email synchronously"""
    try:
        html_content =  payment_received_email_template(
            worker_name,
            agreed_amount,
            task_name,
            task_id,
            client_name,
            client_profile_image,
            completion_timestamp,
            settlement_timestamp
        )
        send_email_async_task.delay(
            to_email=worker_email,
            subject=f"Task settlement successfull - {task_name}",
            html_content=html_content
        )
        logger.info(f"Task settlement email sent to {worker_email} for task {task_id}")
    except Exception as e:
        logger.exception(f"Failed to send task settlement email to {worker_email}")
        self.retry(exc=e)
        raise