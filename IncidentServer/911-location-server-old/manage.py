from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from application.models import *	

from application import db, application
application.config.from_object('config')

migrate = Migrate(application, db)

manager = Manager(application)
manager.add_command('db', MigrateCommand)





if __name__ == '__main__':
	manager.run()