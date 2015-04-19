import logging
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from jsonrpc2 import JsonRpc

from application.libs.helper_functions import register_class_to_rpc
from application.rpc_server import RPCServer

from config import ActiveConfig

# initalize the authentication
auth = HTTPBasicAuth()

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
register_class_to_rpc(RPCServer, mapper)

from application import models, views
from application.initializers import init_db, init_admin, init_login, init_rest

init_db()
init_admin(app)
init_login(app)
init_rest(app)
