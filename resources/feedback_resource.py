from flask import request
from models import db
from models.feedback import Feedback
from flask_restful import Resource

class Feedback_resource(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return {"message": "Invalid or missing JSON payload"}, 400

        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not all([name, email, message]):
            return {"message": "Missing required fields"}, 400

        feedback = Feedback(name=name, email=email, message=message)
        
        db.session.add(feedback)
        db.session.commit()

        return {
            "message": "success",
            "data": {
                "name": feedback.name,
                "email": feedback.email,
                "message": feedback.message
            }
        }, 201

    def get(self):
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)

        feedback_query = Feedback.query.order_by(Feedback.created_at.desc())
        paginated = feedback_query.paginate(page=page, per_page=limit, error_out=False)

        feedbacks = [
            {
                "id": f.id,
                "name": f.name,
                "email": f.email,
                "message": f.message,
                "created_at": f.created_at.isoformat()
            }
            for f in paginated.items
        ]

        return {
            "feedbacks": feedbacks,
            "page": page,
            "limit": limit,
            "total": paginated.total,
            "has_next": paginated.has_next,
            "has_prev": paginated.has_prev
        }, 200
