from flask_restful import Resource, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from sqlalchemy import asc, desc
from sqlalchemy.orm import joinedload
from models import db
from models.task import Task
from models.bid import Bid
from models.user import User
import logging

logger = logging.getLogger(__name__)


class BidsResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('status', type=str, location='args',
                        choices=['pending', 'accepted', 'rejected'],
                        help="Invalid bid status. Allowed: pending, accepted, rejected")
    parser.add_argument('min_amount', type=float, location='args')
    parser.add_argument('max_amount', type=float, location='args')
    parser.add_argument('sort', type=str, location='args',
                        choices=['amount', 'created_at', 'updated_at'],
                        default='created_at',
                        help="Invalid sort field. Allowed: amount, created_at, updated_at")
    parser.add_argument('order', type=str, location='args',
                        choices=['asc', 'desc'], default='desc',
                        help="Invalid sort order. Allowed: asc, desc")
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=20, location='args',
                        choices=[10, 20, 50, 100], help='Invalid items per page')

    @jwt_required()
    def get(self, task_id):
        """
        Get bids for a specific task
        ---
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
          - name: Authorization
            in: header
            type: string
            required: true
            description: JWT access token
        responses:
          200:
            description: List of bids with pagination
          403:
            description: Unauthorized access
          404:
            description: Task not found
        """
        # Validate task existence and ownership
        current_user_id = get_jwt_identity()
        task = db.session.get(Task, task_id)
        if not task or task.is_deleted:
            abort(404, message="Task not found")
        if str(task.user_id) != current_user_id:
            abort(403, message="Unauthorized access to bids")

        # Parse request arguments
        args = self.parser.parse_args()

        # Generate cache key
        cache_key = f"task_bids_{task_id}_{str(args)}"

        # Check cache
        cached_data = current_app.cache.get(cache_key)
        if cached_data:
            return cached_data

        # Base query with eager loading
        query = Bid.query.filter_by(task_id=task_id).options(
            joinedload(Bid.user).joinedload(User.user_info)
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

        # Serialize results
        bids = [self._serialize_bid(bid) for bid in paginated.items]

        response = {
            'bids': bids,
            'pagination': {
                'page': paginated.page,
                'per_page': paginated.per_page,
                'total_pages': paginated.pages,
                'total_items': paginated.total
            }
        }

        # Cache response for 5 minutes
        current_app.cache.set(cache_key, response, timeout=300)
        return response

    def _apply_filters(self, query, args):
        """Apply query filters based on request parameters"""
        if args['status']:
            query = query.filter(Bid.status == args['status'])
        if args['min_amount'] is not None:
            query = query.filter(Bid.amount >= args['min_amount'])
        if args['max_amount'] is not None:
            query = query.filter(Bid.amount <= args['max_amount'])
        return query

    def _apply_sorting(self, query, args):
        """Apply sorting based on request parameters"""
        sort_field = args['sort']
        order = desc if args['order'] == 'desc' else asc

        if sort_field == 'amount':
            return query.order_by(order(Bid.amount))
        if sort_field == 'created_at':
            return query.order_by(order(Bid.created_at))
        return query.order_by(order(Bid.updated_at))

    def _serialize_bid(self, bid):
        """Serialize bid with user information"""
        user_info = bid.user.user_info if bid.user.user_info else None
        return {
            'id': bid.id,
            'amount': float(bid.amount),
            'message': bid.message,
            'status': bid.status,
            'created_at': bid.created_at.isoformat(),
            'updated_at': bid.updated_at.isoformat(),
            'user': {
                'id': bid.user.id,
                'name': bid.user.name,
                'image': bid.user.image
                # 'rating': user_info.rating if user_info else 0.0,
                # 'completed_tasks': user_info.completed_tasks if user_info else 0
            }
        }