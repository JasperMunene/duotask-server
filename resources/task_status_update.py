from flask_restful import Resource, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from sqlalchemy import func, case, or_
from sqlalchemy.orm import joinedload
from models import db
from models.task import Task
from models.user import User
from models.user_info import UserInfo
from models.task_image import TaskImage
from models.bid import Bid
from models.task_assignment import TaskAssignment
import logging
import json
import base64
import urllib.parse
from werkzeug.exceptions import HTTPException
from utils.send_notification import Notify
from utils.ledgers.internal import InternalTransfer
logger = logging.getLogger(__name__)

        
class StatusUpdate(Resource):
    cache = current_app.cache
    parser = reqparse.RequestParser()
    parser.add_argument(
        'status',
        type=str,
        required=True,
        choices=['in_progress', 'completed', 'cancelled', 'on_the_way', 'done'],
        help="Invalid status. Allowed: in_progress, completed, cancelled, on_the_way, done"
    )

    @jwt_required()
    def put(self, task_id):
        user_id = get_jwt_identity()
        args = self.parser.parse_args()
        new_status = args['status']

        release_funds_needed = False
        notify_payload = {}

        try:
            with db.session.begin_nested():
                task = Task.query.get(task_id)
                if not task:
                    abort(404, message="Task not found")

                assignment = TaskAssignment.query.options(
                    joinedload(TaskAssignment.doer)
                ).filter_by(task_id=task_id).first()

                if not assignment:
                    abort(404, message=f"Assignment for task {task_id} not found")

                is_owner = task.user_id == int(user_id)
                is_doer = assignment.doer.id == int(user_id)

                # Permissions
                if new_status in ['on_the_way', 'in_progress', 'done'] and not is_doer:
                    abort(403, message="Only the assigned task doer can perform this action")
                if new_status == 'completed' and not is_owner:
                    abort(403, message="Only the task owner can mark as completed")

                # Apply status updates
                if new_status == "on_the_way":
                    assignment.status = new_status
                elif new_status == "in_progress":
                    assignment.status = new_status
                    task.status = new_status
                elif new_status == "done":
                    assignment.status = new_status
                elif new_status == "completed":
                    assignment.status = new_status
                    task.status = new_status
                    release_funds_needed = True

                notify_payload = {
                    "sender_id": int(user_id),
                    "task": task,
                    "user": assignment.doer if is_doer else User.query.get(user_id),
                    "status": new_status,
                    "receiver_id": task.user_id if is_doer else assignment.doer.id
                }

            # Commit changes
            db.session.commit()

            # Post-commit operations
            if release_funds_needed:
                transfer = InternalTransfer(
                    task_id=task.id,
                    task_title=task.title,
                    user_id=task.user_id,
                    doer_id=assignment.doer.id,
                    amount=assignment.agreed_price
                )
                transfer.release_funds()

            self._notify_based_on_status(**notify_payload)

            return {
                "message": f"Task status updated to {new_status}",
                "status": new_status
            }, 200

        except HTTPException:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Status update failed for task {task_id}: {e}", exc_info=True)
            abort(500, message="Internal server error during status update")

    # ✅ FIXED: Now correctly outside the put() method
    def _notify_based_on_status(self, sender_id, task, user, status, receiver_id):
        task_name = task.title
        user_name = user.name

        status_messages = {
            "on_the_way": f"{user_name} is on the way for task '{task_name}'",
            "in_progress": f"{user_name} has started the task '{task_name}'",
            "done": f"{user_name} has completed the task '{task_name}'. Please review it.",
            "completed": f"{user_name} has marked task '{task_name}' as completed. Payment is being processed.",
        }

        message = status_messages.get(status)
        if message:
            Notify(
                user_id=receiver_id,
                message=message,
                source="task_update",
                is_important=True,
                sender_id=sender_id
            ).post()
