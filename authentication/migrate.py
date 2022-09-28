import os
import shutil

from flask import Flask
from configuration_migrate import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database, User, Role
from sqlalchemy_utils import database_exists, create_database, drop_database

dirpath = "/opt/src/authentication/migrations"

if os.path.exists(dirpath) and os.path.isdir(dirpath):
    shutil.rmtree(dirpath)

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

done = False
while not done:
    try:
        if database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
            drop_database(application.config["SQLALCHEMY_DATABASE_URI"])

        create_database(application.config["SQLALCHEMY_DATABASE_URI"])

        database.init_app(application)

        with application.app_context() as context:
            init()
            migrate(message="Production migration.")
            upgrade()

            adminRole = Role(name="admin")
            customerRole = Role(name="customer")
            storekeeperRole = Role(name="storekeeper")

            database.session.add(adminRole)
            database.session.add(customerRole)
            database.session.add(storekeeperRole)
            database.session.commit()

            admin = User(first_name="admin", last_name="admin", email="admin@admin.com", password="1", role=1)

            database.session.add(admin)
            database.session.commit()

            done = True
    except Exception as error:
        print(error)

while True:
    pass
