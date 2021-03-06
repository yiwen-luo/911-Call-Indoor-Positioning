"""empty message

Revision ID: 8169b0a2c489
Revises: 2e1f354de74e
Create Date: 2016-04-23 19:42:27.453606

"""

# revision identifiers, used by Alembic.
revision = '8169b0a2c489'
down_revision = '2e1f354de74e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wifi_access_points')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('wifi_access_points',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('SSID', mysql.TEXT(), nullable=True),
    sa.Column('BSSID', mysql.TEXT(), nullable=True),
    sa.Column('RSSI', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('frequency', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('timestamp', mysql.FLOAT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'latin1',
    mysql_engine=u'InnoDB'
    )
    ### end Alembic commands ###
