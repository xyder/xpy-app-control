from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

# TODO: move migration logic and commands to main application

# Usage:
# Create migrations folder and initialize
#       python <script-name> db init
# Generate the initial migration
#       python <script-name> db migrate
# Upgrade the database to the latest migration:
#       python <script-name> db upgrade
# List of all available commands:
#       python <script-name> db --help

from config import ActiveConfig

# initialize and configure the flask server
app = Flask(__name__)
app.config.from_object(ActiveConfig)

# open and intialize or read the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
