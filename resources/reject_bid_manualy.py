from flask_restful import Resource, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.bid import Bid
from models.task import Task
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class BidRejectResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'bid_id',
        type=int,
        required=True,
        help="Bid ID is required"
    )

    @jwt_required()
    def post(self, task_id):
        cache = current_app.cache
        # Authenticate user
        raw_identity = get_jwt_identity()
        try:
            user_id = int(raw_identity)
        except (TypeError, ValueError):
            abort(403, message="Invalid user identity")

        # Parse arguments
        args = self.parser.parse_args()
        bid_id = args['bid_id']

        # Validate task
        task = Task.query.get(task_id)
        if not task or getattr(task, 'is_deleted', False):
            abort(404, message="Task not found")
        if task.user_id != user_id:
            abort(403, message="Unauthorized to reject bids on this task")
        if task.status != 'open':
            abort(409, message="Task is not open for bid rejection")

        # Fetch and validate bid
        bid = Bid.query.filter_by(id=bid_id, task_id=task_id).first()
        if not bid:
            abort(404, message="Bid not found for this task")
        if bid.status != 'pending':
            abort(409, message="Only pending bids can be rejected")

        try:
            bid.status = 'rejected'
            db.session.commit()

            # Optional: Notify user via Celery
            try:
                current_app.celery.send_task(
                    'notifications.bid_rejected_single',
                    args=(task.id, bid.user_id, task.user_id),
                    queue='notifications'
                )
            except Exception as notify_err:
                logger.warning(f"Notification error for manual rejection: {notify_err}")

            cache.delete(f"posted_task:{task.user_id}:{task_id}")
            return {
                'message': 'Bid rejected successfully',
                'bid_id': bid.id,
                'status': bid.status
            }, 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to reject bid: {e}", exc_info=True)
            abort(500, message="Internal server error during bid rejection")
