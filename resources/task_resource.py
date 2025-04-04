# task_resource.py
from flask_restful import Resource, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload
from models import db
from models.task import Task
from models.task_location import TaskLocation
from models.category import Category
from models.user import User
from models.user_info import UserInfo
from models.task_image import TaskImage
from datetime import datetime
import os
import math
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

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

    @jwt_required()
    def post(self):
        """Create a new task with validation and atomic operations"""
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True,
                            help='Task title is required')
        parser.add_argument('description', type=str, required=True,
                            help='Task description is required')
        parser.add_argument('work_mode', type=str, required=True,
                            choices=['remote', 'physical'],
                            help='Invalid work mode. Allowed: remote, physical')
        parser.add_argument('budget', type=float, required=True,
                            help='Budget must be a positive number')
        parser.add_argument('schedule_type', type=str, required=True,
                            choices=['specific_day', 'before_day', 'flexible'],
                            help='Invalid schedule type')
        parser.add_argument('specific_date', type=lambda x: datetime.fromisoformat(x) if x else None)
        parser.add_argument('deadline_date', type=lambda x: datetime.fromisoformat(x) if x else None)
        parser.add_argument('preferred_start_time', type=lambda x: datetime.strptime(x, '%H:%M').time() if x else None)
        parser.add_argument('preferred_end_time', type=lambda x: datetime.strptime(x, '%H:%M').time() if x else None)
        parser.add_argument('latitude', type=float)
        parser.add_argument('longitude', type=float)
        parser.add_argument('country', type=str)
        parser.add_argument('state', type=str)
        parser.add_argument('city', type=str)
        parser.add_argument('area', type=str)
        parser.add_argument('images', type=str, action='append')
        # Note: No category_ids argument – category will be generated via AI.

        data = parser.parse_args()
        user_id = get_jwt_identity()  # Assumes JWT is used for authentication

        # Validate business logic
        self._validate_budget(data['budget'])
        self._validate_schedule(data)
        location_data = self._validate_location(data)

        try:
            generated_category_name = self._categorize_task(data['title'], data['description'])
        except Exception as e:
            logger.error(f"AI categorization failed: {str(e)}")
            generated_category_name = "Uncategorized"

        # Normalize and find/create category
        category_name = generated_category_name.strip().title()
        category = self._get_or_create_category(category_name)

        try:
            # Atomic transaction: Create task, add images, and link category
            task = self._create_task(user_id, data, location_data)
            self._create_images(task, data.get('images', []))
            self._link_category(task, category)

            db.session.commit()
            self._invalidate_cache()

            return self._serialize_new_task(task), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Task creation failed: {str(e)}", exc_info=True)
            abort(500, message="Failed to create task")

    def _validate_budget(self, budget):
        """Validate budget constraints"""
        if budget <= 0 or budget > 1000000:  # $1M max
            abort(400, message="Budget must be between 0.01 and 1,000,000")

    def _validate_schedule(self, data):
        """Validate scheduling constraints"""
        now = datetime.now()

        if data['schedule_type'] == 'specific_day':
            if not data['specific_date']:
                abort(400, message="Specific date required for 'specific_day' schedule")
            if data['specific_date'] <= now:
                abort(400, message="Specific date must be in the future")

        elif data['schedule_type'] == 'before_day':
            if not data['deadline_date']:
                abort(400, message="Deadline date required for 'before_day' schedule")
            if data['deadline_date'] <= now:
                abort(400, message="Deadline must be in the future")

        elif data['schedule_type'] == 'flexible':
            if not data['preferred_start_time'] or not data['preferred_end_time']:
                abort(400, message="Start and end times required for 'flexible' schedule")
            if data['preferred_start_time'] >= data['preferred_end_time']:
                abort(400, message="Start time must be before end time")

    def _validate_location(self, data):
        """Validate and extract location data"""
        if data['work_mode'] == 'physical':
            required = ['latitude', 'longitude', 'country', 'state', 'city']
            missing = [field for field in required if not data.get(field)]
            if missing:
                abort(400, message=f"Missing location fields: {', '.join(missing)}")

            if not (-90 <= data['latitude'] <= 90):
                abort(400, message="Invalid latitude (range: -90 to 90)")
            if not (-180 <= data['longitude'] <= 180):
                abort(400, message="Invalid longitude (range: -180 to 180)")

            return {
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'country': data['country'],
                'state': data['state'],
                'city': data['city'],
                'area': data.get('area')
            }
        return None

    def _get_or_create_category(self, category_name):
        """Thread-safe category retrieval/creation"""
        try:
            # Use mutex lock for category creation to prevent race conditions
            with current_app.category_lock:
                category = Category.query.filter(
                    func.lower(Category.name) == func.lower(category_name)
                ).first()

                if not category:
                    category = Category(name=category_name)
                    db.session.add(category)
                    db.session.flush()  # Flush to get ID without commit

                return category
        except Exception as e:
            logger.error(f"Category handling failed: {str(e)}")
            abort(500, message="Failed to process task category")

    def _categorize_task(self, title, description):
        """Improved AI categorization with proper error handling"""
        try:
            # Retrieve AI model from the app attribute
            model = current_app.ai_model
            if not model:
                raise ValueError("AI model not configured")

            # Get existing categories once per request
            existing_categories = Category.query.with_entities(Category.name).all()
            category_names = [c[0] for c in existing_categories]

            # Structured prompt with examples
            prompt = f"""Task Categorization Guide:
1. Analyze this task: "{title}" - {description}
2. Existing categories: {', '.join(category_names) or 'None'}
3. Choose BEST existing category or create new one
4. Return ONLY the category name
Examples:
- "Need plumbing help" → "Plumbing"
- "Logo design needed" → "Graphic Design"
Output:"""

            # Configure API call
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=20,
                    candidate_count=1
                )
            )

            # Validate response structure
            if not response:
                raise ValueError("No candidates in AI response")

            category = response.text.strip().title()

            # Basic sanitization
            return category[:50].strip(' .') or "Uncategorized"

        except Exception as e:
            logger.error(f"AI Categorization error: {str(e)}")
            return "Uncategorized"

    def _link_category(self, task, category):
        """Link the generated or existing category to the task."""
        task.categories.append(category)

    def _create_task(self, user_id, data, location_data):
        """Create task and associated location"""
        task = Task(
            user_id=user_id,
            title=data['title'],
            description=data['description'],
            work_mode=data['work_mode'],
            budget=data['budget'],
            schedule_type=data['schedule_type'],
            specific_date=data.get('specific_date'),
            deadline_date=data.get('deadline_date'),
            preferred_start_time=data.get('preferred_start_time'),
            preferred_end_time=data.get('preferred_end_time')
        )

        db.session.add(task)
        db.session.flush()  # Generate task ID

        if location_data:
            task.location = TaskLocation(**location_data)

        return task

    def _create_images(self, task, image_urls):
        """Bulk create task images"""
        if image_urls:
            images = [TaskImage(task_id=task.id, image_url=url) for url in image_urls]
            db.session.bulk_save_objects(images)

    def _invalidate_cache(self):
        """Invalidate relevant cached data"""
        try:
            cache = current_app.cache
            # Delete memoized cache for task lists
            cache.delete_memoized(self.get)
            # Delete pattern-based keys using Redis directly
            redis_conn = current_app.redis
            cursor = 0
            keys = []
            while True:
                cursor, partial = redis_conn.scan(cursor=cursor, match='tasks_*')
                keys.extend(partial)
                if cursor == 0:
                    break
            if keys:
                redis_conn.delete(*keys)
        except Exception as e:
            logger.error(f"Cache invalidation failed: {str(e)}")

    def _serialize_new_task(self, task):
        """Eager load and serialize new task"""
        fresh_task = Task.query.options(
            joinedload(Task.location),
            joinedload(Task.categories),
            joinedload(Task.images),
            joinedload(Task.user).joinedload(User.user_info)
        ).get(task.id)

        return {
            'id': fresh_task.id,
            'title': fresh_task.title,
            'status': fresh_task.status,
            'created_at': fresh_task.created_at.isoformat(),
            'location': fresh_task.location.to_dict() if fresh_task.location else None,
            'categories': [c.to_dict() for c in fresh_task.categories],
            'images': [img.to_dict() for img in fresh_task.images]
        }

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
        # Implement view tracking logic
        return current_app.redis.get(f"task_views_{task_id}") or 0

    def _calculate_popularity(self, task):
        # Example popularity algorithm
        base_score = getattr(task, "bids_count", 0) * 0.5
        time_score = 1 / (1 + (datetime.now() - task.created_at).days)
        return round(base_score + time_score, 2)
