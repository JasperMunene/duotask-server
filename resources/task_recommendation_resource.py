from flask import current_app, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.recommended_tasks import RecommendedTasks
from models.task import Task
from models.task_location import TaskLocation
from models.user import User
from models.category import Category
from sqlalchemy.orm import joinedload
import logging

logger = logging.getLogger(__name__)

class TaskRecommendationResource(Resource):
    @jwt_required()
    def get(self):
        """Get paginated recommended tasks for the current user."""
        user_id = get_jwt_identity()
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        cache = current_app.cache
        cache_key = f"recommended_tasks:{user_id}:page:{page}:per_page:{per_page}"
        cached = cache.get(cache_key)

        if cached:
            return {
                "tasks": cached,
                "page": page,
                "per_page": per_page,
                "has_next": True,  # Assume true if cached; optional adjustment
            }, 200

        pagination = (
            RecommendedTasks.query
            .filter_by(user_id=user_id)
            .join(RecommendedTasks.task)
            .options(
                joinedload(RecommendedTasks.task).joinedload(Task.location),
                joinedload(RecommendedTasks.task).joinedload(Task.user),
                joinedload(RecommendedTasks.task).joinedload(Task.categories)
            )
            .order_by(RecommendedTasks.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        if not pagination.items:
            return {"tasks": [], "message": "No recommended tasks found."}, 200

        tasks = []
        for rec in pagination.items:
            task = rec.task
            location = task.location
            poster = task.user
            categories = task.categories

            tasks.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "budget": str(task.budget),
                "created_at": task.created_at.strftime("%Y-%m-%d %H:%M:%S") if task.created_at else None,
                "updated_at": task.updated_at.strftime("%Y-%m-%d %H:%M:%S") if task.updated_at else None,
                "schedule_type": task.schedule_type,
                "specific_date": task.specific_date.strftime("%Y-%m-%d %H:%M:%S") if task.specific_date else None,
                "deadline_date": task.deadline_date.strftime("%Y-%m-%d %H:%M:%S") if task.deadline_date else None,
                "preferred_time": task.preferred_time,
                "location": {
                    "id": location.id,
                    "latitude": str(location.latitude),
                    "longitude": str(location.longitude),
                    "city": location.city
                } if location else None,
                "categories": [
                    {"id": cat.id, "name": cat.name} for cat in categories
                ],
                "user": {
                    "id": poster.id,
                    "name": poster.name,
                    "image": poster.image if hasattr(poster, "image") else None
                }
            })

        cache.set(cache_key, tasks, timeout=3600)

        return {
            "tasks": tasks,
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }, 200
