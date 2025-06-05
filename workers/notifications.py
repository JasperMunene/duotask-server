from app import create_app
from utils.send_notification import Notify
from models.bid import Bid
from models.user import User
from models.task import Task
import logging
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)

# Create your Celery instance within an app context.
def create_celery():
    app = create_app()
    celery = app.celery
    return celery

celery = create_celery()

@celery.task(bind=True, max_retries=3, default_retry_delay=30)
def new_bid(self, user_id, bid_id, sender_id):
    """
    Celery task to notify the task owner that a new bid was placed.
    Retrieves additional bid details including the bidder's name.
    """
    # Create a Flask app context for this worker.
    app = create_app()
    with app.app_context():
        try:
            # Retrieve the bid details.
            bid = Bid.query.get(bid_id)
            if not bid:
                logger.error(f"Bid with ID {bid_id} not found.")
                return

            # Extract bid information.
            bid_amount = bid.amount
            bid_message = bid.message if bid.message else "No additional message provided"
            bidder_id = bid.user_id

            # Retrieve the bidder's name from the User model.
            bidder = User.query.get(bidder_id)
            bidder_name = bidder.name if bidder else "Unknown User"

            # Customize the notification message to include the bidder's name.
            message = (
                f"Your task received a new bid (ID: {bid.id}) from {bidder_name} "
                f"with an amount of {bid_amount}. Message: {bid_message}"
            )
            source = 'bid'

            # Create and send the notification.
            notify = Notify(user_id=user_id, message=message, source=source, is_important=True, sender_id=sender_id)
            notify.post()

            # Log the successful notification.
            logger.info(f"Notification sent to user {user_id} for bid {bid_id} from {bidder_name}.")
        except Exception as exc:
            logger.error(f"Error sending notification for bid {bid_id} to user {user_id}: {exc}")
            # Retry the task if it fails.
            raise self.retry(exc=exc)



@celery.task(bind=True, max_retries=3, default_retry_delay=30)
def bid_rejected(self, task_id, user_ids, sender_id):
    """
    Notify all users in the user_ids list that their bid for a task was rejected.
    """
    app = create_app()
    with app.app_context():
        try:
            task = Task.query.get(task_id)
            if not task:
                logger.error(f"Task with ID {task_id} not found.")
                return

            for user_id in user_ids:
                bid = Bid.query.filter_by(task_id=task_id, user_id=user_id).first()
                if not bid:
                    logger.warning(f"No bid found for task {task_id} by user {user_id}. Skipping.")
                    continue

                bidder = User.query.get(user_id)
                bidder_name = bidder.name.split()[0] if bidder and bidder.name else "User"


                message = (
                    f"Hi {bidder_name}, your bid for the task '{task.title}' "
                    f"has been rejected. Bid amount: {bid.amount}. Thank you for your interest."
                )

                notification = Notify(
                    user_id=user_id,
                    message=message,
                    source='bid',
                    is_important=True,
                    sender_id=sender_id
                )
                notification.post()

                logger.info(f"Rejected bid notification sent to user {user_id} (bid ID {bid.id}).")

        except Exception as exc:
            logger.error(f"Failed to send rejected bid notifications: {exc}")
            raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=3, default_retry_delay=30)
def task_assigned(self, task_id, user_id, sender_id):
    # notify the successfully bidder that the task was accepted and the task owner should reach out soon
    app = create_app()
    with app.app_context():
        try:
            task = Task.query.get(task_id)
            bid = Bid.query.filter_by(task_id=task_id, user_id=user_id).first()

            if not task or not bid:
                logger.warning(f"Missing task or bid for task {task_id} and user {user_id}")
                return

            user = User.query.get(user_id)
            username = user.name.split()[0] if user and user.name else "User"

            message = (
                f"🎉 Congratulations {username}! Your bid  for the task '{task.title}' "
                f"has been accepted. Bid amount: {bid.amount}. The task owner will contact you shortly."
            )

            notify = Notify(
                user_id=user_id,
                message=message,
                source='bid',
                is_important=True,
                sender_id=sender_id
            )
            notify.post()

            logger.info(f"Accepted bid notification sent to {user_id} for task {task_id}.")

        except Exception as exc:
            logger.error(f"Failed to notify accepted bid: {exc}")
            raise self.retry(exc=exc)
