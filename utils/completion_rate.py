from __future__ import annotations
from typing import Optional, Tuple
from sqlalchemy import func, case
from sqlalchemy.orm import Session
from models.task_assignment import TaskAssignment
from models import db
from flask import current_app

class UserCompletionRateCalculator:
    """
    Efficiently calculates Bayesian-adjusted task completion rates for users.
    Uses caching for global statistics and optimized SQL queries.

    Bayesian Formula:
        Rate = (User Completed + m * Global Rate) / (User Assigned + m)
    where m is the stabilizer weight (default: 20 tasks).
    """

    def __init__(self, session: Optional[Session] = None, min_tasks: int = 20):
        self.session = session or db.session
        self.min_tasks = min_tasks
        self.cache = current_app.cache  # Assuming current_app.cache is set up

    def _get_user_stats(self, user_id: int) -> Tuple[int, int]:
        """
        Retrieve user's task statistics (completed and total assignments)
        using a single query.
        Returns: (completed_tasks, total_assigned_tasks)
        """
        result = (
            self.session.query(
                func.count(TaskAssignment.id).label("total"),
                func.coalesce(
                    func.sum(
                        case(
                            (TaskAssignment.status == 'completed', 1),
                            else_=0
                        )
                    ), 0
                ).label("completed")
            )
            .filter(TaskAssignment.task_doer == user_id)
            .first()
        )

        total = result.total if result and result.total is not None else 0
        completed = result.completed if result and result.completed is not None else 0

        return (completed, total)

    def _get_global_completion_rate(self) -> float:
        """
        Calculate (and cache) the global completion rate.
        Returns: System-wide completion probability (between 0.0 and 1.0)
        """
        cache_key = "global_completion_rate"
        cached_rate = self.cache.get(cache_key)
        if cached_rate is not None:
            return cached_rate

        result = (
            self.session.query(
                func.count(TaskAssignment.id).label("total"),
                func.coalesce(
                    func.sum(
                        case(
                            (TaskAssignment.status == 'completed', 1),
                            else_=0
                        )
                    ), 0
                ).label("completed")
            )
            .first()
        )
        total_assigned = result.total if result and result.total is not None else 0
        total_completed = result.completed if result and result.completed is not None else 0

        global_rate = total_completed / total_assigned if total_assigned > 0 else 0.0
        # Cache the global rate for 5 minutes
        self.cache.set(cache_key, global_rate, timeout=300)
        return global_rate

    def calculate_rate(self, user_id: int) -> float:
        """
        Calculate the Bayesian-adjusted completion rate for a given user.
        Returns: A percentage value rounded to one decimal place.
        """
        completed, assigned = self._get_user_stats(user_id)
        global_rate = self._get_global_completion_rate()
        m = self.min_tasks

        numerator = completed + m * global_rate
        denominator = assigned + m
        bayesian_rate = numerator / denominator

        return round(bayesian_rate * 100, 1)

# Example usage:
# calc = UserCompletionRateCalculator(min_tasks=20)
# rate = calc.calculate_rate(user_id=123)
# print(f"User Bayesian completion rate: {rate}%")
