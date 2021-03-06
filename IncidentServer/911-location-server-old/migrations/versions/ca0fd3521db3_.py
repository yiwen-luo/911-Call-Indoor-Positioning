"""empty message

Revision ID: ca0fd3521db3
Revises: 7b714f1164ee
Create Date: 2016-04-24 23:25:57.699778

"""

# revision identifiers, used by Alembic.
revision = 'ca0fd3521db3'
down_revision = '7b714f1164ee'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tag_loc')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tag_loc',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('timestamp', mysql.FLOAT(), nullable=True),
    sa.Column('indoorFlag', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('GPSJSON', mysql.FLOAT(), nullable=True),
    sa.Column('wifiJSON', mysql.TEXT(), nullable=True),
    sa.Column('cellTowerJSON', mysql.TEXT(), nullable=True),
    sa.Column('addr_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('addrJson', mysql.TEXT(), nullable=True),
    sa.ForeignKeyConstraint(['addr_id'], [u'addresses.id'], name=u'tag_loc_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'latin1',
    mysql_engine=u'InnoDB'
    )
    ### end Alembic commands ###
