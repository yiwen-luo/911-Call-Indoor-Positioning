"""empty message

Revision ID: 7bd84203003b
Revises: 1b77e3bae583
Create Date: 2016-04-14 23:03:23.043524

"""

# revision identifiers, used by Alembic.
revision = '7bd84203003b'
down_revision = '1b77e3bae583'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gps_loc', sa.Column('timestamp', sa.Float(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('gps_loc', 'timestamp')
    ### end Alembic commands ###
