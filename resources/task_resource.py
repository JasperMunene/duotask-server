from flask_restful import Resource, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from sqlalchemy import func, case, or_
from sqlalchemy.orm import joinedload
from models import db
from models.task import Task
from models.task_location import TaskLocation
from models.category import Category
from models.user import User
from models.user_info import UserInfo
from models.task_image import TaskImage
from models.bid import Bid
from models.task_assignment import TaskAssignment
from datetime import datetime, timezone
import math
import logging
import json
import base64
import urllib.parse
from werkzeug.exceptions import HTTPException


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
    parser.add_argument('cursor', type=str, default=None, location='args')
    parser.add_argument('limit', type=int, default=20, location='args')
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
        user_id = get_jwt_identity()
        args = self.parser.parse_args()
        cache = current_app.cache
        cache_key = f"tasks_{args['cursor']}_{args['limit']}_" \
                    f"{args.get('work_mode')}_{args.get('city')}_" \
                    f"{args.get('min_price')}_{args.get('max_price')}_" \
                    f"{args.get('sort')}"

        # Try cached response
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        # Base query with eager loading
        query = Task.query.options(
            joinedload(Task.location),
            joinedload(Task.categories),
            joinedload(Task.user).joinedload(User.user_info)
        ).filter(Task.user_id != user_id)

        # Apply filters and sorting
        query = self._apply_filters(query, args)
        query = self._apply_sorting(query, args)

        # Decode cursor for keyset pagination
        cursor_data = None
        if args['cursor']:
            try:
                decoded_cursor = urllib.parse.unquote(args['cursor'])
                cursor_str = base64.b64decode(decoded_cursor).decode('utf-8')
                cursor_data = json.loads(cursor_str)
            except Exception as e:
                current_app.logger.error(f"Cursor decoding failed: {str(e)}")
                abort(400, message="Invalid cursor format")

        if cursor_data:
            query = self._apply_cursor(query, args['sort'], cursor_data)

        # Fetch limit + 1 to check for next page
        tasks = query.limit(args['limit'] + 1).all()

        next_cursor = None
        if len(tasks) > args['limit']:
            tasks = tasks[:args['limit']]
            next_cursor = self._create_next_cursor(tasks[-1], args['sort'])

        serialized_tasks = [self._serialize_task(t, args) for t in tasks]

        response = {
            'tasks': serialized_tasks,
            'next_cursor': next_cursor
        }

        # Cache response for 5 minutes
        cache.set(cache_key, response, timeout=300)
        return response

    def _apply_cursor(self, query, sort, cursor_data):
        """Apply cursor condition based on sort type"""
        if sort == 'recommended':
            query = query.join(User).join(UserInfo)
            score = UserInfo.rating * 0.7 + UserInfo.completion_rate * 0.3
            return query.filter(
                (score < cursor_data['score']) |
                ((score == cursor_data['score']) & (Task.created_at < cursor_data['created_at'])) |
                ((score == cursor_data['score']) & (Task.created_at == cursor_data['created_at']) &
                 (Task.id < cursor_data['id']))
            )
        elif sort == 'recent':
            return query.filter(Task.id < cursor_data['id'])
        elif sort == 'price':
            return query.filter(
                (Task.budget < cursor_data['budget']) |
                ((Task.budget == cursor_data['budget']) & (Task.id < cursor_data['id']))
            )
        elif sort == 'due_date':
            # For due_date we sort by a computed value
            return query.filter(
                (Task.specific_date < cursor_data['sort_value']) |
                ((Task.specific_date == cursor_data['sort_value']) & (Task.id < cursor_data['id']))
            )
        elif sort == 'distance':
            # Distance sorting requires special handling
            return query.filter(Task.id < cursor_data['id'])
        else:  # Default to ID-based pagination
            return query.filter(Task.id < cursor_data['id'])

    def _create_next_cursor(self, task, sort_type):
        """Create next cursor from last task"""
        cursor_data = {'id': task.id}

        if sort_type == 'recommended':
             # Calculate and include score in cursor
            rating = task.user.user_info.rating if task.user.user_info.rating is not None else 0
            completion_rate = task.user.user_info.completion_rate if task.user.user_info.completion_rate is not None else 0
            score = rating * 0.7 + completion_rate * 0.3
            cursor_data.update({
                'score': float(score),
                'created_at': task.created_at.isoformat()
            })
        elif sort_type == 'price':
            cursor_data['budget'] = float(task.budget)
        elif sort_type == 'due_date':
            # Use computed due date value
            if task.schedule_type == 'specific_day' and task.specific_date:
                cursor_data['sort_value'] = task.specific_date.isoformat()
            elif task.schedule_type == 'before_day' and task.deadline_date:
                cursor_data['sort_value'] = task.deadline_date.isoformat()
            else:
                cursor_data['sort_value'] = task.created_at.isoformat()

        return base64.b64encode(json.dumps(cursor_data).encode('utf-8')).decode('utf-8')

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
            city_filter = f"%{args['city'].lower()}%"
            query = query.filter(
                or_(
                    func.lower(TaskLocation.city).ilike(city_filter),
                    func.lower(TaskLocation.area).ilike(city_filter)
                )
            )
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
        # 1) explicitly pick just the Task columns you need
        serialized = task.to_dict(
            only=(
                'id',
                'title',
                'description',
                'budget',
                'status',
                'schedule_type',
                'specific_date',
                'deadline_date',
                'created_at',   
                'updated_at',
            )
        )

        # 2) pull in exactly the fields you want from location
        if task.location:
            serialized['location'] = task.location.to_dict(
                only=('id', 'city', 'latitude', 'longitude')
            )
        else:
            serialized['location'] = None


        # 3) same for categories
        serialized['categories'] = [        
            c.to_dict(only=('id', 'name')) for c in task.categories
        ]


        serialized['preferred_time'] = str(task.preferred_time)

        
        if task.user_id:
            serialized['user'] = {
                'id': task.user.id,
                'name': task.user.name,
                'image': task.user.image,
            }
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
        parser.add_argument('preferred_time', type=str)
        parser.add_argument('latitude', type=float)
        parser.add_argument('longitude', type=float)
        parser.add_argument('country', type=str)
        parser.add_argument('state', type=str)
        parser.add_argument('city', type=str)
        parser.add_argument('area', type=str)
        parser.add_argument('images', type=str, action='append')


        data = parser.parse_args()
        user_id = get_jwt_identity()

        # Validate business logic
        self._validate_budget(data['budget'])
        self._validate_schedule(data)
        location_data = self._validate_location(data)

        try:
            # Atomic transaction: Create task, add images, and assign temporary category
            task = self._create_task(user_id, data, location_data)
            self._create_images(task, data.get('images', []))

            # Assign temporary "Uncategorized" category; worker will update this later.
            temp_category = self._get_or_create_category("Uncategorized")
            task.categories.append(temp_category)

            db.session.commit()
            self._invalidate_cache()

            # Enqueue background task for AI categorization
            current_app.celery.send_task(
                'workers.tasks.categorize_task',
                args=(task.id,),
                queue='ai_tasks'
            )

            return self._serialize_new_task(task), 201

        except Exception as e:
            db.session.rollback()
            
            print(f"error: {str(e)}")
            logger.error(f"Task creation failed: {str(e)}", exc_info=True)
            abort(500, message="Failed to create task")

    def _validate_budget(self, budget):
        """Validate budget constraints"""
        if budget <= 0 or budget > 1000000:  # $1M max
            abort(400, message="Budget must be between 0.01 and 1,000,000")

    def _validate_schedule(self, data):
        """Validate scheduling constraints."""
        # get “now” as an aware UTC datetime
        now = datetime.now(timezone.utc)

        schedule_type = data.get('schedule_type')
        if schedule_type == 'specific_day':
            raw = data.get('specific_date')
            if not raw:
                abort(400, message="Specific date required for 'specific_day' schedule")

            # parse and ensure tz-aware
            specific = (
                raw if isinstance(raw, datetime)
                else datetime.fromisoformat(raw)
            )
            if specific.tzinfo is None:
                specific = specific.replace(tzinfo=timezone.utc)

            if specific < now:
                abort(400, message="Specific date must be in the future")

        elif schedule_type == 'before_day':
            raw = data.get('deadline_date')
            if not raw:
                abort(400, message="Deadline date required for 'before_day' schedule")

            deadline = (
                raw if isinstance(raw, datetime)
                else datetime.fromisoformat(raw)
            )
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)

            if deadline <= now:
                abort(400, message="Deadline must be in the future")

        elif schedule_type == 'flexible':
            preferred = data.get('preferred_time')
            if preferred:
                allowed_times = {'morning', 'midday', 'afternoon', 'evening'}
                if preferred not in allowed_times:
                    abort(
                        400,
                        message=f"Preferred time must be one of: {', '.join(allowed_times)}"
                    )
        else:
            abort(400, message=f"Unknown schedule_type: {schedule_type}")


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
            with current_app.category_lock:
                category = Category.query.filter(
                    func.lower(Category.name) == func.lower(category_name)
                ).first()
                if not category:
                    category = Category(name=category_name)
                    db.session.add(category)
                    db.session.flush()  # Flush to generate an ID
                return category
        except Exception as e:
            logger.error(f"Category handling failed: {str(e)}")
            abort(500, message="Failed to process task category")

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
            preferred_time=data["preferred_time"] if data["schedule_type"] == "flexible" else None
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
            cache.delete_memoized(self.get)  # Delete memoized cache for task lists

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
            'images': [img.to_dict() for img in fresh_task.images],
            'categorization_status': (
                'pending' if any(c.name.lower() == 'uncategorized' for c in fresh_task.categories)
                else 'complete'
            )
        }

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
        user_id = get_jwt_identity()
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

        serialized = self._serialize_task(task, user_id)

        # Cache response for 5 minutes
        cache.set(cache_key, serialized, timeout=300)

        return serialized

    def _serialize_task(self, task, user_id):
        # 1) Compute average rating
        user_reviews = task.user.reviews_received if task.user else []
        avg_rating = (
            sum(r.rating for r in user_reviews) / len(user_reviews)
            if user_reviews else 0.0
        )

        # 2) Task fields (only the columns you need)
        task_data = task.to_dict(only=(
            'id',
            'title',
            'description',
            'budget',
            'work_mode',
            'status',
            'schedule_type',
            'specific_date',
            'deadline_date',
            'preferred_time',
            'created_at',
            'updated_at',
        ))

        # 3) Location (only its own fields)
        if task.location:
            location_data = task.location.to_dict(only=(
                'id', 'city', 'latitude', 'longitude'
            ))
        else:
            location_data = None

        # 4) Categories (id & name only)
        categories_data = [
            c.to_dict(only=('id', 'name'))
            for c in task.categories
        ]

        # 5) Images (pick only the fields you actually expose)
        images_data = [
            img.to_dict(only=('id', 'image_url'))
            for img in task.images
        ]

        # 6) Assemble user info manually
        user_data = {
            'id': task.user.id,
            'name': task.user.name,
            'rating': avg_rating,
            'completed_tasks': getattr(task.user, 'completed_tasks_count', 0),
            'avatar': task.user.image
        }

        if task.status not in ["open", "cancelled"]:
                assignment = TaskAssignment.query.options(
                    joinedload(TaskAssignment.doer)
                ).filter_by(task_id=task.id, task_doer=user_id).first()

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
        # 7) Metadata
        metadata = {
            'views': self._get_task_views(task.id),
            'popularity_score': self._calculate_popularity(task)
        }

        # 8) Build and return
        response = {
            'task': task_data,
            'location': location_data,
            'categories': categories_data,
            'images': images_data,
            'user': user_data,
            'metadata': metadata
        }

        if hasattr(task, 'distance'):
            response['distance'] = task.distance

        return response

    def _get_task_views(self, task_id):
        # Implement view tracking logic
        return current_app.redis.get(f"task_views_{task_id}") or 0

    def _calculate_popularity(self, task):
        # Example popularity algorithm
        base_score = getattr(task, "bids_count", 0) * 0.5
        time_score = 1 / (1 + (datetime.now() - task.created_at).days)
        return round(base_score + time_score, 2)

    @jwt_required()
    def put(self, task_id):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str)
        parser.add_argument('description', type=str)
        parser.add_argument('work_mode', type=str, choices=['remote', 'physical'])
        parser.add_argument('budget', type=float)
        parser.add_argument('schedule_type', type=str,
                            choices=['specific_day', 'before_day', 'flexible'])
        parser.add_argument('specific_date', type=lambda x: datetime.fromisoformat(x) if x else None)
        parser.add_argument('deadline_date', type=lambda x: datetime.fromisoformat(x) if x else None)
        parser.add_argument('preferred_time', type=str)
        parser.add_argument('latitude', type=float)
        parser.add_argument('longitude', type=float)
        parser.add_argument('country', type=str)
        parser.add_argument('state', type=str)
        parser.add_argument('city', type=str)
        parser.add_argument('area', type=str)
        parser.add_argument('status', type=str, choices=['open', 'in_progress', 'completed', 'cancelled'])
        data = parser.parse_args()

        current_user_id = get_jwt_identity()

        try:
            task = Task.query.filter_by(id=task_id).with_for_update().first()
            if not task:
                abort(404, message="Task not found")
            if str(task.user_id) != current_user_id:
                abort(403, message="Unauthorized to update this task")
            if any(bid.status == 'accepted' for bid in task.bids):
                abort(409, message="Cannot modify task with accepted bids")

            self._validate_and_update_task(task, data)
            self._validate_and_update_location(task, data)
            task.updated_at = db.func.now()
            db.session.commit()
            self._invalidate_cache()
            return self._serialize_updated_task(task), 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Task update failed: {str(e)}", exc_info=True)
            if isinstance(e, HTTPException):
                raise e
            abort(500, message="Failed to update task")

    def _validate_and_update_task(self, task, data):
        if data.get('budget') is not None:
            if data['budget'] <= 0 or data['budget'] > 1000000:
                abort(400, message="Invalid budget amount")
            task.budget = data['budget']

        if data.get('schedule_type') is not None:
            self._validate_schedule_update(task, data)

        if data.get('status') is not None:
            self._validate_status_transition(task.status, data['status'])

        for field in ['title', 'description', 'work_mode', 'status']:
            if data.get(field) is not None:
                setattr(task, field, data[field])

    def _validate_schedule_update(self, task, data):
        now = datetime.now()
        new_schedule_type = data['schedule_type']
        if new_schedule_type == 'specific_day':
            specific_date = data.get('specific_date') or task.specific_date
            if not specific_date:
                abort(400, message="Specific date required for 'specific_day' schedule")
            if specific_date <= now:
                abort(400, message="Specific date must be in the future")
            task.specific_date = specific_date

        elif new_schedule_type == 'before_day':
            deadline_date = data.get('deadline_date') or task.deadline_date
            if not deadline_date:
                abort(400, message="Deadline date required for 'before_day' schedule")
            if deadline_date <= now:
                abort(400, message="Deadline must be in the future")
            task.deadline_date = deadline_date

        elif new_schedule_type == 'flexible':
            preferred_time = data.get('preferred_time') or task.preferred_time
            if not preferred_time:
                abort(400,
                      message="Preferred time (e.g., morning, midday, afternoon, evening) is required for 'flexible' schedule")
            allowed_times = ['morning', 'midday', 'afternoon', 'evening']
            if preferred_time not in allowed_times:
                abort(400, message=f"Preferred time must be one of: {', '.join(allowed_times)}")

            task.preferred_time = preferred_time

    def _validate_location(self, data):
        if data.get('work_mode') == 'physical':
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

    def _validate_status_transition(self, current_status, new_status):
        valid_transitions = {
            'open': ['in_progress', 'cancelled'],
            'in_progress': ['completed', 'cancelled'],
            'completed': [],
            'cancelled': []
        }
        if new_status not in valid_transitions.get(current_status, []):
            abort(400, message=f"Invalid status transition from {current_status} to {new_status}")

    def _validate_and_update_location(self, task, data):
        work_mode = data.get('work_mode') or task.work_mode
        if work_mode == 'physical':
            location_data = self._get_location_data(task, data)
            self._validate_location(location_data)
            if task.location:
                # Manually update each attribute
                for key, value in location_data.items():
                    setattr(task.location, key, value)
            else:
                task.location = TaskLocation(**location_data)
        else:
            if task.location:
                db.session.delete(task.location)

    def _get_location_data(self, task, data):
        return {
            'latitude': data.get('latitude') or (task.location.latitude if task.location else None),
            'longitude': data.get('longitude') or (task.location.longitude if task.location else None),
            'country': data.get('country') or (task.location.country if task.location else None),
            'state': data.get('state') or (task.location.state if task.location else None),
            'city': data.get('city') or (task.location.city if task.location else None),
            'area': data.get('area') or (task.location.area if task.location else None)
        }

    def _invalidate_cache(self):
        """Invalidate relevant cached data"""
        try:
            cache = current_app.cache
            cache.delete_memoized(self.get)  # Delete memoized cache for task lists

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

    def _serialize_updated_task(self, task):
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
            'updated_at': fresh_task.updated_at.isoformat(),
            'location': fresh_task.location.to_dict() if fresh_task.location else None,
            'categories': [c.to_dict() for c in fresh_task.categories],
            'images': [img.to_dict() for img in fresh_task.images],
            'budget': float(fresh_task.budget),
            'schedule_type': fresh_task.schedule_type
        }

    @jwt_required()
    def delete(self, task_id):
        """
        Delete a task (soft or hard delete)
        ---
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
            description: Numeric ID of the task to delete
          - name: permanent
            in: query
            type: boolean
            default: false
            description: Permanently delete the task (irreversible)
        responses:
          204:
            description: Task successfully deleted
          400:
            description: Invalid request parameters
          403:
            description: Unauthorized deletion attempt
          404:
            description: Task not found
          409:
            description: Task has active commitments preventing deletion
        """
        # Parse request parameters
        delete_parser = reqparse.RequestParser()
        delete_parser.add_argument(
            'permanent',
            type=SingleTaskResource.str_to_bool,
            default=False,
            location='args',
            help="Permanent deletion flag must be boolean"
        )
        args = delete_parser.parse_args()
        permanent_deletion = args['permanent']


        current_user_id = get_jwt_identity()

        try:
            # Atomic transaction with row locking
            with db.session.begin_nested():
                task = Task.query.filter_by(id=task_id).with_for_update().first()

                # Validation checks
                if not task:
                    abort(404, message="Task not found")
                if task.is_deleted and not permanent_deletion:
                    abort(410, message="Task already marked as deleted")
                if str(task.user_id) != current_user_id:
                    abort(403, message="Authorization failed: User doesn't own this task")
                if self._has_active_commitments(task):
                    abort(409, message="Task cannot be deleted due to active bids or assignments")

                # Execute deletion strategy
                if permanent_deletion:
                    self._perform_hard_deletion(task)
                else:
                    self._perform_soft_deletion(task)

                # Post-deletion cleanup
                self._invalidate_related_caches(task_id, task.user_id)

            db.session.commit()
            return '', 204

        except ValueError as ve:
            db.session.rollback()
            logger.warning(f"Invalid deletion request: {str(ve)}")
            abort(400, message=str(ve))
        except HTTPException as he:
            db.session.rollback()
            raise he
        except Exception as e:
            db.session.rollback()
            logger.critical(f"Critical deletion failure: {str(e)}", exc_info=True)
            abort(500, message="Internal server error during deletion")

    @staticmethod
    def str_to_bool(value):
        if isinstance(value, bool):
            return value
        if value.lower() in ('true', '1', 'yes'):
            return True
        elif value.lower() in ('false', '0', 'no'):
            return False
        else:
            raise ValueError("Boolean value expected.")

    def _has_active_commitments(self, task):
        """Check for blocking relationships before deletion"""
        active_bids_exist = db.session.query(
            Bid.query.filter_by(
                task_id=task.id,
                status='accepted'
            ).exists()
        ).scalar()

        active_assignments_exist = db.session.query(
            TaskAssignment.query.filter_by(
                task_id=task.id
            ).filter(
                TaskAssignment.status.in_(['assigned', 'in_progress'])
            ).exists()
        ).scalar()

        return active_bids_exist or active_assignments_exist

    def _perform_soft_deletion(self, task):
        """Mark task as deleted while preserving data"""
        task.is_deleted = True
        task.deleted_at = db.func.now()
        task.status = 'cancelled'

        # Update related entities
        Bid.query.filter_by(task_id=task.id).update(
            {'status': 'rejected'},
            synchronize_session=False
        )

        TaskAssignment.query.filter_by(task_id=task.id).update(
            {'status': 'cancelled'},
            synchronize_session=False
        )

    def _perform_hard_deletion(self, task):
        """Permanently remove task and related data from system"""
        # Delete associated records
        TaskLocation.query.filter_by(task_id=task.id).delete()
        TaskImage.query.filter_by(task_id=task.id).delete()

        # Clear many-to-many relationships
        task.categories = []

        # Delete core task record
        db.session.delete(task)

    def _invalidate_related_caches(self, task_id, user_id):
        """System-wide cache invalidation for task data"""
        try:
            redis = current_app.redis
            cache = current_app.cache

            # Invalidate individual task cache
            cache.delete(f"task_{task_id}")

            # Pattern-based cache clearance
            patterns = [
                'tasks_*',
                f'user_tasks_{user_id}_*',
                f'user_activity_{user_id}',
                f'task_stats_{task_id}'
            ]

            for pattern in patterns:
                cursor, keys = 0, []
                while True:
                    cursor, partial = redis.scan(
                        cursor=cursor,
                        match=pattern,
                        count=1000
                    )
                    keys.extend(partial)
                    if cursor == 0:
                        break
                if keys:
                    redis.delete(*keys)

        except Exception as cache_error:
            logger.error(f"Cache invalidation error: {str(cache_error)}")


class TaskStatusResource(Resource):
    """
    Resource for updating the status of a single task.
    Supports only validated state transitions and enforces
    business rules around assignment and side-effects.
    """
    # Parser to validate incoming JSON payload
    parser = reqparse.RequestParser()
    parser.add_argument(
        'status',
        type=str,
        required=True,
        choices=['in_progress', 'completed', 'cancelled'],
        help="Invalid status. Allowed: in_progress, completed, cancelled"
    )

    @jwt_required()
    def put(self, task_id):
        """
        HTTP PUT /tasks/<task_id>/status
        1. Authenticate user
        2. Load & lock task row
        3. Validate transition & business rules
        4. Persist new status & timestamp
        5. Commit and trigger cache invalidation + notifications
        """
        # 1. Validate JWT identity
        try:
            current_user_id = int(get_jwt_identity())
        except (TypeError, ValueError):
            abort(403, message="Invalid user identity")

        # 2. Parse and validate input
        args = self.parser.parse_args()
        new_status = args['status']

        try:
            # Use a nested transaction so we can rollback on validation failures
            with db.session.begin_nested():
                # Acquire row-level lock to prevent concurrent updates
                task = (
                    db.session.query(Task)
                              .filter_by(id=task_id, is_deleted=False)
                              .with_for_update()
                              .first()
                )
                if not task:
                    abort(404, message="Task not found")
                if task.user_id != current_user_id:
                    abort(403, message="Unauthorized to update this task")

                current_status = task.status

                # 3a. State machine validation
                self._validate_transition(current_status, new_status)
                # 3b. Business-rule validation (assignment state)
                self._validate_business_rules(task, new_status)

                # 4. Apply status change
                task.status = new_status
                task.updated_at = datetime.utcnow()

                # 5. Handle side-effects (bids, assignment, stats)
                self._handle_status_side_effects(task, new_status)

            # Commit DB changes
            db.session.commit()

            # After commit: clear caches & enqueue notifications
            self._invalidate_caches(task_id)
            self._send_notifications(task, current_status, new_status)

            return {
                'message': 'Task status updated successfully',
                'task_id': task_id,
                'new_status': new_status
            }, 200

        except HTTPException:
            # Re-raise HTTP errors (abort)
            db.session.rollback()
            raise
        except Exception as e:
            # Log & return 500 on unexpected failures
            db.session.rollback()
            logger.error(f"Status update failed for task {task_id}: {e}", exc_info=True)
            abort(500, message="Internal server error during status update")

    def _validate_transition(self, current_status, new_status):
        """
        Ensure that new_status is a valid next step from current_status.
        Uses a simple state machine map.
        """
        valid_transitions = {
            'open':         ['in_progress', 'cancelled'],
            'in_progress':  ['completed', 'cancelled'],
            'completed':    [],
            'cancelled':    []
        }
        allowed = valid_transitions.get(current_status, [])
        if new_status not in allowed:
            abort(400, message=f"Invalid transition: {current_status} → {new_status}")

    def _validate_business_rules(self, task, new_status):
        """
        Enforce domain-specific rules before allowing transition:
          - Must be assigned before moving to in_progress
          - Must be in_progress before moving to completed
        """
        assignment = TaskAssignment.query.filter_by(task_id=task.id).first()

        if new_status == 'in_progress':
            if not assignment or assignment.status != 'assigned':
                abort(409, message="Task must be assigned before starting progress")
        elif new_status == 'completed':
            if not assignment or assignment.status != 'in_progress':
                abort(409, message="Task must be in progress before completing")

    def _handle_status_side_effects(self, task, new_status):
        """
        Update related models when status changes:
          - Reject pending bids on cancellation
          - Update assignment and user stats
        """
        assignment = TaskAssignment.query.filter_by(task_id=task.id).first()

        if new_status == 'cancelled':
            # Reject any pending or accepted bids
            (
                Bid.query
                   .filter_by(task_id=task.id)
                   .filter(Bid.status.in_(['pending', 'accepted']))
                   .update({'status': 'rejected'}, synchronize_session=False)
            )
            # Mark assignment cancelled
            if assignment:
                assignment.status = 'cancelled'
                db.session.add(assignment)
            # Increment owner's cancelled count
            self._update_user_stats(task, action='cancelled')

        elif new_status == 'completed':
            # Mark assignment completed
            if assignment:
                assignment.status = 'completed'
                db.session.add(assignment)
            # Increment doer's completed count
            self._update_user_stats(task, action='completed')

        elif new_status == 'in_progress':
            # Mark assignment in_progress
            if assignment:
                assignment.status = 'in_progress'
                db.session.add(assignment)

    def _update_user_stats(self, task, action):
        """
        Atomically update user statistics based on action:
          - 'completed': increment doer’s completed_tasks_count
          - 'cancelled': increment owner’s cancelled_tasks_count
        """
        if action == 'completed':
            assign = TaskAssignment.query.filter_by(task_id=task.id).first()
            if assign:
                User.query.filter_by(id=assign.task_doer).update(
                    {User.completed_tasks_count: User.completed_tasks_count + 1}
                )
        elif action == 'cancelled':
            User.query.filter_by(id=task.user_id).update(
                {User.cancelled_tasks_count: User.cancelled_tasks_count + 1}
            )

    def _invalidate_caches(self, task_id):
        """
        Remove stale cache entries after status change:
         - task detail
         - any paginated task lists
        """
        try:
            redis_cli = current_app.redis
            redis_cli.delete(f"task_{task_id}")
            for key in redis_cli.scan_iter("tasks_*"):
                redis_cli.delete(key)
        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")

    def _send_notifications(self, task, old_status, new_status):
        """
        Enqueue notifications via Celery based on new_status:
          - On completion, notify owner & queue rating reminders
          - On cancellation, notify doer
        """
        try:
            assign = TaskAssignment.query.filter_by(task_id=task.id).first()
            if not assign:
                return

            if new_status == 'completed':
                current_app.celery.send_task(
                    'notifications.task_completed',
                    args=(task.user_id, assign.task_doer, task.id),
                    queue='notifications'
                )
                current_app.celery.send_task(
                    'workers.ratings.queue_rating_reminders',
                    args=(task.id,),
                    queue='background'
                )
            elif new_status == 'cancelled':
                current_app.celery.send_task(
                    'notifications.task_cancelled',
                    args=(assign.task_doer, task.id),
                    queue='notifications'
                )
        except Exception as e:
            logger.error(f"Notification enqueue failed: {e}")

