"""empty message

Revision ID: bd5d3385ad93
Revises: bb1555e07af4
Create Date: 2020-01-18 15:14:40.175182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd5d3385ad93'
down_revision = 'bb1555e07af4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('start_time', sa.Date(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Show', 'start_time')
    # ### end Alembic commands ###
