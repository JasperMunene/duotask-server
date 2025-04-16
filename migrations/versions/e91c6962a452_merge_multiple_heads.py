"""merge multiple heads

Revision ID: e91c6962a452
Revises: b387be61a4ac, bacd6a6cde61
Create Date: 2025-04-16 14:35:33.769145

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e91c6962a452'
down_revision = ('b387be61a4ac', 'bacd6a6cde61')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
