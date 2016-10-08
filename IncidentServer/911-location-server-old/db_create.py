# only for debug, use python manage.py db init/migrate/upgrade instead
from application import db

from application.models import *


db.create_all()

print("DB created.")