from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from models import db
from models.user import User
from models.user_info import UserInfo
from models.review import Review


class UserProfileResource(Resource):
    @jwt_required()
    def get(self):
        """Retrieve user profile with caching"""
        user_id = get_jwt_identity()
        cache_key = f"user_profile_{user_id}"

        # Try to get cached response
        cache = current_app.cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data, 200

        # Optimized database query with eager loading
        user = User.query.options(joinedload(User.user_info)).get(user_id)

        if not user:
            return {"message": "User not found"}, 404

        response_data = {
            "image_url": user.image,
            "user_info": user.user_info.to_dict() if user.user_info else None
        }

        # Cache response for 5 minutes (300 seconds)
        current_app.cache.set(cache_key, response_data, timeout=300)
        return response_data, 200

    @jwt_required()
    def post(self):
        """Create profile with cache invalidation"""
        user_id = get_jwt_identity()
        data = request.get_json()

        # Use optimized query with eager loading
        user = User.query.options(joinedload(User.user_info)).get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        if user.user_info:
            return {"message": "User info already exists. Use PATCH to update."}, 400

        # Validate required fields
        if not all(k in data for k in ('tagline', 'bio')):
            return {"message": "Missing required fields"}, 400

        new_info = UserInfo(
            user_id=user_id,
            tagline=data['tagline'],
            bio=data['bio']
        )

        db.session.add(new_info)
        db.session.commit()

        # Invalidate cache
        current_app.cache.delete(f"user_profile_{user_id}")

        return {
            "message": "Profile created successfully",
            "data": new_info.to_dict()
        }, 201

    @jwt_required()
    def patch(self):
        """Update profile with cache invalidation"""
        user_id = get_jwt_identity()
        data = request.get_json()

        # Optimized query with eager loading
        user = User.query.options(joinedload(User.user_info)).get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        updates = {}
        if "image_url" in data:
            user.image = data["image_url"]

        user_info = user.user_info or UserInfo(user_id=user_id)

        # Track changes for audit logging
        update_fields = ['tagline', 'bio', 'rating', 'completion_rate']
        for field in update_fields:
            if field in data:
                setattr(user_info, field, data[field])
                updates[field] = data[field]

        if not user_info.id:
            db.session.add(user_info)

        db.session.commit()

        # Invalidate cache only if changes occurred
        if updates or "image_url" in data:
            current_app.cache.delete(f"user_profile_{user_id}")

        return {
            "message": "Profile updated successfully",
            "updates": updates
        }, 200

    @jwt_required()
    def delete(self):
        """Delete profile with cache invalidation"""
        user_id = get_jwt_identity()

        # Optimized query with eager loading
        user = User.query.options(joinedload(User.user_info)).get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        user.image = None
        if user.user_info:
            db.session.delete(user.user_info)

        db.session.commit()

        # Invalidate cache
        current_app.cache.delete(f"user_profile_{user_id}")

        return {"message": "Profile deleted successfully"}, 204




class UserProfile(Resource):
    def get(self, user_id):
        # Pagination (can be made dynamic)
        page = 1
        limit = 10

        cache = current_app.cache
        cache_key = f"user_profile:{user_id}:page:{page}:limit:{limit}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response, 200

        user = User.query.options(joinedload(User.user_info)).get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        reviews_query = Review.query.options(joinedload(Review.reviewer)).filter_by(
            reviewee_id=user_id
        ).order_by(Review.created_at.desc())
        paginated = reviews_query.paginate(page=page, per_page=limit, error_out=False)

        reviews = []
        for review in paginated.items:
            reviewer = review.reviewer
            reviews.append({
                "id": review.id,
                "task_assignment_id": review.task_assignment_id,
                "reviewer_id": review.reviewer_id,
                "reviewee_id": review.reviewee_id,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.isoformat() if review.created_at else None,
                "reviewer": _get_user_data(reviewer) if reviewer else None
            })

        response = {
            "user": _get_user_data(user),
            "basic_info": {
                "tagline": user.user_info.tagline if user.user_info else None,
                "bio": user.user_info.bio if user.user_info else None
            },
            "reviews": reviews,
            "pagination": {
                "page": page,
                "limit": limit,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev,
                "total": paginated.total
            }
        }

        # Cache the response for 5 minutes
        cache.set(cache_key, response, timeout=60 * 5)

        return response, 200

def _get_user_data(user):
    """Helper to extract user data with average rating."""
    user_reviews = user.reviews_received or []
    avg_rating = (
        sum(r.rating for r in user_reviews) / len(user_reviews)
        if user_reviews else 0.0
    )
    return {
        "id": user.id,
        "name": user.name,
        "rating": avg_rating,
        "completed_tasks": getattr(user, 'completed_tasks_count', 0),
        "avatar": user.image
    }
         
class UserHealthResource(Resource):
    def get(self):
        try:
            current_app.redis.ping()
            return {"cache_status": "connected"}, 200
        except Exception:
            return {"cache_status": "Disconnected"}, 200