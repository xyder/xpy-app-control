import logging
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from jsonrpc2 import JsonRpc

from config import ActiveConfig

# initialize and configure the flask server
app = Flask(__name__)
app.config.from_object(ActiveConfig)

# set up logger level
if not app.debug:
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

# open and intialize or read the database
db = SQLAlchemy(app)

# initialize rpc mapper
mapper = JsonRpc()

from application.views import main_views
from application.utils.initializers import init_db, init_admin, init_login, init_rest, init_rpc

init_db(db)
init_admin(app, db)
init_login(app)
init_rest(app)
init_rpc(mapper)
