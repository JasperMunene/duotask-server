from app import create_app
from utils.send_notification import Notify
from models.bid import Bid
from models.user import User
import logging

logger = logging.getLogger(__name__)

# Create your Celery instance within an app context.
def create_celery():
    app = create_app()
    celery = app.celery
    return celery

celery = create_celery()

@celery.task(bind=True, max_retries=3, default_retry_delay=30)
def new_bid(self, user_id, bid_id):
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
            notify = Notify(user_id=user_id, message=message, source=source, is_important=True)
            notify.post()

            # Log the successful notification.
            logger.info(f"Notification sent to user {user_id} for bid {bid_id} from {bidder_name}.")
        except Exception as exc:
            logger.error(f"Error sending notification for bid {bid_id} to user {user_id}: {exc}")
            # Retry the task if it fails.
            raise self.retry(exc=exc)
