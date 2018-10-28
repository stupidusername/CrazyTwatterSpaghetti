"""
Create account table.

Revision ID: 0c32f76cf5c8
Revises: 5a0ba9c1cc69
Create Date: 2018-10-27 22:17:39.977251
"""
from alembic import op
import sqlalchemy as sa


# #evision identifiers, used by Alembic.
revision = '0c32f76cf5c8'
down_revision = '5a0ba9c1cc69'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'vote',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('vote_pool_id', sa.Integer, sa.ForeignKey('vote_pool.id')),
        sa.Column('create_datetime', sa.DateTime(), nullable=False),
        sa.Column('screen_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('phone_number', sa.String(), nullable=False),
        sa.Column('hit', sa.Boolean),
        sa.Column('error', sa.Text()),
    )


def downgrade():
    op.drop_table('vote')
