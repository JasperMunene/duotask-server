from flask_restful import Resource, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from werkzeug.exceptions import HTTPException
from sqlalchemy import asc, desc, func, case
from sqlalchemy.orm import joinedload, Session
from models import db
from models.task import Task
from models.bid import Bid
from models.user import User
from utils.completion_rate import UserCompletionRateCalculator
from utils.user_rating import UserRatingCalculator
from utils.send_notification import Notify

import logging
logger = logging.getLogger(__name__)


class BidsResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'status', type=str, location='args',
        choices=['pending', 'accepted', 'rejected'],
        help="Invalid bid status. Allowed: pending, accepted, rejected"
    )
    parser.add_argument('min_amount', type=float, location='args')
    parser.add_argument('max_amount', type=float, location='args')
    parser.add_argument(
        'sort', type=str, location='args',
        choices=['amount', 'created_at', 'updated_at'],
        default='created_at',
        help="Invalid sort field. Allowed: amount, created_at, updated_at"
    )
    parser.add_argument(
        'order', type=str, location='args',
        choices=['asc', 'desc'], default='desc',
        help="Invalid sort order. Allowed: asc, desc"
    )
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument(
        'per_page', type=int, default=20, location='args',
        choices=[10, 20, 50, 100], help='Invalid items per page'
    )

    @jwt_required()
    def get(self, task_id):
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except (TypeError, ValueError):
            abort(403, message="Invalid user identity")

        task = db.session.get(Task, task_id)
        if not task or task.is_deleted:
            abort(404, message="Task not found")

        if task.user_id != current_user_id:
            abort(403, message="Unauthorized access to bids")

        args = self.parser.parse_args()
        cache_key = f"task_bids_{task_id}_{args}"
        cached = current_app.cache.get(cache_key)
        if cached:
            return cached

        query = (
            Bid.query
            .filter_by(task_id=task_id)
            .options(joinedload(Bid.user).joinedload(User.user_info))
        )
        query = self._apply_filters(query, args)
        query = self._apply_sorting(query, args)
        paginated = query.paginate(
            page=args['page'], per_page=args['per_page'], error_out=False
        )

        # Instantiate the completion rate calculator once for this request.
        comp_rate_calc = UserCompletionRateCalculator(min_tasks=20)
        # For rating, create a rating calculator.
        rating_calc = UserRatingCalculator()

        bids = [self._serialize_bid(bid, comp_rate_calc, rating_calc) for bid in paginated.items]

        response = {
            'bids': bids,
            'pagination': {
                'page': paginated.page,
                'per_page': paginated.per_page,
                'total_pages': paginated.pages,
                'total_items': paginated.total
            }
        }
        current_app.cache.set(cache_key, response, timeout=300)
        return response

    def _apply_filters(self, query, args):
        if args['status']:
            query = query.filter(Bid.status == args['status'])
        if args['min_amount'] is not None:
            query = query.filter(Bid.amount >= args['min_amount'])
        if args['max_amount'] is not None:
            query = query.filter(Bid.amount <= args['max_amount'])
        return query

    def _apply_sorting(self, query, args):
        order_fn = desc if args['order'] == 'desc' else asc
        if args['sort'] == 'amount':
            return query.order_by(order_fn(Bid.amount))
        if args['sort'] == 'created_at':
            return query.order_by(order_fn(Bid.created_at))
        return query.order_by(order_fn(Bid.updated_at))

    def _serialize_bid(self, bid, comp_rate_calc: UserCompletionRateCalculator, rating_calc: UserRatingCalculator):
        """
        Serialize a bid and include both the bidder's Bayesian-adjusted completion rate and rating information.
        """
        ui = bid.user.user_info or None
        completion_rate = comp_rate_calc.calculate_rate(bid.user.id)
        rating_result = rating_calc.get_user_rating(bid.user.id)
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
                'image': bid.user.image,
                'completion_rate': completion_rate,
                'rating': rating_result.final_rating,
                'rating_users': rating_result.num_ratings
            }
        }

    post_parser = reqparse.RequestParser()
    post_parser.add_argument(
        'amount', type=float, required=True,
        help='Bid amount is required and must be a positive number'
    )
    post_parser.add_argument(
        'message', type=str, required=False, default="", trim=True
    )

    @jwt_required()
    def post(self, task_id):
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except (TypeError, ValueError):
            abort(403, message="Invalid user identity")

        data = self.post_parser.parse_args()

        try:
            with db.session.begin_nested():
                task = self._validate_task(task_id, current_user_id)
                self._validate_bid_amount(data['amount'], task.budget)
                self._check_existing_bid(task_id, current_user_id)

                bid = Bid(
                    task_id=task_id,
                    user_id=current_user_id,
                    amount=data['amount'],
                    message=data['message'],
                    status='pending'
                )
                db.session.add(bid)

            db.session.commit()

            self._invalidate_bid_cache(task)
            self._notify_task_owner(task, bid)

            return {
                'message': 'Bid submitted successfully',
                'bid_id': bid.id,
                'status': bid.status
            }, 201

        except ValueError as ve:
            db.session.rollback()
            logger.warning(f"Bid validation failed: {ve}")
            abort(400, message=str(ve))

        except HTTPException:
            db.session.rollback()
            raise

        except Exception as e:
            db.session.rollback()
            logger.error(f"Bid creation failed: {e}", exc_info=True)
            abort(500, message="Failed to create bid")

    def _validate_task(self, task_id, user_id):
        task = Task.query.filter_by(id=task_id, is_deleted=False).first()
        if not task:
            abort(404, message="Task not found")
        if task.user_id == user_id:
            abort(403, message="Self-bidding is not allowed")
        if task.status != 'open':
            abort(409, message="Task is not accepting bids")
        return task

    def _validate_bid_amount(self, bid_amount, task_budget):
        """Validate bid amount against business rules:
           - Must be positive
           - Must be ≤ budget
           - Must be ≥ MIN_BID_RATIO * budget
        """
        if bid_amount <= 0:
            raise ValueError("Bid amount must be positive")

        budget = float(task_budget)

        # lower bound
        if bid_amount < budget:
            raise ValueError("Bid amount exceeds task budget")

        # Lower bound via config (default 50%)
        min_ratio = current_app.config.get('MIN_BID_RATIO', 0.5)
        min_allowed = budget * min_ratio
        if bid_amount < min_allowed:
            raise ValueError(
                f"Bid amount must be at least {min_allowed:.2f} "
                f"({int(min_ratio*100)}% of the budget)"
            )

    def _check_existing_bid(self, task_id, user_id):
        if Bid.query.filter_by(task_id=task_id, user_id=user_id).first():
            abort(409, message="You already have an active bid on this task")
            
    def _invalidate_bid_cache(self, task):
        try:
            redis_cli = current_app.cache
            task_owner_id = task.user_id
            task_id = task.id

            # Log the start of cache invalidation
            logger.debug(f"Starting cache invalidation for task {task_id} (owner {task_owner_id})")

            # Define static keys to delete
            cache_keys = [
                f"posted_task:{task_owner_id}:{task_id}",   # Task owner view
                f"my_tasks:{task_owner_id}",                # Task owner's task list
                f"task_{task_id}"                           # Task detail view
            ]

            deleted_keys = []

            # Delete static keys
            for key in cache_keys:
                result = redis_cli.delete(key)
                if result:
                    deleted_keys.append(key)

            # Use scan_iter for pattern matching — non-blocking and safe
            bid_pattern = f"task_bids_{task_id}_*"
            for key in redis_cli.scan_iter(match=bid_pattern):
                result = redis_cli.delete(key)
                if result:
                    deleted_keys.append(key)

            logger.debug(f"Cache keys invalidated: {deleted_keys}")

        except Exception as e:
            logger.exception(f"Cache invalidation failed for task {task_id}: {e}")


    def _notify_task_owner(self, task, bid):
        try:
            current_app.celery.send_task(
                'notifications.new_bid',
                args=(task.user_id, bid.id, bid.user_id),
                queue='notifications'
            )
            
            Notify(user_id=task.user_id, message="Bidded on your task", source="bid", sender_id=bid.user_id).post()
        except Exception as e:
            logger.error(f"Failed to queue notification: {e}")
