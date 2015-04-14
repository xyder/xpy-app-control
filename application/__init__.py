from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api
from flask.ext.httpauth import HTTPBasicAuth
from jsonrpc2 import JsonRpc

from application.libs.helper_functions import register_class_to_rpc
from application.rpc_server import RPCServer

from config import ActiveConfig

# init jsonrpc mapper
mapper = JsonRpc()
register_class_to_rpc(RPCServer, mapper)

# initalize the authentication
auth = HTTPBasicAuth()

# initialize and configure the flask server
app = Flask(__name__)
app.config.from_object(ActiveConfig)

# open and intialize or read the database
db = SQLAlchemy(app)
from application import views, models
# will create database and tables if not exist
db.create_all()

# REST resources
from application.resources.app_resource import AppResource
from application.resources.app_list_resource import AppListResource

# set the rest endpoints
rest_api = Api(app)
rest_api.add_resource(AppListResource,
                      ActiveConfig.REST_URL_APPS_LIST, endpoint='api.apps.list')
rest_api.add_resource(AppResource,
                      ActiveConfig.REST_URL_APPS_ITEM, endpoint='api.apps.item')
