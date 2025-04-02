from . import db
from sqlalchemy_serializer import SerializerMixin

# ---------------------------------------------------------------------------
#  Categories
# ---------------------------------------------------------------------------
class Category(db.Model, SerializerMixin):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    icon = db.Column(db.String(255))
