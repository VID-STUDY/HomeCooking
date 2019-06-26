"""Is hidden field for dishes

Revision ID: f63e6b3ad83c
Revises: 6f546a183d97
Create Date: 2019-06-26 23:08:06.525071

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f63e6b3ad83c'
down_revision = '6f546a183d97'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dishes', sa.Column('is_hidden', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('dishes', 'is_hidden')
    # ### end Alembic commands ###
