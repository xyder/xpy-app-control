from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api
from flask.ext.httpauth import HTTPBasicAuth

from config import ActiveConfig

# initialize and configure the flask server
app = Flask(__name__)
app.config.from_object(ActiveConfig)

# open and intialize or read the database
db = SQLAlchemy(app)
from application import views, models
# will create database and tables if not exist
db.create_all()

# initalize the authentication
auth = HTTPBasicAuth()

# REST resources
from application.resources.app_resource import AppResource
from application.resources.app_list_resource import AppListResource
from application.resources.server_resource import ServerResource

# set the rest endpoints
rest_api = Api(app)
rest_api.add_resource(AppListResource,
                      ActiveConfig.REST_URL_APPS_LIST, endpoint='api.apps.list')
rest_api.add_resource(AppResource,
                      ActiveConfig.REST_URL_APPS_ITEM, endpoint='api.apps.item')
rest_api.add_resource(ServerResource,
                      ActiveConfig.REST_URL_SERVER_CMD, endpoint='api.server.cmd')