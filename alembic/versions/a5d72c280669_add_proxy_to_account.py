"""
Add proxy column to account table.

Revision ID: a5d72c280669
Revises: 0c32f76cf5c8
Create Date: 2018-11-27 16:02:57.475201
"""
from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = 'a5d72c280669'
down_revision = '0c32f76cf5c8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('account', sa.Column('proxy', sa.String()))


def downgrade():
    op.drop_column('account', 'proxy')
