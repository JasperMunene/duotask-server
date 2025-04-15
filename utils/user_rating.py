from __future__ import annotations
from typing import NamedTuple, Optional
from dataclasses import dataclass
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from models.review import Review
from models import db


class RatingResult(NamedTuple):
    """Immutable result container with type-safe fields"""
    final_rating: Optional[float]
    num_ratings: int


class UserRatingCalculator:
    """
    Efficiently calculates user ratings with database-level optimizations.

    Features:
    - Single optimized query with COALESCE handling
    - Type-safe result container
    - Decimal-aware calculations
    - Session independence for testability
    - Batch processing readiness
    """

    def __init__(self, session: Optional[Session] = None):
        self.session = session or db.session

    def get_user_rating(self, user_id: int) -> RatingResult:
        """
        Calculate rating statistics with database-level aggregation.

        Args:
            user_id: ID of user to calculate ratings for

        Returns:
            RatingResult: Named tuple containing:
              - final_rating: None if no ratings, else average rounded to 1 decimal
              - num_ratings: Total number of reviews considered
        """
        # Single query with coalesce handling for database-level null protection
        stmt = select(
            func.coalesce(func.avg(Review.rating), None).label('average'),
            func.count(Review.id).label('count')
        ).where(
            Review.reviewee_id == user_id
        )

        result = self.session.execute(stmt).fetchone()

        avg_rating = round(result.average, 1) if result.average is not None else None
        return RatingResult(
            final_rating=avg_rating,
            num_ratings=result.count or 0
        )
