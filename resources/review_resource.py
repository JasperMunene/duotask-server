from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, current_app
from models import db
from models.review import Review
from sqlalchemy.orm import joinedload  # Make sure this is imported

class ReviewListResource(Resource):
    @jwt_required()
    def get(self, user_id):
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        cache_key = f"reviews:{user_id}:page:{page}:limit:{limit}"

        cached = current_app.cache.get(cache_key)
        if cached:
            return cached, 200

        reviews_query = Review.query.options(joinedload(Review.reviewer)).filter_by(
            reviewee_id=user_id
        ).order_by(Review.created_at.desc())
        
        paginated = reviews_query.paginate(page=page, per_page=limit, error_out=False)

        reviews = []
        for review in paginated.items:
            reviewer = review.reviewer
            reviews.append({
                "review": {
                    "id": review.id,
                    "task_assignment_id": review.task_assignment_id,
                    "reviewer_id": review.reviewer_id,
                    "reviewee_id": review.reviewee_id,
                    "rating": review.rating,
                    "comment": review.comment,
                    "created_at": review.created_at.isoformat() if review.created_at else None,
                    "reviewer": _get_user_data(reviewer) if reviewer else None
                }
            })

        response = {
            "reviews": reviews,
            "page": page,
            "limit": limit,
            "has_next": paginated.has_next,
            "has_prev": paginated.has_prev,
            "total": paginated.total
        }

        current_app.cache.set(cache_key, response, timeout=60 * 5)

        return response, 200


    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('task_assignment_id', type=int, required=True)
        parser.add_argument('reviewee_id', type=int, required=True)
        parser.add_argument('rating', type=float, required=True)
        parser.add_argument('comment', type=str)
        args = parser.parse_args()

        reviewer_id = get_jwt_identity()

        review = Review(
            task_assignment_id=args['task_assignment_id'],
            reviewer_id=reviewer_id,
            reviewee_id=args['reviewee_id'],
            rating=args['rating'],
            comment=args['comment']
        )

        db.session.add(review)
        db.session.commit()

        # Optional: clear relevant cached pages
        for i in range(1, 6):  # Assume first 5 pages could be affected
            current_app.cache.delete(f"reviews:page:{i}:limit:10")

        return {"review": {
                    "id": review.id,
                    "task_assignment_id": review.task_assignment_id,
                    "reviewer_id": review.reviewer_id,
                    "reviewee_id":review.reviewee_id,
                    "rating": review.rating,
                    "comment": review.comment,
                    "reviewer": _get_user_data(review.reviewer) if review.reviewer else None
                }
                }, 201

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
class ReviewResource(Resource):
    @jwt_required()
    def get(self, review_id):
        cache_key = f"review:{review_id}"
        cached = current_app.cache.get(cache_key)

        if cached:
            return cached, 200

        review = Review.query.get_or_404(review_id)
        result = {"review": {
                    "id": review.id,
                    "task_assignment_id": review.task_assignment_id,
                    "reviewer_id": review.reviewer_id,
                    "reviewee_id":review.reviewee_id,
                    "rating": review.rating,
                    "comment": review.comment,
                    "reviewer": _get_user_data(review.reviewer) if review.reviewer else None
                }
                }

        current_app.cache.set(cache_key, result, timeout=60 * 5)  # Cache for 5 mins
        return result, 200

    @jwt_required()
    def put(self, review_id):
        review = Review.query.get_or_404(review_id)
        reviewer_id = get_jwt_identity()

        if review.reviewer_id != reviewer_id:
            return {"message": "Unauthorized"}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('rating', type=float)
        parser.add_argument('comment', type=str)
        args = parser.parse_args()

        if args['rating'] is not None:
            review.rating = args['rating']
        if args['comment'] is not None:
            review.comment = args['comment']

        db.session.commit()

        result = {"review": {
                    "id": review.id,
                    "task_assignment_id": review.task_assignment_id,
                    "reviewer_id": review.reviewer_id,
                    "reviewee_id":review.reviewee_id,
                    "rating": review.rating,
                    "comment": review.comment
                }
                }
        current_app.cache.set(f"review:{review_id}", result, timeout=60 * 5)

        return result, 200

    @jwt_required()
    def delete(self, review_id):
        review = Review.query.get_or_404(review_id)
        reviewer_id = get_jwt_identity()

        if review.reviewer_id != reviewer_id:
            return {"message": "Unauthorized"}, 403

        db.session.delete(review)
        db.session.commit()

        current_app.cache.delete(f"review:{review_id}")

        # Optionally clear first few pages of review list cache too
        for i in range(1, 6):
            current_app.cache.delete(f"reviews:page:{i}:limit:10")

        return {"message": "Review deleted"}, 200