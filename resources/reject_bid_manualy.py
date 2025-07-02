from flask_restful import Resource, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.bid import Bid
from workers.notifications import bid_rejected_single
from models.task import Task
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class BidRejectResource(Resource):
    # Define request parser for bid_id
    parser = reqparse.RequestParser()
    parser.add_argument(
        'bid_id',
        type=int,
        required=True,
        help="Bid ID is required"
    )

    @jwt_required()  # Ensure the user is authenticated
    def post(self, task_id):
        cache = current_app.cache

        # Get and validate current user identity
        raw_identity = get_jwt_identity()
        try:
            user_id = int(raw_identity)
        except (TypeError, ValueError):
            abort(403, message="Invalid user identity")

        # Parse incoming bid_id from request body
        args = self.parser.parse_args()
        bid_id = args['bid_id']

        # Validate task existence and ownership
        task = Task.query.get(task_id)
        if not task or getattr(task, 'is_deleted', False):
            abort(404, message="Task not found")
        if task.user_id != user_id:
            abort(403, message="Unauthorized to reject bids on this task")
        if task.status != 'open':
            abort(409, message="Task is not open for bid rejection")

        # Validate the bid
        bid = Bid.query.filter_by(id=bid_id, task_id=task_id).first()
        if not bid:
            abort(404, message="Bid not found for this task")
        if bid.status != 'pending':
            abort(409, message="Only pending bids can be rejected")

        try:
            # Mark bid as rejected
            bid.status = 'rejected'
            db.session.commit()
            logger.info(f"Bid {bid_id} for task {task_id} rejected by user {user_id}")

            # Clear task cache for the poster
            cache.delete(f"posted_task:{task.user_id}:{task_id}")

            # Send notification asynchronously via Celery
            self._notify_user_bid_rejected(task_id, bid.user_id, task.user_id)

            # Respond with success
            return {
                'message': 'Bid rejected successfully',
                'bid_id': bid.id,
                'status': bid.status
            }, 200

        except Exception as e:
            # Handle and log any unexpected DB error
            db.session.rollback()
            logger.error(f"Failed to reject bid: {e}", exc_info=True)
            abort(500, message="Internal server error during bid rejection")

    # Internal method to send a notification using Celery worker
    def _notify_user_bid_rejected(self, task_id, bidder_id, task_owner_id):
        try:
            with current_app.app_context():
                # Queue background notification
                bid_rejected_single.delay(task_id, bidder_id, task_owner_id)
                logger.info(f"Notification task for bid rejection queued for task {task_id}, bidder {bidder_id}, owner {task_owner_id}")
        except Exception as notify_err:
            # Log any error in notification process
            logger.warning(f"Notification error for manual rejection: {notify_err}")
