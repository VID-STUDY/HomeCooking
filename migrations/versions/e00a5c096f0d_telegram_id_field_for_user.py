"""Telegram ID field for user

Revision ID: e00a5c096f0d
Revises: b312d87d544f
Create Date: 2019-09-09 20:28:00.555225

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e00a5c096f0d'
down_revision = 'b312d87d544f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('telegram_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'telegram_id')
    # ### end Alembic commands ###