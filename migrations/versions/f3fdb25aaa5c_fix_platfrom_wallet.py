"""fix platform wallet

Revision ID: f3fdb25aaa5c
Revises: 6af5cb1a45e7
Create Date: 2025-06-19 00:46:50.443631
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'f3fdb25aaa5c'
down_revision = '6af5cb1a45e7'
branch_labels = None
depends_on = None


def upgrade():
    # Fix NULLs before setting NOT NULL constraints
    op.execute("UPDATE platform_wallet SET status = 'active' WHERE status IS NULL;")
    op.execute("UPDATE platform_wallet SET created_at = now() WHERE created_at IS NULL;")
    op.execute("UPDATE platform_wallet SET updated_at = now() WHERE updated_at IS NULL;")

    with op.batch_alter_table('platform_wallet', schema=None) as batch_op:
        batch_op.alter_column('balance',
               existing_type=sa.NUMERIC(precision=18, scale=2),
               nullable=False)
        batch_op.alter_column('status',
               existing_type=sa.String(length=20),
               nullable=False)
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               nullable=False)
        batch_op.alter_column('updated_at',
               existing_type=sa.DateTime(),
               nullable=False)


def downgrade():
    with op.batch_alter_table('platform_wallet', schema=None) as batch_op:
        batch_op.alter_column('balance',
               existing_type=sa.NUMERIC(precision=18, scale=2),
               nullable=True)
        batch_op.alter_column('status',
               existing_type=sa.String(length=20),
               nullable=True)
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               nullable=True)
        batch_op.alter_column('updated_at',
               existing_type=sa.DateTime(),
               nullable=True)
