"""empty message

Revision ID: b3bf4dc714b7
Revises: a38c7561c80c
Create Date: 2020-01-16 11:16:47.415850

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3bf4dc714b7'
down_revision = 'a38c7561c80c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('website', sa.String(length=120), nullable=True))
    op.drop_column('Artist', 'website_URL')
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('website', sa.String(length=120), nullable=True))
    op.drop_column('Venue', 'website_URL')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('website_URL', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('Venue', 'website')
    op.drop_column('Venue', 'seeking_talent')
    op.add_column('Artist', sa.Column('website_URL', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('Artist', 'website')
    op.drop_column('Artist', 'seeking_venue')
    # ### end Alembic commands ###
