"""
Create account table

Revision ID: afc56bac4b59
Revises:
Create Date: 2018-10-21 21:46:12.620809
"""
from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = 'afc56bac4b59'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'account',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('screen_name', sa.String(), nullable=False, unique=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('phone_number', sa.String(), nullable=False),
        sa.Column('status', sa.String()),
        sa.Column('status_updated_at', sa.DateTime()),
    )


def downgrade():
    op.drop_table('account')
