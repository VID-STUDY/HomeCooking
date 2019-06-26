"""Full user name

Revision ID: ee5483392dca
Revises: f63e6b3ad83c
Create Date: 2019-06-27 03:21:37.760674

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee5483392dca'
down_revision = 'f63e6b3ad83c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('full_user_name', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'full_user_name')
    # ### end Alembic commands ###
