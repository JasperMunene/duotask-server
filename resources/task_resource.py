# task_resource.py
from flask_restful import Resource, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from flask_limiter import Limiter  # Ensure you have a global limiter instance attached to your app
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload
from models.task import Task
from models.task_location import TaskLocation
from models.category import Category
from models.user import User
from models.user_info import UserInfo
from datetime import datetime
import math

# Haversine formula for distance calculation
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class TaskResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=20, location='args',
                        choices=[10, 20, 50, 100], help='Invalid items per page')
    parser.add_argument('work_mode', type=str, location='args',
                        choices=['remote', 'physical'])
    parser.add_argument('category_ids', type=int, action='append', location='args')
    parser.add_argument('min_price', type=float, location='args')
    parser.add_argument('max_price', type=float, location='args')
    parser.add_argument('city', type=str, location='args')
    parser.add_argument('radius', type=float, location='args')
    parser.add_argument('lat', type=float, location='args')
    parser.add_argument('lon', type=float, location='args')
    parser.add_argument('sort', type=str, location='args',
                        choices=['price', 'distance', 'due_date', 'recent', 'recommended'],
                        default='recent')

    @jwt_required()
    def get(self):
        args = self.parser.parse_args()
        cache = current_app.cache
        cache_key = f"tasks_{str(args)}"

        # Try cached response
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        # Base query with eager loading
        query = Task.query.options(
            joinedload(Task.location),
            joinedload(Task.categories),
            joinedload(Task.user).joinedload(User.user_info)
        )

        # Apply filters
        query = self._apply_filters(query, args)

        # Apply sorting
        query = self._apply_sorting(query, args)

        # Pagination
        paginated = query.paginate(
            page=args['page'],
            per_page=args['per_page'],
            error_out=False
        )

        # Process results
        tasks = []
        for task in paginated.items:
            task_data = self._serialize_task(task, args)
            tasks.append(task_data)

        # Build response
        response = {
            'tasks': tasks,
            'pagination': {
                'page': paginated.page,
                'per_page': paginated.per_page,
                'total_pages': paginated.pages,
                'total_items': paginated.total
            }
        }

        # Cache response for 5 minutes
        cache.set(cache_key, response, timeout=300)
        return response

    def _apply_filters(self, query, args):
        # Work mode filter
        if args['work_mode']:
            query = query.filter(Task.work_mode == args['work_mode'])

        # Category filter
        if args['category_ids']:
            query = query.filter(Task.categories.any(Category.id.in_(args['category_ids'])))

        # Price range filter
        if args['min_price'] is not None:
            query = query.filter(Task.budget >= args['min_price'])
        if args['max_price'] is not None:
            query = query.filter(Task.budget <= args['max_price'])

        # Apply location filters with a single join if needed
        if args['city'] or (args['radius'] and args['lat'] and args['lon']):
            query = query.join(TaskLocation)
        if args['city']:
            query = query.filter(func.lower(TaskLocation.city) == func.lower(args['city']))
        if args['radius'] and args['lat'] and args['lon']:
            query = query.filter(
                TaskLocation.latitude.between(
                    args['lat'] - (args['radius'] / 111),
                    args['lat'] + (args['radius'] / 111)
                ),
                TaskLocation.longitude.between(
                    args['lon'] - (args['radius'] / (111 * math.cos(math.radians(args['lat'])))),
                    args['lon'] + (args['radius'] / (111 * math.cos(math.radians(args['lat']))))
                )
            )

        return query.filter(Task.status == 'open')

    def _apply_sorting(self, query, args):
        sort = args['sort']
        if sort == 'price':
            return query.order_by(Task.budget.desc())
        elif sort == 'distance' and args['lat'] and args['lon']:
            # Join TaskLocation if not already joined via filters
            if not (args['city'] or (args['radius'] and args['lat'] and args['lon'])):
                query = query.join(TaskLocation)
            return query.order_by(
                func.abs(TaskLocation.latitude - args['lat']) +
                func.abs(TaskLocation.longitude - args['lon'])
            )
        elif sort == 'due_date':
            return query.order_by(
                case(
                    [
                        (Task.schedule_type == 'specific_day', Task.specific_date),
                        (Task.schedule_type == 'before_day', Task.deadline_date)
                    ],
                    else_=Task.created_at
                ).asc()
            )
        elif sort == 'recommended':
            return query.order_by(
                (UserInfo.rating * 0.7 + UserInfo.completion_rate * 0.3).desc(),
                Task.created_at.desc()
            )
        return query.order_by(Task.created_at.desc())

    def _serialize_task(self, task, args):
        serialized = task.to_dict()
        serialized['location'] = task.location.to_dict() if task.location else None
        serialized['categories'] = [c.to_dict() for c in task.categories]

        # Aggregate ratings from reviews_received (assuming the User model has a 'reviews_received' relationship)
        user = task.user
        user_reviews = getattr(user, 'reviews_received', [])
        if user_reviews:
            avg_rating = sum(review.rating for review in user_reviews) / len(user_reviews)
        else:
            avg_rating = 0.0

        serialized['user'] = {
            'name': user.name,
            'rating': avg_rating
        }

        # Add preferred time range with start and end times
        serialized['preferred_time'] = {
            'start': str(task.preferred_start_time) if task.preferred_start_time else None,
            'end': str(task.preferred_end_time) if task.preferred_end_time else None,
        }

        # Add distance calculation if coordinates provided
        if args['lat'] and args['lon'] and task.location:
            serialized['distance'] = haversine(
                args['lat'], args['lon'],
                float(task.location.latitude),
                float(task.location.longitude)
            )

        return serialized


# Single Task Resource with rate limiting
class SingleTaskResource(Resource):
    @jwt_required()
    def get(self, task_id):
        """
        Get single task details.
        ---
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Task details
          404:
            description: Task not found
        """
        # Validate task ID
        if not isinstance(task_id, int) or task_id < 1:
            abort(400, message="Invalid task ID format")

        cache = current_app.cache
        cache_key = f"task_{task_id}"

        # Try cached response
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        # Eager load all relationships in a single query
        task = Task.query.options(
            joinedload(Task.location),
            joinedload(Task.categories),
            joinedload(Task.images),
            joinedload(Task.user).joinedload(User.user_info)
        ).get(task_id)

        if not task or task.status == 'deleted':
            abort(404, message="Task not found")

        serialized = self._serialize_task(task)

        # Cache response for 5 minutes
        cache.set(cache_key, serialized, timeout=300)

        return serialized

    def _serialize_task(self, task):
        # Calculate average rating from reviews_received
        user_reviews = task.user.reviews_received if task.user else []
        avg_rating = (sum(review.rating for review in user_reviews) / len(user_reviews)
                      if user_reviews else 0.0)

        response = {
            "task": task.to_dict(rules=(
                '-user.tasks',
                '-location.tasks',
                '-categories.tasks',
                '-images.task'
            )),
            "location": task.location.to_dict() if task.location else None,
            "categories": [c.to_dict() for c in task.categories],
            "images": [img.to_dict() for img in task.images],
            "user": {
                "id": task.user.id,
                "name": task.user.name,
                "rating": avg_rating,
                "completed_tasks": getattr(task.user, "completed_tasks_count", 0),
                "avatar": task.user.image
            },
            "metadata": {
                "views": self._get_task_views(task.id),
                "popularity_score": self._calculate_popularity(task)
            }
        }

        # If a distance attribute is present, include it
        if hasattr(task, 'distance'):
            response["distance"] = task.distance

        return response

    def _get_task_views(self, task_id):
        # Implement view tracking logic (e.g., using Redis)
        return current_app.redis.get(f"task_views_{task_id}") or 0

    def _calculate_popularity(self, task):
        # Example popularity algorithm (adjust weights as needed)
        base_score = getattr(task, "bids_count", 0) * 0.5
        time_score = 1 / (1 + (datetime.now() - task.created_at).days)
        return round(base_score + time_score, 2)