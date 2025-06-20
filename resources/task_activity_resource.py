from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from models.task import Task
from models.task_assignment import TaskAssignment
from flask import current_app, request
from collections import defaultdict
from datetime import datetime, date, timedelta

class TaskActivityResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        cache = current_app.cache

        try:
            page = int(request.args.get("page", 1))
            limit = int(request.args.get("limit", 10))
        except ValueError:
            return {"message": "Invalid pagination parameters."}, 400

        offset = (page - 1) * limit
        cache_key = f"task_activity:{user_id}:{page}:{limit}"
        cached = cache.get(cache_key)
        if cached:
            return cached, 200

        # Fetch tasks
        posted_tasks = Task.query.filter(Task.user_id == user_id).options(
            joinedload(Task.location),
            joinedload(Task.categories),
            joinedload(Task.images)
        ).all()

        task_assignments = TaskAssignment.query.filter(TaskAssignment.task_doer == user_id).all()
        assigned_task_ids = [a.task_id for a in task_assignments]
        assigned_tasks = Task.query.filter(Task.id.in_(assigned_task_ids)).options(
            joinedload(Task.user),
            joinedload(Task.location),
            joinedload(Task.categories),
            joinedload(Task.images)
        ).all()

        # Create lists
        activity_list = []
        today = date.today()
        current_month = today.strftime("%Y-%m")
        previous_month = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")

        # Earnings Insights
        completed_assignments = [a for a in task_assignments if a.task.status == "completed"]
        total_earnings = sum(float(a.agreed_price or 0) for a in completed_assignments)
        earnings_by_month = defaultdict(float)

        for a in completed_assignments:
            if a.task and a.task.created_at:
                month = a.task.created_at.strftime("%Y-%m")
                earnings_by_month[month] += float(a.agreed_price or 0)

        earnings_this_month = earnings_by_month.get(current_month, 0)
        earnings_last_month = earnings_by_month.get(previous_month, 0)
        earnings_trend = (
            ((earnings_this_month - earnings_last_month) / earnings_last_month) * 100
            if earnings_last_month > 0 else None
        )

        # Spending Insights
        completed_posted_tasks = [t for t in posted_tasks if t.status == "completed"]
        total_spent = sum(float(t.budget or 0) for t in completed_posted_tasks)
        spending_by_month = defaultdict(float)

        for t in completed_posted_tasks:
            if t.created_at:
                month = t.created_at.strftime("%Y-%m")
                spending_by_month[month] += float(t.budget or 0)

        spending_this_month = spending_by_month.get(current_month, 0)
        spending_last_month = spending_by_month.get(previous_month, 0)
        spending_trend = (
            ((spending_this_month - spending_last_month) / spending_last_month) * 100
            if spending_last_month > 0 else None
        )

        # Populate Activity List
        for task in posted_tasks:
            activity_list.append({
                "type": "posted",
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "work_mode": task.work_mode,
                "budget": float(task.budget or 0),
                "deadline_date": task.deadline_date.isoformat() if task.deadline_date else None,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "preferred_time": task.preferred_time,
                "schedule_type": task.schedule_type,
                "specific_date": task.specific_date.isoformat() if task.specific_date else None,
            })

        for task in assigned_tasks:
            assignment = next((a for a in task_assignments if a.task_id == task.id), None)
            if not assignment:
                continue

            activity_list.append({
                "type": "assigned",
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "agreed_price": float(assignment.agreed_price or 0),
                "deadline_date": task.deadline_date.isoformat() if task.deadline_date else None,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "preferred_time": task.preferred_time,
                "schedule_type": task.schedule_type,
                "specific_date": task.specific_date.isoformat() if task.specific_date else None,
                "task_giver": {
                    "id": task.user.id if task.user else None,
                    "name": task.user.name if task.user else None,
                    "avatar": task.user.image if task.user else None
                }
            })

        # Sort and Paginate
        activity_list.sort(key=lambda x: x["created_at"] or "", reverse=True)
        paginated = activity_list[offset:offset + limit]

        # Final Insight Structure
        insights = {
            "earnings": {
                "total": total_earnings,
                "average_per_task": total_earnings / len(completed_assignments) if completed_assignments else 0,
                "this_month": earnings_this_month,
                "last_month": earnings_last_month,
                "percent_change": round(earnings_trend, 2) if earnings_trend is not None else None,
                "completed_tasks": len(completed_assignments),
                "monthly": dict(earnings_by_month)
            },
            "spending": {
                "total": total_spent,
                "average_per_task": total_spent / len(completed_posted_tasks) if completed_posted_tasks else 0,
                "this_month": spending_this_month,
                "last_month": spending_last_month,
                "percent_change": round(spending_trend, 2) if spending_trend is not None else None,
                "completed_tasks": len(completed_posted_tasks),
                "monthly": dict(spending_by_month)
            },
            "activity": {
                "total_posted": len(posted_tasks),
                "total_assigned": len(task_assignments),
                "total_activities": len(activity_list),
                "completion_rate": round((len(completed_posted_tasks) / len(posted_tasks)) * 100, 2) if posted_tasks else 0
            }
        }

        response = {
            "page": page,
            "limit": limit,
            "total": len(activity_list),
            "results": paginated,
            "insights": insights
        }

        cache.set(cache_key, response, timeout=60 * 5)
        return response, 200
