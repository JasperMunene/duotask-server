from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import current_app
from models import db
from models.category import Category
import logging
import time

logger = logging.getLogger(__name__)


class CategoryResource(Resource):

    def get(self):
        """
        Get all categories
        Response:
            200: {
                "categories": [
                    {
                        "id": 1,
                        "name": "Cleaning",
                        "icon": "cleaning.svg"
                    },
                    ...
                ],
                "meta": {
                    "total_categories": 25,
                    "cache_status": "hit",
                    "response_time": 0.12
                }
            }
        """
        start_time = time.monotonic()
        cache = current_app.cache
        cache_key = "categories_list"
        cached_data = cache.get(cache_key)

        # Return cached data if available
        if cached_data:
            return {
                "categories": cached_data,
                "meta": {
                    "total_categories": len(cached_data),
                    "cache_status": "hit",
                    "response_time": round(time.monotonic() - start_time, 4)
                }
            }

        try:
            # Simple query to get all categories
            categories = Category.query.order_by(Category.name).all()

            # Format results
            result = [{
                "id": c.id,
                "name": c.name,
                "icon": c.icon
            } for c in categories]

            # Cache results for 1 hour
            cache.set(cache_key, result, timeout=3600)

            response_time = round(time.monotonic() - start_time, 4)
            logger.info(f"Categories fetched from DB in {response_time}s")

            return {
                "categories": result,
                "meta": {
                    "total_categories": len(result),
                    "cache_status": "miss",
                    "response_time": response_time
                }
            }

        except Exception as e:
            logger.error(f"Failed to fetch categories: {str(e)}")
            return {
                "error": "Failed to retrieve categories",
                "message": str(e)
            }, 500


class PopularCategoriesResource(Resource):

    def get(self):
        """
        Get top 8 popular categories (placeholder implementation)
        Response:
            200: {
                "categories": [
                    {id, name, icon},
                    ...
                ],
                "meta": {
                    "cache_status": "hit"
                }
            }
        """
        cache = current_app.cache
        cache_key = "popular_categories"
        cached_data = cache.get(cache_key)

        if cached_data:
            return {
                "categories": cached_data,
                "meta": {"cache_status": "hit"}
            }

        try:
            # Simple query to get some categories - this is a placeholder
            # You'll need to implement actual popularity logic later
            categories = Category.query.order_by(Category.name).limit(8).all()

            result = [{
                "id": c.id,
                "name": c.name,
                "icon": c.icon
            } for c in categories]

            # Cache for 15 minutes
            cache.set(cache_key, result, timeout=900)

            return {
                "categories": result,
                "meta": {"cache_status": "miss"}
            }

        except Exception as e:
            logger.error(f"Failed to fetch popular categories: {str(e)}")
            # Return empty array on error
            return {
                "categories": [],
                "meta": {
                    "cache_status": "error",
                    "error": str(e)
                }
            }