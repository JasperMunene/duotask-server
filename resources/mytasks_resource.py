from flask_restful import Resource, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from models import db
from models.task import Task
from models.user import User
from models.task_assignment import TaskAssignment
from models.bid import Bid
from decimal import Decimal

class MyPostedTasksResource(Resource):
    @jwt_required()
    def get(self):
        """Get tasks created by the authenticated user."""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            abort(404, message="User not found")

        tasks = Task.query.filter(Task.user_id == user_id).options(
            joinedload(Task.location),
            joinedload(Task.categories),
            joinedload(Task.images),
        ).all()

        if not tasks:
            return {"message": "No tasks found for this user"}, 404

        result = []
        for task in tasks:
            # Load bids separately with user info
            bid_query = Bid.query.options(joinedload(Bid.user)).filter(Bid.task_id == task.id).all()

            task_data = {
                "id": task.id,
                "status": task.status,
                "budget": float(task.budget),
                "work_mode": task.work_mode,
                "name": task.title,  # Change to task.name if needed
                "bids_count": len(bid_query),
                "bids": [
                    {
                        "price": float(bid.amount),
                        "bidder_image": bid.user.image if bid.user else None
                    }
                    for bid in bid_query
                ]
            }
            result.append(task_data)

        return result, 200
    
class PostedTaskResource(Resource):
    @jwt_required()
    def get(self, task_id):
        """Get a task created by the authenticated user."""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            abort(404, message="User not found")

        # Fetch task with joined relationships
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


        task_location = {} if task.work_mode == "remote" else {
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

        # If task is open, include bids
        if task.status == "open":
            bid_query = Bid.query.options(joinedload(Bid.user)).filter(Bid.task_id == task.id).all()
            result["bids"] = [
                {
                    "bidder_image": bid.user.image,
                    "bidder_name": bid.user.name,
                    "bidder_id": bid.user.id,
                    "bid_id": bid.id,
                    "bid_text": bid.message
                }
                for bid in bid_query
            ]

        # If task is in progress, include assigned user data
        elif task.status == "in_progress" or task.status == "completed":
            task_assignment = TaskAssignment.query.filter_by(task_id=task.id).first()
            if task_assignment:
                assigned_user = User.query.options(joinedload(User.user_info)).get(task_assignment.task_doer)
                if assigned_user:
                    result["assigned_user"] = _get_user_data(task, assigned_user)

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

        # Step 1: Ensure user exists
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 403

        # Step 2: Get task assignments for the user
        task_assignments = TaskAssignment.query.filter_by(task_doer=user_id).all()
        if not task_assignments:
            return {"message": "No task assignments found for this user", "tasks": []}, 200

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
                "specific_date": task.specific_date,
                "deadline_date": task.deadline_date,
                "preferred_time": task.preferred_time,
                "work_mode": task.work_mode
            }
            result.append(assignment_data)

        return result, 200