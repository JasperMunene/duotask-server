from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.user import User
from models.user_relation import UserRelation


class UserRelations(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        other_user_id = data.get('other_user')
        relation = data.get('relation', 'tasker')  # Default relation type

        # Check if both users exist
        user = User.query.get(user_id)
        other_user = User.query.get(other_user_id)

        if not other_user_id:
            return {"message": "missing requirement: other_user_id"}, 404
        
        if not user or not other_user:
            return {"message": "User not found"}, 404

        # Optional: Check if relation already exists
        existing = UserRelation.query.filter_by(
            user_id=user_id,
            related_user_id=other_user_id
        ).first()
        if existing:
            return {"message": "Relation already exists"}, 400

        new_relation = UserRelation(
            user_id=user_id,
            related_user_id=other_user_id,
            relation_type=relation
        )

        db.session.add(new_relation)
        db.session.commit()

        # Invalidate related caches
        cache = current_app.cache
        cache.delete(f"user_relations_{user_id}")
        cache.delete(f"user_relation_{user_id}_{other_user_id}")

        return {
            "message": "success",
            "data": {
                    "user_id": new_relation.user_id,
                    "related_user_id" :new_relation.related_user_id,
                    "relation_type" : new_relation.relation_type
                    }}, 201

    @jwt_required()
    def get(self, other_user_id=None):
        user_id = get_jwt_identity()
        cache = current_app.cache

        if other_user_id:
            cache_key = f"user_relation_{user_id}_{other_user_id}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return {"data": cached_data}, 200

            relation = UserRelation.query.filter_by(
                user_id=user_id,
                related_user_id=other_user_id
            ).first()

            if not relation:
                return {"message": "Relation not found"}, 404

            data =  {
                    "user_id": relation.user_id,
                    "related_user_id" :relation.related_user_id,
                    "relation_type" : relation.relation_type
                    }
            cache.set(cache_key, data, timeout=300)
            return {"data": data}, 200
        else:
            cache_key = f"user_relations_{user_id}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return {"data": cached_data}, 200

            relations = UserRelation.query.filter_by(user_id=user_id).all()
            data = [rel.to_dict() for rel in relations]
            cache.set(cache_key, data, timeout=300)
            return {"data": data}, 200

    @jwt_required()
    def put(self, other_user_id):
        user_id = get_jwt_identity()
        data = request.get_json()
        new_relation_type = data.get('relation')

        relation = UserRelation.query.filter_by(
            user_id=user_id,
            related_user_id=other_user_id
        ).first()

        if not relation:
            return {"message": "Relation not found"}, 404

        relation.relation_type = new_relation_type
        db.session.commit()

        # Invalidate related caches
        cache = current_app.cache
        cache.delete(f"user_relations_{user_id}")
        cache.delete(f"user_relation_{user_id}_{other_user_id}")

        return {"message": "Relation updated", "data": {
                    "user_id": relation.user_id,
                    "related_user_id" :relation.related_user_id,
                    "relation_type" : relation.relation_type
                    }}, 200

    @jwt_required()
    def delete(self, other_user_id):
        user_id = get_jwt_identity()

        relation = UserRelation.query.filter_by(
            user_id=user_id,
            related_user_id=other_user_id
        ).first()

        if not relation:
            return {"message": "Relation not found"}, 404

        db.session.delete(relation)
        db.session.commit()

        # Invalidate related caches
        cache = current_app.cache
        cache.delete(f"user_relations_{user_id}")
        cache.delete(f"user_relation_{user_id}_{other_user_id}")

        return {"message": "Relation deleted"}, 200