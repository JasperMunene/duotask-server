from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData, Index

# Configure naming convention for database constraints
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

db = SQLAlchemy(metadata=metadata)

# ---------------------------------------------------------------------------
# 1. Users & Profiles
# ---------------------------------------------------------------------------
class User(db.Model, SerializerMixin):
    """User model representing application users."""
    __tablename__ = 'users'
    __table_args__ = (
        Index('idx_verification', 'otp_code', 'otp_expires_at'),
    )

    # Serialization rules to exclude sensitive information
    serialize_rules = ('-password', '-otp_code', '-reset_token', '-reset_expires_at')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(15), comment="Stored in E.164 format")
    image = db.Column(db.String(255), nullable=True, comment="URL to profile image")
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expires_at = db.Column(db.DateTime, nullable=True)
    otp_last_sent = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    reset_token = db.Column(db.String(64), nullable=True)
    reset_expires_at = db.Column(db.DateTime, nullable=True)
    auth_provider = db.Column(
        db.String(50),
        nullable=False,
        server_default="email",
        comment="Authentication provider; defaults to 'email' for email/password login"
    )
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


class UserInfo(db.Model, SerializerMixin):
    """User info model for additional user details."""
    __tablename__ = 'user_info'
    __table_args__ = (
        Index('idx_user_info_user', 'user_id'),
        Index('idx_user_info_rating', 'rating'),
        Index('idx_user_info_completion', 'completion_rate'),
    )

    serialize_rules = ('-user',)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), unique=True, nullable=False, index=True)
    tagline = db.Column(db.String(255), nullable=True, comment="User's short description")
    bio = db.Column(db.Text, nullable=True, comment="User's biography")
    rating = db.Column(db.Float, default=0.0, nullable=False, comment="User's rating (0.0 - 5.0)")
    completion_rate = db.Column(db.Float, default=0.0, nullable=False, comment="Task completion rate (0-100%)")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    # Relationship with User
    user = db.relationship("User", backref=db.backref("user_info", uselist=False, cascade="all, delete-orphan"))


class Categories(db.Model, SerializerMixin):
    """Category model for classifying tasks."""
    __tablename__ = 'categories'
    __table_args__ = (
        Index('uq_categories_name', 'name', unique=True),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True, comment="Name of the category")
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now(), nullable=False)

    # Relationship to tasks
    tasks = db.relationship("Task", backref="category", lazy=True)


# ---------------------------------------------------------------------------
# 2. Task Locations
# ---------------------------------------------------------------------------
class TaskLocation(db.Model, SerializerMixin):
    """TaskLocation model storing physical location details for tasks."""
    __tablename__ = 'task_locations'

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Numeric(9, 6), nullable=False, comment="Latitude coordinate")
    longitude = db.Column(db.Numeric(9, 6), nullable=False, comment="Longitude coordinate")
    country = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100), nullable=True, comment="Optional area or neighborhood")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


# ---------------------------------------------------------------------------
# 3. Tasks
# ---------------------------------------------------------------------------
class Task(db.Model, SerializerMixin):
    """Task model representing a task posted on the platform."""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False, comment="Task creator")
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete="CASCADE"), nullable=False)
    work_mode = db.Column(db.String(20), nullable=False, comment="Either 'remote' or 'physical'")
    location_id = db.Column(db.Integer, db.ForeignKey('task_locations.id', ondelete="SET NULL"), nullable=True, comment="Required if work_mode is physical")
    budget = db.Column(db.Numeric(10, 2), nullable=False)
    schedule_type = db.Column(db.String(20), nullable=False, comment="Scheduling type: 'specific_day', 'before_day', or 'flexible'")
    specific_date = db.Column(db.DateTime, nullable=True, comment="Exact date if schedule_type is 'specific_day'")
    deadline_date = db.Column(db.DateTime, nullable=True, comment="Deadline date if schedule_type is 'before_day'")
    preferred_time = db.Column(db.Time, nullable=True, comment="Preferred time if schedule_type is 'flexible'")
    status = db.Column(db.String(20), nullable=False, comment="Task status: e.g., 'open', 'in_progress', 'completed', 'cancelled'")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    # Relationships
    user = db.relationship("User", backref=db.backref("tasks", cascade="all, delete-orphan", lazy=True))
    location = db.relationship("TaskLocation", backref=db.backref("tasks", cascade="all, delete-orphan", lazy=True))


# ---------------------------------------------------------------------------
# 4. Bids
# ---------------------------------------------------------------------------
class Bid(db.Model, SerializerMixin):
    """Bid model for offers made by users on tasks."""
    __tablename__ = 'bids'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, comment="Bid status: e.g., 'pending', 'accepted', 'rejected'")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    # Relationships
    task = db.relationship("Task", backref=db.backref("bids", cascade="all, delete-orphan", lazy=True))
    user = db.relationship("User", backref=db.backref("bids", cascade="all, delete-orphan", lazy=True))


# ---------------------------------------------------------------------------
# 5. Task Assignments
# ---------------------------------------------------------------------------
class TaskAssignment(db.Model, SerializerMixin):
    """TaskAssignment model recording which bid was accepted and the task assignment details."""
    __tablename__ = 'task_assignments'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete="CASCADE"), nullable=False)
    task_giver = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False, comment="User who posted the task")
    task_doer = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False, comment="User assigned to perform the task")
    agreed_price = db.Column(db.Numeric(10, 2), nullable=False)
    conversation_id = db.Column(db.Integer, nullable=True, comment="Optional reference to a conversation for messaging")
    status = db.Column(db.String(20), nullable=False, comment="Assignment status: e.g., 'assigned', 'in_progress', 'completed', 'cancelled'")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    # Relationships
    task = db.relationship("Task", backref=db.backref("assignments", cascade="all, delete-orphan", lazy=True))
    giver = db.relationship("User", foreign_keys=[task_giver], backref=db.backref("given_assignments", cascade="all, delete-orphan", lazy=True))
    doer = db.relationship("User", foreign_keys=[task_doer], backref=db.backref("assignments", cascade="all, delete-orphan", lazy=True))
