"""
Create vote_pool table.

Revision ID: 5a0ba9c1cc69
Revises: afc56bac4b59
Create Date: 2018-10-27 21:52:44.149774
"""
from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = '5a0ba9c1cc69'
down_revision = 'afc56bac4b59'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'vote_pool',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('tweet_id', sa.Integer, nullable=False),
        sa.Column('option_index', sa.Integer, nullable=False),
        sa.Column('intended_hits', sa.Integer, nullable=False),
        sa.Column('max_tries', sa.Integer, nullable=False),
        sa.Column('create_datetime', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
    )


def downgrade():
    op.drop_table('vote_pool')
