import logging
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api
from flask.ext.httpauth import HTTPBasicAuth
from jsonrpc2 import JsonRpc
from werkzeug.security import generate_password_hash

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

# from application import models
# open and intialize or read the database
db = SQLAlchemy(app)

# initialize rpc mapper
mapper = JsonRpc()
register_class_to_rpc(RPCServer, mapper)

from application import models, views

# will create database and tables if not exist
db.create_all()

# will append a default user if none exist
# TODO: flash warning message about the existence of a potential security risk.
if models.User.query.count() == 0:
    default_user = models.User()
    default_user.username = 'Admin'
    default_user.password = generate_password_hash('password')
    db.session.add(default_user)
    db.session.commit()


# initialize flask-login
def init_login(app_):
    login_manager = LoginManager()
    login_manager.init_app(app_)

    # create user loader function
    def load_user(user_id):
        return models.User.query.get(user_id)


# initialize rest interface
def init_rest(app_):
    from application.resources.app_resource import AppResource
    from application.resources.app_list_resource import AppListResource

    rest_api = Api(app_)
    rest_api.add_resource(AppListResource,
                          ActiveConfig.REST_URL_APPS_LIST,
                          ActiveConfig.REST_URL_APPS_LIST + '/')
    rest_api.add_resource(AppResource,
                          ActiveConfig.REST_URL_APPS_ITEM,
                          ActiveConfig.REST_URL_APPS,
                          ActiveConfig.REST_URL_APPS + '/')

init_login(app)
init_rest(app)
