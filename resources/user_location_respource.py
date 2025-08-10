from flask import current_app
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.user_location import UserLocation
import logging  

logger = logging.getLogger(__name__)    

class UserLocationResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('latitude', type=float, required=True, help="Latitude is required")
    parser.add_argument('longitude', type=float, required=True, help="Longitude is required")
    parser.add_argument('area', type=str, required=False)
    parser.add_argument('state', type=str, required=False)
    parser.add_argument('street', type=str, required=False)
    parser.add_argument('city', type=str, required=False)
    parser.add_argument('country', type=str, required=False)
    
    @jwt_required()
    def get(self):
        cache = current_app.cache
        
        """Get the current user's location."""
        user_id = get_jwt_identity()
        cache_key = f"user_location:{user_id}"
        cached_location = cache.get(cache_key)
        if cached_location:
            return cached_location, 200
        location = UserLocation.query.filter_by(user_id=user_id).first()
        if not location:
            return {"error": "User location not found"}, 404

        cache.set(cache_key, {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "area": location.area,
            "state": location.state,
            "street": location.street,
            "city": location.city,
            "country": location.country
        }, timeout=3600)
        return {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "area": location.area,
            "street": location.street,
            "state": location.state,
            "city": location.city,
            "country": location.country
        }, 200

    @jwt_required()
    def post(self):
        """Create or update the current user's location."""
        user_id = get_jwt_identity()
        args = self.parser.parse_args()

        try:
            location = UserLocation.query.filter_by(user_id=user_id).first()

            if not location:
                # Create new location
                location = UserLocation(
                    user_id=user_id,
                    latitude=args['latitude'],
                    longitude=args['longitude'],
                    area=args.get('area'),
                    street=args.get('street'),
                    state=args.get('state'),
                    country=args.get('country')
                )
                # Handle "city" even if it's not in the model yet
                if hasattr(location, "city"):
                    location.city = args.get("city")

                db.session.add(location)
            else:
                # Update existing location
                location.latitude = args['latitude']
                location.longitude = args['longitude']
                location.area = args.get('area')
                location.street = args.get('street')
                location.state = args.get('state')
                location.country = args.get('country')
                location.city = args.get("city")

            db.session.commit()
            return {"message": "User location saved successfully"}, 200

        except Exception as e:
            logger.exception("Failed to save user location")
            return {"error": "Something went wrong", "details": str(e)}, 500

