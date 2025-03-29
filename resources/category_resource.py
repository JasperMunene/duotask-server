from flask_restful import Resource
from flask import request, jsonify
from models import db, Categories  # Import your model correctly

class CategoryResource(Resource):  # Renamed to avoid conflict
    def post(self):
        data = request.get_json()
        if not data or "name" not in data:
            return {"message": "Name is required"}, 400  # Handle missing fields

        # Create new category
        new_category = Categories(name=data["name"])
        db.session.add(new_category)  
        db.session.commit()  # Fix: Corrected commit call
        
        return {
            "message": "Category added successfully", 
            "category": new_category.to_dict()
        }, 201  # Return 201 for resource creation
    
    def get(self):
        page = request.args.get('page', 1, type=int)  # Get page number, default is 1
        per_page = request.args.get('per_page', 10, type=int)  # Items per page, default is 10
        search_query = request.args.get('search', '', type=str)  # Search query

        # Query filtering for search
        query = Categories.query
        if search_query:
            query = query.filter(Categories.name.ilike(f"%{search_query}%"))  # Fix: Removed redundant query call

        # Paginate results
        paginated_data = query.paginate(page=page, per_page=per_page, error_out=False)

        # Return JSON response with has_next
        return jsonify({
            "categories": [category.to_dict() for category in paginated_data.items],  # Implement to_dict in your model
            "total": paginated_data.total,
            "pages": paginated_data.pages,
            "current_page": paginated_data.page,
            "has_next": paginated_data.has_next  # Returns True if there's another page
        })
