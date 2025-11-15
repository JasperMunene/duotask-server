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
from workers.notifications import task_assigned, bid_rejected
from models.user import User
from utils.exceptions import InsufficientBalanceError
from utils.ledgers.internal import InternalTransfer
from utils.send_notification import Notify
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskAssignResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('bid_id', type=int, required=True, help="Bid ID to accept is required")

    @jwt_required()
    def post(self, task_id):
        user_id = self._get_current_user_id()
        args = self.parser.parse_args()
        bid_id = args['bid_id']

        task = self._get_task(task_id, user_id)
        bid = self._get_bid(task_id, bid_id)
        self._ensure_task_not_already_assigned(task_id)

        try:
            rejected_user_ids = self._get_rejected_user_ids(task_id, bid_id)


             # 🟡 Check balance and hold funds
            transfer = InternalTransfer(task_id, task.title, user_id, bid.user_id, bid.amount)
            transfer.hold_funds()
        
            # 🟢 Proceed with task assignment if funds were held
            assignment = TaskAssignment(
                task_id=task_id,
                task_giver=user_id,
                task_doer=bid.user_id,
                agreed_price=bid.amount,
                bid_id=bid.id,
                status='assigned'
            )
            db.session.add(assignment)


            conversation = self._create_conversation(user_id, bid.user_id, task.id)
            db.session.add(conversation)

            bid.status = 'accepted'
            task.status = 'assigned'

            Bid.query.filter(
                and_(Bid.task_id == task_id, Bid.status == 'pending', Bid.id != bid_id)
            ).update({'status': 'rejected'}, synchronize_session=False)


            db.session.commit()
            ids = [task.user_id, bid.user_id]
            self._invalidate_caches(task_id, ids)
            self._notify_parties(task, bid, rejected_user_ids)
            self._notify_new_convo_convos(ids)
            self._send_authorisation_email(
                user_id=task.user_id,
                task_name=task.title,
                task_id=task.id,
                amount=bid.amount,
                worker_name=bid.user.name,
                worker_phone=bid.user.phone,
                worker_profile_image=bid.user.image
            )
            self._send_assignment_email(
                worker_name=bid.user.name,
                worker_email=bid.user.email,
                amount=bid.amount,
                task_name=task.title,
                task_id=task.id,
                task_description=task.description,
                client_name=task.user.name,
                client_phone=task.user.phone,
                client_profile_image=task.user.image,
                timestamp=datetime.now().strftime("%b %d, %Y at %I:%M %p")
            )

            return {
                'message': 'Task assigned successfully',
                'assignment_id': assignment.id,
                'task_status': task.status
            }, 200

        except InsufficientBalanceError as e:
            db.session.rollback()
            amount_needed = float(e.required_amount - e.current_balance)
            return {
                'error': 'Insufficient balance',
                'required_funding': round(amount_needed, 2),
                'message': f'You need KES {amount_needed:.2f} more to assign this task'
            }, 402
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Task assignment failed: {e}", exc_info=True)
            abort(500, message="Internal server error during assignment")

    def _get_current_user_id(self):
        try:
            return int(get_jwt_identity())
        except (TypeError, ValueError):
            abort(403, message="Invalid user identity")

    def _get_task(self, task_id, user_id):
        task = Task.query.get(task_id)
        if not task or getattr(task, 'is_deleted', False):
            abort(404, message="Task not found")
        if task.user_id != user_id:
            abort(403, message="Unauthorized to assign this task")
        if task.status != 'open':
            abort(409, message="Task is not open for assignment")
        return task

    def _get_bid(self, task_id, bid_id):
        bid = Bid.query.filter_by(id=bid_id, task_id=task_id).first()
        if not bid:
            abort(404, message="Bid not found for this task")
        if bid.status != 'pending':
            abort(409, message="Bid is not in a pending state")
        return bid

    def _ensure_task_not_already_assigned(self, task_id):
        if TaskAssignment.query.filter_by(task_id=task_id).first():
            abort(409, message="Task already assigned")

    def _get_rejected_user_ids(self, task_id, bid_id):
        other_bids = Bid.query.filter(
            and_(Bid.task_id == task_id, Bid.status == 'pending', Bid.id != bid_id)
        ).all()
        return [b.user_id for b in other_bids]
    
    def _create_conversation(self, sender_id, receiver_id, task_id):
        # Check for existing conversation between the two users on this task
        existing_convo = Conversation.query.filter(
            Conversation.task_id == task_id,
            db.or_(
                db.and_(Conversation.task_giver == sender_id, Conversation.task_doer == receiver_id),
                db.and_(Conversation.task_giver == receiver_id, Conversation.task_doer == sender_id)
            )
        ).first()

        if existing_convo:
            # Clear existing messages
            Message.query.filter_by(conversation_id=existing_convo.id).delete()

            # Update roles to reflect new direction
            existing_convo.task_giver = sender_id
            existing_convo.task_doer = receiver_id
            db.session.add(existing_convo)

            # Add new opening message
            message = Message(
                conversation=existing_convo,
                sender_id=sender_id,
                reciever_id=receiver_id,
                message="Hello, how are you doing?",
                date_time=db.func.now()
            )
            db.session.add(message)
            return existing_convo

        # No existing conversation, create a new one
        conversation = Conversation(task_giver=sender_id, task_id=task_id, task_doer=receiver_id)
        db.session.add(conversation)

        message = Message(
            conversation=conversation,
            sender_id=sender_id,
            reciever_id=receiver_id,
            message="Hello, how are you doing?",
            date_time=db.func.now()
        )
        db.session.add(message)

        return conversation


    def _invalidate_caches(self, task_id, user_ids):
        try:
            redis_cli = current_app.redis
            for key in redis_cli.scan_iter(f"task_bids_{task_id}_*"):
                redis_cli.delete(key)
            redis_cli.delete(f"task_{task_id}")
            cache = current_app.cache
            cache.delete(f"my_tasks:{user_id}")
            for user_id in user_ids:
                cache.delete(f"conversations_user_{user_id}")
        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")

    def _notify_new_convo_convos(self, user_ids):
        try:
            sender_id = user_ids[0]
            reciever_id = user_ids[1]
            Notify(user_id=sender_id, message="New conversation", source="chat", sender_id=reciever_id).post()
            Notify(user_id=reciever_id, message="New Convesation", source="chat", sender_id=sender_id).post()
        
        except Exception as e:
            logger.error(f"Notification system error: {e}")
    def _notify_parties(self, task, bid, rejected_user_ids):
        try:
            with current_app.app_context():
                task_assigned.delay(task.id, bid.user_id, task.user_id)
                if rejected_user_ids:
                    bid_rejected.delay(task.id, list(set(rejected_user_ids)), task.user_id)
        except Exception as e:
            logger.error(f"Notification system error: {e}")

    def _send_authorisation_email(self, user_id, task_name, task_id, amount, worker_name, worker_phone=None, worker_profile_image=None):
        try:
            from workers.email_worker import send_payment_authorization_email
            send_payment_authorization_email.delay(
                user_id,
                task_name,
                task_id,
                amount,
                worker_name,
                worker_phone,
                worker_profile_image
            )
        except Exception as e:
            logger.error(f"Failed to queue authorization email: {e}")

    def _send_assignment_email(self, worker_name, worker_email, amount, task_name, task_id, task_description, client_name, client_phone, client_profile_image, timestamp):
        try:
            from workers.email_worker import send_task_assignment_email
            send_task_assignment_email.delay(
                worker_name,
                worker_email,
                amount,
                task_name,
                task_id,
                task_description,
                client_name,
                client_phone,
                client_profile_image,
                timestamp
            )
        except Exception as e:
            logger.error(f"Failed to queue task assignment email: {e}")