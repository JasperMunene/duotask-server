from flask_restful import Resource, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from sqlalchemy import and_
from models import db
from models.task import Task
from models.bid import Bid
from models.task_assignment import TaskAssignment
from models.conversation import Conversation
from models.message import Message
from models.user import User

import logging

logger = logging.getLogger(__name__)

class TaskAssignResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'bid_id',
        type=int,
        required=True,
        help="Bid ID to accept is required"
    )

    @jwt_required()
    def post(self, task_id):
        # Parse and validate JWT identity
        raw_identity = get_jwt_identity()
        try:
            user_id = int(raw_identity)
        except (TypeError, ValueError):
            abort(403, message="Invalid user identity")

        # Parse request arguments
        args = self.parser.parse_args()
        bid_id = args['bid_id']

        # Fetch and validate task
        task = Task.query.get(task_id)
        if not task or getattr(task, 'is_deleted', False):
            abort(404, message="Task not found")
        if task.user_id != user_id:
            abort(403, message="Unauthorized to assign this task")
        if task.status != 'open':
            abort(409, message="Task is not open for assignment")

        # Fetch and validate bid
        bid = Bid.query.filter_by(id=bid_id, task_id=task_id).first()
        if not bid:
            abort(404, message="Bid not found for this task")
        if bid.status != 'pending':
            abort(409, message="Bid is not in a pending state")

        # Ensure no existing assignment
        if TaskAssignment.query.filter_by(task_id=task_id).first():
            abort(409, message="Task already assigned")

        try:
            # Collect other pending bids before state updates
            other_bids = Bid.query.filter(
                and_(
                    Bid.task_id == task_id,
                    Bid.status == 'pending',
                    Bid.id != bid_id
                )
            ).all()
            rejected_user_ids = [b.user_id for b in other_bids]

            # Create assignment
            assignment = TaskAssignment(
                task_id=task_id,
                task_giver=user_id,
                task_doer=bid.user_id,
                agreed_price=bid.amount,
                bid_id=bid.id,
                status='assigned'
            )
            db.session.add(assignment)
            conversation = Conversation(task_giver=user_id, task_doer=bid.user_id)

            # Create the default message for task_doer
            message = Message(
                conversation=conversation,
                sender_id=user_id,
                reciever_id=bid.user_id,
                message="Hello, let's start the conversation.",
                date_time=db.func.now()
            )

            # Add the conversation and the message to the session and commit
            db.session.add(conversation)
            db.session.add(message)
            
            
            # Update accepted bid and task status
            bid.status = 'accepted'
            task.status = 'assigned'

            # Reject other pending bids
            Bid.query.filter(
                and_(
                    Bid.task_id == task_id,
                    Bid.status == 'pending',
                    Bid.id != bid_id
                )
            ).update({'status': 'rejected'}, synchronize_session=False)

            # Commit all changes atomically
            db.session.commit()

            # Invalidate caches and send notifications
            self._invalidate_caches(task_id)
            self._notify_parties(task, bid, assignment, rejected_user_ids)
        
            return {
                'message': 'Task assigned successfully',
                'assignment_id': assignment.id,
                'task_status': task.status
            }, 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Task assignment failed: {e}", exc_info=True)
            abort(500, message="Internal server error during assignment")

    def _invalidate_caches(self, task_id):
        """Invalidate cached data related to task and bids"""
        try:
            redis_cli = current_app.redis
            for key in redis_cli.scan_iter(f"task_bids_{task_id}_*"):
                redis_cli.delete(key)
            redis_cli.delete(f"task_{task_id}")
        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")

    def _notify_parties(self, task, bid, assignment, rejected_user_ids):
        """Handle all notification logic through Celery"""
        try:
            # Notify accepted bidder
            current_app.celery.send_task(
                'notifications.task_assigned',
                args=(task.id, bid.user_id, task.user_id),
                queue='notifications'
            )
            # Notify rejected bidders
            if rejected_user_ids:
                current_app.celery.send_task(
                    'notifications.bid_rejected',
                    # task_id, rejected_user_ids, task.user_id -> the owner who created the task
                    args=(task.id, list(set(rejected_user_ids)), task.user_id),
                    queue='notifications'
                )
        except Exception as e:
            logger.error(f"Notification system error: {e}")

    def _notify_success_bider(self, task, bid, assignment, accepted_bidder):
        """Notify the user who won the bid"""
        try:
            message = (
                f"Congratulations! Your bid for the task '{task.title}' has been accepted. "
                f"You have been assigned to complete this task with an agreed price of {bid.amount}."
            )
            notify = Notify(
                user_id=bid.user_id,
                message=message,
                source='task_assignment',
                is_important=True,
                sender_id=task.user_id
            )
            notify.post()
        except Exception as e:
            logger.error(f"Failed to notify winning bidder: {e}")
