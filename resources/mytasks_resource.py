from flask_restful import Resource, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from models import db
from models.task import Task
from models.user import User
from models.task_assignment import TaskAssignment
from models.bid import Bid
from flask import current_app
from sqlalchemy import and_

class MyPostedTasksResource(Resource):
    @jwt_required()
    def get(self):
        """Get tasks created by the authenticated user."""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        cache = current_app.cache

        if not user:
            abort(404, message="User not found")

        cache_key = f"my_tasks:{user_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached, 200

        tasks = Task.query.filter(
                and_(
                    Task.user_id == user_id,
                    Task.status != 'completed'
                )
                ).options(
                    joinedload(Task.location),
                    joinedload(Task.categories),
                    joinedload(Task.images)
                ).all()

        if not tasks:
            return {"message": "No tasks found for this user"}, 404

        result = []
        for task in tasks:
            task_data = {
                "id": task.id,
                "status": task.status,
                "budget": float(task.budget or 0),
                "work_mode": task.work_mode,
                "name": task.title,
            }

            # If task has been assigned
            if task.status not in ["open", "canceled"]:
                assignment = TaskAssignment.query.options(
                    joinedload(TaskAssignment.doer)
                ).filter_by(task_id=task.id).first()

                if assignment:
                    task_data["assignment"] = {
                        "id": assignment.id,
                        "status": assignment.status,
                        "task_doer": {
                            "id": assignment.doer.id,
                            "name": assignment.doer.name,
                            "image": assignment.doer.image
                        } if assignment.doer else None,
                        "agreed_price": float(assignment.agreed_price or 0)
                    }
            else:
                # If task is still open, include bids
                bids = Bid.query.options(joinedload(Bid.user)).filter(Bid.task_id == task.id, Bid.status != 'rejected').all()
                task_data["bids_count"] = len(bids)
                task_data["bids"] = [
                    {
                        "price": float(bid.amount),
                        "bidder_image": bid.user.image if bid.user else None
                    } for bid in bids
                ]

            result.append(task_data)

        # Cache the result for 5 minutes
        cache.set(cache_key, result, timeout=60 * 5)
        return result, 200

    
class PostedTaskResource(Resource):
    @jwt_required()
    def get(self, task_id):
        """Get a task created by the authenticated user."""
        cache = current_app.cache
        user_id = get_jwt_identity()

        cache_key = f"posted_task:{user_id}:{task_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached, 200

        user = User.query.get(user_id)
        if not user:
            abort(404, message="User not found")

        task = Task.query.options(
            joinedload(Task.location),
            joinedload(Task.categories),
            joinedload(Task.images),
        ).get(task_id)

        if not task:
            return {"message": "No task found"}, 404

        task_data = {
            "status": task.status,
            "work_mode": task.work_mode,
            "deadline_date": task.deadline_date.isoformat() if task.deadline_date else None,
            "description": task.description,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "budget": float(task.budget),
            "preferred_time": task.preferred_time,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "title": task.title,
            "id": task.id,
            "schedule_type": task.schedule_type,
            "specific_date": task.specific_date.isoformat() if task.specific_date else None
        }

        # --- Include assignment data ---
        if task.status not in ["open", "canceled"]:
            assignment = TaskAssignment.query.options(
                joinedload(TaskAssignment.doer)
            ).filter_by(task_id=task.id).first()

            if assignment:
                task_data["assignment"] = {
                    "id": assignment.id,
                    "status": assignment.status,
                    "task_doer": {
                        "id": assignment.doer.id,
                        "name": assignment.doer.name,
                        "image": assignment.doer.image
                    } if assignment.doer else None,
                    "agreed_price": float(assignment.agreed_price or 0)
                }

        # --- Location ---
        if task.work_mode == "remote" or not task.location:
            task_location = {}
        else:
            task_location = {
                "latitude": float(task.location.latitude),
                "longitude": float(task.location.longitude),
                "country": task.location.country,
                "state": task.location.state,
                "city": task.location.city,
                "area": task.location.area
            }

        result = {
            "task": task_data,
            "location": task_location,
        }

        # --- Bids if open ---
        if task.status == "open":
            bid_query = Bid.query.options(joinedload(Bid.user)).filter(Bid.task_id == task.id, Bid.status != 'rejected').all()
            result["bids"] = [
                {
                    "bidder_image": bid.user.image,
                    "bidder_name": bid.user.name,
                    "bidder_id": bid.user.id,
                    "bid_id": bid.id,
                    "bid_text": bid.message,
                    "bid_amount": float(bid.amount)
                }
                for bid in bid_query
            ]

        # --- Assigned user info if applicable ---
        elif task.status in ["in_progress", "completed"]:
            task_assignment = TaskAssignment.query.filter_by(task_id=task.id).first()
            if task_assignment:
                assigned_user = User.query.options(joinedload(User.user_info)).get(task_assignment.task_doer)
                if assigned_user:
                    result["assigned_user"] = _get_user_data(task, assigned_user)

        # --- Cache and return ---
        cache.set(cache_key, result, timeout=60 * 5)  # cache for 5 minutes

        return result, 200




def _get_user_data(task, user):
    """Helper to get assigned user data with average rating."""
    user_reviews = user.reviews_received if task.user else []
    avg_rating = (
        sum(r.rating for r in user_reviews) / len(user_reviews)
        if user_reviews else 0.0
    )
    return {
        'id': user.id,
        'name': user.name,
        'rating': avg_rating,
        'completed_tasks': getattr(user, 'completed_tasks_count', 0),
        'avatar': user.image
    }
    
class MyAssignedTasksResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        cache = current_app.cache
        cache_key = f"assigned_tasks:{user_id}"

        # Check for cached response
        cached = cache.get(cache_key)
        if cached:
            return cached, 200

        # Step 1: Ensure user exists
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 403

        # Step 2: Get task assignments for the user
        task_assignments = TaskAssignment.query.filter(
            TaskAssignment.task_doer == user_id,
            TaskAssignment.status != 'completed'
        ).all()
        if not task_assignments:
            response = {"message": "No active task assignments found for this user", "tasks": []}
            cache.set(cache_key, response, timeout=60 * 5)
            return response, 200

        # Step 3: Get all related tasks in one go
        task_ids = [t.task_id for t in task_assignments]
        tasks = Task.query.options(joinedload(Task.user)).filter(Task.id.in_(task_ids)).all()
        task_map = {task.id: task for task in tasks}

        # Step 4: Build response
        result = []
        for assignment in task_assignments:
            task = task_map.get(assignment.task_id)
            if not task:
                continue  # In case task was deleted or mismatch

            assignment_data = {
                "id": task.id,
                "status": task.status,
                "agreed_price": float(assignment.agreed_price),
                "user": {
                    "id": task.user.id,
                    "name": task.user.name,
                    "avator": task.user.image
                },
                "task_title": task.title,
                "task_description": task.description,
                "schedule_type": task.schedule_type,
                "specific_date": task.specific_date.isoformat() if task.specific_date else None,
                "deadline_date": task.deadline_date.isoformat() if task.deadline_date else None,
                "preferred_time": task.preferred_time,
                "work_mode": task.work_mode
            }
            result.append(assignment_data)

        response = {"tasks": result}
        cache.set(cache_key, response, timeout=60 * 5)

        return response, 200
